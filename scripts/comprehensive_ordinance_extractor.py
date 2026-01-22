#!/usr/bin/env python3
"""
ZoneWise Comprehensive Ordinance Extractor
==========================================
Extracts ALL ordinance data from 17 Brevard County jurisdictions:
- Ordinances (target: 850-3,400)
- Development Bonuses (target: 85-340)
- Overlay Districts (target: 51-170)
- Conditional Uses (target: 340-1,700)
- Entitlement Timelines (target: 85-170)

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
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('comprehensive_extraction.log')
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
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"
JINA_URL = "https://r.jina.ai/"
REQUEST_DELAY = 1.5  # Seconds between requests

# Jurisdiction configurations
JURISDICTIONS = [
    {"id": 1, "name": "Melbourne", "slug": "melbourne", "source": "municode"},
    {"id": 2, "name": "Palm Bay", "slug": "palm_bay", "source": "municode"},
    {"id": 3, "name": "Titusville", "slug": "titusville", "source": "municode"},
    {"id": 4, "name": "West Melbourne", "slug": "west_melbourne", "source": "municode"},
    {"id": 5, "name": "Rockledge", "slug": "rockledge", "source": "municode"},
    {"id": 6, "name": "Cocoa", "slug": "cocoa", "source": "municode"},
    {"id": 7, "name": "Cocoa Beach", "slug": "cocoa_beach", "source": "municode"},
    {"id": 8, "name": "Cape Canaveral", "slug": "cape_canaveral", "source": "municode"},
    {"id": 9, "name": "Satellite Beach", "slug": "satellite_beach", "source": "municode"},
    {"id": 10, "name": "Indian Harbour Beach", "slug": "indian_harbour_beach", "source": "municode"},
    {"id": 11, "name": "Indialantic", "slug": "indialantic", "source": "municode"},
    {"id": 12, "name": "Melbourne Beach", "slug": "melbourne_beach", "source": "municode"},
    {"id": 13, "name": "Melbourne Village", "slug": "melbourne_village", "source": "municode"},
    {"id": 14, "name": "Palm Shores", "slug": "palm_shores", "source": "municode"},
    {"id": 15, "name": "Malabar", "slug": "malabar", "source": "municode"},
    {"id": 16, "name": "Grant-Valkaria", "slug": "grant-valkaria", "source": "municode"},
    {"id": 17, "name": "Brevard County", "slug": "brevard_county", "source": "municode"},
]


@dataclass
class ExtractionStats:
    """Track extraction statistics"""
    ordinances: int = 0
    development_bonuses: int = 0
    overlay_districts: int = 0
    conditional_uses: int = 0
    entitlement_timelines: int = 0
    errors: int = 0


class FirecrawlClient:
    """Client for Firecrawl API with rate limiting"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=120.0)
        self.last_request = 0

    def _rate_limit(self):
        """Ensure minimum delay between requests"""
        elapsed = time.time() - self.last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request = time.time()

    def scrape(self, url: str, wait_for: int = 5000) -> Optional[str]:
        """Scrape a URL and return markdown content"""
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
                    "waitFor": wait_for
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {}).get("markdown", "")
                else:
                    logger.error(f"Firecrawl API error: {data.get('error')}")
            elif response.status_code == 401:
                logger.error("Firecrawl API key invalid")
            elif response.status_code == 429:
                logger.warning("Rate limited, waiting 60s...")
                time.sleep(60)
                return self.scrape(url, wait_for)
            else:
                logger.error(f"Firecrawl HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"Firecrawl error: {e}")

        return None

    def close(self):
        self.client.close()


class JinaClient:
    """Fallback scraper using Jina Reader"""

    def __init__(self):
        self.client = httpx.Client(timeout=60.0)
        self.last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request = time.time()

    def scrape(self, url: str) -> Optional[str]:
        """Scrape using Jina Reader"""
        self._rate_limit()

        try:
            response = self.client.get(
                f"{JINA_URL}{url}",
                headers={"Accept": "text/plain"}
            )

            if response.status_code == 200:
                return response.text

        except Exception as e:
            logger.error(f"Jina error: {e}")

        return None

    def close(self):
        self.client.close()


class SupabaseClient:
    """Client for Supabase operations"""

    def __init__(self, url: str, key: str):
        self.url = url
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation,resolution=merge-duplicates"
        }
        self.client = httpx.Client(headers=self.headers, timeout=30)

    def upsert(self, table: str, records: List[Dict]) -> Dict:
        """Upsert records to a table"""
        if not records:
            return {"status": "empty", "count": 0}

        try:
            resp = self.client.post(
                f"{self.url}/rest/v1/{table}",
                json=records
            )

            if resp.status_code in (200, 201):
                return {"status": "success", "count": len(records)}
            else:
                return {"status": "error", "code": resp.status_code, "message": resp.text[:500]}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def log_scrape(self, jurisdiction_id: int, jurisdiction_name: str,
                   scrape_type: str, target_table: str, stats: Dict) -> None:
        """Log scrape operation"""
        try:
            self.client.post(
                f"{self.url}/rest/v1/municode_scrape_log",
                json={
                    "jurisdiction_id": jurisdiction_id,
                    "jurisdiction_name": jurisdiction_name,
                    "scrape_type": scrape_type,
                    "target_table": target_table,
                    "status": "completed",
                    "records_found": stats.get("found", 0),
                    "records_inserted": stats.get("inserted", 0),
                    "end_time": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to log scrape: {e}")

    def close(self):
        self.client.close()


class OrdinanceParser:
    """Parse ordinance references from municipal code text"""

    # Regex patterns for ordinance references
    ORDINANCE_PATTERNS = [
        r'Ord\.?\s*(?:No\.?\s*)?(\d{4}[-–]\d+)',  # Ord. 2024-01
        r'Ord(?:inance)?\.?\s*(?:No\.?\s*)?(\d{2,4}[-–]\d{1,4})',  # Ordinance No. 24-1
        r'(?:^|\s)O(?:rd)?\.?\s*(\d{4}[-–]\d+)',  # O. 2024-01
        r'Ordinance\s+(\d+)',  # Ordinance 1234
        r'\(Ord\.?\s*(\d{4}[-–]\d+)[,\)]',  # (Ord. 2024-01,
        r'adopted\s+(?:by\s+)?Ord(?:inance)?\.?\s*(?:No\.?\s*)?(\d{4}[-–]\d+)',
    ]

    DATE_PATTERNS = [
        r'(?:passed|adopted|approved|effective)\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s*(?:passed|adopted)',
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
    ]

    @staticmethod
    def extract_ordinances(text: str, jurisdiction_id: int, jurisdiction_name: str,
                          source_url: str) -> List[Dict]:
        """Extract ordinance references from text"""
        ordinances = []
        seen = set()

        for pattern in OrdinanceParser.ORDINANCE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                ord_num = match.group(1).replace('–', '-')

                if ord_num in seen:
                    continue
                seen.add(ord_num)

                # Try to extract context
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]

                # Determine ordinance type
                ord_type = "other"
                if re.search(r'zoning|district|setback|height|density', context, re.I):
                    ord_type = "zoning"
                elif re.search(r'land\s*use|comprehensive\s*plan', context, re.I):
                    ord_type = "land_use"
                elif re.search(r'building|construction|permit', context, re.I):
                    ord_type = "building"
                elif re.search(r'environment|wetland|tree|stormwater', context, re.I):
                    ord_type = "environmental"

                # Extract passed date if available
                passed_date = None
                for date_pattern in OrdinanceParser.DATE_PATTERNS:
                    date_match = re.search(date_pattern, context, re.I)
                    if date_match:
                        try:
                            date_str = date_match.group(1) if date_match.lastindex else date_match.group(0)
                            # Parse various date formats
                            for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%B %d, %Y', '%B %d %Y']:
                                try:
                                    passed_date = datetime.strptime(date_str, fmt).date().isoformat()
                                    break
                                except:
                                    continue
                        except:
                            pass
                        break

                ordinances.append({
                    "jurisdiction_id": jurisdiction_id,
                    "jurisdiction_name": jurisdiction_name,
                    "ordinance_number": ord_num,
                    "ordinance_type": ord_type,
                    "source_url": source_url,
                    "passed_date": passed_date,
                    "extraction_date": datetime.now().isoformat(),
                    "extraction_confidence": 0.8 if passed_date else 0.6,
                    "content_hash": hashlib.md5(context.encode()).hexdigest()
                })

        return ordinances


class DevelopmentBonusParser:
    """Parse development bonuses and incentives"""

    BONUS_PATTERNS = [
        (r'density\s+bonus[:\s]+(\d+)\s*%?', 'density'),
        (r'(\d+)\s*%?\s+density\s+bonus', 'density'),
        (r'height\s+bonus[:\s]+(\d+)\s*(?:feet|ft|%)', 'height'),
        (r'additional\s+(\d+)\s*(?:feet|ft|stories)', 'height'),
        (r'parking\s+reduction[:\s]+(\d+)\s*%', 'parking_reduction'),
        (r'reduce[d]?\s+parking\s+(?:by\s+)?(\d+)\s*%', 'parking_reduction'),
        (r'FAR\s+(?:bonus|increase)[:\s]+(\d+(?:\.\d+)?)', 'far'),
        (r'setback\s+reduction[:\s]+(\d+)\s*(?:feet|ft|%)', 'setback_reduction'),
    ]

    QUALIFYING_KEYWORDS = [
        'affordable housing', 'workforce housing', 'senior housing',
        'green building', 'leed', 'sustainable', 'transit oriented',
        'mixed use', 'historic preservation', 'public amenity',
        'open space', 'parking structure', 'urban infill'
    ]

    @staticmethod
    def extract_bonuses(text: str, jurisdiction_id: int, jurisdiction_name: str,
                       source_url: str) -> List[Dict]:
        """Extract development bonus programs from text"""
        bonuses = []
        seen = set()

        # Find sections that discuss bonuses
        bonus_sections = re.split(r'(?:Section|Sec\.?|Article)\s+\d+', text, flags=re.I)

        for section in bonus_sections:
            # Check if section discusses bonuses
            if not re.search(r'bonus|incentive|reduction|increase', section, re.I):
                continue

            for pattern, bonus_type in DevelopmentBonusParser.BONUS_PATTERNS:
                for match in re.finditer(pattern, section, re.I):
                    amount = float(match.group(1))

                    # Determine unit
                    unit = 'percent'
                    if 'feet' in pattern or 'ft' in pattern:
                        unit = 'feet'
                    elif 'stories' in pattern:
                        unit = 'stories'

                    # Find qualifying criteria
                    criteria = []
                    for keyword in DevelopmentBonusParser.QUALIFYING_KEYWORDS:
                        if keyword.lower() in section.lower():
                            criteria.append(keyword)

                    # Generate unique key
                    key = f"{jurisdiction_id}-{bonus_type}-{amount}"
                    if key in seen:
                        continue
                    seen.add(key)

                    # Extract bonus name from context
                    context_start = max(0, match.start() - 100)
                    context = section[context_start:match.start()]
                    name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:bonus|incentive)', context, re.I)
                    bonus_name = name_match.group(1) if name_match else f"{bonus_type.replace('_', ' ').title()} Bonus"

                    bonuses.append({
                        "jurisdiction_id": jurisdiction_id,
                        "jurisdiction_name": jurisdiction_name,
                        "bonus_name": bonus_name,
                        "bonus_type": bonus_type,
                        "bonus_amount": amount,
                        "bonus_unit": unit,
                        "qualifying_criteria": ', '.join(criteria) if criteria else None,
                        "source_url": source_url,
                        "extraction_date": datetime.now().isoformat(),
                        "extraction_confidence": 0.7 if criteria else 0.5,
                        "content_hash": hashlib.md5(section[:500].encode()).hexdigest()
                    })

        return bonuses


class OverlayParser:
    """Parse overlay district information"""

    OVERLAY_KEYWORDS = {
        'historic': ['historic', 'preservation', 'heritage'],
        'flood': ['flood', 'floodplain', 'fema', 'special flood'],
        'coastal': ['coastal', 'beachfront', 'shoreline', 'oceanfront'],
        'airport': ['airport', 'aviation', 'flight path', 'noise zone'],
        'environmental': ['environmental', 'wetland', 'conservation', 'habitat', 'scrub jay'],
        'waterfront': ['waterfront', 'riverfront', 'lakefront', 'marina'],
        'redevelopment': ['redevelopment', 'cra', 'community redevelopment'],
        'downtown': ['downtown', 'central business', 'cbd', 'town center'],
        'corridor': ['corridor', 'gateway', 'scenic'],
    }

    @staticmethod
    def extract_overlays(text: str, jurisdiction_id: int, jurisdiction_name: str,
                        source_url: str) -> List[Dict]:
        """Extract overlay district information"""
        overlays = []
        seen = set()

        for overlay_type, keywords in OverlayParser.OVERLAY_KEYWORDS.items():
            for keyword in keywords:
                # Find overlay district references
                pattern = rf'({keyword})\s+(?:overlay|district|zone)[:\s]*([A-Z0-9-]+)?'
                for match in re.finditer(pattern, text, re.I):
                    context_start = max(0, match.start() - 300)
                    context_end = min(len(text), match.end() + 500)
                    context = text[context_start:context_end]

                    # Extract code if present
                    code_match = re.search(r'[-–]([A-Z]{1,3}[-–]?[A-Z0-9]*)', context)
                    overlay_code = code_match.group(1) if code_match else f"{overlay_type[:3].upper()}-OV"

                    key = f"{jurisdiction_id}-{overlay_code}"
                    if key in seen:
                        continue
                    seen.add(key)

                    # Extract name
                    name_match = re.search(rf'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+{keyword}', context, re.I)
                    overlay_name = name_match.group(0) if name_match else f"{keyword.title()} Overlay District"

                    # Extract purpose
                    purpose_match = re.search(r'(?:purpose|intent)[:\s]*([^.]+\.)', context, re.I)
                    purpose = purpose_match.group(1) if purpose_match else None

                    overlays.append({
                        "jurisdiction_id": jurisdiction_id,
                        "jurisdiction_name": jurisdiction_name,
                        "overlay_code": overlay_code,
                        "overlay_name": overlay_name,
                        "overlay_type": overlay_type,
                        "purpose": purpose,
                        "source_url": source_url,
                        "extraction_date": datetime.now().isoformat(),
                        "extraction_confidence": 0.7,
                        "content_hash": hashlib.md5(context.encode()).hexdigest()
                    })

        return overlays


class ConditionalUseParser:
    """Parse conditional use/special exception requirements"""

    USE_CATEGORIES = {
        'residential': ['dwelling', 'residential', 'home', 'apartment', 'housing'],
        'commercial': ['retail', 'office', 'store', 'shop', 'restaurant', 'hotel'],
        'industrial': ['manufacturing', 'warehouse', 'industrial', 'factory'],
        'institutional': ['school', 'church', 'hospital', 'government', 'library'],
        'recreational': ['park', 'recreation', 'sports', 'entertainment'],
        'utility': ['utility', 'substation', 'tower', 'antenna', 'communication'],
    }

    @staticmethod
    def extract_conditional_uses(text: str, jurisdiction_id: int, jurisdiction_name: str,
                                 source_url: str, districts: List[str]) -> List[Dict]:
        """Extract conditional use requirements"""
        uses = []
        seen = set()

        # Find conditional use sections
        cu_sections = re.finditer(
            r'(?:conditional\s+use|special\s+exception|CU|SE)[:\s]*([^§]+?)(?=(?:conditional\s+use|special\s+exception|Section|$))',
            text, re.I | re.DOTALL
        )

        for section_match in cu_sections:
            section = section_match.group(1)

            # Find specific uses mentioned
            use_patterns = [
                r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s+(?:is|are|shall\s+be)\s+(?:a\s+)?(?:conditional|special)',
                r'(?:conditional|special)[^.]*(?:for|include)[:\s]*([^.]+)',
                r'•\s*([A-Z][a-z]+(?:\s+[a-z]+)*)',
                r'\d+\.\s*([A-Z][a-z]+(?:\s+[a-z]+)*)',
            ]

            for pattern in use_patterns:
                for match in re.finditer(pattern, section, re.I):
                    use_name = match.group(1).strip()

                    if len(use_name) < 3 or len(use_name) > 100:
                        continue

                    # Determine category
                    use_category = 'other'
                    for cat, keywords in ConditionalUseParser.USE_CATEGORIES.items():
                        if any(kw in use_name.lower() for kw in keywords):
                            use_category = cat
                            break

                    # Assign to districts
                    for district in districts[:5]:  # Limit to avoid duplicates
                        key = f"{jurisdiction_id}-{district}-{use_name}"
                        if key in seen:
                            continue
                        seen.add(key)

                        # Extract permit type
                        permit_type = 'conditional_use'
                        if 'special exception' in section.lower():
                            permit_type = 'special_exception'
                        elif 'site plan' in section.lower():
                            permit_type = 'site_plan_review'

                        uses.append({
                            "jurisdiction_id": jurisdiction_id,
                            "jurisdiction_name": jurisdiction_name,
                            "district_code": district,
                            "use_name": use_name,
                            "use_category": use_category,
                            "permit_type": permit_type,
                            "source_url": source_url,
                            "extraction_date": datetime.now().isoformat(),
                            "extraction_confidence": 0.6,
                            "content_hash": hashlib.md5(section[:300].encode()).hexdigest()
                        })

        return uses


class TimelineParser:
    """Parse entitlement processing timelines"""

    ENTITLEMENT_TYPES = {
        'site_plan': ['site plan', 'site development'],
        'rezoning': ['rezoning', 'rezone', 'zoning change'],
        'variance': ['variance', 'deviation'],
        'special_exception': ['special exception', 'special use'],
        'subdivision': ['subdivision', 'plat', 'platting'],
        'pud': ['pud', 'planned unit', 'planned development'],
        'annexation': ['annexation', 'annex'],
        'comp_plan_amendment': ['comprehensive plan', 'comp plan', 'future land use'],
    }

    @staticmethod
    def extract_timelines(text: str, jurisdiction_id: int, jurisdiction_name: str,
                         source_url: str) -> List[Dict]:
        """Extract entitlement processing timelines"""
        timelines = []
        seen = set()

        for ent_type, keywords in TimelineParser.ENTITLEMENT_TYPES.items():
            for keyword in keywords:
                # Find timeline references
                pattern = rf'{keyword}[^.]*?(\d+)\s*(?:days?|weeks?|months?)'
                for match in re.finditer(pattern, text, re.I):
                    days = int(match.group(1))

                    # Convert to days
                    if 'week' in match.group(0).lower():
                        days *= 7
                    elif 'month' in match.group(0).lower():
                        days *= 30

                    key = f"{jurisdiction_id}-{ent_type}"
                    if key in seen:
                        continue
                    seen.add(key)

                    # Extract context for more details
                    context_start = max(0, match.start() - 200)
                    context_end = min(len(text), match.end() + 200)
                    context = text[context_start:context_end]

                    # Check for public hearing
                    public_hearing = bool(re.search(r'public\s+hearing', context, re.I))

                    # Extract review authority
                    authority = None
                    if re.search(r'city\s+council|commission', context, re.I):
                        authority = 'city_council'
                    elif re.search(r'planning\s+(?:commission|board)', context, re.I):
                        authority = 'planning_commission'
                    elif re.search(r'board\s+of\s+adjustment', context, re.I):
                        authority = 'board_of_adjustment'
                    elif re.search(r'staff|administrative', context, re.I):
                        authority = 'staff'

                    timelines.append({
                        "jurisdiction_id": jurisdiction_id,
                        "jurisdiction_name": jurisdiction_name,
                        "entitlement_type": ent_type,
                        "process_name": keyword.title(),
                        "estimated_days_typical": days,
                        "estimated_days_minimum": max(7, days - 14),
                        "estimated_days_maximum": days + 30,
                        "public_hearing_required": public_hearing,
                        "review_authority": authority,
                        "source_url": source_url,
                        "extraction_date": datetime.now().isoformat(),
                        "extraction_confidence": 0.6,
                        "content_hash": hashlib.md5(context.encode()).hexdigest()
                    })

        return timelines


class ComprehensiveExtractor:
    """Main extraction engine"""

    def __init__(self):
        self.firecrawl = FirecrawlClient(FIRECRAWL_KEY) if FIRECRAWL_KEY else None
        self.jina = JinaClient()
        self.supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
        self.stats = ExtractionStats()
        self.all_data = {
            "ordinances": [],
            "development_bonuses": [],
            "overlay_districts": [],
            "conditional_uses": [],
            "entitlement_timelines": []
        }

    def _scrape_url(self, url: str) -> Optional[str]:
        """Scrape URL with fallback"""
        logger.info(f"  Scraping: {url}")

        # Try Firecrawl first
        if self.firecrawl:
            content = self.firecrawl.scrape(url)
            if content and len(content) > 500:
                logger.info(f"    Firecrawl: {len(content)} chars")
                return content

        # Fallback to Jina
        content = self.jina.scrape(url)
        if content and len(content) > 500:
            logger.info(f"    Jina: {len(content)} chars")
            return content

        logger.warning(f"    Failed to scrape: {url}")
        return None

    def _build_municode_urls(self, jurisdiction: Dict) -> List[str]:
        """Build URLs for a Municode jurisdiction"""
        slug = jurisdiction["slug"]
        base = f"https://library.municode.com/fl/{slug}/codes/code_of_ordinances"

        # Key sections to scrape
        sections = [
            "",  # Main page
            "?nodeId=PTIICOOR",  # Part II - Code of Ordinances
            "?nodeId=PTIIICOOR_CH26ZO",  # Zoning chapter (varies)
            "?nodeId=APXAZO",  # Zoning appendix
        ]

        return [f"{base}{section}" for section in sections]

    def extract_jurisdiction(self, jurisdiction: Dict) -> Dict:
        """Extract all data for a single jurisdiction"""
        jid = jurisdiction["id"]
        name = jurisdiction["name"]

        logger.info(f"\n{'='*60}")
        logger.info(f"EXTRACTING: {name} (ID: {jid})")
        logger.info(f"{'='*60}")

        results = {
            "ordinances": [],
            "development_bonuses": [],
            "overlay_districts": [],
            "conditional_uses": [],
            "entitlement_timelines": []
        }

        # Build URLs
        urls = self._build_municode_urls(jurisdiction)

        # Scrape all URLs
        all_content = []
        for url in urls:
            content = self._scrape_url(url)
            if content:
                all_content.append((url, content))
            time.sleep(REQUEST_DELAY)

        if not all_content:
            logger.error(f"  No content retrieved for {name}")
            self.stats.errors += 1
            return results

        # Load config for district codes
        config_path = Path(__file__).parent.parent / "config" / "brevard_jurisdictions.json"
        districts = []
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                for j in config.get("jurisdictions", []):
                    if j["id"] == jid:
                        districts = [d["code"] for d in j.get("districts", [])]
                        break

        # Extract from each scraped page
        for url, content in all_content:
            # Extract ordinances
            ordinances = OrdinanceParser.extract_ordinances(content, jid, name, url)
            results["ordinances"].extend(ordinances)

            # Extract development bonuses
            bonuses = DevelopmentBonusParser.extract_bonuses(content, jid, name, url)
            results["development_bonuses"].extend(bonuses)

            # Extract overlay districts
            overlays = OverlayParser.extract_overlays(content, jid, name, url)
            results["overlay_districts"].extend(overlays)

            # Extract conditional uses
            uses = ConditionalUseParser.extract_conditional_uses(content, jid, name, url, districts)
            results["conditional_uses"].extend(uses)

            # Extract entitlement timelines
            timelines = TimelineParser.extract_timelines(content, jid, name, url)
            results["entitlement_timelines"].extend(timelines)

        # Log results
        logger.info(f"\n  Results for {name}:")
        logger.info(f"    Ordinances: {len(results['ordinances'])}")
        logger.info(f"    Dev Bonuses: {len(results['development_bonuses'])}")
        logger.info(f"    Overlays: {len(results['overlay_districts'])}")
        logger.info(f"    Conditional Uses: {len(results['conditional_uses'])}")
        logger.info(f"    Timelines: {len(results['entitlement_timelines'])}")

        return results

    def save_to_supabase(self, data: Dict) -> Dict[str, int]:
        """Save all extracted data to Supabase"""
        results = {}

        for table, records in data.items():
            if not records:
                results[table] = 0
                continue

            # Deduplicate
            seen = set()
            unique_records = []
            for r in records:
                # Create unique key based on table
                if table == "ordinances":
                    key = f"{r['jurisdiction_id']}-{r['ordinance_number']}"
                elif table == "development_bonuses":
                    key = f"{r['jurisdiction_id']}-{r['bonus_name']}-{r['bonus_type']}"
                elif table == "overlay_districts":
                    key = f"{r['jurisdiction_id']}-{r['overlay_code']}"
                elif table == "conditional_uses":
                    key = f"{r['jurisdiction_id']}-{r['district_code']}-{r['use_name']}"
                elif table == "entitlement_timelines":
                    key = f"{r['jurisdiction_id']}-{r['entitlement_type']}"
                else:
                    key = str(hash(json.dumps(r, sort_keys=True, default=str)))

                if key not in seen:
                    seen.add(key)
                    unique_records.append(r)

            logger.info(f"  Saving {len(unique_records)} {table} records...")

            # Batch upsert
            batch_size = 100
            saved = 0
            for i in range(0, len(unique_records), batch_size):
                batch = unique_records[i:i+batch_size]
                result = self.supabase.upsert(table, batch)
                if result.get("status") == "success":
                    saved += result.get("count", 0)
                else:
                    logger.error(f"    Batch error: {result}")

            results[table] = saved

        return results

    def save_to_json(self, data: Dict, output_path: str):
        """Save data to JSON file"""
        output = {
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "jurisdictions_processed": len(JURISDICTIONS),
                "totals": {k: len(v) for k, v in data.items()}
            },
            "data": data
        }

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        logger.info(f"Saved to {output_path}")

    def run(self):
        """Run full extraction"""
        logger.info("="*60)
        logger.info("ZONEWISE COMPREHENSIVE ORDINANCE EXTRACTOR")
        logger.info("="*60)
        logger.info(f"Supabase: {SUPABASE_URL}")
        logger.info(f"Firecrawl: {'configured' if FIRECRAWL_KEY else 'NOT CONFIGURED'}")
        logger.info(f"Jurisdictions: {len(JURISDICTIONS)}")
        logger.info("="*60)

        start_time = datetime.now()

        # Process each jurisdiction
        for jurisdiction in JURISDICTIONS:
            try:
                results = self.extract_jurisdiction(jurisdiction)

                # Aggregate results
                for key, records in results.items():
                    self.all_data[key].extend(records)

                # Update stats
                self.stats.ordinances += len(results["ordinances"])
                self.stats.development_bonuses += len(results["development_bonuses"])
                self.stats.overlay_districts += len(results["overlay_districts"])
                self.stats.conditional_uses += len(results["conditional_uses"])
                self.stats.entitlement_timelines += len(results["entitlement_timelines"])

                # Progress report
                logger.info(f"\n--- RUNNING TOTALS ---")
                logger.info(f"  Ordinances: {self.stats.ordinances}")
                logger.info(f"  Dev Bonuses: {self.stats.development_bonuses}")
                logger.info(f"  Overlays: {self.stats.overlay_districts}")
                logger.info(f"  Conditional Uses: {self.stats.conditional_uses}")
                logger.info(f"  Timelines: {self.stats.entitlement_timelines}")

            except Exception as e:
                logger.error(f"Error processing {jurisdiction['name']}: {e}")
                self.stats.errors += 1

        # Save to JSON
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"comprehensive_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.save_to_json(self.all_data, str(output_path))

        # Save to Supabase
        logger.info("\n" + "="*60)
        logger.info("SAVING TO SUPABASE")
        logger.info("="*60)
        db_results = self.save_to_supabase(self.all_data)

        # Final report
        elapsed = datetime.now() - start_time
        logger.info("\n" + "="*60)
        logger.info("EXTRACTION COMPLETE")
        logger.info("="*60)
        logger.info(f"Duration: {elapsed}")
        logger.info(f"\nFINAL COUNTS:")
        logger.info(f"  Ordinances: {self.stats.ordinances} (target: 850-3,400)")
        logger.info(f"  Dev Bonuses: {self.stats.development_bonuses} (target: 85-340)")
        logger.info(f"  Overlays: {self.stats.overlay_districts} (target: 51-170)")
        logger.info(f"  Conditional Uses: {self.stats.conditional_uses} (target: 340-1,700)")
        logger.info(f"  Timelines: {self.stats.entitlement_timelines} (target: 85-170)")
        logger.info(f"  Errors: {self.stats.errors}")
        logger.info(f"\nSUPABASE SAVES:")
        for table, count in db_results.items():
            logger.info(f"  {table}: {count}")

        # Validation
        logger.info("\n" + "="*60)
        logger.info("VALIDATION")
        logger.info("="*60)
        passed = True
        if self.stats.ordinances < 500:
            logger.warning(f"  FAIL: ordinances ({self.stats.ordinances}) < 500 minimum")
            passed = False
        else:
            logger.info(f"  PASS: ordinances ({self.stats.ordinances}) >= 500 minimum")

        if self.stats.development_bonuses < 50:
            logger.warning(f"  FAIL: development_bonuses ({self.stats.development_bonuses}) < 50 minimum")
            passed = False
        else:
            logger.info(f"  PASS: development_bonuses ({self.stats.development_bonuses}) >= 50 minimum")

        if self.stats.overlay_districts < 30:
            logger.warning(f"  FAIL: overlay_districts ({self.stats.overlay_districts}) < 30 minimum")
            passed = False
        else:
            logger.info(f"  PASS: overlay_districts ({self.stats.overlay_districts}) >= 30 minimum")

        if self.stats.conditional_uses < 200:
            logger.warning(f"  FAIL: conditional_uses ({self.stats.conditional_uses}) < 200 minimum")
            passed = False
        else:
            logger.info(f"  PASS: conditional_uses ({self.stats.conditional_uses}) >= 200 minimum")

        if self.stats.entitlement_timelines < 50:
            logger.warning(f"  FAIL: entitlement_timelines ({self.stats.entitlement_timelines}) < 50 minimum")
            passed = False
        else:
            logger.info(f"  PASS: entitlement_timelines ({self.stats.entitlement_timelines}) >= 50 minimum")

        logger.info(f"\nOVERALL: {'PASSED' if passed else 'NEEDS MORE DATA'}")

        return passed

    def close(self):
        """Cleanup"""
        if self.firecrawl:
            self.firecrawl.close()
        self.jina.close()
        self.supabase.close()


def main():
    extractor = ComprehensiveExtractor()
    try:
        extractor.run()
    finally:
        extractor.close()


if __name__ == "__main__":
    main()
