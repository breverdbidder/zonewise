# Full Stack Specification: Claude AI for Real Estate

**Version:** 1.0  
**Date:** January 25, 2026  
**Platforms:** ZoneWise | BidDeed.AI | SPD Site Plan Development

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ZONEWISE / BIDDEED.AI / SPD                          │
│                     "Claude AI for Real Estate"                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         FRONTEND LAYER                                  │ │
│  │                                                                         │ │
│  │   ┌─────────────────────────┬─────────────────────────────────────┐   │ │
│  │   │      CHAT PANEL         │         ARTIFACTS PANEL              │   │ │
│  │   │      (Left 40%)         │         (Right 60%)                  │   │ │
│  │   ├─────────────────────────┼─────────────────────────────────────┤   │ │
│  │   │  ChatMode.jsx           │  ArtifactPanel.jsx                  │   │ │
│  │   │  ThinkingDisplay.jsx    │  ZoningReport.jsx                   │   │ │
│  │   │  ModeSwitcher.jsx       │  ParcelMap.jsx                      │   │ │
│  │   │  StreamingMessage.jsx   │  PropertyCard.jsx                   │   │ │
│  │   │  CitationDisplay.jsx    │  AuctionAnalysis.jsx                │   │ │
│  │   └─────────────────────────┴─────────────────────────────────────┘   │ │
│  │                                                                         │ │
│  │   Framework: React 18 + Vite                                            │ │
│  │   Styling: TailwindCSS + Shadcn/ui                                      │ │
│  │   Deploy: Cloudflare Pages                                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         API LAYER                                       │ │
│  │                                                                         │ │
│  │   Supabase Edge Functions (Deno)                                        │ │
│  │   ├── POST /api/chat        → LiteLLM routing                          │ │
│  │   ├── GET  /api/zoning      → ZoneWise queries                         │ │
│  │   ├── GET  /api/parcels     → BCPAO integration                        │ │
│  │   ├── POST /api/agents      → LangGraph orchestration                  │ │
│  │   ├── POST /api/reports     → PDF/DOCX generation                      │ │
│  │   └── WS   /api/stream      → Real-time streaming                      │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │ 
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      AI ORCHESTRATION LAYER                             │ │
│  │                                                                         │ │
│  │   LangGraph Agents                                                      │ │
│  │   ├── Zoning Agent    → Queries districts, standards, uses             │ │
│  │   ├── Parcel Agent    → Queries BCPAO, properties, owners              │ │
│  │   ├── Report Agent    → Generates PDF, DOCX, analysis                  │ │
│  │   └── Forecast Agent  → BidDeed.AI auction predictions                 │ │
│  │                                                                         │ │
│  │   Smart Router (LiteLLM)                                                │ │
│  │   ├── FREE:        Gemini 2.5 Flash (40-55%)                           │ │
│  │   ├── ULTRA_CHEAP: DeepSeek V3.2 ($0.28/1M)                            │ │
│  │   ├── QUALITY:     Claude Sonnet 4.5                                   │ │
│  │   └── COMPLEX:     Claude Opus 4.5                                     │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         DATA LAYER                                      │ │
│  │                                                                         │ │
│  │   Supabase (PostgreSQL + pgvector)                                      │ │
│  │   ├── jurisdictions         → 17 Brevard → 1,100+ FL                   │ │
│  │   ├── zoning_districts      → 290 → 10,000+                            │ │
│  │   ├── parcel_zones          → 24K → 10M+ FL                            │ │
│  │   ├── sample_properties     → 351K Brevard                             │ │
│  │   ├── permitted_uses        → Growing                                   │ │
│  │   ├── dimensional_standards → Growing                                   │ │
│  │   ├── ordinances            → With embeddings for RAG                  │ │
│  │   └── historical_auctions   → BidDeed.AI data                          │ │
│  │                                                                         │ │
│  │   Supabase Auth (FREE)                                                  │ │
│  │   Supabase Storage (PDFs, images)                                       │ │
│  │   Supabase Realtime (streaming updates)                                 │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                       COMPUTE LAYER                                     │ │
│  │                                                                         │ │
│  │   Modal.com                                                             │ │
│  │   ├── Nightly cron: 11 PM EST                                          │ │
│  │   ├── 67 FL counties parallel                                          │ │
│  │   ├── concurrency_limit: 20                                            │ │
│  │   ├── timeout: 600s                                                    │ │
│  │   └── retries: 3                                                       │ │
│  │                                                                         │ │
│  │   GitHub Actions (CI/CD)                                                │ │
│  │   ├── On push: Test + Deploy                                           │ │
│  │   ├── Nightly: Backup verification                                     │ │
│  │   └── Weekly: Dependency updates                                       │ │
│  │                                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Specification

### Source: Open-claude Fork

**Repository:** https://github.com/Damienchakma/Open-claude  
**License:** MIT

### Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatMode.jsx           # Main chat interface
│   │   │   ├── StreamingMessage.jsx   # Real-time responses
│   │   │   ├── ThinkingDisplay.jsx    # AI reasoning
│   │   │   └── ModeSwitcher.jsx       # Chat|Analyze|Build
│   │   ├── artifacts/
│   │   │   ├── ArtifactPanel.jsx      # Split-screen right
│   │   │   ├── ZoningReport.jsx       # 20-phase analysis
│   │   │   ├── ParcelMap.jsx          # Leaflet map
│   │   │   ├── PropertyCard.jsx       # Owner, value, history
│   │   │   ├── AuctionAnalysis.jsx    # Max bid calculator
│   │   │   └── CitationDisplay.jsx    # Source links
│   │   ├── ui/                        # Shadcn/ui components
│   │   └── layout/
│   │       ├── SplitScreen.jsx        # Main layout
│   │       ├── Header.jsx
│   │       └── Sidebar.jsx
│   ├── hooks/
│   │   ├── useChat.js                 # Chat state management
│   │   ├── useArtifacts.js            # Artifact rendering
│   │   ├── useZoning.js               # Zoning queries
│   │   ├── useParcel.js               # Parcel lookups
│   │   └── useReport.js               # Report generation
│   ├── lib/
│   │   ├── supabase.js                # Supabase client
│   │   ├── litellm.js                 # LLM routing
│   │   ├── langgraph.js               # Agent orchestration
│   │   └── utils.js
│   ├── config/
│   │   ├── agents.js                  # Agent definitions
│   │   └── constants.js
│   └── App.jsx
├── public/
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

### Key Components

#### SplitScreen.jsx
```jsx
const SplitScreen = () => {
  const [chatWidth, setChatWidth] = useState(40); // 40% default
  
  return (
    <div className="flex h-screen">
      <div style={{ width: `${chatWidth}%` }} className="border-r">
        <ChatMode />
      </div>
      <div style={{ width: `${100 - chatWidth}%` }}>
        <ArtifactPanel />
      </div>
      <Resizer onResize={setChatWidth} />
    </div>
  );
};
```

#### ZoningReport.jsx
```jsx
const ZoningReport = ({ parcelId }) => {
  const { data, loading } = useZoning(parcelId);
  
  if (loading) return <Skeleton />;
  
  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold">
        20-Phase Zoning Analysis
      </h2>
      
      {/* Phase 1-5: Core Zoning */}
      <Section title="Zoning Classification">
        <Badge>{data.zone_code}</Badge>
        <p>{data.zone_description}</p>
      </Section>
      
      {/* Phase 6-10: Dimensional Standards */}
      <DimensionalTable standards={data.dimensional} />
      
      {/* Phase 11-15: Uses */}
      <PermittedUses uses={data.permitted} />
      <ConditionalUses uses={data.conditional} />
      
      {/* Phase 16-20: Additional */}
      <OverlayDistricts overlays={data.overlays} />
      <Citations sources={data.sources} />
      
      <DownloadPDF data={data} />
    </div>
  );
};
```

#### ParcelMap.jsx
```jsx
import { MapContainer, TileLayer, Polygon, Popup } from 'react-leaflet';

const ParcelMap = ({ parcelId, center }) => {
  const { boundary, nearby } = useParcel(parcelId);
  
  return (
    <MapContainer center={center} zoom={17}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      
      {/* Main parcel */}
      <Polygon 
        positions={boundary} 
        color="blue" 
        fillOpacity={0.3}
      >
        <Popup>
          <PropertyCard parcelId={parcelId} compact />
        </Popup>
      </Polygon>
      
      {/* Nearby parcels */}
      {nearby.map(p => (
        <Polygon 
          key={p.id}
          positions={p.boundary}
          color="gray"
          fillOpacity={0.1}
        />
      ))}
    </MapContainer>
  );
};
```

### Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Framework | React | 18.x |
| Build | Vite | 5.x |
| Styling | TailwindCSS | 3.x |
| Components | Shadcn/ui | Latest |
| Maps | Leaflet | 1.9.x |
| Charts | Recharts | 2.x |
| Icons | Lucide | Latest |
| State | React Query | 5.x |

---

## API Specification

### Supabase Edge Functions

#### POST /api/chat

```typescript
interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: {
    parcel_id?: string;
    jurisdiction?: string;
  };
}

interface ChatResponse {
  id: string;
  content: string;
  artifacts?: Artifact[];
  citations?: Citation[];
  thinking?: string;
}
```

#### GET /api/zoning

```typescript
// Query by address
GET /api/zoning?address=123+Main+St&city=Melbourne&state=FL

// Query by parcel ID
GET /api/zoning?parcel_id=28-37-35-25-00014

interface ZoningResponse {
  parcel_id: string;
  zone_code: string;
  zone_description: string;
  jurisdiction: string;
  dimensional_standards: DimensionalStandards;
  permitted_uses: string[];
  conditional_uses: string[];
  overlays: Overlay[];
  source_url: string;
}
```

#### GET /api/parcels

```typescript
// Query by parcel ID
GET /api/parcels/28-37-35-25-00014

// Search by owner
GET /api/parcels?owner=SMITH

// Search by address
GET /api/parcels?address=123+Main+St

interface ParcelResponse {
  parcel_id: string;
  tax_account: string;
  owner_name: string;
  site_address: string;
  legal_description: string;
  market_value: number;
  assessed_value: number;
  last_sale_date: string;
  last_sale_price: number;
  building_sqft: number;
  lot_size: number;
  year_built: number;
  photo_url: string;
  geometry: GeoJSON;
}
```

#### POST /api/agents

```typescript
interface AgentRequest {
  agent: 'zoning' | 'parcel' | 'report' | 'forecast';
  task: string;
  context?: Record<string, any>;
}

interface AgentResponse {
  status: 'success' | 'error';
  result: any;
  thinking?: string;
  tool_calls?: ToolCall[];
}
```

#### POST /api/reports

```typescript
interface ReportRequest {
  type: 'zoning_analysis' | 'parcel_summary' | 'auction_analysis';
  format: 'pdf' | 'docx';
  parcel_id: string;
  options?: {
    include_map?: boolean;
    include_photos?: boolean;
    include_comparables?: boolean;
  };
}

interface ReportResponse {
  url: string;
  expires_at: string;
}
```

---

## AI Layer Specification

### LangGraph Agents

```python
from langgraph.graph import StateGraph

# Agent State
class AgentState(TypedDict):
    messages: list
    context: dict
    artifacts: list
    thinking: str

# Zoning Agent
class ZoningAgent:
    """Answers zoning questions using ZoneWise data."""
    
    tools = [
        "query_zoning_districts",
        "query_dimensional_standards", 
        "query_permitted_uses",
        "query_overlays"
    ]
    
    model = "gemini/gemini-2.5-flash"  # FREE tier
    
    def query_zoning_districts(self, jurisdiction: str, zone_code: str):
        """Query zoning_districts table."""
        return supabase.table("zoning_districts")\
            .select("*")\
            .eq("jurisdiction_id", jurisdiction)\
            .eq("zone_code", zone_code)\
            .single()\
            .execute()

# Parcel Agent
class ParcelAgent:
    """Looks up property information from BCPAO."""
    
    tools = [
        "query_parcel",
        "search_by_owner",
        "search_by_address",
        "get_sales_history"
    ]
    
    model = "gemini/gemini-2.5-flash"  # FREE tier

# Report Agent  
class ReportAgent:
    """Generates PDF/DOCX reports."""
    
    tools = [
        "generate_zoning_report",
        "generate_parcel_summary",
        "generate_auction_analysis"
    ]
    
    model = "anthropic/claude-sonnet-4-5"  # QUALITY tier
```

### Smart Router Configuration

```python
from litellm import Router

router = Router(
    model_list=[
        {
            "model_name": "free",
            "litellm_params": {
                "model": "gemini/gemini-2.5-flash",
                "api_key": os.getenv("GEMINI_API_KEY")
            }
        },
        {
            "model_name": "cheap",
            "litellm_params": {
                "model": "deepseek/deepseek-chat",
                "api_key": os.getenv("DEEPSEEK_API_KEY")
            }
        },
        {
            "model_name": "quality",
            "litellm_params": {
                "model": "anthropic/claude-sonnet-4-5",
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            }
        },
        {
            "model_name": "complex",
            "litellm_params": {
                "model": "anthropic/claude-opus-4-5",
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            }
        }
    ],
    routing_strategy="simple-shuffle",
    fallbacks=[
        {"free": ["cheap"]},
        {"cheap": ["quality"]},
        {"quality": ["complex"]}
    ]
)

def route_request(task_type: str) -> str:
    """Route to appropriate model based on task."""
    routing = {
        "simple_query": "free",      # 40-55% of requests
        "data_lookup": "free",
        "summarization": "cheap",
        "report_generation": "quality",
        "complex_analysis": "complex",
        "legal_interpretation": "complex"
    }
    return routing.get(task_type, "free")
```

---

## Data Layer Specification

### Supabase Schema

```sql
-- Jurisdictions
CREATE TABLE jurisdictions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    county TEXT NOT NULL,
    state TEXT DEFAULT 'FL',
    municode_url TEXT,
    gis_endpoint TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Zoning Districts (290 Brevard → 10,000+ FL)
CREATE TABLE zoning_districts (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    zone_code TEXT NOT NULL,
    zone_name TEXT,
    description TEXT,
    category TEXT, -- residential, commercial, industrial, etc.
    min_lot_size NUMERIC,
    max_density NUMERIC,
    max_height NUMERIC,
    front_setback NUMERIC,
    side_setback NUMERIC,
    rear_setback NUMERIC,
    max_lot_coverage NUMERIC,
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, zone_code)
);

-- Parcel Zones (24K → 10M+)
CREATE TABLE parcel_zones (
    id SERIAL PRIMARY KEY,
    parcel_id TEXT NOT NULL,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    zone_code TEXT NOT NULL,
    overlay_codes TEXT[],
    flum_code TEXT,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    source TEXT, -- gis, manual, inferred
    UNIQUE(parcel_id)
);

-- Sample Properties (351K Brevard)
CREATE TABLE sample_properties (
    id SERIAL PRIMARY KEY,
    parcel_id TEXT UNIQUE NOT NULL,
    tax_account TEXT,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    zone_code TEXT,
    owner_name TEXT,
    site_address TEXT,
    city TEXT,
    zip TEXT,
    legal_description TEXT,
    market_value NUMERIC,
    assessed_value NUMERIC,
    land_value NUMERIC,
    building_value NUMERIC,
    last_sale_date DATE,
    last_sale_price NUMERIC,
    building_sqft INTEGER,
    lot_size NUMERIC,
    year_built INTEGER,
    bedrooms INTEGER,
    bathrooms NUMERIC,
    photo_url TEXT,
    lat NUMERIC,
    lon NUMERIC,
    geometry GEOMETRY(Polygon, 4326),
    walk_score INTEGER,
    school_score INTEGER,
    crime_score INTEGER,
    census_tract TEXT,
    median_income NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_parcel_zones_parcel ON parcel_zones(parcel_id);
CREATE INDEX idx_parcel_zones_jurisdiction ON parcel_zones(jurisdiction_id);
CREATE INDEX idx_sample_properties_zone ON sample_properties(zone_code);
CREATE INDEX idx_sample_properties_jurisdiction ON sample_properties(jurisdiction_id);
CREATE INDEX idx_sample_properties_geometry ON sample_properties USING GIST(geometry);

-- Enable pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Ordinances with embeddings
CREATE TABLE ordinances (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    title TEXT,
    content TEXT,
    embedding VECTOR(1536),
    source_url TEXT,
    effective_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ordinances_embedding ON ordinances USING ivfflat (embedding vector_cosine_ops);
```

### Supabase Configuration

```
Project: mocerqjnksmhcjzxrewo.supabase.co
Region: us-east-1

Tables:
- jurisdictions: 17 rows (Brevard)
- zoning_districts: 290 rows
- parcel_zones: 24,243 rows
- sample_properties: 351,423 rows

Auth: Email + OAuth (Google, GitHub)
Storage: Bucket for PDFs, images
Realtime: Enabled for chat streaming
```

---

## Compute Layer Specification

### Modal.com Configuration

```python
import modal

app = modal.App("zonewise-scraper")

image = modal.Image.debian_slim().pip_install(
    "supabase",
    "httpx",
    "beautifulsoup4",
    "pdfplumber",
    "selenium",
    "webdriver-manager"
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("zonewise-secrets")],
    timeout=600,
    retries=3,
    concurrency_limit=20
)
def scrape_county(county_id: str, config: dict):
    """Scrape single county."""
    # Implementation
    pass

@app.function(schedule=modal.Cron("0 23 * * *"))  # 11 PM EST
def nightly_pipeline():
    """Run full 67-county scraping pipeline."""
    counties = get_all_counties()
    
    # Parallel execution
    results = list(scrape_county.map(
        [c["id"] for c in counties],
        [c["config"] for c in counties]
    ))
    
    # Log results
    log_pipeline_run(results)
    
    return {"processed": len(results)}
```

### Modal Secrets

```bash
modal secret create zonewise-secrets \
  SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co \
  SUPABASE_KEY=eyJ... \
  CENSUS_API_KEY=8c6ef3cae... \
  FIRECRAWL_API_KEY=fc-fa112951a...
```

---

## Deployment Specification

### Cloudflare Pages

```yaml
# cloudflare.yml
name: zonewise-frontend
build:
  command: npm run build
  output_directory: dist
environment:
  VITE_SUPABASE_URL: https://mocerqjnksmhcjzxrewo.supabase.co
  VITE_SUPABASE_ANON_KEY: eyJ...
```

### GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          projectName: zonewise
          directory: dist
```

---

## Security Specification

### Row Level Security (Supabase)

```sql
-- Public read for zoning data
CREATE POLICY "Public zoning read" ON zoning_districts
    FOR SELECT USING (true);

-- Authenticated write for admin
CREATE POLICY "Admin write" ON zoning_districts
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- User data isolation
CREATE POLICY "User data" ON user_queries
    FOR ALL USING (auth.uid() = user_id);
```

### API Security

- CORS: Whitelist frontend domains only
- Rate limiting: 100 req/min per IP
- Auth: Supabase JWT validation
- Input validation: Zod schemas

---

## Monitoring Specification

### Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Response time (P95) | <2s | >5s |
| Error rate | <1% | >5% |
| Zone coverage | 95%+ | <90% |
| Daily active users | Track | - |
| LLM cost/day | <$5 | >$10 |

### Tools

- Supabase Dashboard: Database metrics
- Cloudflare Analytics: Frontend performance
- Modal Dashboard: Compute usage
- LiteLLM Dashboard: LLM costs

---

*This specification is the technical source of truth for ZoneWise/BidDeed.AI/SPD development.*
