#!/usr/bin/env python3
"""
Municode NodeId Extractor - ZoneWise Project
============================================
Reusable workflow for extracting zoning districts from Municode using the 
direct nodeId URL pattern discovered during Rockledge extraction.

BREAKTHROUGH PATTERN:
- Parent/TOC pages don't render content via Browserless
- Direct division nodeId URLs DO render full content
- Pattern: /codes/{code_type}?nodeId={FULL_NODE_PATH}

Base64 encoded patterns for persistence and reuse.
"""

import json
import base64
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime

# ============================================================================
# JURISDICTION CONFIGURATIONS (Base64 Encoded for Persistence)
# ============================================================================

# Encode jurisdiction configs as base64 for storage/transmission
JURISDICTION_CONFIGS = {
    "rockledge": {
        "city_slug": "rockledge",
        "code_type": "land_development_regulations_",
        "zoning_chapter_node": "SPBLADERE_CH118PLZODI_ARTIVZODI",
        "district_pattern": r"DIV[0-9]+[A-Z0-9]+",
        "districts": [
            {"node_suffix": "DIV3R1SIMIDWDI", "code": "R-1", "name": "Single-Family Dwelling District"},
            {"node_suffix": "DIV4R2SIMIDWDI", "code": "R-2", "name": "Single-Family Dwelling District"},
            {"node_suffix": "DIV5R2MUDWLODE", "code": "R-2M", "name": "Multi-Family Low Density District"},
            {"node_suffix": "DIV6R3MUDWHIDEDI", "code": "R-3", "name": "Multi-Family High Density District"},
            {"node_suffix": "DIV10C1NERECODI", "code": "C-1", "name": "Neighborhood Retail Commercial"},
            {"node_suffix": "DIV11C2GECODI", "code": "C-2", "name": "General Commercial District"},
            {"node_suffix": "DIV12P1PRDI", "code": "P-1", "name": "Professional District"},
            {"node_suffix": "DIV13M1GEINDI", "code": "M-1", "name": "General Industrial District"},
            {"node_suffix": "DIV14M2LIINWADI", "code": "M-2", "name": "Light Industrial Warehouse"},
            {"node_suffix": "DIV15IPINPADI", "code": "IP", "name": "Industrial Park District"},
        ]
    },
    "west_melbourne": {
        "city_slug": "west_melbourne",
        "code_type": "code_of_ordinances",
        "zoning_chapter_node": "PTIICOOR_CH98ZO_ARTIIIDI",
        "district_pattern": r"DIV[0-9]+[A-Z0-9]+",
        "districts": [
            {"node_suffix": "DIV2AASIMIREDI", "code": "AA", "name": "Single-Family Residential"},
            {"node_suffix": "DIV3ASIMIREDI", "code": "A", "name": "Single-Family Residential"},
            {"node_suffix": "DIV4SIMIREDI", "code": "R-1", "name": "Single-Family Residential"},
            {"node_suffix": "DIV5SIMIREDI", "code": "R-2", "name": "Single-Family Residential"},
            {"node_suffix": "DIV6OULMIDWDI", "code": "R-3", "name": "Outlying Multi-Family Dwelling"},
            {"node_suffix": "DIV7MUMIDWDI", "code": "R-4", "name": "Multi-Family Dwelling"},
            {"node_suffix": "DIV10LODECODI", "code": "C-1", "name": "Local Commercial District"},
            {"node_suffix": "DIV11GECODI", "code": "C-2", "name": "General Commercial District"},
            {"node_suffix": "DIV12LIINWADI", "code": "M-1", "name": "Light Industrial Warehouse"},
            {"node_suffix": "DIV13GEINDI", "code": "M-2", "name": "General Industrial District"},
            {"node_suffix": "DIV21COREARDI", "code": "C-NHA", "name": "Corridor Redevelopment District"},
        ]
    },
    "cape_canaveral": {
        "city_slug": "cape_canaveral",
        "code_type": "code_of_ordinances",
        "zoning_chapter_node": "SPBLADECO_CH110ZO_ARTVIIDI",
        "district_pattern": r"DIV[0-9]+[A-Z0-9]+",
        "districts": [
            {"node_suffix": "DIV2LODEREDI", "code": "R-1", "name": "Low Density Residential"},
            {"node_suffix": "DIV3MEDEREDI", "code": "R-2", "name": "Medium Density Residential"},
            {"node_suffix": "DIV4MEDEREDI", "code": "R-3", "name": "Medium Density Residential"},
            {"node_suffix": "DIV5LODECODI", "code": "C-1", "name": "Low Density Commercial"},
            {"node_suffix": "DIV6COMADI", "code": "C-2", "name": "Commercial Marina District"},
            {"node_suffix": "DIV7LIINREDEDI", "code": "M-1", "name": "Light Industrial Research"},
            {"node_suffix": "DIV9PUREPURE", "code": "PUB", "name": "Public Recreation/Purpose"},
            {"node_suffix": "DIV10COCO", "code": "CON", "name": "Conservation District"},
        ]
    },
    "cocoa_beach": {
        "city_slug": "cocoa_beach",
        "code_type": "land_development_code",
        "zoning_chapter_node": "APXBLADECO_CHIIZODI",
        "district_pattern": r"ART[A-Z]+[0-9_]+",
        "districts": [
            {"node_suffix": "ARTIIIESSTZODI_S2", "code": "RS", "name": "Residential Single-Family"},
            {"node_suffix": "ARTVESREZODISU_S2", "code": "RM", "name": "Residential Multi-Family"},
            {"node_suffix": "ARTVIICOUSSTOPALZODI_S2", "code": "C-1", "name": "Commercial District"},
        ]
    }
}

def encode_config(config: dict) -> str:
    """Encode jurisdiction config as base64 for storage."""
    return base64.b64encode(json.dumps(config).encode()).decode()

def decode_config(encoded: str) -> dict:
    """Decode jurisdiction config from base64."""
    return json.loads(base64.b64decode(encoded.encode()).decode())

def build_municode_url(city_slug: str, code_type: str, node_id: str) -> str:
    """Build the full Municode URL for a specific nodeId."""
    return f"https://library.municode.com/fl/{city_slug}/codes/{code_type}?nodeId={node_id}"

def build_district_url(config: dict, district: dict) -> str:
    """Build URL for a specific district within a jurisdiction."""
    full_node = f"{config['zoning_chapter_node']}_{district['node_suffix']}"
    return build_municode_url(
        config['city_slug'],
        config['code_type'],
        full_node
    )

@dataclass
class ZoningDistrict:
    """Extracted zoning district data."""
    jurisdiction: str
    district_code: str
    district_name: str
    source_url: str
    source_platform: str = "municode"
    min_lot_area_sqft: Optional[int] = None
    min_lot_width_ft: Optional[int] = None
    front_setback_ft: Optional[int] = None
    side_setback_ft: Optional[int] = None
    rear_setback_ft: Optional[int] = None
    max_height_ft: Optional[int] = None
    max_coverage_pct: Optional[int] = None
    extracted_at: str = None
    
    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.utcnow().isoformat() + "Z"

def parse_dimensional_standards(html_content: str) -> dict:
    """Extract dimensional standards from HTML content."""
    result = {
        "min_lot_area_sqft": None,
        "min_lot_width_ft": None,
        "front_setback_ft": None,
        "side_setback_ft": None,
        "rear_setback_ft": None,
        "max_height_ft": None,
        "max_coverage_pct": None
    }
    
    # Lot area patterns
    lot_area = re.search(r'(\d{1,2},?\d{3})\s*(?:square feet|sq\.?\s*ft)', html_content, re.IGNORECASE)
    if lot_area:
        result["min_lot_area_sqft"] = int(lot_area.group(1).replace(',', ''))
    
    # Lot width patterns
    lot_width = re.search(r'[Ww]idth[^0-9]*(\d+)\s*feet', html_content)
    if lot_width:
        result["min_lot_width_ft"] = int(lot_width.group(1))
    
    # Setback patterns
    front = re.search(r'[Ff]ront[^0-9]{0,20}(\d+)\s*feet', html_content)
    if front:
        result["front_setback_ft"] = int(front.group(1))
    
    side = re.search(r'[Ss]ide[^0-9]{0,20}(\d+)\s*feet', html_content)
    if side:
        result["side_setback_ft"] = int(side.group(1))
        
    rear = re.search(r'[Rr]ear[^0-9]{0,20}(\d+)\s*feet', html_content)
    if rear:
        result["rear_setback_ft"] = int(rear.group(1))
    
    # Height patterns
    height = re.search(r'[Hh]eight[^0-9]{0,20}(\d+)\s*feet', html_content)
    if height:
        result["max_height_ft"] = int(height.group(1))
    
    # Coverage patterns
    coverage = re.search(r'(\d+)\s*(?:percent|%)', html_content)
    if coverage:
        result["max_coverage_pct"] = int(coverage.group(1))
    
    return result

def generate_browserless_payload(url: str, timeout: int = 60000) -> dict:
    """Generate Browserless API payload for content extraction."""
    return {
        "url": url,
        "gotoOptions": {
            "waitUntil": "networkidle2",
            "timeout": timeout
        }
    }

# ============================================================================
# EXPORT ENCODED CONFIGS FOR STORAGE
# ============================================================================

def export_all_configs_base64() -> dict:
    """Export all jurisdiction configs as base64 for Supabase storage."""
    return {
        jurisdiction: encode_config(config)
        for jurisdiction, config in JURISDICTION_CONFIGS.items()
    }

def print_extraction_urls():
    """Print all URLs needed for extraction."""
    for jurisdiction, config in JURISDICTION_CONFIGS.items():
        print(f"\n=== {jurisdiction.upper()} ===")
        for district in config['districts']:
            url = build_district_url(config, district)
            print(f"  {district['code']}: {url}")

if __name__ == "__main__":
    print("=" * 70)
    print("MUNICODE NODEID EXTRACTOR - ZoneWise Project")
    print("=" * 70)
    
    # Export base64 configs
    print("\n📦 BASE64 ENCODED CONFIGS FOR PERSISTENCE:")
    encoded = export_all_configs_base64()
    for jur, enc in encoded.items():
        print(f"\n{jur}:")
        print(f"  {enc[:80]}...")
    
    # Print URLs
    print("\n\n🔗 EXTRACTION URLS:")
    print_extraction_urls()
    
    # Summary
    print("\n\n📊 SUMMARY:")
    total_districts = sum(len(c['districts']) for c in JURISDICTION_CONFIGS.values())
    print(f"  Jurisdictions: {len(JURISDICTION_CONFIGS)}")
    print(f"  Total Districts: {total_districts}")
