"""
ZoneWise V3 - CMA Agent
Performs Comparative Market Analysis using Gemini 2.5 Flash.
"""

from typing import Optional
import structlog

from services.llm_router import LLMRouter
from services.supabase_client import get_supabase

logger = structlog.get_logger()


class CMAAgent:
    """Agent for Comparative Market Analysis."""
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.supabase = get_supabase()
    
    async def execute(
        self,
        parcel_id: Optional[str] = None,
        query: Optional[str] = None,
        zoning_data: Optional[dict] = None,
    ) -> dict:
        """Execute CMA analysis."""
        logger.info("CMA agent executing", parcel_id=parcel_id)
        
        result = {
            "comparables": [],
            "estimated_value": None,
            "value_range": {"low": None, "high": None},
            "confidence": 0.0,
            "adjustments": [],
        }
        
        try:
            if parcel_id:
                # Get subject property
                subject = await self._get_subject_property(parcel_id)
                
                if subject:
                    # Find comparables
                    comps = await self._find_comparables(subject, zoning_data)
                    result["comparables"] = comps[:5]  # Top 5 comps
                    
                    # Calculate adjusted values
                    if comps:
                        values = [c.get("adjusted_value", 0) for c in comps if c.get("adjusted_value")]
                        if values:
                            result["estimated_value"] = sum(values) / len(values)
                            result["value_range"] = {
                                "low": min(values),
                                "high": max(values),
                            }
                            result["confidence"] = min(0.95, 0.6 + (len(values) * 0.07))
            
            logger.info("CMA agent completed", comps=len(result["comparables"]))
            
        except Exception as e:
            logger.error("CMA agent error", error=str(e))
            result["error"] = str(e)
        
        return result
    
    async def _get_subject_property(self, parcel_id: str) -> Optional[dict]:
        """Get subject property details."""
        try:
            response = self.supabase.table("fl_parcels").select(
                "id, address, latitude, longitude, lot_sqft, building_sqft, "
                "bedrooms, bathrooms, year_built, zone_code"
            ).eq("id", parcel_id).single().execute()
            return response.data
        except:
            return None
    
    async def _find_comparables(
        self,
        subject: dict,
        zoning_data: Optional[dict] = None,
    ) -> list:
        """Find comparable properties."""
        try:
            # Search criteria based on subject
            query = self.supabase.table("fl_parcels").select(
                "id, address, lot_sqft, building_sqft, bedrooms, bathrooms, "
                "year_built, last_sale_price, last_sale_date"
            ).not_.is_("last_sale_price", "null")
            
            # Filter by similar characteristics
            if subject.get("zone_code"):
                query = query.eq("zone_code", subject["zone_code"])
            
            if subject.get("lot_sqft"):
                min_lot = int(subject["lot_sqft"] * 0.7)
                max_lot = int(subject["lot_sqft"] * 1.3)
                query = query.gte("lot_sqft", min_lot).lte("lot_sqft", max_lot)
            
            query = query.limit(10)
            response = query.execute()
            
            comps = []
            for row in response.data or []:
                adjusted = self._calculate_adjustment(subject, row)
                row["adjusted_value"] = adjusted
                comps.append(row)
            
            # Sort by relevance
            comps.sort(key=lambda x: abs(x.get("lot_sqft", 0) - subject.get("lot_sqft", 0)))
            
            return comps
            
        except Exception as e:
            logger.warning("Comparable search failed", error=str(e))
            return []
    
    def _calculate_adjustment(self, subject: dict, comp: dict) -> Optional[float]:
        """Calculate adjusted value for a comparable."""
        sale_price = comp.get("last_sale_price")
        if not sale_price:
            return None
        
        adjustment = 0
        
        # Lot size adjustment ($5/sqft)
        lot_diff = (subject.get("lot_sqft", 0) - comp.get("lot_sqft", 0))
        adjustment += lot_diff * 5
        
        # Building size adjustment ($100/sqft)
        bldg_diff = (subject.get("building_sqft", 0) - comp.get("building_sqft", 0))
        adjustment += bldg_diff * 100
        
        # Bedroom adjustment ($10,000/bedroom)
        bed_diff = (subject.get("bedrooms", 0) - comp.get("bedrooms", 0))
        adjustment += bed_diff * 10000
        
        return sale_price + adjustment
