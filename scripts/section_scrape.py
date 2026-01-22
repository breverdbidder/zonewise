#!/usr/bin/env python3
"""
Section-level scraper - target specific section URLs that have actual content
Based on working pattern from first scrape
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
JINA_URL = "https://r.jina.ai/"

# Section-level URLs known to have content
# Using pattern from successful Melbourne ARTVDIRE and IHB APXAZO
SECTION_URLS = {
    # Melbourne - additional articles
    1: [
        "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVIIPAOF",
        "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTXIGERE",
    ],
    # Palm Bay - specific sections with content
    2: [
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH173DEST_ARTIDEBO",
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH173DEST_ARTIIDERE",
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH173DEST_ARTIIIDEST",
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH173DEST_ARTIVDEBOINAM",
    ],
    # Indian Harbour Beach - additional articles
    3: [
        "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTVSI",
        "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTVIENAM",
    ],
    # Satellite Beach - try specific articles
    4: [
        "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIGERE",
        "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIIREDI",
    ],
    # Indialantic - specific articles
    5: [
        "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTIGE",
        "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTIIREDI",
    ],
    # West Melbourne - articles
    7: [
        "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIGE",
        "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIIREDI",
    ],
    # Cocoa - articles
    8: [
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIGE",
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIREDI",
    ],
    # Cocoa Beach - articles
    9: [
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIGE",
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIREDI",
    ],
    # Rockledge - LDR parts
    10: [
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIZO",
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIIREDI",
    ],
    # Titusville - articles
    11: [
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIGE",
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIIREDI",
    ],
    # Cape Canaveral - articles
    12: [
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIGE",
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIIREDI",
    ],
    # Brevard County - articles
    13: [
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTIAD",
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTIIGE",
    ],
}


def fetch_with_jina(url: str) -> Optional[str]:
    """Fetch using Jina"""
    time.sleep(5)  # Longer delay
    try:
        client = httpx.Client(timeout=120)
        response = client.get(f"{JINA_URL}{url}", headers={"Accept": "text/plain"})
        client.close()
        if response.status_code == 200:
            return response.text
        elif response.status_code == 429:
            logger.warning("Rate limited, waiting 30s...")
            time.sleep(30)
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


def is_real_content(text: str) -> bool:
    """Check if content is actual code, not navigation"""
    if len(text) < 5000:
        return False
    # Check for indicators of real content
    indicators = ['Sec.', 'Section', '(Ord.', 'enacted', 'amended', 'passed']
    for ind in indicators:
        if ind in text:
            return True
    return False


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
            if re.match(r'^\d{4}$', ord_num):
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
    ]

    for pattern, otype in patterns:
        for match in re.finditer(pattern, text):
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
        (r'[Aa]ffordable\s+[Hh]ousing', "Affordable Housing Incentive", "Affordable Units"),
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
    logger.info("SECTION SCRAPE - Specific Article Pages")
    logger.info("=" * 60)

    totals = {"ordinances": 0, "overlays": 0, "timelines": 0, "bonuses": 0}

    for jid, urls in SECTION_URLS.items():
        logger.info(f"\n--- Jurisdiction {jid} ---")

        for url in urls:
            logger.info(f"  Fetching: {url[:65]}...")

            content = fetch_with_jina(url)
            if not content:
                logger.warning(f"    Failed to fetch")
                continue

            content_len = len(content)
            logger.info(f"    Got {content_len} chars")

            if not is_real_content(content):
                logger.info(f"    Skipping - not real content")
                continue

            # Extract and upload
            ords = extract_ordinances(content, url, jid)
            new_ords = 0
            for o in ords:
                if upload_record("ordinances", o):
                    new_ords += 1
                    totals["ordinances"] += 1

            overlays = extract_overlays(content, url, jid)
            new_overlays = 0
            for ov in overlays:
                if upload_record("overlay_districts", ov):
                    new_overlays += 1
                    totals["overlays"] += 1

            times = extract_timelines(content, url, jid)
            new_times = 0
            for t in times:
                if upload_record("entitlement_timelines", t):
                    new_times += 1
                    totals["timelines"] += 1

            bonuses = extract_bonuses(content, url, jid)
            new_bonuses = 0
            for b in bonuses:
                if upload_record("development_bonuses", b):
                    new_bonuses += 1
                    totals["bonuses"] += 1

            logger.info(f"    NEW: {new_ords} ords, {new_overlays} overlays, {new_times} times, {new_bonuses} bonuses")

    logger.info("\n" + "=" * 60)
    logger.info("SECTION SCRAPE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total NEW ordinances: {totals['ordinances']}")
    logger.info(f"Total NEW overlays: {totals['overlays']}")
    logger.info(f"Total NEW timelines: {totals['timelines']}")
    logger.info(f"Total NEW bonuses: {totals['bonuses']}")


if __name__ == "__main__":
    main()
