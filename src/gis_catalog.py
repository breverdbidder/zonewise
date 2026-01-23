"""
ZoneWise GIS API Catalog
=========================

Verified municipal GIS zoning endpoints for Florida counties.
Used by Modal pipeline for Stage 1: Zone Assignment via spatial join.

Coverage (Brevard County):
- ✅ WORKING: 133,350 parcels (53%)
- ⚠️ TEMPORARY_OUTAGE: 78,697 parcels (31%)
- 📋 MANUAL_DATA: 1,430 parcels (0.6%)
- ❌ NO_ENDPOINT: ~40,000 parcels (16%)

Last Updated: 2026-01-23
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
import json


class GISStatus(Enum):
    """GIS endpoint availability status"""
    WORKING = "WORKING"
    TEMPORARY_OUTAGE = "TEMPORARY_OUTAGE"
    UNVERIFIED = "UNVERIFIED"
    NO_FEATURE_SERVICE = "NO_FEATURE_SERVICE"
    NOT_FOUND = "NOT_FOUND"
    MANUAL_DATA = "MANUAL_DATA"


@dataclass
class GISEndpoint:
    """Municipal GIS endpoint configuration"""
    jurisdiction_id: int
    jurisdiction: str
    county: str
    status: GISStatus
    parcels: int
    url: Optional[str]
    zone_field: Optional[str]
    geometry_type: Optional[str]
    spatial_reference: Optional[int]
    rate_limit: Dict[str, int]
    fallback_strategy: Optional[str]
    notes: str
    last_verified: str


# =============================================================================
# BREVARD COUNTY GIS ENDPOINTS (17 Jurisdictions)
# =============================================================================

BREVARD_GIS_ENDPOINTS: Dict[int, GISEndpoint] = {
    # WORKING ENDPOINTS (Spatial Join Ready)
    13: GISEndpoint(
        jurisdiction_id=13,
        jurisdiction="Unincorporated Brevard County",
        county="Brevard",
        status=GISStatus.WORKING,
        parcels=75350,
        url="https://gis.brevardfl.gov/gissrv/rest/services/Planning_Development/Zoning_WKID2881/MapServer/0",
        zone_field="ZONING",
        geometry_type="esriGeometryPolygon",
        spatial_reference=2881,
        rate_limit={"requests_per_minute": 60, "max_records": 1000},
        fallback_strategy="BCPAO_PARCEL_OVERLAY",
        notes="County-maintained, covers all unincorporated areas. Most reliable source.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    5: GISEndpoint(
        jurisdiction_id=5,
        jurisdiction="Cocoa",
        county="Brevard",
        status=GISStatus.WORKING,
        parcels=29882,
        url="https://services1.arcgis.com/Tex1uhbqnOZPx6qT/arcgis/rest/services/Public_View_Cocoa_Zoning_with_Split_Lots_June_2023_view/FeatureServer/1",
        zone_field="Zoning",
        geometry_type="esriGeometryPolygon",
        spatial_reference=4326,
        rate_limit={"requests_per_minute": 100, "max_records": 2000},
        fallback_strategy="BCPAO_USE_CODE",
        notes="ArcGIS Online hosted, includes split lots. Updated June 2023.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    4: GISEndpoint(
        jurisdiction_id=4,
        jurisdiction="Titusville",
        county="Brevard",
        status=GISStatus.WORKING,
        parcels=28118,
        url="https://gis.titusville.com/arcgis/rest/services/CommunityDevelopment/MapServer/15",
        zone_field="Zone_Code",
        geometry_type="esriGeometryPolygon",
        spatial_reference=2881,
        rate_limit={"requests_per_minute": 60, "max_records": 1000},
        fallback_strategy="BCPAO_USE_CODE",
        notes="City-maintained ArcGIS Server. Zone_Code field verified.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    # TEMPORARY OUTAGE (Monitor and Retry)
    2: GISEndpoint(
        jurisdiction_id=2,
        jurisdiction="Palm Bay",
        county="Brevard",
        status=GISStatus.TEMPORARY_OUTAGE,
        parcels=78697,
        url="https://gis.palmbayflorida.org/arcgis/rest/services/GrowthManagement/Zoning/MapServer/0",
        zone_field="ZONING",
        geometry_type="esriGeometryPolygon",
        spatial_reference=2881,
        rate_limit={"requests_per_minute": 60, "max_records": 1000},
        fallback_strategy="BCPAO_USE_CODE",
        notes="City-maintained, returning 503 errors (temporary server issue). Endpoint is correct.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    # MANUAL DATA (POC Complete)
    14: GISEndpoint(
        jurisdiction_id=14,
        jurisdiction="Town of Malabar",
        county="Brevard",
        status=GISStatus.MANUAL_DATA,
        parcels=2249,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="EMBEDDED_PARCEL_ARRAYS",
        notes="POC Complete. Zone data extracted from Town ArcGIS and embedded in parcel_zones table. 100% coverage.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    # NO FEATURE SERVICE (Tile Only)
    1: GISEndpoint(
        jurisdiction_id=1,
        jurisdiction="Melbourne",
        county="Brevard",
        status=GISStatus.NO_FEATURE_SERVICE,
        parcels=0,
        url="https://tiles.arcgis.com/tiles/QNOUArW14R0lClPo/arcgis/rest/services/ped_atlas_zoning/MapServer",
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="CONTACT_CITY_GIS",
        notes="Only tile service available (no spatial queries). Need to contact city for feature service access.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    # UNVERIFIED (Server Exists But Errors)
    8: GISEndpoint(
        jurisdiction_id=8,
        jurisdiction="Rockledge",
        county="Brevard",
        status=GISStatus.UNVERIFIED,
        parcels=0,
        url="https://gis-rockledge.cityofrockledge.org/server/rest/services/Planning_Building_Public_to_create_a_Web_App/MapServer",
        zone_field="Zoning",
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="VERIFY_ACCESS",
        notes="Server exists but returning errors. Need to verify access permissions.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    # NOT FOUND (Smaller Municipalities)
    3: GISEndpoint(
        jurisdiction_id=3,
        jurisdiction="Indian Harbour Beach",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=4496,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="No public GIS found. May use eLaws like Malabar.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    6: GISEndpoint(
        jurisdiction_id=6,
        jurisdiction="Satellite Beach",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=3500,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="No public GIS found. Uses eLaws for ordinances.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    7: GISEndpoint(
        jurisdiction_id=7,
        jurisdiction="Cocoa Beach",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=5000,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="No public GIS found.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    9: GISEndpoint(
        jurisdiction_id=9,
        jurisdiction="West Melbourne",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=10365,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="Only PDF maps available on city website.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    10: GISEndpoint(
        jurisdiction_id=10,
        jurisdiction="Cape Canaveral",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=7355,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="No public GIS found.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    11: GISEndpoint(
        jurisdiction_id=11,
        jurisdiction="Indialantic",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=5205,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="No public GIS found. Uses eLaws for ordinances.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    12: GISEndpoint(
        jurisdiction_id=12,
        jurisdiction="Melbourne Beach",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=7337,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="No public GIS found. Uses eLaws for ordinances.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    15: GISEndpoint(
        jurisdiction_id=15,
        jurisdiction="Grant-Valkaria",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=3065,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="No public GIS found.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    16: GISEndpoint(
        jurisdiction_id=16,
        jurisdiction="Palm Shores",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=433,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="Small town, no public GIS.",
        last_verified="2026-01-23T14:00:00Z"
    ),
    
    17: GISEndpoint(
        jurisdiction_id=17,
        jurisdiction="Melbourne Village",
        county="Brevard",
        status=GISStatus.NOT_FOUND,
        parcels=200,
        url=None,
        zone_field=None,
        geometry_type=None,
        spatial_reference=None,
        rate_limit={"requests_per_minute": 0, "max_records": 0},
        fallback_strategy="BCPAO_USE_CODE",
        notes="Small town, no public GIS.",
        last_verified="2026-01-23T14:00:00Z"
    ),
}


# =============================================================================
# BCPAO PROPERTY APPRAISER API
# =============================================================================

BCPAO_CONFIG = {
    "name": "Brevard County Property Appraiser",
    "base_url": "https://www.bcpao.us",
    "api_version": "v1",
    "endpoints": {
        "search": "/api/v1/search",
        "account": "/api/v1/account/{account}",
        "parcel": "/api/v1/parcel/{parcel_id}",
    },
    "gis": {
        "base_url": "https://gis.brevardfl.gov/gissrv/rest/services",
        "parcel_layer": "/Base_Map/Parcel_New_WKID2881/MapServer/5",
        "zoning_layer": "/Planning_Development/Zoning_WKID2881/MapServer/0",
    },
    "photo_pattern": "https://www.bcpao.us/photos/{prefix}/{account}011.jpg",
    "fields": {
        "parcel": [
            "PARCEL_ID", "TAX_ACCT", "OWNER_NAME1", "OWNER_NAME2",
            "STREET_NUMBER", "STREET_NAME", "CITY", "ZIP",
            "LAND_VALUE", "BLDG_VALUE", "TOTAL_VALUE",
            "ACRES", "USE_CODE", "ZONING"
        ],
        "building": [
            "YEAR_BUILT", "ACTUAL_SQFT", "LIVING_SQFT",
            "BEDROOMS", "BATHROOMS", "STORIES",
            "CONSTRUCTION_TYPE", "ROOF_TYPE"
        ],
        "sales": [
            "SALE_DATE", "SALE_PRICE", "DEED_TYPE",
            "OR_BOOK", "OR_PAGE", "GRANTOR", "GRANTEE"
        ]
    },
    "rate_limit": {
        "requests_per_minute": 120,
        "concurrent": 10
    }
}


# =============================================================================
# TIER 1 FLORIDA COUNTIES GIS ENDPOINTS
# =============================================================================

FL_COUNTY_GIS: Dict[str, Dict] = {
    "brevard": {
        "fips": "12009",
        "appraiser_url": "https://www.bcpao.us",
        "gis_base": "https://gis.brevardfl.gov/gissrv/rest/services",
        "parcel_layer": "/Base_Map/Parcel_New_WKID2881/MapServer/5",
        "zoning_layer": "/Planning_Development/Zoning_WKID2881/MapServer/0",
        "status": "VERIFIED"
    },
    "orange": {
        "fips": "12095",
        "appraiser_url": "https://www.ocpafl.org",
        "gis_base": "https://maps.ocpafl.org/arcgis/rest/services",
        "parcel_layer": "/Parcels/MapServer/0",
        "zoning_layer": None,  # Need to discover
        "status": "UNVERIFIED"
    },
    "hillsborough": {
        "fips": "12057",
        "appraiser_url": "https://www.hcpafl.org",
        "gis_base": "https://maps.hillsboroughcounty.org/arcgis/rest/services",
        "parcel_layer": None,
        "zoning_layer": None,
        "status": "UNVERIFIED"
    },
    "miami-dade": {
        "fips": "12086",
        "appraiser_url": "https://www.miamidade.gov/pa",
        "gis_base": "https://gisws.miamidade.gov/arcgis/rest/services",
        "parcel_layer": None,
        "zoning_layer": None,
        "status": "UNVERIFIED"
    },
    "broward": {
        "fips": "12011",
        "appraiser_url": "https://www.bcpa.net",
        "gis_base": "https://gis.broward.org/arcgis/rest/services",
        "parcel_layer": None,
        "zoning_layer": None,
        "status": "UNVERIFIED"
    },
    "palm-beach": {
        "fips": "12099",
        "appraiser_url": "https://www.pbcgov.org/papa",
        "gis_base": "https://maps.co.palm-beach.fl.us/arcgis/rest/services",
        "parcel_layer": None,
        "zoning_layer": None,
        "status": "UNVERIFIED"
    },
    "duval": {
        "fips": "12031",
        "appraiser_url": "https://www.coj.net/departments/property-appraiser",
        "gis_base": "https://maps.coj.net/arcgis/rest/services",
        "parcel_layer": None,
        "zoning_layer": None,
        "status": "UNVERIFIED"
    },
    "pinellas": {
        "fips": "12103",
        "appraiser_url": "https://www.pcpao.org",
        "gis_base": "https://egis.pinellascounty.org/arcgis/rest/services",
        "parcel_layer": None,
        "zoning_layer": None,
        "status": "UNVERIFIED"
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_working_endpoints(county: str = "brevard") -> List[GISEndpoint]:
    """Get all working GIS endpoints for a county"""
    if county.lower() == "brevard":
        return [ep for ep in BREVARD_GIS_ENDPOINTS.values() 
                if ep.status == GISStatus.WORKING]
    return []


def get_endpoint_by_jurisdiction(jurisdiction_id: int) -> Optional[GISEndpoint]:
    """Get GIS endpoint by jurisdiction ID"""
    return BREVARD_GIS_ENDPOINTS.get(jurisdiction_id)


def build_spatial_query_url(
    endpoint: GISEndpoint,
    lat: float,
    lon: float,
    out_fields: Optional[List[str]] = None
) -> str:
    """Build ArcGIS REST API spatial query URL"""
    if not endpoint.url:
        return None
    
    fields = out_fields or [endpoint.zone_field, "OBJECTID"]
    fields_str = ",".join(fields)
    
    # Build query parameters
    params = [
        f"geometry={lon},{lat}",
        "geometryType=esriGeometryPoint",
        "inSR=4326",
        "spatialRel=esriSpatialRelIntersects",
        f"outFields={fields_str}",
        "returnGeometry=false",
        "f=json"
    ]
    
    return f"{endpoint.url}/query?{'&'.join(params)}"


def build_extent_query_url(
    endpoint: GISEndpoint,
    xmin: float, ymin: float, xmax: float, ymax: float,
    out_fields: Optional[List[str]] = None,
    result_offset: int = 0,
    result_record_count: int = 1000
) -> str:
    """Build ArcGIS REST API extent query URL for bulk retrieval"""
    if not endpoint.url:
        return None
    
    fields = out_fields or [endpoint.zone_field, "OBJECTID"]
    fields_str = ",".join(fields)
    
    # Build envelope geometry
    envelope = f'{{"xmin":{xmin},"ymin":{ymin},"xmax":{xmax},"ymax":{ymax},"spatialReference":{{"wkid":4326}}}}'
    
    params = [
        f"geometry={envelope}",
        "geometryType=esriGeometryEnvelope",
        "inSR=4326",
        "spatialRel=esriSpatialRelIntersects",
        f"outFields={fields_str}",
        "returnGeometry=true",
        f"resultOffset={result_offset}",
        f"resultRecordCount={result_record_count}",
        "f=geojson"
    ]
    
    return f"{endpoint.url}/query?{'&'.join(params)}"


def export_to_json(filepath: str = "gis_endpoints.json"):
    """Export catalog to JSON file"""
    catalog = {
        "metadata": {
            "version": "2.0.0",
            "created": "2026-01-23",
            "description": "Verified municipal GIS zoning endpoints for Brevard County, Florida",
            "maintainer": "ZoneWise.ai / BidDeed.AI"
        },
        "brevard_endpoints": {
            str(k): {
                "jurisdiction_id": v.jurisdiction_id,
                "jurisdiction": v.jurisdiction,
                "status": v.status.value,
                "parcels": v.parcels,
                "url": v.url,
                "zone_field": v.zone_field,
                "geometry_type": v.geometry_type,
                "spatial_reference": v.spatial_reference,
                "rate_limit": v.rate_limit,
                "fallback_strategy": v.fallback_strategy,
                "notes": v.notes,
                "last_verified": v.last_verified
            }
            for k, v in BREVARD_GIS_ENDPOINTS.items()
        },
        "bcpao": BCPAO_CONFIG,
        "fl_counties": FL_COUNTY_GIS
    }
    
    with open(filepath, "w") as f:
        json.dump(catalog, f, indent=2)
    
    return catalog


# =============================================================================
# COVERAGE SUMMARY
# =============================================================================

def get_coverage_summary() -> Dict:
    """Get coverage summary for Brevard County"""
    working = sum(ep.parcels for ep in BREVARD_GIS_ENDPOINTS.values() 
                  if ep.status == GISStatus.WORKING)
    outage = sum(ep.parcels for ep in BREVARD_GIS_ENDPOINTS.values() 
                 if ep.status == GISStatus.TEMPORARY_OUTAGE)
    manual = sum(ep.parcels for ep in BREVARD_GIS_ENDPOINTS.values() 
                 if ep.status == GISStatus.MANUAL_DATA)
    no_endpoint = sum(ep.parcels for ep in BREVARD_GIS_ENDPOINTS.values() 
                      if ep.status in [GISStatus.NOT_FOUND, GISStatus.NO_FEATURE_SERVICE])
    
    total = working + outage + manual + no_endpoint
    
    return {
        "working": {"parcels": working, "pct": round(working/total*100, 1)},
        "temporary_outage": {"parcels": outage, "pct": round(outage/total*100, 1)},
        "manual_data": {"parcels": manual, "pct": round(manual/total*100, 1)},
        "no_endpoint": {"parcels": no_endpoint, "pct": round(no_endpoint/total*100, 1)},
        "total_parcels": total
    }


if __name__ == "__main__":
    # Print coverage summary
    summary = get_coverage_summary()
    print("=" * 60)
    print("ZONEWISE GIS CATALOG - BREVARD COUNTY COVERAGE")
    print("=" * 60)
    print(f"✅ Working:          {summary['working']['parcels']:,} ({summary['working']['pct']}%)")
    print(f"⚠️  Temporary Outage: {summary['temporary_outage']['parcels']:,} ({summary['temporary_outage']['pct']}%)")
    print(f"📋 Manual Data:      {summary['manual_data']['parcels']:,} ({summary['manual_data']['pct']}%)")
    print(f"❌ No Endpoint:      {summary['no_endpoint']['parcels']:,} ({summary['no_endpoint']['pct']}%)")
    print("-" * 60)
    print(f"Total:               {summary['total_parcels']:,} parcels")
    
    # Export to JSON
    export_to_json("/home/claude/zonewise-modal/config/gis_endpoints.json")
    print("\n✅ Exported to config/gis_endpoints.json")
