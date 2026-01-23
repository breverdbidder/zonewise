#!/usr/bin/env python3
"""
Census API Integration for ZoneWise - Malabar POC
Calculates centroids from geometry and assigns demographic data from Census ACS

Prerequisites:
1. Run migrations/004_add_demographics.sql in Supabase SQL Editor
2. Ensure sample_properties has geometry data

Usage:
    python census_integration_malabar.py
"""

import json
import time
import urllib.request
import urllib.error
from datetime import datetime

# Configuration
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE"

# Brevard County FIPS
STATE_FIPS = "12"
COUNTY_FIPS = "009"

# Malabar jurisdiction ID
MALABAR_JURISDICTION_ID = 14


def fetch_acs_data():
    """Fetch ACS 5-year data for all Brevard County census tracts."""
    print("Fetching ACS 5-Year data for Brevard County...")
    
    # ACS variables
    variables = "B19013_001E,B01003_001E,B17001_002E,B25077_001E,B25064_001E,B25002_003E,B25002_001E"
    url = f"https://api.census.gov/data/2022/acs/acs5?get=NAME,{variables}&for=tract:*&in=state:{STATE_FIPS}&in=county:{COUNTY_FIPS}"
    
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read().decode())
    
    headers = data[0]
    tracts = {}
    
    for row in data[1:]:
        row_dict = dict(zip(headers, row))
        tract_code = row_dict.get('tract', '')
        geoid = f"{STATE_FIPS}{COUNTY_FIPS}{tract_code}"
        
        total_pop = int(row_dict.get('B01003_001E') or 0)
        poverty = int(row_dict.get('B17001_002E') or 0)
        total_units = int(row_dict.get('B25002_001E') or 0)
        vacant_units = int(row_dict.get('B25002_003E') or 0)
        
        tracts[geoid] = {
            "census_tract": tract_code,
            "median_household_income": int(row_dict.get('B19013_001E') or 0) or None,
            "total_population": total_pop or None,
            "poverty_rate": round(poverty / total_pop * 100, 2) if total_pop > 0 else None,
            "median_home_value": int(row_dict.get('B25077_001E') or 0) or None,
            "median_rent": int(row_dict.get('B25064_001E') or 0) or None,
            "vacancy_rate": round(vacant_units / total_units * 100, 2) if total_units > 0 else None,
        }
    
    print(f"  Retrieved {len(tracts)} census tracts")
    return tracts


def calculate_centroid(geometry):
    """Calculate centroid from polygon geometry."""
    if not geometry or 'rings' not in geometry:
        return None, None
    
    ring = geometry['rings'][0]
    lon = sum(pt[0] for pt in ring) / len(ring)
    lat = sum(pt[1] for pt in ring) / len(ring)
    return lat, lon


def geocode_to_tract(lat, lon, retries=3):
    """Geocode coordinates to census tract."""
    url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x={lon}&y={lat}&benchmark=Public_AR_Current&vintage=Current_Current&layers=10&format=json"
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode())
            
            geographies = data.get('result', {}).get('geographies', {})
            
            # Try Census Tracts first
            tract_list = geographies.get('Census Tracts', [])
            if tract_list:
                return tract_list[0].get('GEOID')
            
            # Fall back to Block Groups
            bg_list = geographies.get('Census Block Groups', [])
            if bg_list:
                return f"{bg_list[0].get('STATE')}{bg_list[0].get('COUNTY')}{bg_list[0].get('TRACT')}"
            
            return None
            
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                return None


def fetch_parcels_batch(offset, limit=100):
    """Fetch batch of Malabar parcels."""
    url = f"{SUPABASE_URL}/rest/v1/sample_properties?jurisdiction_id=eq.{MALABAR_JURISDICTION_ID}&select=id,parcel_id,geometry&order=id"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Range": f"{offset}-{offset + limit - 1}"
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode())


def update_parcel(parcel_id, data):
    """Update parcel with demographic data."""
    url = f"{SUPABASE_URL}/rest/v1/sample_properties?id=eq.{parcel_id}"
    
    data["demographics_updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        method='PATCH'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return True
    except Exception as e:
        print(f"    Error updating parcel {parcel_id}: {e}")
        return False


def main():
    print("=" * 70)
    print("ZoneWise Census Integration - Malabar POC")
    print("=" * 70)
    
    # Step 1: Fetch ACS data
    tract_data = fetch_acs_data()
    
    # Step 2: Process all Malabar parcels
    print(f"\nProcessing Malabar parcels (jurisdiction_id={MALABAR_JURISDICTION_ID})...")
    
    stats = {
        "total": 0,
        "success": 0,
        "no_geometry": 0,
        "no_tract": 0,
        "no_demographics": 0,
        "update_failed": 0
    }
    
    geocode_cache = {}  # Cache: rounded coords -> geoid
    
    offset = 0
    batch_size = 100
    
    while True:
        parcels = fetch_parcels_batch(offset, batch_size)
        
        if not parcels:
            break
        
        stats["total"] += len(parcels)
        
        for parcel in parcels:
            # Calculate centroid
            lat, lon = calculate_centroid(parcel.get('geometry'))
            
            if lat is None:
                stats["no_geometry"] += 1
                continue
            
            # Check cache
            cache_key = f"{round(lat, 4)},{round(lon, 4)}"
            
            if cache_key in geocode_cache:
                geoid = geocode_cache[cache_key]
            else:
                # Geocode to tract
                geoid = geocode_to_tract(lat, lon)
                geocode_cache[cache_key] = geoid
                time.sleep(0.1)  # Rate limit Census API
            
            if not geoid:
                stats["no_tract"] += 1
                continue
            
            # Get demographics
            demo = tract_data.get(geoid)
            
            if not demo:
                stats["no_demographics"] += 1
                continue
            
            # Update parcel
            update_data = {
                "centroid_lat": lat,
                "centroid_lon": lon,
                **demo
            }
            
            if update_parcel(parcel['id'], update_data):
                stats["success"] += 1
            else:
                stats["update_failed"] += 1
        
        print(f"  Processed {offset + len(parcels)} parcels ({stats['success']} updated)...")
        offset += batch_size
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total Parcels:        {stats['total']}")
    print(f"Successfully Updated: {stats['success']}")
    print(f"No Geometry:          {stats['no_geometry']}")
    print(f"No Tract Match:       {stats['no_tract']}")
    print(f"No Demographics:      {stats['no_demographics']}")
    print(f"Update Failed:        {stats['update_failed']}")
    print(f"Success Rate:         {stats['success'] / stats['total'] * 100:.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
