# BIDDEED.AI / ZONEWISE: Product Requirements Specification (PRS)

**Version:** 5.0  
**Date:** February 8, 2026  
**Status:** PRODUCTION ARCHITECTURE (Desktop v2.0.0)  
**Companion Document:** PRD_V5_COMPLETE.md

---

## Executive Summary

This PRS documents the technical implementation requirements for "Claude AI for Real Estate" - the unified platform combining BidDeed.AI (foreclosure auctions) and ZoneWise (zoning intelligence) with 298 KPIs, shadcn UI components, and a Mapbox-powered split-screen interface.

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [UI/UX Wireframes](#2-uiux-wireframes)
3. [shadcn Component Specifications](#3-shadcn-component-specifications)
4. [Data Flow Diagrams](#4-data-flow-diagrams)
5. [LangGraph Workflow](#5-langgraph-workflow)
6. [API Specifications](#6-api-specifications)
7. [Database Schema](#7-database-schema)
8. [Drive for Dollars Module](#8-drive-for-dollars-module)
9. [Interactive Maps Specification](#9-interactive-maps-specification)
10. [Report Generation](#10-report-generation)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Integration Matrix](#12-integration-matrix)

---

## 1. System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           CLAUDE AI FOR REAL ESTATE                                      │
│                           System Architecture V4.0                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                            PRESENTATION LAYER                                    │   │
│  │                                                                                   │   │
│  │   ┌──────────────────────────────────────────────────────────────────────────┐  │   │
│  │   │                    SPLIT-SCREEN UI (Open-claude Fork)                     │  │   │
│  │   │                                                                            │  │   │
│  │   │  ┌─────────────────────────┐    ┌──────────────────────────────────────┐ │  │   │
│  │   │  │    LEFT PANEL (40%)     │    │       RIGHT PANEL (60%)              │ │  │   │
│  │   │  │                         │    │                                       │ │  │   │
│  │   │  │  ┌───────────────────┐  │    │  ┌─────────────────────────────────┐ │ │  │   │
│  │   │  │  │ ChatMode.jsx      │  │    │  │ MapboxMap.jsx                   │ │ │  │   │
│  │   │  │  │ (NLP Interface)   │  │    │  │ • Property pins (BID/REVIEW/    │ │ │  │   │
│  │   │  │  └───────────────────┘  │    │  │   SKIP color coded)             │ │ │  │   │
│  │   │  │                         │    │  │ • Heatmap layers (6 types)      │ │ │  │   │
│  │   │  │  ┌───────────────────┐  │    │  │ • D4D route display             │ │ │  │   │
│  │   │  │  │ FilterPanel.jsx   │  │    │  │ • County boundaries             │ │ │  │   │
│  │   │  │  │ (shadcn Select)   │  │    │  └─────────────────────────────────┘ │ │  │   │
│  │   │  │  └───────────────────┘  │    │                                       │ │  │   │
│  │   │  │                         │    │  ┌─────────────────────────────────┐ │ │  │   │
│  │   │  │  ┌───────────────────┐  │    │  │ ArtifactPanel.jsx               │ │ │  │   │
│  │   │  │  │ PropertyList.jsx  │  │    │  │ (8 Tabs - 298 KPIs)             │ │ │  │   │
│  │   │  │  │ (shadcn Cards)    │  │    │  │                                 │ │ │  │   │
│  │   │  │  │                   │  │    │  │ • Analysis | Zoning | Liens    │ │ │  │   │
│  │   │  │  │ ┌───────────────┐ │  │    │  │ • Comps | Demographics | HBU   │ │ │  │   │
│  │   │  │  │ │ PropertyCard  │ │  │    │  │ • Risk | Report                │ │ │  │   │
│  │   │  │  │ │ Component     │ │  │    │  └─────────────────────────────────┘ │ │  │   │
│  │   │  │  │ └───────────────┘ │  │    │                                       │ │  │   │
│  │   │  │  └───────────────────┘  │    │  ┌─────────────────────────────────┐ │ │  │   │
│  │   │  │                         │    │  │ AuctionCalendar.jsx             │ │ │  │   │
│  │   │  │  ┌───────────────────┐  │    │  │ (shadcn Event Calendar)         │ │ │  │   │
│  │   │  │  │ThinkingDisplay.jsx│  │    │  │ PropertyOnion parity            │ │ │  │   │
│  │   │  │  │ (AI Reasoning)    │  │    │  └─────────────────────────────────┘ │ │  │   │
│  │   │  │  └───────────────────┘  │    │                                       │ │  │   │
│  │   │  └─────────────────────────┘    └──────────────────────────────────────┘ │  │   │
│  │   │                                                                            │  │   │
│  │   └──────────────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                                   │   │
│  │   React + Vite | Tailwind CSS | shadcn/ui | Mapbox GL JS | TanStack Query       │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                           │                                             │
│                                           │ WebSocket / REST                            │
│                                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                            APPLICATION LAYER                                     │   │
│  │                                                                                   │   │
│  │   ┌────────────────────────────────────────────────────────────────────────┐    │   │
│  │   │                    LANGGRAPH ORCHESTRATION                              │    │   │
│  │   │                                                                          │    │   │
│  │   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │    │   │
│  │   │  │Discovery│►│Scraping │►│Title    │►│Lien     │►│Tax      │          │    │   │
│  │   │  │Agent    │ │Agent    │ │Agent    │ │Agent    │ │Agent    │          │    │   │
│  │   │  │Stage 1  │ │Stage 2  │ │Stage 3  │ │Stage 4  │ │Stage 5  │          │    │   │
│  │   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │    │   │
│  │   │       │           │           │           │           │                │    │   │
│  │   │       ▼           ▼           ▼           ▼           ▼                │    │   │
│  │   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │    │   │
│  │   │  │Demo-    │►│ML       │►│Max Bid  │►│Decision │►│Report   │          │    │   │
│  │   │  │graphics │ │Score    │ │Calc     │ │Log      │ │Generate │          │    │   │
│  │   │  │Stage 6  │ │Stage 7  │ │Stage 8  │ │Stage 9  │ │Stage 10 │          │    │   │
│  │   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │    │   │
│  │   │                                                       │                │    │   │
│  │   │  ┌─────────┐ ┌─────────┐                             ▼                │    │   │
│  │   │  │Dispositi│►│Archive  │                    ┌─────────────────┐       │    │   │
│  │   │  │Stage 11 │ │Stage 12 │                    │ SMART ROUTER V6 │       │    │   │
│  │   │  └─────────┘ └─────────┘                    │                 │       │    │   │
│  │   │                                             │ FREE: Gemini    │       │    │   │
│  │   └─────────────────────────────────────────────│ CHEAP: DeepSeek │───────┘    │   │
│  │                                                 │ QUALITY: Sonnet │             │   │
│  │   LiteLLM | LangGraph | GitHub Actions          │ COMPLEX: Opus   │             │   │
│  └─────────────────────────────────────────────────┴─────────────────┴─────────────┘   │
│                                           │                                             │
│                                           │ PostgreSQL / pgvector                       │
│                                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                              DATA LAYER                                          │   │
│  │                                                                                   │   │
│  │   ┌─────────────────────────────────────────────────────────────────────────┐   │   │
│  │   │                    SUPABASE (PostgreSQL + pgvector)                      │   │   │
│  │   │                                                                           │   │   │
│  │   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │   │
│  │   │  │sample_      │ │auction_     │ │kpi_values   │ │zoning_      │        │   │   │
│  │   │  │properties   │ │properties   │ │(298 columns)│ │districts    │        │   │   │
│  │   │  │(351,423)    │ │             │ │             │ │(290)        │        │   │   │
│  │   │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘        │   │   │
│  │   │                                                                           │   │   │
│  │   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │   │
│  │   │  │multi_county_│ │d4d_routes   │ │d4d_photos   │ │liens        │        │   │   │
│  │   │  │auctions     │ │             │ │             │ │             │        │   │   │
│  │   │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘        │   │   │
│  │   │                                                                           │   │   │
│  │   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                         │   │   │
│  │   │  │ordinances   │ │census_tracts│ │ml_models    │                         │   │   │
│  │   │  │(+ pgvector) │ │(148)        │ │             │                         │   │   │
│  │   │  └─────────────┘ └─────────────┘ └─────────────┘                         │   │   │
│  │   │                                                                           │   │   │
│  │   └─────────────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                                   │   │
│  │   Supabase Auth | Supabase Realtime | Supabase Storage | Supabase Edge Functions │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                           │                                             │
│                                           │ HTTP / Selenium                             │
│                                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           EXTERNAL DATA SOURCES                                  │   │
│  │                                                                                   │   │
│  │   MICRO (Property-Level)              MACRO (Market-Level)       AI/ML           │   │
│  │   ───────────────────────             ──────────────────────     ─────           │   │
│  │   • RealForeclose (Auctions)          • Census API (ACS 5-yr)   • XGBoost       │   │
│  │   • BCPAO (Property + Photos)         • Zillow (via CSV)        • pgvector      │   │
│  │   • AcclaimWeb (Liens/Mortgages)      • Walk Score API          • LiteLLM       │   │
│  │   • RealTDM (Tax Certificates)        • GreatSchools API        • LangGraph     │   │
│  │   • Municode (Zoning Ordinances)      • FEMA Flood Maps         • SHAP          │   │
│  │   • Clerk of Court (Case Files)       • County GIS/TigerLine                    │   │
│  │   • MCS/Servicers (D4D Leads)         • Mapbox Geocoding                        │   │
│  │                                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. UI/UX Wireframes

### 2.1 Main Application Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  🏠 BidDeed.AI   │ 📍 Brevard County ▼ │ 📅 Jan 28, 2026 │ 🔍 │ 👤 Ariel │ ☀️/🌙      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────────────────────────┐  ┌──────────────────────────────────────────┐ │
│  │      LEFT PANEL (40%)               │  │        RIGHT PANEL (60%)                 │ │
│  │                                      │  │                                          │ │
│  │  ┌────────────────────────────────┐ │  │  ┌──────────────────────────────────────┐│ │
│  │  │ 💬 Ask anything about the       │ │  │  │                                      ││ │
│  │  │    Jan 28 Palm Bay auction...   │ │  │  │         🗺️ MAPBOX MAP                ││ │
│  │  │    ____________________________│ │  │  │                                      ││ │
│  │  │                            [↑]  │ │  │  │   🟢 BID properties (green pins)    ││ │
│  │  └────────────────────────────────┘ │  │  │   🟡 REVIEW properties (yellow pins) ││ │
│  │                                      │  │  │   ⚪ SKIP properties (gray pins)     ││ │
│  │  ┌────────────────────────────────┐ │  │  │                                      ││ │
│  │  │ 📊 Jan 28, 2026 Palm Bay       │ │  │  │   🔥 Heatmap overlay toggle          ││ │
│  │  │ Total: 7 | BID: 2 | REVIEW: 3  │ │  │  │   📍 D4D Route line                  ││ │
│  │  │ SKIP: 2                         │ │  │  │                                      ││ │
│  │  └────────────────────────────────┘ │  │  └──────────────────────────────────────┘│ │
│  │                                      │  │                                          │ │
│  │  ┌────────────────────────────────┐ │  │  ┌──────────────────────────────────────┐│ │
│  │  │ 🔧 FILTERS                      │ │  │  │  📑 ARTIFACT PANEL                  ││ │
│  │  │                                 │ │  │  │                                      ││ │
│  │  │ Decision: [All ▼]               │ │  │  │  [Analysis][Zoning][Liens][Comps]   ││ │
│  │  │ Price: [$0] to [$500K]          │ │  │  │  [Demographics][HBU][Risk][Report]  ││ │
│  │  │ Zip: [32905 ▼]                  │ │  │  │  ─────────────────────────────────  ││ │
│  │  │ Type: [SFH ▼]                   │ │  │  │                                      ││ │
│  │  └────────────────────────────────┘ │  │  │  📊 ANALYSIS TAB (Selected)          ││ │
│  │                                      │  │  │                                      ││ │
│  │  ┌────────────────────────────────┐ │  │  │  ML Prediction: 78.4%                ││ │
│  │  │ 📋 PROPERTY LIST                │ │  │  │  Confidence: 85%                    ││ │
│  │  │                                 │ │  │  │  Max Bid: $173,000                  ││ │
│  │  │ ┌───────────────────────────┐  │ │  │  │  Judgment: $215,000                  ││ │
│  │  │ │ 📸 [BCPAO Photo]          │  │ │  │  │  Ratio: 80.5%                        ││ │
│  │  │ │                           │  │ │  │  │                                      ││ │
│  │  │ │ 1470 Country Club Dr NE   │  │ │  │  │  ┌─────────────────────────────────┐││ │
│  │  │ │ Palm Bay, FL 32905        │  │ │  │  │  │ COMPOSITE SCORING               │││ │
│  │  │ │ 5bd │ 3ba │ 2,552 sqft    │  │ │  │  │  │                                 │││ │
│  │  │ │                           │  │ │  │  │  │ HBU Score:  ████████░░ 82/100   │││ │
│  │  │ │ 🟢 BID     $173,000       │  │ │  │  │  │ CMA Score:  ███████░░░ 75/100   │││ │
│  │  │ │ ML: 78%   Ratio: 80.5%    │  │ │  │  │  │ ML Score:   ████████░░ 78/100   │││ │
│  │  │ └───────────────────────────┘  │ │  │  │  │                                 │││ │
│  │  │                                 │ │  │  │  │ COMPOSITE:  ████████░░ 78/100   │││ │
│  │  │ ┌───────────────────────────┐  │ │  │  │  │ Decision:   🟢 BID              │││ │
│  │  │ │ 📸 [BCPAO Photo]          │  │ │  │  │  └─────────────────────────────────┘││ │
│  │  │ │                           │  │ │  │  │                                      ││ │
│  │  │ │ 771 Vantage St SE ⭐ D4D  │  │ │  │  │  [📄 Generate DOCX Report]          ││ │
│  │  │ │ Palm Bay, FL 32909        │  │ │  │  │                                      ││ │
│  │  │ │ 3bd │ 2ba │ 1,536 sqft    │  │ │  │  └──────────────────────────────────────┘│ │
│  │  │ │                           │  │ │  │                                          │ │
│  │  │ │ 🟢 PURSUE  $71,000        │  │ │  │  ┌──────────────────────────────────────┐│ │
│  │  │ │ D4D Find │ MCS Managed    │  │ │  │  │  🧠 AI REASONING                    ││ │
│  │  │ └───────────────────────────┘  │ │  │  │                                      ││ │
│  │  │                                 │ │  │  │  "This property shows strong        ││ │
│  │  │ ┌───────────────────────────┐  │ │  │  │   investment potential. The 80.5%   ││ │
│  │  │ │ 📸 [BCPAO Photo]          │  │ │  │  │   bid/judgment ratio exceeds our    ││ │
│  │  │ │                           │  │ │  │  │   75% threshold. ML model predicts  ││ │
│  │  │ │ 170 Bayamo Ave NE         │  │ │  │  │   78% probability of third-party    ││ │
│  │  │ │ Palm Bay, FL 32907        │  │ │  │  │   purchase. No red flags detected." ││ │
│  │  │ │ 3bd │ 2ba │ 1,456 sqft    │  │ │  │  │                                      ││ │
│  │  │ │                           │  │ │  │  │  Stage: 9/12 ████████████░░░░        ││ │
│  │  │ │ 🟡 REVIEW  $108,000       │  │ │  │  │  Processing: Decision Log            ││ │
│  │  │ │ ML: 58%   Ratio: 68%      │  │ │  │  └──────────────────────────────────────┘│ │
│  │  │ └───────────────────────────┘  │ │  │                                          │ │
│  │  │                                 │ │  └──────────────────────────────────────────┘ │
│  │  │ [Load More Properties...]       │ │                                              │
│  │  └────────────────────────────────┘ │                                              │
│  │                                      │                                              │
│  └─────────────────────────────────────┘                                              │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 PropertyOnion-Style Auction Calendar

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           AUCTION CALENDAR (PropertyOnion Parity)                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  📅 January 2026              [◀ Prev]  [Today]  [Next ▶]   [Month ▼]           │   │
│  │                                                                                   │   │
│  │  County Filter: [All Florida ▼] [Brevard ▼] [+]                                  │   │
│  │  Type Filter: [🔴 Foreclosure ✓] [🔵 Tax Deed ✓]                                 │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌───────┬───────┬───────┬───────┬───────┬───────┬───────┐                            │
│  │  Sun  │  Mon  │  Tue  │  Wed  │  Thu  │  Fri  │  Sat  │                            │
│  ├───────┼───────┼───────┼───────┼───────┼───────┼───────┤                            │
│  │       │       │       │   1   │   2   │   3   │   4   │                            │
│  │       │       │       │       │       │       │       │                            │
│  ├───────┼───────┼───────┼───────┼───────┼───────┼───────┤                            │
│  │   5   │   6   │  🔴7  │   8   │   9   │  10   │  11   │                            │
│  │       │       │  (12) │       │       │       │       │                            │
│  ├───────┼───────┼───────┼───────┼───────┼───────┼───────┤                            │
│  │  12   │  13   │ 🔴14  │  15   │ 🔵16  │  17   │  18   │                            │
│  │       │       │  (8)  │       │  (23) │       │       │                            │
│  ├───────┼───────┼───────┼───────┼───────┼───────┼───────┤                            │
│  │  19   │  20   │ 🔴21  │  22   │ 🔵23  │  24   │  25   │                            │
│  │       │       │  (15) │       │  (31) │       │       │                            │
│  ├───────┼───────┼───────┼───────┼───────┼───────┼───────┤                            │
│  │  26   │  27   │ 🔴28  │  29   │ 🔵30  │  31   │       │                            │
│  │       │       │  (7)  │       │  (18) │       │       │  ◄── Jan 28: Palm Bay      │
│  │       │       │ ★PALM │       │       │       │       │      7 properties          │
│  │       │       │  BAY  │       │       │       │       │      $1.2M total judgment  │
│  └───────┴───────┴───────┴───────┴───────┴───────┴───────┘                            │
│                                                                                          │
│  Legend:                                                                                │
│  🔴 (n) = Foreclosure Auction (n properties)                                           │
│  🔵 (n) = Tax Deed Auction (n properties)                                              │
│  ★ = Your watched/analyzed auctions                                                    │
│                                                                                          │
│  Click any date to view property list and analysis                                      │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 PropertyCard Component Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           PROPERTYCARD COMPONENT DESIGN                                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────────────────────────────────────────┐                               │
│  │                                                      │                               │
│  │              📸 BCPAO PROPERTY PHOTO                │                               │
│  │                  (aspect ratio 16:9)                 │                               │
│  │                                                      │  ┌────────────┐               │
│  │                                                      │  │  🟢 BID    │ ◄── Badge    │
│  │                                                      │  └────────────┘               │
│  └─────────────────────────────────────────────────────┘                               │
│  ┌─────────────────────────────────────────────────────┐                               │
│  │                                                      │                               │
│  │  📍 1470 Country Club Dr NE                         │ ◄── Address (truncate)        │
│  │     Palm Bay, FL 32905                              │                               │
│  │                                                      │                               │
│  │  ┌─────────┬─────────┬─────────┐                    │                               │
│  │  │ 5 bd    │ 3 ba    │ 2,552sf │                    │ ◄── Quick specs               │
│  │  └─────────┴─────────┴─────────┘                    │                               │
│  │                                                      │                               │
│  │  ┌─────────────────────┬─────────────────────┐      │                               │
│  │  │     $173,000        │         78%         │      │                               │
│  │  │     Max Bid         │     ML Confidence   │      │ ◄── Key metrics               │
│  │  │  ──────────────     │   ──────────────    │      │                               │
│  │  │     80.5%           │         82          │      │                               │
│  │  │   Bid/Judgment      │    Composite Score  │      │                               │
│  │  └─────────────────────┴─────────────────────┘      │                               │
│  │                                                      │                               │
│  │  ┌─────────────────────────────────────────────┐    │                               │
│  │  │ ████████████████████░░░░░ 80.5% of $215K   │    │ ◄── Progress bar               │
│  │  └─────────────────────────────────────────────┘    │                               │
│  │                                                      │                               │
│  │  [📄 Report] [🔗 Direct Bid] [📍 Map] [📸 Photos]   │ ◄── Action buttons           │
│  │                                                      │                               │
│  └─────────────────────────────────────────────────────┘                               │
│                                                                                          │
│  STATES:                                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ 🟢 BID       │  │ 🟡 REVIEW    │  │ ⚪ SKIP      │  │ ⭐ D4D FIND  │               │
│  │ green-500    │  │ yellow-500   │  │ gray-400     │  │ amber-500    │               │
│  │ border-l-4   │  │ border-l-4   │  │ border-l-4   │  │ border-l-4   │               │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Drive for Dollars Module Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           DRIVE FOR DOLLARS MODULE                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  🚗 D4D MODE: Jan 28 Palm Bay Route                    [Exit D4D Mode]          │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────┐  ┌────────────────────────────────────────────────┐  │
│  │    ROUTE STATUS             │  │              LIVE MAP                           │  │
│  │                             │  │                                                  │  │
│  │  📍 Stop 1/7               │  │   ┌────────────────────────────────────────┐   │  │
│  │  1470 Country Club Dr NE   │  │   │                                        │   │  │
│  │  ───────────────────────   │  │   │     🔵 Start (Satellite Beach)         │   │  │
│  │                             │  │   │          │                             │   │  │
│  │  ✅ Visited                 │  │   │          │ (2.1 mi)                    │   │  │
│  │  📸 3 photos captured       │  │   │          ▼                             │   │  │
│  │  📝 Notes: Vacant, overgrown│  │   │     ① 1511 Joshua Dr ⚪               │   │  │
│  │  🟢 Updated: BID → BID      │  │   │          │                             │   │  │
│  │                             │  │   │          │ (1.3 mi)                    │   │  │
│  │  ───────────────────────   │  │   │          ▼                             │   │  │
│  │                             │  │   │     ② 1313 Vista Oaks ⚪              │   │  │
│  │  📍 Stop 2/7               │  │   │          │                             │   │  │
│  │  771 Vantage St SE ⭐       │  │   │          │ (0.5 mi)                    │   │  │
│  │  ───────────────────────   │  │   │          ▼                             │   │  │
│  │                             │  │   │  ★ ③ 1470 Country Club 🟢 ◄── CURRENT │   │  │
│  │  ⏳ Not visited             │  │   │          │                             │   │  │
│  │  🆕 D4D DISCOVERY!          │  │   │          │ (3.5 mi)                    │   │  │
│  │  📞 Call MCS: 866-563-1100  │  │   │          ▼                             │   │  │
│  │                             │  │   │     ④ 170 Bayamo Ave 🟡               │   │  │
│  │  ───────────────────────   │  │   │          │                             │   │  │
│  │                             │  │   │          │ (1.2 mi)                    │   │  │
│  │  ROUTE SUMMARY              │  │   │          ▼                             │   │  │
│  │  Total: 22 miles            │  │   │     ⑤ 1889 Brookside 🟡               │   │  │
│  │  Est. Time: 45-55 min       │  │   │          │                             │   │  │
│  │  Stops: 7 (2 visited)       │  │   │          │ (2.8 mi)                    │   │  │
│  │  Photos: 3                  │  │   │          ▼                             │   │  │
│  │                             │  │   │     ⑥ 763 Vantage 🟡                   │   │  │
│  │  [📸 Add Photo]             │  │   │     ⭐ 771 Vantage (D4D Find)          │   │  │
│  │  [📝 Add Note]              │  │   │          │                             │   │  │
│  │  [🔄 Re-route]              │  │   │          │ (8.5 mi)                    │   │  │
│  │                             │  │   │          ▼                             │   │  │
│  └─────────────────────────────┘  │   │     🏁 Return (Satellite Beach)        │   │  │
│                                    │   │                                        │   │  │
│                                    │   └────────────────────────────────────────┘   │  │
│                                    │                                                  │  │
│                                    │   [🧭 Navigate to Next] [📊 View Analysis]      │  │
│                                    └────────────────────────────────────────────────┘  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. shadcn Component Specifications

### 3.1 Required Components

| Component | Import | Usage | Customization |
|-----------|--------|-------|---------------|
| `Card` | `@/components/ui/card` | PropertyCard, StatCard | Custom border colors for BID/REVIEW/SKIP |
| `Badge` | `@/components/ui/badge` | Decision labels | Green/Yellow/Gray variants |
| `Button` | `@/components/ui/button` | Actions | Primary, Secondary, Ghost |
| `Calendar` | `@/components/ui/calendar` | Auction calendar | Custom day rendering |
| `Select` | `@/components/ui/select` | Filters | Multi-select for counties |
| `Input` | `@/components/ui/input` | NLP chat, search | With icons |
| `Tabs` | `@/components/ui/tabs` | Artifact panel | 8 tabs |
| `Dialog` | `@/components/ui/dialog` | Property modal | Full-screen on mobile |
| `Table` | `@/components/ui/table` | Lien priority, comps | Sortable |
| `Progress` | `@/components/ui/progress` | Bid ratio visual | Color-coded |
| `Skeleton` | `@/components/ui/skeleton` | Loading states | Card skeleton |
| `Sidebar` | `@/components/ui/sidebar` | Left panel | Collapsible |

### 3.2 Component Installation

```bash
# Core components
npx shadcn@latest add card badge button calendar select input tabs dialog table progress skeleton sidebar

# Extended calendar (PropertyOnion parity)
npx shadcn@latest add "https://shadcn-event-calendar.vercel.app/r/event-calendar.json"

# Charts integration
npm install recharts
```

### 3.3 PropertyCard Implementation

```tsx
// components/property-card.tsx
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { MapPin, FileText, ExternalLink, Camera } from "lucide-react"

interface PropertyCardProps {
  // Property Identification (ZW-001 to ZW-012)
  parcel_id: string;
  address: string;
  city: string;
  zip_code: string;
  
  // Physical (ZW-151 to ZW-164)
  bedrooms: number;
  bathrooms: number;
  sqft: number;
  photo_url: string;
  
  // Financial (ZW-093 to ZW-114)
  judgment_amount: number;
  opening_bid: number;
  
  // Investment (ZW-165 to ZW-176)
  max_bid: number;
  bid_ratio: number;
  recommendation: 'BID' | 'REVIEW' | 'SKIP' | 'D4D';
  composite_score: number;
  
  // ML (ZW-135 to ZW-150)
  ml_probability: number;
  ml_confidence: number;
  
  // Auction (ZW-075 to ZW-092)
  case_number: string;
  auction_date: string;
  direct_bid_url: string;
  
  // D4D specific
  is_d4d_find?: boolean;
  d4d_notes?: string;
  d4d_photos?: string[];
}

const recommendationStyles = {
  BID: { badge: 'bg-green-500 hover:bg-green-600', border: 'border-l-4 border-green-500' },
  REVIEW: { badge: 'bg-yellow-500 hover:bg-yellow-600', border: 'border-l-4 border-yellow-500' },
  SKIP: { badge: 'bg-gray-400 hover:bg-gray-500', border: 'border-l-4 border-gray-400' },
  D4D: { badge: 'bg-amber-500 hover:bg-amber-600', border: 'border-l-4 border-amber-500' },
};

export function PropertyCard(props: PropertyCardProps) {
  const styles = recommendationStyles[props.recommendation];
  
  return (
    <Card className={`hover:shadow-lg transition-all cursor-pointer ${styles.border}`}>
      <CardHeader className="p-0 relative">
        <img 
          src={props.photo_url || '/placeholder-house.jpg'} 
          alt={props.address}
          className="w-full h-32 object-cover rounded-t-lg"
        />
        <Badge className={`absolute top-2 right-2 ${styles.badge}`}>
          {props.is_d4d_find ? '⭐ D4D FIND' : props.recommendation}
        </Badge>
        {props.d4d_photos && props.d4d_photos.length > 0 && (
          <Badge className="absolute top-2 left-2 bg-blue-500">
            <Camera className="w-3 h-3 mr-1" />
            {props.d4d_photos.length}
          </Badge>
        )}
      </CardHeader>
      
      <CardContent className="p-3 space-y-2">
        {/* Address */}
        <div>
          <h3 className="font-semibold text-sm truncate flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {props.address}
          </h3>
          <p className="text-xs text-muted-foreground">
            {props.city}, FL {props.zip_code}
          </p>
        </div>
        
        {/* Quick Specs */}
        <div className="grid grid-cols-3 gap-1 text-xs text-muted-foreground">
          <span>{props.bedrooms} bd</span>
          <span>{props.bathrooms} ba</span>
          <span>{props.sqft?.toLocaleString()} sqft</span>
        </div>
        
        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-2 pt-2">
          <div>
            <p className="text-lg font-bold text-green-600">
              ${props.max_bid.toLocaleString()}
            </p>
            <p className="text-xs text-muted-foreground">Max Bid</p>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold">
              {(props.ml_probability * 100).toFixed(0)}%
            </p>
            <p className="text-xs text-muted-foreground">ML Confidence</p>
          </div>
        </div>
        
        {/* Bid Ratio Progress */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span>Bid/Judgment Ratio</span>
            <span className="font-medium">{(props.bid_ratio * 100).toFixed(1)}%</span>
          </div>
          <Progress 
            value={props.bid_ratio * 100} 
            className={props.bid_ratio >= 0.75 ? '[&>div]:bg-green-500' : 
                       props.bid_ratio >= 0.60 ? '[&>div]:bg-yellow-500' : 
                       '[&>div]:bg-gray-400'}
          />
        </div>
        
        {/* D4D Notes */}
        {props.d4d_notes && (
          <p className="text-xs italic text-amber-600 bg-amber-50 p-2 rounded">
            📝 {props.d4d_notes}
          </p>
        )}
        
        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-2 pt-2">
          <Button size="sm" variant="outline" className="text-xs">
            <FileText className="w-3 h-3 mr-1" />
            Report
          </Button>
          <Button size="sm" variant="default" className="text-xs" asChild>
            <a href={props.direct_bid_url} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="w-3 h-3 mr-1" />
              Bid Now
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

### 3.4 AuctionCalendar Implementation

```tsx
// components/auction-calendar.tsx
import { useState } from 'react'
import { Calendar } from "@/components/ui/calendar"
import { Badge } from "@/components/ui/badge"
import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { format, startOfMonth, endOfMonth } from 'date-fns'

interface AuctionDay {
  date: string;
  foreclosure_count: number;
  tax_deed_count: number;
  total_judgment: number;
  counties: string[];
}

export function AuctionCalendar({ onDateSelect }: { onDateSelect: (date: Date) => void }) {
  const [month, setMonth] = useState(new Date())
  
  const { data: auctionDays } = useQuery({
    queryKey: ['auction-calendar', format(month, 'yyyy-MM')],
    queryFn: async () => {
      const { data } = await supabase
        .from('multi_county_auctions')
        .select('auction_date, auction_type, county, count(*), sum(judgment_amount)')
        .gte('auction_date', format(startOfMonth(month), 'yyyy-MM-dd'))
        .lte('auction_date', format(endOfMonth(month), 'yyyy-MM-dd'))
        .order('auction_date')
      
      // Group by date
      const grouped: Record<string, AuctionDay> = {}
      data?.forEach(row => {
        const date = row.auction_date
        if (!grouped[date]) {
          grouped[date] = {
            date,
            foreclosure_count: 0,
            tax_deed_count: 0,
            total_judgment: 0,
            counties: []
          }
        }
        if (row.auction_type === 'foreclosure') {
          grouped[date].foreclosure_count += row.count
        } else {
          grouped[date].tax_deed_count += row.count
        }
        grouped[date].total_judgment += row.sum || 0
        if (!grouped[date].counties.includes(row.county)) {
          grouped[date].counties.push(row.county)
        }
      })
      
      return grouped
    }
  })
  
  const getDayContent = (day: Date) => {
    const dateStr = format(day, 'yyyy-MM-dd')
    const auction = auctionDays?.[dateStr]
    
    if (!auction) return null
    
    return (
      <div className="relative w-full h-full">
        <span>{day.getDate()}</span>
        <div className="absolute -bottom-1 left-0 right-0 flex justify-center gap-0.5">
          {auction.foreclosure_count > 0 && (
            <div className="w-2 h-2 rounded-full bg-red-500" title={`${auction.foreclosure_count} foreclosures`} />
          )}
          {auction.tax_deed_count > 0 && (
            <div className="w-2 h-2 rounded-full bg-blue-500" title={`${auction.tax_deed_count} tax deeds`} />
          )}
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-4">
      <Calendar
        mode="single"
        month={month}
        onMonthChange={setMonth}
        onSelect={(date) => date && onDateSelect(date)}
        components={{
          DayContent: ({ date }) => getDayContent(date) || <span>{date.getDate()}</span>
        }}
        className="rounded-md border"
      />
      
      <div className="flex gap-4 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span>Foreclosure</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span>Tax Deed</span>
        </div>
      </div>
    </div>
  )
}
```

---

## 4. Data Flow Diagrams

*See full DFD documentation: `docs/architecture/DFD_CLAUDE_AI_REAL_ESTATE_298_KPI.md`*

### Summary Data Flows

| Flow | Description | Format | Frequency |
|------|-------------|--------|-----------|
| User → NLP | Query input | Text/Voice | Real-time |
| NLP → LangGraph | Structured query | JSON | Real-time |
| LangGraph → Scrapers | Agent tasks | LangGraph State | Per property |
| Scrapers → KPI Engine | Raw data | JSON/HTML | Per property |
| KPI Engine → Supabase | 298 KPIs | SQL Insert | Per property |
| Supabase → UI | Realtime updates | WebSocket | Real-time |
| UI → User | Split-screen display | React components | Real-time |

---

## 5. LangGraph Workflow

### State Machine Definition

```python
# langgraph/pipeline.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

class PropertyState(TypedDict):
    # Input
    case_number: str
    parcel_id: Optional[str]
    
    # Stage outputs (298 KPIs)
    kpi_values: dict  # ZW-001 to ZW-298
    
    # Processing
    current_stage: int  # 1-12
    errors: List[str]
    
    # Decision
    recommendation: Optional[str]  # BID/REVIEW/SKIP
    composite_score: Optional[float]

# Define the graph
workflow = StateGraph(PropertyState)

# Add nodes (stages)
workflow.add_node("discovery", discovery_agent)
workflow.add_node("scraping", scraping_agent)
workflow.add_node("title_search", title_agent)
workflow.add_node("lien_priority", lien_agent)
workflow.add_node("tax_certs", tax_agent)
workflow.add_node("demographics", demographics_agent)
workflow.add_node("ml_score", ml_agent)
workflow.add_node("max_bid", bid_agent)
workflow.add_node("decision_log", decision_agent)
workflow.add_node("report_generate", report_agent)
workflow.add_node("disposition", disposition_agent)
workflow.add_node("archive", archive_agent)

# Define edges
workflow.add_edge("discovery", "scraping")
workflow.add_edge("scraping", "title_search")
workflow.add_edge("title_search", "lien_priority")
workflow.add_edge("lien_priority", "tax_certs")
workflow.add_edge("tax_certs", "demographics")
workflow.add_edge("demographics", "ml_score")
workflow.add_edge("ml_score", "max_bid")
workflow.add_edge("max_bid", "decision_log")
workflow.add_edge("decision_log", "report_generate")
workflow.add_edge("report_generate", "disposition")
workflow.add_edge("disposition", "archive")
workflow.add_edge("archive", END)

# Set entry point
workflow.set_entry_point("discovery")

# Compile
app = workflow.compile()
```

---

## 6. API Specifications

### REST Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/properties` | GET | List properties with filters | JWT |
| `/api/properties/{id}` | GET | Single property with 298 KPIs | JWT |
| `/api/properties/{id}/report` | POST | Generate DOCX report | JWT |
| `/api/auctions` | GET | Auction calendar data | JWT |
| `/api/auctions/{date}` | GET | Properties for specific date | JWT |
| `/api/d4d/routes` | POST | Create optimized D4D route | JWT |
| `/api/d4d/photos` | POST | Upload D4D photo | JWT |
| `/api/chat` | POST | NLP query processing | JWT |

### Supabase Edge Functions

```typescript
// supabase/functions/generate-report/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const { property_id } = await req.json()
  
  // Fetch all 298 KPIs
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )
  
  const { data: property } = await supabase
    .from('kpi_values')
    .select('*')
    .eq('property_id', property_id)
    .single()
  
  // Generate DOCX via docx library
  // ... document generation code ...
  
  return new Response(
    JSON.stringify({ download_url: signedUrl }),
    { headers: { "Content-Type": "application/json" } }
  )
})
```

---

## 7. Database Schema

### Core Tables

```sql
-- Properties with 298 KPIs
CREATE TABLE kpi_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES sample_properties(id),
    
    -- Category 1: Property Identification (ZW-001 to ZW-012)
    zw_001_parcel_id VARCHAR(50) NOT NULL,
    zw_002_county VARCHAR(50) NOT NULL,
    zw_003_address VARCHAR(255),
    zw_004_city VARCHAR(100),
    zw_005_zip_code VARCHAR(10),
    zw_006_latitude DECIMAL(10,8),
    zw_007_longitude DECIMAL(11,8),
    zw_008_subdivision VARCHAR(255),
    zw_009_legal_description TEXT,
    zw_010_use_code VARCHAR(20),
    zw_011_property_type VARCHAR(50),
    zw_012_owner_name VARCHAR(255),
    
    -- Category 2: Zoning (ZW-013 to ZW-074)
    zw_013_zone_code VARCHAR(20),
    zw_014_zone_description VARCHAR(255),
    zw_015_jurisdiction VARCHAR(100),
    -- ... 59 more zoning KPIs ...
    
    -- Category 3-5: Auction/Financial/Liens (ZW-075 to ZW-134)
    zw_075_case_number VARCHAR(50),
    zw_076_plaintiff VARCHAR(255),
    zw_077_defendant VARCHAR(255),
    zw_093_opening_bid DECIMAL(12,2),
    zw_094_final_judgment DECIMAL(12,2),
    zw_117_first_mortgage DECIMAL(12,2),
    zw_122_hoa_lien DECIMAL(12,2),
    -- ... more financial/lien KPIs ...
    
    -- Category 6: ML Predictions (ZW-135 to ZW-150)
    zw_135_third_party_probability DECIMAL(5,4),
    zw_136_predicted_sale_price DECIMAL(12,2),
    zw_137_confidence_score DECIMAL(5,4),
    zw_138_model_version VARCHAR(20),
    -- ... more ML KPIs ...
    
    -- Category 7-8: Physical/Investment (ZW-151 to ZW-176)
    zw_152_bedrooms INTEGER,
    zw_153_bathrooms DECIMAL(3,1),
    zw_155_sqft INTEGER,
    zw_164_photo_url VARCHAR(500),
    zw_165_max_bid_amount DECIMAL(12,2),
    zw_166_bid_judgment_ratio DECIMAL(5,4),
    zw_167_recommendation VARCHAR(10),
    zw_173_estimated_roi DECIMAL(5,4),
    -- ... more investment KPIs ...
    
    -- Category 9-11: Demographics/Market/Comps (ZW-177 to ZW-220)
    zw_178_median_household_income INTEGER,
    zw_186_vacancy_rate DECIMAL(5,4),
    -- ... more demographic/market KPIs ...
    
    -- Category 12-13: HBU/CMA (ZW-221 to ZW-248)
    zw_221_current_use VARCHAR(100),
    zw_222_highest_use VARCHAR(100),
    zw_227_hbu_score INTEGER,
    zw_242_cma_confidence DECIMAL(5,4),
    -- ... more HBU/CMA KPIs ...
    
    -- Category 14-17: Risk/Flags/Dev/Env (ZW-249 to ZW-298)
    zw_257_composite_risk_score INTEGER,
    zw_259_hoa_foreclosure_warning BOOLEAN DEFAULT FALSE,
    zw_260_senior_lien_survives BOOLEAN DEFAULT FALSE,
    zw_264_do_not_bid_flag BOOLEAN DEFAULT FALSE,
    -- ... more risk/env KPIs ...
    
    -- Metadata
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- D4D Routes
CREATE TABLE d4d_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    name VARCHAR(255),
    auction_date DATE,
    properties JSONB,  -- Ordered list of property IDs
    route_geometry JSONB,  -- GeoJSON LineString
    total_distance_miles DECIMAL(6,2),
    estimated_time_minutes INTEGER,
    status VARCHAR(20) DEFAULT 'planned',  -- planned, in_progress, completed
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- D4D Photos
CREATE TABLE d4d_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES sample_properties(id),
    route_id UUID REFERENCES d4d_routes(id),
    photo_url VARCHAR(500),
    photo_type VARCHAR(50),  -- front, side, rear, street, damage, neighbor
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    notes TEXT,
    captured_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_kpi_property ON kpi_values(property_id);
CREATE INDEX idx_kpi_recommendation ON kpi_values(zw_167_recommendation);
CREATE INDEX idx_kpi_auction_date ON kpi_values(zw_091_auction_date);
CREATE INDEX idx_d4d_route_user ON d4d_routes(user_id);
CREATE INDEX idx_d4d_photos_property ON d4d_photos(property_id);
```

---

## 8. Drive for Dollars Module

### D4D Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           DRIVE FOR DOLLARS WORKFLOW                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  1. PRE-FIELD PLANNING                                                                  │
│  ───────────────────────                                                                │
│  • Select auction date (e.g., Jan 28, 2026)                                            │
│  • Filter properties by area (e.g., Palm Bay)                                          │
│  • System generates optimized route                                                     │
│  • Download offline data pack                                                           │
│                                                                                          │
│  2. FIELD EXECUTION                                                                     │
│  ───────────────────────                                                                │
│  • Navigate via optimized route                                                         │
│  • At each stop:                                                                        │
│    - Capture photos (front, side, street view)                                          │
│    - Note occupancy indicators                                                          │
│    - Assess exterior condition                                                          │
│    - Talk to neighbors if appropriate                                                   │
│    - Mark as BID/REVIEW/SKIP                                                            │
│                                                                                          │
│  3. D4D DISCOVERY                                                                       │
│  ───────────────────────                                                                │
│  • Spot distressed properties not on auction list                                       │
│  • Capture photos and GPS location                                                      │
│  • Flag as "D4D FIND" for follow-up                                                     │
│  • Research ownership (MCS, bank, etc.)                                                 │
│                                                                                          │
│  4. POST-FIELD ANALYSIS                                                                 │
│  ───────────────────────                                                                │
│  • Sync photos and notes to cloud                                                       │
│  • Update ZW-167 recommendations                                                        │
│  • Run full ZoneWise 20-phase on D4D finds                                             │
│  • Generate updated reports                                                             │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Jan 28, 2026 Palm Bay Route Data

| Stop | Address | Type | Field Status | Max Bid | Updated Rec |
|------|---------|------|--------------|---------|-------------|
| 1 | 1511 Joshua Dr NE | Condo 3/2 | OCCUPIED ❌ | — | SKIP |
| 2 | 1313 Vista Oaks Cir | Condo 3/2 | HOA Issues | — | SKIP |
| 3 | **1470 Country Club Dr** | SFH 5/3 | **VACANT ✅** | **$173K** | **BID** |
| 4 | 170 Bayamo Ave NE | SFH 3/2 | No plates | $108K | REVIEW |
| 5 | 1889 Brookside St | SFH 3/2 | Flat tire car | $102K | REVIEW |
| 6 | 763 Vantage St SE | SFH 2/2 | Likely vacant | $72K | REVIEW |
| ⭐ | **771 Vantage St SE** | SFH 3/2 | **D4D FIND** | **$71K** | **PURSUE** |

---

## 9. Interactive Maps Specification

### Mapbox Configuration

```typescript
// lib/mapbox-config.ts
export const MAPBOX_CONFIG = {
  accessToken: process.env.NEXT_PUBLIC_MAPBOX_TOKEN,
  style: 'mapbox://styles/mapbox/streets-v12',
  
  // Default view for Brevard County
  initialViewState: {
    latitude: 28.2639,
    longitude: -80.7214,
    zoom: 9
  },
  
  // Heatmap layers
  heatmapLayers: {
    price: {
      id: 'price-heatmap',
      source: 'properties',
      property: 'zw_179_median_home_value',
      colorScale: ['#313695', '#74add1', '#fee090', '#f46d43', '#a50026']
    },
    appreciation: {
      id: 'appreciation-heatmap',
      source: 'properties',
      property: 'zw_198_appreciation_yoy',
      colorScale: ['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850']
    },
    vacancy: {
      id: 'vacancy-heatmap',
      source: 'properties',
      property: 'zw_186_vacancy_rate',
      colorScale: ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027']
    },
    income: {
      id: 'income-heatmap',
      source: 'properties',
      property: 'zw_178_median_household_income',
      colorScale: ['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20']
    },
    roi: {
      id: 'roi-heatmap',
      source: 'properties',
      property: 'zw_173_estimated_roi',
      colorScale: ['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850']
    },
    risk: {
      id: 'risk-heatmap',
      source: 'properties',
      property: 'zw_257_composite_risk_score',
      colorScale: ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027']
    }
  },
  
  // Property pin colors based on ZW-167
  pinColors: {
    BID: '#22C55E',      // green-500
    REVIEW: '#EAB308',   // yellow-500
    SKIP: '#9CA3AF',     // gray-400
    D4D: '#F59E0B'       // amber-500
  },
  
  // D4D route styling
  routeStyle: {
    lineColor: '#3B82F6',  // blue-500
    lineWidth: 4,
    lineDasharray: [2, 2]
  }
};
```

### MapboxMap Component

```tsx
// components/mapbox-map.tsx
import Map, { Marker, Source, Layer, Popup } from 'react-map-gl';
import { useState } from 'react';
import { MAPBOX_CONFIG } from '@/lib/mapbox-config';

interface Property {
  id: string;
  latitude: number;
  longitude: number;
  address: string;
  recommendation: 'BID' | 'REVIEW' | 'SKIP' | 'D4D';
  max_bid: number;
}

interface MapboxMapProps {
  properties: Property[];
  d4dRoute?: GeoJSON.LineString;
  activeHeatmap?: keyof typeof MAPBOX_CONFIG.heatmapLayers;
  onPropertyClick: (property: Property) => void;
}

export function MapboxMap({ properties, d4dRoute, activeHeatmap, onPropertyClick }: MapboxMapProps) {
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  
  return (
    <Map
      mapboxAccessToken={MAPBOX_CONFIG.accessToken}
      initialViewState={MAPBOX_CONFIG.initialViewState}
      style={{ width: '100%', height: '100%' }}
      mapStyle={MAPBOX_CONFIG.style}
    >
      {/* Heatmap Layer */}
      {activeHeatmap && (
        <Source
          id="heatmap-source"
          type="geojson"
          data={{
            type: 'FeatureCollection',
            features: properties.map(p => ({
              type: 'Feature',
              geometry: { type: 'Point', coordinates: [p.longitude, p.latitude] },
              properties: { value: p[MAPBOX_CONFIG.heatmapLayers[activeHeatmap].property] }
            }))
          }}
        >
          <Layer
            id={MAPBOX_CONFIG.heatmapLayers[activeHeatmap].id}
            type="heatmap"
            paint={{
              'heatmap-weight': ['get', 'value'],
              'heatmap-intensity': 1,
              'heatmap-radius': 30,
              'heatmap-opacity': 0.7
            }}
          />
        </Source>
      )}
      
      {/* D4D Route */}
      {d4dRoute && (
        <Source type="geojson" data={d4dRoute}>
          <Layer
            id="d4d-route"
            type="line"
            paint={{
              'line-color': MAPBOX_CONFIG.routeStyle.lineColor,
              'line-width': MAPBOX_CONFIG.routeStyle.lineWidth,
              'line-dasharray': MAPBOX_CONFIG.routeStyle.lineDasharray
            }}
          />
        </Source>
      )}
      
      {/* Property Markers */}
      {properties.map((property) => (
        <Marker
          key={property.id}
          latitude={property.latitude}
          longitude={property.longitude}
          onClick={() => {
            setSelectedProperty(property);
            onPropertyClick(property);
          }}
        >
          <div
            className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold cursor-pointer shadow-md"
            style={{ backgroundColor: MAPBOX_CONFIG.pinColors[property.recommendation] }}
          >
            {property.recommendation === 'D4D' ? '⭐' : property.recommendation[0]}
          </div>
        </Marker>
      ))}
      
      {/* Popup */}
      {selectedProperty && (
        <Popup
          latitude={selectedProperty.latitude}
          longitude={selectedProperty.longitude}
          onClose={() => setSelectedProperty(null)}
          closeOnClick={false}
        >
          <div className="p-2">
            <p className="font-semibold">{selectedProperty.address}</p>
            <p className="text-sm">Max Bid: ${selectedProperty.max_bid.toLocaleString()}</p>
            <p className={`text-sm font-medium ${
              selectedProperty.recommendation === 'BID' ? 'text-green-600' :
              selectedProperty.recommendation === 'REVIEW' ? 'text-yellow-600' :
              'text-gray-600'
            }`}>
              {selectedProperty.recommendation}
            </p>
          </div>
        </Popup>
      )}
    </Map>
  );
}
```

---

## 10. Report Generation

### DOCX Template Structure

See PRD V4 Section 11 for full template specification.

### Report Generation Flow

```
User clicks "Generate Report"
         │
         ▼
┌─────────────────────────┐
│ Supabase Edge Function  │
│ /functions/generate-report │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Fetch all 298 KPIs      │
│ for property_id         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Generate DOCX using     │
│ docx library            │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Upload to Supabase      │
│ Storage                 │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Return signed URL       │
│ (24hr expiry)           │
└───────────┴─────────────┘
```

---

## 11. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           DEPLOYMENT ARCHITECTURE                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                           CLOUDFLARE EDGE                                         │  │
│  │                                                                                    │  │
│  │   ┌─────────────────────────┐    ┌─────────────────────────────────────────┐    │  │
│  │   │  Cloudflare Pages       │    │  Cloudflare Workers                      │    │  │
│  │   │  (Frontend - React)     │    │  (Edge Functions)                        │    │  │
│  │   │                         │    │                                          │    │  │
│  │   │  • biddeed.ai           │    │  • api.biddeed.ai                        │    │  │
│  │   │  • zonewise.io          │    │  • Caching                               │    │  │
│  │   │                         │    │  • Rate limiting                         │    │  │
│  │   └─────────────────────────┘    └─────────────────────────────────────────┘    │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
│                                           │ HTTPS                                       │
│                                           ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                           SUPABASE CLOUD                                          │  │
│  │                                                                                    │  │
│  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │  │
│  │   │ PostgreSQL  │ │  pgvector   │ │  Realtime   │ │   Storage   │               │  │
│  │   │  + RLS      │ │ (embeddings)│ │ (WebSocket) │ │  (Photos)   │               │  │
│  │   └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘               │  │
│  │                                                                                    │  │
│  │   ┌─────────────┐ ┌─────────────┐                                                │  │
│  │   │    Auth     │ │    Edge     │                                                │  │
│  │   │  (JWT/OAuth)│ │  Functions  │                                                │  │
│  │   └─────────────┘ └─────────────┘                                                │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
│                                           │ Internal                                    │
│                                           ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                           GITHUB ACTIONS                                          │  │
│  │                                                                                    │  │
│  │   ┌─────────────────────────────────────────────────────────────────────────┐   │  │
│  │   │                    LANGGRAPH PIPELINE                                     │   │  │
│  │   │                                                                           │   │  │
│  │   │  Scheduled: Daily 11 PM EST                                               │   │  │
│  │   │  Triggered: On new auction dates                                          │   │  │
│  │   │                                                                           │   │  │
│  │   │  master_scraper.yml:                                                      │   │  │
│  │   │  • Brevard (current)                                                      │   │  │
│  │   │  • 67 FL counties (Q2 2026)                                               │   │  │
│  │   └─────────────────────────────────────────────────────────────────────────┘   │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
│                                           │ Scale Compute (50+ counties)               │
│                                           ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │                           RENDER.COM                                              │  │
│  │                                                                                    │  │
│  │   ┌─────────────────────────┐    ┌─────────────────────────────────────────┐    │  │
│  │   │  Cron Jobs              │    │  Background Workers                      │    │  │
│  │   │  (Multi-county scraping)│    │  (ML model training)                     │    │  │
│  │   └─────────────────────────┘    └─────────────────────────────────────────┘    │  │
│  │                                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---



### Desktop Distribution (NEW — v2.0.0)

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                        ZONEWISE DESKTOP v2.0.0                                        │
│                        (Craft Agents OSS v0.4.0 Fork)                                 │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  ┌───────────────────────────────┐    ┌──────────────────────────────────────────┐  │
│  │   ELECTRON APP               │    │   LLM CONNECTIONS                         │  │
│  │   • Claude Agent SDK 0.2.34  │    │   • Anthropic (Claude Opus 4.6/Sonnet)   │  │
│  │   • Multi-Session Inbox      │    │   • OpenRouter (multi-model)              │  │
│  │   • MCP Integration          │    │   • Codex/OpenAI (OAuth)                  │  │
│  │   • Permission Modes         │    │   • Custom endpoints                      │  │
│  │   • Focus Mode               │    │   • Per-workspace defaults                │  │
│  └───────────────────────────────┘    └──────────────────────────────────────────┘  │
│                    │                                    │                             │
│                    ▼                                    ▼                             │
│  ┌───────────────────────────────┐    ┌──────────────────────────────────────────┐  │
│  │   ZONEWISE CUSTOMIZATIONS    │    │   SKILLS & SOURCES                        │  │
│  │   • Navy theme (#1E3A5F)     │    │   • ~/.agents/skills/ (cross-tool)       │  │
│  │   • ZoneWise Agent API       │    │   • Supabase source (67 counties)        │  │
│  │   • Master Intelligence Skill│    │   • MCP servers (stdio/OAuth)             │  │
│  │   • Custom statuses/labels   │    │   • Auto OAuth token refresh              │  │
│  └───────────────────────────────┘    └──────────────────────────────────────────┘  │
│                                                                                       │
│  Platforms: Windows x64 (177MB) | macOS ARM (178MB) | macOS Intel (189MB) | Linux    │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Desktop Release History

| Version | Date | Key Features |
|---------|------|-------------|
| v1.0.0 | Jan 27, 2026 | Initial branded release (Craft Agents v0.3.1) |
| v1.0.1 | Jan 27, 2026 | Branding fixes |
| **v2.0.0** | **Feb 8, 2026** | **Multi-provider LLM, Codex/OpenAI, Opus 4.6, per-workspace defaults** |


---

## 12. Integration Matrix

### Document Cross-References

| This PRS Section | Related PRD Section | Related Architecture Doc |
|------------------|---------------------|-------------------------|
| System Architecture | 13. Tech Stack | ARCHITECTURE_DECISION_2026-01-25.md |
| Desktop Distribution | 13. Tech Stack | RELEASE_v2.0.0.md (zonewise-desktop repo) |
| UI/UX Wireframes | 5. UI/UX Specification | UI_UX_MAPBOX_SPLIT_SCREEN_SPECIFICATION.md |
| shadcn Components | 6. shadcn Component Library | FULL_STACK_SPECIFICATION.md |
| Data Flow Diagrams | 4. Data Flow Architecture | DFD_CLAUDE_AI_REAL_ESTATE_298_KPI.md |
| LangGraph Workflow | 9. LangGraph Pipeline | MASTER_INTEGRATION.md |
| Database Schema | - | SUPABASE_INTEGRATION.md |
| D4D Module | 8. Drive for Dollars | (this document) |
| Interactive Maps | - | UI_UX_MAPBOX_SPLIT_SCREEN_SPECIFICATION.md |

### KPI ↔ Component Matrix

| UI Component | KPIs Used | Count |
|--------------|-----------|-------|
| PropertyCard | ZW-001 to ZW-012, ZW-151 to ZW-167 | 29 |
| AuctionCalendar | ZW-075 to ZW-092 | 18 |
| AnalysisTab | ZW-093 to ZW-114, ZW-135 to ZW-176 | 64 |
| ZoningTab | ZW-013 to ZW-074 | 62 |
| LiensTab | ZW-115 to ZW-134, ZW-259 to ZW-264 | 26 |
| CompsTab | ZW-205 to ZW-248 | 44 |
| DemographicsTab | ZW-177 to ZW-204 | 28 |
| HBUTab | ZW-221 to ZW-232 | 12 |
| RiskTab | ZW-249 to ZW-258 | 10 |
| MapboxHeatmaps | ZW-178, ZW-179, ZW-186, ZW-198, ZW-173, ZW-257 | 6 |

---

## Appendix: Jan 28, 2026 Palm Bay Auction Data

### Properties Analyzed

```json
{
  "auction_date": "2026-01-28",
  "county": "Brevard",
  "city": "Palm Bay",
  "total_properties": 7,
  "recommendations": {
    "BID": 2,
    "REVIEW": 3,
    "SKIP": 2
  },
  "d4d_finds": 1,
  "total_judgment": 1200000,
  "properties": [
    {
      "address": "1470 Country Club Dr NE",
      "zip": "32905",
      "beds": 5,
      "baths": 3,
      "sqft": 2552,
      "judgment": 215000,
      "max_bid": 173000,
      "recommendation": "BID",
      "field_status": "VACANT",
      "ml_confidence": 0.78
    },
    {
      "address": "771 Vantage St SE",
      "zip": "32909",
      "beds": 3,
      "baths": 2,
      "sqft": 1536,
      "judgment": null,
      "max_bid": 71000,
      "recommendation": "D4D",
      "field_status": "VACANT (MCS Managed)",
      "d4d_find": true,
      "servicer_phone": "866-563-1100"
    }
  ]
}
```

---

*PRS V4.0 - BidDeed.AI / ZoneWise: Claude AI for Real Estate*  
*January 25, 2026*


---

## CHANGELOG

### V5.0 (February 8, 2026)
- Added Desktop Distribution section with ZoneWise Desktop v2.0.0 architecture
- Multi-provider LLM connection specifications (Anthropic, OpenRouter, Codex/OpenAI)
- Per-workspace default connection and theme configuration
- Claude Agent SDK 0.2.34 integration details
- `.agents/skills` cross-tool convention (Codex, Gemini compatibility)
- OAuth token auto-refresh for MCP sources
- Desktop release history tracking
- Updated Integration Matrix with desktop cross-references

### V4.0 (January 25, 2026)
- Initial unified PRS for BidDeed.AI/ZoneWise platform
- System architecture with split-screen UI
- LangGraph pipeline specifications
- 298 KPI implementation details
