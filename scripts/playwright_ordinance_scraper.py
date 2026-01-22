#!/usr/bin/env python3
"""
Playwright-based Municode scraper - JavaScript rendering enabled
Scrapes all 17 Brevard County jurisdictions for ordinances
"""

import os
import sys
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import httpx
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright, Browser, Page

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Load credentials
env_path = Path(__file__).parent.parent / "agents" / "verify" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE")

# Jurisdictions to scrape
JURISDICTIONS = {
    1: "melbourne",
    2: "palm_bay",
    3: "indian_harbour_beach",
    4: "satellite_beach",
    5: "indialantic",
    6: "melbourne_beach",
    7: "west_melbourne",
    8: "cocoa",
    9: "cocoa_beach",
    10: "rockledge",
    11: "titusville",
    12: "cape_canaveral",
    13: "brevard_county",
    14: "malabar",
    15: "palm_shores",
    16: "grant-valkaria",
    17: "melbourne_village",
}


class MunicodeScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.stats = {jid: {"pages": 0, "ordinances": 0, "errors": 0} for jid in JURISDICTIONS}

    def start_browser(self):
        """Start Playwright browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        logger.info("Browser started")

    def stop_browser(self):
        """Stop Playwright browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser stopped")

    def scrape_page(self, url: str, wait_time: int = 5000) -> Tuple[str, str]:
        """Scrape a single page with JS rendering"""
        page = self.browser.new_page()
        try:
            for attempt in range(3):
                try:
                    page.goto(url, wait_until='networkidle', timeout=60000)
                    page.wait_for_timeout(wait_time)
                    content = page.content()
                    text = page.inner_text('body')
                    return content, text
                except Exception as e:
                    if attempt == 2:
                        logger.error(f"Failed to load {url}: {e}")
                        return "", ""
                    time.sleep(2)
        finally:
            page.close()
        return "", ""

    def get_chapter_links(self, base_url: str, content: str) -> List[str]:
        """Extract chapter/section links from TOC"""
        soup = BeautifulSoup(content, 'html.parser')
        links = []

        # Find all links that point to code sections
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'nodeId=' in href:
                if href.startswith('/'):
                    full_url = f"https://library.municode.com{href}"
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = f"{base_url}?{href}" if '?' in href else f"{base_url}/{href}"

                if full_url not in links:
                    links.append(full_url)

        return links

    def extract_ordinances(self, text: str, url: str, jid: int) -> List[Dict]:
        """Extract ordinance references from page text"""
        ordinances = []
        seen = set()

        # Multiple patterns for ordinance references
        patterns = [
            # (Ord. No. 2024-33, § 2, 9-19-24)
            r'\(Ord\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{2,4}[-–]\d{1,4})\s*,?[^)]*?(\d{1,2}[-–/]\d{1,2}[-–/]\d{2,4})?\)',
            # Ord. 2024-33
            r'Ord(?:inance)?\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{4}[-–]\d+)',
            # [Ord. 2024-33]
            r'\[Ord\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{4}[-–]\d+)',
            # amended by Ord. 2024-33
            r'(?:amended|enacted|added|repealed)\s+by\s+Ord\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{2,4}[-–]\d+)',
            # General pattern
            r'Ord\.?\s*(?:No\.?\s*)?(\d{2,4}[-–]\d{1,4})',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                ord_num = match.group(1).replace('–', '-')

                # Skip if too short or already seen
                if len(ord_num) < 5 or ord_num in seen:
                    continue
                # Skip if it looks like just a year
                if re.match(r'^\d{4}$', ord_num):
                    continue

                seen.add(ord_num)

                # Try to extract date
                passed_date = None
                if len(match.groups()) > 1 and match.group(2):
                    date_str = match.group(2).replace('–', '-')
                    for fmt in ['%m-%d-%y', '%m/%d/%y', '%m-%d-%Y', '%m/%d/%Y']:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            if dt.year > 2050:
                                dt = dt.replace(year=dt.year - 100)
                            passed_date = dt.date().isoformat()
                            break
                        except:
                            continue

                # Get surrounding context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()

                ordinances.append({
                    "jurisdiction_id": jid,
                    "ordinance_number": ord_num,
                    "title": ord_num,
                    "source_url": url,
                    "passed_date": passed_date,
                    "full_text": context[:500] if context else None,
                })

        return ordinances

    def extract_overlays(self, text: str, url: str, jid: int) -> List[Dict]:
        """Extract overlay district references"""
        overlays = []
        seen = set()

        patterns = [
            (r'([A-Z]{2,5}[-\s]?O(?:V|VL)?)\s+(?:district|zone)', 'general'),
            (r'(\w+)\s+[Oo]verlay\s+[Dd]istrict', 'general'),
            (r'([Hh]istoric(?:al)?\s+[Pp]reservation\s+[Dd]istrict)', 'historic'),
            (r'([Ff]lood(?:plain)?\s+[Oo]verlay)', 'flood'),
            (r'([Cc]oastal\s+[Hh]igh\s+[Hh]azard\s+[Aa]rea)', 'coastal'),
            (r'([Aa]irport\s+[Nn]oise\s+[Zz]one)', 'airport'),
            (r'([Ww]aterfront\s+[Oo]verlay)', 'waterfront'),
            (r'([Dd]owntown\s+[Oo]verlay)', 'downtown'),
            (r'(CRA|Community\s+Redevelopment\s+Area)', 'redevelopment'),
            (r'(CHHA|Coastal\s+High\s+Hazard)', 'coastal'),
        ]

        for pattern, otype in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                name = match.group(1).strip()
                key = f"{jid}-{name.lower()}"
                if key in seen or len(name) < 3:
                    continue
                seen.add(key)

                overlays.append({
                    "jurisdiction_id": jid,
                    "overlay_name": name,
                    "overlay_code": name[:10].upper().replace(' ', '-'),
                    "overlay_type": otype,
                    "source_url": url,
                })

        return overlays

    def extract_bonuses(self, text: str, url: str, jid: int) -> List[Dict]:
        """Extract development bonus references"""
        bonuses = []
        seen = set()

        bonus_patterns = [
            (r'[Dd]ensity\s+[Bb]onus', "Density Bonus", "Increased Density"),
            (r'[Hh]eight\s+[Bb]onus', "Height Bonus", "Additional Height"),
            (r'[Pp]arking\s+[Rr]eduction', "Parking Reduction", "Reduced Parking"),
            (r'[Aa]ffordable\s+[Hh]ousing\s+[Bb]onus', "Affordable Housing", "Affordable Units"),
            (r'[Mm]ixed[- ][Uu]se\s+[Bb]onus', "Mixed Use Bonus", "Mixed Use"),
            (r'[Gg]reen\s+[Bb]uilding', "Green Building", "Sustainability"),
            (r'[Ii]mpact\s+[Ff]ee\s+[Cc]redit', "Impact Fee Credit", "Fee Reduction"),
            (r'TDR|[Tt]ransfer.*[Dd]evelopment\s+[Rr]ights', "TDR Program", "Development Rights"),
            (r'[Ll]IVE\s*[Ll]ocal', "Live Local Act", "Housing Incentive"),
        ]

        for pattern, program, feature in bonus_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                key = f"{jid}-{program.lower()}"
                if key in seen:
                    continue
                seen.add(key)

                bonuses.append({
                    "jurisdiction_id": jid,
                    "program_name": program,
                    "feature_name": feature,
                    "source_url": url,
                })

        return bonuses

    def extract_timelines(self, text: str, url: str, jid: int) -> List[Dict]:
        """Extract entitlement timeline references"""
        timelines = []
        seen = set()

        process_types = [
            (r'[Ss]ite\s+[Pp]lan\s+[Rr]eview', "Site Plan Review"),
            (r'[Rr]ezon(?:e|ing)', "Rezoning"),
            (r'[Cc]onditional\s+[Uu]se', "Conditional Use Permit"),
            (r'[Ss]pecial\s+[Ee]xception', "Special Exception"),
            (r'[Vv]ariance', "Variance"),
            (r'[Pp]reliminary\s+[Pp]lat', "Preliminary Plat"),
            (r'[Ff]inal\s+[Pp]lat', "Final Plat"),
            (r'[Pp]lanned\s+[Uu]nit\s+[Dd]evelopment', "PUD Review"),
            (r'[Aa]nnexation', "Annexation"),
            (r'[Bb]uilding\s+[Pp]ermit', "Building Permit"),
        ]

        for pattern, process_type in process_types:
            if re.search(pattern, text, re.IGNORECASE):
                key = f"{jid}-{process_type}"
                if key in seen:
                    continue
                seen.add(key)

                timelines.append({
                    "jurisdiction_id": jid,
                    "process_type": process_type,
                    "steps": [],
                    "source_url": url,
                })

        return timelines

    def upload_record(self, table: str, record: Dict) -> bool:
        """Upload a record to Supabase"""
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        try:
            client = httpx.Client(timeout=30)
            resp = client.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=headers, json=record)
            client.close()
            return resp.status_code in (200, 201)
        except Exception as e:
            return False

    def scrape_jurisdiction(self, jid: int, slug: str) -> Dict:
        """Scrape a single jurisdiction"""
        logger.info(f"[{jid}/17] Starting {slug}...")

        base_url = f"https://library.municode.com/fl/{slug}/codes/code_of_ordinances"
        results = {
            "ordinances": [],
            "overlays": [],
            "bonuses": [],
            "timelines": [],
        }

        # Get TOC
        logger.info(f"  Fetching TOC...")
        content, text = self.scrape_page(base_url)
        if not content:
            logger.error(f"  Failed to load TOC for {slug}")
            self.stats[jid]["errors"] += 1
            return results

        self.stats[jid]["pages"] += 1
        logger.info(f"  TOC: {len(content)} bytes")

        # Extract from TOC
        results["ordinances"].extend(self.extract_ordinances(text, base_url, jid))
        results["overlays"].extend(self.extract_overlays(text, base_url, jid))
        results["bonuses"].extend(self.extract_bonuses(text, base_url, jid))
        results["timelines"].extend(self.extract_timelines(text, base_url, jid))

        # Get chapter links
        chapter_links = self.get_chapter_links(base_url, content)
        logger.info(f"  Found {len(chapter_links)} chapter links")

        # Limit to first 50 links to avoid timeout
        chapter_links = chapter_links[:50]

        # Scrape each chapter
        for i, chapter_url in enumerate(chapter_links):
            if i % 10 == 0:
                logger.info(f"  Scraping chapter {i+1}/{len(chapter_links)}...")

            try:
                chapter_content, chapter_text = self.scrape_page(chapter_url, wait_time=3000)
                if not chapter_content:
                    continue

                self.stats[jid]["pages"] += 1

                # Extract data
                results["ordinances"].extend(self.extract_ordinances(chapter_text, chapter_url, jid))
                results["overlays"].extend(self.extract_overlays(chapter_text, chapter_url, jid))
                results["bonuses"].extend(self.extract_bonuses(chapter_text, chapter_url, jid))
                results["timelines"].extend(self.extract_timelines(chapter_text, chapter_url, jid))

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                logger.error(f"  Error on chapter {i}: {e}")
                self.stats[jid]["errors"] += 1

        # Deduplicate
        seen_ords = set()
        unique_ords = []
        for o in results["ordinances"]:
            key = o["ordinance_number"]
            if key not in seen_ords:
                seen_ords.add(key)
                unique_ords.append(o)
        results["ordinances"] = unique_ords

        logger.info(f"  Found: {len(results['ordinances'])} ordinances, {len(results['overlays'])} overlays, {len(results['bonuses'])} bonuses, {len(results['timelines'])} timelines")

        # Upload results
        uploaded_ords = 0
        for o in results["ordinances"]:
            if self.upload_record("ordinances", o):
                uploaded_ords += 1

        for ov in results["overlays"]:
            self.upload_record("overlay_districts", ov)

        # Don't upload bonuses for Palm Bay (jid=2) - ground truth already exists
        if jid != 2:
            for b in results["bonuses"]:
                self.upload_record("development_bonuses", b)

        for t in results["timelines"]:
            self.upload_record("entitlement_timelines", t)

        self.stats[jid]["ordinances"] = uploaded_ords
        logger.info(f"  Uploaded: {uploaded_ords} new ordinances")

        return results

    def run(self):
        """Run the full scraper"""
        logger.info("=" * 60)
        logger.info("PLAYWRIGHT MUNICODE SCRAPER")
        logger.info("=" * 60)

        try:
            self.start_browser()

            for jid, slug in JURISDICTIONS.items():
                try:
                    self.scrape_jurisdiction(jid, slug)
                except Exception as e:
                    logger.error(f"Error scraping {slug}: {e}")
                    # Restart browser on failure
                    try:
                        self.stop_browser()
                        self.start_browser()
                    except:
                        pass

        finally:
            self.stop_browser()

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("SCRAPING COMPLETE")
        logger.info("=" * 60)

        total_pages = sum(s["pages"] for s in self.stats.values())
        total_ords = sum(s["ordinances"] for s in self.stats.values())
        total_errors = sum(s["errors"] for s in self.stats.values())

        logger.info(f"Total pages scraped: {total_pages}")
        logger.info(f"Total new ordinances: {total_ords}")
        logger.info(f"Total errors: {total_errors}")

        logger.info("\nBy jurisdiction:")
        for jid, slug in JURISDICTIONS.items():
            s = self.stats[jid]
            logger.info(f"  [{jid}] {slug}: {s['pages']} pages, {s['ordinances']} ords, {s['errors']} errors")


if __name__ == "__main__":
    scraper = MunicodeScraper()
    scraper.run()
