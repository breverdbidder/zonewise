#!/usr/bin/env python3
"""
Batch 1 Scraper — Top 10 FL Counties
=====================================
Scrapes zoning districts, dimensional standards, and permitted uses
for 149 jurisdictions across Florida's 10 largest counties.

Uses Playwright for Municode JS rendering, Claude Sonnet 4.5 for
structured extraction, and Supabase REST API for data storage.

Author: Claude AI Architect
Date: 2026-02-06
"""

import os
import sys
import json
import re
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

import subprocess

import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Browser, Page

# ──────────────────────────────────────────────────────────────
# 1. CONFIGURATION & SETUP
# ──────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('batch1_scraper.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

# Load credentials from .env
env_path = Path(__file__).parent.parent / "agents" / "verify" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CHECKPOINT_PATH = DATA_DIR / "batch1_checkpoint.json"
ERRORS_PATH = DATA_DIR / "batch1_errors.json"

# County order: smallest first for quick validation
COUNTY_ORDER = [
    "Hillsborough",   # 4 jurisdictions
    "Lee",             # 6
    "Duval",           # 6
    "Orange",          # 12
    "Polk",            # 17
    "Brevard",         # 18
    "Broward",         # 20
    "Palm Beach",      # 21
    "Miami-Dade",      # 21
    "Pinellas",        # 24
]

# Scraping config
PAGE_LOAD_WAIT = 5000       # ms to wait after networkidle
RATE_LIMIT_DELAY = 3.0      # seconds between page loads
MAX_SCRAPE_RETRIES = 3
MAX_TEXT_LENGTH = 15000      # chars sent to Claude per prompt
BATCH_INSERT_SIZE = 50


# ──────────────────────────────────────────────────────────────
# 2. SUPABASE CLIENT
# ──────────────────────────────────────────────────────────────

class SupabaseClient:
    """Lightweight REST client for Supabase PostgREST API."""

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client = httpx.Client(timeout=60.0)
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def get(self, table: str, params: Dict[str, str]) -> List[Dict]:
        """GET request with query params."""
        resp = self.client.get(
            f"{self.url}/rest/v1/{table}",
            headers=self.headers,
            params=params,
        )
        if resp.status_code == 200:
            return resp.json()
        logger.warning(f"GET {table} failed: {resp.status_code} {resp.text[:200]}")
        return []

    def post(
        self, table: str, records: List[Dict],
        upsert: bool = False, on_conflict: str = "",
    ) -> List[Dict]:
        """POST (insert) records, optionally upsert. Returns inserted rows."""
        headers = {**self.headers, "Prefer": "return=representation"}
        if upsert:
            headers["Prefer"] += ",resolution=merge-duplicates"

        params = {}
        if upsert and on_conflict:
            params["on_conflict"] = on_conflict

        all_results = []
        for i in range(0, len(records), BATCH_INSERT_SIZE):
            batch = records[i:i + BATCH_INSERT_SIZE]
            for attempt in range(2):
                try:
                    resp = self.client.post(
                        f"{self.url}/rest/v1/{table}",
                        headers=headers,
                        params=params,
                        json=batch,
                    )
                    if resp.status_code in (200, 201):
                        all_results.extend(resp.json())
                        break
                    else:
                        logger.warning(
                            f"POST {table} batch {i//BATCH_INSERT_SIZE} "
                            f"attempt {attempt+1}: {resp.status_code} {resp.text[:300]}"
                        )
                        if attempt == 0:
                            time.sleep(2)
                except Exception as e:
                    logger.error(f"POST {table} error: {e}")
                    if attempt == 0:
                        time.sleep(2)

        return all_results

    def get_jurisdictions(self, county: str) -> List[Dict]:
        """Get jurisdictions for a county with municode_url."""
        rows = self.get("jurisdictions", {
            "select": "id,name,municode_url",
            "county": f"eq.{county}",
            "order": "name",
        })
        # Filter out rows without municode_url
        return [r for r in rows if r.get("municode_url")]

    def insert_zoning_districts(self, records: List[Dict]) -> List[Dict]:
        """Insert/upsert zoning districts, return rows with IDs."""
        return self.post(
            "zoning_districts", records,
            upsert=True, on_conflict="jurisdiction_id,code",
        )

    def insert_zone_standards(self, records: List[Dict]) -> int:
        """Insert zone standards. Returns count."""
        results = self.post("zone_standards", records)
        return len(results)

    def insert_permitted_uses(self, records: List[Dict]) -> int:
        """Insert permitted uses. Returns count."""
        results = self.post("permitted_uses", records)
        return len(results)

    def close(self):
        self.client.close()


# ──────────────────────────────────────────────────────────────
# 3. PLAYWRIGHT SCRAPER
# ──────────────────────────────────────────────────────────────

class MunicodeScraper:
    """Headless Chromium scraper for Municode pages."""

    def __init__(self):
        self.pw = None
        self.browser = None

    def start(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        logger.info("Browser started")

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.pw:
            self.pw.stop()
        logger.info("Browser stopped")

    def restart(self):
        """Restart browser (crash recovery)."""
        try:
            self.stop()
        except Exception:
            pass
        self.start()

    @staticmethod
    def _clean_municode_text(text: str) -> str:
        """Strip Municode navigation chrome from scraped text."""
        # Skip past language selector block
        for end_marker in ['Zulu\n', 'Yoruba\n', 'Yiddish\n']:
            idx = text.find(end_marker)
            if 0 < idx < 5000:
                text = text[idx + len(end_marker):]
                break

        # Skip past sidebar TOC (list of "CHAPTER X - NAME\nEXPAND" entries)
        # These repeat on every Municode page as a left-nav
        expand_count = 0
        lines = text.split('\n')
        content_start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped in ('EXPAND', 'COLLAPSE', ''):
                expand_count += 1
            elif expand_count > 5 and not stripped.startswith('CHAPTER '):
                # Past the sidebar TOC
                content_start = i
                break
        if content_start > 0:
            text = '\n'.join(lines[content_start:])

        # Skip past "PRINT OR DOWNLOAD" and "VERSION:" controls
        for marker in ['PRINT OR DOWNLOAD TABLE OF CONTENTS\n', 'VERSION:']:
            idx = text.find(marker)
            if 0 < idx < 2000:
                newline = text.find('\n', idx + len(marker))
                if newline > 0:
                    text = text[newline + 1:]

        # Find actual section content (Sec. X-XXX references)
        sec_match = re.search(r'^Sec\. \d', text, re.MULTILINE)
        if sec_match and sec_match.start() < 3000:
            text = text[sec_match.start():]

        return text.strip()

    def scrape_page(self, url: str, wait_ms: int = PAGE_LOAD_WAIT) -> str:
        """Scrape a single page, return cleaned text content."""
        page = self.browser.new_page()
        try:
            for attempt in range(MAX_SCRAPE_RETRIES):
                try:
                    page.goto(url, wait_until='networkidle', timeout=60000)
                    page.wait_for_timeout(wait_ms)
                    text = page.inner_text('body')
                    if len(text) > 200:
                        return self._clean_municode_text(text)
                    logger.warning(f"Short content ({len(text)} chars) from {url}")
                except Exception as e:
                    wait = (attempt + 1) * 5
                    logger.warning(f"Scrape attempt {attempt+1} failed for {url}: {e}. Retrying in {wait}s")
                    time.sleep(wait)
            return ""
        finally:
            page.close()

    def scrape_page_html(self, url: str, wait_ms: int = PAGE_LOAD_WAIT) -> Tuple[str, str]:
        """Scrape a page, return (html, text)."""
        page = self.browser.new_page()
        try:
            for attempt in range(MAX_SCRAPE_RETRIES):
                try:
                    page.goto(url, wait_until='networkidle', timeout=60000)
                    page.wait_for_timeout(wait_ms)
                    html = page.content()
                    text = page.inner_text('body')
                    return html, text
                except Exception as e:
                    wait = (attempt + 1) * 5
                    logger.warning(f"Scrape attempt {attempt+1} failed: {e}. Retrying in {wait}s")
                    time.sleep(wait)
            return "", ""
        finally:
            page.close()

    def _extract_nodeId_links(self, html: str) -> List[Tuple[str, str]]:
        """Extract all (link_text, full_url) pairs with nodeId from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'nodeId=' not in href:
                continue
            link_text = a.get_text(strip=True)
            if href.startswith('/'):
                full_url = f"https://library.municode.com{href}"
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = f"https://library.municode.com{href}"
            results.append((link_text, full_url))
        return results

    @staticmethod
    def _filter_content_links(links: List[Tuple[str, str]], parent_url: str = "") -> List[Tuple[str, str]]:
        """Filter to actual content links, excluding sidebar navigation.
        Content links typically start with 'Sec.', 'ARTICLE', 'DIVISION'.
        Sidebar links are full chapter titles like 'Chapter 1 - GENERAL PROVISIONS'."""
        content_prefixes = ['sec.', 'sec ', 'article ', 'division ']
        sidebar_pattern = re.compile(r'^chapter\s+\d', re.I)
        results = []
        seen = set()
        for text, url in links:
            if url in seen:
                continue
            lt = text.lower().strip()
            # Always include Sec./Article/Division links
            if any(lt.startswith(p) for p in content_prefixes):
                results.append((text, url))
                seen.add(url)
            # Skip sidebar-style chapter links (unless it's the parent chapter itself)
            elif sidebar_pattern.match(lt):
                continue
            # Skip very generic links (code title, supplement tables, etc.)
            elif any(skip in lt for skip in ['code of ordinance', 'supplement history',
                                              'comparative table', 'charter and related']):
                continue
        return results

    @staticmethod
    def _prioritize_links(links: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Sort section links so the most extraction-valuable ones come first.
        Ensures per-district standards/uses sections get scraped within the limit."""
        high_priority = [
            'height', 'area requirement', 'dimensional', 'setback', 'density',
            'lot size', 'lot area', 'lot width', 'bulk', 'yard',
            'uses permitted', 'permitted use', 'conditional use', 'use regulation',
            'accessory use', 'prohibited use', 'special exception',
            'district', 'classification', 'establishment',
        ]
        medium_prefixes = ['article ', 'division ']

        def priority(item):
            lt = item[0].lower()
            if any(kw in lt for kw in high_priority):
                return 0
            if any(lt.strip().startswith(p) for p in medium_prefixes):
                return 1
            return 2

        return sorted(links, key=priority)

    def find_zoning_sections(self, base_url: str) -> List[Tuple[str, str]]:
        """Multi-level TOC navigation: find zoning chapter, drill into sub-chapters.
        Returns list of (title, url) pairs."""
        html, text = self.scrape_page_html(base_url)
        if not html:
            return []

        all_links = self._extract_nodeId_links(html)
        logger.info(f"  TOC has {len(all_links)} nodeId links")

        chapter_keywords = [
            'zoning', 'land development', 'land use', 'development code',
            'development regulation', 'unified land',
        ]

        # Check if the TOC already has Sec.-level zoning content links
        content_links = self._filter_content_links(all_links)
        zoning_content = [
            (t, u) for t, u in content_links
            if any(kw in t.lower() for kw in ['zon', 'district', 'use', 'setback', 'dimensional'])
        ]
        if len(zoning_content) >= 3:
            logger.info(f"  Found {len(zoning_content)} zoning section links directly in TOC")
            return zoning_content[:50]

        # Find the zoning/land-development chapter
        chapter_url = None
        chapter_name = None
        for link_text, url in all_links:
            lt = link_text.lower()
            if any(kw in lt for kw in chapter_keywords):
                chapter_url = url
                chapter_name = link_text
                logger.info(f"  Found zoning chapter: {link_text[:60]}")
                break

        if not chapter_url:
            for link_text, url in all_links:
                lt = link_text.lower()
                if 'zon' in lt or ('land' in lt and 'develop' in lt):
                    chapter_url = url
                    chapter_name = link_text
                    logger.info(f"  Fallback chapter: {link_text[:60]}")
                    break

        if not chapter_url:
            logger.warning(f"  No zoning chapter found in TOC")
            return []

        # Level 2: Scrape the chapter page
        time.sleep(RATE_LIMIT_DELAY)
        chapter_html, _ = self.scrape_page_html(chapter_url)
        if not chapter_html:
            return [("Zoning Chapter", chapter_url)]

        chapter_links = self._extract_nodeId_links(chapter_html)
        logger.info(f"  Chapter page has {len(chapter_links)} nodeId links")

        # Check if there's a more specific zoning sub-chapter to drill into
        # (e.g., "Chapter 102 - ZONING" within "Subpart B - BUILDING REGULATIONS")
        zoning_subchapter = None
        for link_text, url in chapter_links:
            lt = link_text.lower()
            if 'zoning' in lt and url != chapter_url:
                if any(p in lt for p in ['chapter ', 'title ', 'part ']):
                    zoning_subchapter = (link_text, url)
                    logger.info(f"  Found zoning sub-chapter: {link_text[:60]}")
                    break

        if zoning_subchapter:
            # Drill one more level into the specific zoning chapter
            time.sleep(RATE_LIMIT_DELAY)
            sub_html, _ = self.scrape_page_html(zoning_subchapter[1])
            if sub_html:
                chapter_links = self._extract_nodeId_links(sub_html)
                logger.info(f"  Sub-chapter page has {len(chapter_links)} nodeId links")
                chapter_url = zoning_subchapter[1]

        # Filter to actual content links (Sec., Article, Division)
        content_links = self._filter_content_links(chapter_links, chapter_url)
        if len(content_links) >= 3:
            # Prioritize links by title relevance before truncating
            content_links = self._prioritize_links(content_links)
            logger.info(f"  Found {len(content_links)} content section links after drill-down")
            return content_links[:50]

        # Fallback: keyword-matched links (excluding obvious sidebar items)
        section_keywords = [
            'zon', 'district', 'land use', 'dimensional', 'setback',
            'permitted use', 'conditional use', 'development standard',
            'height', 'density', 'lot size', 'overlay', 'pud',
            'use regulation', 'bulk regulation',
        ]
        section_links = []
        seen_urls = set()
        for link_text, url in chapter_links:
            lt = link_text.lower()
            if any(kw in lt for kw in section_keywords):
                if url not in seen_urls and url != chapter_url:
                    section_links.append((link_text, url))
                    seen_urls.add(url)

        if not section_links:
            # Last resort: include all non-sidebar chapter links
            for link_text, url in chapter_links:
                lt = link_text.lower().strip()
                if url not in seen_urls and url != chapter_url:
                    if not re.match(r'^chapter\s+\d', lt, re.I):
                        section_links.append((link_text, url))
                        seen_urls.add(url)

        logger.info(f"  Found {len(section_links)} keyword-matched sections after drill-down")
        return section_links[:50]


# ──────────────────────────────────────────────────────────────
# 4. CLAUDE EXTRACTOR
# ──────────────────────────────────────────────────────────────

class ClaudeExtractor:
    """Use Claude Code CLI for structured zoning data extraction (covered by Max plan)."""

    def __init__(self, model: str = "sonnet"):
        self.model = model

    def _call(self, system: str, user: str) -> str:
        """Call Claude Code CLI in print mode via stdin pipe, return text response."""
        prompt = f"{system}\n\n{user}"
        logger.info(f"  Claude CLI call: {len(prompt)} chars prompt")
        for attempt in range(2):
            try:
                result = subprocess.run(
                    [
                        "claude", "-p",
                        "--model", self.model,
                        "--output-format", "json",
                        "--no-session-persistence",
                        "--max-turns", "1",
                    ],
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=180,
                    encoding="utf-8",
                    errors="replace",
                )
                if result.returncode != 0:
                    logger.error(
                        f"Claude CLI returncode={result.returncode} (attempt {attempt+1}): "
                        f"stderr={result.stderr[:300]} stdout={result.stdout[:300]}"
                    )
                    if attempt == 0:
                        time.sleep(5)
                    continue

                # Parse the CLI JSON envelope to get the actual result text
                if not result.stdout.strip():
                    logger.error(f"Claude CLI returned empty stdout (attempt {attempt+1})")
                    if attempt == 0:
                        time.sleep(5)
                    continue

                try:
                    envelope = json.loads(result.stdout)
                except json.JSONDecodeError:
                    logger.warning(f"Claude CLI non-JSON output ({len(result.stdout)} chars), using raw")
                    return result.stdout

                if envelope.get("is_error"):
                    logger.error(f"Claude CLI error response: {envelope.get('result', '')[:300]}")
                    if attempt == 0:
                        time.sleep(5)
                    continue

                text = envelope.get("result", "") or ""
                logger.info(f"  Claude CLI response: {len(text)} chars")
                return text

            except subprocess.TimeoutExpired:
                logger.error(f"Claude CLI timeout (attempt {attempt+1})")
                if attempt == 0:
                    time.sleep(5)
            except Exception as e:
                logger.error(f"Claude CLI exception (attempt {attempt+1}): {e}")
                if attempt == 0:
                    time.sleep(5)
        return ""

    def _parse_json(self, text: str) -> Any:
        """Parse JSON from Claude response, handling common issues."""
        # Strip markdown code fences
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
        text = text.strip()

        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Fix trailing commas
        text = re.sub(r',\s*([}\]])', r'\1', text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find a JSON array or object
        for pattern in [r'\[[\s\S]*\]', r'\{[\s\S]*\}']:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue

        logger.warning(f"Failed to parse JSON from Claude response ({len(text)} chars): {text[:200]}")
        return []

    @staticmethod
    def _combine_sections(sections, keywords: List[str], max_chars: int = MAX_TEXT_LENGTH) -> str:
        """Combine sections, prioritizing by title match (10x) + text keyword count.
        sections: List of (title, text) tuples or List of str (backwards compat)
        """
        # Normalize to (title, text) tuples
        if sections and isinstance(sections[0], str):
            pairs = [("", s) for s in sections]
        else:
            pairs = sections

        # Filter out very short sections (likely junk/dead links)
        valid = [(title, text) for title, text in pairs if len(text) > 300]
        if not valid:
            fallback = [t if isinstance(t, str) else t[1] for t in sections]
            return "\n\n".join(fallback)[:max_chars]

        # Score by title keyword match (100x boost) + text keyword density
        # Density prevents long documents from dominating short, focused ones
        scored = []
        for title, text in valid:
            title_lower = title.lower()
            text_lower = text.lower()
            title_score = sum(100 for kw in keywords if kw in title_lower)
            raw_count = sum(text_lower.count(kw) for kw in keywords)
            text_density = raw_count / max(len(text_lower) / 1000, 1)
            scored.append((title_score + text_density, title, text))

        # Sort: highest-scoring sections first
        scored.sort(key=lambda x: x[0], reverse=True)

        # Log top 3 selected sections for debugging
        for i, (score, title, _) in enumerate(scored[:3]):
            logger.info(f"    Section rank {i+1}: score={score} title='{title[:60]}'")

        # Combine up to max_chars
        parts = []
        total = 0
        for score, title, text in scored:
            if total >= max_chars:
                break
            remaining = max_chars - total
            parts.append(text[:remaining])
            total += len(text)

        return "\n\n".join(parts)

    def extract_districts(self, sections, jurisdiction_name: str) -> List[Dict]:
        """Prompt A: Extract zoning district codes and names."""
        district_keywords = [
            'district', 'zone', 'classif', 'establish', 'r-1', 'r-2', 'c-1', 'c-2',
            'residential', 'commercial', 'industrial', 'agricultural', 'pud',
        ]
        text = self._combine_sections(sections, district_keywords)
        system = (
            "You are a zoning code analyst. Extract ALL zoning district classifications "
            "from the provided municipal code text. Return ONLY a JSON array."
        )
        user = f"""Extract all zoning districts from this {jurisdiction_name} zoning code text.

For each district, provide:
- "code": The district code/abbreviation (e.g., "R-1", "C-2", "PUD")
- "name": The full district name (e.g., "Single-Family Residential")
- "category": One of: residential, commercial, industrial, agricultural, mixed_use, planned, conservation, institutional, overlay, special

Return ONLY a JSON array of objects. If no districts are found, return [].

TEXT:
{text}"""

        raw = self._call(system, user)
        result = self._parse_json(raw)
        if not isinstance(result, list):
            return []
        return [r for r in result if isinstance(r, dict) and r.get("code") and r.get("name")]

    def extract_standards(self, sections, jurisdiction_name: str, district_codes: List[str]) -> List[Dict]:
        """Prompt B: Extract dimensional standards per district."""
        standards_keywords = [
            'setback', 'height', 'lot size', 'lot area', 'lot width', 'coverage',
            'density', 'far', 'floor area', 'stories', 'minimum', 'maximum',
            'front yard', 'side yard', 'rear yard', 'sqft', 'sq ft', 'square feet',
            'dimensional', 'development standard', 'bulk regulation',
        ]
        text = self._combine_sections(sections, standards_keywords)
        codes_str = ", ".join(district_codes[:30])
        system = (
            "You are a zoning code analyst. Extract dimensional/development standards "
            "from the provided text. Return ONLY a JSON array."
        )
        user = f"""Extract dimensional standards for these {jurisdiction_name} zoning districts: {codes_str}

For each district with available data, provide:
- "district_code": Must match one of the codes above
- "min_lot_sqft": Minimum lot area in square feet (integer or null)
- "min_lot_width_ft": Minimum lot width in feet (number or null)
- "min_lot_depth_ft": Minimum lot depth in feet (number or null)
- "max_height_ft": Maximum building height in feet (number or null)
- "max_stories": Maximum number of stories (integer or null)
- "front_setback_ft": Front yard setback in feet (number or null)
- "side_setback_ft": Side yard setback in feet (number or null)
- "rear_setback_ft": Rear yard setback in feet (number or null)
- "corner_setback_ft": Corner lot setback in feet (number or null)
- "max_lot_coverage_pct": Maximum lot coverage percentage (number or null)
- "max_far": Maximum floor area ratio (number or null)
- "max_density_du_acre": Maximum density in dwelling units per acre (number or null)
- "min_open_space_pct": Minimum open space percentage (number or null)

Only include districts where you can find at least 2 numeric values. Return ONLY a JSON array.

TEXT:
{text}"""

        raw = self._call(system, user)
        result = self._parse_json(raw)
        if not isinstance(result, list):
            return []
        # Validate: must have district_code and at least 2 values
        valid = []
        for r in result:
            if not isinstance(r, dict) or not r.get("district_code"):
                continue
            numeric_fields = [
                "min_lot_sqft", "min_lot_width_ft", "max_height_ft", "max_stories",
                "front_setback_ft", "side_setback_ft", "rear_setback_ft",
                "max_lot_coverage_pct", "max_far", "max_density_du_acre",
            ]
            count = sum(1 for f in numeric_fields if r.get(f) is not None)
            if count >= 2:
                valid.append(r)
        return valid

    def extract_uses(self, sections, jurisdiction_name: str, district_codes: List[str]) -> List[Dict]:
        """Prompt C: Extract permitted/conditional uses per district."""
        uses_keywords = [
            'permitted use', 'conditional use', 'accessory use', 'prohibited',
            'special exception', 'use regulation', 'allowed use', 'land use',
            'dwelling', 'single-family', 'multi-family', 'commercial', 'retail',
            'office', 'industrial', 'warehouse', 'restaurant', 'hotel',
        ]
        text = self._combine_sections(sections, uses_keywords)
        codes_str = ", ".join(district_codes[:30])
        system = (
            "You are a zoning code analyst. Extract land use permissions from the "
            "provided text. Return ONLY a JSON array."
        )
        user = f"""Extract permitted and conditional uses for these {jurisdiction_name} zoning districts: {codes_str}

For each use entry, provide:
- "district_code": Must match one of the codes above
- "use_description": Clear description of the use (REQUIRED, e.g., "Single-family detached dwelling")
- "use_type": One of: "permitted", "conditional", "accessory", "prohibited"
- "use_category": One of: residential, commercial, industrial, institutional, recreational, agricultural, utility, mixed_use, other
- "is_single_family": true/false
- "is_multi_family": true/false
- "is_commercial": true/false
- "is_industrial": true/false
- "is_mixed_use": true/false
- "is_adu": true/false (accessory dwelling unit)
- "is_short_term_rental": true/false
- "special_conditions": Any special conditions or notes (string or null)

Return ONLY a JSON array. Focus on the most important/common uses per district.

TEXT:
{text}"""

        raw = self._call(system, user)
        result = self._parse_json(raw)
        if not isinstance(result, list):
            return []
        # Validate: must have district_code and use_description
        return [
            r for r in result
            if isinstance(r, dict) and r.get("district_code") and r.get("use_description")
        ]


# ──────────────────────────────────────────────────────────────
# 5. CHECKPOINT SYSTEM
# ──────────────────────────────────────────────────────────────

class Checkpoint:
    """Track per-jurisdiction progress across restarts."""

    def __init__(self, path: Path):
        self.path = path
        self.data: Dict[str, Any] = {"jurisdictions": {}, "stats": {}, "errors": []}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                with open(self.path) as f:
                    self.data = json.load(f)
                logger.info(f"Loaded checkpoint: {len(self.data['jurisdictions'])} jurisdictions tracked")
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)

    def get_status(self, jurisdiction_id: str) -> str:
        return self.data["jurisdictions"].get(jurisdiction_id, {}).get("status", "pending")

    def set_status(self, jurisdiction_id: str, status: str, **extra):
        if jurisdiction_id not in self.data["jurisdictions"]:
            self.data["jurisdictions"][jurisdiction_id] = {}
        self.data["jurisdictions"][jurisdiction_id]["status"] = status
        self.data["jurisdictions"][jurisdiction_id]["updated_at"] = datetime.now().isoformat()
        self.data["jurisdictions"][jurisdiction_id].update(extra)
        self.save()

    def add_error(self, jurisdiction_id: str, error: str):
        self.data["errors"].append({
            "jurisdiction_id": jurisdiction_id,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        })

    def update_county_stats(self, county: str, stats: Dict):
        self.data["stats"][county] = {
            **stats,
            "completed_at": datetime.now().isoformat(),
        }
        self.save()


# ──────────────────────────────────────────────────────────────
# 6. MAIN PIPELINE
# ──────────────────────────────────────────────────────────────

def determine_confidence(text: str) -> float:
    """Estimate confidence based on content structure."""
    # Tables suggest well-structured data
    if re.search(r'\|.*\|.*\|', text) or re.search(r'<table', text, re.I):
        return 0.8
    # Numbered lists or bullet points
    if re.search(r'^\s*\d+[\.\)]\s', text, re.MULTILINE):
        return 0.7
    # Narrative text is less reliable
    return 0.5


def build_district_records(jurisdiction_id: str, districts: List[Dict]) -> List[Dict]:
    """Convert extracted districts to Supabase insert format."""
    records = []
    for d in districts:
        records.append({
            "jurisdiction_id": jurisdiction_id,
            "code": d["code"][:20],
            "name": d["name"][:200],
            "category": d.get("category"),
        })
    return records


def build_standards_records(
    district_id_map: Dict[str, str],  # code -> uuid
    standards: List[Dict],
    source_url: str,
    confidence: float,
) -> List[Dict]:
    """Convert extracted standards to zone_standards insert format."""
    records = []
    now = datetime.now().isoformat()
    for s in standards:
        code = s.get("district_code", "")
        district_id = district_id_map.get(code)
        if not district_id:
            # Try case-insensitive match
            for k, v in district_id_map.items():
                if k.lower() == code.lower():
                    district_id = v
                    break
        records.append({
            "zoning_district_id": district_id,  # nullable, ok if None
            "min_lot_sqft": _safe_int(s.get("min_lot_sqft")),
            "min_lot_width_ft": _safe_int(s.get("min_lot_width_ft")),
            "min_lot_depth_ft": _safe_int(s.get("min_lot_depth_ft")),
            "max_height_ft": _safe_int(s.get("max_height_ft")),
            "max_stories": _safe_int(s.get("max_stories")),
            "front_setback_ft": _safe_int(s.get("front_setback_ft")),
            "side_setback_ft": _safe_int(s.get("side_setback_ft")),
            "rear_setback_ft": _safe_int(s.get("rear_setback_ft")),
            "corner_setback_ft": _safe_int(s.get("corner_setback_ft")),
            "max_lot_coverage_pct": _safe_num(s.get("max_lot_coverage_pct")),
            "max_far": _safe_num(s.get("max_far")),
            "max_density_du_acre": _safe_num(s.get("max_density_du_acre")),
            "min_open_space_pct": _safe_num(s.get("min_open_space_pct")),
            "source_url": source_url,
            "confidence_score": confidence,
            "scraped_at": now,
        })
    return records


def build_uses_records(
    district_id_map: Dict[str, str],
    uses: List[Dict],
    source_url: str,
    confidence: float,
) -> List[Dict]:
    """Convert extracted uses to permitted_uses insert format."""
    records = []
    now = datetime.now().isoformat()
    for u in uses:
        code = u.get("district_code", "")
        district_id = district_id_map.get(code)
        if not district_id:
            for k, v in district_id_map.items():
                if k.lower() == code.lower():
                    district_id = v
                    break

        use_type = u.get("use_type", "permitted")
        if use_type not in ("permitted", "conditional", "accessory", "prohibited"):
            use_type = "permitted"

        records.append({
            "zoning_district_id": district_id,
            "use_type": use_type,
            "use_category": u.get("use_category"),
            "use_description": u["use_description"][:500],
            "is_single_family": u.get("is_single_family", False),
            "is_multi_family": u.get("is_multi_family", False),
            "is_commercial": u.get("is_commercial", False),
            "is_industrial": u.get("is_industrial", False),
            "is_mixed_use": u.get("is_mixed_use", False),
            "is_adu": u.get("is_adu", False),
            "is_short_term_rental": u.get("is_short_term_rental", False),
            "special_conditions": u.get("special_conditions"),
            "confidence_score": confidence,
            "scraped_at": now,
        })
    return records


def _safe_num(val) -> Optional[float]:
    """Convert to float or None."""
    if val is None:
        return None
    try:
        n = float(val)
        return n if n >= 0 else None
    except (TypeError, ValueError):
        return None


def _safe_int(val) -> Optional[int]:
    """Convert to int or None."""
    if val is None:
        return None
    try:
        n = int(val)
        return n if n >= 0 else None
    except (TypeError, ValueError):
        return None


def run_pipeline():
    """Main pipeline: scrape → extract → upload for all counties."""
    logger.info("=" * 70)
    logger.info("BATCH 1 SCRAPER — Top 10 FL Counties")
    logger.info("=" * 70)
    logger.info(f"Supabase: {SUPABASE_URL}")
    logger.info(f"Extraction: Claude Code CLI (covered by Max plan)")
    logger.info(f"Counties: {len(COUNTY_ORDER)}")
    logger.info(f"Checkpoint: {CHECKPOINT_PATH}")
    logger.info("=" * 70)

    if not SUPABASE_KEY:
        logger.error("SUPABASE_KEY not set. Aborting.")
        return

    # Verify claude CLI is available
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logger.error("Claude Code CLI not available. Install it first.")
            return
        logger.info(f"Claude Code CLI: {result.stdout.strip()}")
    except FileNotFoundError:
        logger.error("Claude Code CLI not found in PATH. Install it first.")
        return

    db = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
    extractor = ClaudeExtractor(model="sonnet")
    checkpoint = Checkpoint(CHECKPOINT_PATH)
    scraper = MunicodeScraper()

    # Global stats
    total_districts = 0
    total_standards = 0
    total_uses = 0
    total_jurisdictions = 0
    start_time = datetime.now()

    try:
        scraper.start()

        for county in COUNTY_ORDER:
            logger.info(f"\n{'='*60}")
            logger.info(f"COUNTY: {county}")
            logger.info(f"{'='*60}")

            jurisdictions = db.get_jurisdictions(county)
            if not jurisdictions:
                logger.warning(f"  No jurisdictions with municode_url found for {county}")
                continue

            logger.info(f"  {len(jurisdictions)} jurisdictions found")
            county_districts = 0
            county_standards = 0
            county_uses = 0
            county_scraped = 0

            for j in jurisdictions:
                jid = j["id"]
                jname = j["name"]
                municode_url = j["municode_url"]

                # Skip if already completed
                status = checkpoint.get_status(jid)
                if status == "uploaded":
                    logger.info(f"  [{jname}] Already uploaded, skipping")
                    county_scraped += 1
                    continue

                logger.info(f"\n  --- {jname} ---")
                logger.info(f"  URL: {municode_url}")

                try:
                    # ── SCRAPE ──
                    logger.info(f"  Scraping TOC...")
                    section_pairs = scraper.find_zoning_sections(municode_url)
                    time.sleep(RATE_LIMIT_DELAY)

                    all_sections = []  # List of (title, text) tuples
                    if section_pairs:
                        for i, (title, section_url) in enumerate(section_pairs):
                            logger.info(f"  Scraping section {i+1}/{len(section_pairs)}: {title[:50]}...")
                            text = scraper.scrape_page(section_url)
                            if text and len(text) > 200:
                                all_sections.append((title, text))
                            time.sleep(RATE_LIMIT_DELAY)
                    else:
                        # Fallback: scrape the base URL directly
                        logger.info(f"  No section links found, scraping base URL...")
                        text = scraper.scrape_page(municode_url)
                        if text:
                            all_sections.append(("Base page", text))

                    if not all_sections:
                        logger.warning(f"  No content scraped for {jname}")
                        checkpoint.set_status(jid, "failed", error="no_content")
                        checkpoint.add_error(jid, "No content scraped")
                        continue

                    total_chars = sum(len(t) for _, t in all_sections)
                    logger.info(f"  Scraped {total_chars} chars from {len(all_sections)} sections")
                    checkpoint.set_status(jid, "scraped", chars=total_chars, sections=len(all_sections))

                    # ── EXTRACT VIA CLAUDE ──
                    # Pass titled sections — extractor picks best by title + text scoring
                    logger.info(f"  Extracting districts...")
                    districts = extractor.extract_districts(all_sections, jname)
                    logger.info(f"  Found {len(districts)} districts")

                    if not districts:
                        logger.warning(f"  No districts extracted for {jname}")
                        checkpoint.set_status(jid, "failed", error="no_districts")
                        checkpoint.add_error(jid, "No districts extracted by Claude")
                        continue

                    district_codes = [d["code"] for d in districts]

                    logger.info(f"  Extracting dimensional standards...")
                    standards = extractor.extract_standards(all_sections, jname, district_codes)
                    logger.info(f"  Found {len(standards)} standard entries")

                    logger.info(f"  Extracting permitted uses...")
                    uses = extractor.extract_uses(all_sections, jname, district_codes)
                    logger.info(f"  Found {len(uses)} use entries")

                    checkpoint.set_status(
                        jid, "extracted",
                        districts=len(districts),
                        standards=len(standards),
                        uses=len(uses),
                    )

                    # ── UPLOAD ──
                    combined_text = "\n".join(t for _, t in all_sections)
                    confidence = determine_confidence(combined_text)
                    source_url = municode_url

                    # 1. Insert districts first → get IDs
                    logger.info(f"  Uploading {len(districts)} districts...")
                    district_records = build_district_records(jid, districts)
                    inserted_districts = db.insert_zoning_districts(district_records)

                    # Build code → id map
                    district_id_map: Dict[str, str] = {}
                    for row in inserted_districts:
                        district_id_map[row["code"]] = row["id"]
                    logger.info(f"  Inserted {len(inserted_districts)} districts (got {len(district_id_map)} IDs)")

                    # 2. Insert zone_standards
                    if standards:
                        logger.info(f"  Uploading {len(standards)} zone standards...")
                        std_records = build_standards_records(district_id_map, standards, source_url, confidence)
                        std_count = db.insert_zone_standards(std_records)
                        logger.info(f"  Inserted {std_count} zone standards")
                    else:
                        std_count = 0

                    # 3. Insert permitted_uses
                    if uses:
                        logger.info(f"  Uploading {len(uses)} permitted uses...")
                        use_records = build_uses_records(district_id_map, uses, source_url, confidence)
                        use_count = db.insert_permitted_uses(use_records)
                        logger.info(f"  Inserted {use_count} permitted uses")
                    else:
                        use_count = 0

                    checkpoint.set_status(
                        jid, "uploaded",
                        districts_inserted=len(inserted_districts),
                        standards_inserted=std_count,
                        uses_inserted=use_count,
                    )

                    county_districts += len(inserted_districts)
                    county_standards += std_count
                    county_uses += use_count
                    county_scraped += 1
                    total_jurisdictions += 1

                except Exception as e:
                    logger.error(f"  ERROR processing {jname}: {e}", exc_info=True)
                    checkpoint.set_status(jid, "failed", error=str(e))
                    checkpoint.add_error(jid, str(e))
                    # Restart browser if it might be crashed
                    try:
                        scraper.restart()
                    except Exception:
                        pass

            # County summary
            total_districts += county_districts
            total_standards += county_standards
            total_uses += county_uses

            checkpoint.update_county_stats(county, {
                "jurisdictions_total": len(jurisdictions),
                "jurisdictions_scraped": county_scraped,
                "districts": county_districts,
                "standards": county_standards,
                "uses": county_uses,
            })

            logger.info(f"\n  COUNTY SUMMARY: {county}")
            logger.info(f"    Jurisdictions: {county_scraped}/{len(jurisdictions)}")
            logger.info(f"    Districts: {county_districts}")
            logger.info(f"    Standards: {county_standards}")
            logger.info(f"    Uses: {county_uses}")

    finally:
        scraper.stop()
        db.close()

    # Final report
    elapsed = datetime.now() - start_time
    logger.info("\n" + "=" * 70)
    logger.info("BATCH 1 COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Duration: {elapsed}")
    logger.info(f"Jurisdictions processed: {total_jurisdictions}")
    logger.info(f"Zoning districts inserted: {total_districts}")
    logger.info(f"Zone standards inserted: {total_standards}")
    logger.info(f"Permitted uses inserted: {total_uses}")
    logger.info(f"Errors: {len(checkpoint.data['errors'])}")
    logger.info("=" * 70)

    # Save final errors
    if checkpoint.data["errors"]:
        with open(ERRORS_PATH, 'w') as f:
            json.dump(checkpoint.data["errors"], f, indent=2, default=str)
        logger.info(f"Errors saved to: {ERRORS_PATH}")

    checkpoint.save()
    logger.info(f"Checkpoint saved to: {CHECKPOINT_PATH}")


if __name__ == "__main__":
    run_pipeline()
