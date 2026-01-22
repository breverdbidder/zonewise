#!/usr/bin/env python3
"""
Firecrawl-based scraper - better JS rendering for Municode pages
Targets URLs that Jina failed to render properly
"""

import os
import sys
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import httpx

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent / "agents" / "verify" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
FIRECRAWL_KEY = "fc-fa112951a2564765a2d146302774ac9b"

# URLs that Jina couldn't render properly - need Firecrawl's JS rendering
FIRECRAWL_URLS = {
    # Cocoa - full zoning chapter
    8: [
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVGEPRDI",
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTVUSRE",
    ],
    # Cocoa Beach
    9: [
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVDEST",
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTVUSRE",
    ],
    # Rockledge
    10: [
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVZO",
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIXDEST",
    ],
    # Titusville
    11: [
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTVUSRE",
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTVISP",
    ],
    # Cape Canaveral
    12: [
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTVUSRE",
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIVDEST",
    ],
    # Brevard County
    13: [
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIIUSST",
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTIXDEST",
    ],
}


def fetch_with_firecrawl(url: str) -> Optional[str]:
    """Fetch using Firecrawl API with JS rendering"""
    time.sleep(3)  # Rate limiting
    try:
        client = httpx.Client(timeout=120)
        response = client.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "url": url,
                "formats": ["markdown"],
                "waitFor": 3000,  # Wait for JS to render
            }
        )
        client.close()

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("data", {}).get("markdown", "")
        elif response.status_code == 429:
            logger.warning("Rate limited, waiting 30s...")
            time.sleep(30)
        else:
            logger.error(f"Firecrawl error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


def extract_ordinances(text: str, url: str, jid: int) -> List[Dict]:
    """Extract ordinances from text"""
    ordinances = []
    seen = set()

    patterns = [
        r'\(Ord\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{2,4}[-–]\d{1,4})\s*,?[^)]*\)',
        r'Ord(?:inance)?\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{4}[-–]\d+)',
        r'\[Ord\.?\s*([A-Z]?[\d]{4}[-–]\d+)',
        r'(?:amended|enacted|added)\s+by\s+Ord\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{4}[-–]\d+)',
        r'Ord\.?\s*(?:No\.?\s*)?(\d{2,4}[-–]\d{1,4})',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ord_num = match.group(1).replace('–', '-')
            if ord_num in seen or len(ord_num) < 4:
                continue
            seen.add(ord_num)

            passed_date = None
            context = text[max(0, match.start()-50):min(len(text), match.end()+100)]
            dm = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', context)
            if dm:
                for fmt in ['%m-%d-%y', '%m/%d/%y', '%m-%d-%Y', '%m/%d/%Y']:
                    try:
                        dt = datetime.strptime(dm.group(1), fmt)
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
            })

    return ordinances


def extract_overlays(text: str, url: str, jid: int) -> List[Dict]:
    """Extract overlay districts"""
    overlays = []
    seen = set()

    patterns = [
        (r'([A-Z]{2,5}[-\s]?O(?:V|VL)?)\s+(?:district|zone)', 'general'),
        (r'(\w+)\s+[Oo]verlay\s+[Dd]istrict', 'general'),
        (r'([Hh]istoric(?:al)?\s+[Dd]istrict)', 'historic'),
        (r'([Ff]lood(?:plain)?\s+[Oo]verlay)', 'flood'),
        (r'([Cc]oastal\s+[Hh]igh\s+[Hh]azard)', 'coastal'),
        (r'([Aa]irport\s+[Nn]oise)', 'airport'),
        (r'([Ww]aterfront\s+[Oo]verlay)', 'waterfront'),
        (r'([Dd]owntown\s+[Oo]verlay)', 'downtown'),
        (r'(PD[-\s]?O)', 'planned'),
    ]

    for pattern, otype in patterns:
        for match in re.finditer(pattern, text):
            name = match.group(1).strip()
            key = f"{jid}-{name.lower()}"
            if key in seen:
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


def extract_timelines(text: str, url: str, jid: int) -> List[Dict]:
    """Extract entitlement timelines"""
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
        if re.search(pattern, text):
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


def extract_bonuses(text: str, url: str, jid: int) -> List[Dict]:
    """Extract development bonuses"""
    bonuses = []
    seen = set()

    bonus_patterns = [
        (r'[Dd]ensity\s+[Bb]onus', "Density Bonus Program", "Increased Density"),
        (r'[Hh]eight\s+[Bb]onus', "Height Bonus Program", "Additional Height"),
        (r'[Pp]arking\s+[Rr]eduction', "Parking Reduction", "Reduced Parking"),
        (r'[Aa]ffordable\s+[Hh]ousing\s+[Bb]onus', "Affordable Housing Incentive", "Affordable Units"),
        (r'[Mm]ixed[- ][Uu]se\s+[Bb]onus', "Mixed Use Incentive", "Mixed Use"),
        (r'[Gg]reen\s+[Bb]uilding', "Green Building Program", "Sustainability"),
        (r'[Ii]mpact\s+[Ff]ee\s+[Cc]redit', "Impact Fee Credit", "Fee Reduction"),
    ]

    for pattern, program, feature in bonus_patterns:
        if re.search(pattern, text):
            key = f"{jid}-{program}"
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


def upload_record(table: str, record: Dict) -> bool:
    """Upload a record to Supabase"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=30)
    try:
        resp = client.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=headers, json=record)
        client.close()
        return resp.status_code in (200, 201)
    except:
        client.close()
        return False


def main():
    logger.info("=" * 60)
    logger.info("FIRECRAWL SCRAPE - JS Rendered Pages")
    logger.info("=" * 60)

    totals = {"ordinances": 0, "overlays": 0, "timelines": 0, "bonuses": 0}

    for jid, urls in FIRECRAWL_URLS.items():
        logger.info(f"\n--- Jurisdiction {jid} ---")

        for url in urls:
            logger.info(f"  Fetching: {url[:65]}...")

            content = fetch_with_firecrawl(url)
            if not content:
                logger.warning(f"    Failed to fetch")
                continue

            logger.info(f"    Got {len(content)} chars")

            # Extract and upload
            ords = extract_ordinances(content, url, jid)
            for o in ords:
                if upload_record("ordinances", o):
                    totals["ordinances"] += 1

            overlays = extract_overlays(content, url, jid)
            for ov in overlays:
                if upload_record("overlay_districts", ov):
                    totals["overlays"] += 1

            times = extract_timelines(content, url, jid)
            for t in times:
                if upload_record("entitlement_timelines", t):
                    totals["timelines"] += 1

            bonuses = extract_bonuses(content, url, jid)
            for b in bonuses:
                if upload_record("development_bonuses", b):
                    totals["bonuses"] += 1

            logger.info(f"    NEW: {len(ords)} ords, {len(overlays)} overlays, {len(times)} times, {len(bonuses)} bonuses")

    logger.info("\n" + "=" * 60)
    logger.info("FIRECRAWL SCRAPE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total NEW ordinances: {totals['ordinances']}")
    logger.info(f"Total NEW overlays: {totals['overlays']}")
    logger.info(f"Total NEW timelines: {totals['timelines']}")
    logger.info(f"Total NEW bonuses: {totals['bonuses']}")


if __name__ == "__main__":
    main()
