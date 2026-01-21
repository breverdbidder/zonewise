"""
ZoneWise V3 - Map API Endpoint
/api/v1/map - Spatial queries and GeoJSON generation
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import structlog

from services.supabase_client import get_supabase

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/map", tags=["map"])


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature"""
    type: str = "Feature"
    geometry: dict
    properties: dict


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON Feature Collection"""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


@router.get("/parcels", response_model=GeoJSONFeatureCollection)
async def get_parcels_in_bounds(
    min_lng: float = Query(..., description="Southwest longitude"),
    min_lat: float = Query(..., description="Southwest latitude"),
    max_lng: float = Query(..., description="Northeast longitude"),
    max_lat: float = Query(..., description="Northeast latitude"),
    limit: int = Query(1000, le=5000, description="Maximum parcels")
):
    """Get parcels within map bounds as GeoJSON"""
    supabase = get_supabase()
    
    # Call the spatial function
    result = await supabase.rpc(
        "get_parcels_in_bounds",
        {
            "min_lng": min_lng,
            "min_lat": min_lat,
            "max_lng": max_lng,
            "max_lat": max_lat,
            "max_parcels": limit
        }
    ).execute()
    
    if not result.data:
        return GeoJSONFeatureCollection(features=[])
    
    # Convert to GeoJSON features
    features = []
    for parcel in result.data:
        if parcel.get("latitude") and parcel.get("longitude"):
            feature = GeoJSONFeature(
                geometry={
                    "type": "Point",
                    "coordinates": [float(parcel["longitude"]), float(parcel["latitude"])]
                },
                properties={
                    "parcel_id": parcel["parcel_id"],
                    "address": parcel.get("address"),
                    "zone_code": parcel.get("zone_code"),
                    "assessed_value": parcel.get("assessed_value")
                }
            )
            features.append(feature)
    
    return GeoJSONFeatureCollection(features=features)


@router.get("/zoning", response_model=GeoJSONFeatureCollection)
async def get_zoning_districts():
    """Get zoning districts as GeoJSON"""
    supabase = get_supabase()
    
    # Get zone boundaries (if available) or create from parcels
    result = await supabase.table("fl_zoning_districts").select(
        "zone_code, zone_name, color_hex"
    ).execute()
    
    if not result.data:
        return GeoJSONFeatureCollection(features=[])
    
    # For now, return zone metadata (actual polygons would come from separate geometry table)
    features = []
    for zone in result.data:
        # Placeholder - actual implementation would have geometry
        feature = GeoJSONFeature(
            geometry={"type": "Point", "coordinates": [-80.6, 28.4]},  # Placeholder
            properties={
                "zone_code": zone["zone_code"],
                "zone_name": zone.get("zone_name"),
                "color": zone.get("color_hex", "#808080")
            }
        )
        features.append(feature)
    
    return GeoJSONFeatureCollection(features=features)


@router.get("/parcel/{parcel_id}/geometry")
async def get_parcel_geometry(parcel_id: str):
    """Get full geometry for a specific parcel"""
    supabase = get_supabase()
    
    # Get parcel with geometry
    result = await supabase.table("fl_parcels").select(
        "parcel_id, address, zone_code, geometry, centroid, latitude, longitude"
    ).eq("parcel_id", parcel_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Parcel {parcel_id} not found")
    
    parcel = result.data
    
    # Return as GeoJSON Feature
    return {
        "type": "Feature",
        "geometry": parcel.get("geometry") or {
            "type": "Point",
            "coordinates": [
                float(parcel.get("longitude", -80.6)),
                float(parcel.get("latitude", 28.4))
            ]
        },
        "properties": {
            "parcel_id": parcel["parcel_id"],
            "address": parcel.get("address"),
            "zone_code": parcel.get("zone_code")
        }
    }


@router.post("/session")
async def create_map_session(
    center_lat: float = 28.3922,
    center_lng: float = -80.6077,
    zoom: float = 10
):
    """Create a new map session"""
    import uuid
    
    supabase = get_supabase()
    
    session_id = str(uuid.uuid4())
    
    result = await supabase.table("map_sessions").insert({
        "session_id": session_id,
        "center_lat": center_lat,
        "center_lng": center_lng,
        "zoom_level": zoom
    }).execute()
    
    return {
        "session_id": session_id,
        "center": [center_lng, center_lat],
        "zoom": zoom
    }


@router.put("/session/{session_id}")
async def update_map_session(
    session_id: str,
    center_lat: Optional[float] = None,
    center_lng: Optional[float] = None,
    zoom: Optional[float] = None,
    selected_parcel_id: Optional[str] = None
):
    """Update map session state"""
    supabase = get_supabase()
    
    update_data = {}
    if center_lat is not None:
        update_data["center_lat"] = center_lat
    if center_lng is not None:
        update_data["center_lng"] = center_lng
    if zoom is not None:
        update_data["zoom_level"] = zoom
    if selected_parcel_id is not None:
        update_data["selected_parcel_id"] = selected_parcel_id
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    result = await supabase.table("map_sessions").update(
        update_data
    ).eq("session_id", session_id).execute()
    
    return {"session_id": session_id, "updated": True}


@router.get("/session/{session_id}")
async def get_map_session(session_id: str):
    """Get map session state"""
    supabase = get_supabase()
    
    result = await supabase.table("map_sessions").select(
        "*"
    ).eq("session_id", session_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return result.data
