#!/usr/bin/env python3
"""
Merge extracted real ordinance data into complete_districts.json
Replaces template values with actual scraped values where available

Author: Claude AI Architect
Date: 2026-01-18
"""

import json
import os
from datetime import datetime
from pathlib import Path


def load_json(path: str) -> dict:
    """Load JSON file"""
    with open(path) as f:
        return json.load(f)


def save_json(data: dict, path: str):
    """Save JSON file with pretty formatting"""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def merge_district_data(template: dict, real: dict) -> dict:
    """Merge real extracted data into template, preserving non-null real values"""
    merged = template.copy()
    
    # Direct field mappings
    field_mappings = {
        'min_lot_size_sqft': 'min_lot_size_sqft',
        'min_lot_width_ft': 'min_lot_width_ft',
        'max_height_ft': 'max_height_ft',
        'max_lot_coverage_pct': 'max_lot_coverage_pct',
        'min_living_area_sqft': 'min_living_area_sqft',
        'density_units_per_acre': 'density_units_per_acre',
        'parking_spaces_required': 'parking_spaces_required',
    }
    
    # Get dimensional standards from real data
    real_standards = real.get('dimensional_standards', {})
    
    for template_field, real_field in field_mappings.items():
        real_value = real_standards.get(real_field)
        if real_value is not None:
            merged[template_field] = real_value
    
    # Handle setbacks
    setbacks = real_standards.get('setbacks', {})
    if setbacks:
        front = setbacks.get('front', {})
        if front and front.get('standard_ft'):
            merged['front_setback_ft'] = front['standard_ft']
        
        side = setbacks.get('side', {})
        if side and side.get('standard_ft'):
            merged['side_setback_ft'] = side['standard_ft']
        
        rear = setbacks.get('rear', {})
        if rear and rear.get('standard_ft'):
            merged['rear_setback_ft'] = rear['standard_ft']
    
    # Add extraction metadata
    merged['extraction_status'] = real.get('extraction_status', 'unknown')
    merged['extraction_confidence'] = real.get('extraction_confidence', 0.0)
    merged['extraction_date'] = real.get('extraction_date')
    merged['source_url'] = real.get('source_url')
    
    return merged


def main():
    """Main merge workflow"""
    print("=" * 60)
    print("ZoneWise Data Merge Tool")
    print("=" * 60)
    
    # Find files
    data_dir = Path("data")
    
    # Find latest extraction file
    extraction_files = list(data_dir.glob("real_districts_*.json"))
    if not extraction_files:
        print("No extraction files found in data/")
        return
    
    latest_extraction = max(extraction_files, key=lambda p: p.stat().st_mtime)
    print(f"Latest extraction: {latest_extraction}")
    
    # Load complete_districts.json (template data)
    template_path = data_dir / "complete_districts.json"
    if not template_path.exists():
        print(f"Template file not found: {template_path}")
        return
    
    template_data = load_json(template_path)
    extraction_data = load_json(latest_extraction)
    
    print(f"Template districts: {len(template_data.get('districts', []))}")
    print(f"Extracted districts: {len(extraction_data.get('districts', []))}")
    
    # Build lookup for extracted data
    extracted_lookup = {}
    for district in extraction_data.get('districts', []):
        key = (district['jurisdiction_name'], district['code'])
        extracted_lookup[key] = district
    
    # Merge data
    merged_count = 0
    updated_districts = []
    
    for template_district in template_data.get('districts', []):
        key = (template_district['jurisdiction_name'], template_district['code'])
        
        if key in extracted_lookup:
            real_district = extracted_lookup[key]
            
            # Only merge if extraction was at least partial
            if real_district.get('extraction_status') in ('success', 'partial'):
                merged = merge_district_data(template_district, real_district)
                updated_districts.append(merged)
                merged_count += 1
                print(f"  ✓ Merged: {key[0]} - {key[1]}")
            else:
                updated_districts.append(template_district)
        else:
            updated_districts.append(template_district)
    
    # Update metadata
    template_data['districts'] = updated_districts
    template_data['metadata']['last_merge'] = datetime.now().isoformat()
    template_data['metadata']['merged_districts'] = merged_count
    template_data['metadata']['data_source'] = 'hybrid_template_and_real'
    
    # Save merged data
    output_path = data_dir / "complete_districts.json"
    save_json(template_data, output_path)
    
    print(f"\n{'=' * 60}")
    print(f"Merge complete!")
    print(f"  Districts merged with real data: {merged_count}")
    print(f"  Output: {output_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
