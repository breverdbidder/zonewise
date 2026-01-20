"""
ZoneWise V3 - FastAPI Backend
Main application with REST API and WebSocket support.
"""

import os
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

from agents.orchestrator import get_orchestrator, ChatResponse
from services.supabase_client import get_supabase

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)
logger = structlog.get_logger()


# ==========================================
# APPLICATION LIFECYCLE
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting ZoneWise V3 API")
    # Initialize orchestrator on startup
    get_orchestrator()
    yield
    logger.info("Shutting down ZoneWise V3 API")


app = FastAPI(
    title="ZoneWise V3 API",
    description="AI-powered zoning intelligence platform",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://zonewise-v3.pages.dev",
        "https://zonewise.pages.dev",
        os.environ.get("FRONTEND_URL", "*"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# MODELS
# ==========================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    agents: list[str]


class ParcelQuery(BaseModel):
    west: float
    south: float
    east: float
    north: float
    layers: Optional[list[str]] = None
    limit: int = 1000


# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.get("/health", response_model=HealthResponse)
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for deployment verification."""
    return HealthResponse(
        status="ok",
        version="3.0.0",
        agents=["coordinator", "zoning", "cma", "hbu", "ml", "reporter"],
    )


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return AI response.
    
    This is the primary endpoint for the chat interface.
    """
    logger.info("Chat request received", message=request.message[:100])
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get orchestrator
    orchestrator = get_orchestrator()
    
    # Process query
    response = await orchestrator.process_query(
        query=request.message,
        session_id=session_id,
        map_context=request.context.get("map_context") if request.context else None,
        selected_parcel=request.context.get("selected_parcel") if request.context else None,
        conversation_history=request.context.get("history") if request.context else None,
    )
    
    # Log to Supabase
    try:
        supabase = get_supabase()
        supabase.table("chatbot_messages").insert({
            "session_id": session_id,
            "role": "user",
            "content": request.message,
        }).execute()
        supabase.table("chatbot_messages").insert({
            "session_id": session_id,
            "role": "assistant",
            "content": response.content,
            "intent": response.intent,
            "entities": response.entities,
        }).execute()
    except Exception as e:
        logger.warning("Failed to log chat to Supabase", error=str(e))
    
    return response


@app.get("/api/v1/parcels")
async def get_parcels(
    west: float,
    south: float,
    east: float,
    north: float,
    layers: Optional[str] = None,
    limit: int = 1000,
):
    """
    Get parcels within a bounding box for map display.
    Returns GeoJSON FeatureCollection.
    """
    logger.info("Parcel query", bounds=[west, south, east, north])
    
    try:
        supabase = get_supabase()
        
        # Query parcels in bounds
        response = supabase.rpc(
            "get_parcels_in_bounds",
            {
                "west": west,
                "south": south,
                "east": east,
                "north": north,
                "layer_filter": layers,
            }
        ).execute()
        
        # Convert to GeoJSON
        features = []
        for row in response.data or []:
            if row.get("geojson"):
                features.append({
                    "type": "Feature",
                    "id": row.get("id"),
                    "geometry": row.get("geojson"),
                    "properties": {
                        "parcel_id": row.get("parcel_id"),
                        "address": row.get("address"),
                        "zone_code": row.get("zone_code"),
                        "zone_category": row.get("zone_category"),
                        "hbu_score": row.get("hbu_score"),
                        "foreclosure_status": row.get("foreclosure_status"),
                    }
                })
        
        return {
            "type": "FeatureCollection",
            "features": features,
        }
        
    except Exception as e:
        logger.error("Parcel query failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/parcels/{parcel_id}")
async def get_parcel(parcel_id: str):
    """Get detailed information for a single parcel."""
    try:
        supabase = get_supabase()
        
        response = supabase.table("fl_parcels").select(
            "*"
        ).eq("id", parcel_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Parcel not found")
        
        return response.data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Parcel lookup failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analysis/hbu")
async def analyze_hbu(parcel_id: str, include_cma: bool = True, include_ml: bool = True):
    """Run full HBU analysis on a parcel."""
    orchestrator = get_orchestrator()
    
    response = await orchestrator.process_query(
        query=f"Run a complete HBU analysis for parcel {parcel_id}",
        session_id=str(uuid.uuid4()),
        selected_parcel=parcel_id,
    )
    
    return response


# ==========================================
# WEBSOCKET ENDPOINT
# ==========================================

class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info("WebSocket connected", session_id=session_id)
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info("WebSocket disconnected", session_id=session_id)
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat.
    Supports streaming responses.
    """
    await manager.connect(websocket, session_id)
    
    orchestrator = get_orchestrator()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if data.get("type") == "chat":
                message = data.get("payload", {}).get("message", "")
                context = data.get("payload", {}).get("context", {})
                
                logger.info("WebSocket message", session_id=session_id, message=message[:50])
                
                # Send typing indicator
                await manager.send_message(session_id, {
                    "type": "typing",
                    "payload": {"is_typing": True},
                })
                
                # Process query
                response = await orchestrator.process_query(
                    query=message,
                    session_id=session_id,
                    map_context=context.get("map_context"),
                    selected_parcel=context.get("selected_parcel"),
                    conversation_history=context.get("history"),
                )
                
                # Send response
                await manager.send_message(session_id, {
                    "type": "chat",
                    "payload": {
                        "id": response.id,
                        "content": response.content,
                        "intent": response.intent,
                        "confidence": response.confidence,
                        "map_actions": [a.dict() for a in response.map_actions],
                        "suggestions": response.suggestions,
                        "is_complete": True,
                    },
                })
                
            elif data.get("type") == "ping":
                await manager.send_message(session_id, {"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error("WebSocket error", session_id=session_id, error=str(e))
        manager.disconnect(session_id)


# ==========================================
# ERROR HANDLERS
# ==========================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", error=str(exc))
    return {"detail": "Internal server error"}, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=os.environ.get("ENV", "development") == "development",
    )
