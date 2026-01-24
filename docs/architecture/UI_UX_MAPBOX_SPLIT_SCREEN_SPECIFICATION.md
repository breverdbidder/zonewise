# UI/UX Architecture: Split-Screen Mapbox Interface

**Version:** 1.0  
**Date:** January 25, 2026  
**Based On:** PropertyOnion (micro) + Reventure.app (macro) reverse engineering  
**Implementation:** Open-claude fork with custom artifacts

---

## Executive Summary

This document specifies the **split-screen interface** that combines:
- **LEFT PANEL (40%):** NLP chat + property list + filters
- **RIGHT PANEL (60%):** Interactive Mapbox with heatmaps, pins, and artifacts

The design synthesizes:
- **PropertyOnion's strengths:** 96 KPIs, property-level detail, auction calendar
- **Reventure.app's strengths:** Market heatmaps, demographic overlays, macro analytics
- **BidDeed.AI's advantage:** AI-powered analysis, ML predictions, agentic workflows

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER BAR                                      │
│  Logo | County Selector | Auction Date | User Auth | Settings | Theme       │
├──────────────────────────────┬──────────────────────────────────────────────┤
│                              │                                              │
│   LEFT PANEL (40%)           │   RIGHT PANEL (60%)                          │
│                              │                                              │
│  ┌────────────────────────┐  │  ┌────────────────────────────────────────┐  │
│  │     NLP CHAT INPUT     │  │  │                                        │  │
│  │  "Analyze 32937 props" │  │  │         MAPBOX GL JS                   │  │
│  └────────────────────────┘  │  │                                        │  │
│                              │  │   🔴 Foreclosure pins                  │  │
│  ┌────────────────────────┐  │  │   🔵 Tax deed pins                     │  │
│  │    QUICK STATS         │  │  │   🟢 BID recommended                   │  │
│  │  Total: 19 | BID: 4    │  │  │   🟡 REVIEW recommended                │  │
│  │  REVIEW: 3 | SKIP: 12  │  │  │   ⚪ SKIP recommended                  │  │
│  └────────────────────────┘  │  │                                        │  │
│                              │  │   ░░░░░░░░░░░░░░░░░░░                  │  │
│  ┌────────────────────────┐  │  │   HEATMAP LAYER (toggleable)           │  │
│  │      FILTERS           │  │  │   - Price density                      │  │
│  │  ☑ BID  ☑ REVIEW       │  │  │   - ROI potential                      │  │
│  │  ☐ SKIP                │  │  │   - Demographics                       │  │
│  │  Price: $0 - $500K     │  │  │                                        │  │
│  │  Zip: 32937, 32940     │  │  │   CONTROLS:                            │  │
│  └────────────────────────┘  │  │   [Layers] [Draw] [Measure] [3D]       │  │
│                              │  │                                        │  │
│  ┌────────────────────────┐  │  └────────────────────────────────────────┘  │
│  │   PROPERTY LIST        │  │                                              │
│  │  ┌──────────────────┐  │  │  ┌────────────────────────────────────────┐  │
│  │  │ 🏠 123 Main St   │  │  │  │         ARTIFACT PANEL                 │  │
│  │  │ BID | $185K | 89%│◄─┼──┼──│  (Shows when property selected)        │  │
│  │  └──────────────────┘  │  │  │                                        │  │
│  │  ┌──────────────────┐  │  │  │  ┌──────────────────────────────────┐  │  │
│  │  │ 🏠 456 Oak Ave   │  │  │  │  │ BCPAO PHOTO                      │  │  │
│  │  │ REVIEW | $220K   │  │  │  │  │ [Property Image]                 │  │  │
│  │  └──────────────────┘  │  │  │  └──────────────────────────────────┘  │  │
│  │  ┌──────────────────┐  │  │  │                                        │  │
│  │  │ 🏠 789 Pine Rd   │  │  │  │  TABS: [Analysis] [Liens] [Comps]     │  │
│  │  │ SKIP | $450K     │  │  │  │        [Demographics] [Report]        │  │
│  │  └──────────────────┘  │  │  │                                        │  │
│  └────────────────────────┘  │  │  ┌──────────────────────────────────┐  │  │
│                              │  │  │ BidDeed.AI ML: 89% BID confidence │  │  │
│  ┌────────────────────────┐  │  │  │ ARV: $285K | Max Bid: $199K      │  │  │
│  │    AI REASONING        │  │  │  │ Bid/Jdg: 78% ████████░░          │  │  │
│  │  "Senior mortgage      │  │  │  └──────────────────────────────────┘  │  │
│  │   survives, recommend  │  │  │                                        │  │
│  │   SKIP due to liens"   │  │  │  [Generate Report] [Update Max Bid]   │  │
│  └────────────────────────┘  │  └────────────────────────────────────────┘  │
│                              │                                              │
├──────────────────────────────┴──────────────────────────────────────────────┤
│                              FOOTER                                          │
│  Pipeline Status: ████████░░ Stage 8/12 | Last Updated: 2 min ago          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Header Bar

```typescript
interface HeaderProps {
  logo: string;              // BidDeed.AI logo
  countySelector: {
    selected: string[];      // ["Brevard", "Orange", "Seminole"]
    available: County[];     // 67 FL counties
    onSelect: (counties: string[]) => void;
  };
  auctionDate: {
    selected: Date;
    upcoming: AuctionDate[];
  };
  user: {
    name: string;
    avatar: string;
    plan: "free" | "pro" | "enterprise";
  };
  theme: "light" | "dark" | "system";
}
```

### 2. Left Panel (40%)

#### 2.1 NLP Chat Input

```typescript
interface ChatInputProps {
  placeholder: string;       // "Ask about any property or auction..."
  suggestions: string[];     // ["Analyze 32937", "Show HOA foreclosures", ...]
  onSubmit: (query: string) => void;
  isProcessing: boolean;
}

// Example queries:
const exampleQueries = [
  "Show me all properties in 32937 under $200K",
  "Which properties have HOA as plaintiff?",
  "Analyze liens for 123 Main St",
  "Generate report for tomorrow's auction",
  "What's the max bid for parcel 28-37-35?",
];
```

#### 2.2 Quick Stats Bar

```typescript
interface QuickStatsProps {
  total: number;
  byDecision: {
    BID: number;
    REVIEW: number;
    SKIP: number;
  };
  totalJudgment: number;
  avgBidRatio: number;
}

// Visual:
// ┌──────────────────────────────────────┐
// │ 📊 19 Properties | $4.35M Judgment   │
// │ 🟢 BID: 4  🟡 REVIEW: 3  ⚪ SKIP: 12 │
// └──────────────────────────────────────┘
```

#### 2.3 Filters Panel

```typescript
interface FiltersProps {
  decision: ("BID" | "REVIEW" | "SKIP")[];
  priceRange: [number, number];
  zipCodes: string[];
  propertyType: string[];
  plaintiffType: ("Bank" | "HOA" | "Tax" | "Other")[];
  bedsMin: number;
  bathsMin: number;
  sqftRange: [number, number];
  auctionDateRange: [Date, Date];
}
```

#### 2.4 Property List

```typescript
interface PropertyCardProps {
  id: string;
  address: string;
  city: string;
  zip: string;
  decision: "BID" | "REVIEW" | "SKIP";
  mlConfidence: number;      // 0-100
  judgment: number;
  maxBid: number;
  bidRatio: number;          // maxBid / judgment
  thumbnail: string;
  isSelected: boolean;
  onSelect: () => void;
  onHover: () => void;
}

// Card design:
// ┌──────────────────────────────────────┐
// │ 🏠 123 Main St, Melbourne 32937      │
// │ ┌────────┐ Judgment: $185,000        │
// │ │ PHOTO  │ Max Bid:  $145,000        │
// │ │        │ Ratio: 78% ████████░░     │
// │ └────────┘ 🟢 BID | 89% confidence   │
// │ 3bd/2ba | 1,850 sqft | Built 2005    │
// └──────────────────────────────────────┘
```

#### 2.5 AI Reasoning Panel

```typescript
interface AIReasoningProps {
  thinking: string;          // Current reasoning text
  stages: {
    name: string;
    status: "pending" | "running" | "complete" | "error";
    output?: string;
  }[];
  citations: {
    source: string;
    url: string;
  }[];
}

// Visual (inspired by Claude's thinking):
// ┌──────────────────────────────────────┐
// │ 🧠 AI Analysis                       │
// │                                      │
// │ "Checking lien priority...          │
// │  Found: 1st mortgage $180K (Chase)  │
// │  Found: HOA lien $12K              │
// │                                      │
// │  ⚠️ Senior mortgage survives HOA    │
// │  foreclosure. Recommend SKIP."      │
// │                                      │
// │ Sources: [AcclaimWeb] [BCPAO]        │
// └──────────────────────────────────────┘
```

---

### 3. Right Panel (60%)

#### 3.1 Mapbox GL Implementation

```typescript
interface MapboxConfig {
  accessToken: string;
  style: "mapbox://styles/mapbox/dark-v11";  // Dark theme default
  center: [number, number];  // [lng, lat]
  zoom: number;
  pitch: number;             // 0 for 2D, 45 for 3D
  bearing: number;
}

interface MapLayers {
  properties: {
    type: "geojson";
    data: PropertyGeoJSON;
    clusterRadius: 50;
    clusterMaxZoom: 14;
  };
  heatmap: {
    type: "heatmap";
    source: "properties";
    paint: {
      "heatmap-weight": ["get", "weight"];      // Based on judgment/ROI
      "heatmap-intensity": 1;
      "heatmap-color": [
        "interpolate", ["linear"], ["heatmap-density"],
        0, "rgba(0,0,255,0)",
        0.2, "rgb(0,255,0)",
        0.4, "rgb(255,255,0)",
        0.6, "rgb(255,128,0)",
        1, "rgb(255,0,0)"
      ];
      "heatmap-radius": 30;
    };
  };
  demographics: {
    type: "fill";
    source: "census-tracts";
    paint: {
      "fill-color": ["interpolate", ...];  // Based on income/vacancy
      "fill-opacity": 0.5;
    };
  };
}
```

#### 3.2 Map Controls

```typescript
interface MapControls {
  layers: {
    properties: boolean;     // Pin markers
    heatmap: boolean;        // Heat overlay
    demographics: boolean;   // Census tract colors
    flood: boolean;          // FEMA flood zones
    zoning: boolean;         // Zoning boundaries
  };
  draw: {
    polygon: boolean;        // Draw search area
    circle: boolean;         // Radius search
    rectangle: boolean;      // Box search
  };
  measure: {
    distance: boolean;       // Measure distances
    area: boolean;           // Measure area
  };
  view: {
    "2d": boolean;
    "3d": boolean;           // Building extrusion
    satellite: boolean;      // Satellite imagery
  };
}
```

#### 3.3 Property Pin Markers

```typescript
interface PropertyMarker {
  id: string;
  coordinates: [number, number];
  decision: "BID" | "REVIEW" | "SKIP";
  color: {
    BID: "#22c55e",          // Green
    REVIEW: "#eab308",       // Yellow
    SKIP: "#6b7280"          // Gray
  };
  size: number;              // Based on judgment amount
  popup: {
    thumbnail: string;
    address: string;
    judgment: number;
    decision: string;
    confidence: number;
  };
  onClick: () => void;       // Select property
  onHover: () => void;       // Highlight in list
}
```

#### 3.4 Artifact Panel (Slides Up When Property Selected)

```typescript
interface ArtifactPanelProps {
  property: Property;
  tabs: ("analysis" | "liens" | "comps" | "demographics" | "report")[];
  activeTab: string;
}

// Tab contents:

// ANALYSIS TAB
interface AnalysisTab {
  photo: string;             // BCPAO photo
  mlPrediction: {
    decision: "BID" | "REVIEW" | "SKIP";
    confidence: number;
    reasoning: string;
  };
  financials: {
    arv: number;
    repairEstimate: number;
    maxBid: number;
    judgment: number;
    bidRatio: number;
    potentialROI: number;
  };
  keyRisks: string[];
  keyOpportunities: string[];
}

// LIENS TAB
interface LiensTab {
  liens: {
    type: string;            // "1st Mortgage", "HOA", "Tax"
    holder: string;          // "Chase Bank", "HOA Inc"
    amount: number;
    recordingDate: Date;
    priority: number;
    survivesSale: boolean;
  }[];
  totalLiens: number;
  seniorLiens: number;       // Amount surviving sale
  lienPriorityDiagram: string; // Visual representation
}

// COMPS TAB
interface CompsTab {
  comparables: {
    address: string;
    saleDate: Date;
    salePrice: number;
    sqft: number;
    pricePerSqft: number;
    distance: number;        // Miles from subject
    similarity: number;      // 0-100%
  }[];
  arvCalculation: {
    avgPricePerSqft: number;
    subjectSqft: number;
    adjustments: Adjustment[];
    finalARV: number;
  };
}

// DEMOGRAPHICS TAB (Reventure.app style)
interface DemographicsTab {
  censusTract: string;
  income: {
    median: number;
    percentile: number;      // vs FL average
  };
  housing: {
    medianValue: number;
    medianRent: number;
    vacancyRate: number;
    ownerOccupied: number;   // %
  };
  population: {
    total: number;
    density: number;         // per sq mi
    growth: number;          // YoY %
  };
  scores: {
    walkScore: number;
    schoolScore: number;
    crimeScore: number;
  };
  charts: {
    incomeDistribution: ChartData;
    priceHistory: ChartData;
    rentTrend: ChartData;
  };
}

// REPORT TAB
interface ReportTab {
  preview: string;           // PDF preview iframe
  formats: ("pdf" | "docx")[];
  sections: {
    name: string;
    included: boolean;
  }[];
  generateButton: () => void;
  downloadButton: () => void;
}
```

---

## PropertyOnion 96 KPIs Mapping

### Where Each KPI Appears in Our UI

| KPI Category | KPI Count | UI Location |
|--------------|-----------|-------------|
| Property Info (1-10) | 10 | Property Card, Analysis Tab |
| Financial Data (11-20) | 10 | Analysis Tab, Quick Stats |
| Auction Details (21-30) | 10 | Property Card, Calendar |
| Liens (31-39) | 9 | Liens Tab |
| Title Info (40-48) | 9 | Analysis Tab |
| Market Analysis (49-56) | 8 | Comps Tab, Heatmap |
| Location Data (57-66) | 10 | Map, Demographics Tab |
| Property Condition (67-75) | 9 | Analysis Tab |
| Investment Metrics (76-84) | 9 | Analysis Tab |
| Historical Data (85-90) | 6 | Analysis Tab |
| Additional Intel (91-96) | 6 | Analysis Tab |

### PropertyOnion KPIs We EXCEED

| PropertyOnion | BidDeed.AI Enhancement |
|---------------|------------------------|
| Static market value | ML-predicted ARV with confidence |
| Manual repair estimate | AI-analyzed repair scope |
| Basic lien list | Lien priority analysis + survival calc |
| Static comparables | Dynamic comp selection with similarity score |
| No ML predictions | XGBoost third-party probability |
| No recommendations | BID/REVIEW/SKIP with reasoning |
| No AI chat | Full NLP interface |

---

## Reventure.app Macro Features

### Heatmap Layers (Toggleable)

```typescript
interface HeatmapLayers {
  // PRICE HEATMAP (Reventure style)
  priceHeatmap: {
    metric: "median_home_value";
    colorScale: ["#2563eb", "#22c55e", "#eab308", "#ef4444"];
    legend: "Home Values: $100K → $1M+";
  };
  
  // APPRECIATION HEATMAP
  appreciationHeatmap: {
    metric: "yoy_appreciation";
    colorScale: ["#ef4444", "#fbbf24", "#22c55e"];
    legend: "Appreciation: -10% → +30%";
  };
  
  // VACANCY HEATMAP
  vacancyHeatmap: {
    metric: "vacancy_rate";
    colorScale: ["#22c55e", "#fbbf24", "#ef4444"];
    legend: "Vacancy: 0% → 20%+";
  };
  
  // INCOME HEATMAP
  incomeHeatmap: {
    metric: "median_household_income";
    colorScale: ["#f87171", "#fbbf24", "#4ade80", "#22d3ee"];
    legend: "Income: $30K → $150K+";
  };
  
  // ROI POTENTIAL (BidDeed.AI exclusive)
  roiHeatmap: {
    metric: "calculated_roi_potential";
    colorScale: ["#6b7280", "#22c55e", "#10b981"];
    legend: "ROI: 0% → 100%+";
  };
}
```

### Market Analytics Panel (Reventure Style)

```typescript
interface MarketAnalyticsPanel {
  // ZIP Code Summary
  zipStats: {
    medianPrice: number;
    priceChange: number;     // YoY %
    daysOnMarket: number;
    inventory: number;
    absorptionRate: number;  // Months of supply
  };
  
  // County Summary
  countyStats: {
    totalForeclosures: number;
    avgJudgment: number;
    successRate: number;     // % sold at auction
    thirdPartyRate: number;  // % bought by investors
  };
  
  // Trend Charts
  charts: {
    priceHistory: TimeSeriesChart;
    foreclosureTrend: TimeSeriesChart;
    inventoryTrend: TimeSeriesChart;
  };
}
```

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  MICRO (Property Level)              MACRO (Market Level)                   │
│  ├── BCPAO (Property cards)          ├── Census API (Demographics)          │
│  ├── AcclaimWeb (Liens)              ├── Zillow CSVs (Market data)          │
│  ├── RealTDM (Tax certs)             ├── Redfin (Price trends)              │
│  ├── RealForeclose (Auctions)        ├── FEMA (Flood zones)                 │
│  └── Clerk (Case files)              └── County GIS (Boundaries)            │
│                                                                              │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SUPABASE DATABASE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  sample_properties (351K)    jurisdictions (17)     census_tracts (148)    │
│  parcel_zones (24K)          zoning_districts (290) market_metrics         │
│  liens                       sales_history          demographic_cache      │
│                                                                              │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH AGENTS                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Zoning Agent ──► Parcel Agent ──► Lien Agent ──► Analysis Agent            │
│       │               │                │               │                    │
│       ▼               ▼                ▼               ▼                    │
│  Zone lookup    Property data    Lien priority    ML prediction             │
│  Dimensional    BCPAO fetch      AcclaimWeb       BID/REVIEW/SKIP          │
│  standards      Photos           Survival calc    Confidence %              │
│                                                                              │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Open-claude Fork)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────────────────────┐   │
│  │    ChatMode.jsx      │    │           ArtifactPanel.jsx              │   │
│  │    (NLP input)       │    │    ┌─────────────────────────────────┐  │   │
│  └──────────────────────┘    │    │        MapboxMap.jsx            │  │   │
│                              │    │  (Heatmaps, pins, layers)       │  │   │
│  ┌──────────────────────┐    │    └─────────────────────────────────┘  │   │
│  │  ThinkingDisplay.jsx │    │    ┌─────────────────────────────────┐  │   │
│  │  (AI reasoning)      │    │    │     PropertyDetail.jsx          │  │   │
│  └──────────────────────┘    │    │  (Tabs: Analysis, Liens, etc)   │  │   │
│                              │    └─────────────────────────────────┘  │   │
│  ┌──────────────────────┐    │    ┌─────────────────────────────────┐  │   │
│  │  PropertyList.jsx    │◄───┼───►│     MarketAnalytics.jsx         │  │   │
│  │  (Sortable cards)    │    │    │  (Reventure-style charts)       │  │   │
│  └──────────────────────┘    │    └─────────────────────────────────┘  │   │
│                              │                                          │   │
│  LEFT PANEL (40%)            │    RIGHT PANEL (60%)                     │   │
│                              │                                          │   │
└──────────────────────────────┴──────────────────────────────────────────────┘
```

---

## Implementation Components

### New Components to Create (in Open-claude fork)

```
src/components/
├── map/
│   ├── MapboxMap.jsx              # Main Mapbox GL container
│   ├── PropertyMarkers.jsx        # Pin layer
│   ├── HeatmapLayer.jsx           # Price/ROI/vacancy heatmaps
│   ├── DemographicsLayer.jsx      # Census tract fills
│   ├── MapControls.jsx            # Layer toggles, draw tools
│   └── MapPopup.jsx               # Property preview on hover
├── property/
│   ├── PropertyList.jsx           # Left panel list
│   ├── PropertyCard.jsx           # Individual card
│   ├── PropertyDetail.jsx         # Full detail tabs
│   ├── AnalysisTab.jsx            # ML predictions, financials
│   ├── LiensTab.jsx               # Lien priority diagram
│   ├── CompsTab.jsx               # Comparable sales
│   └── DemographicsTab.jsx        # Census data, scores
├── analytics/
│   ├── MarketAnalytics.jsx        # Reventure-style dashboard
│   ├── ZipCodeStats.jsx           # ZIP summary card
│   ├── TrendCharts.jsx            # Price/inventory/foreclosure
│   └── HeatmapLegend.jsx          # Color scale legend
└── report/
    ├── ReportPreview.jsx          # PDF preview
    └── ReportGenerator.jsx        # DOCX generation
```

### Mapbox Access Token

```bash
# .env.local
VITE_MAPBOX_TOKEN=pk.eyJ1IjoiYmlkZGVlZGFpIiwiYSI6ImNs...
```

### Required NPM Packages

```json
{
  "dependencies": {
    "mapbox-gl": "^3.0.1",
    "react-map-gl": "^7.1.7",
    "@mapbox/mapbox-gl-draw": "^1.4.3",
    "@turf/turf": "^6.5.0",
    "recharts": "^2.10.0",
    "framer-motion": "^10.16.0"
  }
}
```

---

## Responsive Design

### Desktop (>1024px)
- 40% / 60% split
- Both panels visible
- Full map with all controls

### Tablet (768px - 1024px)
- 35% / 65% split
- Collapsible left panel
- Simplified map controls

### Mobile (<768px)
- Full screen map (default)
- Bottom sheet for property list (30vh)
- FAB button for chat modal
- Swipe up for property details

---

## Performance Requirements

| Metric | Target |
|--------|--------|
| Initial map load | <2s |
| Property pin render | <500ms for 100 pins |
| Heatmap render | <1s |
| Property detail load | <500ms |
| NLP response (simple) | <2s |
| NLP response (complex) | <10s with streaming |

---

## Next Steps

1. **Week 9:** Fork Open-claude, add Mapbox setup
2. **Week 10:** Implement PropertyMarkers, HeatmapLayer
3. **Week 11:** Build PropertyDetail tabs, DemographicsTab
4. **Week 12:** Polish, mobile responsive, MVP launch

---

*This specification combines PropertyOnion's 96 KPIs (micro) with Reventure.app's market analytics (macro) into a unified split-screen interface powered by BidDeed.AI's ML engine.*
