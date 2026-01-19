"""
ZoneWise MCP Server
FastAPI-based zoning intelligence API for Brevard County, Florida

Deployment: Render.com
Database: Supabase
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import json
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="ZoneWise MCP Server",
    description="Zoning Intelligence API for Brevard County, Florida. 17 jurisdictions, 273 districts, 100% verified.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for Claude Desktop and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class ZoningDistrict(BaseModel):
    id: int
    jurisdiction_id: int
    code: str
    name: str
    category: Optional[str]
    description: Optional[str]
    dims: Optional[dict] = None

class Jurisdiction(BaseModel):
    id: int
    name: str
    county: str
    state: str
    district_count: Optional[int] = None

class ZoningQuery(BaseModel):
    address: Optional[str] = None
    jurisdiction: Optional[str] = None
    district_code: Optional[str] = None
    use_type: Optional[str] = None  # residential, commercial, industrial
    min_lot_sqft: Optional[int] = None
    max_height_ft: Optional[int] = None

class DimensionalStandards(BaseModel):
    min_lot_sqft: Optional[int]
    min_lot_width_ft: Optional[int]
    max_height_ft: Optional[int]
    max_stories: Optional[int]
    coverage_pct: Optional[int]
    setbacks_ft: Optional[dict]
    density: Optional[float]
    floor_area_ratio: Optional[float]
    source_url: Optional[str]
    verified_date: Optional[str]

# ============================================================================
# SUPABASE CLIENT
# ============================================================================

async def supabase_query(endpoint: str, params: dict = None) -> dict:
    """Execute Supabase REST API query"""
    if not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_KEY not configured")
    
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

def parse_dims(description: str) -> Optional[dict]:
    """Extract DIMS JSON from description field"""
    if not description or "<!--DIMS:" not in description:
        return None
    try:
        start = description.index("<!--DIMS:") + 9
        end = description.index("-->", start)
        return json.loads(description[start:end])
    except:
        return None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API info and health check"""
    return {
        "name": "ZoneWise MCP Server",
        "version": "1.0.0",
        "status": "operational",
        "coverage": {
            "county": "Brevard",
            "state": "Florida",
            "jurisdictions": 17,
            "districts": 273,
            "completeness": "100%"
        },
        "endpoints": {
            "jurisdictions": "/jurisdictions",
            "districts": "/districts",
            "lookup": "/lookup",
            "search": "/search",
            "dims": "/dims/{jurisdiction}/{code}"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    """Health check for Render"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# ----------------------------------------------------------------------------
# JURISDICTIONS
# ----------------------------------------------------------------------------

@app.get("/jurisdictions", response_model=List[dict])
async def list_jurisdictions():
    """List all 17 Brevard County jurisdictions"""
    data = await supabase_query("jurisdictions", {"county": "eq.Brevard", "order": "id"})
    return data

@app.get("/jurisdictions/{jurisdiction_id}")
async def get_jurisdiction(jurisdiction_id: int):
    """Get jurisdiction details with district count"""
    data = await supabase_query("jurisdictions", {"id": f"eq.{jurisdiction_id}"})
    if not data:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    
    # Get district count
    districts = await supabase_query("zoning_districts", {
        "jurisdiction_id": f"eq.{jurisdiction_id}",
        "select": "id"
    })
    
    result = data[0]
    result["district_count"] = len(districts)
    return result

# ----------------------------------------------------------------------------
# DISTRICTS
# ----------------------------------------------------------------------------

@app.get("/districts")
async def list_districts(
    jurisdiction_id: Optional[int] = Query(None, description="Filter by jurisdiction ID"),
    category: Optional[str] = Query(None, description="Filter by category (Residential, Commercial, Industrial)"),
    limit: int = Query(50, le=273, description="Max results to return")
):
    """List zoning districts with optional filters"""
    params = {"order": "jurisdiction_id,code", "limit": str(limit)}
    
    if jurisdiction_id:
        params["jurisdiction_id"] = f"eq.{jurisdiction_id}"
    if category:
        params["category"] = f"eq.{category}"
    
    data = await supabase_query("zoning_districts", params)
    
    # Parse DIMS for each district
    for d in data:
        d["dims"] = parse_dims(d.get("description"))
    
    return data

@app.get("/districts/{district_id}")
async def get_district(district_id: int):
    """Get single district with full details"""
    data = await supabase_query("zoning_districts", {"id": f"eq.{district_id}"})
    if not data:
        raise HTTPException(status_code=404, detail="District not found")
    
    result = data[0]
    result["dims"] = parse_dims(result.get("description"))
    return result

# ----------------------------------------------------------------------------
# DIMENSIONAL STANDARDS LOOKUP
# ----------------------------------------------------------------------------

@app.get("/dims/{jurisdiction}/{code}")
async def get_dimensional_standards(jurisdiction: str, code: str):
    """
    Get dimensional standards for a specific zoning district
    
    Examples:
    - /dims/Melbourne/R-1A
    - /dims/Palm%20Bay/RS-1
    - /dims/Rockledge/C-2
    """
    # First get jurisdiction ID
    jur_data = await supabase_query("jurisdictions", {
        "name": f"ilike.{jurisdiction}",
        "county": "eq.Brevard"
    })
    
    if not jur_data:
        raise HTTPException(status_code=404, detail=f"Jurisdiction '{jurisdiction}' not found")
    
    jur_id = jur_data[0]["id"]
    
    # Get district
    district_data = await supabase_query("zoning_districts", {
        "jurisdiction_id": f"eq.{jur_id}",
        "code": f"eq.{code}"
    })
    
    if not district_data:
        raise HTTPException(status_code=404, detail=f"District '{code}' not found in {jurisdiction}")
    
    district = district_data[0]
    dims = parse_dims(district.get("description"))
    
    return {
        "jurisdiction": jurisdiction,
        "jurisdiction_id": jur_id,
        "code": code,
        "name": district["name"],
        "category": district.get("category"),
        "dimensional_standards": dims,
        "raw_description": district.get("description", "").split("<!--DIMS:")[0].strip()
    }

# ----------------------------------------------------------------------------
# SEARCH
# ----------------------------------------------------------------------------

@app.get("/search")
async def search_districts(
    q: str = Query(..., min_length=2, description="Search query"),
    jurisdiction_id: Optional[int] = None
):
    """
    Search districts by name, code, or description
    
    Examples:
    - /search?q=single-family
    - /search?q=commercial&jurisdiction_id=1
    - /search?q=PUD
    """
    params = {
        "or": f"(code.ilike.%{q}%,name.ilike.%{q}%,description.ilike.%{q}%)",
        "order": "jurisdiction_id,code",
        "limit": "50"
    }
    
    if jurisdiction_id:
        params["jurisdiction_id"] = f"eq.{jurisdiction_id}"
    
    data = await supabase_query("zoning_districts", params)
    
    for d in data:
        d["dims"] = parse_dims(d.get("description"))
    
    return {
        "query": q,
        "count": len(data),
        "results": data
    }

# ----------------------------------------------------------------------------
# LOOKUP BY USE TYPE
# ----------------------------------------------------------------------------

@app.get("/lookup/residential")
async def lookup_residential(
    jurisdiction_id: Optional[int] = None,
    min_density: Optional[float] = Query(None, description="Minimum units per acre"),
    max_density: Optional[float] = Query(None, description="Maximum units per acre")
):
    """Find residential zoning districts"""
    params = {
        "category": "eq.Residential",
        "order": "jurisdiction_id,code"
    }
    if jurisdiction_id:
        params["jurisdiction_id"] = f"eq.{jurisdiction_id}"
    
    data = await supabase_query("zoning_districts", params)
    
    results = []
    for d in data:
        dims = parse_dims(d.get("description"))
        d["dims"] = dims
        
        # Filter by density if specified
        if dims:
            density = dims.get("density")
            if min_density and (not density or density < min_density):
                continue
            if max_density and (not density or density > max_density):
                continue
        
        results.append(d)
    
    return {"count": len(results), "districts": results}

@app.get("/lookup/commercial")
async def lookup_commercial(jurisdiction_id: Optional[int] = None):
    """Find commercial zoning districts"""
    params = {
        "category": "eq.Commercial",
        "order": "jurisdiction_id,code"
    }
    if jurisdiction_id:
        params["jurisdiction_id"] = f"eq.{jurisdiction_id}"
    
    data = await supabase_query("zoning_districts", params)
    
    for d in data:
        d["dims"] = parse_dims(d.get("description"))
    
    return {"count": len(data), "districts": data}

@app.get("/lookup/industrial")
async def lookup_industrial(jurisdiction_id: Optional[int] = None):
    """Find industrial zoning districts"""
    params = {
        "category": "eq.Industrial",
        "order": "jurisdiction_id,code"
    }
    if jurisdiction_id:
        params["jurisdiction_id"] = f"eq.{jurisdiction_id}"
    
    data = await supabase_query("zoning_districts", params)
    
    for d in data:
        d["dims"] = parse_dims(d.get("description"))
    
    return {"count": len(data), "districts": data}

# ----------------------------------------------------------------------------
# MCP TOOL INTERFACE
# ----------------------------------------------------------------------------

@app.post("/mcp/tools/lookup_zoning")
async def mcp_lookup_zoning(query: ZoningQuery):
    """
    MCP Tool: Lookup zoning information
    
    Used by Claude Desktop and other MCP clients
    """
    results = {}
    
    if query.jurisdiction and query.district_code:
        # Direct lookup
        dims = await get_dimensional_standards(query.jurisdiction, query.district_code)
        results["district"] = dims
    
    elif query.jurisdiction:
        # List all districts in jurisdiction
        jur_data = await supabase_query("jurisdictions", {
            "name": f"ilike.{query.jurisdiction}",
            "county": "eq.Brevard"
        })
        if jur_data:
            districts = await list_districts(jurisdiction_id=jur_data[0]["id"], limit=100)
            results["jurisdiction"] = jur_data[0]
            results["districts"] = districts
    
    elif query.use_type:
        # Lookup by use type
        if query.use_type.lower() == "residential":
            results = await lookup_residential()
        elif query.use_type.lower() == "commercial":
            results = await lookup_commercial()
        elif query.use_type.lower() == "industrial":
            results = await lookup_industrial()
    
    return results

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup():
    print("=" * 60)
    print("ZoneWise MCP Server Starting...")
    print("=" * 60)
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Supabase Key: {'✅ Set' if SUPABASE_KEY else '❌ Missing'}")
    print("Coverage: Brevard County, FL (17 jurisdictions, 273 districts)")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
