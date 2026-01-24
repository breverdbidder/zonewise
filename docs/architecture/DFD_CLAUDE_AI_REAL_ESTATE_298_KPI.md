# Claude AI for Real Estate: Data Flow Diagram (DFD)

**Version:** 1.0  
**Date:** January 25, 2026  
**Status:** PRODUCTION ARCHITECTURE  
**Integration:** 298 KPIs + Split-Screen UI + LangGraph Agents

---

## Executive Summary

This Data Flow Diagram (DFD) documents the complete data architecture for "Claude AI for Real Estate" - the unified platform combining BidDeed.AI (foreclosure auctions) and ZoneWise (zoning intelligence). The system processes data through three levels, integrating 298 unique KPIs.

---

## DFD Level 0: Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    EXTERNAL ENTITIES                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │   INVESTOR   │  │   BROKER     │  │  DEVELOPER   │  │   LENDER     │                │
│  │    (User)    │  │    (User)    │  │    (User)    │  │    (User)    │                │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                │
│         │                 │                 │                 │                         │
│         └─────────────────┴────────┬────────┴─────────────────┘                         │
│                                    │                                                     │
│                                    ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                                   │   │
│  │                    CLAUDE AI FOR REAL ESTATE                                      │   │
│  │                    (298 KPI Processing System)                                    │   │
│  │                                                                                   │   │
│  │    ┌─────────────────────────────────────────────────────────────────────────┐  │   │
│  │    │                        SPLIT-SCREEN UI                                   │  │   │
│  │    │   ┌──────────────────────┐    ┌─────────────────────────────────────┐   │  │   │
│  │    │   │    LEFT PANEL (40%)  │    │      RIGHT PANEL (60%)              │   │  │   │
│  │    │   │                      │    │                                      │   │  │   │
│  │    │   │  • NLP Chat          │    │  • Mapbox Map + Heatmaps            │   │  │   │
│  │    │   │  • Property List     │    │  • Property Pins                    │   │  │   │
│  │    │   │  • Filters           │    │  • 298 KPI Artifact Panel           │   │  │   │
│  │    │   │  • AI Reasoning      │    │  • Report Generator                 │   │  │   │
│  │    │   └──────────────────────┘    └─────────────────────────────────────┘   │  │   │
│  │    └─────────────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                                     │
│                                    ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           EXTERNAL DATA SOURCES                                   │   │
│  ├─────────────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                                   │   │
│  │  MICRO (Property)              │  MACRO (Market)            │  AI/ML             │   │
│  │  ─────────────────             │  ──────────────            │  ─────             │   │
│  │  • RealForeclose (Auctions)    │  • Census API              │  • LiteLLM        │   │
│  │  • BCPAO (Property Data)       │  • Zillow CSVs             │  • LangGraph      │   │
│  │  • AcclaimWeb (Liens)          │  • Walk Score API          │  • XGBoost ML     │   │
│  │  • RealTDM (Tax Certs)         │  • GreatSchools API        │  • pgvector       │   │
│  │  • Municode (Zoning)           │  • FEMA Flood Maps         │                    │   │
│  │  • Clerk of Court (Cases)      │  • County GIS              │                    │   │
│  │                                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## DFD Level 1: System Decomposition

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              LEVEL 1: PROCESS DECOMPOSITION                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  USERS                                                                                   │
│    │                                                                                     │
│    │ D1: User Query                                                                      │
│    ▼                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  P1: NLP PROCESSING LAYER                                                        │   │
│  │  ─────────────────────────                                                       │   │
│  │  • Intent Classification                                                          │   │
│  │  • Entity Extraction (parcel, address, case#)                                    │   │
│  │  • Query Routing (zoning vs auction vs analysis)                                 │   │
│  │  • Context Management                                                             │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│    │                                                                                     │
│    │ D2: Structured Query                                                               │
│    ▼                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  P2: LANGGRAPH ORCHESTRATION LAYER                                               │   │
│  │  ─────────────────────────────────                                               │   │
│  │                                                                                   │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐     │   │
│  │  │  Zoning   │  │  Parcel   │  │   Lien    │  │ Analysis  │  │  Report   │     │   │
│  │  │   Agent   │  │   Agent   │  │   Agent   │  │   Agent   │  │   Agent   │     │   │
│  │  │  (ZW-013  │  │  (ZW-001  │  │  (ZW-115  │  │  (ZW-135  │  │  (DOCX/   │     │   │
│  │  │  to 074)  │  │  to 012)  │  │  to 134)  │  │  to 176)  │  │   PDF)    │     │   │
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘     │   │
│  │        │              │              │              │              │            │   │
│  │        └──────────────┴──────────────┴──────────────┴──────────────┘            │   │
│  │                                      │                                           │   │
│  └──────────────────────────────────────┼───────────────────────────────────────────┘   │
│                                         │                                                │
│                                         │ D3: Agent Tasks                               │
│                                         ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  P3: DATA ACQUISITION LAYER                                                      │   │
│  │  ──────────────────────────                                                      │   │
│  │                                                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │ RealForeclose│  │   BCPAO     │  │ AcclaimWeb  │  │  Municode   │             │   │
│  │  │   Scraper   │  │   Scraper   │  │   Scraper   │  │   Scraper   │             │   │
│  │  │  (Auctions) │  │ (Property)  │  │   (Liens)   │  │  (Zoning)   │             │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │   │
│  │         │                │                │                │                     │   │
│  │  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐             │   │
│  │  │  RealTDM    │  │  Census     │  │   FEMA      │  │  Walk Score │             │   │
│  │  │  (Tax Certs)│  │    API      │  │ (Flood)     │  │    API      │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  │                                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                                │
│                                         │ D4: Raw Data                                  │
│                                         ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  P4: DATA PROCESSING & 298 KPI ENGINE                                            │   │
│  │  ────────────────────────────────────                                            │   │
│  │                                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐│   │
│  │  │ 298 KPI CALCULATION ENGINE                                                   ││   │
│  │  │                                                                               ││   │
│  │  │  Category 1-2:   Property + Zoning       (74 KPIs: ZW-001 to ZW-074)        ││   │
│  │  │  Category 3-5:   Auction + Financial     (58 KPIs: ZW-075 to ZW-134)        ││   │
│  │  │  Category 6:     ML Predictions          (16 KPIs: ZW-135 to ZW-150)  ⭐     ││   │
│  │  │  Category 7-8:   Physical + Investment   (26 KPIs: ZW-151 to ZW-176)  ⭐     ││   │
│  │  │  Category 9-11:  Demographics + Market   (44 KPIs: ZW-177 to ZW-220)        ││   │
│  │  │  Category 12-13: HBU + CMA Analysis      (28 KPIs: ZW-221 to ZW-248)  ⭐     ││   │
│  │  │  Category 14-17: Risk + Dev + Env        (52 KPIs: ZW-249 to ZW-298)  ⭐     ││   │
│  │  │                                                                               ││   │
│  │  │  ⭐ = BidDeed.AI/ZoneWise EXCLUSIVE (competitors don't have)                 ││   │
│  │  └─────────────────────────────────────────────────────────────────────────────┘│   │
│  │                                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐│   │
│  │  │ COMPOSITE SCORING ENGINE                                                     ││   │
│  │  │                                                                               ││   │
│  │  │  COMPOSITE = HBU (30%) + CMA (30%) + ML (40%)                               ││   │
│  │  │                                                                               ││   │
│  │  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                    ││   │
│  │  │  │ HBU ENGINE    │  │ CMA ENGINE    │  │ ML ENGINE     │                    ││   │
│  │  │  │ ZW-221 to 232 │  │ ZW-233 to 248 │  │ ZW-135 to 150 │                    ││   │
│  │  │  │               │  │               │  │               │                    ││   │
│  │  │  │ Highest &     │  │ Comparable    │  │ XGBoost       │                    ││   │
│  │  │  │ Best Use      │  │ Market        │  │ Third-Party   │                    ││   │
│  │  │  │ Analysis      │  │ Analysis      │  │ Probability   │                    ││   │
│  │  │  └───────────────┘  └───────────────┘  └───────────────┘                    ││   │
│  │  │                           │                                                  ││   │
│  │  │                           ▼                                                  ││   │
│  │  │                  ┌───────────────────┐                                       ││   │
│  │  │                  │   DECISION ENGINE │                                       ││   │
│  │  │                  │   ZW-167          │                                       ││   │
│  │  │                  │                   │                                       ││   │
│  │  │                  │ BID | REVIEW | SKIP│                                      ││   │
│  │  │                  └───────────────────┘                                       ││   │
│  │  └─────────────────────────────────────────────────────────────────────────────┘│   │
│  │                                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                                │
│                                         │ D5: Processed KPIs                            │
│                                         ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  D1: SUPABASE DATABASE (PostgreSQL + pgvector)                                   │   │
│  │  ─────────────────────────────────────────────                                   │   │
│  │                                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐│   │
│  │  │ TABLES                                                                       ││   │
│  │  │                                                                               ││   │
│  │  │ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          ││   │
│  │  │ │sample_      │  │jurisdictions│  │zoning_      │  │parcel_zones │          ││   │
│  │  │ │properties   │  │   (17)      │  │districts    │  │  (24,243)   │          ││   │
│  │  │ │ (351,423)   │  │             │  │   (290)     │  │             │          ││   │
│  │  │ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          ││   │
│  │  │                                                                               ││   │
│  │  │ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          ││   │
│  │  │ │auction_     │  │liens        │  │ml_predictions│ │kpi_values   │          ││   │
│  │  │ │properties   │  │             │  │              │  │  (298 cols) │          ││   │
│  │  │ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          ││   │
│  │  │                                                                               ││   │
│  │  │ ┌─────────────┐  ┌─────────────┐                                             ││   │
│  │  │ │ordinances   │  │census_tracts│                                             ││   │
│  │  │ │ (+ pgvector)│  │  (148)      │                                             ││   │
│  │  │ └─────────────┘  └─────────────┘                                             ││   │
│  │  └─────────────────────────────────────────────────────────────────────────────┘│   │
│  │                                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                                │
│                                         │ D6: Structured Data                           │
│                                         ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  P5: PRESENTATION LAYER (Split-Screen UI)                                        │   │
│  │  ────────────────────────────────────────                                        │   │
│  │                                                                                   │   │
│  │  ┌────────────────────────────────┐  ┌──────────────────────────────────────┐   │   │
│  │  │      LEFT PANEL (40%)          │  │      RIGHT PANEL (60%)               │   │   │
│  │  │                                │  │                                       │   │   │
│  │  │  ┌─────────────────────────┐   │  │  ┌────────────────────────────────┐  │   │   │
│  │  │  │ ChatMode.jsx            │   │  │  │ MapboxMap.jsx                  │  │   │   │
│  │  │  │ • NLP Input             │   │  │  │ • Heatmap Layers               │  │   │   │
│  │  │  │ • Streaming Response    │   │  │  │ • Property Pins (BID/REVIEW/   │  │   │   │
│  │  │  │ • Query History         │   │  │  │   SKIP color coded)            │  │   │   │
│  │  │  └─────────────────────────┘   │  │  │ • Demographic Overlays         │  │   │   │
│  │  │                                │  │  └────────────────────────────────┘  │   │   │
│  │  │  ┌─────────────────────────┐   │  │                                       │   │   │
│  │  │  │ PropertyList.jsx        │   │  │  ┌────────────────────────────────┐  │   │   │
│  │  │  │ • Sortable Cards        │   │  │  │ ArtifactPanel.jsx              │  │   │   │
│  │  │  │ • Decision Badges       │   │  │  │ (298 KPI Display)              │  │   │   │
│  │  │  │ • Quick Stats           │   │  │  │                                 │  │   │   │
│  │  │  └─────────────────────────┘   │  │  │  TABS:                          │  │   │   │
│  │  │                                │  │  │  ├── Analysis (ZW-135 to 176)   │  │   │   │
│  │  │  ┌─────────────────────────┐   │  │  │  ├── Zoning (ZW-013 to 074)     │  │   │   │
│  │  │  │ ThinkingDisplay.jsx     │   │  │  │  ├── Liens (ZW-115 to 134)      │  │   │   │
│  │  │  │ • AI Reasoning          │   │  │  │  ├── Comps (ZW-205 to 248)      │  │   │   │
│  │  │  │ • Stage Progress        │   │  │  │  ├── Demographics (ZW-177-190)  │  │   │   │
│  │  │  │ • Citations             │   │  │  │  ├── HBU (ZW-221 to 232)        │  │   │   │
│  │  │  └─────────────────────────┘   │  │  │  ├── Risk (ZW-249 to 264)       │  │   │   │
│  │  │                                │  │  │  └── Report (DOCX/PDF)          │  │   │   │
│  │  │  ┌─────────────────────────┐   │  │  │                                 │  │   │   │
│  │  │  │ FilterPanel.jsx         │   │  │  └────────────────────────────────┘  │   │   │
│  │  │  │ • Decision (BID/REVIEW/ │   │  │                                       │   │   │
│  │  │  │   SKIP)                 │   │  │  ┌────────────────────────────────┐  │   │   │
│  │  │  │ • Price Range           │   │  │  │ MarketAnalytics.jsx            │  │   │   │
│  │  │  │ • Zip Code              │   │  │  │ (Reventure.app style)          │  │   │   │
│  │  │  │ • Property Type         │   │  │  │ • Trend Charts                 │  │   │   │
│  │  │  └─────────────────────────┘   │  │  │ • ZIP Statistics               │  │   │   │
│  │  │                                │  │  └────────────────────────────────┘  │   │   │
│  │  └────────────────────────────────┘  └──────────────────────────────────────┘   │   │
│  │                                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## DFD Level 2: Detailed Process Flows

### P2.1: LangGraph Agent Orchestration Detail

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH ORCHESTRATION DETAIL                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│                              ┌─────────────────┐                                         │
│                              │   User Query    │                                         │
│                              └────────┬────────┘                                         │
│                                       │                                                  │
│                                       ▼                                                  │
│                         ┌─────────────────────────┐                                     │
│                         │    SMART ROUTER V6      │                                     │
│                         │                         │                                     │
│                         │  ┌─────────────────┐   │                                     │
│                         │  │ FREE (40-55%)   │   │  → Gemini 2.5 Flash                │
│                         │  │ ULTRA_CHEAP     │   │  → DeepSeek V3.2 ($0.28/1M)        │
│                         │  │ QUALITY         │   │  → Claude Sonnet 4.5               │
│                         │  │ COMPLEX         │   │  → Claude Opus 4.5                 │
│                         │  └─────────────────┘   │                                     │
│                         └───────────┬─────────────┘                                     │
│                                     │                                                   │
│                                     ▼                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                         LANGGRAPH STATE MACHINE                                   │  │
│  │                                                                                    │  │
│  │    START                                                                          │  │
│  │      │                                                                            │  │
│  │      ▼                                                                            │  │
│  │  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐               │  │
│  │  │ Stage 1   │───►│ Stage 2   │───►│ Stage 3   │───►│ Stage 4   │               │  │
│  │  │ Discovery │    │ Scraping  │    │ Title     │    │ Lien      │               │  │
│  │  │           │    │           │    │ Search    │    │ Priority  │               │  │
│  │  │ KPIs:     │    │ KPIs:     │    │ KPIs:     │    │ KPIs:     │               │  │
│  │  │ ZW-075-092│    │ ZW-001-012│    │ ZW-115-120│    │ ZW-121-134│               │  │
│  │  └───────────┘    └───────────┘    └───────────┘    └───────────┘               │  │
│  │       │                │                │                │                        │  │
│  │       ▼                ▼                ▼                ▼                        │  │
│  │  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐               │  │
│  │  │ Stage 5   │───►│ Stage 6   │───►│ Stage 7   │───►│ Stage 8   │               │  │
│  │  │ Tax Certs │    │Demographics│    │ ML Score  │    │ Max Bid   │               │  │
│  │  │           │    │           │    │           │    │           │               │  │
│  │  │ KPIs:     │    │ KPIs:     │    │ KPIs:     │    │ KPIs:     │               │  │
│  │  │ ZW-124-125│    │ ZW-177-204│    │ ZW-135-150│    │ ZW-165-166│               │  │
│  │  └───────────┘    └───────────┘    └───────────┘    └───────────┘               │  │
│  │       │                │                │                │                        │  │
│  │       ▼                ▼                ▼                ▼                        │  │
│  │  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐               │  │
│  │  │ Stage 9   │───►│ Stage 10  │───►│ Stage 11  │───►│ Stage 12  │               │  │
│  │  │ Decision  │    │ Report    │    │ Disposition│    │ Archive   │               │  │
│  │  │ Log       │    │ Generate  │    │           │    │           │               │  │
│  │  │           │    │           │    │           │    │           │               │  │
│  │  │ KPIs:     │    │ All 298   │    │ KPIs:     │    │ Persist   │               │  │
│  │  │ ZW-167-176│    │ KPIs →    │    │ Result    │    │ to        │               │  │
│  │  │ ZW-259-264│    │ DOCX/PDF  │    │ tracking  │    │ Supabase  │               │  │
│  │  └───────────┘    └───────────┘    └───────────┘    └───────────┘               │  │
│  │                                                           │                       │  │
│  │                                                           ▼                       │  │
│  │                                                        END                        │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### P4.1: 298 KPI Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        298 KPI PROCESSING PIPELINE                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ INPUT: Raw Data from Scrapers                                                      │  │
│  │                                                                                     │  │
│  │  RealForeclose ─┬─► Auction Data (Case#, Date, Judgment)                          │  │
│  │  BCPAO ─────────┼─► Property Data (Beds, Baths, SqFt, Photos)                     │  │
│  │  AcclaimWeb ────┼─► Lien Data (Mortgages, HOA, Tax Liens)                         │  │
│  │  Municode ──────┼─► Zoning Data (Districts, Setbacks, Uses)                       │  │
│  │  Census API ────┼─► Demographics (Income, Population, Vacancy)                    │  │
│  │  Walk Score ────┴─► Location Scores (Walk, Transit, Bike)                         │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ STAGE 1: DATA VALIDATION & NORMALIZATION                                           │  │
│  │                                                                                     │  │
│  │  • Validate parcel IDs (28-37-35 format for Brevard)                              │  │
│  │  • Normalize addresses (standardize street types)                                  │  │
│  │  • Convert data types (currency, dates, coordinates)                              │  │
│  │  • Detect missing required fields                                                  │  │
│  │  • Flag data quality issues                                                        │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ STAGE 2: KPI CALCULATION (298 KPIs across 17 categories)                          │  │
│  │                                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │ CATEGORY 1-2: Property + Zoning (74 KPIs)                                    │  │  │
│  │  │ ZW-001 to ZW-074                                                              │  │  │
│  │  │ • Direct mapping from BCPAO, Municode                                         │  │  │
│  │  │ • Spatial join for zone assignment                                            │  │  │
│  │  │ • Use table parsing for permitted/conditional uses                            │  │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │ CATEGORY 3-5: Auction + Financial + Liens (60 KPIs)                          │  │  │
│  │  │ ZW-075 to ZW-134                                                              │  │  │
│  │  │ • RealForeclose auction parsing                                               │  │  │
│  │  │ • AcclaimWeb lien priority analysis                                           │  │  │
│  │  │ • Senior lien survival calculation                                            │  │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │ CATEGORY 6: ML PREDICTIONS (16 KPIs) ⭐ EXCLUSIVE                             │  │  │
│  │  │ ZW-135 to ZW-150                                                              │  │  │
│  │  │ • XGBoost third_party_probability model                                       │  │  │
│  │  │ • Feature importance extraction                                               │  │  │
│  │  │ • Confidence scoring                                                          │  │  │
│  │  │ • SHAP value explanations                                                     │  │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │ CATEGORY 7-8: Physical + Investment (26 KPIs) ⭐ EXCLUSIVE                    │  │  │
│  │  │ ZW-151 to ZW-176                                                              │  │  │
│  │  │ • Shapira Formula™: (ARV×70%)-Repairs-$10K-MIN($25K,15%×ARV)                 │  │  │
│  │  │ • Bid/Judgment ratio calculation                                              │  │  │
│  │  │ • BID/REVIEW/SKIP decision engine                                             │  │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │ CATEGORY 9-11: Demographics + Market + Comps (44 KPIs)                       │  │  │
│  │  │ ZW-177 to ZW-220                                                              │  │  │
│  │  │ • Census API integration (ACS 5-year)                                         │  │  │
│  │  │ • Walk Score / GreatSchools APIs                                              │  │  │
│  │  │ • Comparable sales matching algorithm                                         │  │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │ CATEGORY 12-13: HBU + CMA (28 KPIs) ⭐ EXCLUSIVE                              │  │  │
│  │  │ ZW-221 to ZW-248                                                              │  │  │
│  │  │ • Highest & Best Use 4-test analysis                                          │  │  │
│  │  │ • Comparable Market Analysis adjustments                                      │  │  │
│  │  │ • ARV reconciliation                                                          │  │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │ CATEGORY 14-17: Risk + Red Flags + Dev + Env (50 KPIs) ⭐ EXCLUSIVE          │  │  │
│  │  │ ZW-249 to ZW-298                                                              │  │  │
│  │  │ • Risk assessment scoring                                                     │  │  │
│  │  │ • Red flag detection (HOA plaintiff, senior liens survive)                   │  │  │
│  │  │ • Development process timeline estimates                                      │  │  │
│  │  │ • Environmental overlay analysis (FEMA, wetlands)                            │  │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                                     │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ STAGE 3: COMPOSITE SCORING                                                         │  │
│  │                                                                                     │  │
│  │  COMPOSITE_SCORE = HBU_SCORE (30%) + CMA_SCORE (30%) + ML_SCORE (40%)             │  │
│  │                                                                                     │  │
│  │  Decision Thresholds:                                                              │  │
│  │  • BID:    Bid/Judgment Ratio ≥ 75% AND Composite ≥ 80                            │  │
│  │  • REVIEW: Bid/Judgment Ratio 60-74% OR Composite 60-79                           │  │
│  │  • SKIP:   Bid/Judgment Ratio < 60% OR Composite < 60 OR Red Flag                 │  │
│  │                                                                                     │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ OUTPUT: 298 KPIs → Supabase + UI                                                   │  │
│  │                                                                                     │  │
│  │  • Store all 298 KPIs in kpi_values table                                         │  │
│  │  • Publish to UI via Supabase Realtime                                            │  │
│  │  • Generate DOCX/PDF reports on demand                                            │  │
│  │                                                                                     │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Store Specifications

### D1: Supabase Database Schema

```sql
-- Core Tables for 298 KPI System

-- Property Identification (ZW-001 to ZW-012)
CREATE TABLE sample_properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parcel_id VARCHAR(50) UNIQUE NOT NULL,  -- ZW-001
    county VARCHAR(50) NOT NULL,            -- ZW-002
    address VARCHAR(255),                   -- ZW-003
    city VARCHAR(100),                      -- ZW-004
    zip_code VARCHAR(10),                   -- ZW-005
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    -- ... additional property fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 298 KPI Values (One row per property)
CREATE TABLE kpi_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES sample_properties(id),
    
    -- Category 1-2: Property + Zoning (ZW-001 to ZW-074)
    zw_013_zone_code VARCHAR(20),
    zw_023_min_lot_size INTEGER,
    zw_028_front_setback INTEGER,
    zw_033_max_height INTEGER,
    zw_037_permitted_uses TEXT[],
    
    -- Category 3-5: Auction + Financial (ZW-075 to ZW-134)
    zw_075_case_number VARCHAR(50),
    zw_093_opening_bid DECIMAL(12,2),
    zw_094_final_judgment DECIMAL(12,2),
    zw_117_first_mortgage DECIMAL(12,2),
    
    -- Category 6: ML Predictions (ZW-135 to ZW-150)
    zw_135_third_party_probability DECIMAL(5,4),
    zw_137_prediction_confidence DECIMAL(5,4),
    
    -- Category 7-8: Investment Scoring (ZW-151 to ZW-176)
    zw_165_max_bid_amount DECIMAL(12,2),
    zw_166_bid_judgment_ratio DECIMAL(5,4),
    zw_167_recommendation VARCHAR(10),  -- BID/REVIEW/SKIP
    
    -- Category 12-13: HBU + CMA (ZW-221 to ZW-248)
    zw_221_hbu_current_use VARCHAR(100),
    zw_227_hbu_score INTEGER,
    zw_242_cma_confidence DECIMAL(5,4),
    
    -- Category 14-17: Risk + Flags (ZW-249 to ZW-298)
    zw_257_composite_risk_score INTEGER,
    zw_259_hoa_foreclosure_warning BOOLEAN,
    zw_260_senior_lien_survives BOOLEAN,
    zw_264_do_not_bid_flag BOOLEAN,
    
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX idx_kpi_property ON kpi_values(property_id);
CREATE INDEX idx_kpi_recommendation ON kpi_values(zw_167_recommendation);
CREATE INDEX idx_kpi_composite_risk ON kpi_values(zw_257_composite_risk_score);
```

---

## External Entity Interfaces

### E1: Data Source APIs

| Source | Protocol | Auth | Rate Limit | KPIs Provided |
|--------|----------|------|------------|---------------|
| RealForeclose | HTTP/Selenium | Session | 100/hr | ZW-075 to ZW-092 |
| BCPAO | REST API | None | 500/hr | ZW-001 to ZW-012, ZW-151 to ZW-164 |
| AcclaimWeb | HTTP/Selenium | Session | 50/hr | ZW-115 to ZW-134 |
| Municode | HTTP/Scraping | None | 200/hr | ZW-013 to ZW-074 |
| Census API | REST | API Key | 500/day | ZW-177 to ZW-190 |
| Walk Score | REST | API Key | 5000/day | ZW-191 to ZW-195 |

### E2: LLM Providers (via LiteLLM Smart Router)

| Provider | Model | Tier | Cost | Use Case |
|----------|-------|------|------|----------|
| Google | Gemini 2.5 Flash | FREE | $0 | 40-55% of requests |
| DeepSeek | V3.2 | ULTRA_CHEAP | $0.28/1M | Simple analysis |
| Anthropic | Claude Sonnet 4.5 | QUALITY | ~$3/1M | Report generation |
| Anthropic | Claude Opus 4.5 | COMPLEX | ~$15/1M | HBU/CMA reasoning |

---

## Data Flow Summary

| Flow ID | From | To | Data | Format | Frequency |
|---------|------|----|----|--------|-----------|
| D1 | User | P1 | Query | Text/Voice | Real-time |
| D2 | P1 | P2 | Structured Query | JSON | Real-time |
| D3 | P2 | P3 | Agent Tasks | LangGraph State | Real-time |
| D4 | P3 | P4 | Raw Data | JSON/HTML | Per property |
| D5 | P4 | D1 | 298 KPIs | SQL Insert | Per property |
| D6 | D1 | P5 | Structured Data | Supabase Realtime | Real-time |
| D7 | P5 | User | UI Response | React Components | Real-time |

---

## Integration with Existing Documentation

This DFD integrates with:

1. **KPI_FRAMEWORK_298_COMPLETE.md** - Complete 298 KPI definitions
2. **UI_UX_MAPBOX_SPLIT_SCREEN_SPECIFICATION.md** - UI component specs
3. **ARCHITECTURE_DECISION_2026-01-25.md** - Stack decisions
4. **FULL_STACK_SPECIFICATION.md** - Technical implementation
5. **DATA_FRAMEWORK_20_PHASES_10_STAGES.md** - Data collection phases

---

*This DFD serves as the master reference for data flow through the Claude AI for Real Estate ecosystem, integrating all 298 KPIs with the split-screen UI architecture.*
