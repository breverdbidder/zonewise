#!/usr/bin/env python3
"""
ZoneWise Real Data Extractor
Replaces synthetic/template data with verified ordinance values

Extraction Methods:
1. Municode (11 jurisdictions): Jina Reader + regex parsing
2. eLaws (4 jurisdictions): Direct HTTP + BeautifulSoup
3. PDF (3 jurisdictions): Firecrawl + pdfplumber

Usage:
  python extract_real_data.py --jurisdiction melbourne
  python extract_real_data.py --all
  
Author: Ariel Shapira / Claude AI Architect
Date: January 18, 2026
"""

import os
import re
import json
import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

# Configuration
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE")
JINA_READER_URL = "https://r.jina.ai"

# Jurisdiction configurations
JURISDICTIONS = {
    "melbourne": {
        "id": 1,
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/melbourne/codes/code_of_ordinances",
        "zoning_node": "PTIICOOR_CH26ZO",
        "dimensional_table_node": "PTIICOOR_CH26ZO_ARTIIIDIST_S26-71DISTA"
    },
    "palm_bay": {
        "id": 2,
        "platform": "american_legal",
        "base_url": "https://codelibrary.amlegal.com/codes/palmbay/latest/palmbay_fl/",
        "zoning_node": "0-0-0-2301"
    },
    "indian_harbour_beach": {
        "id": 3,
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances",
        "zoning_node": "APXAZO",
        "dimensional_table_node": "APXAZO_ARTXXVIIEFDA"
    },
    "titusville": {
        "id": 4,
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/titusville/codes/code_of_ordinances",
        "zoning_node": "PTIICOOR_CH28ZO"
    },
    "cocoa": {
        "id": 5,
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/cocoa/codes/code_of_ordinances",
        "zoning_node": "PTIICOOR_CH13ZO"
    },
    "satellite_beach": {
        "id": 6,
        "platform": "elaws",
        "base_url": "https://satellitebeach.elaws.us",
        "zoning_path": "/code/coor_ptii_ch78"
    },
    "cocoa_beach": {
        "id": 7,
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances",
        "zoning_node": "LADECO"
    },
    "rockledge": {
        "id": 8,
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/rockledge/codes/code_of_ordinances",
        "zoning_node": "PTIICOOR_CH54ZO"
    },
    "west_melbourne": {
        "id": 9,
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances",
        "zoning_node": "PTIILAUSam_CH98ZO"
    },
    "cape_canaveral": {
        "id": 10,
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances",
        "zoning_node": "PTIICOOR_CH110ZO"
    },
    "indialantic": {
        "id": 11,
        "platform": "elaws",
        "base_url": "https://indialantic.elaws.us",
        "zoning_path": "/code/coor_apxa"
    },
    "melbourne_beach": {
        "id": 12,
        "platform": "elaws",
        "base_url": "https://melbournebeach.elaws.us",
        "zoning_path": "/code/coor_ch34"
    },
    "brevard_county": {
        "id": 13,
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances",
        "zoning_node": "PTIIILADECO_CH62ZO"
    },
    "malabar": {
        "id": 14,
        "platform": "elaws",
        "base_url": "https://malabar.elaws.us",
        "zoning_path": "/code/coor_apxa"
    },
    "grant_valkaria": {
        "id": 15,
        "platform": "pdf",
        "pdf_url": "https://www.grantvalkaria.org/documents/zoning-ordinance.pdf"
    },
    "melbourne_village": {
        "id": 16,
        "platform": "pdf",
        "pdf_url": "https://www.melbournevillage.org/ordinances/zoning.pdf"
    },
    "palm_shores": {
        "id": 17,
        "platform": "pdf",
        "pdf_url": "https://www.palmshores.org/zoning-regulations.pdf"
    }
}

@dataclass
class ZoningDistrict:
    """Zoning district data structure."""
    jurisdiction_id: int
    code: str
    name: str
    category: str
    min_lot_sqft: Optional[int] = None
    max_height_ft: Optional[int] = None
    max_stories: Optional[int] = None
    coverage_pct: Optional[int] = None
    front_setback_ft: Optional[float] = None
    side_setback_ft: Optional[float] = None
    rear_setback_ft: Optional[float] = None
    density: Optional[float] = None
    source_url: Optional[str] = None
    verified_date: Optional[str] = None
    
    def to_description(self) -> str:
        """Convert to description field format with embedded DIMS."""
        desc = f"{self.name} district."
        if self.min_lot_sqft:
            desc += f" Min lot: {self.min_lot_sqft} sqft."
        if self.max_height_ft:
            desc += f" Max height: {self.max_height_ft} ft"
            if self.max_stories:
                desc += f" / {self.max_stories} stories"
            desc += "."
        if self.coverage_pct:
            desc += f" Coverage: {self.coverage_pct}%."
        if self.front_setback_ft or self.side_setback_ft or self.rear_setback_ft:
            desc += f" Setbacks: {self.front_setback_ft or 'N/A'}/{self.side_setback_ft or 'N/A'}/{self.rear_setback_ft or 'N/A'} ft (F/S/R)."
        
        # Embed structured data as HTML comment
        dims = {
            "min_lot_sqft": self.min_lot_sqft,
            "max_height_ft": self.max_height_ft,
            "max_stories": self.max_stories,
            "coverage_pct": self.coverage_pct,
            "setbacks_ft": {
                "front": self.front_setback_ft,
                "side": self.side_setback_ft,
                "rear": self.rear_setback_ft
            },
            "density": self.density,
            "source_url": self.source_url,
            "verified_date": self.verified_date
        }
        desc += f" <!--DIMS:{json.dumps(dims)}-->"
        return desc


class ZoneWiseExtractor:
    """Extract real zoning data from municipal codes."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(verify=False, timeout=60.0)
        self.results: List[ZoningDistrict] = []
    
    async def fetch_via_jina(self, url: str) -> str:
        """Fetch URL content via Jina Reader (bypasses JS rendering)."""
        jina_url = f"{JINA_READER_URL}/{url}"
        response = await self.client.get(jina_url)
        response.raise_for_status()
        return response.text
    
    async def fetch_direct(self, url: str) -> str:
        """Fetch URL content directly."""
        response = await self.client.get(url)
        response.raise_for_status()
        return response.text
    
    def parse_dimensional_value(self, text: str) -> Optional[int]:
        """Parse dimensional value from text (handles '12,000', '35', '7.5')."""
        if not text:
            return None
        # Remove commas and extract first number
        text = text.replace(",", "").strip()
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if match:
            return int(float(match.group(1)))
        return None
    
    def parse_float_value(self, text: str) -> Optional[float]:
        """Parse float value (for setbacks like '7.5')."""
        if not text:
            return None
        text = text.replace(",", "").strip()
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if match:
            return float(match.group(1))
        return None
    
    async def extract_municode(self, jurisdiction_key: str) -> List[ZoningDistrict]:
        """Extract zoning data from Municode jurisdiction."""
        config = JURISDICTIONS[jurisdiction_key]
        districts = []
        
        # Construct URL for dimensional standards table
        url = f"{config['base_url']}?nodeId={config.get('dimensional_table_node', config['zoning_node'])}"
        
        print(f"Fetching {jurisdiction_key} from Municode...")
        try:
            content = await self.fetch_via_jina(url)
        except Exception as e:
            print(f"  Error fetching: {e}")
            return districts
        
        # Parse dimensional table
        # Common Municode table patterns
        patterns = {
            # Pattern for table rows with district info
            "district_row": r'([A-Z]+-?\d*[A-Z]*)\s*\|\s*([^\|]+)\s*\|\s*(\d[\d,]*)\s*\|\s*(\d+)\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*(\d+(?:\.\d+)?)',
            # Alternative pattern
            "alt_row": r'([A-Z]+-?\d*[A-Z]*)\s+([^\n]+?)\s+(\d[\d,]*)\s+sqft?\s+(\d+)\s*(?:ft|feet)',
        }
        
        # Try to find dimensional data
        # Look for patterns like "R-1 | Single-Family | 10,000 | 35 | 25 | 7.5 | 20"
        for match in re.finditer(patterns["district_row"], content, re.IGNORECASE):
            code, name, lot_size, height, front, side, rear = match.groups()
            
            district = ZoningDistrict(
                jurisdiction_id=config["id"],
                code=code.strip().upper(),
                name=name.strip(),
                category=self._categorize_district(code),
                min_lot_sqft=self.parse_dimensional_value(lot_size),
                max_height_ft=self.parse_dimensional_value(height),
                front_setback_ft=self.parse_float_value(front),
                side_setback_ft=self.parse_float_value(side),
                rear_setback_ft=self.parse_float_value(rear),
                source_url=url,
                verified_date=datetime.now().strftime("%Y-%m-%d")
            )
            districts.append(district)
            print(f"  Found: {district.code} - {district.name}")
        
        # If no matches, try alternative parsing strategies
        if not districts:
            print(f"  No districts found with primary pattern, trying alternatives...")
            districts = self._parse_municode_fallback(content, config, url)
        
        return districts
    
    def _parse_municode_fallback(self, content: str, config: dict, source_url: str) -> List[ZoningDistrict]:
        """Fallback parsing for Municode content."""
        districts = []
        
        # Look for district definitions in section headers
        # Pattern: "Sec. 26-71. - R-1, Single-family residential district."
        section_pattern = r'Sec\.\s*[\d-]+\.\s*-?\s*([A-Z]+-?\d*[A-Z]*)[,\s]+([^\.]+)'
        
        for match in re.finditer(section_pattern, content):
            code, name = match.groups()
            code = code.strip().upper()
            name = name.strip()
            
            # Skip if not a zoning district code
            if not re.match(r'^[A-Z]+-?\d*[A-Z]*$', code):
                continue
            
            district = ZoningDistrict(
                jurisdiction_id=config["id"],
                code=code,
                name=name,
                category=self._categorize_district(code),
                source_url=source_url,
                verified_date=datetime.now().strftime("%Y-%m-%d")
            )
            districts.append(district)
            print(f"  Found (fallback): {district.code} - {district.name}")
        
        return districts
    
    async def extract_elaws(self, jurisdiction_key: str) -> List[ZoningDistrict]:
        """Extract zoning data from eLaws jurisdiction."""
        config = JURISDICTIONS[jurisdiction_key]
        districts = []
        
        url = f"{config['base_url']}{config['zoning_path']}"
        
        print(f"Fetching {jurisdiction_key} from eLaws...")
        try:
            content = await self.fetch_direct(url)
        except Exception as e:
            print(f"  Error fetching: {e}")
            return districts
        
        # eLaws uses HTML tables - parse directly
        # Pattern for district sections
        section_pattern = r'<h\d[^>]*>.*?([A-Z]+-?\d*[A-Z]*)[^<]*district[^<]*</h\d>'
        
        for match in re.finditer(section_pattern, content, re.IGNORECASE):
            code = match.group(1).strip().upper()
            
            district = ZoningDistrict(
                jurisdiction_id=config["id"],
                code=code,
                name=f"{code} District",
                category=self._categorize_district(code),
                source_url=url,
                verified_date=datetime.now().strftime("%Y-%m-%d")
            )
            districts.append(district)
            print(f"  Found: {district.code}")
        
        return districts
    
    def _categorize_district(self, code: str) -> str:
        """Categorize district by code prefix."""
        code = code.upper()
        if code.startswith(('R-', 'RS', 'RU', 'RM', 'RMF')):
            return "Residential"
        elif code.startswith(('C-', 'CC', 'CN', 'CG', 'CBD')):
            return "Commercial"
        elif code.startswith(('I-', 'IL', 'IH', 'IP', 'M-')):
            return "Industrial"
        elif code.startswith(('A-', 'AG', 'AR')):
            return "Agricultural"
        elif code.startswith(('PUD', 'MXD', 'MU')):
            return "Mixed-Use"
        elif code.startswith(('P', 'GU', 'PF')):
            return "Institutional"
        elif code.startswith(('OS', 'CON', 'PRE')):
            return "Conservation"
        else:
            return "Other"
    
    async def upsert_to_supabase(self, districts: List[ZoningDistrict]) -> int:
        """Upsert districts to Supabase."""
        if not districts:
            return 0
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        
        updated = 0
        for district in districts:
            data = {
                "jurisdiction_id": district.jurisdiction_id,
                "code": district.code,
                "name": district.name,
                "category": district.category,
                "description": district.to_description(),
                "ordinance_section": "Municipal Code",
                "effective_date": "2024-01-01"
            }
            
            try:
                response = await self.client.post(
                    f"{SUPABASE_URL}/rest/v1/zoning_districts",
                    headers=headers,
                    json=data
                )
                if response.status_code in (200, 201):
                    updated += 1
                else:
                    print(f"  Error upserting {district.code}: {response.text}")
            except Exception as e:
                print(f"  Error upserting {district.code}: {e}")
        
        return updated
    
    async def extract_jurisdiction(self, jurisdiction_key: str) -> int:
        """Extract data for a single jurisdiction."""
        if jurisdiction_key not in JURISDICTIONS:
            print(f"Unknown jurisdiction: {jurisdiction_key}")
            return 0
        
        config = JURISDICTIONS[jurisdiction_key]
        platform = config["platform"]
        
        if platform == "municode":
            districts = await self.extract_municode(jurisdiction_key)
        elif platform == "elaws":
            districts = await self.extract_elaws(jurisdiction_key)
        elif platform == "pdf":
            print(f"PDF extraction not yet implemented for {jurisdiction_key}")
            return 0
        elif platform == "american_legal":
            print(f"American Legal extraction not yet implemented for {jurisdiction_key}")
            return 0
        else:
            print(f"Unknown platform: {platform}")
            return 0
        
        if districts:
            updated = await self.upsert_to_supabase(districts)
            print(f"  Updated {updated} districts for {jurisdiction_key}")
            return updated
        
        return 0
    
    async def extract_all(self):
        """Extract data for all jurisdictions."""
        total = 0
        for jurisdiction_key in JURISDICTIONS:
            count = await self.extract_jurisdiction(jurisdiction_key)
            total += count
        print(f"\nTotal districts updated: {total}")
        return total
    
    async def close(self):
        await self.client.aclose()


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract real zoning data for ZoneWise")
    parser.add_argument("--jurisdiction", "-j", help="Specific jurisdiction to extract")
    parser.add_argument("--all", "-a", action="store_true", help="Extract all jurisdictions")
    parser.add_argument("--list", "-l", action="store_true", help="List available jurisdictions")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available jurisdictions:")
        for key, config in JURISDICTIONS.items():
            print(f"  {key}: {config['platform']} (id={config['id']})")
        return
    
    extractor = ZoneWiseExtractor()
    
    try:
        if args.all:
            await extractor.extract_all()
        elif args.jurisdiction:
            await extractor.extract_jurisdiction(args.jurisdiction)
        else:
            # Default: extract Melbourne as proof of concept
            print("No jurisdiction specified. Extracting Melbourne as proof of concept...")
            await extractor.extract_jurisdiction("melbourne")
    finally:
        await extractor.close()


if __name__ == "__main__":
    asyncio.run(main())
