"""
ZoneWise V3 - Zoning Agent
Specializes in zone lookup, rules interpretation, and dimensional standards.
Uses Gemini 2.5 Flash for cost-effective processing.
"""

from typing import Optional
import structlog

from services.llm_router import LLMRouter
from services.supabase_client import get_supabase

logger = structlog.get_logger()


class ZoningAgent:
    """
    Agent specialized in zoning intelligence.
    
    Capabilities:
    - Zone code lookup by parcel ID or address
    - Dimensional standards (setbacks, FAR, height)
    - Allowed uses (by-right, conditional, prohibited)
    - Overlay districts and special conditions
    """
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.supabase = get_supabase()
    
    async def execute(
        self,
        parcel_id: Optional[str] = None,
        query: Optional[str] = None,
        entities: Optional[dict] = None,
    ) -> dict:
        """
        Execute zoning analysis.
        
        Args:
            parcel_id: Parcel ID to lookup
            query: Original user query for context
            entities: Extracted entities from coordinator
        
        Returns:
            Dict with zoning information
        """
        logger.info("Zoning agent executing", parcel_id=parcel_id)
        
        result = {
            "zone_code": None,
            "zone_name": None,
            "zone_category": None,
            "jurisdiction": None,
            "dimensional_standards": {},
            "allowed_uses": {},
            "overlays": [],
            "source": "database",
        }
        
        try:
            # Step 1: Get parcel zoning from database
            if parcel_id:
                zoning = await self._lookup_parcel_zoning(parcel_id)
                if zoning:
                    result.update(zoning)
            
            # Step 2: Get dimensional standards
            if result["zone_code"]:
                standards = await self._get_dimensional_standards(
                    result["zone_code"],
                    result["jurisdiction"],
                )
                result["dimensional_standards"] = standards
            
            # Step 3: Get allowed uses
            if result["zone_code"]:
                uses = await self._get_allowed_uses(
                    result["zone_code"],
                    result["jurisdiction"],
                )
                result["allowed_uses"] = uses
            
            # Step 4: Check for overlays
            if parcel_id:
                overlays = await self._check_overlays(parcel_id)
                result["overlays"] = overlays
            
            logger.info(
                "Zoning agent completed",
                zone_code=result["zone_code"],
                has_standards=bool(result["dimensional_standards"]),
            )
            
        except Exception as e:
            logger.error("Zoning agent error", error=str(e))
            result["error"] = str(e)
        
        return result
    
    async def _lookup_parcel_zoning(self, parcel_id: str) -> Optional[dict]:
        """Lookup zoning for a parcel from database."""
        try:
            response = self.supabase.table("fl_parcels").select(
                "zone_code, zone_category, jurisdiction"
            ).eq("id", parcel_id).single().execute()
            
            if response.data:
                return {
                    "zone_code": response.data.get("zone_code"),
                    "zone_category": response.data.get("zone_category"),
                    "jurisdiction": response.data.get("jurisdiction"),
                }
        except Exception as e:
            logger.warning("Parcel zoning lookup failed", error=str(e))
        
        return None
    
    async def _get_dimensional_standards(
        self,
        zone_code: str,
        jurisdiction: Optional[str] = None,
    ) -> dict:
        """Get dimensional standards for a zone."""
        try:
            query = self.supabase.table("fl_zoning_districts").select(
                "min_lot_size, min_lot_width, max_density, max_height, max_far, "
                "front_setback, side_setback, rear_setback, max_lot_coverage"
            ).eq("zone_code", zone_code)
            
            if jurisdiction:
                query = query.eq("jurisdiction", jurisdiction)
            
            response = query.single().execute()
            
            if response.data:
                return {
                    "min_lot_size": response.data.get("min_lot_size"),
                    "min_lot_width": response.data.get("min_lot_width"),
                    "max_density": response.data.get("max_density"),
                    "max_height": response.data.get("max_height"),
                    "max_far": response.data.get("max_far"),
                    "setbacks": {
                        "front": response.data.get("front_setback"),
                        "side": response.data.get("side_setback"),
                        "rear": response.data.get("rear_setback"),
                    },
                    "max_lot_coverage": response.data.get("max_lot_coverage"),
                }
        except Exception as e:
            logger.warning("Dimensional standards lookup failed", error=str(e))
        
        return {}
    
    async def _get_allowed_uses(
        self,
        zone_code: str,
        jurisdiction: Optional[str] = None,
    ) -> dict:
        """Get allowed uses for a zone."""
        try:
            query = self.supabase.table("fl_allowed_uses").select(
                "use_type, permission_type"
            ).eq("zone_code", zone_code)
            
            if jurisdiction:
                query = query.eq("jurisdiction", jurisdiction)
            
            response = query.execute()
            
            uses = {"by_right": [], "conditional": [], "prohibited": []}
            
            for row in response.data or []:
                permission = row.get("permission_type", "").lower()
                use_type = row.get("use_type", "")
                
                if permission in ["by_right", "permitted", "p"]:
                    uses["by_right"].append(use_type)
                elif permission in ["conditional", "cup", "c"]:
                    uses["conditional"].append(use_type)
                elif permission in ["prohibited", "not_allowed", "x"]:
                    uses["prohibited"].append(use_type)
            
            return uses
            
        except Exception as e:
            logger.warning("Allowed uses lookup failed", error=str(e))
        
        return {"by_right": [], "conditional": [], "prohibited": []}
    
    async def _check_overlays(self, parcel_id: str) -> list:
        """Check for overlay districts affecting the parcel."""
        try:
            response = self.supabase.table("fl_overlay_districts").select(
                "overlay_code, overlay_name, restrictions"
            ).contains("parcel_ids", [parcel_id]).execute()
            
            return [
                {
                    "code": row.get("overlay_code"),
                    "name": row.get("overlay_name"),
                    "restrictions": row.get("restrictions"),
                }
                for row in response.data or []
            ]
        except Exception as e:
            logger.warning("Overlay check failed", error=str(e))
        
        return []
