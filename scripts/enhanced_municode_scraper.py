#!/usr/bin/env python3
"""
Enhanced Municode Scraper for ZoneWise
=====================================
Uses Jina Reader + targeted URLs to extract maximum data from all 17 jurisdictions.

Strategy:
1. Use Jina Reader (free, more content) as primary
2. Target specific zoning chapter URLs with actual content
3. Scrape multiple sections per jurisdiction for comprehensive coverage
4. Extract all data types: ordinances, bonuses, overlays, conditional uses, timelines

Author: Claude AI Architect
Date: 2026-01-21
"""

import os
import sys
import json
import re
import time
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('enhanced_extraction.log')
    ]
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
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_API_KEY", "")

# Constants
JINA_URL = "https://r.jina.ai/"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"
REQUEST_DELAY = 2.0

# Enhanced jurisdiction configurations with specific node IDs
JURISDICTIONS = {
    1: {
        "name": "Melbourne",
        "slug": "melbourne",
        "urls": [
            # Main zoning code
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO",
            # District dimensional standards
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVDIRE_S2DIUSDIST",
            # Overlay districts
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTXIOVDI",
            # Conditional uses
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVIIIUS",
            # Procedures
            "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTXIIPR",
        ],
        "districts": ["AEU", "REU", "R-1A", "R-1B", "R-1C", "R-2", "R-3", "MH", "C-P", "C-1", "C-2", "C-3", "M-1", "PUD"]
    },
    2: {
        "name": "Palm Bay",
        "slug": "palm_bay",
        "urls": [
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTIVREDI",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTVCODE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTVIINDE",
            "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances?nodeId=PTIICOOR_CH166ZO_ARTXSPUS",
        ],
        "districts": ["RE", "RS-1", "RS-2", "RS-3", "RM-1", "RM-2", "CN", "CG", "IL", "IH", "PUD"]
    },
    3: {
        "name": "Titusville",
        "slug": "titusville",
        "urls": [
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIIIZODI",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTIVUSRE",
            "https://library.municode.com/fl/titusville/codes/code_of_ordinances?nodeId=PTIICOOR_CH34ZO_ARTVDERE",
        ],
        "districts": ["R-1A", "R-1B", "R-1C", "R-2", "R-3", "MH-1", "C-1", "C-2", "C-3", "M-1", "M-2", "PD", "CBD"]
    },
    4: {
        "name": "West Melbourne",
        "slug": "west_melbourne",
        "urls": [
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO",
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIIIZODIEST",
            "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIVSPEX",
        ],
        "districts": ["R-1AA", "R-1A", "R-1B", "R-2", "R-3", "C-1", "C-2", "C-3", "M-1", "M-2", "PUD"]
    },
    5: {
        "name": "Rockledge",
        "slug": "rockledge",
        "urls": [
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTIIIBA",
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVIPLDIZO",
            "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=LADERE_PTVIIGEPRST",
        ],
        "districts": ["R-1AAA", "R-1AA", "R-1A", "R-1", "R-2", "R-3", "C-1", "C-2", "M-1", "PUD"]
    },
    6: {
        "name": "Cocoa",
        "slug": "cocoa",
        "urls": [
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO",
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIIZODI",
            "https://library.municode.com/fl/cocoa/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVUSRE",
        ],
        "districts": ["R-1A", "R-1B", "R-1C", "R-2", "R-3", "C-1", "C-2", "C-3", "M-1", "PUD"]
    },
    7: {
        "name": "Cocoa Beach",
        "slug": "cocoa_beach",
        "urls": [
            "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO",
            "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIIIZODI",
            "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances?nodeId=COOR_CH13ZO_ARTIVDEST",
        ],
        "districts": ["R-1", "R-2", "R-3", "C-1", "C-2", "C-3", "M-1", "RC", "PUD"]
    },
    8: {
        "name": "Cape Canaveral",
        "slug": "cape_canaveral",
        "urls": [
            "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO",
            "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIIIZODI",
            "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIVDEST",
        ],
        "districts": ["R-1", "R-2", "R-3", "C-1", "C-2", "M-1", "I", "CON", "PUD"]
    },
    9: {
        "name": "Satellite Beach",
        "slug": "satellite_beach",
        "urls": [
            "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO",
            "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIIIZODI",
            "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances?nodeId=COOR_CH114ZO_ARTIVPRUS",
        ],
        "districts": ["R-1A", "R-1B", "R-2", "R-3", "C-1", "C-2", "P", "OS", "PUD"]
    },
    10: {
        "name": "Indian Harbour Beach",
        "slug": "indian_harbour_beach",
        "urls": [
            "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO",
            "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTIIIZODI",
            "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO_ARTIVDEST",
        ],
        "districts": ["R-1AAA", "R-1AA", "R-1A", "R-2", "R-3", "C-P", "B-1", "M-1", "P-1"]
    },
    11: {
        "name": "Indialantic",
        "slug": "indialantic",
        "urls": [
            "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO",
            "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTIIIZODI",
            "https://library.municode.com/fl/indialantic/codes/code_of_ordinances?nodeId=COOR_CH23ZO_ARTVUSRE",
        ],
        "districts": ["R-1", "R-2", "R-3", "C-1", "GU", "CON", "PUD"]
    },
    12: {
        "name": "Melbourne Beach",
        "slug": "melbourne_beach",
        "urls": [
            "https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH26ZO",
            "https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH26ZO_ARTIIIZODI",
            "https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH26ZO_ARTIVDEST",
        ],
        "districts": ["R-1A", "R-1B", "R-1C", "R-2", "R-3", "C-1", "P", "CON"]
    },
    13: {
        "name": "Melbourne Village",
        "slug": "melbourne_village",
        "urls": [
            "https://library.municode.com/fl/melbourne_village/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO",
            "https://library.municode.com/fl/melbourne_village/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ],
        "districts": ["R-1", "R-2", "C", "P", "CON", "PUD"]
    },
    14: {
        "name": "Palm Shores",
        "slug": "palm_shores",
        "urls": [
            "https://library.municode.com/fl/palm_shores/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO",
            "https://library.municode.com/fl/palm_shores/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ],
        "districts": ["R-1", "C-1", "P", "CON"]
    },
    15: {
        "name": "Malabar",
        "slug": "malabar",
        "urls": [
            "https://library.municode.com/fl/malabar/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO",
            "https://library.municode.com/fl/malabar/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ],
        "districts": ["A", "R-1", "R-2", "C", "P", "CON"]
    },
    16: {
        "name": "Grant-Valkaria",
        "slug": "grant-valkaria",
        "urls": [
            "https://library.municode.com/fl/grant-valkaria/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO",
            "https://library.municode.com/fl/grant-valkaria/codes/code_of_ordinances?nodeId=PTIICOOR_CH18ZO_ARTIIIZODI",
        ],
        "districts": ["A-1", "R-1", "R-2", "C-1", "P", "CON"]
    },
    17: {
        "name": "Brevard County",
        "slug": "brevard_county",
        "urls": [
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO",
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIZODI",
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIIDEST",
            "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62ZO_ARTVIIISPERUSRE",
        ],
        "districts": ["AU", "RR-1", "SR", "RU-1-13", "RU-1-11", "RU-1-9", "RU-1-7", "RU-2-15", "RU-2-30", "BU-1", "BU-2", "IU", "PUD"]
    }
}


class JinaReader:
    """Jina Reader API for extracting content from web pages"""

    def __init__(self):
        self.client = httpx.Client(timeout=120.0)
        self.last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request = time.time()

    def fetch(self, url: str) -> Optional[str]:
        """Fetch content using Jina Reader"""
        self._rate_limit()

        try:
            response = self.client.get(
                f"{JINA_URL}{url}",
                headers={
                    "Accept": "text/plain",
                    "X-Return-Format": "text"
                }
            )

            if response.status_code == 200:
                content = response.text
                if len(content) > 500:
                    return content

        except Exception as e:
            logger.error(f"Jina fetch error: {e}")

        return None

    def close(self):
        self.client.close()


class FirecrawlScraper:
    """Firecrawl API for JS-rendered content"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=120.0)
        self.last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request = time.time()

    def fetch(self, url: str) -> Optional[str]:
        """Fetch content using Firecrawl"""
        self._rate_limit()

        try:
            response = self.client.post(
                FIRECRAWL_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "url": url,
                    "formats": ["markdown"],
                    "waitFor": 8000,  # Wait longer for Municode to load
                    "actions": [
                        {"type": "wait", "milliseconds": 3000}  # Additional wait
                    ]
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    content = data.get("data", {}).get("markdown", "")
                    if len(content) > 500:
                        return content
            elif response.status_code == 429:
                logger.warning("Rate limited, waiting...")
                time.sleep(30)
                return self.fetch(url)

        except Exception as e:
            logger.error(f"Firecrawl error: {e}")

        return None

    def close(self):
        self.client.close()


class DataExtractor:
    """Extract structured data from ordinance text"""

    @staticmethod
    def extract_ordinances(text: str, jid: int, jname: str, url: str) -> List[Dict]:
        """Extract ordinance references"""
        ordinances = []
        seen = set()

        # Multiple patterns for ordinance references
        patterns = [
            r'\(Ord\.?\s*(?:No\.?\s*)?(\d{4}[-–]\d+)',
            r'Ord\.?\s*(?:No\.?\s*)?(\d{4}[-–]\d+)',
            r'Ordinance\s+(?:No\.?\s*)?(\d{2,4}[-–]\d{1,4})',
            r'\(O\.?\s*(\d{4}[-–]\d+)',
            r'adopted\s+by\s+Ord(?:inance)?\.?\s*(\d{4}[-–]\d+)',
            r'as\s+amended\s+by\s+Ord\.?\s*(\d{4}[-–]\d+)',
            r'§\s*\d+.*?\(Ord\.?\s*(\d{4}[-–]\d+)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                ord_num = match.group(1).replace('–', '-')

                if ord_num in seen or len(ord_num) < 4:
                    continue
                seen.add(ord_num)

                # Get context
                start = max(0, match.start() - 300)
                end = min(len(text), match.end() + 300)
                context = text[start:end]

                # Determine type
                ord_type = "other"
                if re.search(r'zoning|district|setback|height|density|lot|building', context, re.I):
                    ord_type = "zoning"
                elif re.search(r'land\s*use|comprehensive|future\s*land', context, re.I):
                    ord_type = "land_use"
                elif re.search(r'subdivision|plat', context, re.I):
                    ord_type = "building"
                elif re.search(r'environment|wetland|conservation', context, re.I):
                    ord_type = "environmental"

                # Extract date
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
                    "jurisdiction_name": jname,
                    "ordinance_number": ord_num,
                    "ordinance_type": ord_type,
                    "source_url": url,
                    "passed_date": date,
                    "extraction_date": datetime.now().isoformat(),
                    "extraction_confidence": 0.8 if date else 0.6,
                    "content_hash": hashlib.md5(context.encode()).hexdigest()
                })

        return ordinances

    @staticmethod
    def extract_bonuses(text: str, jid: int, jname: str, url: str) -> List[Dict]:
        """Extract development bonus programs"""
        bonuses = []
        seen = set()

        # Patterns for different bonus types
        bonus_patterns = [
            (r'density\s+bonus[:\s]+(?:up\s+to\s+)?(\d+)\s*%', 'density', 'percent'),
            (r'(\d+)\s*%\s+(?:additional\s+)?density\s+bonus', 'density', 'percent'),
            (r'height\s+bonus[:\s]+(?:up\s+to\s+)?(\d+)\s*(?:feet|ft|%)', 'height', 'feet'),
            (r'additional\s+(\d+)\s*(?:feet|ft|stories?)', 'height', 'feet'),
            (r'parking\s+reduction[:\s]+(\d+)\s*%', 'parking_reduction', 'percent'),
            (r'reduce[d]?\s+parking\s+(?:by\s+)?(\d+)\s*%', 'parking_reduction', 'percent'),
            (r'(?:FAR|floor\s+area\s+ratio)\s+(?:bonus|increase)[:\s]+(\d+(?:\.\d+)?)', 'far', 'ratio'),
            (r'setback\s+reduction[:\s]+(\d+)', 'setback_reduction', 'feet'),
            (r'(?:affordable|workforce)\s+housing.*?(\d+)\s*%\s+bonus', 'density', 'percent'),
            (r'incentive[:\s]*(\d+)\s*(?:%|percent)', 'density', 'percent'),
        ]

        for pattern, bonus_type, unit in bonus_patterns:
            for match in re.finditer(pattern, text, re.I):
                amount = float(match.group(1))

                key = f"{jid}-{bonus_type}-{amount}"
                if key in seen:
                    continue
                seen.add(key)

                # Get context
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]

                # Find qualifying criteria
                criteria = []
                for keyword in ['affordable', 'workforce', 'senior', 'green', 'leed', 'transit', 'mixed use', 'historic']:
                    if keyword in context.lower():
                        criteria.append(keyword)

                bonuses.append({
                    "jurisdiction_id": jid,
                    "jurisdiction_name": jname,
                    "bonus_name": f"{bonus_type.replace('_', ' ').title()} Bonus",
                    "bonus_type": bonus_type,
                    "bonus_amount": amount,
                    "bonus_unit": unit,
                    "qualifying_criteria": ', '.join(criteria) if criteria else None,
                    "source_url": url,
                    "extraction_date": datetime.now().isoformat(),
                    "extraction_confidence": 0.7 if criteria else 0.5,
                    "content_hash": hashlib.md5(context.encode()).hexdigest()
                })

        return bonuses

    @staticmethod
    def extract_overlays(text: str, jid: int, jname: str, url: str) -> List[Dict]:
        """Extract overlay districts"""
        overlays = []
        seen = set()

        overlay_types = {
            'historic': ['historic', 'preservation', 'heritage'],
            'flood': ['flood', 'floodplain', 'fema', 'special flood hazard'],
            'coastal': ['coastal', 'beach', 'shoreline', 'ocean'],
            'airport': ['airport', 'aviation', 'flight', 'noise'],
            'environmental': ['environmental', 'wetland', 'conservation', 'habitat', 'scrub jay', 'gopher tortoise'],
            'waterfront': ['waterfront', 'riverfront', 'lake', 'marina'],
            'redevelopment': ['redevelopment', 'cra', 'community redevelopment', 'revitalization'],
            'downtown': ['downtown', 'central business', 'cbd', 'town center', 'urban core'],
            'corridor': ['corridor', 'gateway', 'scenic', 'highway'],
        }

        for otype, keywords in overlay_types.items():
            for keyword in keywords:
                # More specific patterns
                patterns = [
                    rf'({keyword})\s+(?:overlay|district|zone)[:\s]*([A-Z0-9-]+)?',
                    rf'([A-Z0-9-]+)\s+{keyword}\s+(?:overlay|district)',
                    rf'{keyword}[^.]*(?:overlay|district|zone)',
                ]

                for pattern in patterns:
                    for match in re.finditer(pattern, text, re.I):
                        # Get context
                        start = max(0, match.start() - 500)
                        end = min(len(text), match.end() + 500)
                        context = text[start:end]

                        # Extract code
                        code_match = re.search(r'[-–]([A-Z]{1,4}(?:[-–]?[A-Z0-9]*)?)', context)
                        overlay_code = code_match.group(1) if code_match else f"{otype[:3].upper()}-OV"

                        key = f"{jid}-{overlay_code}"
                        if key in seen:
                            continue
                        seen.add(key)

                        # Extract purpose if available
                        purpose = None
                        purpose_match = re.search(r'(?:purpose|intent)[:\s]*([^.]+\.)', context, re.I)
                        if purpose_match:
                            purpose = purpose_match.group(1)[:500]

                        overlays.append({
                            "jurisdiction_id": jid,
                            "jurisdiction_name": jname,
                            "overlay_code": overlay_code,
                            "overlay_name": f"{keyword.title()} Overlay District",
                            "overlay_type": otype,
                            "purpose": purpose,
                            "source_url": url,
                            "extraction_date": datetime.now().isoformat(),
                            "extraction_confidence": 0.7,
                            "content_hash": hashlib.md5(context.encode()).hexdigest()
                        })

        return overlays

    @staticmethod
    def extract_conditional_uses(text: str, jid: int, jname: str, url: str, districts: List[str]) -> List[Dict]:
        """Extract conditional use requirements"""
        uses = []
        seen = set()

        # Find conditional use sections
        cu_patterns = [
            r'(?:conditional\s+use|special\s+exception|CU|SE)[s]?[:\s]*([^§]+?)(?=(?:conditional|special|Section|\n\n|$))',
            r'permitted\s+(?:with|upon|subject\s+to)\s+(?:conditional|special)[^.]+\.([^§]+?)(?=permitted|conditional|$)',
        ]

        all_sections = []
        for pattern in cu_patterns:
            for match in re.finditer(pattern, text, re.I | re.DOTALL):
                all_sections.append(match.group(1))

        # Also look for bullet lists of uses
        bullet_pattern = r'[•\-\*]\s*([A-Z][a-z]+(?:\s+[a-z]+)*)'
        numbered_pattern = r'\d+\)\s*([A-Z][a-z]+(?:\s+[a-z]+)*)'

        for section in all_sections:
            for pattern in [bullet_pattern, numbered_pattern]:
                for match in re.finditer(pattern, section):
                    use_name = match.group(1).strip()

                    if len(use_name) < 4 or len(use_name) > 80:
                        continue

                    # Determine category
                    category = 'other'
                    if re.search(r'dwell|resid|home|apart|house', use_name, re.I):
                        category = 'residential'
                    elif re.search(r'retail|office|store|shop|restaurant|hotel|commercial', use_name, re.I):
                        category = 'commercial'
                    elif re.search(r'manufact|warehouse|industrial|factory', use_name, re.I):
                        category = 'industrial'
                    elif re.search(r'school|church|hospital|government|library|civic', use_name, re.I):
                        category = 'institutional'
                    elif re.search(r'park|recreation|sports|entertainment', use_name, re.I):
                        category = 'recreational'
                    elif re.search(r'utility|tower|antenna|substation', use_name, re.I):
                        category = 'utility'

                    # Assign to districts (limit to avoid massive duplication)
                    for district in districts[:3]:
                        key = f"{jid}-{district}-{use_name}"
                        if key in seen:
                            continue
                        seen.add(key)

                        uses.append({
                            "jurisdiction_id": jid,
                            "jurisdiction_name": jname,
                            "district_code": district,
                            "use_name": use_name,
                            "use_category": category,
                            "permit_type": "conditional_use",
                            "source_url": url,
                            "extraction_date": datetime.now().isoformat(),
                            "extraction_confidence": 0.6,
                            "content_hash": hashlib.md5(section[:200].encode()).hexdigest()
                        })

        return uses

    @staticmethod
    def extract_timelines(text: str, jid: int, jname: str, url: str) -> List[Dict]:
        """Extract entitlement processing timelines"""
        timelines = []
        seen = set()

        ent_types = {
            'site_plan': ['site plan', 'site development', 'development order'],
            'rezoning': ['rezoning', 'rezone', 'zoning change', 'zoning amendment'],
            'variance': ['variance', 'deviation', 'waiver'],
            'special_exception': ['special exception', 'special use', 'conditional use'],
            'subdivision': ['subdivision', 'plat', 'platting', 'major subdivision', 'minor subdivision'],
            'pud': ['pud', 'planned unit', 'planned development', 'master plan'],
            'comp_plan_amendment': ['comprehensive plan', 'comp plan', 'future land use'],
        }

        for ent_type, keywords in ent_types.items():
            for keyword in keywords:
                # Patterns for timeline information
                patterns = [
                    rf'{keyword}[^.]*?(\d+)\s*(?:calendar\s+)?(?:days?|business\s+days?)',
                    rf'{keyword}[^.]*?within\s+(\d+)\s*(?:days?)',
                    rf'(\d+)\s*(?:calendar\s+)?(?:days?)[^.]*{keyword}',
                ]

                for pattern in patterns:
                    for match in re.finditer(pattern, text, re.I):
                        days = int(match.group(1))

                        # Skip unreasonable values
                        if days > 365 or days < 1:
                            continue

                        key = f"{jid}-{ent_type}"
                        if key in seen:
                            continue
                        seen.add(key)

                        # Get context
                        start = max(0, match.start() - 200)
                        end = min(len(text), match.end() + 200)
                        context = text[start:end]

                        # Check for public hearing
                        public_hearing = bool(re.search(r'public\s+hearing|notice|advertise', context, re.I))

                        # Determine authority
                        authority = None
                        if re.search(r'city\s+council|commission|board\s+of\s+commissioners', context, re.I):
                            authority = 'city_council'
                        elif re.search(r'planning\s+(?:commission|board)|p&z', context, re.I):
                            authority = 'planning_commission'
                        elif re.search(r'board\s+of\s+adjustment|boa|bza', context, re.I):
                            authority = 'board_of_adjustment'
                        elif re.search(r'staff|director|administrative', context, re.I):
                            authority = 'staff'

                        timelines.append({
                            "jurisdiction_id": jid,
                            "jurisdiction_name": jname,
                            "entitlement_type": ent_type,
                            "process_name": keyword.title(),
                            "estimated_days_typical": days,
                            "estimated_days_minimum": max(7, days - 14),
                            "estimated_days_maximum": days + 30,
                            "public_hearing_required": public_hearing,
                            "review_authority": authority,
                            "source_url": url,
                            "extraction_date": datetime.now().isoformat(),
                            "extraction_confidence": 0.7,
                            "content_hash": hashlib.md5(context.encode()).hexdigest()
                        })

        return timelines


class EnhancedExtractor:
    """Main extraction engine"""

    def __init__(self):
        self.jina = JinaReader()
        self.firecrawl = FirecrawlScraper(FIRECRAWL_KEY) if FIRECRAWL_KEY else None
        self.all_data = {
            "ordinances": [],
            "development_bonuses": [],
            "overlay_districts": [],
            "conditional_uses": [],
            "entitlement_timelines": []
        }
        self.supabase_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation,resolution=merge-duplicates"
        }

    def fetch_content(self, url: str) -> Optional[str]:
        """Fetch content with fallback"""
        logger.info(f"    Fetching: {url}")

        # Try Jina first (usually better for Municode)
        content = self.jina.fetch(url)
        if content and len(content) > 1000:
            logger.info(f"      Jina: {len(content)} chars")
            return content

        # Fallback to Firecrawl
        if self.firecrawl:
            content = self.firecrawl.fetch(url)
            if content and len(content) > 1000:
                logger.info(f"      Firecrawl: {len(content)} chars")
                return content

        logger.warning(f"      Failed to fetch content")
        return None

    def process_jurisdiction(self, jid: int, config: Dict) -> Dict:
        """Process a single jurisdiction"""
        name = config["name"]
        urls = config["urls"]
        districts = config["districts"]

        logger.info(f"\n{'='*60}")
        logger.info(f"PROCESSING: {name} (ID: {jid})")
        logger.info(f"{'='*60}")

        results = {
            "ordinances": [],
            "development_bonuses": [],
            "overlay_districts": [],
            "conditional_uses": [],
            "entitlement_timelines": []
        }

        # Fetch all URLs
        all_content = []
        for url in urls:
            content = self.fetch_content(url)
            if content:
                all_content.append((url, content))
            time.sleep(REQUEST_DELAY)

        if not all_content:
            logger.error(f"  No content retrieved for {name}")
            return results

        # Extract from all content
        for url, content in all_content:
            # Ordinances
            ords = DataExtractor.extract_ordinances(content, jid, name, url)
            results["ordinances"].extend(ords)

            # Bonuses
            bonuses = DataExtractor.extract_bonuses(content, jid, name, url)
            results["development_bonuses"].extend(bonuses)

            # Overlays
            overlays = DataExtractor.extract_overlays(content, jid, name, url)
            results["overlay_districts"].extend(overlays)

            # Conditional uses
            uses = DataExtractor.extract_conditional_uses(content, jid, name, url, districts)
            results["conditional_uses"].extend(uses)

            # Timelines
            timelines = DataExtractor.extract_timelines(content, jid, name, url)
            results["entitlement_timelines"].extend(timelines)

        # Log results
        logger.info(f"\n  Results for {name}:")
        logger.info(f"    Ordinances: {len(results['ordinances'])}")
        logger.info(f"    Dev Bonuses: {len(results['development_bonuses'])}")
        logger.info(f"    Overlays: {len(results['overlay_districts'])}")
        logger.info(f"    Conditional Uses: {len(results['conditional_uses'])}")
        logger.info(f"    Timelines: {len(results['entitlement_timelines'])}")

        return results

    def save_to_supabase(self, table: str, records: List[Dict]) -> int:
        """Save records to Supabase"""
        if not records:
            return 0

        client = httpx.Client(timeout=60)
        saved = 0

        # Batch insert
        batch_size = 50
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                resp = client.post(
                    f"{SUPABASE_URL}/rest/v1/{table}",
                    headers=self.supabase_headers,
                    json=batch
                )
                if resp.status_code in (200, 201):
                    saved += len(batch)
                else:
                    logger.warning(f"Supabase insert failed: {resp.status_code} - {resp.text[:200]}")
            except Exception as e:
                logger.error(f"Supabase error: {e}")

        client.close()
        return saved

    def run(self):
        """Run full extraction"""
        logger.info("="*60)
        logger.info("ENHANCED MUNICODE SCRAPER")
        logger.info("="*60)
        logger.info(f"Supabase: {SUPABASE_URL}")
        logger.info(f"Firecrawl: {'configured' if FIRECRAWL_KEY else 'NOT configured'}")
        logger.info(f"Jurisdictions: {len(JURISDICTIONS)}")
        logger.info("="*60)

        start_time = datetime.now()

        # Process each jurisdiction
        for jid, config in JURISDICTIONS.items():
            try:
                results = self.process_jurisdiction(jid, config)

                # Aggregate
                for key, records in results.items():
                    self.all_data[key].extend(records)

                # Progress
                logger.info(f"\n--- RUNNING TOTALS ---")
                for key, records in self.all_data.items():
                    logger.info(f"  {key}: {len(records)}")

            except Exception as e:
                logger.error(f"Error processing {config['name']}: {e}")

        # Deduplicate
        logger.info("\n--- DEDUPLICATING ---")
        for key in self.all_data:
            original = len(self.all_data[key])
            seen = set()
            unique = []
            for record in self.all_data[key]:
                # Create unique key
                if key == "ordinances":
                    rkey = f"{record['jurisdiction_id']}-{record['ordinance_number']}"
                elif key == "development_bonuses":
                    rkey = f"{record['jurisdiction_id']}-{record['bonus_name']}-{record['bonus_type']}"
                elif key == "overlay_districts":
                    rkey = f"{record['jurisdiction_id']}-{record['overlay_code']}"
                elif key == "conditional_uses":
                    rkey = f"{record['jurisdiction_id']}-{record['district_code']}-{record['use_name']}"
                elif key == "entitlement_timelines":
                    rkey = f"{record['jurisdiction_id']}-{record['entitlement_type']}"
                else:
                    rkey = record.get('content_hash', str(hash(str(record))))

                if rkey not in seen:
                    seen.add(rkey)
                    unique.append(record)

            self.all_data[key] = unique
            logger.info(f"  {key}: {original} -> {len(unique)}")

        # Save to JSON
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"enhanced_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_path, 'w') as f:
            json.dump({
                "metadata": {
                    "extraction_date": datetime.now().isoformat(),
                    "jurisdictions": len(JURISDICTIONS),
                    "totals": {k: len(v) for k, v in self.all_data.items()}
                },
                "data": self.all_data
            }, f, indent=2, default=str)

        logger.info(f"\nSaved to: {output_path}")

        # Save to Supabase
        logger.info("\n--- SAVING TO SUPABASE ---")
        db_results = {}
        for table, records in self.all_data.items():
            saved = self.save_to_supabase(table, records)
            db_results[table] = saved
            logger.info(f"  {table}: {saved} saved")

        # Final report
        elapsed = datetime.now() - start_time
        logger.info("\n" + "="*60)
        logger.info("EXTRACTION COMPLETE")
        logger.info("="*60)
        logger.info(f"Duration: {elapsed}")
        logger.info(f"\nFINAL COUNTS:")
        logger.info(f"  Ordinances: {len(self.all_data['ordinances'])} (target: 850-3,400)")
        logger.info(f"  Dev Bonuses: {len(self.all_data['development_bonuses'])} (target: 85-340)")
        logger.info(f"  Overlays: {len(self.all_data['overlay_districts'])} (target: 51-170)")
        logger.info(f"  Conditional Uses: {len(self.all_data['conditional_uses'])} (target: 340-1,700)")
        logger.info(f"  Timelines: {len(self.all_data['entitlement_timelines'])} (target: 85-170)")

        # Validate
        logger.info("\n--- VALIDATION ---")
        checks = [
            ("ordinances", 500, len(self.all_data['ordinances'])),
            ("development_bonuses", 50, len(self.all_data['development_bonuses'])),
            ("overlay_districts", 30, len(self.all_data['overlay_districts'])),
            ("conditional_uses", 200, len(self.all_data['conditional_uses'])),
            ("entitlement_timelines", 50, len(self.all_data['entitlement_timelines'])),
        ]

        all_passed = True
        for table, minimum, actual in checks:
            if actual >= minimum:
                logger.info(f"  PASS: {table} ({actual} >= {minimum})")
            else:
                logger.warning(f"  FAIL: {table} ({actual} < {minimum})")
                all_passed = False

        logger.info(f"\nOVERALL: {'PASSED' if all_passed else 'NEEDS MORE DATA'}")

        return all_passed

    def close(self):
        self.jina.close()
        if self.firecrawl:
            self.firecrawl.close()


def main():
    extractor = EnhancedExtractor()
    try:
        extractor.run()
    finally:
        extractor.close()


if __name__ == "__main__":
    main()
