#!/usr/bin/env python3
"""
Comprehensive Extraction for Ordinances, Timelines, and Bonuses
Targets specific sections of Municode for each jurisdiction
"""

import os
import sys
import json
import re
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
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

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
JINA_URL = "https://r.jina.ai/"
REQUEST_DELAY = 1.5


class JinaReader:
    def __init__(self):
        self.client = httpx.Client(timeout=120.0)
        self.last_request = 0

    def fetch(self, url: str) -> Optional[str]:
        elapsed = time.time() - self.last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request = time.time()

        try:
            response = self.client.get(
                f"{JINA_URL}{url}",
                headers={"Accept": "text/plain"}
            )
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.error(f"Fetch error: {e}")
        return None

    def close(self):
        self.client.close()


# Comprehensive URL targets focusing on procedures, bonuses, and all ordinances
EXTRACTION_TARGETS = {
    1: {
        "name": "Melbourne",
        "urls": [
            # Core zoning articles
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIINGE",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIIIDE",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIVUS",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVDIRE",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVIST",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVIIIUS",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIXSUST",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTXIOVDI",
            # Development procedures
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_CH1GEPR",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_CH2ADPR",
        ]
    },
    2: {
        "name": "Palm Bay",
        "urls": [
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIINGE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIIIDE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIIIAG",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIVREDI",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTVCODE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTVIINDE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTVIIIBUST",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIXINPA",
        ]
    },
    3: {
        "name": "Titusville",
        "urls": [
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIINGE",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIIIZODI",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIVUSRE",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTVDERE",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTXSP",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTXIAD",
        ]
    },
    4: {
        "name": "West Melbourne",
        "urls": [
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIIIZODIEST",
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIVSPEX",
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTVPRUS",
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTVIIIAD",
        ]
    },
    5: {
        "name": "Rockledge",
        "urls": [
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIIAD",
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIIIBA",
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVIPLDIZO",
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVIIIDERE",
        ]
    },
    6: {
        "name": "Cocoa",
        "urls": [
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIINGE",
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIIZODI",
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVUSRE",
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTVAD",
        ]
    },
    7: {
        "name": "Cocoa Beach",
        "urls": [
            "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIIZODI",
            "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVDEST",
            "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTVAD",
        ]
    },
    8: {
        "name": "Cape Canaveral",
        "urls": [
            "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIIIZODI",
            "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIVDEST",
            "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTVAD",
        ]
    },
    9: {
        "name": "Satellite Beach",
        "urls": [
            "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIIIZODI",
            "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIVPRUS",
            "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTVAD",
        ]
    },
    10: {
        "name": "Indian Harbour Beach",
        "urls": [
            "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTIIIZODI",
            "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTIVDEST",
        ]
    },
    11: {
        "name": "Indialantic",
        "urls": [
            "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTIIIZODI",
            "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTVUSRE",
        ]
    },
    12: {
        "name": "Melbourne Beach",
        "urls": [
            "https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH26ZO_ARTIIIZODI",
            "https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH26ZO_ARTIVDEST",
        ]
    },
    13: {
        "name": "Melbourne Village",
        "urls": [
            "https://library.municode.com/fl/melbourne_village/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ]
    },
    14: {
        "name": "Palm Shores",
        "urls": [
            "https://library.municode.com/fl/palm_shores/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ]
    },
    15: {
        "name": "Malabar",
        "urls": [
            "https://library.municode.com/fl/malabar/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ]
    },
    16: {
        "name": "Grant-Valkaria",
        "urls": [
            "https://library.municode.com/fl/grant-valkaria/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ]
    },
    17: {
        "name": "Brevard County",
        "urls": [
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTIINGE",
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIZODI",
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIIDEST",
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTIXAD",
        ]
    },
}


def extract_ordinances(text: str, jid: int, url: str) -> List[Dict]:
    """Extract ordinance references"""
    ordinances = []
    seen = set()

    patterns = [
        r'\(Ord\.?\s*(?:No\.?\s*)?(\d{4}[-\u2013]\d+)',
        r'Ord\.?\s*(?:No\.?\s*)?(\d{4}[-\u2013]\d+)',
        r'Ordinance\s+(?:No\.?\s*)?(\d{2,4}[-\u2013]\d{1,4})',
        r'adopted\s+by\s+Ord(?:inance)?\.?\s*(\d{4}[-\u2013]\d+)',
        r'as\s+amended\s+by\s+Ord\.?\s*(\d{4}[-\u2013]\d+)',
        r'\[Ord\.?\s*(\d{4}[-\u2013]\d+)',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ord_num = match.group(1).replace('\u2013', '-')
            if ord_num in seen or len(ord_num) < 4:
                continue
            seen.add(ord_num)

            # Extract date
            context = text[max(0, match.start()-200):min(len(text), match.end()+200)]
            date = None
            date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', context)
            if date_match:
                for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y']:
                    try:
                        date = datetime.strptime(date_match.group(1), fmt).date().isoformat()
                        break
                    except:
                        continue

            ordinances.append({
                "jurisdiction_id": jid,
                "ordinance_number": ord_num,
                "title": ord_num,
                "source_url": url,
                "passed_date": date,
            })

    return ordinances


def extract_timelines(text: str, jid: int, url: str) -> List[Dict]:
    """Extract development process timelines"""
    timelines = []
    seen = set()

    # Look for process types with time references
    process_patterns = [
        (r'(?:site\s+plan|development)\s+review', "Site Plan Review"),
        (r'rezon(?:e|ing)', "Rezoning"),
        (r'conditional\s+use\s+(?:permit|approval)', "Conditional Use Permit"),
        (r'special\s+exception', "Special Exception"),
        (r'variance', "Variance"),
        (r'plat(?:ting)?\s+(?:approval|review)', "Plat Approval"),
        (r'preliminary\s+plat', "Preliminary Plat"),
        (r'final\s+plat', "Final Plat"),
        (r'building\s+permit', "Building Permit"),
        (r'planned\s+(?:unit|development)', "Planned Development"),
        (r'comprehensive\s+plan\s+amendment', "Comprehensive Plan Amendment"),
        (r'(?:zoning|text)\s+amendment', "Zoning Amendment"),
        (r'annexation', "Annexation"),
        (r'development\s+agreement', "Development Agreement"),
    ]

    for pattern, process_type in process_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            key = f"{jid}-{process_type}"
            if key not in seen:
                seen.add(key)
                timelines.append({
                    "jurisdiction_id": jid,
                    "process_type": process_type,
                    "steps": [],
                    "source_url": url,
                })

    return timelines


def extract_bonuses(text: str, jid: int, url: str) -> List[Dict]:
    """Extract development bonuses and incentives"""
    bonuses = []
    seen = set()

    # Look for bonus/incentive patterns
    bonus_patterns = [
        (r'density\s+bonus', "Density Bonus Program", "Increased Density"),
        (r'height\s+bonus', "Height Bonus Program", "Additional Height"),
        (r'floor\s+area\s+(?:ratio|bonus)', "FAR Bonus", "Increased FAR"),
        (r'parking\s+reduction', "Parking Reduction", "Reduced Parking"),
        (r'affordable\s+housing\s+(?:bonus|incentive)', "Affordable Housing Incentive", "Affordable Units"),
        (r'transfer\s+of\s+development\s+rights', "TDR Program", "Development Rights Transfer"),
        (r'(?:tax|fee)\s+(?:incentive|abatement|credit)', "Tax Incentive", "Tax Benefits"),
        (r'impact\s+fee\s+(?:waiver|reduction|credit)', "Impact Fee Credit", "Fee Reduction"),
        (r'expedited\s+(?:review|permitting)', "Expedited Review", "Faster Processing"),
        (r'mixed[- ]use\s+(?:bonus|incentive)', "Mixed Use Incentive", "Mixed Use Development"),
        (r'green\s+building\s+(?:bonus|incentive)', "Green Building Program", "Sustainability Features"),
        (r'workforce\s+housing', "Workforce Housing Incentive", "Workforce Units"),
    ]

    for pattern, program_name, feature_name in bonus_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            key = f"{jid}-{program_name}"
            if key not in seen:
                seen.add(key)
                bonuses.append({
                    "jurisdiction_id": jid,
                    "program_name": program_name,
                    "feature_name": feature_name,
                    "source_url": url,
                })

    return bonuses


def upload_records(table: str, records: List[Dict]) -> int:
    """Upload records to Supabase"""
    if not records:
        return 0

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0

    for record in records:
        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/{table}",
                headers=headers,
                json=record
            )
            if resp.status_code in (200, 201):
                saved += 1
        except:
            pass

    client.close()
    return saved


def main():
    logger.info("=" * 60)
    logger.info("COMPREHENSIVE EXTRACTION")
    logger.info("=" * 60)

    jina = JinaReader()

    all_ordinances = []
    all_timelines = []
    all_bonuses = []

    for jid, config in EXTRACTION_TARGETS.items():
        name = config["name"]
        urls = config["urls"]

        logger.info(f"\n--- {name} (ID: {jid}) ---")

        for url in urls:
            logger.info(f"  Fetching: {url[:60]}...")
            content = jina.fetch(url)

            if content:
                logger.info(f"    Got {len(content)} chars")

                ords = extract_ordinances(content, jid, url)
                all_ordinances.extend(ords)
                logger.info(f"    Ordinances: {len(ords)}")

                times = extract_timelines(content, jid, url)
                all_timelines.extend(times)
                logger.info(f"    Timelines: {len(times)}")

                bonus = extract_bonuses(content, jid, url)
                all_bonuses.extend(bonus)
                logger.info(f"    Bonuses: {len(bonus)}")
            else:
                logger.warning(f"    Failed to fetch")

    jina.close()

    # Deduplicate
    def dedup(records, key_fn):
        seen = set()
        unique = []
        for r in records:
            key = key_fn(r)
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    unique_ords = dedup(all_ordinances, lambda r: f"{r['jurisdiction_id']}-{r['ordinance_number']}")
    unique_times = dedup(all_timelines, lambda r: f"{r['jurisdiction_id']}-{r['process_type']}")
    unique_bonuses = dedup(all_bonuses, lambda r: f"{r['jurisdiction_id']}-{r['program_name']}")

    logger.info(f"\n--- EXTRACTION SUMMARY ---")
    logger.info(f"Ordinances: {len(unique_ords)}")
    logger.info(f"Timelines: {len(unique_times)}")
    logger.info(f"Bonuses: {len(unique_bonuses)}")

    # Upload
    logger.info(f"\n--- UPLOADING ---")
    ord_saved = upload_records("ordinances", unique_ords)
    logger.info(f"Ordinances uploaded: {ord_saved}")

    time_saved = upload_records("entitlement_timelines", unique_times)
    logger.info(f"Timelines uploaded: {time_saved}")

    bonus_saved = upload_records("development_bonuses", unique_bonuses)
    logger.info(f"Bonuses uploaded: {bonus_saved}")

    # Save to JSON
    output_path = Path(__file__).parent.parent / "data" / f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump({
            "ordinances": unique_ords,
            "timelines": unique_times,
            "bonuses": unique_bonuses,
        }, f, indent=2)
    logger.info(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
