# ZoneWise / BidDeed.AI / SPD Architecture Decision

**Date:** January 25, 2026  
**Author:** Claude AI (AI Architect)  
**Approved By:** Ariel Shapira (Solo Founder)  
**Status:** APPROVED

---

## Executive Summary

This document captures the definitive architecture decision for building "Claude AI for Real Estate" - a split-screen NLP chatbot platform serving ZoneWise, BidDeed.AI, and SPD Site Plan Development.

**Key Decision:** Open Source foundation (90%) with Open-claude UI + Supabase backend + Modal.com compute.

---

## Table of Contents

1. [Context & Problem Statement](#context--problem-statement)
2. [Current State Assessment](#current-state-assessment)
3. [Repository Analysis](#repository-analysis)
4. [Architecture Decision](#architecture-decision)
5. [Full Stack Specification](#full-stack-specification)
6. [Open Source vs Closed Source](#open-source-vs-closed-source)
7. [12-Week Execution Plan](#12-week-execution-plan)
8. [Cost Analysis](#cost-analysis)
9. [Risk Assessment](#risk-assessment)

---

## Context & Problem Statement

### The Goal
Build a Claude AI / Manus AI style interface with:
- Split-screen layout (chat left, artifacts right)
- NLP chatbot capabilities
- Real estate domain specialization (zoning, parcels, foreclosures)
- 67 Florida counties coverage for MVP

### The Constraint
- Solo founder with ADHD
- 20 minutes/day oversight maximum
- Autonomous AI team (Claude AI + Claude Code + Greptile)
- Must leverage existing proven infrastructure

### The Proven Foundation
- **Malabar POC:** 100% stable (1,430 parcels, 10 stages complete)
- **20-Phase ZoneWise Framework:** Validated methodology
- **10-Stage Data Framework:** Production-ready pipeline
- **Modal.com:** Identified for 67-county parallel compute

---

## Current State Assessment

### Supabase Data (as of Jan 25, 2026)

| Table | Count | Status |
|-------|-------|--------|
| jurisdictions | 17 | ✅ Brevard complete |
| zoning_districts | 290 | ✅ Growing |
| sample_properties | 351,423 | ✅ Brevard parcels |
| parcel_zones | 24,243 | ⚠️ 6.8% coverage |

### GitHub Repository: breverdbidder/zonewise

```
zonewise/
├── .claude/                 # Claude Code config
├── .github/                 # GitHub Actions
├── src/
│   ├── agents/             # LangGraph agents
│   ├── scrapers/           # Municode, BCPAO, GIS
│   ├── integrations/       # External APIs
│   └── gis_catalog.py      # Verified GIS endpoints
├── mcp-server/             # MCP integration
├── database/               # Supabase schemas
├── docs/                   # Documentation
└── PROJECT_STATE.json      # Current state
```

### Gap Analysis

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Brevard Zone Coverage | 6.8% | 100% | 93.2% |
| Florida Counties | 1 | 67 | 66 |
| UI Platform | None | Split-screen | 100% |
| Production Deployment | Partial | Full | Modal.com needed |

---

## Repository Analysis

### Repositories Evaluated (18 Total)

#### Tier 1: Stack-Aligned (Ranks 1-5)

| Rank | Repository | Stars | Why Important |
|------|------------|-------|---------------|
| 1 | **Damienchakma/Open-claude** | New | EXACT split-screen UI needed |
| 2 | mckaywrigley/chatbot-ui | 28K | Native Supabase, battle-tested |
| 3 | makerkit/next-supabase-saas-kit | 500+ | Full SaaS (approved $299) |
| 4 | supabase-community/chatgpt-your-files | 2K | RAG with pgvector |
| 5 | cloudflare/agents-starter | 1K | Official Cloudflare AI |

#### Tier 2: Infrastructure (Ranks 6-10)

| Rank | Repository | Stars | Use Case |
|------|------------|-------|----------|
| 6 | BerriAI/litellm | 15K | Multi-provider LLM routing |
| 7 | fastapi/full-stack-fastapi-template | 27K | Backend patterns |
| 8 | langfuse/langfuse | 6K | LLM observability (GAP) |
| 9 | Unstructured-IO/unstructured | 9K | Doc processing (GAP) |
| 10 | wassim249/fastapi-langgraph | 500+ | Agent patterns |

#### Tier 3-4: Reference Only (Ranks 11-18)

- pengxiaoo/llama-index-fastapi
- QuivrHQ/quivr
- electron-react-boilerplate
- WrathChaos/react-native-typescript-boilerplate
- borys25ol/fastapi-react-kubernetes
- Harmeet10000/langchain-fastapi-production
- alan345/Fullstack-SaaS-Boilerplate
- Significant-Gravitas/AutoGPT

### Winner: Open-claude

**Why Open-claude beats alternatives:**

| Factor | Open-claude | chatbot-ui | Makerkit |
|--------|-------------|------------|----------|
| Split-screen UI | ✅ Built-in | ❌ Build | ❌ Build |
| ArtifactPanel | ✅ Ready | ❌ Build | ❌ Build |
| ThinkingDisplay | ✅ Ready | ❌ No | ❌ No |
| Time to MVP | 3 weeks | 4+ weeks | 5+ weeks |
| Cost | $0 | $0 | $299 |

---

## Architecture Decision

### DECISION: Open Source Foundation (90%)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ZONEWISE / BIDDEED.AI / SPD                          │
│                     "Claude AI for Real Estate"                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FRONTEND LAYER (Open-claude Fork)                                          │
│  ├── React 18 + Vite + TailwindCSS + Shadcn/ui                             │
│  ├── ArtifactPanel.jsx (split-screen right)                                │
│  ├── ChatMode.jsx (split-screen left)                                      │
│  ├── ThinkingDisplay.jsx (AI reasoning)                                    │
│  └── Deploy: Cloudflare Pages (FREE)                                       │
│                                                                              │
│  API LAYER (Supabase Edge Functions)                                        │
│  ├── /api/chat → LiteLLM routing                                           │
│  ├── /api/zoning → ZoneWise queries                                        │
│  ├── /api/parcels → BCPAO integration                                      │
│  └── /api/agents → LangGraph orchestration                                 │
│                                                                              │
│  AI ORCHESTRATION (LangGraph + LiteLLM)                                     │
│  ├── Zoning Agent                                                           │
│  ├── Parcel Agent                                                           │
│  ├── Report Agent                                                           │
│  └── Smart Router (FREE: Gemini, CHEAP: DeepSeek, QUALITY: Claude)         │
│                                                                              │
│  DATA LAYER (Supabase)                                                      │
│  ├── PostgreSQL + pgvector                                                  │
│  ├── Auth (FREE)                                                            │
│  ├── Storage (PDFs, images)                                                 │
│  └── Realtime (streaming)                                                   │
│                                                                              │
│  COMPUTE LAYER (Modal.com)                                                  │
│  ├── 67 FL counties parallel scraping                                       │
│  ├── Daily 11 PM EST cron                                                   │
│  └── $30 FREE credit/month                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Full Stack Specification

### Frontend: Open-claude Fork

**Repository:** https://github.com/Damienchakma/Open-claude  
**License:** MIT (Open Source)

**Components to Use:**
```
src/components/
├── ArtifactPanel.jsx      → Zoning reports, maps, analysis
├── ChatMode.jsx           → NLP input, message history
├── ThinkingDisplay.jsx    → AI reasoning transparency
├── ModeSwitcher.jsx       → Chat | Analyze | Build | Research
├── CitationDisplay.jsx    → Source document links
└── StreamingMessage.jsx   → Real-time AI responses
```

**Components to Add:**
```
src/components/
├── ZoningReport.jsx       → 20-phase analysis display
├── ParcelMap.jsx          → Leaflet/Mapbox integration
├── PropertyCard.jsx       → BCPAO data display
└── AuctionAnalysis.jsx    → BidDeed.AI max bid
```

**Modifications:**
```
src/lib/
├── llm-factory.js         → REPLACE with LiteLLM
└── storage.js             → REPLACE with Supabase
```

### Backend: Supabase

**Project:** mocerqjnksmhcjzxrewo.supabase.co  
**License:** Apache 2.0 (Open Source, Self-hostable)

**Tables:**
| Table | Purpose | Current Rows |
|-------|---------|--------------|
| jurisdictions | FL municipalities | 17 |
| zoning_districts | Zone definitions + DIMS | 290 |
| parcel_zones | Parcel-to-zone mapping | 24,243 |
| sample_properties | BCPAO parcel data | 351,423 |
| permitted_uses | By-right uses | Growing |
| dimensional_standards | Setbacks, heights | Growing |
| ordinances | Full code text + embeddings | Growing |

### AI Layer: LiteLLM + LangGraph

**LiteLLM (MIT License):**
```python
# Smart Router Tiers
TIERS = {
    "FREE": "gemini/gemini-2.5-flash",      # 40-55% of requests
    "ULTRA_CHEAP": "deepseek/deepseek-chat", # $0.28/1M tokens
    "QUALITY": "anthropic/claude-sonnet-4-5", # Complex queries
    "COMPLEX": "anthropic/claude-opus-4-5",   # Reasoning tasks
}
```

**LangGraph (MIT License):**
```python
# Agent Definitions
agents = {
    "zoning_agent": "Queries zoning_districts, dimensional_standards",
    "parcel_agent": "Queries BCPAO, sample_properties",
    "report_agent": "Generates PDF/DOCX reports",
    "foreclosure_agent": "BidDeed.AI specific analysis",
}
```

### Compute: Modal.com

**Pricing:** $30 FREE credit/month (covers 67 counties)  
**License:** Proprietary (but replaceable with GitHub Actions)

**Configuration:**
```python
import modal

app = modal.App("zonewise-scraper")

@app.function(
    schedule=modal.Cron("0 23 * * *"),  # 11 PM EST daily
    concurrency_limit=20,
    timeout=600,
    retries=3
)
def nightly_scrape():
    # Parallel execution across 67 counties
    results = list(scrape_county.map(county_ids))
    return results
```

---

## Open Source vs Closed Source

| Layer | Choice | License | Replaceable? |
|-------|--------|---------|--------------|
| Frontend UI | Open-claude | MIT | N/A (we own fork) |
| UI Components | Shadcn/ui | MIT | Yes |
| Database | Supabase | Apache 2.0 | Yes (self-host) |
| Auth | Supabase Auth | Apache 2.0 | Yes |
| LLM Routing | LiteLLM | MIT | Yes |
| Agents | LangGraph | MIT | Yes |
| Compute | Modal.com | Proprietary | Yes (GitHub Actions) |
| Hosting | Cloudflare | Proprietary | Yes (Vercel, Netlify) |

**Verdict: 90% Open Source**

Proprietary components (Modal, Cloudflare) are:
- Easily replaceable
- Have generous free tiers
- No data lock-in (all data in Supabase)

---

## 12-Week Execution Plan

### PHASE 1: DATA SCALING (Weeks 1-6)

**Principle:** "Data is the moat. Everything else is a wrapper."

#### Weeks 1-2: Brevard 100%

| Day | Task | Owner | Output |
|-----|------|-------|--------|
| Sun | Greptile audit: GIS endpoint gaps | Claude AI | Task list |
| Mon | Zone assignment: Unincorporated (75K) | Claude Code | +75K parcels |
| Tue | Zone assignment: Palm Bay (78K) | Claude Code | +78K parcels |
| Wed | Zone assignment: Melbourne (62K) | Claude Code | +62K parcels |
| Thu | Remaining 13 jurisdictions | Claude Code | +112K parcels |
| Fri | Validation + fixes | Claude AI | 100% verified |
| Sat | Shabbat | - | Rest |

**Exit Criteria:** 351,423 parcels at 100% zone coverage

#### Weeks 3-4: Modal.com Production

| Task | Owner | Output |
|------|-------|--------|
| Sign up Modal.com | Ariel (5 min) | Account |
| Create secrets | Ariel (2 min) | Credentials |
| Deploy zonewise app | Claude Code | Live endpoint |
| Test 3 counties parallel | Claude Code | Verified |
| Configure nightly cron | Claude Code | 11 PM EST |

**Exit Criteria:** Modal.com running 67 counties nightly

#### Weeks 5-6: Top 5 Counties

| Week | Counties | Est. Parcels |
|------|----------|--------------|
| 5 | Orange, Hillsborough | ~400K |
| 6 | Miami-Dade, Broward, Palm Beach | ~600K |

**Exit Criteria:** 6 counties at 95%+ accuracy

### PHASE 2: INFRASTRUCTURE (Weeks 7-8)

#### Week 7: Remaining Counties

| Task | Owner | Output |
|------|-------|--------|
| Duval, Pinellas, Polk | Claude Code | +350K |
| Lee, Volusia, Seminole | Claude Code | +300K |
| Remaining 55 counties | Claude Code | Pipeline ready |

#### Week 8: Quality Gates

| Task | Owner | Output |
|------|-------|--------|
| Greptile codebase audit | Claude AI | Clean code |
| Remove dead code | Claude Code | Optimized |
| Test coverage >80% | Claude Code | Verified |
| Documentation complete | Claude AI | Ready |

**Exit Criteria:** 67 counties in pipeline, codebase clean

### PHASE 3: UI + MVP (Weeks 9-12)

#### Week 9: Foundation

| Day | Task | Output |
|-----|------|--------|
| Sun | Fork Open-claude | Local running |
| Mon | Add Supabase auth | Login working |
| Tue | Replace LLM factory with LiteLLM | AI responses |
| Wed | Connect to ZoneWise Supabase | Data flowing |
| Thu | Basic chat → zoning query | E2E test |
| Fri | Deploy to Cloudflare Pages | Live URL |

#### Week 10: AI Integration

| Day | Task | Output |
|-----|------|--------|
| Sun | LangGraph agent setup | Scaffold |
| Mon | Zoning Agent | "What's the zoning?" |
| Tue | Parcel Agent | "Show me parcel X" |
| Wed | Report Agent | PDF downloads |
| Thu | Smart Router | Cost optimization |
| Fri | Streaming responses | Real-time UX |

#### Week 11: Artifacts

| Day | Task | Output |
|-----|------|--------|
| Sun | ZoningReport component | 20-phase display |
| Mon | ParcelMap component | Interactive map |
| Tue | PropertyCard component | Owner, value |
| Wed | AuctionAnalysis component | Max bid calc |
| Thu | PDF export | Downloadable |
| Fri | Polish transitions | Smooth UX |

#### Week 12: Launch

| Day | Task | Output |
|-----|------|--------|
| Sun | Bug fixes | Stable |
| Mon | Performance (<2s) | Fast |
| Tue | Mobile responsive | Works on phone |
| Wed | Error handling | Professional |
| Thu | Final testing | All passing |
| Fri | **MVP LAUNCH** | 🚀 LIVE |

---

## Cost Analysis

### Monthly Operating Costs (MVP Phase)

| Service | Cost | Notes |
|---------|------|-------|
| Cloudflare Pages | $0 | Unlimited sites |
| Supabase | $0 | Free tier (500MB, 50K auth) |
| Modal.com | $0 | $30 credit covers 67 counties |
| LiteLLM | $0 | Self-hosted |
| Gemini API | $0 | Free tier (40-55% of requests) |
| DeepSeek API | ~$5 | ULTRA_CHEAP tier |
| Claude API | ~$50 | Quality tier only |
| **TOTAL** | **~$55/month** | Until paying users |

### Scaling Costs (Post-MVP)

| Users | Est. Monthly Cost |
|-------|-------------------|
| 1-100 | $55 |
| 100-1,000 | $200 |
| 1,000-10,000 | $500 + Supabase Pro ($25) |
| 10,000+ | Custom pricing needed |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Modal.com pricing changes | Low | Medium | GitHub Actions fallback |
| Open-claude abandoned | Low | Low | We own the fork |
| Supabase outage | Low | High | Daily backups, can self-host |
| GIS API changes | Medium | Medium | Multiple endpoint catalog |
| LLM API costs spike | Medium | Medium | Smart Router optimization |
| Solo founder burnout | Medium | High | 20 min/day rule, AI team |

---

## Appendix: Key Links

### Repositories
- ZoneWise: https://github.com/breverdbidder/zonewise
- Open-claude: https://github.com/Damienchakma/Open-claude
- LiteLLM: https://github.com/BerriAI/litellm
- LangGraph: https://github.com/langchain-ai/langgraph

### Services
- Supabase: https://supabase.com
- Modal.com: https://modal.com
- Cloudflare Pages: https://pages.cloudflare.com

### Documentation
- Supabase Docs: https://supabase.com/docs
- LiteLLM Docs: https://docs.litellm.ai
- Modal Docs: https://modal.com/docs

---

## Approval

**AI Architect Decision:** APPROVED  
**Date:** January 25, 2026  
**Next Action:** Complete Brevard 100% before UI development

---

*This document represents the definitive architecture for ZoneWise/BidDeed.AI/SPD. All future development should reference this as the source of truth.*
