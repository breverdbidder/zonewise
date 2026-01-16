#!/usr/bin/env python3
"""
ZoneWise Municipal Code Extraction System
=========================================

Extracts zoning dimensional standards from multiple code publishing platforms:
- eLaws (Satellite Beach, Indialantic, Malabar, Melbourne Beach)
- American Legal Publishing (Palm Bay)
- Municode (Melbourne, Cocoa, Titusville, Rockledge, etc.)

Part of the ZoneWise ecosystem for verified zoning data.
"""

import httpx
from bs4 import BeautifulSoup
import re
import json
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ZoningDistrict:
    """Represents a zoning district with dimensional standards"""
    jurisdiction: str
    district_code: str
    district_name: str
    source_url: str
    source_section: str
    last_extracted: str
    
    # Dimensional Standards
    front_setback_ft: Optional[int] = None
    rear_setback_ft: Optional[int] = None
    side_setback_ft: Optional[int] = None
    corner_setback_ft: Optional[int] = None
    max_height_ft: Optional[int] = None
    max_stories: Optional[int] = None
    max_lot_coverage_pct: Optional[float] = None
    max_impervious_pct: Optional[float] = None
    min_lot_size_sqft: Optional[int] = None
    min_lot_width_ft: Optional[int] = None
    min_lot_depth_ft: Optional[int] = None
    min_dwelling_size_sqft: Optional[int] = None
    max_density_units_acre: Optional[float] = None
    parking_spaces_per_unit: Optional[float] = None
    floor_area_ratio: Optional[float] = None
    
    # Metadata
    verified: bool = False
    verification_notes: Optional[str] = None
    raw_text: Optional[str] = None


class eLawsExtractor:
    """Extract zoning data from eLaws municipal code sites"""
    
    BASE_URLS = {
        "satellite_beach": "https://satellitebeach.elaws.us",
        "indialantic": "https://indialantic.elaws.us",
        "malabar": "https://malabar.elaws.us",
        "melbourne_beach": "https://melbournebeach.elaws.us",
    }
    
    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
            },
            timeout=30,
            follow_redirects=True
        )
    
    def get_chapter_structure(self, jurisdiction: str) -> Dict[str, str]:
        """Get the zoning chapter structure for a jurisdiction"""
        base_url = self.BASE_URLS.get(jurisdiction)
        if not base_url:
            raise ValueError(f"Unknown jurisdiction: {jurisdiction}")
        
        # Get the code overview
        resp = self.client.get(f"{base_url}/code/ordinances")
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        chapters = {}
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip()
            href = link.get('href', '')
            if any(term in text.lower() for term in ['zoning', 'land development', 'chapter 30']):
                chapters[text] = href
        
        return chapters
    
    def get_district_sections(self, jurisdiction: str, chapter_url: str) -> List[Dict[str, str]]:
        """Get all district sections from a zoning chapter"""
        base_url = self.BASE_URLS.get(jurisdiction)
        
        # Handle relative URLs
        if not chapter_url.startswith('http'):
            full_url = f"{base_url}{chapter_url}" if chapter_url.startswith('/') else f"{base_url}/code/{chapter_url}"
        else:
            full_url = chapter_url
        
        resp = self.client.get(full_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        districts = []
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip()
            href = link.get('href', '')
            
            # Match district patterns (R-1, RM-2, C-1, etc.)
            if re.search(r'§\s*\d+-\d+', text) and re.search(r'[RC][MSL]?-?\d|district', text, re.I):
                section_match = re.search(r'§\s*(\d+-\d+)', text)
                section = section_match.group(1) if section_match else ''
                
                districts.append({
                    "section": section,
                    "name": text,
                    "url": href if href.startswith('http') else f"{base_url}{href}"
                })
        
        return districts
    
    def extract_district_data(self, jurisdiction: str, section_url: str) -> ZoningDistrict:
        """Extract dimensional standards from a district section"""
        base_url = self.BASE_URLS.get(jurisdiction)
        
        resp = self.client.get(section_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        content = soup.get_text()
        
        # Extract section number and name from the content
        section_match = re.search(r'§\s*(\d+-\d+(?:\.\d+)?)\.\s*([^,\n]+)', content)
        section_num = section_match.group(1) if section_match else ""
        district_name = section_match.group(2).strip() if section_match else ""
        
        # Extract district code from name (e.g., "R-1A" from "R-1A, single-family residential")
        code_match = re.search(r'([A-Z]{1,2}-?\d[A-Z]?)', district_name, re.I)
        district_code = code_match.group(1).upper() if code_match else ""
        
        # Create district object
        district = ZoningDistrict(
            jurisdiction=jurisdiction.replace('_', ' ').title(),
            district_code=district_code,
            district_name=district_name,
            source_url=section_url,
            source_section=f"§{section_num}",
            last_extracted=datetime.now().isoformat(),
            raw_text=content[:5000]
        )
        
        # Extract dimensional standards using regex patterns
        district.front_setback_ft = self._extract_number(content, r'front\s*(?:yard\s*)?setback[:\s]*(\d+)', default=None)
        district.rear_setback_ft = self._extract_number(content, r'rear\s*(?:yard\s*)?setback[:\s]*(\d+)', default=None)
        district.side_setback_ft = self._extract_number(content, r'side\s*(?:interior\s*)?(?:yard\s*)?setback[:\s]*(\d+)', default=None)
        district.corner_setback_ft = self._extract_number(content, r'(?:corner|side\s*street)\s*(?:yard\s*)?setback[:\s]*(\d+)', default=None)
        district.max_height_ft = self._extract_number(content, r'(?:maximum\s*)?(?:building\s*)?height[:\s]*(\d+)\s*(?:feet|ft)', default=None)
        district.max_stories = self._extract_number(content, r'(?:maximum\s*)?(\d+)\s*stor(?:y|ies)', default=None)
        district.max_lot_coverage_pct = self._extract_number(content, r'(?:maximum\s*)?lot\s*coverage[:\s]*(\d+)\s*%?', default=None)
        district.max_impervious_pct = self._extract_number(content, r'impervious[:\s]*(\d+)\s*%?', default=None)
        district.min_lot_size_sqft = self._extract_number(content, r'(?:minimum\s*)?lot\s*(?:size|area)[:\s]*([\d,]+)', remove_commas=True, default=None)
        district.min_lot_width_ft = self._extract_number(content, r'(?:minimum\s*)?lot\s*width[:\s]*(\d+)', default=None)
        district.min_lot_depth_ft = self._extract_number(content, r'(?:minimum\s*)?lot\s*depth[:\s]*(\d+)', default=None)
        district.min_dwelling_size_sqft = self._extract_number(content, r'(?:minimum\s*)?(?:living|dwelling|floor)\s*area[:\s]*([\d,]+)', remove_commas=True, default=None)
        district.max_density_units_acre = self._extract_float(content, r'density[:\s]*([\d.]+)', default=None)
        district.floor_area_ratio = self._extract_float(content, r'(?:floor\s*area\s*ratio|FAR)[:\s]*([\d.]+)', default=None)
        
        return district
    
    def _extract_number(self, text: str, pattern: str, remove_commas: bool = False, default=None) -> Optional[int]:
        """Extract a number from text using regex"""
        match = re.search(pattern, text, re.I)
        if match:
            value = match.group(1)
            if remove_commas:
                value = value.replace(',', '')
            try:
                return int(value)
            except ValueError:
                return default
        return default
    
    def _extract_float(self, text: str, pattern: str, default=None) -> Optional[float]:
        """Extract a float from text using regex"""
        match = re.search(pattern, text, re.I)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return default
        return default
    
    def extract_all_districts(self, jurisdiction: str) -> List[ZoningDistrict]:
        """Extract all zoning districts for a jurisdiction"""
        logger.info(f"Extracting districts for {jurisdiction}")
        
        # Get chapter structure
        chapters = self.get_chapter_structure(jurisdiction)
        logger.info(f"Found chapters: {list(chapters.keys())}")
        
        # Find zoning article
        zoning_chapter = None
        for name, url in chapters.items():
            if 'land development' in name.lower() or 'zoning' in name.lower():
                zoning_chapter = url
                break
        
        if not zoning_chapter:
            logger.warning(f"No zoning chapter found for {jurisdiction}")
            return []
        
        # Get the Article IV - Zoning subsection
        base_url = self.BASE_URLS[jurisdiction]
        resp = self.client.get(f"{base_url}{zoning_chapter}")
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find Article IV (Zoning) link
        article_iv_url = None
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip().lower()
            if 'article iv' in text or 'article 4' in text or 'zoning' in text:
                href = link.get('href')
                if 'artiv' in href.lower() or 'art4' in href.lower():
                    article_iv_url = href
                    break
        
        if article_iv_url:
            districts_list = self.get_district_sections(jurisdiction, article_iv_url)
        else:
            districts_list = self.get_district_sections(jurisdiction, zoning_chapter)
        
        logger.info(f"Found {len(districts_list)} district sections")
        
        # Extract data for each district
        results = []
        for district_info in districts_list:
            try:
                district = self.extract_district_data(jurisdiction, district_info['url'])
                results.append(district)
                logger.info(f"  Extracted: {district.district_code} - {district.district_name[:40]}")
            except Exception as e:
                logger.error(f"  Error extracting {district_info['section']}: {e}")
        
        return results


class AmericanLegalExtractor:
    """Extract zoning data from American Legal Publishing sites"""
    
    BASE_URL = "https://codelibrary.amlegal.com"
    
    JURISDICTIONS = {
        "palm_bay": "/codes/palmbay/latest",
    }
    
    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
            },
            timeout=30,
            follow_redirects=True
        )
    
    def get_toc(self, jurisdiction: str) -> Dict[str, str]:
        """Get table of contents for a jurisdiction"""
        path = self.JURISDICTIONS.get(jurisdiction)
        if not path:
            raise ValueError(f"Unknown jurisdiction: {jurisdiction}")
        
        resp = self.client.get(f"{self.BASE_URL}{path}/overview")
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        chapters = {}
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip()
            href = link.get('href', '')
            if text and '/codes/' in href:
                chapters[text] = href
        
        return chapters
    
    def extract_all_districts(self, jurisdiction: str) -> List[ZoningDistrict]:
        """Extract all zoning districts from American Legal Publishing"""
        logger.info(f"Extracting from American Legal: {jurisdiction}")
        
        toc = self.get_toc(jurisdiction)
        logger.info(f"Found {len(toc)} sections in TOC")
        
        # Find zoning chapter
        zoning_sections = {k: v for k, v in toc.items() 
                         if any(term in k.lower() for term in ['zoning', 'land development', 'land use'])}
        
        logger.info(f"Zoning sections found: {list(zoning_sections.keys())}")
        
        # Implementation continues similarly to eLaws...
        return []


class BrevardCountyExtractor:
    """Coordinate extraction across all Brevard County jurisdictions"""
    
    JURISDICTION_SOURCES = {
        # eLaws sites
        "satellite_beach": ("elaws", "satellite_beach"),
        "indialantic": ("elaws", "indialantic"),
        "malabar": ("elaws", "malabar"),
        "melbourne_beach": ("elaws", "melbourne_beach"),
        
        # American Legal sites
        "palm_bay": ("american_legal", "palm_bay"),
        
        # Municode sites (require Firecrawl/Selenium)
        "melbourne": ("municode", "melbourne"),
        "cocoa": ("municode", "cocoa"),
        "cocoa_beach": ("municode", "cocoa_beach"),
        "titusville": ("municode", "titusville"),
        "rockledge": ("municode", "rockledge"),
        "cape_canaveral": ("municode", "cape_canaveral"),
        "west_melbourne": ("municode", "west_melbourne"),
        "brevard_county": ("municode", "brevard_county"),
        "indian_harbour_beach": ("municode", "indian_harbour_beach"),
        
        # Unknown/TBD
        "grant_valkaria": ("tbd", "grant_valkaria"),
        "melbourne_village": ("tbd", "melbourne_village"),
        "palm_shores": ("tbd", "palm_shores"),
    }
    
    def __init__(self):
        self.elaws = eLawsExtractor()
        self.american_legal = AmericanLegalExtractor()
    
    def extract_jurisdiction(self, jurisdiction: str) -> List[ZoningDistrict]:
        """Extract zoning data for a specific jurisdiction"""
        source_type, source_id = self.JURISDICTION_SOURCES.get(jurisdiction, (None, None))
        
        if source_type == "elaws":
            return self.elaws.extract_all_districts(source_id)
        elif source_type == "american_legal":
            return self.american_legal.extract_all_districts(source_id)
        elif source_type == "municode":
            logger.warning(f"{jurisdiction} uses Municode - requires Firecrawl integration")
            return []
        else:
            logger.warning(f"Unknown source for {jurisdiction}")
            return []
    
    def extract_all(self) -> Dict[str, List[ZoningDistrict]]:
        """Extract zoning data for all Brevard County jurisdictions"""
        results = {}
        
        for jurisdiction in self.JURISDICTION_SOURCES.keys():
            try:
                districts = self.extract_jurisdiction(jurisdiction)
                results[jurisdiction] = districts
                logger.info(f"{jurisdiction}: {len(districts)} districts extracted")
            except Exception as e:
                logger.error(f"{jurisdiction}: Error - {e}")
                results[jurisdiction] = []
        
        return results
    
    def export_to_json(self, results: Dict[str, List[ZoningDistrict]], filepath: str):
        """Export results to JSON"""
        output = {}
        for jurisdiction, districts in results.items():
            output[jurisdiction] = [asdict(d) for d in districts]
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        logger.info(f"Exported to {filepath}")


def main():
    """Main entry point"""
    extractor = BrevardCountyExtractor()
    
    # Test with Satellite Beach (eLaws)
    print("\n" + "="*60)
    print("Testing Satellite Beach extraction...")
    print("="*60 + "\n")
    
    districts = extractor.extract_jurisdiction("satellite_beach")
    
    print(f"\nExtracted {len(districts)} districts:")
    for d in districts:
        print(f"\n  {d.district_code}: {d.district_name[:50]}")
        print(f"    Source: {d.source_section}")
        print(f"    Front setback: {d.front_setback_ft} ft")
        print(f"    Max height: {d.max_height_ft} ft")
        print(f"    Lot coverage: {d.max_lot_coverage_pct}%")
    
    # Export results
    if districts:
        extractor.export_to_json({"satellite_beach": districts}, "/tmp/satellite_beach_zoning.json")


if __name__ == "__main__":
    main()
