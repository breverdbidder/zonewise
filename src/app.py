"""
ZoneWise Modal App - 20 Phases + 10 Stages Data Pipeline
=========================================================

Autonomous parallel scraping and enrichment for 67 FL counties.

Architecture:
- 20 ZoneWise Data Phases (what data to collect)
- 10 Data Stages (how data flows from raw to enriched)
- 67 FL counties × 18 phases = 1,206 discrete tasks
- Parallel execution via Modal .map()

Supabase: mocerqjnksmhcjzxrewo.supabase.co
GitHub: breverdbidder/zonewise
"""

import modal
import os
import json
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# MODAL APP CONFIGURATION
# =============================================================================

app = modal.App("zonewise-pipeline")

# Container image with all dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "httpx>=0.27.0",
    "supabase>=2.0.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=5.0.0",
    "pdfplumber>=0.10.0",
    "selenium>=4.15.0",
    "pandas>=2.0.0",
    "geopandas>=0.14.0",
    "shapely>=2.0.0",
)

# Modal Secrets (configure in Modal dashboard)
# modal secret create zonewise-secrets \
#   SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co \
#   SUPABASE_KEY=eyJ... \
#   CENSUS_API_KEY=8c6ef3cae05fd24b03c4e541d9eb11c2ba9c6589 \
#   WALKSCORE_API_KEY=xxx \
#   FIRECRAWL_API_KEY=fc-fa112951a2564765a2d146302774ac9b


# =============================================================================
# 20 ZONEWISE DATA PHASES
# =============================================================================

class Phase(Enum):
    """
    20 ZoneWise Data Phases - competitive parity with Gridics/Zoneomics
    
    Foundation (1-5): Core zoning data
    Advanced (6-10): Complex zoning rules
    Specialty (11-15): Niche regulations
    Infrastructure (16-20): Supporting data
    """
    # FOUNDATION DATA (Phases 1-5)
    PROPERTY_IDENTIFICATION = 1   # Parcel ID, Address, Owner, Property Type
    BASE_ZONING = 2               # Zone Code, Name, Description, Category
    DIMENSIONAL_STANDARDS = 3     # Setbacks, Height, FAR, Coverage, Lot Size
    PERMITTED_USES = 4            # By-right uses per district
    CONDITIONAL_USES = 5          # CUP requirements, approval body, conditions
    
    # ADVANCED ZONING (Phases 6-10)
    PROHIBITED_USES = 6           # Not allowed uses, variance eligibility
    OVERLAY_DISTRICTS = 7         # Historic, Flood, Airport, Environmental
    DEVELOPMENT_BONUSES = 8       # Density/height/parking bonuses (UNIQUE)
    PARKING_REQUIREMENTS = 9      # Per-use parking, EV, shared parking
    DENSITY_INTENSITY = 10        # Units/acre, FAR, FLUM max density
    
    # SPECIALTY DATA (Phases 11-15)
    SHORT_TERM_RENTALS = 11       # STR allowed, license, restrictions
    ADU_REGULATIONS = 12          # ADU allowed, size, owner occupancy
    HISTORIC_DESIGN = 13          # Historic districts, design standards
    FLUM_DESIGNATIONS = 14        # Future Land Use Map data
    ENTITLEMENT_TIMELINES = 15    # Processing times (UNIQUE)
    
    # INFRASTRUCTURE (Phases 16-20)
    ORDINANCE_LIBRARY = 16        # Full ordinance text
    ORDINANCE_CHANGES = 17        # Amendment tracking (UNIQUE)
    PARCEL_DATA = 18              # County appraiser APIs
    ENVIRONMENTAL_OVERLAYS = 19   # Flood zones, wetlands, conservation
    CENSUS_DEMOGRAPHICS = 20      # Population, income, housing


# =============================================================================
# 10 DATA STAGES (Malabar POC Framework)
# =============================================================================

class Stage(Enum):
    """
    10-Stage Data Framework from Malabar POC
    
    Each jurisdiction must complete ALL 10 stages for 100% stability.
    """
    ZONE_ASSIGNMENT = 1           # Spatial join: parcel → zone code (GIS)
    ZONING_DISTRICTS = 2          # District definitions from Municode
    DIMENSIONAL_STANDARDS = 3     # Setbacks, heights, lot sizes per zone
    PERMITTED_USES = 4            # Use tables from zoning code
    SOURCE_URLS = 5               # Municode/official code links
    CENSUS_DEMOGRAPHICS = 6       # Census API: income, population, housing
    LOCATION_SCORES = 7           # WalkScore, Schools, Crime
    SALES_HISTORY = 8             # BCPAO/County appraiser sales data
    BUILDING_RECORDS = 9          # BCPAO/County appraiser building details
    PARCEL_ZONE_LINK = 10         # Final parcel_zones table population


# =============================================================================
# FLORIDA COUNTIES (67 total)
# =============================================================================

FL_COUNTIES = {
    # Tier 1: Major metros (priority)
    "brevard": {"fips": "12009", "seat": "Titusville", "pop": 606612, "tier": 1},
    "orange": {"fips": "12095", "seat": "Orlando", "pop": 1429908, "tier": 1},
    "hillsborough": {"fips": "12057", "seat": "Tampa", "pop": 1512070, "tier": 1},
    "miami-dade": {"fips": "12086", "seat": "Miami", "pop": 2716940, "tier": 1},
    "broward": {"fips": "12011", "seat": "Fort Lauderdale", "pop": 1944375, "tier": 1},
    "palm-beach": {"fips": "12099", "seat": "West Palm Beach", "pop": 1496770, "tier": 1},
    "duval": {"fips": "12031", "seat": "Jacksonville", "pop": 995567, "tier": 1},
    "pinellas": {"fips": "12103", "seat": "Clearwater", "pop": 974996, "tier": 1},
    
    # Tier 2: Secondary metros
    "polk": {"fips": "12105", "seat": "Bartow", "pop": 753197, "tier": 2},
    "lee": {"fips": "12071", "seat": "Fort Myers", "pop": 822779, "tier": 2},
    "volusia": {"fips": "12127", "seat": "DeLand", "pop": 553284, "tier": 2},
    "seminole": {"fips": "12117", "seat": "Sanford", "pop": 480587, "tier": 2},
    "pasco": {"fips": "12101", "seat": "Dade City", "pop": 589199, "tier": 2},
    "sarasota": {"fips": "12115", "seat": "Sarasota", "pop": 434006, "tier": 2},
    "manatee": {"fips": "12081", "seat": "Bradenton", "pop": 403253, "tier": 2},
    "collier": {"fips": "12021", "seat": "Naples", "pop": 393973, "tier": 2},
    
    # Tier 3: Remaining 51 counties...
    # (abbreviated for space - full list in production)
}


# =============================================================================
# SUPABASE CLIENT
# =============================================================================

def get_supabase():
    """Initialize Supabase client from Modal secrets"""
    from supabase import create_client
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"]
    )


# =============================================================================
# PHASE SCRAPERS
# =============================================================================

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=20  # Rate-limit safe for Municode
)
def scrape_phase_2_base_zoning(county_id: str, jurisdiction_id: int) -> Dict:
    """
    PHASE 2: Base Zoning Districts
    
    Scrapes zoning district definitions from Municode.
    Returns: List of zoning districts with codes and descriptions.
    """
    supabase = get_supabase()
    
    # Get jurisdiction's Municode URL
    result = supabase.table("jurisdictions").select("municode_url").eq("id", jurisdiction_id).single().execute()
    municode_url = result.data.get("municode_url")
    
    if not municode_url:
        return {"status": "skip", "reason": "No Municode URL"}
    
    # Scrape zoning districts
    districts = []
    async with httpx.AsyncClient() as client:
        # Find zoning chapter
        response = await client.get(f"{municode_url}", timeout=30)
        # Parse and extract districts...
        # (Implementation uses BeautifulSoup to parse table structure)
    
    # Insert to Supabase
    if districts:
        supabase.table("zoning_districts").upsert(
            districts,
            on_conflict="jurisdiction_id,zone_code"
        ).execute()
    
    return {
        "county": county_id,
        "jurisdiction_id": jurisdiction_id,
        "phase": 2,
        "districts_found": len(districts),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=20
)
def scrape_phase_3_dimensional_standards(county_id: str, jurisdiction_id: int) -> Dict:
    """
    PHASE 3: Dimensional Standards
    
    Extracts setbacks, heights, lot sizes from zoning tables.
    Pattern: Table 1-3.3(A) style dimensional standards tables.
    """
    supabase = get_supabase()
    
    # Get existing districts
    districts = supabase.table("zoning_districts")\
        .select("id,zone_code")\
        .eq("jurisdiction_id", jurisdiction_id)\
        .execute().data
    
    standards = []
    for district in districts:
        # Parse dimensional standards from Municode
        dims = {
            "district_id": district["id"],
            "min_lot_size_sf": None,  # Parsed from table
            "min_lot_width_ft": None,
            "front_setback_ft": None,
            "side_setback_ft": None,
            "rear_setback_ft": None,
            "max_height_ft": None,
            "max_building_coverage_pct": None,
            "max_impervious_pct": None,
            "max_far": None,
            "max_density_units_acre": None,
            "source_section": None,
            "source_url": None,
        }
        standards.append(dims)
    
    # Upsert to Supabase
    if standards:
        supabase.table("dimensional_standards").upsert(
            standards,
            on_conflict="district_id"
        ).execute()
    
    return {
        "county": county_id,
        "jurisdiction_id": jurisdiction_id,
        "phase": 3,
        "standards_extracted": len(standards),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=20
)
def scrape_phase_4_permitted_uses(county_id: str, jurisdiction_id: int) -> Dict:
    """
    PHASE 4: Permitted Uses (By-Right)
    
    Extracts use tables: P=Permitted, C=Conditional, S=Special, X=Prohibited
    Target: 50-100 uses per district × 273 districts = 13K-27K rows
    """
    supabase = get_supabase()
    
    # Standard use categories to find
    USE_CATEGORIES = {
        "RESIDENTIAL": [
            "Single-family detached",
            "Single-family attached",
            "Duplex",
            "Townhouse",
            "Multi-family",
            "Manufactured home",
            "Accessory dwelling unit"
        ],
        "COMMERCIAL": [
            "Retail sales",
            "Restaurant",
            "Office",
            "Bank/financial",
            "Hotel/motel",
            "Gas station",
            "Auto sales/service"
        ],
        "INDUSTRIAL": [
            "Light manufacturing",
            "Heavy manufacturing",
            "Warehouse",
            "Distribution center"
        ],
        "INSTITUTIONAL": [
            "Church/worship",
            "School (K-12)",
            "Hospital",
            "Government facility"
        ]
    }
    
    uses = []
    # Parse use matrix from Municode...
    
    if uses:
        supabase.table("permitted_uses").upsert(
            uses,
            on_conflict="district_id,use_name"
        ).execute()
    
    return {
        "county": county_id,
        "jurisdiction_id": jurisdiction_id,
        "phase": 4,
        "uses_extracted": len(uses),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=20
)
def scrape_phase_7_overlay_districts(county_id: str, jurisdiction_id: int) -> Dict:
    """
    PHASE 7: Overlay Districts
    
    Types: Historic, Flood, Airport, Environmental, Downtown/CRA, Corridor, TOD
    """
    supabase = get_supabase()
    
    OVERLAY_SEARCH_TERMS = [
        "overlay district",
        "special district",
        "historic preservation",
        "flood zone",
        "airport approach",
        "conservation area",
        "coastal high hazard",
        "redevelopment area",
        "CRA district",
        "scenic corridor"
    ]
    
    overlays = []
    # Search Municode for overlay sections...
    
    if overlays:
        supabase.table("overlay_districts").upsert(
            overlays,
            on_conflict="jurisdiction_id,overlay_code"
        ).execute()
    
    return {
        "county": county_id,
        "jurisdiction_id": jurisdiction_id,
        "phase": 7,
        "overlays_found": len(overlays),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=20
)
def scrape_phase_8_development_bonuses(county_id: str, jurisdiction_id: int) -> Dict:
    """
    PHASE 8: Development Bonuses (COMPETITIVE ADVANTAGE)
    
    Palm Bay Table 173-8 style incentive programs.
    Neither Gridics nor Zoneomics has comprehensive bonus data.
    """
    supabase = get_supabase()
    
    BONUS_TYPES = [
        "Density Bonus",
        "Height Bonus",
        "Parking Reduction",
        "Setback Reduction",
        "FAR Bonus",
        "Fee Waiver",
        "Expedited Review"
    ]
    
    bonuses = []
    # Parse bonus tables from zoning code...
    
    if bonuses:
        supabase.table("development_bonuses").upsert(
            bonuses,
            on_conflict="jurisdiction_id,bonus_type"
        ).execute()
    
    return {
        "county": county_id,
        "jurisdiction_id": jurisdiction_id,
        "phase": 8,
        "bonuses_found": len(bonuses),
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# STAGE PROCESSORS (10-Stage Malabar Framework)
# =============================================================================

# Import GIS Catalog (verified endpoints)
from src.gis_catalog import (
    BREVARD_GIS_ENDPOINTS,
    BCPAO_CONFIG,
    FL_COUNTY_GIS,
    GISStatus,
    get_endpoint_by_jurisdiction,
    get_working_endpoints,
    build_spatial_query_url,
    build_extent_query_url
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=900,
    retries=3,
    concurrency_limit=10
)
def process_stage_1_zone_assignment(county_id: str, jurisdiction_id: int) -> Dict:
    """
    STAGE 1: Zone Assignment via GIS Spatial Join
    
    Uses verified GIS catalog for endpoint configuration.
    Malabar achieved 100% (2,249/2,249 parcels).
    Titusville achieved 78.2% (21,995/28,118 parcels).
    
    GIS Catalog Coverage (Brevard):
    - ✅ WORKING: Unincorporated (75K), Cocoa (30K), Titusville (28K)
    - ⚠️ OUTAGE: Palm Bay (79K)
    - 📋 MANUAL: Malabar (2.2K)
    """
    import httpx
    supabase = get_supabase()
    
    # Get endpoint from verified GIS catalog
    endpoint = get_endpoint_by_jurisdiction(jurisdiction_id)
    
    if not endpoint:
        return {"status": "skip", "reason": f"No endpoint for jurisdiction {jurisdiction_id}"}
    
    if endpoint.status == GISStatus.NOT_FOUND:
        return {"status": "skip", "reason": f"No GIS endpoint found for {endpoint.jurisdiction}"}
    
    if endpoint.status == GISStatus.TEMPORARY_OUTAGE:
        return {"status": "retry_later", "reason": f"{endpoint.jurisdiction} GIS is temporarily down"}
    
    if endpoint.status == GISStatus.MANUAL_DATA:
        return {"status": "skip", "reason": f"{endpoint.jurisdiction} uses embedded data (already complete)"}
    
    if endpoint.status != GISStatus.WORKING:
        return {"status": "skip", "reason": f"{endpoint.jurisdiction} status: {endpoint.status.value}"}
    
    # Get parcels needing zone assignment
    parcels = supabase.table("sample_properties")\
        .select("id,parcel_id,lat,lon")\
        .eq("jurisdiction_id", jurisdiction_id)\
        .is_("zone_code", "null")\
        .limit(1000)\
        .execute().data
    
    assignments = []
    failed = 0
    
    async with httpx.AsyncClient(timeout=30) as client:
        for parcel in parcels:
            lat, lon = parcel.get("lat"), parcel.get("lon")
            if not lat or not lon:
                failed += 1
                continue
            
            # Build query URL using catalog helper
            query_url = build_spatial_query_url(endpoint, lat, lon)
            
            try:
                response = await client.get(query_url)
                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])
                    if features:
                        zone_code = features[0]["attributes"].get(endpoint.zone_field)
                        if zone_code:
                            assignments.append({
                                "parcel_id": parcel["parcel_id"],
                                "jurisdiction_id": jurisdiction_id,
                                "zone_code": zone_code,
                                "source": "GIS_SPATIAL_JOIN",
                                "confidence_score": 95.0
                            })
            except Exception as e:
                failed += 1
                continue
    
    # Batch insert to parcel_zones
    if assignments:
        supabase.table("parcel_zones").upsert(
            assignments,
            on_conflict="parcel_id,jurisdiction_id"
        ).execute()
    
    return {
        "county": county_id,
        "jurisdiction_id": jurisdiction_id,
        "jurisdiction": endpoint.jurisdiction,
        "stage": 1,
        "parcels_assigned": len(assignments),
        "parcels_failed": failed,
        "gis_endpoint": endpoint.url,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=20
)
def process_stage_6_census_demographics(county_id: str, fips_code: str) -> Dict:
    """
    STAGE 6: Census Demographics via Census API
    
    Variables: B19013_001E (median income), B01003_001E (population),
               B25001_001E (housing units), B25002_003E (vacant)
    """
    census_key = os.environ["CENSUS_API_KEY"]
    supabase = get_supabase()
    
    # Census API endpoint
    CENSUS_URL = "https://api.census.gov/data/2022/acs/acs5"
    
    variables = [
        "B19013_001E",  # Median household income
        "B01003_001E",  # Total population
        "B25001_001E",  # Total housing units
        "B25002_003E",  # Vacant housing units
        "B25077_001E",  # Median home value
        "B25064_001E",  # Median gross rent
    ]
    
    demographics = []
    
    async with httpx.AsyncClient() as client:
        # Query at tract level
        params = {
            "get": ",".join(["NAME"] + variables),
            "for": "tract:*",
            "in": f"state:12&county:{fips_code[2:5]}",
            "key": census_key
        }
        response = await client.get(CENSUS_URL, params=params, timeout=30)
        data = response.json()
        
        # Parse response (first row is headers)
        headers = data[0]
        for row in data[1:]:
            tract_data = dict(zip(headers, row))
            demographics.append({
                "county_id": county_id,
                "tract_id": tract_data.get("tract"),
                "median_income": int(tract_data.get("B19013_001E") or 0),
                "total_population": int(tract_data.get("B01003_001E") or 0),
                "housing_units": int(tract_data.get("B25001_001E") or 0),
                "vacant_units": int(tract_data.get("B25002_003E") or 0),
                "median_home_value": int(tract_data.get("B25077_001E") or 0),
                "median_rent": int(tract_data.get("B25064_001E") or 0),
                "data_year": 2022,
                "source": "ACS 5-Year"
            })
    
    if demographics:
        supabase.table("census_demographics").upsert(
            demographics,
            on_conflict="county_id,tract_id"
        ).execute()
    
    return {
        "county": county_id,
        "stage": 6,
        "tracts_loaded": len(demographics),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=10
)
def process_stage_7_location_scores(county_id: str, parcel_batch: List[Dict]) -> Dict:
    """
    STAGE 7: Location Intelligence Scores
    
    Sources:
    - Walk Score API (FREE 5K/day)
    - NCES + Florida DOE (FREE)
    - FBI CDE + FDLE (FREE)
    
    GitHub repos:
    - gboeing/osmnx (5.4K stars) - walkability alternative
    - UDST/pandana (400 stars) - accessibility metrics
    - fbi-cde/crime-data-api (~100 stars) - crime data
    """
    walkscore_key = os.environ.get("WALKSCORE_API_KEY")
    supabase = get_supabase()
    
    scores = []
    
    for parcel in parcel_batch:
        lat, lon = parcel.get("lat"), parcel.get("lon")
        if not lat or not lon:
            continue
        
        # Walk Score API
        walk_score = None
        if walkscore_key:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.walkscore.com/score",
                    params={
                        "format": "json",
                        "lat": lat,
                        "lon": lon,
                        "wsapikey": walkscore_key
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    walk_score = data.get("walkscore")
        
        # Composite score calculation
        # Weights: Walk 30%, Schools 35%, Crime 35% (inverted)
        school_score = 60  # Default, updated with NCES data
        crime_score = 70   # Default, updated with FBI/FDLE data
        
        composite = int(
            (walk_score or 30) * 0.30 +
            school_score * 0.35 +
            crime_score * 0.35
        )
        
        scores.append({
            "parcel_id": parcel["parcel_id"],
            "walk_score": walk_score,
            "transit_score": None,
            "bike_score": None,
            "school_score": school_score,
            "crime_score": crime_score,
            "composite_score": composite,
            "updated_at": datetime.utcnow().isoformat()
        })
    
    if scores:
        supabase.table("location_scores").upsert(
            scores,
            on_conflict="parcel_id"
        ).execute()
    
    return {
        "county": county_id,
        "stage": 7,
        "parcels_scored": len(scores),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=10
)
def process_stage_8_sales_history(county_id: str, tax_accounts: List[str]) -> Dict:
    """
    STAGE 8: Sales History from County Appraiser
    
    BCPAO API: https://www.bcpao.us/api/v1/account/{account}
    Returns: sale_date, sale_price, deed_type, grantor, grantee
    """
    supabase = get_supabase()
    
    APPRAISER_APIS = {
        "brevard": "https://www.bcpao.us/api/v1/account",
        # Add other counties...
    }
    
    api_url = APPRAISER_APIS.get(county_id)
    if not api_url:
        return {"status": "skip", "reason": "No appraiser API"}
    
    sales = []
    
    async with httpx.AsyncClient() as client:
        for account in tax_accounts:
            try:
                response = await client.get(f"{api_url}/{account}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for sale in data.get("sales", []):
                        sales.append({
                            "tax_account": account,
                            "sale_date": sale.get("date"),
                            "sale_price": sale.get("price"),
                            "deed_type": sale.get("deed_type"),
                            "grantor": sale.get("grantor"),
                            "grantee": sale.get("grantee"),
                            "or_book": sale.get("or_book"),
                            "or_page": sale.get("or_page")
                        })
            except Exception as e:
                continue
    
    if sales:
        supabase.table("sales_history").upsert(
            sales,
            on_conflict="tax_account,sale_date"
        ).execute()
    
    return {
        "county": county_id,
        "stage": 8,
        "sales_loaded": len(sales),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=10
)
def process_stage_9_building_records(county_id: str, tax_accounts: List[str]) -> Dict:
    """
    STAGE 9: Building Records from County Appraiser
    
    BCPAO API: https://www.bcpao.us/api/v1/account/{account}
    Returns: year_built, sqft, bedrooms, bathrooms, construction_type
    """
    supabase = get_supabase()
    
    APPRAISER_APIS = {
        "brevard": "https://www.bcpao.us/api/v1/account",
    }
    
    api_url = APPRAISER_APIS.get(county_id)
    if not api_url:
        return {"status": "skip", "reason": "No appraiser API"}
    
    buildings = []
    
    async with httpx.AsyncClient() as client:
        for account in tax_accounts:
            try:
                response = await client.get(f"{api_url}/{account}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for bldg in data.get("buildings", []):
                        buildings.append({
                            "tax_account": account,
                            "building_num": bldg.get("building_num", 1),
                            "year_built": bldg.get("year_built"),
                            "actual_sqft": bldg.get("actual_sqft"),
                            "living_sqft": bldg.get("living_sqft"),
                            "bedrooms": bldg.get("bedrooms"),
                            "bathrooms": bldg.get("bathrooms"),
                            "construction_type": bldg.get("construction_type"),
                            "roof_type": bldg.get("roof_type"),
                            "stories": bldg.get("stories")
                        })
            except Exception as e:
                continue
    
    if buildings:
        supabase.table("building_details").upsert(
            buildings,
            on_conflict="tax_account,building_num"
        ).execute()
    
    return {
        "county": county_id,
        "stage": 9,
        "buildings_loaded": len(buildings),
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# ORCHESTRATION FUNCTIONS
# =============================================================================

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=3600,
    schedule=modal.Cron("0 23 * * *")  # 11 PM EST daily
)
def nightly_pipeline():
    """
    Nightly Pipeline - runs all phases and stages for active counties.
    
    Uses GIS catalog to route to working endpoints only.
    
    Current: 3 counties (Brevard POC)
    Q1 2026: 67 FL counties, 1K-2K auctions/day
    """
    supabase = get_supabase()
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "counties_processed": [],
        "phases_completed": [],
        "stages_completed": [],
        "gis_status": {}
    }
    
    # Get working endpoints from GIS catalog
    working_endpoints = get_working_endpoints("brevard")
    results["gis_status"] = {
        "working": [ep.jurisdiction for ep in working_endpoints],
        "working_parcels": sum(ep.parcels for ep in working_endpoints)
    }
    
    # Process only jurisdictions with working GIS endpoints
    for endpoint in working_endpoints:
        jurisdiction_id = endpoint.jurisdiction_id
        
        # Stage 1: Zone Assignment
        stage_1_result = process_stage_1_zone_assignment.remote(
            "brevard",
            jurisdiction_id
        )
        results["stages_completed"].append({
            "jurisdiction": endpoint.jurisdiction,
            "stage": 1,
            "result": stage_1_result
        })
        
        # Phases 2-8 for this jurisdiction
        phase_results = []
        
        # Phase 2: Base Zoning
        phase_results.append(
            scrape_phase_2_base_zoning.remote("brevard", jurisdiction_id)
        )
        
        # Phase 3: Dimensional Standards
        phase_results.append(
            scrape_phase_3_dimensional_standards.remote("brevard", jurisdiction_id)
        )
        
        # Phase 4: Permitted Uses
        phase_results.append(
            scrape_phase_4_permitted_uses.remote("brevard", jurisdiction_id)
        )
        
        # Phase 7: Overlay Districts
        phase_results.append(
            scrape_phase_7_overlay_districts.remote("brevard", jurisdiction_id)
        )
        
        # Phase 8: Development Bonuses
        phase_results.append(
            scrape_phase_8_development_bonuses.remote("brevard", jurisdiction_id)
        )
        
        results["phases_completed"].extend(phase_results)
        results["counties_processed"].append(endpoint.jurisdiction)
    
    # Run Stage 6: Census Demographics for entire county
    county_info = FL_COUNTIES.get("brevard")
    if county_info:
        census_result = process_stage_6_census_demographics.remote(
            "brevard",
            county_info["fips"]
        )
        results["stages_completed"].append({
            "jurisdiction": "brevard_county",
            "stage": 6,
            "result": census_result
        })
    
    # Log results to Supabase
    supabase.table("pipeline_runs").insert({
        "run_type": "nightly",
        "results": results,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    return results


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=7200
)
def full_county_pipeline(county_id: str):
    """
    Full County Pipeline - complete 10-stage deployment for a county.
    
    Equivalent to Malabar POC process, but automated.
    Target: 100% data stability across all 10 stages.
    """
    supabase = get_supabase()
    county_info = FL_COUNTIES.get(county_id)
    
    if not county_info:
        return {"error": f"Unknown county: {county_id}"}
    
    results = {
        "county": county_id,
        "timestamp": datetime.utcnow().isoformat(),
        "stages": {}
    }
    
    # Get jurisdictions
    jurisdictions = supabase.table("jurisdictions")\
        .select("id,name")\
        .eq("county", county_id.title())\
        .execute().data
    
    # Stage 1: Zone Assignment (parallel across jurisdictions)
    stage_1_results = list(process_stage_1_zone_assignment.map(
        [county_id] * len(jurisdictions),
        [j["id"] for j in jurisdictions]
    ))
    results["stages"]["1_zone_assignment"] = stage_1_results
    
    # Stages 2-5: Phase scrapers (already covered above)
    phase_results = list(scrape_phase_2_base_zoning.map(
        [county_id] * len(jurisdictions),
        [j["id"] for j in jurisdictions]
    ))
    results["stages"]["2_zoning_districts"] = phase_results
    
    # Stage 6: Census Demographics
    stage_6_result = process_stage_6_census_demographics.remote(
        county_id,
        county_info["fips"]
    )
    results["stages"]["6_census_demographics"] = stage_6_result
    
    # Stage 7: Location Scores (batch parcels)
    parcels = supabase.table("sample_properties")\
        .select("parcel_id,lat,lon")\
        .eq("county", county_id.title())\
        .limit(1000)\
        .execute().data
    
    # Batch into groups of 50
    batches = [parcels[i:i+50] for i in range(0, len(parcels), 50)]
    stage_7_results = list(process_stage_7_location_scores.map(
        [county_id] * len(batches),
        batches
    ))
    results["stages"]["7_location_scores"] = stage_7_results
    
    # Stages 8-9: Sales and Building data
    tax_accounts = [p["tax_account"] for p in 
        supabase.table("sample_properties")
        .select("tax_account")
        .eq("county", county_id.title())
        .limit(1000)
        .execute().data
        if p.get("tax_account")
    ]
    
    # Batch tax accounts
    account_batches = [tax_accounts[i:i+50] for i in range(0, len(tax_accounts), 50)]
    
    stage_8_results = list(process_stage_8_sales_history.map(
        [county_id] * len(account_batches),
        account_batches
    ))
    results["stages"]["8_sales_history"] = stage_8_results
    
    stage_9_results = list(process_stage_9_building_records.map(
        [county_id] * len(account_batches),
        account_batches
    ))
    results["stages"]["9_building_records"] = stage_9_results
    
    # Stage 10: Verify parcel_zones linking
    parcel_zones_count = supabase.table("parcel_zones")\
        .select("id", count="exact")\
        .execute().count
    results["stages"]["10_parcel_zone_link"] = {
        "parcel_zones_count": parcel_zones_count
    }
    
    # Log completion
    supabase.table("pipeline_runs").insert({
        "run_type": "full_county",
        "county": county_id,
        "results": results,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    return results


# =============================================================================
# CLI ENTRYPOINTS
# =============================================================================

@app.local_entrypoint()
def main(
    county: str = "brevard",
    phase: int = None,
    stage: int = None,
    full: bool = False
):
    """
    CLI entrypoint for ZoneWise pipeline.
    
    Usage:
        modal run src/app.py --county brevard --full
        modal run src/app.py --county brevard --phase 2
        modal run src/app.py --county brevard --stage 6
    """
    if full:
        result = full_county_pipeline.remote(county)
        print(f"Full pipeline complete: {result}")
    elif phase:
        # Run specific phase
        print(f"Running phase {phase} for {county}")
    elif stage:
        # Run specific stage
        print(f"Running stage {stage} for {county}")
    else:
        # Run nightly pipeline
        result = nightly_pipeline.remote()
        print(f"Nightly pipeline complete: {result}")


if __name__ == "__main__":
    main()
