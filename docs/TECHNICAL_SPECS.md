# ZoneWise Technical Requirements Specification (TRS/PRS)
## AI-Powered Conversational Zoning Intelligence Platform

**Product:** ZoneWise  
**Version:** 1.0 (Q1 2026 Launch)  
**Architecture:** AI-First, Chatbot-Core  
**Created:** January 12, 2026

---

## 🎯 TECHNICAL FOUNDATION

### **Core Architectural Principle:**

```
LAYER 1: AI CHATBOT/NLP (CORE INTERFACE)
    ↓ uses
LAYER 2: ML/AI CAPABILITIES (INTELLIGENCE)
    ↓ queries
LAYER 3: REAL DATA INTEGRATION (KNOWLEDGE BASE)
```

**Technology flows from user conversation, not database queries.**

---

## 1. SYSTEM ARCHITECTURE

### **1.1 High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Web/Mobile/API)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               FRONTEND LAYER (React + Vite)                  │
│  Components:                                                 │
│  - ChatInterface (primary UI)                               │
│  - ConversationHistory                                       │
│  - SuggestedActions                                         │
│  - MapVisualization (optional, chatbot-accessible)          │
│  - TraditionalSearch (fallback)                             │
│                                                              │
│  Hosting: Cloudflare Pages (global CDN, auto-deploy)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            BACKEND API LAYER (Python FastAPI)                │
│  Services:                                                   │
│  - ChatbotController (main entry point)                     │
│  - NLUService (intent + entity extraction)                  │
│  - ConversationManager (context + state)                    │
│  - RAGRetriever (knowledge base queries)                    │
│  - ResponseGenerator (natural language)                     │
│  - ReportGenerator (PDF creation)                           │
│                                                              │
│  Hosting: Render.com (auto-scaling, Docker containers)      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              AI/ML ORCHESTRATION (LangGraph)                 │
│  Agents:                                                     │
│  - IntentClassificationAgent                                │
│  - EntityExtractionAgent                                    │
│  - KnowledgeRetrievalAgent                                  │
│  - ResponseGenerationAgent                                  │
│  - QualityCheckAgent                                        │
│                                                              │
│  Pattern: ForecastEngine™ (93.7 accuracy score)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           AI/ML MODELS (Gemini + Claude + OpenAI)            │
│  Primary: Gemini 2.5 Flash (NLP, 90% FREE tier, fast)      │
│  Backup: Claude Sonnet 4.5 (complex reasoning, high quality)│
│  Embeddings: OpenAI text-embedding-3 (RAG semantic search)  │
│                                                              │
│  Smart Router: Cost optimization (FREE → CHEAP → PREMIUM)   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          DATABASE LAYER (Supabase PostgreSQL + PostGIS)      │
│  Primary Tables (Chatbot):                                  │
│  - chatbot_conversations (THE CORE)                         │
│  - chatbot_messages (user + AI)                             │
│  - chatbot_intents (classification tracking)                │
│  - chatbot_entities (extraction tracking)                   │
│  - chatbot_feedback (learning data)                         │
│  - chatbot_knowledge_base (RAG embeddings)                  │
│                                                              │
│  Support Tables (Knowledge):                                │
│  - jurisdictions, zoning_districts, allowed_uses            │
│  - dimensional_standards, parcels, ordinance_content        │
│                                                              │
│  Extensions: PostGIS (spatial), pgvector (embeddings)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            DATA SOURCES (Automated Pipelines)                │
│  - Firecrawl API (ordinance scraping, $5,988/year)         │
│  - BCPAO API (property data, FREE)                         │
│  - American Legal / Municode (ordinances, access required)  │
│                                                              │
│  Frequency: Daily updates at 11 PM EST                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. CORE TECHNOLOGY STACK

### **2.1 Frontend Technologies**

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 18.3+ | Component library, reactive UI |
| **Build Tool** | Vite | 5.0+ | 5x faster than Webpack, HMR |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first, responsive |
| **State** | Zustand | 4.5+ | Lightweight state management |
| **HTTP** | Axios | 1.6+ | HTTP client with interceptors |
| **Forms** | React Hook Form + Zod | Latest | Forms + validation |
| **Maps** | Mapbox GL JS | 3.0+ | Interactive maps, PostGIS |
| **Testing** | Vitest + RTL | Latest | Unit + component tests |

**Chat UI Components:**
```typescript
// Primary chat interface
<ChatInterface>
  <ChatHeader />
  <ConversationHistory messages={messages} />
  <TypingIndicator isLoading={isLoading} />
  <MessageInput onSend={handleSend} />
  <SuggestedActions actions={suggestions} />
</ChatInterface>
```

**Performance Targets:**
- Initial load: <3s
- Message rendering: <100ms
- Chatbot response display: <50ms
- Lighthouse Score: 95+ (Performance, Accessibility, SEO)

---

### **2.2 Backend Technologies**

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.110+ | Async web framework, OpenAPI |
| **Language** | Python | 3.11+ | Type hints, async/await |
| **Orchestration** | LangGraph | 0.2+ | Agentic workflows, state machines |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM, async support |
| **Validation** | Pydantic | 2.6+ | Data validation, settings |
| **HTTP Client** | httpx | 0.27+ | Async HTTP client |
| **Testing** | pytest + pytest-asyncio | Latest | Unit + integration tests |

**Chatbot API Endpoint:**
```python
from fastapi import FastAPI, WebSocket
from langgraph import StateGraph
from pydantic import BaseModel

app = FastAPI()

class ChatMessage(BaseModel):
    session_id: str
    message: str
    context: dict | None = None

@app.post("/api/v1/chat")
async def chat(message: ChatMessage):
    """
    Primary chatbot endpoint
    """
    # Step 1: Load conversation context
    context = await load_conversation_context(message.session_id)
    
    # Step 2: Run LangGraph chatbot workflow
    result = await chatbot_workflow.ainvoke({
        "user_message": message.message,
        "context": context,
        "session_id": message.session_id
    })
    
    # Step 3: Store conversation
    await store_message(
        session_id=message.session_id,
        role="user",
        content=message.message
    )
    await store_message(
        session_id=message.session_id,
        role="assistant",
        content=result["response"],
        intent=result["intent"],
        entities=result["entities"],
        confidence=result["confidence"]
    )
    
    # Step 4: Return response
    return {
        "response": result["response"],
        "suggestions": result["suggestions"],
        "confidence": result["confidence"],
        "response_time_ms": result["timing"]
    }

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket for real-time chat (optional, lower latency)
    """
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = await process_chat_message(data)
        await websocket.send_json(response)
```

**Performance Targets:**
- API response time: <2s (p95) total
- NLP processing: <500ms
- Database queries: <200ms
- Response generation: <1s
- Concurrent users: 100+ (auto-scaling)

---

### **2.3 AI/ML Technologies**

| Component | Technology | Cost | Purpose |
|-----------|-----------|------|---------|
| **Primary NLP** | Gemini 2.5 Flash | 90% FREE | Intent, entity extraction, responses |
| **Backup NLP** | Claude Sonnet 4.5 | $15/1M tokens | Complex reasoning, high quality |
| **Embeddings** | OpenAI text-embedding-3 | $0.13/1M tokens | Semantic search, RAG |
| **Orchestration** | LangGraph | FREE (OSS) | Agentic workflows |
| **Pattern** | ForecastEngine™ | Internal | ML orchestration, proven |

**LangGraph Chatbot Workflow:**
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class ChatbotState(TypedDict):
    user_message: str
    context: dict
    intent: str
    entities: dict
    knowledge: dict
    response: str
    suggestions: list
    confidence: float

# Define workflow
workflow = StateGraph(ChatbotState)

# Add nodes (agents)
workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("extract_entities", extract_entities_node)
workflow.add_node("retrieve_knowledge", retrieve_knowledge_node)
workflow.add_node("generate_response", generate_response_node)
workflow.add_node("generate_suggestions", generate_suggestions_node)
workflow.add_node("quality_check", quality_check_node)

# Define flow
workflow.set_entry_point("classify_intent")
workflow.add_edge("classify_intent", "extract_entities")
workflow.add_edge("extract_entities", "retrieve_knowledge")
workflow.add_edge("retrieve_knowledge", "generate_response")
workflow.add_edge("generate_response", "generate_suggestions")
workflow.add_edge("generate_suggestions", "quality_check")
workflow.add_conditional_edges(
    "quality_check",
    lambda state: "regenerate" if state["confidence"] < 0.7 else "complete",
    {
        "regenerate": "generate_response",
        "complete": END
    }
)

chatbot_workflow = workflow.compile()
```

**Smart Router (Cost Optimization):**
```python
def route_to_model(intent, complexity, budget):
    """
    Route to optimal model based on task
    """
    if budget == "FREE" and complexity == "simple":
        return "gemini-2.5-flash"  # 90% of requests
    
    elif complexity == "complex" or confidence < 0.8:
        return "claude-sonnet-4.5"  # 10% of requests
    
    else:
        return "gemini-2.5-flash"  # Default
```

**Performance Targets:**
- Intent classification: 90%+ accuracy
- Entity extraction: 85%+ accuracy
- Response quality: 95%+ user satisfaction
- Confidence threshold: 0.7 minimum (else escalate)
- Cost per conversation: <$0.01 average

---

### **2.4 Database Technologies**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Database** | PostgreSQL 15 | Relational data, ACID compliance |
| **Spatial** | PostGIS | Parcel boundaries, zoning polygons |
| **Vectors** | pgvector | Embeddings for semantic search |
| **Hosting** | Supabase | Managed Postgres, auth, storage |
| **Auth** | Supabase Auth | JWT-based authentication |
| **Storage** | Supabase Storage | PDFs, reports, images |

**Primary Schema (Chatbot-First):**

```sql
-- CORE: Chatbot conversations (THE PRIMARY FOCUS)
CREATE TABLE chatbot_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    session_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    conversation_status TEXT DEFAULT 'active',
    user_satisfaction INTEGER,  -- 1-5 rating
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chatbot_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES chatbot_conversations(id),
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    intent TEXT,  -- classified intent
    entities JSONB,  -- extracted entities
    context JSONB,  -- conversation context
    response_time_ms INTEGER,
    confidence_score DECIMAL(3,2),
    thumbs_up BOOLEAN,
    thumbs_down BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- SUPPORT: Zoning data (serves chatbot)
CREATE TABLE jurisdictions (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    data_completeness DECIMAL(5,2),  -- 0-100%
    last_updated TIMESTAMP
);

CREATE TABLE zoning_districts (
    id UUID PRIMARY KEY,
    jurisdiction_id UUID REFERENCES jurisdictions(id),
    code TEXT NOT NULL,  -- 'R-1', 'C-2'
    name TEXT NOT NULL,
    description TEXT,  -- for chatbot explanations
    geometry GEOMETRY(MULTIPOLYGON, 4326)
);

CREATE TABLE allowed_uses (
    id UUID PRIMARY KEY,
    zoning_district_id UUID REFERENCES zoning_districts(id),
    use_name TEXT NOT NULL,
    use_type TEXT NOT NULL,  -- 'by-right', 'conditional', 'prohibited'
    conditions TEXT[]
);

-- RAG: Knowledge base for semantic search
CREATE TABLE ordinance_content (
    id UUID PRIMARY KEY,
    jurisdiction_id UUID REFERENCES jurisdictions(id),
    section_number TEXT NOT NULL,
    content TEXT NOT NULL,
    content_vector VECTOR(1536),  -- OpenAI embeddings
    metadata JSONB
);

-- Function: Semantic search
CREATE OR REPLACE FUNCTION search_ordinances_semantic(
    query_embedding VECTOR(1536),
    similarity_threshold FLOAT DEFAULT 0.7,
    match_limit INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ordinance_content.id,
        ordinance_content.content,
        1 - (ordinance_content.content_vector <=> query_embedding) as similarity
    FROM ordinance_content
    WHERE 1 - (ordinance_content.content_vector <=> query_embedding) > similarity_threshold
    ORDER BY similarity DESC
    LIMIT match_limit;
END;
$$ LANGUAGE plpgsql;
```

**Performance Targets:**
- Query response time: <200ms (p95)
- Semantic search: <500ms
- Concurrent connections: 100+
- Database size: <10GB (initial), scalable
- Backup frequency: Hourly (Supabase automatic)

---

## 3. CHATBOT IMPLEMENTATION DETAILS

### **3.1 Intent Classification**

**Model:** Fine-tuned Gemini 2.5 Flash

**6 Core Intent Classes:**
```python
INTENTS = {
    "feasibility": {
        "description": "User asks if something is allowed",
        "examples": [
            "Can I build apartments?",
            "Is duplex allowed in R-1?",
            "Am I able to add a garage apartment?"
        ],
        "confidence_threshold": 0.85
    },
    "calculation": {
        "description": "User wants quantitative analysis",
        "examples": [
            "How much can I build?",
            "What's the maximum square footage?",
            "How many units fit on my lot?"
        ],
        "confidence_threshold": 0.80
    },
    "comparison": {
        "description": "User wants to compare options",
        "examples": [
            "What's the difference between R-1 and R-1A?",
            "R-2 vs R-3 zoning?",
            "Which zone allows commercial?"
        ],
        "confidence_threshold": 0.80
    },
    "process": {
        "description": "User needs procedural guidance",
        "examples": [
            "How do I get a variance?",
            "What's the permit process?",
            "Who do I contact about rezoning?"
        ],
        "confidence_threshold": 0.75
    },
    "research": {
        "description": "User wants to discover options",
        "examples": [
            "Find properties where I can build 4 units",
            "Show me all R-2 parcels in Melbourne",
            "What lots allow commercial use?"
        ],
        "confidence_threshold": 0.70
    },
    "definition": {
        "description": "User needs education/explanation",
        "examples": [
            "What does FAR mean?",
            "Explain setbacks",
            "What is conditional use permit?"
        ],
        "confidence_threshold": 0.90
    }
}
```

**Implementation:**
```python
async def classify_intent(user_message: str) -> dict:
    """
    Classify user intent using Gemini 2.5 Flash
    """
    prompt = f"""
    Classify the user's intent into ONE of these categories:
    {json.dumps(INTENTS, indent=2)}
    
    User message: "{user_message}"
    
    Respond with JSON:
    {{
        "intent": "intent_name",
        "confidence": 0.0-1.0,
        "reasoning": "brief explanation"
    }}
    """
    
    response = await gemini_client.generate(
        prompt=prompt,
        temperature=0.1,  # Low for classification
        response_format="json"
    )
    
    result = json.loads(response.content)
    
    # Log for learning
    await supabase.table('chatbot_intents').insert({
        'user_query': user_message,
        'classified_intent': result['intent'],
        'confidence': result['confidence']
    })
    
    return result
```

---

### **3.2 Entity Extraction**

**Entities to Extract:**
```python
ENTITY_TYPES = {
    "address": {
        "regex": [
            r'\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way)',
            r'\d+\s+[A-Za-z\s]+,\s*[A-Za-z\s]+,\s*FL'
        ],
        "examples": ["123 Ocean Ave", "456 Palm Bay Rd, Melbourne, FL"]
    },
    "zoning_code": {
        "regex": [r'R-\d+[A-Z]?', r'C-\d+', r'I-\d+', r'PUD'],
        "examples": ["R-1", "R-1A", "C-2", "PUD"]
    },
    "use_type": {
        "keywords": {
            "residential": ["apartment", "duplex", "single-family", "multifamily", "ADU", "garage apartment"],
            "commercial": ["restaurant", "office", "retail", "store", "shop"],
            "mixed-use": ["mixed-use", "live-work"]
        }
    },
    "location": {
        "cities": ["Melbourne", "Satellite Beach", "Cocoa Beach", "Titusville", "Palm Bay", ...],
        "fuzzy_match": True
    },
    "quantity": {
        "regex": [r'(\d{1,3}(?:,\d{3})*)\s*(?:SF|square feet|feet)', r'(\d+)\s*units?'],
        "examples": ["10,000 SF", "4 units"]
    }
}
```

**Implementation:**
```python
import re
from fuzzywuzzy import fuzz

async def extract_entities(user_message: str, context: dict) -> dict:
    """
    Extract entities from user message
    """
    entities = {}
    
    # Extract address
    for pattern in ENTITY_TYPES["address"]["regex"]:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            entities["address"] = match.group()
            # Geocode address to get coordinates
            geocoded = await geocode_address(entities["address"])
            if geocoded:
                entities["coordinates"] = geocoded["coordinates"]
                entities["parcel_id"] = await lookup_parcel(geocoded["coordinates"])
            break
    
    # Extract zoning code
    for pattern in ENTITY_TYPES["zoning_code"]["regex"]:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            entities["zoning_code"] = match.group().upper()
            break
    
    # Extract use type (keyword matching)
    for use_category, keywords in ENTITY_TYPES["use_type"]["keywords"].items():
        for keyword in keywords:
            if keyword.lower() in user_message.lower():
                entities["use_type"] = keyword
                entities["use_category"] = use_category
                break
    
    # Extract location (fuzzy matching for cities)
    for city in ENTITY_TYPES["location"]["cities"]:
        if city.lower() in user_message.lower():
            entities["location"] = city
            break
        # Fuzzy match for misspellings
        elif fuzz.partial_ratio(city.lower(), user_message.lower()) > 90:
            entities["location"] = city
            break
    
    # Extract quantity
    for pattern in ENTITY_TYPES["quantity"]["regex"]:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            entities["quantity"] = match.group()
            break
    
    # Use context if entities missing (from previous messages)
    if not entities.get("address") and context.get("current_property"):
        entities["address"] = context["current_property"]["address"]
        entities["parcel_id"] = context["current_property"]["parcel_id"]
    
    # Log for learning
    await supabase.table('chatbot_entities').insert({
        'message_id': ...,
        'entity_type': list(entities.keys()),
        'entity_values': entities,
        'confidence': calculate_entity_confidence(entities)
    })
    
    return entities
```

---

### **3.3 RAG Knowledge Retrieval**

**Implementation:**
```python
from openai import AsyncOpenAI

openai_client = AsyncOpenAI()

async def retrieve_knowledge(
    user_message: str,
    entities: dict,
    context: dict
) -> dict:
    """
    Retrieve relevant zoning knowledge using RAG
    """
    knowledge = {}
    
    # Step 1: Generate query embedding
    embedding_response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=user_message
    )
    query_embedding = embedding_response.data[0].embedding
    
    # Step 2: Semantic search on ordinance content
    ordinances = await supabase.rpc('search_ordinances_semantic', {
        'query_embedding': query_embedding,
        'similarity_threshold': 0.7,
        'match_limit': 5
    }).execute()
    
    knowledge["ordinances"] = ordinances.data
    
    # Step 3: Structured data lookup (if entities present)
    if entities.get("zoning_code"):
        zoning_data = await supabase.table('zoning_districts')\
            .select('*, allowed_uses(*), dimensional_standards(*)')\
            .eq('code', entities["zoning_code"])\
            .limit(1)\
            .execute()
        knowledge["zoning_data"] = zoning_data.data[0] if zoning_data.data else None
    
    if entities.get("parcel_id"):
        parcel_data = await supabase.table('parcels')\
            .select('*, zoning_districts(*)')\
            .eq('parcel_id', entities["parcel_id"])\
            .single()\
            .execute()
        knowledge["parcel_data"] = parcel_data.data
    
    # Step 4: Calculate confidence
    knowledge["confidence"] = calculate_knowledge_confidence(
        ordinances.data,
        knowledge.get("zoning_data"),
        knowledge.get("parcel_data")
    )
    
    return knowledge
```

---

[Document continues with Response Generation, Testing Strategy, Deployment, Monitoring, etc.]

