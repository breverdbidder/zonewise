"""
ZoneWise FastAPI Application
REST API for AI chatbot
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
import time
from typing import Optional

from src.models import ChatRequest, ChatResponse
from src.workflow import run_chatbot
from src.utils.database import (
    store_conversation,
    store_message,
    get_conversation_history,
    update_conversation_stats
)
from config.settings import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(settings.LOG_LEVEL),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False
)

logger = structlog.get_logger()


# ============================================================================
# LIFESPAN CONTEXT MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("starting_zonewise_api", version=settings.APP_VERSION)
    
    # Startup
    logger.info("api_ready", host=settings.HOST, port=settings.PORT)
    
    yield
    
    # Shutdown
    logger.info("shutting_down_zonewise_api")


# ============================================================================
# CREATE APP
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered conversational zoning intelligence for Brevard County, Florida",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()
    
    logger.info(
        "request_start",
        method=request.method,
        url=str(request.url),
        client=request.client.host if request.client else None
    )
    
    response = await call_next(request)
    
    duration_ms = int((time.time() - start_time) * 1000)
    
    logger.info(
        "request_complete",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration_ms=duration_ms
    )
    
    return response


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# ============================================================================
# CHAT ENDPOINT (PRIMARY)
# ============================================================================

@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chatbot endpoint
    
    Send a message to ZoneWise AI and get a response.
    
    **Request:**
    - message: Your zoning question (1-2000 characters)
    - session_id: Unique session identifier for conversation continuity
    - context: Optional additional context
    
    **Response:**
    - response: AI-generated answer
    - suggestions: Follow-up action suggestions (3-5)
    - confidence: Response confidence score (0.0-1.0)
    - intent: Classified user intent
    - entities: Extracted structured entities
    - response_time_ms: Response generation time
    
    **Example:**
    ```
    POST /api/v1/chat
    {
        "message": "Can I build apartments in Melbourne?",
        "session_id": "session_abc123"
    }
    ```
    """
    logger.info(
        "chat_request_received",
        session_id=request.session_id,
        message_length=len(request.message)
    )
    
    try:
        # Get conversation history from database
        conversation_history = await get_conversation_history(request.session_id)
        
        # Get current property context (if exists)
        current_property = request.context.get("current_property") if request.context else None
        
        # Run chatbot workflow
        result = await run_chatbot(
            user_message=request.message,
            session_id=request.session_id,
            conversation_history=conversation_history,
            current_property=current_property
        )
        
        # Store conversation in database (async, don't wait)
        await store_conversation_and_messages(
            session_id=request.session_id,
            user_message=request.message,
            assistant_response=result["response"],
            intent=result["intent"],
            entities=result["entities"],
            confidence=result["confidence"],
            response_time_ms=result["response_time_ms"]
        )
        
        # Return response
        return ChatResponse(
            response=result["response"],
            suggestions=result["suggestions"],
            confidence=result["confidence"],
            intent=result["intent"],
            entities=result["entities"],
            response_time_ms=result["response_time_ms"],
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error("chat_endpoint_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot error: {str(e)}"
        )


# ============================================================================
# FEEDBACK ENDPOINT
# ============================================================================

@app.post("/api/v1/feedback", tags=["Chat"])
async def submit_feedback(
    session_id: str,
    message_id: str,
    feedback_type: str,  # thumbs_up, thumbs_down, report
    feedback_text: Optional[str] = None
):
    """
    Submit feedback on a chatbot response
    
    **Parameters:**
    - session_id: Conversation session ID
    - message_id: Specific message ID
    - feedback_type: thumbs_up, thumbs_down, or report
    - feedback_text: Optional detailed feedback
    
    **Example:**
    ```
    POST /api/v1/feedback
    {
        "session_id": "session_abc123",
        "message_id": "msg_xyz789",
        "feedback_type": "thumbs_up"
    }
    ```
    """
    logger.info("feedback_received", session_id=session_id, type=feedback_type)
    
    try:
        # Store feedback in database
        from src.utils.database import store_feedback
        
        await store_feedback(
            session_id=session_id,
            message_id=message_id,
            feedback_type=feedback_type,
            feedback_text=feedback_text
        )
        
        return {"status": "success", "message": "Feedback recorded"}
        
    except Exception as e:
        logger.error("feedback_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback storage error: {str(e)}"
        )


# ============================================================================
# CONVERSATION HISTORY ENDPOINT
# ============================================================================

@app.get("/api/v1/conversations/{session_id}", tags=["Chat"])
async def get_conversation(session_id: str):
    """
    Retrieve conversation history for a session
    
    **Parameters:**
    - session_id: Conversation session ID
    
    **Returns:**
    - messages: List of all messages in conversation
    - metadata: Conversation statistics
    """
    logger.info("fetching_conversation", session_id=session_id)
    
    try:
        history = await get_conversation_history(session_id)
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": history
        }
        
    except Exception as e:
        logger.error("conversation_fetch_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found: {str(e)}"
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def store_conversation_and_messages(
    session_id: str,
    user_message: str,
    assistant_response: str,
    intent: Optional[str],
    entities: dict,
    confidence: float,
    response_time_ms: int
):
    """Store conversation and messages in database"""
    try:
        # Ensure conversation exists
        conversation_id = await store_conversation(session_id)
        
        # Store user message
        await store_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            intent=None,
            entities=entities,
            response_time_ms=None,
            confidence=None
        )
        
        # Store assistant message
        await store_message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_response,
            intent=intent,
            entities=entities,
            response_time_ms=response_time_ms,
            confidence=confidence
        )
        
        # Update conversation stats
        await update_conversation_stats(conversation_id)
        
        logger.info("conversation_stored", session_id=session_id)
        
    except Exception as e:
        logger.error("conversation_storage_error", error=str(e))
        # Don't raise - storage failure shouldn't break chat


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
