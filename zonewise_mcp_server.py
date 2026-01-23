#!/usr/bin/env python3
"""
ZoneWise MCP Server - Municipal Code Extraction
===============================================

Model Context Protocol server for continuous extraction of zoning dimensional 
standards from Municode, eLaws, and American Legal Publishing.

Uses Jina AI Reader for JavaScript rendering (FREE, no API key needed).

Part of the ZoneWise / BidDeed.AI ecosystem.
"""

import os
import httpx
import re
import json
import asyncio
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging
from hashlib import md5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
JINA_READER_BASE = "https://r.jina.ai/"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
REQUEST_TIMEOUT = 90

# Brevard County Jurisdictions and their code publishing platforms
BREVARD_JURISDICTIONS = {
    # Municode jurisdictions
    "melbourne": {
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/melbourne",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": "PTIIILADERE_APXBZO_ARTVDIRE_S2DIUSDIST",
    },
    "cocoa": {
        "platform": "municode", 
        "base_url": "https://library.municode.com/fl/cocoa",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": None,  # To be discovered
    },
    "titusville": {
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/titusville",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": None,
    },
    "rockledge": {
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/rockledge",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": None,
    },
    "palm_bay": {
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/palm_bay",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": None,
    },
    "west_melbourne": {
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/west_melbourne",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": None,
    },
    "brevard_county": {
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/brevard_county",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": None,
    },
    "indian_harbour_beach": {
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/indian_harbour_beach",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": None,
    },
    "cape_canaveral": {
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/cape_canaveral",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": None,
    },
    "cocoa_beach": {
        "platform": "municode",
        "base_url": "https://library.municode.com/fl/cocoa_beach",
        "code_path": "/codes/code_of_ordinances",
        "zoning_node": None,
    },
    # eLaws jurisdictions
    "satellite_beach": {
        "platform": "elaws",
        "base_url": "https://satellitebeach.elaws.us",
        "code_path": "/code/ordinances_ch30_artiv",
        "zoning_node": None,
    },
    "indialantic": {
        "platform": "elaws",
        "base_url": "https://indialantic.elaws.us",
        "code_path": "/code",
        "zoning_node": None,
    },
    "melbourne_beach": {
        "platform": "elaws",
        "base_url": "https://melbournebeach.elaws.us",
        "code_path": "/code",
        "zoning_node": None,
    },
    "malabar": {
        "platform": "elaws",
        "base_url": "https://malabar.elaws.us",
        "code_path": "/code",
        "zoning_node": None,
    },
}


@dataclass
class ZoningDistrict:
    """Represents a zoning district with dimensional standards"""
    jurisdiction: str
    district_code: str
    district_name: str
    district_type: str  # residential, commercial, industrial, mixed
    
    # Source info
    source_url: str
    source_section: str
    source_platform: str
    last_extracted: str
    content_hash: str  # For change detection
    
    # Dimensional Standards - Residential
    min_lot_area_sqft: Optional[int] = None
    min_lot_width_ft: Optional[int] = None
    min_lot_depth_ft: Optional[int] = None
    max_lot_coverage_pct: Optional[float] = None
    min_living_area_sqft: Optional[int] = None
    max_height_ft: Optional[int] = None
    max_stories: Optional[int] = None
    
    # Setbacks
    front_setback_ft: Optional[int] = None
    side_interior_setback_ft: Optional[int] = None
    side_corner_setback_ft: Optional[int] = None
    rear_setback_ft: Optional[int] = None
    rear_alley_setback_ft: Optional[int] = None
    water_setback_ft: Optional[int] = None
    
    # Additional
    max_density_units_acre: Optional[float] = None
    floor_area_ratio: Optional[float] = None
    parking_spaces_per_unit: Optional[float] = None
    open_space_pct: Optional[float] = None
    
    # Metadata
    verified: bool = False
    verification_date: Optional[str] = None
    notes: Optional[str] = None
    raw_text: Optional[str] = None


class JinaReader:
    """Wrapper for Jina AI Reader to fetch JS-rendered pages"""
    
    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
                "Accept": "text/plain",
            },
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True
        )
    
    def fetch(self, url: str) -> str:
        """Fetch a URL through Jina Reader for JS rendering"""
        jina_url = f"{JINA_READER_BASE}{url}"
        resp = self.client.get(jina_url)
        resp.raise_for_status()
        return resp.text
    
    def close(self):
        self.client.close()


class MunicodeExtractor:
    """Extract zoning data from Municode-hosted municipal codes"""
    
    def __init__(self, reader: JinaReader):
        self.reader = reader
    
    def discover_zoning_node(self, jurisdiction: str, config: dict) -> Optional[str]:
        """Discover the zoning section nodeId for a jurisdiction"""
        base_url = config["base_url"]
        code_path = config["code_path"]
        
        logger.info(f"Discovering zoning node for {jurisdiction}...")
        
        try:
            content = self.reader.fetch(f"{base_url}{code_path}")
            
            # Look for zoning-related nodeIds
            patterns = [
                r'nodeId=(PTIIILADERE_APXBZO[A-Z0-9_]*)',  # Melbourne-style
                r'nodeId=([A-Z0-9_]*ZO[A-Z0-9_]*DIST[A-Z0-9_]*)',  # Zoning district
                r'nodeId=([A-Z0-9_]*LANDDEV[A-Z0-9_]*)',  # Land development
                r'nodeId=([A-Z0-9_]*CH\d+[A-Z0-9_]*ZO[A-Z0-9_]*)',  # Chapter zoning
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    logger.info(f"  Found potential zoning nodes: {matches[:5]}")
                    # Return the first match that looks like district standards
                    for node in matches:
                        if 'DIST' in node or 'STANDARD' in node or 'DIMEN' in node:
                            return node
                    return matches[0]
            
            logger.warning(f"  No zoning node found for {jurisdiction}")
            return None
            
        except Exception as e:
            logger.error(f"Error discovering zoning node: {e}")
            return None
    
    def extract_dimensional_tables(self, jurisdiction: str, config: dict) -> List[ZoningDistrict]:
        """Extract dimensional standards from a Municode jurisdiction"""
        results = []
        
        zoning_node = config.get("zoning_node")
        if not zoning_node:
            zoning_node = self.discover_zoning_node(jurisdiction, config)
            if not zoning_node:
                return results
        
        base_url = config["base_url"]
        code_path = config["code_path"]
        url = f"{base_url}{code_path}?nodeId={zoning_node}"
        
        logger.info(f"Fetching dimensional tables from {url}")
        
        try:
            content = self.reader.fetch(url)
            content_hash = md5(content.encode()).hexdigest()[:16]
            
            # Parse residential districts table
            residential = self._parse_residential_table(content, jurisdiction, url, content_hash, config)
            results.extend(residential)
            
            # Parse nonresidential districts table
            nonresidential = self._parse_nonresidential_table(content, jurisdiction, url, content_hash, config)
            results.extend(nonresidential)
            
            logger.info(f"Extracted {len(results)} districts from {jurisdiction}")
            
        except Exception as e:
            logger.error(f"Error extracting from {jurisdiction}: {e}")
        
        return results
    
    def _parse_residential_table(self, content: str, jurisdiction: str, 
                                  url: str, content_hash: str, config: dict) -> List[ZoningDistrict]:
        """Parse Table 2A - Residential Districts"""
        results = []
        
        # Find the residential table section
        table_match = re.search(
            r'Table 2A[.\s]*Table of Dimensional Standards[,\s]*Residential[^\n]*\n(.*?)(?:Table 2B|EXPAND|$)',
            content, re.DOTALL | re.I
        )
        
        if not table_match:
            # Try alternative pattern
            table_match = re.search(
                r'Residential\s+1?\s*\t([A-Z0-9\-\t\s]+)\nMinimum lot area',
                content, re.I
            )
        
        if not table_match:
            logger.warning(f"Could not find residential table for {jurisdiction}")
            return results
        
        table_content = table_match.group(1) if table_match else ""
        
        # Extract district headers
        header_match = re.search(
            r'Residential\s+1?\s*\t([^\n]+)',
            content, re.I
        )
        
        if header_match:
            districts = header_match.group(1).split('\t')
            districts = [d.strip() for d in districts if d.strip() and d.strip() not in ['', '1']]
            logger.info(f"Found residential districts: {districts}")
            
            # For each district, create an entry
            for idx, district_code in enumerate(districts):
                if not district_code or district_code.isdigit():
                    continue
                
                district = ZoningDistrict(
                    jurisdiction=jurisdiction.replace('_', ' ').title(),
                    district_code=district_code,
                    district_name=f"{district_code} Residential District",
                    district_type="residential",
                    source_url=url,
                    source_section="Table 2A",
                    source_platform=config["platform"],
                    last_extracted=datetime.now().isoformat(),
                    content_hash=content_hash,
                )
                
                # Extract values for this district
                district.min_lot_area_sqft = self._extract_table_value(
                    content, "Minimum lot area", "Single-family", idx
                )
                district.min_lot_width_ft = self._extract_table_value(
                    content, "Minimum lot width", "Single-family", idx
                )
                district.min_lot_depth_ft = self._extract_table_value(
                    content, "Minimum lot depth", "Single-family", idx
                )
                district.max_lot_coverage_pct = self._extract_table_value(
                    content, "Maximum lot coverage", "Single-family", idx
                )
                district.min_living_area_sqft = self._extract_table_value(
                    content, "Minimum living area", "Single-family", idx
                )
                district.max_height_ft = self._extract_height(content, idx)
                
                # Setbacks
                district.front_setback_ft = self._extract_setback(content, "Front", idx)
                district.side_interior_setback_ft = self._extract_setback(content, "Side interior", idx)
                district.side_corner_setback_ft = self._extract_setback(content, "Side corner", idx)
                district.rear_setback_ft = self._extract_setback(content, "Rear—permitted", idx)
                district.rear_alley_setback_ft = self._extract_setback(content, "Rear—abutting alley", idx)
                district.water_setback_ft = self._extract_setback(content, "setback from water", idx)
                
                results.append(district)
        
        return results
    
    def _parse_nonresidential_table(self, content: str, jurisdiction: str,
                                     url: str, content_hash: str, config: dict) -> List[ZoningDistrict]:
        """Parse Table 2B - Nonresidential Districts"""
        results = []
        
        # Find the nonresidential table section
        table_match = re.search(
            r'Table 2B[.\s]*Table of Dimensional Standards[,\s]*Nonresidential[^\n]*\n(.*?)(?:Table 2C|NOTE:|$)',
            content, re.DOTALL | re.I
        )
        
        if not table_match:
            return results
        
        # Extract district headers from nonresidential section
        header_match = re.search(
            r'\tR-P\t([^\n]+)',
            content, re.I
        )
        
        if header_match:
            raw_districts = "R-P\t" + header_match.group(1)
            districts = raw_districts.split('\t')
            districts = [d.strip() for d in districts if d.strip()]
            logger.info(f"Found nonresidential districts: {districts}")
            
            for idx, district_code in enumerate(districts):
                if not district_code:
                    continue
                
                # Determine district type
                if district_code.startswith('M-'):
                    district_type = "industrial"
                elif district_code.startswith('C-'):
                    district_type = "commercial"
                elif district_code.startswith('I-'):
                    district_type = "institutional"
                else:
                    district_type = "mixed"
                
                district = ZoningDistrict(
                    jurisdiction=jurisdiction.replace('_', ' ').title(),
                    district_code=district_code,
                    district_name=f"{district_code} District",
                    district_type=district_type,
                    source_url=url,
                    source_section="Table 2B",
                    source_platform=config["platform"],
                    last_extracted=datetime.now().isoformat(),
                    content_hash=content_hash,
                )
                
                results.append(district)
        
        return results
    
    def _extract_table_value(self, content: str, row_name: str, 
                             sub_row: str, col_idx: int) -> Optional[int]:
        """Extract a numeric value from a dimensional table"""
        # Build pattern to find the row
        pattern = rf'{row_name}[^\n]*\n{sub_row}\t([^\n]+)'
        match = re.search(pattern, content, re.I)
        
        if match:
            values = match.group(1).split('\t')
            if col_idx < len(values):
                value = values[col_idx].strip()
                # Parse the value
                num_match = re.search(r'([\d,]+)', value)
                if num_match:
                    return int(num_match.group(1).replace(',', ''))
        return None
    
    def _extract_height(self, content: str, col_idx: int) -> Optional[int]:
        """Extract maximum height value"""
        # Height is often formatted as "X floors with a maximum height of Y feet"
        height_match = re.search(r'maximum height of (\d+) feet', content, re.I)
        if height_match:
            return int(height_match.group(1))
        return None
    
    def _extract_setback(self, content: str, setback_type: str, col_idx: int) -> Optional[int]:
        """Extract setback value from dimensional table"""
        pattern = rf'{setback_type}[^\n]*\t([^\n]+)'
        match = re.search(pattern, content, re.I)
        
        if match:
            values = match.group(1).split('\t')
            if col_idx < len(values):
                value = values[col_idx].strip()
                # Handle formats like "20 or 30(MF)" - take the first number
                num_match = re.search(r'(\d+)', value)
                if num_match:
                    return int(num_match.group(1))
        return None


class eLawsExtractor:
    """Extract zoning data from eLaws-hosted municipal codes"""
    
    def __init__(self, reader: JinaReader):
        self.reader = reader
    
    def extract_districts(self, jurisdiction: str, config: dict) -> List[ZoningDistrict]:
        """Extract zoning districts from an eLaws jurisdiction"""
        results = []
        
        base_url = config["base_url"]
        code_path = config["code_path"]
        
        logger.info(f"Extracting from eLaws: {jurisdiction}")
        
        try:
            # First get the zoning article page
            content = self.reader.fetch(f"{base_url}{code_path}")
            content_hash = md5(content.encode()).hexdigest()[:16]
            
            # Find district sections
            district_pattern = r'§\s*(\d+-\d+(?:\.\d+)?)\.\s*([A-Z][A-Z0-9-]+),\s*([^.]+)'
            matches = re.findall(district_pattern, content, re.I)
            
            for section_num, district_code, district_name in matches:
                district_type = self._determine_district_type(district_code)
                
                district = ZoningDistrict(
                    jurisdiction=jurisdiction.replace('_', ' ').title(),
                    district_code=district_code.upper(),
                    district_name=district_name.strip(),
                    district_type=district_type,
                    source_url=f"{base_url}/code/{section_num}",
                    source_section=f"§{section_num}",
                    source_platform="elaws",
                    last_extracted=datetime.now().isoformat(),
                    content_hash=content_hash,
                )
                
                # Try to extract dimensional standards from the section
                self._extract_elaws_dimensions(district, content)
                results.append(district)
            
            logger.info(f"Extracted {len(results)} districts from {jurisdiction}")
            
        except Exception as e:
            logger.error(f"Error extracting from eLaws {jurisdiction}: {e}")
        
        return results
    
    def _determine_district_type(self, district_code: str) -> str:
        """Determine district type from code"""
        code = district_code.upper()
        if code.startswith('R-') or code.startswith('RS-') or code.startswith('RM-'):
            return "residential"
        elif code.startswith('C-') or code.startswith('CB-'):
            return "commercial"
        elif code.startswith('M-') or code.startswith('LIU') or code.startswith('I-'):
            return "industrial"
        elif code.startswith('ITU') or code.startswith('P-'):
            return "institutional"
        else:
            return "mixed"
    
    def _extract_elaws_dimensions(self, district: ZoningDistrict, content: str):
        """Extract dimensional standards from eLaws content"""
        # Look for common patterns in eLaws format
        patterns = {
            'max_height_ft': r'(?:maximum\s*)?height[:\s]*(\d+)\s*(?:feet|ft)',
            'max_lot_coverage_pct': r'lot\s*coverage[:\s]*(\d+)\s*%?',
            'front_setback_ft': r'front\s*(?:yard\s*)?setback[:\s]*(\d+)',
            'rear_setback_ft': r'rear\s*(?:yard\s*)?setback[:\s]*(\d+)',
            'side_interior_setback_ft': r'side\s*(?:interior\s*)?(?:yard\s*)?setback[:\s]*(\d+)',
        }
        
        for attr, pattern in patterns.items():
            match = re.search(pattern, content, re.I)
            if match:
                try:
                    setattr(district, attr, int(match.group(1)))
                except (ValueError, AttributeError):
                    pass


class ZoneWiseExtractor:
    """Main extractor coordinating all platforms"""
    
    def __init__(self, supabase_key: Optional[str] = None):
        self.reader = JinaReader()
        self.municode = MunicodeExtractor(self.reader)
        self.elaws = eLawsExtractor(self.reader)
        self.supabase_key = supabase_key
    
    def extract_jurisdiction(self, jurisdiction: str) -> List[ZoningDistrict]:
        """Extract all zoning districts from a jurisdiction"""
        config = BREVARD_JURISDICTIONS.get(jurisdiction)
        if not config:
            logger.error(f"Unknown jurisdiction: {jurisdiction}")
            return []
        
        platform = config["platform"]
        
        if platform == "municode":
            return self.municode.extract_dimensional_tables(jurisdiction, config)
        elif platform == "elaws":
            return self.elaws.extract_districts(jurisdiction, config)
        else:
            logger.warning(f"Unsupported platform: {platform}")
            return []
    
    def extract_all(self) -> Dict[str, List[ZoningDistrict]]:
        """Extract zoning data from all Brevard County jurisdictions"""
        results = {}
        
        for jurisdiction in BREVARD_JURISDICTIONS.keys():
            logger.info(f"Processing {jurisdiction}...")
            try:
                districts = self.extract_jurisdiction(jurisdiction)
                results[jurisdiction] = districts
            except Exception as e:
                logger.error(f"Error processing {jurisdiction}: {e}")
                results[jurisdiction] = []
        
        return results
    
    def detect_changes(self, jurisdiction: str, previous_hash: str) -> bool:
        """Check if a jurisdiction's zoning code has changed"""
        config = BREVARD_JURISDICTIONS.get(jurisdiction)
        if not config:
            return False
        
        try:
            url = f"{config['base_url']}{config['code_path']}"
            if config.get('zoning_node'):
                url += f"?nodeId={config['zoning_node']}"
            
            content = self.reader.fetch(url)
            current_hash = md5(content.encode()).hexdigest()[:16]
            
            return current_hash != previous_hash
            
        except Exception as e:
            logger.error(f"Error checking changes for {jurisdiction}: {e}")
            return False
    
    def export_json(self, results: Dict[str, List[ZoningDistrict]], filepath: str):
        """Export results to JSON file"""
        output = {}
        for jurisdiction, districts in results.items():
            output[jurisdiction] = [asdict(d) for d in districts]
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        logger.info(f"Exported to {filepath}")
    
    def close(self):
        self.reader.close()


# MCP Server Implementation
class ZoneWiseMCPServer:
    """Model Context Protocol server for ZoneWise extraction"""
    
    def __init__(self):
        self.extractor = ZoneWiseExtractor()
    
    def get_tools(self) -> List[Dict]:
        """Return available MCP tools"""
        return [
            {
                "name": "extract_jurisdiction",
                "description": "Extract zoning dimensional standards from a Brevard County jurisdiction",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jurisdiction": {
                            "type": "string",
                            "description": "Jurisdiction name (e.g., 'melbourne', 'satellite_beach')",
                            "enum": list(BREVARD_JURISDICTIONS.keys())
                        }
                    },
                    "required": ["jurisdiction"]
                }
            },
            {
                "name": "extract_all_jurisdictions",
                "description": "Extract zoning data from all 17 Brevard County jurisdictions",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "check_for_changes",
                "description": "Check if a jurisdiction's zoning code has been updated",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jurisdiction": {"type": "string"},
                        "previous_hash": {"type": "string"}
                    },
                    "required": ["jurisdiction", "previous_hash"]
                }
            },
            {
                "name": "list_jurisdictions",
                "description": "List all available Brevard County jurisdictions",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    
    def call_tool(self, name: str, arguments: Dict) -> Any:
        """Execute an MCP tool"""
        if name == "extract_jurisdiction":
            jurisdiction = arguments.get("jurisdiction")
            districts = self.extractor.extract_jurisdiction(jurisdiction)
            return [asdict(d) for d in districts]
        
        elif name == "extract_all_jurisdictions":
            results = self.extractor.extract_all()
            return {k: [asdict(d) for d in v] for k, v in results.items()}
        
        elif name == "check_for_changes":
            return self.extractor.detect_changes(
                arguments.get("jurisdiction"),
                arguments.get("previous_hash")
            )
        
        elif name == "list_jurisdictions":
            return {
                "jurisdictions": list(BREVARD_JURISDICTIONS.keys()),
                "platforms": {k: v["platform"] for k, v in BREVARD_JURISDICTIONS.items()}
            }
        
        else:
            raise ValueError(f"Unknown tool: {name}")


def main():
    """Main entry point for testing"""
    extractor = ZoneWiseExtractor()
    
    print("\n" + "="*60)
    print("ZoneWise Municipal Code Extractor")
    print("="*60 + "\n")
    
    # Test with Melbourne (Municode)
    print("Testing Melbourne extraction...")
    melbourne_districts = extractor.extract_jurisdiction("melbourne")
    
    print(f"\nExtracted {len(melbourne_districts)} districts from Melbourne:")
    for d in melbourne_districts[:10]:
        print(f"\n  {d.district_code}: {d.district_name[:40]}")
        print(f"    Type: {d.district_type}")
        print(f"    Min Lot Area: {d.min_lot_area_sqft} sqft")
        print(f"    Max Height: {d.max_height_ft} ft")
        print(f"    Front Setback: {d.front_setback_ft} ft")
    
    # Test with Satellite Beach (eLaws)
    print("\n\nTesting Satellite Beach extraction...")
    satellite_districts = extractor.extract_jurisdiction("satellite_beach")
    
    print(f"\nExtracted {len(satellite_districts)} districts from Satellite Beach:")
    for d in satellite_districts[:10]:
        print(f"\n  {d.district_code}: {d.district_name[:40]}")
        print(f"    Type: {d.district_type}")
    
    # Export results
    all_results = {
        "melbourne": melbourne_districts,
        "satellite_beach": satellite_districts,
    }
    extractor.export_json(all_results, "/tmp/zonewise_extraction.json")
    
    extractor.close()
    print("\n\nExtraction complete!")


if __name__ == "__main__":
    main()
