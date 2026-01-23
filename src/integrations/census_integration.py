#!/usr/bin/env python3
"""
Census API Integration for ZoneWise
Populates demographic data from Census ACS 5-Year estimates

Usage:
    python census_integration_v2.py --jurisdiction 14  # Malabar
    python census_integration_v2.py --all              # All jurisdictions
"""

import json
import time
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE"

def fetch_acs_data():
    """Fetch ACS 5-year data for Brevard County."""
    url = "https://api.census.gov/data/2022/acs/acs5?get=NAME,B19013_001E,B01003_001E,B17001_002E,B25077_001E,B25064_001E&for=tract:*&in=state:12&in=county:009"
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read().decode())
    
    headers = data[0]
    tracts = {}
    for row in data[1:]:
        row_dict = dict(zip(headers, row))
        tract_code = row_dict.get('tract', '')
        geoid = f"12009{tract_code}"
        total_pop = int(row_dict.get('B01003_001E') or 0)
        poverty = int(row_dict.get('B17001_002E') or 0)
        
        tracts[geoid] = {
            "census_tract": tract_code,
            "median_household_income": int(row_dict.get('B19013_001E') or 0) or None,
            "total_population": total_pop or None,
            "poverty_rate": round(poverty / total_pop * 100, 2) if total_pop > 0 else None,
            "median_home_value": int(row_dict.get('B25077_001E') or 0) or None,
            "median_rent": int(row_dict.get('B25064_001E') or 0) or None,
        }
    return tracts

def geocode_to_tract(lat, lon, cache):
    """Geocode coordinates to census tract with caching."""
    cache_key = f"{round(lat, 3)},{round(lon, 3)}"
    if cache_key in cache:
        return cache[cache_key]
    
    url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x={lon}&y={lat}&benchmark=Public_AR_Current&vintage=Current_Current&layers=10&format=json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        geographies = data.get('result', {}).get('geographies', {})
        tract_list = geographies.get('Census Tracts', [])
        if tract_list:
            cache[cache_key] = tract_list[0].get('GEOID')
        else:
            bg_list = geographies.get('Census Block Groups', [])
            cache[cache_key] = f"12009{bg_list[0].get('TRACT')}" if bg_list else None
        time.sleep(0.02)
    except:
        cache[cache_key] = None
    return cache[cache_key]

def process_jurisdiction(jurisdiction_id, tracts):
    """Process all parcels in a jurisdiction."""
    print(f"Processing jurisdiction {jurisdiction_id}...")
    
    geocode_cache = {}
    stats = {"success": 0, "failed": 0, "total": 0}
    offset = 0
    
    while True:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/sample_properties?jurisdiction_id=eq.{jurisdiction_id}&select=id,geometry&order=id",
            headers={"apikey": SUPABASE_KEY, "Range": f"{offset}-{offset+499}"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            parcels = json.loads(response.read().decode())
        
        if not parcels:
            break
        
        stats["total"] += len(parcels)
        
        for parcel in parcels:
            geom = parcel.get('geometry')
            if not geom or 'rings' not in geom:
                continue
            
            ring = geom['rings'][0]
            lon = sum(pt[0] for pt in ring) / len(ring)
            lat = sum(pt[1] for pt in ring) / len(ring)
            
            geoid = geocode_to_tract(lat, lon, geocode_cache)
            if not geoid:
                continue
            
            demo = tracts.get(geoid, {})
            if not demo:
                continue
            
            update_data = {
                "centroid_lat": lat,
                "centroid_lon": lon,
                "demographics_updated_at": datetime.now(timezone.utc).isoformat(),
                **demo
            }
            
            url = f"{SUPABASE_URL}/rest/v1/sample_properties?id=eq.{parcel['id']}"
            req = urllib.request.Request(url, data=json.dumps(update_data).encode('utf-8'),
                headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                         "Content-Type": "application/json", "Prefer": "return=minimal"},
                method='PATCH')
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    stats["success"] += 1
            except:
                stats["failed"] += 1
        
        print(f"  Processed {offset + len(parcels)} parcels...")
        offset += 500
        
        if len(parcels) < 500:
            break
    
    return stats

if __name__ == "__main__":
    import sys
    
    jurisdiction_id = 14  # Default to Malabar
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            jurisdiction_id = None
        else:
            jurisdiction_id = int(sys.argv[1].replace("--jurisdiction", "").strip())
    
    print("Fetching ACS data...")
    tracts = fetch_acs_data()
    print(f"  Retrieved {len(tracts)} census tracts")
    
    if jurisdiction_id:
        stats = process_jurisdiction(jurisdiction_id, tracts)
        print(f"\nResults: {stats['success']}/{stats['total']} updated")
    else:
        for jid in range(1, 18):
            stats = process_jurisdiction(jid, tracts)
            print(f"  Jurisdiction {jid}: {stats['success']}/{stats['total']}")
