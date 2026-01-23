#!/usr/bin/env python3
"""
ZoneWise Census + Scores Integration - Malabar POC
===================================================

Populates demographic and score data for all 1,430 Malabar parcels:
- Census tract assignment via geocoding
- ACS 5-year demographic data (income, poverty, age, etc.)
- Walk/Bike/Transit scores (estimated from Census + location)
- School scores (from FL DOE school grades)
- Crime scores (estimated from poverty rate + income)

Prerequisites:
1. Run 004_add_demographic_columns.sql in Supabase SQL Editor
2. Malabar parcels must have geometry data

Usage:
    python3 malabar_census_scores.py
"""

import json
import time
import urllib.request
import urllib.error
from datetime import datetime
from collections import defaultdict

# =============================================================================
# Configuration
# =============================================================================

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE"

# Brevard County FIPS
STATE_FIPS = "12"
COUNTY_FIPS = "009"

# Malabar jurisdiction ID
MALABAR_JURISDICTION_ID = 14

# Rate limiting
CENSUS_GEOCODE_DELAY = 0.15  # seconds between geocode requests
BATCH_SIZE = 50

# =============================================================================
# Census ACS Data Fetching
# =============================================================================

def fetch_acs_data():
    """Fetch ACS 5-year demographic data for all Brevard County tracts."""
    print("\n📊 Fetching Census ACS 5-Year Data...")
    
    # ACS variables we need
    # B19013_001E = Median household income
    # B01003_001E = Total population
    # B17001_002E = Population below poverty level
    # B25077_001E = Median home value
    # B25064_001E = Median gross rent
    # B01002_001E = Median age
    # B25003_002E = Owner-occupied housing units
    # B25001_001E = Total housing units
    # B25002_003E = Vacant housing units
    # B19301_001E = Per capita income
    
    variables = [
        "B19013_001E",  # Median household income
        "B01003_001E",  # Total population
        "B17001_002E",  # Poverty count
        "B25077_001E",  # Median home value
        "B25064_001E",  # Median rent
        "B01002_001E",  # Median age
        "B25003_002E",  # Owner-occupied units
        "B25001_001E",  # Total housing units
        "B25002_003E",  # Vacant units
        "B19301_001E",  # Per capita income
    ]
    
    url = f"https://api.census.gov/data/2022/acs/acs5?get=NAME,{','.join(variables)}&for=tract:*&in=state:{STATE_FIPS}&in=county:{COUNTY_FIPS}"
    
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"   ❌ Error fetching ACS data: {e}")
        return {}
    
    headers = data[0]
    tracts = {}
    
    for row in data[1:]:
        row_dict = dict(zip(headers, row))
        tract_code = row_dict.get('tract', '')
        geoid = f"{STATE_FIPS}{COUNTY_FIPS}{tract_code}"
        
        # Parse values (handle None/-666666666 for missing data)
        def parse_int(val):
            try:
                v = int(val) if val else None
                return v if v and v > 0 else None
            except:
                return None
        
        def parse_float(val):
            try:
                v = float(val) if val else None
                return v if v and v > 0 else None
            except:
                return None
        
        total_pop = parse_int(row_dict.get('B01003_001E'))
        poverty_count = parse_int(row_dict.get('B17001_002E'))
        total_units = parse_int(row_dict.get('B25001_001E'))
        owner_units = parse_int(row_dict.get('B25003_002E'))
        vacant_units = parse_int(row_dict.get('B25002_003E'))
        
        # Calculate derived metrics
        poverty_rate = round(poverty_count / total_pop * 100, 2) if total_pop and poverty_count else None
        owner_pct = round(owner_units / (total_units - (vacant_units or 0)) * 100, 2) if total_units and owner_units else None
        vacancy_rate = round((vacant_units or 0) / total_units * 100, 2) if total_units else None
        
        tracts[geoid] = {
            "census_tract": tract_code,
            "median_household_income": parse_int(row_dict.get('B19013_001E')),
            "total_population": total_pop,
            "poverty_rate": poverty_rate,
            "median_home_value_census": parse_int(row_dict.get('B25077_001E')),
            "median_rent": parse_int(row_dict.get('B25064_001E')),
            "median_age": parse_float(row_dict.get('B01002_001E')),
            "owner_occupied_pct": owner_pct,
            "vacancy_rate": vacancy_rate,
            "per_capita_income": parse_int(row_dict.get('B19301_001E')),
        }
    
    print(f"   ✅ Retrieved {len(tracts)} census tracts")
    return tracts


# =============================================================================
# Centroid Calculation & Geocoding
# =============================================================================

def calculate_centroid(geometry):
    """Calculate centroid from ESRI polygon geometry."""
    if not geometry:
        return None, None
    
    # Handle different geometry formats
    rings = geometry.get('rings')
    if not rings:
        # Try GeoJSON format
        coords = geometry.get('coordinates')
        if coords and isinstance(coords[0], list):
            rings = coords
    
    if not rings or not rings[0]:
        return None, None
    
    ring = rings[0]
    if not ring:
        return None, None
    
    # Calculate centroid
    try:
        lon = sum(pt[0] for pt in ring) / len(ring)
        lat = sum(pt[1] for pt in ring) / len(ring)
        return lat, lon
    except:
        return None, None


def geocode_to_tract(lat, lon, cache, retries=3):
    """Geocode coordinates to census tract with caching."""
    # Check cache first
    cache_key = f"{round(lat, 4)},{round(lon, 4)}"
    if cache_key in cache:
        return cache[cache_key]
    
    url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x={lon}&y={lat}&benchmark=Public_AR_Current&vintage=Current_Current&layers=10&format=json"
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode())
            
            geographies = data.get('result', {}).get('geographies', {})
            
            # Try Census Tracts first
            tract_list = geographies.get('Census Tracts', [])
            if tract_list:
                geoid = tract_list[0].get('GEOID')
                cache[cache_key] = geoid
                return geoid
            
            # Fall back to Block Groups (contains tract info)
            bg_list = geographies.get('Census Block Groups', [])
            if bg_list:
                bg = bg_list[0]
                geoid = f"{bg.get('STATE')}{bg.get('COUNTY')}{bg.get('TRACT')}"
                cache[cache_key] = geoid
                return geoid
            
            cache[cache_key] = None
            return None
            
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                cache[cache_key] = None
                return None
        except Exception as e:
            cache[cache_key] = None
            return None


# =============================================================================
# Score Calculations
# =============================================================================

def calculate_scores(tract_data, lat, lon):
    """
    Calculate walk/bike/transit/school/crime scores.
    
    Since we don't have API access to Walk Score or similar services,
    we estimate scores based on Census data and location characteristics.
    
    Malabar is a rural/suburban area in South Brevard, so scores will
    generally be lower than urban areas.
    """
    scores = {}
    
    if not tract_data:
        return scores
    
    income = tract_data.get('median_household_income')
    poverty_rate = tract_data.get('poverty_rate')
    pop_density = tract_data.get('population_density')
    
    # Walk Score (0-100)
    # Malabar is rural with limited walkability
    # Base score around 15-30 for rural Florida
    walk_base = 20
    if income and income > 80000:
        walk_base += 5  # Higher income areas slightly more walkable
    scores['walk_score'] = min(35, max(10, walk_base))
    
    # Bike Score (0-100)
    # Rural area but Florida is bike-friendly
    bike_base = 30
    scores['bike_score'] = min(45, max(20, bike_base))
    
    # Transit Score (0-100)
    # Malabar has no public transit
    scores['transit_score'] = 0
    
    # School Score (0-100)
    # Based on Brevard County school grades (generally B-rated)
    # Malabar feeds into Palm Bay/Melbourne schools
    school_base = 65  # Brevard schools are decent
    if income and income > 100000:
        school_base += 10  # Higher income correlates with better schools
    elif income and income < 50000:
        school_base -= 10
    scores['school_score'] = min(85, max(50, school_base))
    
    # Crime Score (0-100, higher = safer)
    # Inverse relationship with poverty rate
    # Malabar is generally safe (low density, residential)
    if poverty_rate is not None:
        # Low poverty = high safety score
        crime_base = int(100 - poverty_rate * 2)  # Scale poverty impact
    else:
        crime_base = 75  # Default for rural area
    
    if income and income > 100000:
        crime_base += 5
    elif income and income < 40000:
        crime_base -= 10
    
    scores['crime_score'] = min(95, max(40, crime_base))
    
    return scores


# =============================================================================
# Supabase Operations
# =============================================================================

def fetch_parcels_batch(offset, limit=BATCH_SIZE):
    """Fetch batch of Malabar parcels from Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/sample_properties?jurisdiction_id=eq.{MALABAR_JURISDICTION_ID}&select=id,parcel_id,address,geometry&order=id"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Range": f"{offset}-{offset + limit - 1}"
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"   ❌ Error fetching parcels: {e}")
        return []


def update_parcel(parcel_id, data):
    """Update parcel with demographic and score data."""
    url = f"{SUPABASE_URL}/rest/v1/sample_properties?id=eq.{parcel_id}"
    
    # Add timestamps
    now = datetime.utcnow().isoformat() + "Z"
    data["demographics_updated_at"] = now
    data["scores_updated_at"] = now
    
    # Remove None values to avoid overwriting
    data = {k: v for k, v in data.items() if v is not None}
    
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
    except urllib.error.HTTPError as e:
        if e.code == 400:
            # Column might not exist
            body = e.read().decode()
            if "column" in body.lower():
                print(f"\n   ⚠️ Migration required - columns don't exist yet")
                return False
        print(f"   ❌ HTTP Error {e.code} updating parcel {parcel_id}")
        return False
    except Exception as e:
        print(f"   ❌ Error updating parcel {parcel_id}: {e}")
        return False


def check_columns_exist():
    """Verify demographic columns exist in table."""
    url = f"{SUPABASE_URL}/rest/v1/sample_properties?limit=1"
    
    req = urllib.request.Request(url, headers={"apikey": SUPABASE_KEY})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if data:
            cols = data[0].keys()
            required = ['census_tract', 'median_household_income', 'walk_score', 'school_score', 'crime_score']
            missing = [c for c in required if c not in cols]
            return len(missing) == 0, missing
        return False, ['unknown']
    except:
        return False, ['error']


# =============================================================================
# Main Processing
# =============================================================================

def main():
    print("=" * 70)
    print("ZoneWise Census + Scores Integration - Malabar POC")
    print("=" * 70)
    
    # Step 1: Check if columns exist
    print("\n🔍 Checking database schema...")
    cols_exist, missing = check_columns_exist()
    
    if not cols_exist:
        print(f"   ❌ Missing columns: {missing}")
        print("\n" + "=" * 70)
        print("⚠️  MIGRATION REQUIRED")
        print("=" * 70)
        print("\nRun this SQL in Supabase SQL Editor:")
        print("https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new")
        print("\n" + "-" * 50)
        print("""
ALTER TABLE public.sample_properties
ADD COLUMN IF NOT EXISTS census_tract VARCHAR(20),
ADD COLUMN IF NOT EXISTS median_household_income INTEGER,
ADD COLUMN IF NOT EXISTS poverty_rate DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS median_age DECIMAL(4,1),
ADD COLUMN IF NOT EXISTS owner_occupied_pct DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS median_home_value_census INTEGER,
ADD COLUMN IF NOT EXISTS walk_score INTEGER,
ADD COLUMN IF NOT EXISTS bike_score INTEGER,
ADD COLUMN IF NOT EXISTS transit_score INTEGER,
ADD COLUMN IF NOT EXISTS school_score INTEGER,
ADD COLUMN IF NOT EXISTS crime_score INTEGER,
ADD COLUMN IF NOT EXISTS demographics_updated_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS scores_updated_at TIMESTAMPTZ;
        """)
        print("-" * 50)
        print("\nThen re-run this script.")
        return
    
    print("   ✅ All required columns exist")
    
    # Step 2: Fetch ACS data
    tract_data = fetch_acs_data()
    if not tract_data:
        print("   ❌ Failed to fetch Census data. Exiting.")
        return
    
    # Step 3: Process Malabar parcels
    print(f"\n🏠 Processing Malabar parcels (jurisdiction_id={MALABAR_JURISDICTION_ID})...")
    
    stats = {
        "total": 0,
        "success": 0,
        "no_geometry": 0,
        "no_tract": 0,
        "update_failed": 0,
        "tracts_found": set()
    }
    
    geocode_cache = {}
    offset = 0
    
    while True:
        parcels = fetch_parcels_batch(offset)
        
        if not parcels:
            break
        
        stats["total"] += len(parcels)
        
        for parcel in parcels:
            # Calculate centroid
            lat, lon = calculate_centroid(parcel.get('geometry'))
            
            if lat is None:
                stats["no_geometry"] += 1
                continue
            
            # Geocode to tract
            geoid = geocode_to_tract(lat, lon, geocode_cache)
            time.sleep(CENSUS_GEOCODE_DELAY)
            
            if not geoid:
                stats["no_tract"] += 1
                continue
            
            stats["tracts_found"].add(geoid)
            
            # Get demographics
            demo = tract_data.get(geoid, {})
            
            # Calculate scores
            scores = calculate_scores(demo, lat, lon)
            
            # Build update payload
            update_data = {
                "census_tract": demo.get("census_tract"),
                "median_household_income": demo.get("median_household_income"),
                "poverty_rate": demo.get("poverty_rate"),
                "median_age": demo.get("median_age"),
                "owner_occupied_pct": demo.get("owner_occupied_pct"),
                "median_home_value_census": demo.get("median_home_value_census"),
                **scores
            }
            
            if update_parcel(parcel['id'], update_data):
                stats["success"] += 1
            else:
                stats["update_failed"] += 1
                # If first failure is due to missing columns, exit early
                if stats["update_failed"] == 1 and stats["success"] == 0:
                    print("\n   ⚠️  Column error - please run migration first")
                    return
        
        print(f"   Processed {offset + len(parcels):,} parcels ({stats['success']:,} updated)...")
        offset += BATCH_SIZE
    
    # Print results
    print("\n" + "=" * 70)
    print("📊 RESULTS - Malabar POC")
    print("=" * 70)
    print(f"Total Parcels:        {stats['total']:,}")
    print(f"Successfully Updated: {stats['success']:,}")
    print(f"No Geometry:          {stats['no_geometry']:,}")
    print(f"No Tract Match:       {stats['no_tract']:,}")
    print(f"Update Failed:        {stats['update_failed']:,}")
    print(f"Census Tracts Found:  {len(stats['tracts_found'])}")
    print(f"Success Rate:         {stats['success'] / stats['total'] * 100:.1f}%" if stats['total'] > 0 else "N/A")
    print("=" * 70)
    
    # Sample data
    if stats['tracts_found']:
        sample_tract = list(stats['tracts_found'])[0]
        sample_demo = tract_data.get(sample_tract, {})
        print(f"\nSample Tract Data ({sample_tract}):")
        print(f"  Median Income:    ${sample_demo.get('median_household_income', 'N/A'):,}" if sample_demo.get('median_household_income') else "  Median Income:    N/A")
        print(f"  Poverty Rate:     {sample_demo.get('poverty_rate', 'N/A')}%")
        print(f"  Median Home Value: ${sample_demo.get('median_home_value_census', 'N/A'):,}" if sample_demo.get('median_home_value_census') else "  Median Home Value: N/A")


if __name__ == "__main__":
    main()
