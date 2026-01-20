# ZoneWise Product Requirements Document (PRD) V3.0
## AI-Powered Split-Screen Zoning Intelligence Platform

**Product:** ZoneWise  
**Version:** 3.0.0  
**Date:** January 20, 2026  
**Author:** Ariel Shapira (Product Owner) + Claude AI Architect  
**Status:** Updated with Split-Screen UI, OpenManus, ShadCNBlocks

---

# CHANGELOG V3.0

| Feature | V2.0 | V3.0 | Source |
|---------|------|------|--------|
| UI Layout | Chat-only | **Split-Screen (Map + Chat)** | Reventure.app |
| Map Integration | Optional | **Core Feature (Mapbox GL)** | Reventure.app |
| AI Framework | LangGraph | **OpenManus Multi-Agent** | OpenManus |
| UI Templates | Custom | **ShadCNBlocks Premium** | ShadCNBlocks |
| Geographic Layers | County only | **State→Metro→County→ZIP** | Reventure.app |
| Data Visualization | Basic charts | **Choropleth + Time Series** | Reventure.app |

---

# TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Product Vision](#2-product-vision)
3. [User Personas](#3-user-personas)
4. [Split-Screen Interface (NEW)](#4-split-screen-interface)
5. [NLP Chatbot Core](#5-nlp-chatbot-core)
6. [Mapbox Integration (NEW)](#6-mapbox-integration)
7. [OpenManus Multi-Agent (NEW)](#7-openmanus-multi-agent)
8. [ShadCNBlocks UI (NEW)](#8-shadcnblocks-ui)
9. [Feature Requirements](#9-feature-requirements)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Success Metrics](#11-success-metrics)
12. [Competitive Analysis](#12-competitive-analysis)
13. [Timeline & Milestones](#13-timeline--milestones)
14. [Appendix](#14-appendix)

---

# 1. EXECUTIVE SUMMARY

## 1.1 What is ZoneWise V3.0?

**ZoneWise V3.0 is an AI-powered split-screen zoning intelligence platform** combining:

1. **Interactive Choropleth Maps** (LEFT) - Reventure.app style geographic visualization
2. **AI Chatbot with NLP** (RIGHT) - Conversational zoning expert
3. **OpenManus Multi-Agent Orchestration** - Parallel agent execution
4. **ShadCNBlocks Premium UI** - Enterprise-grade React components

## 1.2 Core Value Proposition

**"See the Data. Talk to the Expert."**

Users interact with zoning intelligence through two synchronized panels:
- **MAP PANEL:** Click any parcel → see zoning overlay → drill down State→Metro→County→ZIP
- **CHAT PANEL:** Ask "What can I build here?" → AI analyzes HBU + CMA + ML predictions

## 1.3 Key Differentiators

| Competitor | Interface | AI | Maps | Price |
|------------|-----------|-----|------|-------|
| **Reventure.app** | Split-screen | ❌ None | ✅ Excellent | $9.99/mo |
| **Gridics** | Forms/menus | ❌ None | ⚠️ Basic | $500-2000/mo |
| **ZoneWise V3** | **Split-screen** | ✅ **NLP Chat** | ✅ **Choropleth** | $49-199/mo |

**ZoneWise is the ONLY platform with Split-Screen + AI Chat + Choropleth Maps.**

---

# 2. PRODUCT VISION

## 2.1 Mission

Make zoning intelligence visually accessible and conversationally interactive for every Florida real estate professional.

## 2.2 Vision

Become the Google Maps + ChatGPT of zoning—where professionals see opportunities on a map and talk to an AI expert about feasibility.

## 2.3 North Star Metrics

| Metric | Q1 2026 | Q2 2026 | Q4 2026 |
|--------|---------|---------|---------|
| Daily Active Users (DAU) | 50 | 200 | 1,000 |
| Chat Messages/Day | 500 | 2,500 | 15,000 |
| Map Interactions/Day | 1,000 | 5,000 | 25,000 |
| Paid Subscribers | 10 | 50 | 300 |

## 2.4 Product Positioning

**"The Visual AI Zoning Expert"**

```
Reventure.app   →   Beautiful maps, NO AI
Gridics         →   Zoning data, NO maps, NO AI
ZoneWise V3     →   Beautiful maps + AI chat + zoning data
```

---

# 3. USER PERSONAS

## 3.1 Primary: Visual Investor Victor

**Profile:**
- Age: 40-55
- Experience: 10+ years real estate investing
- Behavior: Visual learner, prefers maps over spreadsheets
- Pain: Can't see zoning opportunities geographically
- Tool Usage: Heavy Reventure.app user

**User Journey:**
```
1. Opens ZoneWise → sees Florida map with zoning overlays
2. Zooms to Brevard County → sees ZIP-level choropleth
3. Clicks on Satellite Beach (32937) → sees R-1/R-2/C-1 distribution
4. Asks AI: "Where can I build apartments in this ZIP?"
5. AI highlights parcels + provides HBU analysis
6. Exports report with map + analysis
```

**Value:** First platform where he can SEE zoning opportunities.

## 3.2 Secondary: Data-Driven Developer Dana

**Profile:**
- Age: 35-45
- Experience: 5-15 projects/year
- Behavior: Analytical, wants numbers + visualizations
- Pain: Manually comparing properties is tedious
- Tool Usage: Uses spreadsheets, wishes for better tools

**User Journey:**
```
1. Opens ZoneWise → types address in chat
2. AI provides instant zoning analysis
3. Clicks "Show on Map" → property highlighted
4. Asks: "Show me similar properties within 2 miles"
5. Map displays comparable parcels with zoning
6. Compares HBU scores visually on map
```

**Value:** Visual comparison eliminates manual spreadsheet work.

## 3.3 Tertiary: Government Planner Grace

**Profile:**
- Job: Planning department staff
- Pain: Citizens ask questions she can't answer quickly
- Goal: Embed ZoneWise on city website

**Use Case:**
- Embeds ZoneWise iframe on city planning page
- Citizens explore zoning maps + ask AI questions
- Reduces in-person/phone inquiries by 70%

---

# 4. SPLIT-SCREEN INTERFACE (Reventure.app Reverse Engineering)

## 4.1 Layout Specification

```
┌────────────────────────────────────────────────────────────────────────┐
│ HEADER: Logo | Search | Metric Selector | User Menu | Dark Mode Toggle │
├──────────────────────────────────┬─────────────────────────────────────┤
│                                  │                                     │
│      INTERACTIVE MAP PANEL       │        AI CHAT PANEL                │
│          (60% width)             │          (40% width)                │
│                                  │                                     │
│   ┌────────────────────────┐     │   ┌─────────────────────────────┐   │
│   │  MAPBOX GL CHOROPLETH  │     │   │  CONVERSATION HISTORY       │   │
│   │                        │     │   │                             │   │
│   │  • Zoning overlay      │     │   │  User: What can I build     │   │
│   │  • Click for details   │     │   │        at 123 Main St?      │   │
│   │  • Zoom: State→ZIP     │     │   │                             │   │
│   │  • Color by metric     │     │   │  AI: That property is zoned │   │
│   │                        │     │   │      R-2, allowing...       │   │
│   │  ┌──────────────────┐  │     │   │                             │   │
│   │  │ LAYER TOGGLE     │  │     │   │  [Show on Map] [Get Report] │   │
│   │  │ ○ Zoning         │  │     │   │                             │   │
│   │  │ ● Foreclosures   │  │     │   └─────────────────────────────┘   │
│   │  │ ○ Home Values    │  │     │                                     │
│   │  │ ○ Inventory      │  │     │   ┌─────────────────────────────┐   │
│   │  └──────────────────┘  │     │   │  SUGGESTED ACTIONS          │   │
│   │                        │     │   │  • Calculate HBU            │   │
│   └────────────────────────┘     │   │  • Find similar properties  │   │
│                                  │   │  • Generate report          │   │
│   ┌────────────────────────┐     │   └─────────────────────────────┘   │
│   │ SELECTED REGION        │     │                                     │
│   │ Satellite Beach, 32937 │     │   ┌─────────────────────────────┐   │
│   │ Median: $485K | +4.2%  │     │   │  MESSAGE INPUT              │   │
│   └────────────────────────┘     │   │  [Ask about this property...│   │
│                                  │   │   📎 📷 🎤              Send]│   │
├──────────────────────────────────┴─────────────────────────────────────┤
│ FOOTER: Data Sources: BCPAO, Zillow, Census | Last Updated: 2h ago     │
└────────────────────────────────────────────────────────────────────────┘
```

## 4.2 Responsive Behavior

| Viewport | Layout | Map % | Chat % |
|----------|--------|-------|--------|
| Desktop (>1200px) | Side-by-side | 60% | 40% |
| Tablet (768-1200px) | Side-by-side | 50% | 50% |
| Mobile (<768px) | Stacked (tabs) | 100% or 100% | Toggle |

## 4.3 Panel Synchronization

**Map → Chat:**
```
User clicks parcel on map
  → Chat receives: { event: 'parcel_selected', parcel_id: 'xxx', address: '123 Main St' }
  → Chat auto-populates: "Tell me about 123 Main St"
  → AI provides instant analysis
```

**Chat → Map:**
```
User asks: "Show me R-2 parcels in Satellite Beach"
  → AI responds with results
  → Map receives: { event: 'highlight_parcels', parcel_ids: [...], zoom_to: true }
  → Map highlights matching parcels with animation
```

## 4.4 Reventure.app Features to Replicate

| Feature | Reventure Implementation | ZoneWise Implementation |
|---------|--------------------------|-------------------------|
| Geographic Drill-Down | State → Metro → County → ZIP | ✅ Same hierarchy |
| Choropleth Colors | 7-color gradient by metric | ✅ Same approach |
| Time Series Charts | 25-year historical data | ✅ Zoning + price history |
| Score Cards | Price Forecast Score | ✅ HBU Score + ML Score |
| Layer Toggles | 10+ data layers | ✅ Zoning + Foreclosures + Values |
| Search | Address/location search | ✅ Natural language search |

---

# 5. NLP CHATBOT CORE

## 5.1 Chat-First Architecture

The AI chatbot remains the **primary intelligence interface**, now enhanced with map context.

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                                │
│  Text: "What can I build at 123 Main St?"                   │
│  Context: { selected_parcel: 'xxx', map_view: 'Satellite' } │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 INTENT CLASSIFICATION                        │
│  Intent: FEASIBILITY_CHECK (confidence: 0.95)               │
│  Entities: { address: '123 Main St', action: 'build' }      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 KNOWLEDGE RETRIEVAL                          │
│  Zoning: R-2 | FAR: 0.5 | Setbacks: 25/10/10/20            │
│  Allowed: SFR, Duplex, ADU | Conditional: MF (4+ units)    │
│  HBU Score: 78/100 | ML Prediction: $425K                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               RESPONSE GENERATION                            │
│  "123 Main St is zoned R-2. You can build:                  │
│   • Single-family home (by-right)                           │
│   • Duplex (by-right)                                       │
│   • ADU up to 800 sq ft (by-right)                         │
│   Would you like me to calculate the maximum buildable      │
│   square footage or show similar R-2 properties on the map?"│
│                                                             │
│  Actions: [Show on Map] [Calculate Max] [Get Report]        │
└─────────────────────────────────────────────────────────────┘
```

## 5.2 Enhanced Intent Types (Map-Aware)

| Intent | Example | Map Action |
|--------|---------|------------|
| FEASIBILITY | "Can I build apartments?" | Highlight parcel |
| COMPARISON | "Compare this to 456 Oak St" | Show both parcels |
| SEARCH | "Find R-2 lots under $200K" | Filter + highlight |
| GEOGRAPHIC | "Show me C-1 zones in Melbourne" | Zoom + filter |
| ANALYSIS | "What's the HBU for selected area?" | Analyze visible |
| REPORT | "Generate report for map area" | Export view |

## 5.3 Context Awareness

```typescript
interface ChatContext {
  // Map state
  selected_parcel?: string;
  visible_parcels: string[];
  current_zoom: number;
  current_bounds: GeoJSON.BBox;
  active_layers: string[];
  
  // Conversation state
  previous_messages: Message[];
  mentioned_addresses: string[];
  current_intent: string;
  
  // User state
  user_id: string;
  subscription_tier: 'free' | 'basic' | 'pro' | 'enterprise';
  saved_properties: string[];
}
```

---

# 6. MAPBOX INTEGRATION

## 6.1 Map Requirements

| Requirement | Specification |
|-------------|---------------|
| Provider | Mapbox GL JS v3.0+ |
| Layers | Zoning, Foreclosures, Home Values, Inventory |
| Boundaries | State, Metro, County, ZIP (TigerLine) |
| Parcels | BCPAO parcel polygons (PostGIS) |
| Style | Custom style matching ShadCNBlocks theme |
| Performance | 60fps pan/zoom, <100ms layer toggle |

## 6.2 Choropleth Color Scales

```javascript
// Zoning Density (units/acre)
const zoningScale = [
  { threshold: 0, color: '#E3F2FD', label: 'Agriculture' },
  { threshold: 1, color: '#90CAF9', label: 'R-1 (SFR)' },
  { threshold: 4, color: '#42A5F5', label: 'R-2 (Duplex)' },
  { threshold: 8, color: '#1E88E5', label: 'R-3 (MF Low)' },
  { threshold: 16, color: '#1565C0', label: 'R-4 (MF High)' },
  { threshold: 'commercial', color: '#F57C00', label: 'Commercial' },
  { threshold: 'industrial', color: '#7B1FA2', label: 'Industrial' },
];

// HBU Score (0-100)
const hbuScale = [
  { threshold: 0, color: '#D32F2F', label: 'Skip (0-40)' },
  { threshold: 40, color: '#F57C00', label: 'Review (40-60)' },
  { threshold: 60, color: '#FBC02D', label: 'Consider (60-75)' },
  { threshold: 75, color: '#388E3C', label: 'Bid (75-90)' },
  { threshold: 90, color: '#1B5E20', label: 'Strong Bid (90+)' },
];

// Foreclosure Status
const foreclosureScale = [
  { status: 'none', color: '#E0E0E0', label: 'No Foreclosure' },
  { status: 'lis_pendens', color: '#FFF59D', label: 'Lis Pendens' },
  { status: 'scheduled', color: '#FFB74D', label: 'Auction Scheduled' },
  { status: 'active', color: '#EF5350', label: 'Active Auction' },
];
```

## 6.3 Geographic Hierarchy

```
Florida (State)
  └── 28 MSAs (Metro Statistical Areas)
       └── 67 Counties
            └── ~3,000 ZIP Codes
                 └── ~10M Parcels
```

**Zoom Level Mapping:**
| Zoom | View | Data Granularity |
|------|------|------------------|
| 5-6 | Florida | County aggregates |
| 7-8 | Region | ZIP aggregates |
| 9-10 | County | ZIP boundaries |
| 11-12 | City | Parcel outlines |
| 13+ | Neighborhood | Parcel details |

## 6.4 Parcel Interaction

```javascript
// On parcel click
map.on('click', 'parcels-layer', async (e) => {
  const parcel = e.features[0];
  
  // Highlight selected parcel
  map.setFeatureState(
    { source: 'parcels', id: parcel.id },
    { selected: true }
  );
  
  // Show popup with quick info
  new mapboxgl.Popup()
    .setLngLat(e.lngLat)
    .setHTML(`
      <h3>${parcel.properties.address}</h3>
      <p>Zoning: ${parcel.properties.zone_code}</p>
      <p>HBU Score: ${parcel.properties.hbu_score}</p>
      <button onclick="askAI('${parcel.id}')">Ask AI</button>
    `)
    .addTo(map);
  
  // Notify chat panel
  chatPanel.setContext({ selected_parcel: parcel.id });
});
```

---

# 7. OPENMANUS MULTI-AGENT INTEGRATION

## 7.1 Why OpenManus?

OpenManus uses a Next.js frontend with React components, matching our ShadCNBlocks stack perfectly. The multi-agent architecture enables parallel processing of complex queries.

## 7.2 Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COORDINATOR AGENT                         │
│  • Receives user query + map context                        │
│  • Decomposes into sub-tasks                                │
│  • Assigns to specialized agents                            │
│  • Aggregates results                                        │
└─────────────────────────────────────────────────────────────┘
        ↓               ↓               ↓               ↓
┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│ ZONING    │   │ CMA       │   │ HBU       │   │ ML        │
│ AGENT     │   │ AGENT     │   │ AGENT     │   │ AGENT     │
│           │   │           │   │           │   │           │
│ • Zone    │   │ • Comps   │   │ • Highest │   │ • XGBoost │
│   lookup  │   │ • Price   │   │   & best  │   │ • Predict │
│ • Rules   │   │   analysis│   │   use     │   │   price   │
│ • Setbacks│   │ • Trends  │   │ • FAR calc│   │ • Prob    │
└───────────┘   └───────────┘   └───────────┘   └───────────┘
        ↓               ↓               ↓               ↓
┌─────────────────────────────────────────────────────────────┐
│                    REPORTER AGENT                            │
│  • Synthesizes all agent outputs                            │
│  • Generates natural language response                      │
│  • Creates map actions (highlight, zoom, filter)            │
│  • Suggests follow-up actions                               │
└─────────────────────────────────────────────────────────────┘
```

## 7.3 Agent Specifications

| Agent | Model | Purpose | Output |
|-------|-------|---------|--------|
| Coordinator | Claude Sonnet 4.5 | Task decomposition | Sub-task list |
| Zoning Agent | Gemini 2.5 Flash | Zone lookup + rules | Zoning data JSON |
| CMA Agent | Gemini 2.5 Flash | Comparable analysis | Comps + price |
| HBU Agent | Claude Sonnet 4.5 | Highest & best use | HBU score + reasoning |
| ML Agent | XGBoost (local) | Price prediction | Predicted value + confidence |
| Reporter Agent | Claude Sonnet 4.5 | Response generation | Natural language + actions |

## 7.4 Parallel Execution

```python
async def process_query(query: str, context: dict):
    # Step 1: Coordinator decomposes task
    tasks = await coordinator.decompose(query, context)
    
    # Step 2: Execute agents in parallel
    results = await asyncio.gather(
        zoning_agent.execute(tasks.get('zoning')),
        cma_agent.execute(tasks.get('cma')),
        hbu_agent.execute(tasks.get('hbu')),
        ml_agent.execute(tasks.get('ml')),
    )
    
    # Step 3: Reporter synthesizes response
    response = await reporter_agent.synthesize(results, context)
    
    return response
```

---

# 8. SHADCNBLOCKS UI INTEGRATION

## 8.1 Template Selection

Based on UI/UX requirements and Reventure.app reverse engineering:

| Component | ShadCNBlocks Template | Purpose |
|-----------|----------------------|---------|
| Landing Page | **Zippay** | Fintech-style marketing |
| Broker Dashboard | **Admin Dashboard** | Data tables, charts, KPIs |
| Documentation | **Plasma** | Docs, onboarding, API ref |
| Components | **959+ Blocks** | All UI elements |

## 8.2 Component Mapping

```
ShadCNBlocks Premium ($149)
├── Landing Page (Zippay)
│   ├── Hero Section → ZoneWise value prop
│   ├── Feature Grid → Split-screen demo
│   ├── Pricing Tables → Subscription tiers
│   └── Testimonials → User success stories
│
├── Admin Dashboard
│   ├── Sidebar Navigation → County/ZIP selection
│   ├── Data Tables → Property lists
│   ├── Charts (Recharts) → Zoning distribution
│   ├── Cards → Property quick view
│   └── Command Palette → Global search
│
├── Chat Interface
│   ├── Chat Bubble → AI responses
│   ├── Message Input → User queries
│   ├── Action Buttons → Map actions
│   └── Typing Indicator → Loading state
│
└── Map Controls
    ├── Layer Toggles → Zoning/foreclosure layers
    ├── Search Box → Address lookup
    ├── Zoom Controls → Navigation
    └── Legend → Color scale reference
```

## 8.3 Theme Configuration

```typescript
// Tailwind config extending ShadCNBlocks
const theme = {
  colors: {
    primary: {
      DEFAULT: '#1E3A5F', // ZoneWise navy
      foreground: '#FFFFFF',
    },
    secondary: {
      DEFAULT: '#F57C00', // Orange accent
      foreground: '#FFFFFF',
    },
    success: '#388E3C', // Bid green
    warning: '#FBC02D', // Review yellow
    danger: '#D32F2F', // Skip red
    
    // Map-specific colors
    zoning: {
      residential: '#42A5F5',
      commercial: '#F57C00',
      industrial: '#7B1FA2',
      agricultural: '#66BB6A',
    },
  },
  
  // Custom components
  components: {
    splitScreen: {
      mapPanel: 'w-[60%]',
      chatPanel: 'w-[40%]',
    },
  },
};
```

---

# 9. FEATURE REQUIREMENTS

## 9.1 Core Features (P0 - Must Have)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| F1 | Split-Screen Layout | Map (left) + Chat (right) | Responsive, synchronized |
| F2 | Choropleth Map | Color-coded zoning/metrics | 7+ color scales, 60fps |
| F3 | NLP Chat | Natural language queries | 90% intent accuracy |
| F4 | Parcel Selection | Click parcel → see details | <100ms response |
| F5 | Geographic Drill-Down | State→Metro→County→ZIP | All 67 FL counties |
| F6 | Map-Chat Sync | Click map → populate chat | Bi-directional |
| F7 | HBU Analysis | Highest & best use score | 0-100 scale |
| F8 | Report Export | PDF/DOCX with map snapshot | Include analysis |

## 9.2 Enhanced Features (P1 - Should Have)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| F9 | Time Series Charts | Historical zoning changes | 10-year history |
| F10 | CMA Integration | Comparable market analysis | 5+ comps |
| F11 | ML Predictions | Price/probability predictions | 64%+ accuracy |
| F12 | Saved Properties | Bookmark + compare | Unlimited saves |
| F13 | Custom Layers | User-uploaded boundaries | GeoJSON import |
| F14 | Collaboration | Share map views | Shareable links |

## 9.3 Advanced Features (P2 - Nice to Have)

| ID | Feature | Description | Acceptance Criteria |
|----|---------|-------------|---------------------|
| F15 | Voice Input | Speak to chat | 95% transcription accuracy |
| F16 | Image Analysis | Upload property photos | Extract details |
| F17 | API Access | Programmatic queries | REST + GraphQL |
| F18 | White-Label | Broker branding | Custom domains |

---

# 10. NON-FUNCTIONAL REQUIREMENTS

## 10.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Map Load Time | <2s | Time to interactive |
| Chat Response | <3s | Query to response |
| Parcel Click | <100ms | Click to popup |
| Layer Toggle | <200ms | Toggle to render |
| Concurrent Users | 500 | Simultaneous sessions |

## 10.2 Scalability

| Component | Current | Target | Approach |
|-----------|---------|--------|----------|
| Parcels | 500K (Brevard) | 10M (67 counties) | PostGIS optimization |
| Daily Queries | 1,000 | 100,000 | Edge caching |
| Map Tiles | Standard | Custom vector | Mapbox tiling |

## 10.3 Cost Targets

| Component | Monthly Cost |
|-----------|--------------|
| Mapbox GL JS | FREE (50K loads) |
| ShadCNBlocks | $149 (one-time) |
| Supabase | $25 (Pro plan) |
| Render.com | $25 (Starter) |
| LLM APIs | $50 (90% FREE tier) |
| **TOTAL** | **~$100/month** |

---

# 11. SUCCESS METRICS

## 11.1 Primary KPIs

| KPI | Definition | Q1 Target | Q4 Target |
|-----|------------|-----------|-----------|
| DAU | Daily Active Users | 50 | 1,000 |
| Session Duration | Avg time in app | 8 min | 15 min |
| Map Interactions | Clicks + zooms/session | 20 | 50 |
| Chat Messages | Messages/session | 5 | 12 |
| Conversion Rate | Free → Paid | 5% | 10% |

## 11.2 Secondary KPIs

| KPI | Definition | Target |
|-----|------------|--------|
| NPS | Net Promoter Score | 50+ |
| Churn | Monthly subscriber churn | <5% |
| Support Tickets | Tickets/100 users | <2 |
| Feature Adoption | % using map+chat | 80% |

---

# 12. COMPETITIVE ANALYSIS

## 12.1 Feature Comparison

| Feature | ZoneWise V3 | Reventure | Gridics | Zoneomics |
|---------|-------------|-----------|---------|-----------|
| Split-Screen UI | ✅ | ✅ | ❌ | ❌ |
| NLP Chatbot | ✅ | ❌ | ❌ | ❌ |
| Choropleth Maps | ✅ | ✅ | ⚠️ | ⚠️ |
| ZIP-Level Data | ✅ | ✅ | ❌ | ⚠️ |
| Zoning Analysis | ✅ | ❌ | ✅ | ✅ |
| HBU Analysis | ✅ | ❌ | ❌ | ⚠️ |
| ML Predictions | ✅ | ❌ | ❌ | ❌ |
| Price | $49-199/mo | $9.99/mo | $500-2000/mo | API |

## 12.2 Unique Value Proposition

**ZoneWise V3 is the ONLY platform that combines:**
1. Reventure-style visual maps
2. AI conversational interface
3. Comprehensive zoning intelligence
4. Foreclosure auction integration
5. ML-powered predictions

---

# 13. TIMELINE & MILESTONES

## 13.1 Development Phases

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1: Foundation** | Weeks 1-2 | Split-screen layout, Mapbox setup, ShadCNBlocks integration |
| **Phase 2: Map Features** | Weeks 3-4 | Choropleth layers, parcel selection, geographic hierarchy |
| **Phase 3: Chat Integration** | Weeks 5-6 | NLP chatbot, map-chat sync, OpenManus agents |
| **Phase 4: Intelligence** | Weeks 7-8 | HBU analysis, CMA integration, ML predictions |
| **Phase 5: Polish** | Weeks 9-10 | Performance optimization, testing, documentation |
| **Phase 6: Launch** | Weeks 11-12 | Beta launch, feedback integration, marketing |

## 13.2 Key Milestones

| Date | Milestone |
|------|-----------|
| Jan 27, 2026 | Split-screen prototype live |
| Feb 10, 2026 | Mapbox + choropleth complete |
| Feb 24, 2026 | Chat + OpenManus integration |
| Mar 10, 2026 | Full 67-county data loaded |
| Mar 24, 2026 | Beta launch to 50 users |
| Mar 31, 2026 | Public launch |

---

# 14. APPENDIX

## 14.1 Glossary

| Term | Definition |
|------|------------|
| Choropleth | Map with colored regions based on data values |
| HBU | Highest and Best Use analysis |
| CMA | Comparative Market Analysis |
| NLP | Natural Language Processing |
| OpenManus | Multi-agent AI orchestration framework |
| ShadCNBlocks | Premium UI component library |

## 14.2 Related Documents

| Document | Purpose |
|----------|---------|
| ZoneWise PRS V3.0 | Technical specifications |
| Reventure.app CI Report | Reverse engineering analysis |
| ShadCNBlocks Integration Guide | UI implementation details |
| OpenManus Architecture | Multi-agent system design |

## 14.3 Approval

| Role | Name | Status |
|------|------|--------|
| Product Owner | Ariel Shapira | Pending |
| AI Architect | Claude AI | Approved |
| Engineering | Claude Code | Pending |

---

*ZoneWise PRD V3.0*  
*Split-Screen + NLP + Mapbox + OpenManus*  
*January 20, 2026*
