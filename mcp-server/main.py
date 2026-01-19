"""
ZoneWise MCP Server
FastAPI-based zoning intelligence API for Brevard County, Florida
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import httpx
import json
import os
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI(
    title="ZoneWise MCP Server",
    description="Zoning Intelligence API for Brevard County, Florida",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def supabase_query(endpoint: str, params: dict = None):
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

def parse_dims(description: str):
    if not description or "<!--DIMS:" not in description:
        return None
    try:
        start = description.index("<!--DIMS:") + 9
        end = description.index("-->", start)
        return json.loads(description[start:end])
    except:
        return None

@app.get("/")
async def root():
    return {
        "name": "ZoneWise MCP Server",
        "version": "1.0.0",
        "status": "operational",
        "coverage": {
            "county": "Brevard",
            "state": "Florida",
            "jurisdictions": 17,
            "districts": 273
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/jurisdictions")
async def list_jurisdictions():
    data = await supabase_query("jurisdictions", {"county": "eq.Brevard", "order": "id"})
    return data

@app.get("/districts")
async def list_districts(
    jurisdiction_id: Optional[int] = Query(None),
    limit: int = Query(50, le=273)
):
    params = {"order": "jurisdiction_id,code", "limit": str(limit)}
    if jurisdiction_id:
        params["jurisdiction_id"] = f"eq.{jurisdiction_id}"
    data = await supabase_query("zoning_districts", params)
    for d in data:
        d["dims"] = parse_dims(d.get("description"))
    return data

@app.get("/dims/{jurisdiction}/{code}")
async def get_dims(jurisdiction: str, code: str):
    jur_data = await supabase_query("jurisdictions", {
        "name": f"ilike.{jurisdiction}",
        "county": "eq.Brevard"
    })
    if not jur_data:
        raise HTTPException(status_code=404, detail=f"Jurisdiction '{jurisdiction}' not found")
    
    jur_id = jur_data[0]["id"]
    district_data = await supabase_query("zoning_districts", {
        "jurisdiction_id": f"eq.{jur_id}",
        "code": f"eq.{code}"
    })
    if not district_data:
        raise HTTPException(status_code=404, detail=f"District '{code}' not found")
    
    district = district_data[0]
    dims = parse_dims(district.get("description"))
    return {
        "jurisdiction": jurisdiction,
        "code": code,
        "name": district["name"],
        "dimensional_standards": dims
    }

@app.get("/search")
async def search_districts(q: str = Query(..., min_length=2)):
    params = {
        "or": f"(code.ilike.%{q}%,name.ilike.%{q}%)",
        "order": "jurisdiction_id,code",
        "limit": "50"
    }
    data = await supabase_query("zoning_districts", params)
    for d in data:
        d["dims"] = parse_dims(d.get("description"))
    return {"query": q, "count": len(data), "results": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
