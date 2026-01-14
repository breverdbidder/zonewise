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
    from compliance_agent import analyze_compliance
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

# Initialize FastAPI
app = FastAPI(
    title="ZoneWise API",
    description="Property zoning compliance analysis for Brevard County jurisdictions",
    version="1.0.0",
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


# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "ZoneWise API",
        "version": "1.0.0",
        "description": "Property zoning compliance analysis",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    # TODO: Implement actual health checks
    supabase_url = os.getenv("SUPABASE_URL")
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        supabase_connected=bool(supabase_url),
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


@app.get("/api/v1/jurisdictions", tags=["Reference"])
async def list_jurisdictions():
    """
    List supported jurisdictions
    
    Returns list of cities/counties with available zoning data
    """
    return {
        "jurisdictions": [
            {
                "name": "Indian Harbour Beach",
                "type": "city",
                "districts": 16,
                "coverage": "complete"
            },
            {
                "name": "Melbourne",
                "type": "city",
                "districts": 11,
                "coverage": "complete"
            },
            {
                "name": "Satellite Beach",
                "type": "city",
                "districts": 10,
                "coverage": "complete"
            },
            {
                "name": "Brevard County",
                "type": "county",
                "districts": 0,
                "coverage": "partial"
            }
        ],
        "total_supported": 4,
        "coming_soon": [
            "Titusville",
            "Cocoa",
            "Cocoa Beach",
            "Cape Canaveral",
            "Rockledge",
            "Palm Bay",
            "West Melbourne"
        ]
    }


# Run with: uvicorn zonewise_api:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "zonewise_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
