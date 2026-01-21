"""
ZoneWise V3 - Parcels API Endpoint
/api/v1/parcels - CRUD operations for parcel data
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
import structlog

from services.supabase_client import get_supabase

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/parcels", tags=["parcels"])


class ParcelResponse(BaseModel):
    """Parcel response model"""
    parcel_id: str
    address: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    zone_code: Optional[str] = None
    zone_district: Optional[str] = None
    lot_size_sqft: Optional[float] = None
    living_area_sqft: Optional[float] = None
    year_built: Optional[int] = None
    assessed_value: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ParcelDetail(ParcelResponse):
    """Detailed parcel response"""
    land_value: Optional[float] = None
    improvement_value: Optional[float] = None
    last_sale_date: Optional[str] = None
    last_sale_price: Optional[float] = None
    flood_zone: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    owner_type: Optional[str] = None


class ParcelSearchParams(BaseModel):
    """Search parameters"""
    zone_code: Optional[str] = None
    city: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_lot_size: Optional[float] = None
    max_lot_size: Optional[float] = None


@router.get("/{parcel_id}", response_model=ParcelDetail)
async def get_parcel(parcel_id: str):
    """Get parcel by ID"""
    supabase = get_supabase()
    
    result = await supabase.table("fl_parcels").select("*").eq("parcel_id", parcel_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Parcel {parcel_id} not found")
    
    return ParcelDetail(**result.data)


@router.get("/", response_model=List[ParcelResponse])
async def search_parcels(
    address: Optional[str] = Query(None, description="Search by address"),
    zone_code: Optional[str] = Query(None, description="Filter by zone code"),
    city: Optional[str] = Query(None, description="Filter by city"),
    min_value: Optional[float] = Query(None, description="Minimum assessed value"),
    max_value: Optional[float] = Query(None, description="Maximum assessed value"),
    limit: int = Query(50, le=200, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Search parcels with filters"""
    supabase = get_supabase()
    
    query = supabase.table("fl_parcels").select(
        "parcel_id, address, city, zip_code, zone_code, zone_district, "
        "lot_size_sqft, living_area_sqft, year_built, assessed_value, latitude, longitude"
    )
    
    # Apply filters
    if address:
        query = query.ilike("address", f"%{address}%")
    if zone_code:
        query = query.eq("zone_code", zone_code)
    if city:
        query = query.ilike("city", f"%{city}%")
    if min_value:
        query = query.gte("assessed_value", min_value)
    if max_value:
        query = query.lte("assessed_value", max_value)
    
    # Pagination
    query = query.range(offset, offset + limit - 1)
    
    result = await query.execute()
    
    return [ParcelResponse(**p) for p in result.data] if result.data else []


@router.get("/{parcel_id}/zoning")
async def get_parcel_zoning(parcel_id: str):
    """Get zoning details for a parcel"""
    supabase = get_supabase()
    
    # Get parcel zone code
    parcel = await supabase.table("fl_parcels").select(
        "zone_code, jurisdiction"
    ).eq("parcel_id", parcel_id).single().execute()
    
    if not parcel.data:
        raise HTTPException(status_code=404, detail=f"Parcel {parcel_id} not found")
    
    zone_code = parcel.data.get("zone_code")
    jurisdiction = parcel.data.get("jurisdiction", "Brevard County")
    
    # Get zone rules
    zone = await supabase.table("fl_zoning_districts").select("*").eq(
        "zone_code", zone_code
    ).eq("jurisdiction", jurisdiction).single().execute()
    
    if not zone.data:
        return {
            "parcel_id": parcel_id,
            "zone_code": zone_code,
            "jurisdiction": jurisdiction,
            "message": "Zone details not found in database"
        }
    
    return {
        "parcel_id": parcel_id,
        **zone.data
    }


@router.get("/{parcel_id}/comparables")
async def get_parcel_comparables(
    parcel_id: str,
    radius_miles: float = Query(1.0, le=5.0, description="Search radius in miles"),
    max_results: int = Query(5, le=20, description="Maximum comparables")
):
    """Get comparable sales for a parcel"""
    supabase = get_supabase()
    
    # Call the find_comparable_sales function
    result = await supabase.rpc(
        "find_comparable_sales",
        {
            "subject_parcel_id": parcel_id,
            "search_radius_meters": radius_miles * 1609.34,
            "max_results": max_results
        }
    ).execute()
    
    return {
        "parcel_id": parcel_id,
        "radius_miles": radius_miles,
        "comparables": result.data if result.data else []
    }
