#!/usr/bin/env python3
"""
ZoneWise Real Ordinance Extraction Engine
Extracts dimensional standards from Brevard County FL jurisdictions using Firecrawl

Requirements:
  pip install httpx supabase python-dotenv --break-system-packages

Environment Variables:
  FIRECRAWL_API_KEY - Firecrawl API key for JS-rendered page scraping
  SUPABASE_URL - Supabase project URL
  SUPABASE_SERVICE_KEY - Supabase service role key

Author: Claude AI Architect for BidDeed.AI
Date: January 18, 2026
Version: 3.0.0
"""

import os
import sys
import json
import re
import time
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('extraction.log')
    ]
)
logger = logging.getLogger(__name__)

# Constants
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"
JINA_URL = "https://r.jina.ai/"
REQUEST_DELAY = 2.0  # Seconds between requests to avoid rate limiting
MAX_RETRIES = 3


@dataclass
class SetbackStandards:
    """Setback requirements with conditional variations"""
    standard_ft: Optional[float] = None
    with_alley_ft: Optional[float] = None
    corner_lot_ft: Optional[float] = None
    adjacent_residential_ft: Optional[float] = None
    adjacent_commercial_ft: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class DimensionalStandards:
    """Complete dimensional standards for a zoning district"""
    min_lot_size_sqft: Optional[int] = None
    min_lot_width_ft: Optional[float] = None
    min_lot_depth_ft: Optional[float] = None
    min_living_area_sqft: Optional[int] = None
    max_height_ft: Optional[int] = None
    max_stories: Optional[int] = None
    max_lot_coverage_pct: Optional[float] = None
    max_impervious_pct: Optional[float] = None
    max_far: Optional[float] = None
    density_units_per_acre: Optional[float] = None
    parking_spaces_required: Optional[float] = None
    front_setback: Optional[SetbackStandards] = None
    side_setback: Optional[SetbackStandards] = None
    rear_setback: Optional[SetbackStandards] = None


@dataclass 
class DistrictData:
    """Extracted data for a single zoning district"""
    jurisdiction_id: int
    jurisdiction_name: str
    code: str
    name: str
    category: str
    ordinance_section: Optional[str] = None
    source_url: Optional[str] = None
    extraction_date: Optional[str] = None
    extraction_status: str = "pending"
    extraction_confidence: float = 0.0
    raw_text_excerpt: Optional[str] = None
    dimensional_standards: Optional[DimensionalStandards] = None
    permitted_uses: Optional[List[str]] = None
    conditional_uses: Optional[List[str]] = None
    notes: Optional[str] = None


class FirecrawlClient:
    """Client for Firecrawl API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=120.0)
    
    def scrape(self, url: str, wait_for: int = 5000) -> Optional[str]:
        """Scrape a URL and return markdown content"""
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
                logger.error("Firecrawl API key invalid or expired")
            else:
                logger.error(f"Firecrawl HTTP error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Firecrawl request failed: {e}")
        
        return None
    
    def close(self):
        self.client.close()


class JinaClient:
    """Fallback client using Jina Reader"""
    
    def __init__(self):
        self.client = httpx.Client(timeout=60.0)
    
    def scrape(self, url: str) -> Optional[str]:
        """Scrape a URL using Jina Reader"""
        try:
            response = self.client.get(
                f"{JINA_URL}{url}",
                headers={"Accept": "text/plain"}
            )
            
            if response.status_code == 200:
                return response.text
                
        except Exception as e:
            logger.error(f"Jina request failed: {e}")
        
        return None
    
    def close(self):
        self.client.close()


class DimensionalParser:
    """Parser for extracting dimensional standards from ordinance text"""
    
    # Regex patterns for different dimensional values
    LOT_SIZE_PATTERNS = [
        r'minimum\s+lot\s+(?:size|area)[:\s]*(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft|square\s*feet)',
        r'lot\s+area[:\s]*(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft|square\s*feet)\s*minimum',
        r'(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft|square\s*feet)\s+(?:minimum\s+)?lot',
        r'min(?:imum)?\s+(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft|sf)',
    ]
    
    LOT_WIDTH_PATTERNS = [
        r'minimum\s+(?:lot\s+)?width[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|\')',
        r'lot\s+width[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|\')',
        r'width[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|\')\s*min',
        r'(\d+(?:\.\d+)?)\s*(?:ft|feet|\')\s+(?:lot\s+)?width',
    ]
    
    FRONT_SETBACK_PATTERNS = [
        r'front\s+(?:yard\s+)?setback[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|\')',
        r'front[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|\')',
        r'(\d+(?:\.\d+)?)\s*(?:ft|feet|\')\s+front\s+(?:yard\s+)?setback',
        r'front\s+yard[:\s]*(\d+(?:\.\d+)?)',
    ]
    
    SIDE_SETBACK_PATTERNS = [
        r'(?:interior\s+)?side\s+(?:yard\s+)?setback[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|\')',
        r'side[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|\')',
        r'(\d+(?:\.\d+)?)\s*(?:ft|feet|\')\s+(?:each\s+)?side',
        r'side\s+yard[:\s]*(\d+(?:\.\d+)?)',
    ]
    
    REAR_SETBACK_PATTERNS = [
        r'rear\s+(?:yard\s+)?setback[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|\')',
        r'rear[:\s]*(\d+(?:\.\d+)?)\s*(?:ft|feet|\')',
        r'(\d+(?:\.\d+)?)\s*(?:ft|feet|\')\s+rear',
        r'rear\s+yard[:\s]*(\d+(?:\.\d+)?)',
    ]
    
    HEIGHT_PATTERNS = [
        r'maximum\s+(?:building\s+)?height[:\s]*(\d+)\s*(?:ft|feet|\')',
        r'height[:\s]*(\d+)\s*(?:ft|feet|\')\s*max',
        r'(\d+)\s*(?:ft|feet|\')\s+max(?:imum)?\s+height',
        r'max\s+height[:\s]*(\d+)',
    ]
    
    LIVING_AREA_PATTERNS = [
        r'minimum\s+(?:living|floor|dwelling)\s+area[:\s]*(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft|sf)',
        r'(?:living|floor)\s+area[:\s]*(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft|sf)\s*min',
        r'(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft|sf)\s+(?:minimum\s+)?(?:living|floor)\s+area',
    ]
    
    COVERAGE_PATTERNS = [
        r'(?:maximum\s+)?lot\s+coverage[:\s]*(\d+(?:\.\d+)?)\s*%',
        r'(\d+(?:\.\d+)?)\s*%\s+(?:max(?:imum)?\s+)?lot\s+coverage',
        r'coverage[:\s]*(\d+(?:\.\d+)?)\s*%',
    ]
    
    DENSITY_PATTERNS = [
        r'(\d+(?:\.\d+)?)\s+(?:units?|du|dwelling\s+units?)\s+per\s+acre',
        r'density[:\s]*(\d+(?:\.\d+)?)\s+(?:du|units?)/acre',
        r'max(?:imum)?\s+density[:\s]*(\d+(?:\.\d+)?)',
    ]
    
    @staticmethod
    def _extract_value(text: str, patterns: List[str]) -> Optional[float]:
        """Extract first matching numeric value from text"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    value_str = match.group(1).replace(",", "")
                    return float(value_str)
                except (ValueError, IndexError):
                    continue
        return None
    
    @staticmethod
    def _extract_setback(text: str, setback_type: str, patterns: List[str]) -> SetbackStandards:
        """Extract setback standards with conditional variations"""
        setback = SetbackStandards()
        setback.standard_ft = DimensionalParser._extract_value(text, patterns)
        
        # Look for conditional variations
        alley_patterns = [
            rf'{setback_type}[^.]*(?:with|from)\s+alley[^.]*(\d+(?:\.\d+)?)\s*(?:ft|feet)',
            rf'(\d+(?:\.\d+)?)\s*(?:ft|feet)[^.]*alley[^.]*{setback_type}',
        ]
        setback.with_alley_ft = DimensionalParser._extract_value(text, alley_patterns)
        
        corner_patterns = [
            rf'corner\s+(?:lot\s+)?{setback_type}[^.]*(\d+(?:\.\d+)?)\s*(?:ft|feet)',
            rf'{setback_type}[^.]*corner\s+lot[^.]*(\d+(?:\.\d+)?)\s*(?:ft|feet)',
        ]
        setback.corner_lot_ft = DimensionalParser._extract_value(text, corner_patterns)
        
        return setback
    
    def parse(self, text: str, district_code: str = "") -> Tuple[DimensionalStandards, float]:
        """
        Parse dimensional standards from text.
        Returns (standards, confidence_score)
        """
        standards = DimensionalStandards()
        fields_found = 0
        total_fields = 10
        
        # Extract basic dimensions
        standards.min_lot_size_sqft = self._extract_value(text, self.LOT_SIZE_PATTERNS)
        if standards.min_lot_size_sqft:
            fields_found += 1
            
        standards.min_lot_width_ft = self._extract_value(text, self.LOT_WIDTH_PATTERNS)
        if standards.min_lot_width_ft:
            fields_found += 1
            
        standards.max_height_ft = self._extract_value(text, self.HEIGHT_PATTERNS)
        if standards.max_height_ft:
            fields_found += 1
            
        standards.min_living_area_sqft = self._extract_value(text, self.LIVING_AREA_PATTERNS)
        if standards.min_living_area_sqft:
            fields_found += 1
            
        standards.max_lot_coverage_pct = self._extract_value(text, self.COVERAGE_PATTERNS)
        if standards.max_lot_coverage_pct:
            fields_found += 1
            
        standards.density_units_per_acre = self._extract_value(text, self.DENSITY_PATTERNS)
        if standards.density_units_per_acre:
            fields_found += 1
        
        # Extract setbacks
        standards.front_setback = self._extract_setback(text, "front", self.FRONT_SETBACK_PATTERNS)
        if standards.front_setback.standard_ft:
            fields_found += 1
            
        standards.side_setback = self._extract_setback(text, "side", self.SIDE_SETBACK_PATTERNS)
        if standards.side_setback.standard_ft:
            fields_found += 1
            
        standards.rear_setback = self._extract_setback(text, "rear", self.REAR_SETBACK_PATTERNS)
        if standards.rear_setback.standard_ft:
            fields_found += 1
        
        # Calculate confidence
        confidence = fields_found / total_fields
        
        return standards, confidence


class ZoneWiseExtractor:
    """Main extraction engine"""
    
    def __init__(self, config_path: str, firecrawl_key: str, supabase_url: str = None, supabase_key: str = None):
        self.config = self._load_config(config_path)
        self.firecrawl = FirecrawlClient(firecrawl_key)
        self.jina = JinaClient()
        self.parser = DimensionalParser()
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.results = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load jurisdiction configuration"""
        with open(config_path) as f:
            return json.load(f)
    
    def _build_url(self, jurisdiction: Dict) -> str:
        """Build scrape URL for a jurisdiction"""
        base_url = jurisdiction["base_url"]
        sections = jurisdiction.get("zoning_sections", [])
        
        if sections and "node_id" in sections[0]:
            return f"{base_url}?nodeId={sections[0]['node_id']}"
        return base_url
    
    def _scrape_with_fallback(self, url: str) -> Optional[str]:
        """Try Firecrawl first, fall back to Jina"""
        logger.info(f"Scraping: {url}")
        
        # Try Firecrawl first
        content = self.firecrawl.scrape(url)
        if content and len(content) > 1000:
            logger.info(f"  Firecrawl success: {len(content)} chars")
            return content
        
        # Fall back to Jina
        logger.info("  Firecrawl failed, trying Jina...")
        content = self.jina.scrape(url)
        if content and len(content) > 500:
            logger.info(f"  Jina success: {len(content)} chars")
            return content
        
        logger.warning(f"  Both scrapers failed for {url}")
        return None
    
    def extract_jurisdiction(self, jurisdiction: Dict) -> List[DistrictData]:
        """Extract all districts for a jurisdiction"""
        jurisdiction_name = jurisdiction["name"]
        jurisdiction_id = jurisdiction["id"]
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Extracting: {jurisdiction_name} (ID: {jurisdiction_id})")
        logger.info(f"{'='*60}")
        
        url = self._build_url(jurisdiction)
        content = self._scrape_with_fallback(url)
        
        results = []
        for district_config in jurisdiction.get("districts", []):
            district = DistrictData(
                jurisdiction_id=jurisdiction_id,
                jurisdiction_name=jurisdiction_name,
                code=district_config["code"],
                name=district_config["name"],
                category=district_config["category"],
                source_url=url,
                extraction_date=datetime.now().isoformat()
            )
            
            if content:
                # Try to find section specific to this district
                district_section = self._find_district_section(content, district.code)
                
                if district_section:
                    standards, confidence = self.parser.parse(district_section, district.code)
                    district.dimensional_standards = standards
                    district.extraction_confidence = confidence
                    district.extraction_status = "success" if confidence > 0.3 else "partial"
                    district.raw_text_excerpt = district_section[:500] if district_section else None
                else:
                    # Try parsing from full content
                    standards, confidence = self.parser.parse(content, district.code)
                    district.dimensional_standards = standards
                    district.extraction_confidence = confidence * 0.5  # Lower confidence
                    district.extraction_status = "partial" if confidence > 0.2 else "failed"
            else:
                district.extraction_status = "scrape_failed"
                district.extraction_confidence = 0.0
            
            logger.info(f"  {district.code}: {district.extraction_status} (confidence: {district.extraction_confidence:.2f})")
            results.append(district)
        
        return results
    
    def _find_district_section(self, content: str, district_code: str) -> Optional[str]:
        """Find the section of text relevant to a specific district"""
        # Escape special regex characters in district code
        escaped_code = re.escape(district_code)
        
        # Patterns to find district sections
        patterns = [
            rf'(?:Section|Sec\.?|Article)\s+\d+[^.]*{escaped_code}[^.]*\.([^§]+?)(?=(?:Section|Sec\.?|Article)\s+\d+|$)',
            rf'{escaped_code}\s+(?:district|zone)[^.]*\.([^§]+?)(?={escaped_code}|(?:Section|Sec\.?)|$)',
            rf'(?:^|\n)[\*\-]\s*{escaped_code}[:\s]+([^\n]+(?:\n(?![\*\-])[^\n]+)*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                section = match.group(1) if match.lastindex else match.group(0)
                if len(section) > 100:
                    return section[:3000]  # Limit to reasonable size
        
        return None
    
    def extract_all(self) -> List[DistrictData]:
        """Extract all jurisdictions"""
        all_results = []
        jurisdictions = self.config.get("jurisdictions", [])
        
        logger.info(f"Starting extraction for {len(jurisdictions)} jurisdictions")
        
        for i, jurisdiction in enumerate(jurisdictions):
            try:
                results = self.extract_jurisdiction(jurisdiction)
                all_results.extend(results)
                
                # Rate limiting
                if i < len(jurisdictions) - 1:
                    time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                logger.error(f"Error extracting {jurisdiction['name']}: {e}")
        
        self.results = all_results
        return all_results
    
    def save_results(self, output_path: str):
        """Save results to JSON file"""
        output = {
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "total_jurisdictions": len(set(r.jurisdiction_name for r in self.results)),
                "total_districts": len(self.results),
                "successful_extractions": len([r for r in self.results if r.extraction_status == "success"]),
                "partial_extractions": len([r for r in self.results if r.extraction_status == "partial"]),
                "failed_extractions": len([r for r in self.results if r.extraction_status in ("failed", "scrape_failed")])
            },
            "districts": []
        }
        
        for district in self.results:
            district_dict = {
                "jurisdiction_id": district.jurisdiction_id,
                "jurisdiction_name": district.jurisdiction_name,
                "code": district.code,
                "name": district.name,
                "category": district.category,
                "ordinance_section": district.ordinance_section,
                "source_url": district.source_url,
                "extraction_date": district.extraction_date,
                "extraction_status": district.extraction_status,
                "extraction_confidence": district.extraction_confidence
            }
            
            if district.dimensional_standards:
                ds = district.dimensional_standards
                district_dict["dimensional_standards"] = {
                    "min_lot_size_sqft": ds.min_lot_size_sqft,
                    "min_lot_width_ft": ds.min_lot_width_ft,
                    "min_lot_depth_ft": ds.min_lot_depth_ft,
                    "min_living_area_sqft": ds.min_living_area_sqft,
                    "max_height_ft": ds.max_height_ft,
                    "max_stories": ds.max_stories,
                    "max_lot_coverage_pct": ds.max_lot_coverage_pct,
                    "density_units_per_acre": ds.density_units_per_acre,
                    "parking_spaces_required": ds.parking_spaces_required,
                    "setbacks": {
                        "front": asdict(ds.front_setback) if ds.front_setback else None,
                        "side": asdict(ds.side_setback) if ds.side_setback else None,
                        "rear": asdict(ds.rear_setback) if ds.rear_setback else None
                    }
                }
            
            output["districts"].append(district_dict)
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
    
    def save_to_supabase(self):
        """Save results to Supabase"""
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not configured, skipping database save")
            return
        
        try:
            from supabase import create_client
            
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            for district in self.results:
                record = {
                    "jurisdiction_id": district.jurisdiction_id,
                    "jurisdiction_name": district.jurisdiction_name,
                    "district_code": district.code,
                    "district_name": district.name,
                    "category": district.category,
                    "source_url": district.source_url,
                    "extraction_date": district.extraction_date,
                    "extraction_status": district.extraction_status,
                    "extraction_confidence": district.extraction_confidence
                }
                
                if district.dimensional_standards:
                    ds = district.dimensional_standards
                    record.update({
                        "min_lot_size_sqft": ds.min_lot_size_sqft,
                        "min_lot_width_ft": ds.min_lot_width_ft,
                        "min_living_area_sqft": ds.min_living_area_sqft,
                        "max_height_ft": ds.max_height_ft,
                        "max_lot_coverage_pct": ds.max_lot_coverage_pct,
                        "density_units_per_acre": ds.density_units_per_acre,
                        "front_setback_ft": ds.front_setback.standard_ft if ds.front_setback else None,
                        "side_setback_ft": ds.side_setback.standard_ft if ds.side_setback else None,
                        "rear_setback_ft": ds.rear_setback.standard_ft if ds.rear_setback else None
                    })
                
                # Upsert record
                supabase.table("real_zoning_districts").upsert(
                    record,
                    on_conflict="jurisdiction_id,district_code"
                ).execute()
            
            logger.info(f"Saved {len(self.results)} records to Supabase")
            
        except ImportError:
            logger.error("supabase package not installed")
        except Exception as e:
            logger.error(f"Supabase save failed: {e}")
    
    def close(self):
        """Clean up resources"""
        self.firecrawl.close()
        self.jina.close()


def main():
    """Main entry point"""
    # Load environment variables
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not firecrawl_key:
        logger.error("FIRECRAWL_API_KEY environment variable not set")
        sys.exit(1)
    
    # Determine config path
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / "config" / "brevard_jurisdictions.json"
    
    if not config_path.exists():
        # Try alternate location
        config_path = Path("../config/brevard_jurisdictions.json")
    
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("ZoneWise Real Ordinance Extraction Engine v3.0.0")
    logger.info("=" * 60)
    logger.info(f"Config: {config_path}")
    logger.info(f"Firecrawl key: {firecrawl_key[:10]}...")
    logger.info(f"Supabase: {'configured' if supabase_url else 'not configured'}")
    
    # Run extraction
    extractor = ZoneWiseExtractor(
        config_path=str(config_path),
        firecrawl_key=firecrawl_key,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    try:
        results = extractor.extract_all()
        
        # Save to JSON
        output_path = f"../data/real_districts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("../data", exist_ok=True)
        extractor.save_results(output_path)
        
        # Save to Supabase
        extractor.save_to_supabase()
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("EXTRACTION COMPLETE")
        logger.info("=" * 60)
        
        success = len([r for r in results if r.extraction_status == "success"])
        partial = len([r for r in results if r.extraction_status == "partial"])
        failed = len([r for r in results if r.extraction_status in ("failed", "scrape_failed")])
        
        logger.info(f"Total districts: {len(results)}")
        logger.info(f"  Successful: {success}")
        logger.info(f"  Partial:    {partial}")
        logger.info(f"  Failed:     {failed}")
        logger.info(f"Output: {output_path}")
        
    finally:
        extractor.close()


if __name__ == "__main__":
    main()
