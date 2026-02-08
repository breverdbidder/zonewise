# BIDDEED.AI / ZONEWISE: Product Requirements Document (PRD)

**Version:** 5.0  
**Date:** February 8, 2026  
**Status:** PRODUCTION ARCHITECTURE (Desktop v2.0.0)  
**Codename:** "Claude AI for Real Estate"

---

## Executive Summary

BidDeed.AI / ZoneWise is a unified real estate intelligence platform combining:
- **BidDeed.AI**: Foreclosure auction intelligence with ML predictions
- **ZoneWise**: Zoning & land use intelligence for development analysis
- **Claude AI Interface**: Split-screen NLP chatbot with artifacts
- **ZoneWise Desktop v2.0.0**: Craft Agents v0.4.0 fork with multi-provider LLM support

**Core Differentiator:** 298 unique KPIs (3x PropertyOnion's 96) processed through a 12-stage LangGraph pipeline, displayed via a Mapbox-powered split-screen UI with shadcn components.

---

## Table of Contents

1. [Product Vision](#1-product-vision)
2. [Target Users](#2-target-users)
3. [298 KPI Framework](#3-298-kpi-framework)
4. [Data Flow Architecture (DFD)](#4-data-flow-architecture)
5. [UI/UX Specification](#5-uiux-specification)
6. [shadcn Component Library](#6-shadcn-component-library)
7. [PropertyOnion Feature Parity](#7-propertyonion-feature-parity)
8. [Drive for Dollars Module](#8-drive-for-dollars-module)
9. [LangGraph Pipeline](#9-langgraph-pipeline)
10. [Composite Scoring Engine](#10-composite-scoring-engine)
11. [Report Generation](#11-report-generation)
12. [Multi-County Expansion](#12-multi-county-expansion)
13. [Tech Stack](#13-tech-stack)
14. [Competitive Positioning](#14-competitive-positioning)
15. [Roadmap](#15-roadmap)

---

## 1. Product Vision

### Mission Statement
*"Distressed Assets Decoded. For Everyone. Everywhere."*

### Product Philosophy
- **Data is the moat** - Everything else is a wrapper
- **Agentic AI ecosystem** - NOT traditional SaaS
- **Internal alpha first** - Build for ourselves, then commercialize

### Value Proposition

| Metric | Internal Alpha Value |
|--------|---------------------|
| Extra deals per quarter | 1 × $50K = $50K |
| Avoided losses per quarter | 1 × $100K = $100K |
| Time savings per quarter | $50K equivalent |
| **Annual Value** | **$300-400K** |
| Annual Cost | $3.3K |
| **ROI** | **100x** |

---

## 2. Target Users

### Primary Personas

| Persona | Use Case | Key Features Needed |
|---------|----------|---------------------|
| **Foreclosure Investor** (Ariel) | Auction bidding, lien analysis | ML predictions, max bid calc |
| **Real Estate Broker** | Market analysis, comps | CMA engine, demographic data |
| **Developer** | Site feasibility, zoning | HBU analysis, development process |
| **Lender** | Risk assessment, valuations | Composite scoring, red flags |

### Secondary Personas
- Title companies (lien priority analysis)
- Property appraisers (CMA data)
- City planners (zoning lookups)

---

## 3. 298 KPI Framework

### KPI Distribution

```
┌─────────────────────────────────────────────────────────────────────┐
│                    298 UNIFIED KPI FRAMEWORK                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PROPERTYONION REPLICATED (96 KPIs)                                 │
│  ├── Property Basics: ZW-001 to ZW-012 (12)                         │
│  ├── Auction Info: ZW-075 to ZW-092 (18)                            │
│  ├── Financial: ZW-093 to ZW-114 (22)                               │
│  ├── Liens: ZW-115 to ZW-134 (20)                                   │
│  ├── Physical: ZW-151 to ZW-164 (14)                                │
│  └── Market: ZW-191 to ZW-200 (10)                                  │
│                                                                      │
│  BIDDEED.AI EXCLUSIVE (74 KPIs) ⭐                                   │
│  ├── ML Predictions: ZW-135 to ZW-150 (16)                          │
│  ├── Investment Scoring: ZW-165 to ZW-176 (12)                      │
│  ├── Risk Assessment: ZW-249 to ZW-258 (10)                         │
│  ├── Demographics: ZW-177 to ZW-190 (14)                            │
│  ├── Comps Deep: ZW-205 to ZW-220 (16)                              │
│  └── Red Flags: ZW-259 to ZW-264 (6)                                │
│                                                                      │
│  ZONEWISE EXCLUSIVE (128 KPIs) ⭐                                    │
│  ├── Zoning & Land Use: ZW-013 to ZW-074 (62)                       │
│  ├── HBU Analysis: ZW-221 to ZW-232 (12)                            │
│  ├── CMA Deep: ZW-233 to ZW-248 (16)                                │
│  ├── Development Process: ZW-265 to ZW-280 (16)                     │
│  └── Environmental: ZW-281 to ZW-298 (18)                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Competitive Comparison

| Platform | Total KPIs | ML Predictions | HBU Analysis | Zoning Data |
|----------|------------|----------------|--------------|-------------|
| **BidDeed/ZoneWise** | **298** | ✅ 16 | ✅ 12 | ✅ 62 |
| PropertyOnion | 96 | ❌ 0 | ❌ 0 | ❌ 0 |
| Gridics | 74 | ❌ 0 | ⚠️ 3 | ✅ 45 |
| Zoneomics | 66 | ❌ 0 | ❌ 0 | ✅ 52 |

---

## 4. Data Flow Architecture

### DFD Level 0: Context Diagram

```
                    ┌─────────────────────────────┐
                    │         USERS               │
                    │  (Investor/Broker/Developer)│
                    └─────────────┬───────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                  CLAUDE AI FOR REAL ESTATE                           │
│                  (298 KPI Processing System)                         │
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    SPLIT-SCREEN UI                           │   │
│   │   ┌────────────────────┐    ┌──────────────────────────┐    │   │
│   │   │  LEFT PANEL (40%)  │    │   RIGHT PANEL (60%)      │    │   │
│   │   │  • NLP Chat        │    │   • Mapbox + Heatmaps    │    │   │
│   │   │  • Property List   │    │   • 298 KPI Artifacts    │    │   │
│   │   │  • Filters         │    │   • Report Generator     │    │   │
│   │   └────────────────────┘    └──────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL DATA SOURCES                           │
│                                                                      │
│  MICRO (Property)           │  MACRO (Market)       │  AI/ML        │
│  • RealForeclose            │  • Census API         │  • LiteLLM    │
│  • BCPAO                    │  • Zillow CSVs        │  • LangGraph  │
│  • AcclaimWeb               │  • Walk Score API     │  • XGBoost ML │
│  • RealTDM                  │  • FEMA Flood Maps    │  • pgvector   │
│  • Municode                 │  • County GIS         │               │
└─────────────────────────────────────────────────────────────────────┘
```

### DFD Level 1: Process Decomposition

| Process | Description | KPIs Produced |
|---------|-------------|---------------|
| **P1: NLP Processing** | Intent classification, entity extraction | Query routing |
| **P2: LangGraph Orchestration** | 12-stage pipeline execution | All 298 |
| **P3: Data Acquisition** | Scraper coordination | ZW-001 to ZW-134 |
| **P4: 298 KPI Engine** | Calculation, scoring, ML | ZW-135 to ZW-298 |
| **P5: Presentation** | UI rendering, reports | Display |

---

## 5. UI/UX Specification

### Split-Screen Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HEADER: County Selector | Auction Date | User Auth | Theme Toggle          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────┐    ┌───────────────────────────────────────┐  │
│  │    LEFT PANEL (40%)     │    │        RIGHT PANEL (60%)              │  │
│  │                         │    │                                        │  │
│  │  ┌───────────────────┐  │    │  ┌────────────────────────────────┐   │  │
│  │  │ NLP Chat Input    │  │    │  │     MAPBOX MAP                 │   │  │
│  │  │ "Ask about any    │  │    │  │                                │   │  │
│  │  │  property..."     │  │    │  │  • Property Pins (BID/REVIEW/  │   │  │
│  │  └───────────────────┘  │    │  │    SKIP color coded)           │   │  │
│  │                         │    │  │  • Heatmap Layers              │   │  │
│  │  ┌───────────────────┐  │    │  │  • County Boundaries           │   │  │
│  │  │ Quick Stats Bar   │  │    │  │  • Demographic Overlays        │   │  │
│  │  │ Total: 45 | BID:12│  │    │  │                                │   │  │
│  │  │ REVIEW:8 | SKIP:25│  │    │  └────────────────────────────────┘   │  │
│  │  └───────────────────┘  │    │                                        │  │
│  │                         │    │  ┌────────────────────────────────┐   │  │
│  │  ┌───────────────────┐  │    │  │     ARTIFACT PANEL             │   │  │
│  │  │ Filter Panel      │  │    │  │     (298 KPI Display)          │   │  │
│  │  │ • Decision Type   │  │    │  │                                │   │  │
│  │  │ • Price Range     │  │    │  │  TABS:                         │   │  │
│  │  │ • Zip Code        │  │    │  │  ├── Analysis (ML/Investment)  │   │  │
│  │  │ • Property Type   │  │    │  │  ├── Zoning (62 KPIs)          │   │  │
│  │  └───────────────────┘  │    │  │  ├── Liens (Priority Diagram)  │   │  │
│  │                         │    │  │  ├── Comps (CMA Analysis)      │   │  │
│  │  ┌───────────────────┐  │    │  │  ├── Demographics              │   │  │
│  │  │ Property List     │  │    │  │  ├── HBU (Highest & Best Use)  │   │  │
│  │  │ (Sortable Cards)  │  │    │  │  ├── Risk (Red Flags)          │   │  │
│  │  │                   │  │    │  │  └── Report (DOCX/PDF)         │   │  │
│  │  │ ┌───────────────┐ │  │    │  │                                │   │  │
│  │  │ │ 1470 Country  │ │  │    │  └────────────────────────────────┘   │  │
│  │  │ │ Club Dr       │ │  │    │                                        │  │
│  │  │ │ 🟢 BID $173K  │ │  │    │                                        │  │
│  │  │ └───────────────┘ │  │    │                                        │  │
│  │  └───────────────────┘  │    │                                        │  │
│  │                         │    │                                        │  │
│  │  ┌───────────────────┐  │    │                                        │  │
│  │  │ AI Reasoning      │  │    │                                        │  │
│  │  │ (ThinkingDisplay) │  │    │                                        │  │
│  │  └───────────────────┘  │    │                                        │  │
│  └─────────────────────────┘    └───────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Property Card Design (shadcn)

```tsx
// PropertyCard.tsx - shadcn/ui implementation
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface PropertyCardProps {
  address: string;                    // ZW-003
  photo_url: string;                  // ZW-164
  recommendation: 'BID' | 'REVIEW' | 'SKIP';  // ZW-167
  max_bid: number;                    // ZW-165
  judgment: number;                   // ZW-094
  bid_ratio: number;                  // ZW-166
  ml_confidence: number;              // ZW-137
  bedrooms: number;                   // ZW-152
  bathrooms: number;                  // ZW-153
  sqft: number;                       // ZW-155
  case_number: string;                // ZW-075
}

export function PropertyCard({ ...props }: PropertyCardProps) {
  const badgeColor = {
    BID: 'bg-green-500',
    REVIEW: 'bg-yellow-500',
    SKIP: 'bg-gray-400'
  };

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer">
      <CardHeader className="p-0">
        <img 
          src={props.photo_url} 
          alt={props.address}
          className="w-full h-32 object-cover rounded-t-lg"
        />
        <Badge className={`absolute top-2 right-2 ${badgeColor[props.recommendation]}`}>
          {props.recommendation}
        </Badge>
      </CardHeader>
      <CardContent className="p-3">
        <h3 className="font-semibold text-sm truncate">{props.address}</h3>
        <div className="grid grid-cols-3 gap-1 text-xs text-muted-foreground mt-1">
          <span>{props.bedrooms}bd</span>
          <span>{props.bathrooms}ba</span>
          <span>{props.sqft.toLocaleString()} sqft</span>
        </div>
        <div className="flex justify-between items-center mt-2">
          <div>
            <p className="text-lg font-bold text-green-600">
              ${props.max_bid.toLocaleString()}
            </p>
            <p className="text-xs text-muted-foreground">
              {(props.bid_ratio * 100).toFixed(0)}% of judgment
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium">{(props.ml_confidence * 100).toFixed(0)}%</p>
            <p className="text-xs text-muted-foreground">ML Confidence</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## 6. shadcn Component Library

### Required Components

| Component | Purpose | Status |
|-----------|---------|--------|
| **Card** | Property cards, stat cards | ✅ Core |
| **Badge** | BID/REVIEW/SKIP labels | ✅ Core |
| **Calendar** | Auction calendar (PropertyOnion parity) | ✅ Install |
| **Dialog** | Property detail modal | ✅ Core |
| **Tabs** | Artifact panel tabs | ✅ Core |
| **Select** | County selector, filters | ✅ Core |
| **Input** | NLP chat input, search | ✅ Core |
| **Button** | Actions, filters | ✅ Core |
| **Skeleton** | Loading states | ✅ Core |
| **Table** | Lien priority, comps | ✅ Core |
| **Chart** | Trend lines (Recharts) | ✅ Integration |
| **Sidebar** | Left panel layout | ✅ Install |

### shadcn Event Calendar (PropertyOnion Parity)

```bash
# Install event calendar component
npx shadcn@latest add "https://shadcn-event-calendar.vercel.app/r/event-calendar.json"
```

```tsx
// AuctionCalendar.tsx
import { Calendar } from "@/components/ui/calendar"
import { useQuery } from "@tanstack/react-query"
import { supabase } from "@/lib/supabase"

export function AuctionCalendar() {
  const { data: auctions } = useQuery({
    queryKey: ['auction-calendar'],
    queryFn: async () => {
      const { data } = await supabase
        .from('multi_county_auctions')
        .select('auction_date, county, auction_type, count')
        .gte('auction_date', startOfMonth(new Date()))
        .lte('auction_date', endOfMonth(new Date()))
      return data
    }
  })

  // Count auctions per date
  const auctionDates = auctions?.reduce((acc, auction) => {
    const date = auction.auction_date
    acc[date] = (acc[date] || 0) + auction.count
    return acc
  }, {} as Record<string, number>)

  return (
    <Calendar
      mode="single"
      modifiers={{
        hasAuction: Object.keys(auctionDates || {}).map(d => new Date(d)),
      }}
      modifiersStyles={{
        hasAuction: { 
          backgroundColor: '#fee2e2',
          fontWeight: 'bold'
        },
      }}
      components={{
        DayContent: ({ date }) => {
          const count = auctionDates?.[format(date, 'yyyy-MM-dd')]
          return (
            <div className="relative">
              {date.getDate()}
              {count && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                  {count}
                </span>
              )}
            </div>
          )
        }
      }}
      onDayClick={(date) => 
        router.push(`/auctions/${format(date, 'yyyy-MM-dd')}`)
      }
    />
  )
}
```

---

## 7. PropertyOnion Feature Parity

### Feature Comparison Matrix

| PropertyOnion Feature | Status | Our Implementation |
|----------------------|--------|-------------------|
| **Auction Calendar** | ✅ Parity | shadcn Event Calendar + Supabase |
| **Property Cards** | ✅ Enhanced | shadcn Card + 298 KPIs |
| **County Filter** | ✅ Parity | shadcn Select + 67 counties |
| **Price Heatmap** | ✅ Enhanced | Mapbox heatmap layers |
| **Direct Bid Links** | ✅ Parity | RealForeclose/RealAuction URLs |
| **Case Details** | ✅ Enhanced | 8 artifact tabs vs 1 page |
| **Photo Gallery** | ✅ Enhanced | BCPAO + Street View |
| **Lien Search** | ✅ Enhanced | Priority analysis + survival calc |
| **Export to PDF** | ✅ Enhanced | DOCX with all 298 KPIs |
| **ML Predictions** | 🆕 Exclusive | XGBoost third-party probability |
| **HBU Analysis** | 🆕 Exclusive | 12 KPIs, 4-test methodology |
| **Zoning Data** | 🆕 Exclusive | 62 KPIs, Municode scraping |

### Direct Bid URL Integration

```typescript
// Generate direct bid URLs for each auction platform
const AUCTION_URLS = {
  // Foreclosures
  'brevard': 'https://brevard.realforeclose.com',
  'orange': 'https://orange.realforeclose.com',
  'hillsborough': 'https://hillsborough.realforeclose.com',
  'miami-dade': 'https://miamidade.realforeclose.com',
  'broward': 'https://broward.realforeclose.com',
  'palm-beach': 'https://palmbeach.realforeclose.com',
  // ... 67 total FL counties
};

// Tax Deeds use different URL pattern
const TAX_DEED_URLS = {
  'brevard': 'https://brevard.realtaxdeed.com',
  // etc.
};

function getDirectBidUrl(county: string, caseNumber: string, type: 'foreclosure' | 'tax_deed') {
  const baseUrl = type === 'foreclosure' 
    ? AUCTION_URLS[county] 
    : TAX_DEED_URLS[county];
  return `${baseUrl}/index.cfm?zession=&action=SALE&SALEID=${caseNumber}`;
}
```

---

## 8. Drive for Dollars Module

### Overview

The Drive for Dollars (D4D) module enables field research with:
- Optimized driving routes
- On-site property assessment
- Photo capture and tagging
- Real-time ZoneWise 20-phase analysis
- Discovery of non-auction opportunities

### Jan 28, 2026 Palm Bay Auction Example

| Property | Type | Status | Max Bid | Rec |
|----------|------|--------|---------|-----|
| **1470 Country Club Dr** | SFH 5/3 | VACANT ✅ | **$173K** | **BID** |
| **771 Vantage St** ⭐ D4D | SFH 3/2 | VACANT (MCS) | **$71K** | **PURSUE** |
| 170 Bayamo Ave | SFH 3/2 | No plates on cars | $108K | REVIEW |
| 1889 Brookside St | SFH 3/2 | Flat tire car | $102K | REVIEW |
| 763 Vantage St | SFH 2/2 | Likely vacant | $72K | REVIEW |
| 1511 Joshua Dr | Condo 3/2 | OCCUPIED | — | SKIP |
| 1313 Vista Oaks Cir | Condo 3/2 | Same issues | — | SKIP |

### D4D Route Map Integration

```tsx
// D4DRouteMap.tsx - Mapbox optimized route display
import Map, { Marker, Source, Layer } from 'react-map-gl';

export function D4DRouteMap({ properties, route }) {
  return (
    <Map
      mapboxAccessToken={process.env.MAPBOX_TOKEN}
      initialViewState={{
        latitude: 27.99,
        longitude: -80.65,
        zoom: 11
      }}
      style={{ width: '100%', height: '400px' }}
      mapStyle="mapbox://styles/mapbox/streets-v12"
    >
      {/* Optimized driving route */}
      <Source type="geojson" data={route}>
        <Layer
          id="route"
          type="line"
          paint={{
            'line-color': '#3b82f6',
            'line-width': 4
          }}
        />
      </Source>

      {/* Property markers with sequence numbers */}
      {properties.map((prop, idx) => (
        <Marker
          key={prop.id}
          latitude={prop.latitude}
          longitude={prop.longitude}
        >
          <div className={`
            w-8 h-8 rounded-full flex items-center justify-center text-white font-bold
            ${prop.recommendation === 'BID' ? 'bg-green-500' : 
              prop.recommendation === 'REVIEW' ? 'bg-yellow-500' : 'bg-gray-400'}
          `}>
            {idx + 1}
          </div>
        </Marker>
      ))}
    </Map>
  );
}
```

### D4D Photo Capture Workflow

```
1. User clicks property pin on map
2. "Start Field Assessment" button appears
3. Camera opens for photo capture
4. Photos tagged with:
   - GPS coordinates
   - Timestamp
   - Property ID (ZW-001)
   - Assessment notes
5. AI analyzes photos for:
   - Occupancy indicators (cars, lights, mail)
   - Condition indicators (roof, landscaping, damage)
   - Security concerns (boarded windows, notices)
6. Updates ZW-167 recommendation in real-time
```

---

## 9. LangGraph Pipeline

### 12-Stage Everest Ascent™ Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH 12-STAGE PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  START                                                                       │
│    │                                                                         │
│    ▼                                                                         │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐          │
│  │ Stage 1   │───►│ Stage 2   │───►│ Stage 3   │───►│ Stage 4   │          │
│  │ Discovery │    │ Scraping  │    │ Title     │    │ Lien      │          │
│  │           │    │           │    │ Search    │    │ Priority  │          │
│  │ KPIs:     │    │ KPIs:     │    │ KPIs:     │    │ KPIs:     │          │
│  │ ZW-075-092│    │ ZW-001-012│    │ ZW-115-120│    │ ZW-121-134│          │
│  └───────────┘    │ ZW-151-164│    └───────────┘    └───────────┘          │
│                   └───────────┘                                             │
│       │                │                │                │                  │
│       ▼                ▼                ▼                ▼                  │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐          │
│  │ Stage 5   │───►│ Stage 6   │───►│ Stage 7   │───►│ Stage 8   │          │
│  │ Tax Certs │    │Demographics│    │ ML Score  │    │ Max Bid   │          │
│  │           │    │           │    │           │    │           │          │
│  │ KPIs:     │    │ KPIs:     │    │ KPIs:     │    │ KPIs:     │          │
│  │ ZW-124-125│    │ ZW-177-204│    │ ZW-135-150│    │ ZW-165-166│          │
│  └───────────┘    └───────────┘    └───────────┘    └───────────┘          │
│                                                                              │
│       │                │                │                │                  │
│       ▼                ▼                ▼                ▼                  │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐          │
│  │ Stage 9   │───►│ Stage 10  │───►│ Stage 11  │───►│ Stage 12  │          │
│  │ Decision  │    │ Report    │    │ Disposition│    │ Archive   │          │
│  │ Log       │    │ Generate  │    │           │    │           │          │
│  │           │    │           │    │           │    │           │          │
│  │ KPIs:     │    │ All 298   │    │ Result    │    │ Persist   │          │
│  │ ZW-167-176│    │ KPIs →    │    │ tracking  │    │ to        │          │
│  │ ZW-259-264│    │ DOCX/PDF  │    │           │    │ Supabase  │          │
│  └───────────┘    └───────────┘    └───────────┘    └───────────┘          │
│                                                           │                 │
│                                                           ▼                 │
│                                                        END                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Smart Router V6 LLM Routing

| Tier | Provider | Model | Cost | Use Case |
|------|----------|-------|------|----------|
| FREE | Google | Gemini 2.5 Flash | $0 | 40-55% of requests |
| ULTRA_CHEAP | DeepSeek | V3.2 | $0.28/1M | Simple analysis |
| QUALITY | Anthropic | Claude Sonnet 4.5 | ~$3/1M | Report generation |
| COMPLEX | Anthropic | Claude Opus 4.5 | ~$15/1M | HBU/CMA reasoning |

---

## 10. Composite Scoring Engine

### Formula

```
COMPOSITE_SCORE = HBU (30%) + CMA (30%) + ML (40%)

Where:
- HBU Score: ZW-221 to ZW-232 (Highest & Best Use Analysis)
- CMA Score: ZW-233 to ZW-248 (Comparable Market Analysis)
- ML Score: ZW-135 to ZW-150 (XGBoost Predictions)
```

### Decision Thresholds

| Bid/Judgment Ratio | Composite Score | Red Flags | Decision |
|-------------------|-----------------|-----------|----------|
| ≥ 75% | ≥ 80 | None | 🟢 **BID** |
| 60-74% | 60-79 | None | 🟡 **REVIEW** |
| < 60% | < 60 | Any | ⚪ **SKIP** |

### Red Flag Auto-Skip Rules (ZW-259 to ZW-264)

| KPI | Red Flag | Condition | Action |
|-----|----------|-----------|--------|
| ZW-259 | HOA Foreclosure | Plaintiff is HOA | Auto-SKIP |
| ZW-260 | Senior Lien Survives | First mortgage > judgment | Auto-SKIP |
| ZW-261 | Title Defect | Clouded title detected | Auto-SKIP |
| ZW-262 | Bankruptcy Filed | Active BK case | Auto-SKIP |
| ZW-263 | Multiple Defendants | > 3 defendants | REVIEW required |
| ZW-264 | DO NOT BID | Any critical issue | Auto-SKIP |

---

## 11. Report Generation

### DOCX Report Template (298 KPIs)

```
BIDDEED.AI PROPERTY INTELLIGENCE REPORT
═══════════════════════════════════════════════════════════════

EXECUTIVE SUMMARY
├── Address: [ZW-003]
├── Recommendation: [ZW-167] 🟢 BID / 🟡 REVIEW / ⚪ SKIP
├── Max Bid: [ZW-165] $XXX,XXX
├── Final Judgment: [ZW-094] $XXX,XXX
├── Bid/Judgment Ratio: [ZW-166] XX%
├── Composite Score: [Calculated] XX/100
└── Risk Score: [ZW-257] XX/100

PROPERTY DETAILS (14 KPIs)
├── ZW-001 to ZW-012: Identification
├── ZW-151 to ZW-164: Physical characteristics
└── BCPAO Photo: [ZW-164]

ZONING ANALYSIS (62 KPIs)
├── Zone Code: [ZW-013]
├── Permitted Uses: [ZW-037]
├── Setbacks: [ZW-028 to ZW-032]
├── Max Height: [ZW-033]
└── Development Potential: [ZW-265 to ZW-280]

FINANCIAL ANALYSIS (22 KPIs)
├── Opening Bid: [ZW-093]
├── ARV Estimate: [ZW-103]
├── Repair Estimate: [ZW-106]
├── Shapira Formula™ Calculation
└── ROI Estimate: [ZW-114]

LIEN ANALYSIS (20 KPIs)
├── Total Liens: [ZW-116]
├── First Mortgage: [ZW-117]
├── HOA Liens: [ZW-122]
├── Tax Certificates: [ZW-125]
├── Lien Priority Diagram
└── Senior Lien Survival Analysis

ML PREDICTIONS (16 KPIs)
├── Third-Party Probability: [ZW-135] XX%
├── Predicted Sale Price: [ZW-136]
├── Confidence Score: [ZW-137]
├── Model Version: [ZW-138]
└── Feature Importance: [ZW-146]

HBU ANALYSIS (12 KPIs)
├── Current Use: [ZW-221]
├── Highest Use: [ZW-222]
├── 4-Test Analysis: [ZW-223 to ZW-226]
├── HBU Score: [ZW-227]
└── Premium Potential: [ZW-231]

CMA ANALYSIS (16 KPIs)
├── Comparable 1-3: [ZW-206 to ZW-216]
├── Adjustments: [ZW-235 to ZW-240]
├── Reconciled Value: [ZW-245]
└── CMA Confidence: [ZW-242]

RISK ASSESSMENT (16 KPIs)
├── Risk Scores: [ZW-249 to ZW-258]
├── Red Flags: [ZW-259 to ZW-264]
└── Mitigation Notes: [ZW-258]

APPENDICES
├── A: BCPAO Photo Gallery
├── B: Comp Photos
├── C: Lien Documents
├── D: Source Citations
└── E: Disclaimer
```

---

## 12. Multi-County Expansion

### Phase 1: Current (Brevard)
- 351,423 parcels
- 290 zoning districts
- 17 jurisdictions
- 100% zone coverage

### Phase 2: Q1 2026 (10 Counties)
- Brevard, Orange, Hillsborough, Miami-Dade, Broward
- Palm Beach, Duval, Pinellas, Lee, Volusia
- ~2M parcels
- ~1,000 auctions/month

### Phase 3: Q2 2026 (67 Counties)
- All Florida counties
- ~10M parcels
- ~3,000 auctions/month
- Render.com deployment for scale

### Multi-County Database Schema

```sql
-- multi_county_auctions table
CREATE TABLE multi_county_auctions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    county TEXT NOT NULL,
    auction_date DATE NOT NULL,
    auction_type TEXT NOT NULL,  -- 'foreclosure' or 'tax_deed'
    case_number TEXT NOT NULL,
    property_address TEXT,
    parcel_id TEXT,
    judgment_amount DECIMAL(12,2),
    opening_bid DECIMAL(12,2),
    -- 298 KPI columns...
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(county, case_number)
);

-- Index for fast calendar queries
CREATE INDEX idx_auction_date ON multi_county_auctions(auction_date);
CREATE INDEX idx_county ON multi_county_auctions(county);
```

---

## 13. Tech Stack

### Frontend
| Component | Technology |
|-----------|------------|
| **Desktop App** | **ZoneWise Desktop v2.0.0 (Craft Agents v0.4.0 fork)** |
| Desktop Framework | Electron + Claude Agent SDK 0.2.34 |
| Web Framework | Next.js 15 (React + Vite) |
| Components | shadcn/ui |
| Styling | Tailwind CSS |
| Maps | Mapbox GL JS |
| Charts | Recharts |
| State | TanStack Query |
| LLM Connections | Multi-provider (Anthropic, OpenRouter, Codex/OpenAI) |
| Skills | `.agents/skills` cross-tool convention |

### Backend
| Component | Technology |
|-----------|------------|
| Database | Supabase (PostgreSQL + pgvector) |
| Auth | Supabase Auth |
| Realtime | Supabase Realtime |
| Edge Functions | Supabase Edge |
| LLM Routing | LiteLLM + Smart Router V6 |
| Agents | LangGraph |
| ML | XGBoost (scikit-learn) |

### Infrastructure
| Component | Technology |
|-----------|------------|
| Hosting | Cloudflare Pages |
| Compute | GitHub Actions (CI/CD) |
| Scale Compute | Render.com (50+ counties) |
| Storage | Supabase Storage |
| CDN | Cloudflare |

---

## 14. Competitive Positioning

### Market Position

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPETITIVE POSITIONING                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                        HIGH                                          │
│                          │                                           │
│                          │        ⭐ BidDeed.AI                      │
│   DATA                   │           (298 KPIs)                      │
│   COMPREHENSIVENESS      │                                           │
│                          │                                           │
│                          │    PropertyOnion                          │
│                          │       (96 KPIs)                           │
│                          │                                           │
│                          │              Gridics                      │
│                          │              (74 KPIs)                    │
│                          │                                           │
│                        LOW──────────────────────────────► HIGH       │
│                                  AI/ML CAPABILITIES                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Feature Differentiation

| Feature | BidDeed/ZoneWise | PropertyOnion | Gridics |
|---------|------------------|---------------|---------|
| Total KPIs | **298** | 96 | 74 |
| ML Predictions | ✅ XGBoost | ❌ | ❌ |
| HBU Analysis | ✅ 12 KPIs | ❌ | ⚠️ 3 |
| CMA Deep | ✅ 16 KPIs | ❌ | ❌ |
| Zoning Data | ✅ 62 KPIs | ❌ | ✅ 45 |
| NLP Chat | ✅ Claude | ❌ | ❌ |
| Split-Screen UI | ✅ Artifacts | ❌ | ❌ |
| Drive for Dollars | ✅ Integrated | ❌ | ❌ |

---

## 15. Roadmap

### Phase 1: Data Foundation (Weeks 1-8)
- [x] 298 KPI framework defined
- [x] DFD architecture documented
- [x] UI/UX specification complete
- [ ] Brevard 100% zone coverage verified
- [ ] Modal.com scraper deployment
- [ ] 10 county data collection

### Phase 2: UI Implementation (Weeks 9-12)
- [x] Fork Craft Agents OSS → ZoneWise Desktop v2.0.0
- [x] Multi-provider LLM connections (Anthropic + Codex/OpenAI)
- [x] Per-workspace theming (Navy #1E3A5F)
- [x] Claude Opus 4.6 support
- [ ] Add Supabase integration
- [ ] Implement PropertyCard component
- [ ] Build AuctionCalendar
- [ ] Create ArtifactPanel with 8 tabs
- [ ] Integrate Mapbox with heatmaps

### Phase 3: MVP Launch (Week 12)
- [ ] Deploy to Cloudflare Pages
- [ ] Connect LangGraph pipeline
- [ ] Enable 298 KPI display
- [ ] DOCX report generation
- [ ] Internal alpha testing

### Phase 4: Scale (Q2 2026)
- [ ] 67 Florida counties
- [ ] Multi-tenant architecture
- [ ] API access for brokers
- [ ] Mobile responsive optimization

---

## Document References

| Document | Location |
|----------|----------|
| **298 KPI Framework** | docs/data/KPI_FRAMEWORK_298_COMPLETE.md |
| **DFD Architecture** | docs/architecture/DFD_CLAUDE_AI_REAL_ESTATE_298_KPI.md |
| **UI/UX Specification** | docs/architecture/UI_UX_MAPBOX_SPLIT_SCREEN_SPECIFICATION.md |
| **Master Integration** | docs/architecture/MASTER_INTEGRATION.md |
| **Architecture Decision** | docs/architecture/ARCHITECTURE_DECISION_2026-01-25.md |
| **Full Stack Spec** | docs/architecture/FULL_STACK_SPECIFICATION.md |
| **Execution Plan** | docs/planning/EXECUTION_PLAN_12_WEEKS.md |

---

*PRD V4.0 - BidDeed.AI / ZoneWise: Claude AI for Real Estate*  
*January 25, 2026*


---

## CHANGELOG

### V5.0 (February 8, 2026)
- Added ZoneWise Desktop v2.0.0 (Craft Agents v0.4.0 fork) to platform
- Multi-provider LLM connections (Anthropic, OpenRouter, Codex/OpenAI)
- Per-workspace default connections and theming
- Claude Opus 4.6 support (1M context, 128K output)
- `.agents/skills` cross-tool convention support
- Updated Tech Stack with desktop distribution channel
- Updated Roadmap with completed desktop milestones

### V4.0 (January 25, 2026)
- Initial unified PRD combining BidDeed.AI and ZoneWise
- 298 KPI framework
- Split-screen UI specification
- shadcn component library
