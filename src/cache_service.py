"""
ZoneWise Cache Service V1.0
Three-Layer Caching Architecture for Firecrawl Cost Optimization

Layers:
- L1: Jurisdiction Codes (monthly refresh)
- L2: Parcel Cache (90-day refresh)
- L3: Live Firecrawl (cache miss)

Target: 70%+ cache hit rate
Cost Target: $20-40/month (Alpha), $50-83/month (Beta)
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import httpx
from supabase import create_client, Client


class CacheLayer(Enum):
    """Cache layer identifiers"""
    L1 = "L1"  # Jurisdiction codes
    L2 = "L2"  # Parcel cache
    MISS = "MISS"  # Cache miss - live lookup


class LookupType(Enum):
    """Type of zoning lookup"""
    PARCEL = "parcel"
    JURISDICTION = "jurisdiction"
    BULK = "bulk"
    REFRESH = "refresh"


@dataclass
class CacheResult:
    """Result from cache lookup"""
    hit: bool
    layer: CacheLayer
    data: Optional[Dict[str, Any]] = None
    record_id: Optional[str] = None
    

@dataclass
class LookupResult:
    """Complete result from zoning lookup"""
    success: bool
    cache_hit: bool
    cache_layer: CacheLayer
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    firecrawl_cost: float = 0.0
    firecrawl_pages: int = 0
    response_time_ms: int = 0


class ZoneWiseCacheService:
    """
    Three-layer cache service for ZoneWise zoning lookups.
    
    Usage:
        cache = ZoneWiseCacheService()
        result = await cache.lookup_parcel("2835546")
        result = await cache.lookup_jurisdiction("satellite_beach")
    """
    
    # Firecrawl cost estimates (per page)
    FIRECRAWL_COST_PER_PAGE = 0.0053  # Hobby plan: $16/3000 pages
    
    # Cache TTLs
    L1_TTL_DAYS = 30  # Jurisdiction codes
    L2_TTL_DAYS = 90  # Parcel cache
    
    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        firecrawl_api_key: Optional[str] = None
    ):
        """Initialize cache service with Supabase and Firecrawl credentials."""
        self.supabase_url = supabase_url or os.environ.get("ZONEWISE_SUPABASE_URL")
        self.supabase_key = supabase_key or os.environ.get("ZONEWISE_SUPABASE_KEY")
        self.firecrawl_api_key = firecrawl_api_key or os.environ.get("FIRECRAWL_API_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials required")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client connections."""
        await self.http_client.aclose()
    
    # =========================================================================
    # MAIN LOOKUP METHODS
    # =========================================================================
    
    async def lookup_parcel(
        self,
        parcel_id: str,
        force_refresh: bool = False,
        user_id: Optional[str] = None,
        source: str = "api"
    ) -> LookupResult:
        """
        Look up zoning information for a parcel.
        
        Args:
            parcel_id: BCPAO parcel/account number
            force_refresh: Skip cache and fetch fresh data
            user_id: User ID for tracking (Beta)
            source: Request source (api, biddeed_integration, spd_integration, web_ui)
        
        Returns:
            LookupResult with zoning data
        """
        import time
        start_time = time.time()
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cache_result = await self._check_parcel_cache(parcel_id)
            if cache_result.hit:
                # Log cache hit
                await self._log_lookup(
                    lookup_type=LookupType.PARCEL,
                    query_input={"parcel_id": parcel_id},
                    cache_hit=True,
                    cache_layer=cache_result.layer,
                    response_data=cache_result.data,
                    user_id=user_id,
                    source=source
                )
                
                return LookupResult(
                    success=True,
                    cache_hit=True,
                    cache_layer=cache_result.layer,
                    data=cache_result.data,
                    response_time_ms=int((time.time() - start_time) * 1000)
                )
        
        # Cache miss - live lookup via Firecrawl
        try:
            firecrawl_result = await self._firecrawl_parcel_lookup(parcel_id)
            
            # Store in cache
            if firecrawl_result.get("success"):
                await self._store_parcel_cache(parcel_id, firecrawl_result["data"])
            
            # Log lookup
            await self._log_lookup(
                lookup_type=LookupType.PARCEL,
                query_input={"parcel_id": parcel_id},
                cache_hit=False,
                cache_layer=CacheLayer.MISS,
                firecrawl_called=True,
                firecrawl_pages=firecrawl_result.get("pages_scraped", 0),
                firecrawl_cost=firecrawl_result.get("cost_estimate", 0),
                response_data=firecrawl_result.get("data"),
                response_success=firecrawl_result.get("success", False),
                error_message=firecrawl_result.get("error"),
                user_id=user_id,
                source=source
            )
            
            return LookupResult(
                success=firecrawl_result.get("success", False),
                cache_hit=False,
                cache_layer=CacheLayer.MISS,
                data=firecrawl_result.get("data"),
                error=firecrawl_result.get("error"),
                firecrawl_cost=firecrawl_result.get("cost_estimate", 0),
                firecrawl_pages=firecrawl_result.get("pages_scraped", 0),
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            
        except Exception as e:
            return LookupResult(
                success=False,
                cache_hit=False,
                cache_layer=CacheLayer.MISS,
                error=str(e),
                response_time_ms=int((time.time() - start_time) * 1000)
            )
    
    async def lookup_jurisdiction(
        self,
        jurisdiction_id: str,
        force_refresh: bool = False,
        user_id: Optional[str] = None,
        source: str = "api"
    ) -> LookupResult:
        """
        Look up zoning codes for a jurisdiction.
        
        Args:
            jurisdiction_id: Jurisdiction identifier (e.g., "satellite_beach")
            force_refresh: Skip cache and fetch fresh data
            user_id: User ID for tracking
            source: Request source
        
        Returns:
            LookupResult with jurisdiction zoning codes
        """
        import time
        start_time = time.time()
        
        # Check L1 cache
        if not force_refresh:
            cache_result = await self._check_jurisdiction_cache(jurisdiction_id)
            if cache_result.hit:
                await self._log_lookup(
                    lookup_type=LookupType.JURISDICTION,
                    query_input={"jurisdiction_id": jurisdiction_id},
                    cache_hit=True,
                    cache_layer=CacheLayer.L1,
                    response_data=cache_result.data,
                    user_id=user_id,
                    source=source
                )
                
                return LookupResult(
                    success=True,
                    cache_hit=True,
                    cache_layer=CacheLayer.L1,
                    data=cache_result.data,
                    response_time_ms=int((time.time() - start_time) * 1000)
                )
        
        # Cache miss - scrape jurisdiction website
        try:
            firecrawl_result = await self._firecrawl_jurisdiction_lookup(jurisdiction_id)
            
            if firecrawl_result.get("success"):
                await self._store_jurisdiction_cache(jurisdiction_id, firecrawl_result["data"])
            
            await self._log_lookup(
                lookup_type=LookupType.JURISDICTION,
                query_input={"jurisdiction_id": jurisdiction_id},
                cache_hit=False,
                cache_layer=CacheLayer.MISS,
                firecrawl_called=True,
                firecrawl_pages=firecrawl_result.get("pages_scraped", 0),
                firecrawl_cost=firecrawl_result.get("cost_estimate", 0),
                response_data=firecrawl_result.get("data"),
                response_success=firecrawl_result.get("success", False),
                error_message=firecrawl_result.get("error"),
                user_id=user_id,
                source=source
            )
            
            return LookupResult(
                success=firecrawl_result.get("success", False),
                cache_hit=False,
                cache_layer=CacheLayer.MISS,
                data=firecrawl_result.get("data"),
                error=firecrawl_result.get("error"),
                firecrawl_cost=firecrawl_result.get("cost_estimate", 0),
                firecrawl_pages=firecrawl_result.get("pages_scraped", 0),
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            
        except Exception as e:
            return LookupResult(
                success=False,
                cache_hit=False,
                cache_layer=CacheLayer.MISS,
                error=str(e),
                response_time_ms=int((time.time() - start_time) * 1000)
            )
    
    # =========================================================================
    # CACHE CHECK METHODS
    # =========================================================================
    
    async def _check_parcel_cache(self, parcel_id: str) -> CacheResult:
        """Check L2 parcel cache for existing entry."""
        try:
            result = self.supabase.table("zonewise_parcel_cache") \
                .select("*") \
                .eq("parcel_id", parcel_id) \
                .gt("expires_at", datetime.utcnow().isoformat()) \
                .eq("is_stale", False) \
                .single() \
                .execute()
            
            if result.data:
                # Record cache hit
                await self._record_cache_hit("parcel", result.data["id"])
                
                return CacheResult(
                    hit=True,
                    layer=CacheLayer.L2,
                    data=result.data,
                    record_id=result.data["id"]
                )
        except Exception:
            pass  # No cache entry found
        
        return CacheResult(hit=False, layer=CacheLayer.MISS)
    
    async def _check_jurisdiction_cache(self, jurisdiction_id: str) -> CacheResult:
        """Check L1 jurisdiction cache for existing entry."""
        try:
            result = self.supabase.table("zonewise_jurisdiction_codes") \
                .select("*") \
                .eq("jurisdiction_id", jurisdiction_id) \
                .gt("expires_at", datetime.utcnow().isoformat()) \
                .single() \
                .execute()
            
            if result.data and result.data.get("districts"):
                # Only return hit if we have actual data (not just seed)
                await self._record_cache_hit("jurisdiction", result.data["id"])
                
                return CacheResult(
                    hit=True,
                    layer=CacheLayer.L1,
                    data=result.data,
                    record_id=result.data["id"]
                )
        except Exception:
            pass
        
        return CacheResult(hit=False, layer=CacheLayer.MISS)
    
    # =========================================================================
    # CACHE STORAGE METHODS
    # =========================================================================
    
    async def _store_parcel_cache(self, parcel_id: str, data: Dict[str, Any]) -> None:
        """Store parcel data in L2 cache."""
        cache_entry = {
            "parcel_id": parcel_id,
            "account_number": data.get("account_number"),
            "jurisdiction_id": data.get("jurisdiction_id"),
            "address": data.get("address"),
            "city": data.get("city"),
            "zip_code": data.get("zip_code"),
            "zoning_code": data.get("zoning_code"),
            "zoning_description": data.get("zoning_description"),
            "future_land_use": data.get("future_land_use"),
            "overlay_districts": json.dumps(data.get("overlay_districts", [])),
            "min_lot_size": data.get("min_lot_size"),
            "min_lot_width": data.get("min_lot_width"),
            "max_height": data.get("max_height"),
            "front_setback": data.get("front_setback"),
            "rear_setback": data.get("rear_setback"),
            "side_setback": data.get("side_setback"),
            "max_lot_coverage": data.get("max_lot_coverage"),
            "permitted_uses": json.dumps(data.get("permitted_uses", {})),
            "conditional_uses": json.dumps(data.get("conditional_uses", {})),
            "bcpao_url": data.get("bcpao_url"),
            "jurisdiction_code_url": data.get("jurisdiction_code_url"),
            "cached_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=self.L2_TTL_DAYS)).isoformat(),
            "is_stale": False
        }
        
        # Upsert (insert or update)
        self.supabase.table("zonewise_parcel_cache") \
            .upsert(cache_entry, on_conflict="parcel_id") \
            .execute()
    
    async def _store_jurisdiction_cache(self, jurisdiction_id: str, data: Dict[str, Any]) -> None:
        """Store jurisdiction data in L1 cache."""
        cache_entry = {
            "jurisdiction_id": jurisdiction_id,
            "jurisdiction_name": data.get("jurisdiction_name"),
            "districts": json.dumps(data.get("districts", [])),
            "code_document": data.get("code_document"),
            "code_document_url": data.get("code_document_url"),
            "code_last_updated": data.get("code_last_updated"),
            "permitted_uses": json.dumps(data.get("permitted_uses", {})),
            "dimensional_standards": json.dumps(data.get("dimensional_standards", {})),
            "source_url": data.get("source_url"),
            "data_quality_score": data.get("data_quality_score", 50),
            "cached_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=self.L1_TTL_DAYS)).isoformat()
        }
        
        self.supabase.table("zonewise_jurisdiction_codes") \
            .upsert(cache_entry, on_conflict="jurisdiction_id") \
            .execute()
    
    async def _record_cache_hit(self, table_type: str, record_id: str) -> None:
        """Record a cache hit for analytics."""
        table_name = f"zonewise_{table_type}_cache" if table_type == "parcel" else "zonewise_jurisdiction_codes"
        
        self.supabase.rpc("record_cache_hit", {
            "p_table_name": table_type,
            "p_record_id": record_id
        }).execute()
    
    # =========================================================================
    # FIRECRAWL INTEGRATION
    # =========================================================================
    
    async def _firecrawl_parcel_lookup(self, parcel_id: str) -> Dict[str, Any]:
        """
        Perform live Firecrawl lookup for parcel zoning.
        
        Flow:
        1. Query BCPAO for parcel info (address, jurisdiction)
        2. Query jurisdiction website for zoning details
        3. Parse and structure response
        """
        if not self.firecrawl_api_key:
            return {
                "success": False,
                "error": "Firecrawl API key not configured",
                "pages_scraped": 0,
                "cost_estimate": 0
            }
        
        pages_scraped = 0
        
        try:
            # Step 1: Get parcel info from BCPAO
            bcpao_url = f"https://www.bcpao.us/api/v1/search?parcel={parcel_id}"
            bcpao_data = await self._scrape_url(bcpao_url)
            pages_scraped += 1
            
            if not bcpao_data:
                return {
                    "success": False,
                    "error": f"Parcel {parcel_id} not found in BCPAO",
                    "pages_scraped": pages_scraped,
                    "cost_estimate": pages_scraped * self.FIRECRAWL_COST_PER_PAGE
                }
            
            # Extract key info
            parcel_info = self._parse_bcpao_response(bcpao_data, parcel_id)
            
            # Step 2: Get zoning requirements from jurisdiction
            if parcel_info.get("jurisdiction_id"):
                jurisdiction_data = await self._get_jurisdiction_zoning(
                    parcel_info["jurisdiction_id"],
                    parcel_info.get("zoning_code")
                )
                pages_scraped += jurisdiction_data.get("pages_scraped", 0)
                
                # Merge data
                parcel_info.update(jurisdiction_data.get("data", {}))
            
            return {
                "success": True,
                "data": parcel_info,
                "pages_scraped": pages_scraped,
                "cost_estimate": pages_scraped * self.FIRECRAWL_COST_PER_PAGE
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pages_scraped": pages_scraped,
                "cost_estimate": pages_scraped * self.FIRECRAWL_COST_PER_PAGE
            }
    
    async def _firecrawl_jurisdiction_lookup(self, jurisdiction_id: str) -> Dict[str, Any]:
        """Perform live Firecrawl lookup for jurisdiction zoning codes."""
        if not self.firecrawl_api_key:
            return {
                "success": False,
                "error": "Firecrawl API key not configured",
                "pages_scraped": 0,
                "cost_estimate": 0
            }
        
        pages_scraped = 0
        
        try:
            # Get jurisdiction base URL
            result = self.supabase.table("zonewise_jurisdiction_codes") \
                .select("source_url, jurisdiction_name") \
                .eq("jurisdiction_id", jurisdiction_id) \
                .single() \
                .execute()
            
            if not result.data or not result.data.get("source_url"):
                return {
                    "success": False,
                    "error": f"Jurisdiction {jurisdiction_id} not found",
                    "pages_scraped": 0,
                    "cost_estimate": 0
                }
            
            source_url = result.data["source_url"]
            jurisdiction_name = result.data["jurisdiction_name"]
            
            # Scrape zoning code pages
            zoning_data = await self._scrape_url(source_url)
            pages_scraped += 1
            
            # Parse zoning codes (this would need jurisdiction-specific parsing)
            parsed_data = self._parse_jurisdiction_zoning(zoning_data, jurisdiction_id, jurisdiction_name)
            
            return {
                "success": True,
                "data": parsed_data,
                "pages_scraped": pages_scraped,
                "cost_estimate": pages_scraped * self.FIRECRAWL_COST_PER_PAGE
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pages_scraped": pages_scraped,
                "cost_estimate": pages_scraped * self.FIRECRAWL_COST_PER_PAGE
            }
    
    async def _scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a URL using Firecrawl API."""
        response = await self.http_client.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {self.firecrawl_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "url": url,
                "formats": ["markdown", "html"],
                "onlyMainContent": True
            }
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    async def _get_jurisdiction_zoning(
        self,
        jurisdiction_id: str,
        zoning_code: Optional[str]
    ) -> Dict[str, Any]:
        """Get zoning details from jurisdiction for specific code."""
        # Check if we have cached jurisdiction data
        cache_result = await self._check_jurisdiction_cache(jurisdiction_id)
        
        if cache_result.hit and zoning_code:
            # Extract specific zoning code requirements
            dimensional = cache_result.data.get("dimensional_standards", {})
            if isinstance(dimensional, str):
                dimensional = json.loads(dimensional)
            
            code_standards = dimensional.get(zoning_code, {})
            
            return {
                "data": code_standards,
                "pages_scraped": 0
            }
        
        # Would need to scrape - for now return empty
        return {"data": {}, "pages_scraped": 0}
    
    # =========================================================================
    # PARSING HELPERS
    # =========================================================================
    
    def _parse_bcpao_response(self, response: Dict[str, Any], parcel_id: str) -> Dict[str, Any]:
        """Parse BCPAO API response into structured data."""
        # This is a simplified parser - actual implementation would be more robust
        data = response.get("data", {})
        
        return {
            "parcel_id": parcel_id,
            "account_number": data.get("account"),
            "address": data.get("address"),
            "city": data.get("city"),
            "zip_code": data.get("zip"),
            "zoning_code": data.get("zoning"),
            "jurisdiction_id": self._map_city_to_jurisdiction(data.get("city", "")),
            "bcpao_url": f"https://www.bcpao.us/PropertySearch/#/parcel/{parcel_id}"
        }
    
    def _parse_jurisdiction_zoning(
        self,
        response: Dict[str, Any],
        jurisdiction_id: str,
        jurisdiction_name: str
    ) -> Dict[str, Any]:
        """Parse jurisdiction website response into structured zoning data."""
        # Placeholder - actual implementation would parse HTML/markdown
        return {
            "jurisdiction_id": jurisdiction_id,
            "jurisdiction_name": jurisdiction_name,
            "districts": [],
            "permitted_uses": {},
            "dimensional_standards": {},
            "data_quality_score": 50
        }
    
    def _map_city_to_jurisdiction(self, city: str) -> str:
        """Map city name to jurisdiction_id."""
        city_map = {
            "satellite beach": "satellite_beach",
            "indian harbour beach": "indian_harbour_beach",
            "melbourne": "melbourne",
            "palm bay": "palm_bay",
            "cocoa": "cocoa",
            "cocoa beach": "cocoa_beach",
            "titusville": "titusville",
            "rockledge": "rockledge",
            "melbourne beach": "melbourne_beach",
            "indialantic": "indialantic",
            "west melbourne": "west_melbourne",
            "cape canaveral": "cape_canaveral",
            "malabar": "malabar",
            "grant-valkaria": "grant_valkaria",
            "palm shores": "palm_shores",
            "melbourne village": "melbourne_village"
        }
        
        return city_map.get(city.lower().strip(), "brevard_county")
    
    # =========================================================================
    # LOGGING
    # =========================================================================
    
    async def _log_lookup(
        self,
        lookup_type: LookupType,
        query_input: Dict[str, Any],
        cache_hit: bool,
        cache_layer: CacheLayer,
        firecrawl_called: bool = False,
        firecrawl_pages: int = 0,
        firecrawl_cost: float = 0,
        firecrawl_duration_ms: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        response_success: bool = True,
        error_message: Optional[str] = None,
        user_id: Optional[str] = None,
        source: str = "api"
    ) -> None:
        """Log lookup to audit table."""
        log_entry = {
            "lookup_type": lookup_type.value,
            "query_input": json.dumps(query_input),
            "cache_hit": cache_hit,
            "cache_layer": cache_layer.value,
            "firecrawl_called": firecrawl_called,
            "firecrawl_pages_scraped": firecrawl_pages,
            "firecrawl_cost_estimate": firecrawl_cost,
            "firecrawl_duration_ms": firecrawl_duration_ms,
            "response_success": response_success,
            "response_data": json.dumps(response_data) if response_data else None,
            "error_message": error_message,
            "user_id": user_id,
            "source": source
        }
        
        try:
            self.supabase.table("zonewise_lookup_log").insert(log_entry).execute()
        except Exception as e:
            # Don't fail lookup if logging fails
            print(f"Warning: Failed to log lookup: {e}")
    
    # =========================================================================
    # ANALYTICS
    # =========================================================================
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get current cache statistics."""
        result = self.supabase.table("zonewise_cache_stats").select("*").single().execute()
        return result.data if result.data else {}
    
    async def get_cost_summary(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get Firecrawl cost summary for date range."""
        result = self.supabase.rpc("get_firecrawl_cost_summary", {
            "p_start_date": start_date,
            "p_end_date": end_date
        }).execute()
        
        return result.data[0] if result.data else {}


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def lookup_parcel_zoning(parcel_id: str, **kwargs) -> LookupResult:
    """Convenience function for quick parcel lookup."""
    cache = ZoneWiseCacheService()
    try:
        return await cache.lookup_parcel(parcel_id, **kwargs)
    finally:
        await cache.close()


async def lookup_jurisdiction_zoning(jurisdiction_id: str, **kwargs) -> LookupResult:
    """Convenience function for quick jurisdiction lookup."""
    cache = ZoneWiseCacheService()
    try:
        return await cache.lookup_jurisdiction(jurisdiction_id, **kwargs)
    finally:
        await cache.close()


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        if len(sys.argv) < 3:
            print("Usage: python cache_service.py <parcel|jurisdiction> <id>")
            sys.exit(1)
        
        lookup_type = sys.argv[1]
        lookup_id = sys.argv[2]
        
        if lookup_type == "parcel":
            result = await lookup_parcel_zoning(lookup_id)
        elif lookup_type == "jurisdiction":
            result = await lookup_jurisdiction_zoning(lookup_id)
        else:
            print(f"Unknown lookup type: {lookup_type}")
            sys.exit(1)
        
        print(f"\nResult:")
        print(f"  Success: {result.success}")
        print(f"  Cache Hit: {result.cache_hit} (Layer: {result.cache_layer.value})")
        print(f"  Firecrawl Cost: ${result.firecrawl_cost:.4f}")
        print(f"  Response Time: {result.response_time_ms}ms")
        if result.data:
            print(f"  Data: {json.dumps(result.data, indent=2)}")
        if result.error:
            print(f"  Error: {result.error}")
    
    asyncio.run(main())
