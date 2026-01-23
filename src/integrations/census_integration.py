#!/usr/bin/env python3
"""
Census API Integration for ZoneWise
Fetches demographic data and assigns to parcels based on census tract

Data Sources:
- Census Geocoding API: Convert lat/lon to census tract
- Census ACS 5-Year API: Demographic data by tract
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# Configuration
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE"

# Brevard County FIPS
STATE_FIPS = "12"  # Florida
COUNTY_FIPS = "009"  # Brevard

# ACS Variables
ACS_VARIABLES = {
    "B19013_001E": "median_household_income",  # Median household income
    "B01003_001E": "total_population",          # Total population
    "B17001_002E": "poverty_count",             # Population below poverty
    "B25077_001E": "median_home_value",         # Median home value
    "B25064_001E": "median_rent",               # Median gross rent
    "B25002_003E": "vacant_units",              # Vacant housing units
    "B25002_001E": "total_units",               # Total housing units
    "B01002_001E": "median_age",                # Median age
    "B25003_002E": "owner_occupied",            # Owner-occupied units
}


def fetch_acs_data():
    """Fetch ACS 5-year data for all Brevard County census tracts."""
    print("Fetching ACS data for Brevard County...")
    
    variables = ",".join(ACS_VARIABLES.keys())
    url = f"https://api.census.gov/data/2022/acs/acs5?get=NAME,{variables}&for=tract:*&in=state:{STATE_FIPS}&in=county:{COUNTY_FIPS}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching ACS data: {e}")
        return {}
    
    # Parse response into dict keyed by tract GEOID
    headers = data[0]
    tracts = {}
    
    for row in data[1:]:
        row_dict = dict(zip(headers, row))
        tract_code = row_dict.get('tract', '')
        geoid = f"{STATE_FIPS}{COUNTY_FIPS}{tract_code}"
        
        # Calculate derived fields
        total_pop = int(row_dict.get('B01003_001E') or 0)
        poverty_count = int(row_dict.get('B17001_002E') or 0)
        total_units = int(row_dict.get('B25002_001E') or 0)
        vacant_units = int(row_dict.get('B25002_003E') or 0)
        owner_occupied = int(row_dict.get('B25003_002E') or 0)
        
        tracts[geoid] = {
            "geoid": geoid,
            "tract_code": tract_code,
            "name": row_dict.get('NAME', ''),
            "median_household_income": int(row_dict.get('B19013_001E') or 0) or None,
            "total_population": total_pop or None,
            "poverty_count": poverty_count or None,
            "poverty_rate": round(poverty_count / total_pop * 100, 2) if total_pop > 0 else None,
            "median_home_value": int(row_dict.get('B25077_001E') or 0) or None,
            "median_rent": int(row_dict.get('B25064_001E') or 0) or None,
            "vacancy_rate": round(vacant_units / total_units * 100, 2) if total_units > 0 else None,
            "median_age": float(row_dict.get('B01002_001E') or 0) or None,
            "owner_occupied_rate": round(owner_occupied / (total_units - vacant_units) * 100, 2) if (total_units - vacant_units) > 0 else None,
        }
    
    print(f"Fetched {len(tracts)} census tracts")
    return tracts


def geocode_to_tract(lat, lon):
    """Use Census Geocoding API to get census tract for coordinates."""
    url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x={lon}&y={lat}&benchmark=Public_AR_Current&vintage=Current_Current&layers=10&format=json"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return None, None
    
    result = data.get('result', {})
    geographies = result.get('geographies', {})
    
    # Try Census Tracts first
    tracts = geographies.get('Census Tracts', [])
    if tracts:
        tract = tracts[0]
        geoid = tract.get('GEOID')
        tract_code = tract.get('TRACT')
        return geoid, tract_code
    
    # Fall back to Census Block Groups
    block_groups = geographies.get('Census Block Groups', [])
    if block_groups:
        bg = block_groups[0]
        tract_code = bg.get('TRACT')
        geoid = f"{bg.get('STATE')}{bg.get('COUNTY')}{tract_code}"
        return geoid, tract_code
    
    return None, None


def fetch_parcels(jurisdiction_id):
    """Fetch parcels from Supabase for given jurisdiction."""
    url = f"{SUPABASE_URL}/rest/v1/sample_properties?jurisdiction_id=eq.{jurisdiction_id}&select=id,parcel_id,centroid_lat,centroid_lon"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Range": "0-9999"
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching parcels: {e}")
        return []


def update_parcel_demographics(parcel_id, demographics):
    """Update parcel with demographic data."""
    url = f"{SUPABASE_URL}/rest/v1/sample_properties?id=eq.{parcel_id}"
    
    # Add update timestamp
    demographics["demographics_updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    data = json.dumps(demographics).encode('utf-8')
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    req = urllib.request.Request(url, data=data, headers=headers, method='PATCH')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return True
    except Exception as e:
        print(f"Error updating parcel {parcel_id}: {e}")
        return False


def process_jurisdiction(jurisdiction_id, jurisdiction_name, tract_data):
    """Process all parcels in a jurisdiction."""
    print(f"\nProcessing {jurisdiction_name} (ID: {jurisdiction_id})...")
    
    parcels = fetch_parcels(jurisdiction_id)
    print(f"Found {len(parcels)} parcels")
    
    if not parcels:
        return {"total": 0, "success": 0, "failed": 0, "no_coords": 0}
    
    stats = {"total": len(parcels), "success": 0, "failed": 0, "no_coords": 0, "no_tract": 0}
    tract_cache = {}  # Cache geocoded tracts
    
    for i, parcel in enumerate(parcels):
        lat = parcel.get('centroid_lat')
        lon = parcel.get('centroid_lon')
        
        if not lat or not lon:
            stats["no_coords"] += 1
            continue
        
        # Check cache first
        cache_key = f"{round(lat, 4)},{round(lon, 4)}"
        if cache_key in tract_cache:
            geoid = tract_cache[cache_key]
        else:
            # Geocode to get tract
            geoid, tract_code = geocode_to_tract(lat, lon)
            tract_cache[cache_key] = geoid
            time.sleep(0.1)  # Rate limit
        
        if not geoid:
            stats["no_tract"] += 1
            continue
        
        # Get demographics from tract data
        tract = tract_data.get(geoid)
        if not tract:
            stats["no_tract"] += 1
            continue
        
        # Build update payload
        demographics = {
            "census_tract": tract["tract_code"],
            "median_household_income": tract["median_household_income"],
            "total_population": tract["total_population"],
            "poverty_count": tract["poverty_count"],
            "poverty_rate": tract["poverty_rate"],
            "median_home_value": tract["median_home_value"],
            "median_rent": tract["median_rent"],
            "vacancy_rate": tract["vacancy_rate"],
        }
        
        if update_parcel_demographics(parcel['id'], demographics):
            stats["success"] += 1
        else:
            stats["failed"] += 1
        
        # Progress update
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(parcels)} parcels...")
    
    return stats


def main():
    """Main entry point."""
    print("=" * 60)
    print("ZoneWise Census API Integration")
    print("=" * 60)
    
    # Step 1: Fetch all Brevard County tract data
    tract_data = fetch_acs_data()
    if not tract_data:
        print("Failed to fetch ACS data. Exiting.")
        return
    
    # Step 2: Process Malabar (jurisdiction_id = 14)
    stats = process_jurisdiction(14, "Malabar", tract_data)
    
    print("\n" + "=" * 60)
    print("RESULTS - Malabar POC")
    print("=" * 60)
    print(f"Total Parcels: {stats['total']}")
    print(f"Successfully Updated: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    print(f"No Coordinates: {stats['no_coords']}")
    print(f"No Tract Match: {stats.get('no_tract', 0)}")
    print(f"Success Rate: {stats['success'] / stats['total'] * 100:.1f}%" if stats['total'] > 0 else "N/A")


if __name__ == "__main__":
    main()
