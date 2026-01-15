"""
ZoneWise FastAPI Application
Property zoning compliance analysis API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import os
import sys

# Add src/agents to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "agents"))

try:
    from src.agents.compliance_agent import analyze_compliance
except ImportError:
    # Fallback for development
    def analyze_compliance(address: str) -> Dict[str, Any]:
        return {
            "address": address,
            "status": "ERROR",
            "confidence": 0,
            "violations": [{"type": "IMPORT_ERROR", "message": "Agent not available"}],
            "recommendations": [],
            "property_data": None,
            "zoning_data": None
        }

# Supabase client initialization
try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_KEY else None
except Exception:
    supabase_client = None

# Initialize FastAPI
app = FastAPI(
    title="ZoneWise API",
    description="Property zoning compliance analysis for Brevard County jurisdictions",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalyzeRequest(BaseModel):
    address: str = Field(..., description="Full property address including city and state")
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "798 Ocean Dr, Satellite Beach, FL"
            }
        }


class ViolationDetail(BaseModel):
    type: str
    message: str
    severity: Optional[str] = None


class PropertyData(BaseModel):
    parcel_id: Optional[str]
    owner: Optional[str]
    city: Optional[str]
    lot_size: Optional[int]
    building_area: Optional[int]
    use_code: Optional[str]
    year_built: Optional[int]


class AnalyzeResponse(BaseModel):
    address: str
    status: str = Field(..., description="COMPLIANT, NON_COMPLIANT, or MANUAL_REVIEW")
    confidence: int = Field(..., ge=0, le=100, description="Confidence percentage")
    violations: List[ViolationDetail]
    recommendations: List[str]
    property_data: Optional[PropertyData]
    zoning_data: Optional[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "798 Ocean Dr, Satellite Beach, FL",
                "status": "COMPLIANT",
                "confidence": 95,
                "violations": [],
                "recommendations": [],
                "property_data": {
                    "parcel_id": "2401234",
                    "owner": "John Doe",
                    "city": "Satellite Beach",
                    "lot_size": 7500,
                    "building_area": 2000,
                    "use_code": "0100",
                    "year_built": 1985
                },
                "zoning_data": {
                    "district": "R-1",
                    "min_lot_size": 6000,
                    "max_coverage": 40
                }
            }
        }


class HealthResponse(BaseModel):
    status: str
    version: str
    supabase_connected: bool
    bcpao_api_available: bool


class JurisdictionInfo(BaseModel):
    id: int
    name: str
    type: str
    districts: int
    coverage: str


class JurisdictionsResponse(BaseModel):
    jurisdictions: List[JurisdictionInfo]
    total_supported: int
    total_districts: int


# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "ZoneWise API",
        "version": "1.1.0",
        "description": "Property zoning compliance analysis for all 17 Brevard County jurisdictions",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    supabase_connected = False
    
    if supabase_client:
        try:
            # Test Supabase connection
            supabase_client.table("jurisdictions").select("id").limit(1).execute()
            supabase_connected = True
        except Exception:
            pass
    
    return HealthResponse(
        status="healthy",
        version="1.1.0",
        supabase_connected=supabase_connected,
        bcpao_api_available=True  # Assume available unless checked
    )


@app.post("/api/v1/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_property(request: AnalyzeRequest):
    """
    Analyze property compliance with local zoning ordinances
    
    Returns compliance status, violations, and recommendations
    """
    try:
        # Run compliance analysis
        result = analyze_compliance(request.address)
        
        # Convert to response model
        return AnalyzeResponse(
            address=result["address"],
            status=result["status"],
            confidence=result["confidence"],
            violations=[ViolationDetail(**v) for v in result["violations"]],
            recommendations=result["recommendations"],
            property_data=PropertyData(**result["property_data"]) if result.get("property_data") else None,
            zoning_data=result.get("zoning_data")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/api/v1/jurisdictions", response_model=JurisdictionsResponse, tags=["Reference"])
async def list_jurisdictions():
    """
    List supported jurisdictions
    
    Returns list of all 17 Brevard County cities/counties with available zoning data,
    dynamically queried from Supabase.
    """
    if not supabase_client:
        # Fallback if Supabase not available
        return JurisdictionsResponse(
            jurisdictions=[],
            total_supported=0,
            total_districts=0
        )
    
    try:
        # Get jurisdictions from database
        jur_result = supabase_client.table("jurisdictions").select("id, name").execute()
        jurisdictions = {j["id"]: j["name"] for j in jur_result.data}
        
        # Get district counts per jurisdiction
        district_result = supabase_client.table("zoning_districts").select("jurisdiction_id").execute()
        
        from collections import Counter
        district_counts = Counter(d["jurisdiction_id"] for d in district_result.data)
        
        # Build response
        jur_list = []
        total_districts = 0
        
        for jid in sorted(jurisdictions.keys()):
            name = jurisdictions[jid]
            count = district_counts.get(jid, 0)
            total_districts += count
            
            # Determine type (county vs city)
            jur_type = "county" if "county" in name.lower() else "city"
            
            # Determine coverage status
            if count >= 10:
                coverage = "complete"
            elif count > 0:
                coverage = "partial"
            else:
                coverage = "pending"
            
            jur_list.append(JurisdictionInfo(
                id=jid,
                name=name,
                type=jur_type,
                districts=count,
                coverage=coverage
            ))
        
        return JurisdictionsResponse(
            jurisdictions=jur_list,
            total_supported=len([j for j in jur_list if j.districts > 0]),
            total_districts=total_districts
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch jurisdictions: {str(e)}"
        )


@app.get("/api/v1/districts/{jurisdiction_id}", tags=["Reference"])
async def get_districts(jurisdiction_id: int):
    """
    Get all zoning districts for a specific jurisdiction
    
    Returns list of zoning districts with their details
    """
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get jurisdiction name
        jur_result = supabase_client.table("jurisdictions").select("name").eq("id", jurisdiction_id).execute()
        
        if not jur_result.data:
            raise HTTPException(status_code=404, detail=f"Jurisdiction {jurisdiction_id} not found")
        
        jurisdiction_name = jur_result.data[0]["name"]
        
        # Get districts
        district_result = supabase_client.table("zoning_districts")\
            .select("*")\
            .eq("jurisdiction_id", jurisdiction_id)\
            .order("code")\
            .execute()
        
        return {
            "jurisdiction_id": jurisdiction_id,
            "jurisdiction_name": jurisdiction_name,
            "districts": district_result.data,
            "total": len(district_result.data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch districts: {str(e)}"
        )


@app.get("/api/v1/district/{district_code}", tags=["Reference"])
async def lookup_district(district_code: str, jurisdiction_id: Optional[int] = None):
    """
    Look up a specific zoning district by code
    
    Optionally filter by jurisdiction_id if district codes are not unique
    """
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase_client.table("zoning_districts")\
            .select("*, jurisdictions(name)")\
            .eq("code", district_code.upper())
        
        if jurisdiction_id:
            query = query.eq("jurisdiction_id", jurisdiction_id)
        
        result = query.execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail=f"District {district_code} not found")
        
        return {
            "districts": result.data,
            "total": len(result.data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to lookup district: {str(e)}"
        )


# Run with: uvicorn zonewise_api:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "zonewise_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
