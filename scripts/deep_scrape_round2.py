#!/usr/bin/env python3
"""
Deep scrape round 2 - Target known-good Municode content pages
Focus on the full zoning article/chapter pages that contain actual ordinance citations
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
JINA_URL = "https://r.jina.ai/"

# Known-good deep URLs that contain actual content (not just navigation)
# These are the specific article/chapter pages with full text
DEEP_URLS = {
    1: [  # Melbourne - found 72 ordinances from ARTVDIRE
        "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVDIRE",
        "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIIIDE",
        "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIVUS",
        "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVIST",
    ],
    2: [  # Palm Bay
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIIIDE",
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIVREDI",
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH173DEST",
    ],
    3: [  # Indian Harbour Beach - found 28 ordinances from APXAZO
        "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO",
        "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTIIIZODI",
        "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTIVDEST",
    ],
    4: [  # Satellite Beach
        "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO",
        "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIIIZODI",
    ],
    5: [  # Indialantic
        "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO",
        "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTIIIZODI",
    ],
    7: [  # West Melbourne
        "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO",
        "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIIIZODIEST",
    ],
    8: [  # Cocoa
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO",
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIIZODI",
    ],
    9: [  # Cocoa Beach
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO",
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIIZODI",
    ],
    10: [  # Rockledge
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVIPLDIZO",
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIIIBA",
    ],
    11: [  # Titusville
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO",
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIIIZODI",
    ],
    12: [  # Cape Canaveral
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO",
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIIIZODI",
    ],
    13: [  # Brevard County
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO",
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIZODI",
    ],
}


def fetch_with_jina(url: str) -> Optional[str]:
    """Fetch using Jina with delay"""
    time.sleep(3)  # Longer delay to avoid rate limits
    try:
        client = httpx.Client(timeout=120)
        response = client.get(f"{JINA_URL}{url}", headers={"Accept": "text/plain"})
        client.close()
        if response.status_code == 200:
            return response.text
        elif response.status_code == 429:
            logger.warning("Rate limited, waiting 15s...")
            time.sleep(15)
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


def extract_ordinances(text: str, url: str, jid: int) -> List[Dict]:
    """Extract ordinances from text"""
    ordinances = []
    seen = set()

    patterns = [
        r'\(Ord\.?\s*(?:No\.?\s*)?([\d]{2,4}[-–]\d{1,4})\s*,?\s*(?:passed\s+)?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})?\)',
        r'\(Ord\.?\s*(?:No\.?\s*)?([\d]{4}[-–]\d+)[,;]',
        r'Ord(?:inance)?\.?\s*(?:No\.?\s*)?([\d]{4}[-–]\d+)',
        r'\[Ord\.?\s*([\d]{4}[-–]\d+)',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ord_num = match.group(1).replace('–', '-')
            if ord_num in seen or len(ord_num) < 4:
                continue
            seen.add(ord_num)

            passed_date = None
            if len(match.groups()) > 1 and match.group(2):
                for fmt in ['%m-%d-%y', '%m/%d/%y', '%m-%d-%Y', '%m/%d/%Y']:
                    try:
                        dt = datetime.strptime(match.group(2), fmt)
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
    logger.info("DEEP SCRAPE ROUND 2")
    logger.info("=" * 60)

    totals = {"ordinances": 0, "overlays": 0, "timelines": 0, "bonuses": 0}

    for jid, urls in DEEP_URLS.items():
        logger.info(f"\n--- Jurisdiction {jid} ---")

        for url in urls:
            logger.info(f"  Fetching: {url[:60]}...")

            content = fetch_with_jina(url)
            if not content:
                logger.warning(f"    Failed")
                continue

            logger.info(f"    Got {len(content)} chars")

            # Extract and upload ordinances
            ords = extract_ordinances(content, url, jid)
            for o in ords:
                if upload_record("ordinances", o):
                    totals["ordinances"] += 1

            # Extract and upload overlays
            overlays = extract_overlays(content, url, jid)
            for ov in overlays:
                if upload_record("overlay_districts", ov):
                    totals["overlays"] += 1

            # Extract and upload timelines
            times = extract_timelines(content, url, jid)
            for t in times:
                if upload_record("entitlement_timelines", t):
                    totals["timelines"] += 1

            # Extract and upload bonuses
            bonuses = extract_bonuses(content, url, jid)
            for b in bonuses:
                if upload_record("development_bonuses", b):
                    totals["bonuses"] += 1

            logger.info(f"    Found: {len(ords)} ords, {len(overlays)} overlays, {len(times)} times, {len(bonuses)} bonuses")

    logger.info("\n" + "=" * 60)
    logger.info("DEEP SCRAPE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total new ordinances: {totals['ordinances']}")
    logger.info(f"Total new overlays: {totals['overlays']}")
    logger.info(f"Total new timelines: {totals['timelines']}")
    logger.info(f"Total new bonuses: {totals['bonuses']}")


if __name__ == "__main__":
    main()
