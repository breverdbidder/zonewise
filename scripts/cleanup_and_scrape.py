#!/usr/bin/env python3
"""
Real Ordinance Scraper for ZoneWise
Scrapes ACTUAL data from Municode - NO fabrication
"""

import os
import sys
import json
import re
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import httpx

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
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
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_API_KEY", "fc-fa112951a2564765a2d146302774ac9b")

JINA_URL = "https://r.jina.ai/"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"
REQUEST_DELAY = 2.0

# Jurisdictions
JURISDICTIONS = {
    2: {"name": "Palm Bay", "slug": "palm_bay", "priority": "VALIDATION"},
    1: {"name": "Melbourne", "slug": "melbourne", "priority": "HIGH"},
    3: {"name": "Indian Harbour Beach", "slug": "indian_harbour_beach", "priority": "HIGH"},
    4: {"name": "Satellite Beach", "slug": "satellite_beach", "priority": "HIGH"},
    13: {"name": "Brevard County", "slug": "brevard_county", "priority": "HIGH"},
    5: {"name": "Indialantic", "slug": "indialantic", "priority": "MEDIUM"},
    6: {"name": "Melbourne Beach", "slug": "melbourne_beach", "priority": "MEDIUM"},
    7: {"name": "West Melbourne", "slug": "west_melbourne", "priority": "MEDIUM"},
    8: {"name": "Cocoa", "slug": "cocoa", "priority": "MEDIUM"},
    9: {"name": "Cocoa Beach", "slug": "cocoa_beach", "priority": "MEDIUM"},
    10: {"name": "Rockledge", "slug": "rockledge", "priority": "MEDIUM"},
    11: {"name": "Titusville", "slug": "titusville", "priority": "MEDIUM"},
    12: {"name": "Cape Canaveral", "slug": "cape_canaveral", "priority": "MEDIUM"},
    14: {"name": "Malabar", "slug": "malabar", "priority": "LOW"},
    15: {"name": "Palm Shores", "slug": "palm_shores", "priority": "LOW"},
    16: {"name": "Grant-Valkaria", "slug": "grant-valkaria", "priority": "LOW"},
    17: {"name": "Melbourne Village", "slug": "melbourne_village", "priority": "LOW"},
}


class MunicodeScraper:
    """Scraper for Municode using Firecrawl and Jina"""

    def __init__(self):
        self.client = httpx.Client(timeout=120.0)
        self.last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request = time.time()

    def fetch_with_firecrawl(self, url: str) -> Optional[str]:
        """Fetch using Firecrawl (handles JS rendering)"""
        self._rate_limit()

        try:
            response = self.client.post(
                FIRECRAWL_URL,
                headers={
                    "Authorization": f"Bearer {FIRECRAWL_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": url,
                    "formats": ["markdown"],
                    "waitFor": 3000
                },
                timeout=60.0
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {}).get("markdown", "")

            logger.warning(f"Firecrawl returned {response.status_code}")

        except Exception as e:
            logger.error(f"Firecrawl error: {e}")

        return None

    def fetch_with_jina(self, url: str) -> Optional[str]:
        """Fetch using Jina Reader (fallback)"""
        self._rate_limit()

        try:
            response = self.client.get(
                f"{JINA_URL}{url}",
                headers={"Accept": "text/plain"},
                timeout=60.0
            )

            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                logger.warning("Jina rate limited, waiting...")
                time.sleep(10)

        except Exception as e:
            logger.error(f"Jina error: {e}")

        return None

    def fetch(self, url: str) -> Optional[str]:
        """Fetch URL content, trying Firecrawl first then Jina"""
        # Try Firecrawl first
        content = self.fetch_with_firecrawl(url)
        if content and len(content) > 1000:
            return content

        # Fallback to Jina
        content = self.fetch_with_jina(url)
        return content

    def close(self):
        self.client.close()


def extract_real_ordinances(text: str, url: str, jid: int) -> List[Dict]:
    """Extract REAL ordinance references from scraped text"""
    ordinances = []
    seen = set()

    # Pattern for real Municode ordinance citations
    # Examples: "(Ord. 2024-33, passed 9-19-24)" or "(Ord. No. 2020-15, § 2)"
    patterns = [
        r'\(Ord\.?\s*(?:No\.?\s*)?([\d]{2,4}[-–]\d{1,4})\s*,?\s*(?:passed\s+)?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})?\)',
        r'\(Ord\.?\s*(?:No\.?\s*)?([\d]{4}[-–]\d+)[,;]',
        r'Ord(?:inance)?\.?\s*(?:No\.?\s*)?([\d]{4}[-–]\d+)',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ord_num = match.group(1).replace('–', '-')

            if ord_num in seen or len(ord_num) < 4:
                continue
            seen.add(ord_num)

            # Get surrounding context as raw_scraped_text
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].strip()

            # Try to extract date
            passed_date = None
            if len(match.groups()) > 1 and match.group(2):
                date_str = match.group(2)
                for fmt in ['%m-%d-%y', '%m/%d/%y', '%m-%d-%Y', '%m/%d/%Y']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        # Handle 2-digit years
                        if dt.year > 2050:
                            dt = dt.replace(year=dt.year - 100)
                        passed_date = dt.date().isoformat()
                        break
                    except:
                        continue

            ordinances.append({
                "jurisdiction_id": jid,
                "ordinance_number": ord_num,
                "title": ord_num,
                "source_url": url,
                "passed_date": passed_date,
                "raw_scraped_text": context,
            })

    return ordinances


def extract_overlay_districts(text: str, url: str, jid: int) -> List[Dict]:
    """Extract overlay district information"""
    overlays = []
    seen = set()

    # Look for overlay district mentions
    overlay_patterns = [
        r'([A-Z]{2,5}[-\s]?(?:O|OV|OVL|OVERLAY))\s+(?:district|zone)',
        r'(\w+)\s+[Oo]verlay\s+[Dd]istrict',
        r'([Hh]istoric(?:al)?\s+[Dd]istrict)',
        r'([Ff]lood(?:plain)?\s+[Oo]verlay)',
        r'([Cc]oastal\s+[Hh]igh\s+[Hh]azard)',
        r'([Aa]irport\s+[Nn]oise\s+[Zz]one)',
    ]

    for pattern in overlay_patterns:
        for match in re.finditer(pattern, text):
            overlay_name = match.group(1).strip()
            key = f"{jid}-{overlay_name.lower()}"

            if key in seen:
                continue
            seen.add(key)

            # Get context
            start = max(0, match.start() - 150)
            end = min(len(text), match.end() + 150)
            context = text[start:end].strip()

            # Determine overlay type
            name_lower = overlay_name.lower()
            if 'flood' in name_lower:
                overlay_type = 'flood'
            elif 'historic' in name_lower:
                overlay_type = 'historic'
            elif 'coastal' in name_lower:
                overlay_type = 'coastal'
            elif 'airport' in name_lower or 'noise' in name_lower:
                overlay_type = 'airport'
            else:
                overlay_type = 'general'

            overlays.append({
                "jurisdiction_id": jid,
                "overlay_name": overlay_name,
                "overlay_code": overlay_name[:10].upper().replace(' ', '-'),
                "overlay_type": overlay_type,
                "source_url": url,
                "raw_scraped_text": context,
            })

    return overlays


def extract_entitlement_processes(text: str, url: str, jid: int) -> List[Dict]:
    """Extract entitlement timeline information"""
    timelines = []
    seen = set()

    # Look for process descriptions with timeframes
    process_patterns = [
        (r'[Ss]ite\s+[Pp]lan\s+[Rr]eview', "Site Plan Review"),
        (r'[Rr]ezon(?:e|ing)', "Rezoning"),
        (r'[Cc]onditional\s+[Uu]se\s+[Pp]ermit', "Conditional Use Permit"),
        (r'[Ss]pecial\s+[Ee]xception', "Special Exception"),
        (r'[Vv]ariance', "Variance"),
        (r'[Pp]reliminary\s+[Pp]lat', "Preliminary Plat"),
        (r'[Ff]inal\s+[Pp]lat', "Final Plat"),
        (r'[Pp]lanned\s+[Uu]nit\s+[Dd]evelopment', "Planned Unit Development"),
    ]

    for pattern, process_type in process_patterns:
        if re.search(pattern, text):
            key = f"{jid}-{process_type}"
            if key in seen:
                continue
            seen.add(key)

            # Find context around the match
            match = re.search(pattern, text)
            if match:
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end].strip()

                # Try to extract days/timeframes
                days_match = re.search(r'(\d+)\s*(?:calendar\s+)?days?', context, re.IGNORECASE)
                typical_days = int(days_match.group(1)) if days_match else None

                timelines.append({
                    "jurisdiction_id": jid,
                    "process_type": process_type,
                    "typical_days_avg": typical_days,
                    "steps": [],  # Required field
                    "source_url": url,
                    "raw_scraped_text": context,
                })

    return timelines


def upload_record(table: str, record: Dict) -> bool:
    """Upload a single record to Supabase"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    # Remove raw_scraped_text for now as it may not be in schema
    clean_record = {k: v for k, v in record.items() if k != 'raw_scraped_text'}

    client = httpx.Client(timeout=30)
    try:
        resp = client.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers=headers,
            json=clean_record
        )
        client.close()
        return resp.status_code in (200, 201)
    except:
        client.close()
        return False


def delete_test_records():
    """Delete test records from conditional_uses"""
    logger.info("Cleaning up test records...")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    client = httpx.Client(timeout=30)

    # Delete test records (district_code starts with T)
    resp = client.delete(
        f"{SUPABASE_URL}/rest/v1/conditional_uses?district_code=like.T*",
        headers=headers
    )
    logger.info(f"Deleted test conditional_uses: {resp.status_code}")

    # Delete records with bad use_name
    resp = client.delete(
        f"{SUPABASE_URL}/rest/v1/conditional_uses?use_name=eq.Test",
        headers=headers
    )

    client.close()


def get_zoning_chapter_urls(slug: str) -> List[str]:
    """Get URLs for zoning-related chapters"""
    base_url = f"https://library.municode.com/fl/{slug}/codes/code_of_ordinances"

    # Common chapter patterns for Florida municipalities
    chapter_patterns = [
        f"{base_url}?nodeId=PTIICOOR_CH166ZO",  # Palm Bay
        f"{base_url}?nodeId=PTIIILADERE_APXBZO",  # Melbourne
        f"{base_url}?nodeId=COOR_CH13ZO",  # Cocoa style
        f"{base_url}?nodeId=APXAZO",  # Indian Harbour Beach
        f"{base_url}?nodeId=COORBRCOFLVOII_CH62ZO",  # Brevard County
    ]

    return [base_url] + chapter_patterns


def scrape_jurisdiction(jid: int, scraper: MunicodeScraper) -> Dict[str, int]:
    """Scrape a single jurisdiction"""
    config = JURISDICTIONS[jid]
    name = config["name"]
    slug = config["slug"]

    logger.info(f"\n{'='*60}")
    logger.info(f"[{jid}/17] {name}: {config['priority']}")
    logger.info(f"{'='*60}")

    results = {
        "pages_scraped": 0,
        "ordinances": 0,
        "overlays": 0,
        "timelines": 0,
    }

    urls = get_zoning_chapter_urls(slug)

    for url in urls:
        logger.info(f"  Fetching: {url[:70]}...")

        content = scraper.fetch(url)
        if not content:
            logger.warning(f"    Failed to fetch")
            continue

        results["pages_scraped"] += 1
        logger.info(f"    Got {len(content)} chars")

        # Extract ordinances
        ords = extract_real_ordinances(content, url, jid)
        for o in ords:
            if upload_record("ordinances", o):
                results["ordinances"] += 1

        # Extract overlays
        overlays = extract_overlay_districts(content, url, jid)
        for ov in overlays:
            if upload_record("overlay_districts", ov):
                results["overlays"] += 1

        # Extract timelines
        timelines = extract_entitlement_processes(content, url, jid)
        for t in timelines:
            if upload_record("entitlement_timelines", t):
                results["timelines"] += 1

        logger.info(f"    Found: {len(ords)} ords, {len(overlays)} overlays, {len(timelines)} timelines")

    logger.info(f"  TOTAL: {results}")
    return results


def main():
    logger.info("=" * 60)
    logger.info("REAL ORDINANCE SCRAPER - NO FAKE DATA")
    logger.info("=" * 60)

    # Clean up test records first
    delete_test_records()

    scraper = MunicodeScraper()
    all_results = {}

    # Process in priority order
    priority_order = ["VALIDATION", "HIGH", "MEDIUM", "LOW"]

    for priority in priority_order:
        jids = [jid for jid, cfg in JURISDICTIONS.items() if cfg["priority"] == priority]

        for jid in jids:
            try:
                results = scrape_jurisdiction(jid, scraper)
                all_results[jid] = results
            except Exception as e:
                logger.error(f"Error scraping jurisdiction {jid}: {e}")
                all_results[jid] = {"error": str(e)}

    scraper.close()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SCRAPING COMPLETE - SUMMARY")
    logger.info("=" * 60)

    total_ords = sum(r.get("ordinances", 0) for r in all_results.values())
    total_overlays = sum(r.get("overlays", 0) for r in all_results.values())
    total_timelines = sum(r.get("timelines", 0) for r in all_results.values())

    logger.info(f"Total ordinances: {total_ords}")
    logger.info(f"Total overlays: {total_overlays}")
    logger.info(f"Total timelines: {total_timelines}")


if __name__ == "__main__":
    main()
