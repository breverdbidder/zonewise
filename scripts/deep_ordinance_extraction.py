#!/usr/bin/env python3
"""
Deep Ordinance Extraction
========================
Targets specific zoning code sections to maximize ordinance extraction.
Uses Jina Reader to get full content from Municode pages.
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

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

JINA_URL = "https://r.jina.ai/"
REQUEST_DELAY = 2.0

# Comprehensive URL targets for each jurisdiction
DEEP_TARGETS = {
    1: {  # Melbourne
        "name": "Melbourne",
        "urls": [
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIINGE",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIIIDE",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIVUS",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVDIRE",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVIST",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVIIIUS",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTIXSUST",
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTXIOVDI",
        ]
    },
    2: {  # Palm Bay
        "name": "Palm Bay",
        "urls": [
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIINGE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIIIDE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIIIAG",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIVREDI",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTVCODE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTVIINDE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTVIIIBUST",
        ]
    },
    3: {  # Titusville
        "name": "Titusville",
        "urls": [
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIINGE",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIIIZODI",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIVUSRE",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTVDERE",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTXSP",
        ]
    },
    4: {  # West Melbourne
        "name": "West Melbourne",
        "urls": [
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIIIZODIEST",
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIVSPEX",
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTVPRUS",
        ]
    },
    5: {  # Rockledge
        "name": "Rockledge",
        "urls": [
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIIAD",
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIIIBA",
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVIPLDIZO",
        ]
    },
    6: {  # Cocoa
        "name": "Cocoa",
        "urls": [
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIINGE",
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIIZODI",
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVUSRE",
        ]
    },
    7: {  # Cocoa Beach
        "name": "Cocoa Beach",
        "urls": [
            "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIIZODI",
            "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVDEST",
        ]
    },
    8: {  # Cape Canaveral
        "name": "Cape Canaveral",
        "urls": [
            "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIIIZODI",
            "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIVDEST",
        ]
    },
    9: {  # Satellite Beach
        "name": "Satellite Beach",
        "urls": [
            "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIIIZODI",
            "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIVPRUS",
        ]
    },
    10: {  # Indian Harbour Beach
        "name": "Indian Harbour Beach",
        "urls": [
            "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTIIIZODI",
            "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTIVDEST",
        ]
    },
    11: {  # Indialantic
        "name": "Indialantic",
        "urls": [
            "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTIIIZODI",
            "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTVUSRE",
        ]
    },
    12: {  # Melbourne Beach
        "name": "Melbourne Beach",
        "urls": [
            "https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH26ZO_ARTIIIZODI",
            "https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH26ZO_ARTIVDEST",
        ]
    },
    13: {  # Melbourne Village
        "name": "Melbourne Village",
        "urls": [
            "https://library.municode.com/fl/melbourne_village/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ]
    },
    14: {  # Palm Shores
        "name": "Palm Shores",
        "urls": [
            "https://library.municode.com/fl/palm_shores/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ]
    },
    15: {  # Malabar
        "name": "Malabar",
        "urls": [
            "https://library.municode.com/fl/malabar/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ]
    },
    16: {  # Grant-Valkaria
        "name": "Grant-Valkaria",
        "urls": [
            "https://library.municode.com/fl/grant-valkaria/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ]
    },
    17: {  # Brevard County
        "name": "Brevard County",
        "urls": [
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTIINGE",
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIZODI",
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIIDEST",
        ]
    },
}


class JinaReader:
    """Jina Reader for content extraction"""

    def __init__(self):
        self.client = httpx.Client(timeout=120.0)
        self.last_request = 0

    def fetch(self, url: str) -> Optional[str]:
        """Fetch content using Jina Reader"""
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
            logger.error(f"Jina fetch error: {e}")

        return None

    def close(self):
        self.client.close()


def extract_ordinances(text: str, jid: int, jname: str, url: str) -> List[Dict]:
    """Extract ordinance references from text"""
    ordinances = []
    seen = set()

    # Multiple patterns for ordinance references
    patterns = [
        r'\(Ord\.?\s*(?:No\.?\s*)?(\d{4}[-–]\d+)',
        r'Ord\.?\s*(?:No\.?\s*)?(\d{4}[-–]\d+)',
        r'Ordinance\s+(?:No\.?\s*)?(\d{2,4}[-–]\d{1,4})',
        r'adopted\s+by\s+Ord(?:inance)?\.?\s*(\d{4}[-–]\d+)',
        r'as\s+amended\s+by\s+Ord\.?\s*(\d{4}[-–]\d+)',
        r'§\s*\d+.*?\(Ord\.?\s*(\d{4}[-–]\d+)',
        r'Ord\.\s+(\d{4}[-–]\d+)',
        r'\[Ord\.?\s*(\d{4}[-–]\d+)',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ord_num = match.group(1).replace('–', '-')

            if ord_num in seen or len(ord_num) < 4:
                continue
            seen.add(ord_num)

            # Extract date
            context_start = max(0, match.start() - 200)
            context_end = min(len(text), match.end() + 200)
            context = text[context_start:context_end]

            date = None
            date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', context)
            if date_match:
                try:
                    date_str = date_match.group(1)
                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y']:
                        try:
                            date = datetime.strptime(date_str, fmt).date().isoformat()
                            break
                        except:
                            continue
                except:
                    pass

            ordinances.append({
                "jurisdiction_id": jid,
                "ordinance_number": ord_num,
                "source_url": url,
                "passed_date": date,
            })

    return ordinances


def upload_to_supabase(ordinances: List[Dict]) -> int:
    """Upload ordinances to Supabase"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0

    for record in ordinances:
        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/ordinances",
                headers=headers,
                json=record
            )

            if resp.status_code in (200, 201):
                saved += 1
            elif resp.status_code == 409:
                pass  # duplicate

        except:
            pass

    client.close()
    return saved


def main():
    logger.info("="*60)
    logger.info("DEEP ORDINANCE EXTRACTION")
    logger.info("="*60)

    jina = JinaReader()
    all_ordinances = []

    for jid, config in DEEP_TARGETS.items():
        name = config["name"]
        urls = config["urls"]

        logger.info(f"\n--- {name} (ID: {jid}) ---")

        for url in urls:
            logger.info(f"  Fetching: {url[:60]}...")
            content = jina.fetch(url)

            if content:
                logger.info(f"    Got {len(content)} chars")
                ords = extract_ordinances(content, jid, name, url)
                all_ordinances.extend(ords)
                logger.info(f"    Found {len(ords)} ordinances")
            else:
                logger.warning(f"    Failed to fetch")

            time.sleep(REQUEST_DELAY)

    jina.close()

    # Deduplicate
    seen = set()
    unique = []
    for o in all_ordinances:
        key = f"{o['jurisdiction_id']}-{o['ordinance_number']}"
        if key not in seen:
            seen.add(key)
            unique.append(o)

    logger.info(f"\n--- SUMMARY ---")
    logger.info(f"Total found: {len(all_ordinances)}")
    logger.info(f"Unique: {len(unique)}")

    # Upload
    logger.info(f"\nUploading to Supabase...")
    saved = upload_to_supabase(unique)
    logger.info(f"Saved: {saved}")

    # Save to JSON
    output_path = Path(__file__).parent.parent / "data" / f"deep_ordinances_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump({"ordinances": unique}, f, indent=2)
    logger.info(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
