#!/usr/bin/env python3
"""
Deep scrape round 3 - Target additional Municode pages not covered in rounds 1-2
Focus on jurisdictions that yielded 0 results or have untapped content
Use different nodeId patterns and full section URLs
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

# Additional deep URLs - targeting pages NOT scraped in rounds 1-2
# Focus on specific section pages that often contain many ordinances
ROUND3_URLS = {
    # Palm Bay - try full chapter pages instead of article pages
    2: [
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO",  # Full zoning chapter
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTVRE",  # Regulations
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTXSI",  # Signs
        "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTXIPA",  # Parking
    ],
    # Satellite Beach - additional articles
    4: [
        "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIVDEST",  # Development standards
        "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTVUSRE",  # Use regulations
    ],
    # Indialantic - additional articles
    5: [
        "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTIVDEST",
        "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTVOFPRPA",
    ],
    # West Melbourne - additional sections
    7: [
        "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIVUSRE",
        "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTVDEST",
        "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTVIIISUAM",  # Amendments
    ],
    # Cocoa - additional sections
    8: [
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVGEPRDI",
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTVUSRE",
        "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTVIPLDEUS",  # Planned uses
    ],
    # Cocoa Beach - additional
    9: [
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVDEST",
        "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTVUSRE",
    ],
    # Rockledge - land development codes
    10: [
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVZO",  # Zoning
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVIIISU",  # Subdivision
        "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIXDEST",  # Development standards
    ],
    # Titusville - additional
    11: [
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIVGEPR",
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTVUSRE",
        "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTXAM",  # Amendments - good for ordinances
    ],
    # Cape Canaveral - additional
    12: [
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIVDEST",
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTVUSRE",
        "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTXAD",  # Admin - amendments
    ],
    # Brevard County - additional chapters
    13: [
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIIUSST",  # Use standards
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTIXDEST",  # Dev standards
        "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTXIIISUBDST",  # Subdivision
    ],
    # Melbourne - try additional articles that may have content
    1: [
        "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVIIIPA",  # Parking
        "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIXSI",  # Signs
        "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTXSUAM",  # Amendments
    ],
    # Indian Harbour Beach - additional
    3: [
        "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTVOFPA",
        "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTVISI",
    ],
}


def fetch_with_jina(url: str) -> Optional[str]:
    """Fetch using Jina with delay"""
    time.sleep(2)
    try:
        client = httpx.Client(timeout=120)
        response = client.get(f"{JINA_URL}{url}", headers={"Accept": "text/plain"})
        client.close()
        if response.status_code == 200:
            return response.text
        elif response.status_code == 429:
            logger.warning("Rate limited, waiting 20s...")
            time.sleep(20)
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


def extract_ordinances(text: str, url: str, jid: int) -> List[Dict]:
    """Extract ordinances from text - expanded patterns"""
    ordinances = []
    seen = set()

    # Expanded patterns to catch more formats
    patterns = [
        # Standard: (Ord. No. 2024-33, passed 9-19-24)
        r'\(Ord\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{2,4}[-–]\d{1,4})\s*,?[^)]*\)',
        # Just ordinance reference: Ord. 2024-33
        r'Ord(?:inance)?\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{4}[-–]\d+)',
        # Brackets: [Ord. 2024-33]
        r'\[Ord\.?\s*([A-Z]?[\d]{4}[-–]\d+)',
        # Section amended by: amended by Ord. 2024-33
        r'(?:amended|enacted|added|repealed)\s+by\s+Ord\.?\s*(?:No\.?\s*)?([A-Z]?[\d]{4}[-–]\d+)',
        # History citations: (Ord. 98-12; Ord. 2001-45)
        r'Ord\.?\s*(?:No\.?\s*)?(\d{2,4}[-–]\d{1,4})',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ord_num = match.group(1).replace('–', '-')
            if ord_num in seen or len(ord_num) < 4:
                continue
            seen.add(ord_num)

            # Try to extract date
            passed_date = None
            date_patterns = [
                r'passed\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'adopted\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            ]
            context = text[max(0, match.start()-50):min(len(text), match.end()+100)]
            for dp in date_patterns:
                dm = re.search(dp, context, re.IGNORECASE)
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
                    if passed_date:
                        break

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
        (r'[Dd]evelopment\s+[Oo]rder', "Development Order"),
        (r'[Cc]omprehensive\s+[Pp]lan\s+[Aa]mendment', "Comp Plan Amendment"),
        (r'[Aa]dministrative\s+[Aa]pproval', "Administrative Approval"),
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
    logger.info("DEEP SCRAPE ROUND 3 - Additional Pages")
    logger.info("=" * 60)

    totals = {"ordinances": 0, "overlays": 0, "timelines": 0, "bonuses": 0}

    for jid, urls in ROUND3_URLS.items():
        logger.info(f"\n--- Jurisdiction {jid} ---")

        for url in urls:
            logger.info(f"  Fetching: {url[:65]}...")

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

            logger.info(f"    NEW: {len(ords)} ords, {len(overlays)} overlays, {len(times)} times, {len(bonuses)} bonuses")

    logger.info("\n" + "=" * 60)
    logger.info("DEEP SCRAPE ROUND 3 COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total NEW ordinances: {totals['ordinances']}")
    logger.info(f"Total NEW overlays: {totals['overlays']}")
    logger.info(f"Total NEW timelines: {totals['timelines']}")
    logger.info(f"Total NEW bonuses: {totals['bonuses']}")


if __name__ == "__main__":
    main()
