#!/usr/bin/env python3
"""
Full content scraper - target APXA/APXB full appendix pages
These pages have all content pre-loaded without JS rendering
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

# Full appendix pages that are known to have pre-loaded content
# Focus on APXA, APXB, full chapter pages
FULL_CONTENT_URLS = {
    # Satellite Beach - try full appendix
    4: [
        "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=APXAZO",
        "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=APXBSURE",
    ],
    # Indialantic - try appendix
    5: [
        "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=APXALA",
        "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=APXBZO",
    ],
    # West Melbourne - try LDR appendix
    7: [
        "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=APXALADERE",
        "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=APXALADERESO",
    ],
    # Cocoa - try appendix structure
    8: [
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=APXAZO",
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=APXBSUPLATST",
    ],
    # Cocoa Beach - appendix
    9: [
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=APXAZO",
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=APXBLADERE",
    ],
    # Rockledge - full LDR
    10: [
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE",
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIVZO",
    ],
    # Titusville - appendix
    11: [
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=APXALA",
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=APXBZO",
    ],
    # Cape Canaveral - appendix
    12: [
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=APXALA",
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=APXAZO",
    ],
    # Brevard County - full chapter
    13: [
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO",
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOI_CH22SU",
    ],
    # Palm Bay - try different structure
    2: [
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=APXALADERE",
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH173DEST",
    ],
}


def fetch_with_jina(url: str) -> Optional[str]:
    """Fetch using Jina with delay"""
    time.sleep(4)  # Longer delay for rate limiting
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


def extract_ordinances(text: str, url: str, jid: int) -> List[Dict]:
    """Extract ordinances from text - comprehensive patterns"""
    ordinances = []
    seen = set()

    # Multiple pattern variations
    patterns = [
        # Standard: (Ord. No. 2024-33, passed 9-19-24)
        r'\(Ord\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{2,4}[-–]\d{1,4})\s*,?[^)]*\)',
        # Just ordinance reference
        r'Ord(?:inance)?\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{4}[-–]\d+)',
        # Brackets style
        r'\[Ord\.?\s*([A-Z]?[\d]{4}[-–]\d+)',
        # Amended by references
        r'(?:amended|enacted|added|repealed)\s+by\s+Ord\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{4}[-–]\d+)',
        # Simple format
        r'Ord\.?\s*(?:No\.?\s*)?(\d{2,4}[-–]\d{1,4})',
        # Section history format
        r'History.*?Ord\.?\s*(\d{4}[-–]\d+)',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ord_num = match.group(1).replace('–', '-')
            # Skip if too short or already seen
            if ord_num in seen or len(ord_num) < 4:
                continue
            # Skip if it looks like a year
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
        (r'([Ww]aterfront\s+[Oo]verlay)', 'waterfront'),
        (r'([Dd]owntown\s+[Oo]verlay)', 'downtown'),
        (r'([Cc]orridor\s+[Oo]verlay)', 'corridor'),
        (r'([Rr]edevelopment\s+[Oo]verlay)', 'redevelopment'),
        (r'(PD[-\s]?O(?:verlay)?)', 'planned'),
        (r'(TOD|Transit.Oriented)', 'transit'),
        (r'([Ss]pecial\s+[Ff]lood\s+[Hh]azard)', 'flood'),
        (r'([Ee]nvironmental\s+[Oo]verlay)', 'environmental'),
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
        (r'[Dd]evelopment\s+[Oo]rder', "Development Order"),
        (r'[Cc]omprehensive\s+[Pp]lan\s+[Aa]mendment', "Comp Plan Amendment"),
        (r'[Mm]ajor\s+[Ss]ite\s+[Pp]lan', "Major Site Plan"),
        (r'[Mm]inor\s+[Ss]ite\s+[Pp]lan', "Minor Site Plan"),
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
        (r'[Ff]loor\s+[Aa]rea\s+[Rr]atio.*[Bb]onus', "FAR Bonus", "Increased FAR"),
        (r'[Tt]ransfer.*[Dd]evelopment\s+[Rr]ights', "TDR Program", "Development Rights Transfer"),
        (r'[Ee]xpedited\s+[Rr]eview', "Expedited Review", "Faster Processing"),
        (r'[Ff]ee\s+[Ww]aiver', "Fee Waiver Program", "Waived Fees"),
        (r'[Ii]ncentive\s+[Pp]rogram', "Development Incentive", "Incentive"),
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
    logger.info("FULL CONTENT SCRAPE - Appendix Pages")
    logger.info("=" * 60)

    totals = {"ordinances": 0, "overlays": 0, "timelines": 0, "bonuses": 0}

    for jid, urls in FULL_CONTENT_URLS.items():
        logger.info(f"\n--- Jurisdiction {jid} ---")

        for url in urls:
            logger.info(f"  Fetching: {url[:65]}...")

            content = fetch_with_jina(url)
            if not content:
                logger.warning(f"    Failed to fetch")
                continue

            content_len = len(content)
            logger.info(f"    Got {content_len} chars")

            # Skip if too small (navigation page)
            if content_len < 10000:
                logger.info(f"    Skipping - looks like navigation page")
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

            logger.info(f"    Extracted: {len(ords)} ords, {len(overlays)} overlays, {len(times)} times, {len(bonuses)} bonuses")
            logger.info(f"    NEW: {new_ords} ords, {new_overlays} overlays, {new_times} times, {new_bonuses} bonuses")

    logger.info("\n" + "=" * 60)
    logger.info("FULL CONTENT SCRAPE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total NEW ordinances: {totals['ordinances']}")
    logger.info(f"Total NEW overlays: {totals['overlays']}")
    logger.info(f"Total NEW timelines: {totals['timelines']}")
    logger.info(f"Total NEW bonuses: {totals['bonuses']}")


if __name__ == "__main__":
    main()
