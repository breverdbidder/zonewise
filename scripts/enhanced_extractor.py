#!/usr/bin/env python3
"""
Enhanced ZoneWise Extractor - Fixed Setback Parsing
====================================================
Properly parses Melbourne's Table 2A tab-separated format
"""

import subprocess
import re
import json
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class ZoningDistrict:
    """Represents a zoning district with dimensional standards"""
    jurisdiction: str
    district_code: str
    district_name: str
    district_type: str
    source_url: str
    source_section: str
    source_platform: str
    last_extracted: str
    content_hash: str
    
    # Lot requirements
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
    
    verified: bool = False
    notes: Optional[str] = None


def fetch_via_jina(url: str) -> str:
    """Fetch URL through Jina Reader"""
    jina_url = f"https://r.jina.ai/{url}"
    result = subprocess.run(
        ["curl", "-s", jina_url],
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.stdout


def parse_table_value(value: str) -> Optional[int]:
    """Parse a table cell value, handling special cases"""
    if not value or value.strip() == '' or value.strip().lower() == 'none':
        return None
    
    clean = value.strip()
    
    # Handle acre values (convert to sqft)
    acre_match = re.match(r'([\d.]+)\s*acre', clean, re.I)
    if acre_match:
        acres = float(acre_match.group(1))
        return int(acres * 43560)
    
    # Handle "X or Y(MF)" format - take first number
    or_match = re.match(r'(\d+)\s*or', clean)
    if or_match:
        return int(or_match.group(1))
    
    # Handle "50/65" format - take first number
    slash_match = re.match(r'(\d+)/', clean)
    if slash_match:
        return int(slash_match.group(1))
    
    # Handle footnote markers (e.g., "5 12" where 12 is footnote)
    footnote_match = re.match(r'([\d.]+)\s+\d+$', clean)
    if footnote_match:
        try:
            return int(float(footnote_match.group(1)))
        except:
            pass
    
    # Parse standard numeric value with commas
    num_match = re.search(r'^([\d,]+)', clean)
    if num_match:
        try:
            return int(num_match.group(1).replace(',', ''))
        except:
            pass
    
    # Try float conversion for values like "7.5"
    try:
        return int(float(clean))
    except:
        pass
    
    return None


def parse_float_value(value: str) -> Optional[float]:
    """Parse a float table cell value"""
    if not value or value.strip() == '':
        return None
    
    match = re.search(r'([\d.]+)', value.strip())
    if match:
        return float(match.group(1))
    return None


def extract_melbourne_districts(content: str) -> List[ZoningDistrict]:
    """Extract Melbourne residential districts from Table 2A"""
    results = []
    
    # Define district columns (0-indexed)
    districts = ['AEU', 'REU', 'R-A', 'R-1AAA', 'R-1AA', 'R-1A', 'R-1B', 'R-2', 'R-3', 'R-4']
    
    # Extract data rows
    data = {
        'min_lot_area': {},
        'min_lot_width': {},
        'min_lot_depth': {},
        'max_lot_coverage': {},
        'max_height': {},
        'front_setback': {},
        'side_interior': {},
        'side_corner': {},
        'rear': {},
        'rear_alley': {},
        'water_setback': {},
    }
    
    # Parse lot area row - look for the specific pattern after header
    lot_area_match = re.search(r'Minimum lot area[^\n]*\nSingle-family\t([^\n]+)', content)
    if lot_area_match:
        values = lot_area_match.group(1).split('\t')
        print(f"  LOT AREA values found: {values[:10]}")
        for idx, val in enumerate(values[:len(districts)]):
            data['min_lot_area'][idx] = parse_table_value(val)
    
    # Parse lot width row
    width_match = re.search(r'Minimum lot width[^\n]*\nSingle-family\t([^\n]+)', content)
    if width_match:
        values = width_match.group(1).split('\t')
        print(f"  LOT WIDTH values found: {values[:10]}")
        for idx, val in enumerate(values[:len(districts)]):
            data['min_lot_width'][idx] = parse_table_value(val)
    
    # Parse lot depth row
    depth_match = re.search(r'Minimum lot depth[^\n]*\nSingle-family\t([^\n]+)', content)
    if depth_match:
        values = depth_match.group(1).split('\t')
        print(f"  LOT DEPTH values found: {values[:10]}")
        for idx, val in enumerate(values[:len(districts)]):
            data['min_lot_depth'][idx] = parse_table_value(val)
    
    # Parse lot coverage row
    coverage_match = re.search(r'Maximum lot coverage[^\n]*\nSingle-family\t([^\n]+)', content, re.I)
    if coverage_match:
        values = coverage_match.group(1).split('\t')
        print(f"  COVERAGE values found: {values[:10]}")
        for idx, val in enumerate(values[:len(districts)]):
            data['max_lot_coverage'][idx] = parse_float_value(val)
    
    # Parse height - Melbourne uses text description, extract number
    height_match = re.search(r'Single-, two-, and three-family\t([^\n]+)', content)
    if height_match:
        height_text = height_match.group(1)
        height_num = re.search(r'(\d+)\s*feet', height_text)
        if height_num:
            height_val = int(height_num.group(1))
            for idx in range(len(districts)):
                data['max_height'][idx] = height_val
            print(f"  HEIGHT: {height_val} ft for all residential districts")
    
    # Parse setback rows
    front_match = re.search(r'^Front\t([^\n]+)', content, re.M)
    if front_match:
        values = front_match.group(1).split('\t')
        print(f"  FRONT SETBACK values found: {values[:10]}")
        for idx, val in enumerate(values[:len(districts)]):
            data['front_setback'][idx] = parse_table_value(val)
    
    side_int_match = re.search(r'^Side interior[^\t]*\t([^\n]+)', content, re.M | re.I)
    if side_int_match:
        values = side_int_match.group(1).split('\t')
        print(f"  SIDE INT values found: {values[:10]}")
        for idx, val in enumerate(values[:len(districts)]):
            data['side_interior'][idx] = parse_table_value(val)
    
    side_corner_match = re.search(r'^Side corner lot\t([^\n]+)', content, re.M | re.I)
    if side_corner_match:
        values = side_corner_match.group(1).split('\t')
        print(f"  SIDE CORNER values found: {values[:10]}")
        for idx, val in enumerate(values[:len(districts)]):
            data['side_corner'][idx] = parse_table_value(val)
    
    rear_match = re.search(r'^Rear—permitted\t([^\n]+)', content, re.M)
    if rear_match:
        values = rear_match.group(1).split('\t')
        print(f"  REAR values found: {values[:10]}")
        for idx, val in enumerate(values[:len(districts)]):
            data['rear'][idx] = parse_table_value(val)
    
    rear_alley_match = re.search(r'^Rear—abutting alley\t([^\n]+)', content, re.M)
    if rear_alley_match:
        values = rear_alley_match.group(1).split('\t')
        for idx, val in enumerate(values[:len(districts)]):
            data['rear_alley'][idx] = parse_table_value(val)
    
    water_match = re.search(r'^Minimum setback from water[^\t]*\t([^\n]+)', content, re.M | re.I)
    if water_match:
        values = water_match.group(1).split('\t')
        print(f"  WATER SETBACK values found: {values[:10]}")
        for idx, val in enumerate(values[:len(districts)]):
            data['water_setback'][idx] = parse_table_value(val)
    
    # Create district objects
    url = "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVDIRE_S2DIUSDIST"
    content_hash = str(hash(content[:1000]))[:16]
    
    for idx, code in enumerate(districts):
        district = ZoningDistrict(
            jurisdiction="Melbourne",
            district_code=code,
            district_name=f"{code} Residential District",
            district_type="residential",
            source_url=url,
            source_section="Table 2A",
            source_platform="municode",
            last_extracted=datetime.now().isoformat(),
            content_hash=content_hash,
            min_lot_area_sqft=data['min_lot_area'].get(idx),
            min_lot_width_ft=data['min_lot_width'].get(idx),
            min_lot_depth_ft=data['min_lot_depth'].get(idx),
            max_lot_coverage_pct=data['max_lot_coverage'].get(idx),
            max_height_ft=data['max_height'].get(idx),
            front_setback_ft=data['front_setback'].get(idx),
            side_interior_setback_ft=data['side_interior'].get(idx),
            side_corner_setback_ft=data['side_corner'].get(idx),
            rear_setback_ft=data['rear'].get(idx),
            rear_alley_setback_ft=data['rear_alley'].get(idx),
            water_setback_ft=data['water_setback'].get(idx),
        )
        results.append(district)
        print(f"  {code}: Lot={district.min_lot_area_sqft}, Width={district.min_lot_width_ft}, "
              f"Height={district.max_height_ft}, Front={district.front_setback_ft}, "
              f"Side={district.side_interior_setback_ft}, Rear={district.rear_setback_ft}")
    
    return results


def main():
    print("=" * 60)
    print("Enhanced Melbourne Zoning Extraction")
    print("=" * 60)
    print()
    
    # Read cached content
    with open('/tmp/melbourne_zoning.txt', 'r') as f:
        content = f.read()
    
    print(f"Content length: {len(content)} chars")
    print()
    print("Extracting districts from Table 2A...")
    print()
    
    districts = extract_melbourne_districts(content)
    
    print()
    print(f"Total districts extracted: {len(districts)}")
    
    # Export to JSON
    output = {"melbourne": [asdict(d) for d in districts]}
    
    with open('/tmp/melbourne_enhanced.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nExported to /tmp/melbourne_enhanced.json")
    
    # Show sample district
    print("\n=== SAMPLE: R-1AA ===")
    for d in districts:
        if d.district_code == 'R-1AA':
            print(f"District: {d.district_code} - {d.district_name}")
            print(f"  Min Lot Area: {d.min_lot_area_sqft} sqft")
            print(f"  Min Lot Width: {d.min_lot_width_ft} ft")
            print(f"  Min Lot Depth: {d.min_lot_depth_ft} ft")
            print(f"  Max Height: {d.max_height_ft} ft")
            print(f"  Front Setback: {d.front_setback_ft} ft")
            print(f"  Side Interior: {d.side_interior_setback_ft} ft")
            print(f"  Side Corner: {d.side_corner_setback_ft} ft")
            print(f"  Rear: {d.rear_setback_ft} ft")
            print(f"  Water: {d.water_setback_ft} ft")
            break


if __name__ == "__main__":
    main()
