# Claude AI for Real Estate: Master Integration Document

**Version:** 1.0  
**Date:** January 25, 2026  
**Status:** PRODUCTION ARCHITECTURE  
**Purpose:** Single source of truth connecting all ecosystem documentation

---

## Executive Summary

The "Claude AI for Real Estate" ecosystem combines three platforms into a unified split-screen interface:

1. **BidDeed.AI** - Foreclosure auction intelligence (74 exclusive KPIs)
2. **ZoneWise** - Zoning & land use intelligence (128 exclusive KPIs)  
3. **PropertyOnion Parity** - Replicated competitor features (96 KPIs)

**Total: 298 Unique KPIs** processed through a 12-stage LangGraph pipeline and displayed via a Claude AI-style split-screen UI.

---

## Document Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                     CLAUDE AI FOR REAL ESTATE - DOCUMENTATION MAP                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│                            ┌─────────────────────────┐                                  │
│                            │  MASTER INTEGRATION     │ ◄── YOU ARE HERE                │
│                            │  (This Document)        │                                  │
│                            └───────────┬─────────────┘                                  │
│                                        │                                                │
│           ┌────────────────────────────┼────────────────────────────┐                  │
│           │                            │                            │                  │
│           ▼                            ▼                            ▼                  │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐            │
│  │ DFD_CLAUDE_AI_      │  │ UI_UX_MAPBOX_       │  │ KPI_FRAMEWORK_      │            │
│  │ REAL_ESTATE_        │  │ SPLIT_SCREEN_       │  │ 298_COMPLETE.md     │            │
│  │ 298_KPI.md          │  │ SPECIFICATION.md    │  │                     │            │
│  │                     │  │                     │  │ • 17 Categories     │            │
│  │ • Level 0 Context   │  │ • Left Panel 40%    │  │ • ZW-001 to ZW-298  │            │
│  │ • Level 1 Processes │  │ • Right Panel 60%   │  │ • Competitive edge  │            │
│  │ • Level 2 Detail    │  │ • Component specs   │  │                     │            │
│  │ • Data stores       │  │ • Responsive design │  │                     │            │
│  └─────────┬───────────┘  └─────────┬───────────┘  └─────────┬───────────┘            │
│            │                        │                        │                         │
│            └────────────────────────┼────────────────────────┘                         │
│                                     │                                                   │
│           ┌─────────────────────────┼─────────────────────────┐                        │
│           │                         │                         │                        │
│           ▼                         ▼                         ▼                        │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐            │
│  │ ARCHITECTURE_       │  │ FULL_STACK_         │  │ DATA_FRAMEWORK_     │            │
│  │ DECISION_           │  │ SPECIFICATION.md    │  │ 20_PHASES_          │            │
│  │ 2026-01-25.md       │  │                     │  │ 10_STAGES.md        │            │
│  │                     │  │ • Tech stack        │  │                     │            │
│  │ • Open-claude fork  │  │ • API contracts     │  │ • Data collection   │            │
│  │ • Supabase backend  │  │ • Database schema   │  │ • 67 FL counties    │            │
│  │ • LangGraph agents  │  │ • LLM routing       │  │ • Scaling plan      │            │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘            │
│                                                                                          │
│                      ┌─────────────────────────────────┐                               │
│                      │ EXECUTION_PLAN_12_WEEKS.md     │                               │
│                      │                                 │                               │
│                      │ • Phase 1: Data (Weeks 1-8)    │                               │
│                      │ • Phase 2: UI (Weeks 9-12)     │                               │
│                      │ • MVP Launch                    │                               │
│                      └─────────────────────────────────┘                               │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Integration Matrix: DFD ↔ UI/UX ↔ 298 KPIs

### How DFD Processes Map to UI Components

| DFD Process | UI Component | KPI Categories | KPI Codes |
|-------------|--------------|----------------|-----------|
| **P1: NLP Processing** | ChatMode.jsx | - | Query parsing |
| **P2: LangGraph Orchestration** | ThinkingDisplay.jsx | All 17 | Stage progress |
| **P3: Data Acquisition** | (Background) | 1-5 | ZW-001 to ZW-134 |
| **P4: 298 KPI Engine** | ArtifactPanel.jsx | All 17 | ZW-001 to ZW-298 |
| **P5: Presentation** | Split-Screen UI | Display only | All |

### How UI Tabs Map to KPI Categories

| UI Tab | DFD Data Store | KPI Categories | Count |
|--------|----------------|----------------|-------|
| **Analysis Tab** | kpi_values | Financial, ML, Investment | 54 |
| **Zoning Tab** | zoning_districts, parcel_zones | Zoning & Land Use | 62 |
| **Liens Tab** | liens | Liens & Encumbrances, Red Flags | 26 |
| **Comps Tab** | sales_history | Comparable Sales, CMA | 32 |
| **Demographics Tab** | census_tracts | Demographics, Market | 28 |
| **HBU Tab** | kpi_values | HBU Analysis | 12 |
| **Risk Tab** | kpi_values | Risk Assessment | 10 |
| **Development Tab** | zoning_districts | Development, Environmental | 34 |
| **Report Tab** | (Generated) | All 298 → DOCX/PDF | 298 |

### Data Flow: External Sources → UI Display

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW: SOURCE TO UI                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  EXTERNAL SOURCES              DFD PROCESSES              UI COMPONENTS                 │
│  ─────────────────             ─────────────              ─────────────                 │
│                                                                                          │
│  RealForeclose ─────────┐                           ┌──► PropertyList.jsx              │
│  (Auctions)              │      ┌─────────────┐     │    (ZW-075 to ZW-092)            │
│                          ├────► │   P3: Data  │ ────┤                                   │
│  BCPAO ─────────────────┤      │ Acquisition │     ├──► PropertyCard.jsx              │
│  (Property)              │      └──────┬──────┘     │    (ZW-001 to ZW-012)            │
│                          │             │            │    (ZW-151 to ZW-164)            │
│  AcclaimWeb ────────────┤             ▼            │                                   │
│  (Liens)                 │      ┌─────────────┐     ├──► LiensTab.jsx                  │
│                          │      │   P4: 298   │     │    (ZW-115 to ZW-134)            │
│  Municode ──────────────┤      │ KPI Engine  │     │                                   │
│  (Zoning)                │      └──────┬──────┘     ├──► ZoningTab.jsx                 │
│                          │             │            │    (ZW-013 to ZW-074)            │
│  Census API ────────────┤             ▼            │                                   │
│  (Demographics)          │      ┌─────────────┐     ├──► DemographicsTab.jsx           │
│                          └────► │  D1: Supa-  │ ────┤    (ZW-177 to ZW-204)            │
│                                 │    base     │     │                                   │
│  XGBoost Model ─────────────►  │  Database   │     ├──► AnalysisTab.jsx               │
│  (ML Predictions)               └─────────────┘     │    (ZW-135 to ZW-176)            │
│                                       │             │                                   │
│                                       │             ├──► MapboxMap.jsx                 │
│                                       │             │    (Heatmaps, Pins)              │
│                                       │             │                                   │
│                                       │             └──► ReportGenerator.jsx           │
│                                       │                  (All 298 → DOCX)              │
│                                       │                                                 │
│                                       ▼                                                 │
│                               ┌─────────────────┐                                      │
│                               │ Supabase Tables │                                      │
│                               │                 │                                      │
│                               │ sample_properties│                                     │
│                               │ (351,423 rows)  │                                      │
│                               │                 │                                      │
│                               │ kpi_values      │                                      │
│                               │ (298 columns)   │                                      │
│                               │                 │                                      │
│                               │ zoning_districts│                                      │
│                               │ (290 rows)      │                                      │
│                               │                 │                                      │
│                               │ parcel_zones    │                                      │
│                               │ (24,243 rows)   │                                      │
│                               └─────────────────┘                                      │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## LangGraph Agent → UI Component Mapping

### Stage-by-Stage Integration

| LangGraph Stage | Agent Name | KPIs Produced | UI Updates |
|-----------------|------------|---------------|------------|
| **Stage 1: Discovery** | DiscoveryAgent | ZW-075 to ZW-092 | PropertyList populates |
| **Stage 2: Scraping** | ParcelAgent | ZW-001 to ZW-012, ZW-151-164 | PropertyCard with photos |
| **Stage 3: Title Search** | TitleAgent | ZW-115 to ZW-120 | LiensTab basic |
| **Stage 4: Lien Priority** | LienAgent | ZW-121 to ZW-134 | LiensTab priority diagram |
| **Stage 5: Tax Certs** | TaxAgent | ZW-124 to ZW-125 | LiensTab tax section |
| **Stage 6: Demographics** | DemographicsAgent | ZW-177 to ZW-204 | DemographicsTab, Heatmaps |
| **Stage 7: ML Score** | MLAgent | ZW-135 to ZW-150 | AnalysisTab ML section |
| **Stage 8: Max Bid** | BidAgent | ZW-165 to ZW-166 | AnalysisTab financial |
| **Stage 9: Decision Log** | DecisionAgent | ZW-167 to ZW-176, ZW-259-264 | PropertyCard badge (BID/REVIEW/SKIP) |
| **Stage 10: Report** | ReportAgent | All 298 | ReportTab preview |
| **Stage 11: Disposition** | DispositionAgent | Result tracking | PropertyList status |
| **Stage 12: Archive** | ArchiveAgent | Persistence | Database only |

### Real-Time UI Updates via Supabase

```typescript
// Supabase Realtime subscription for stage progress
const subscription = supabase
  .channel('kpi_updates')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'kpi_values',
    filter: `property_id=eq.${propertyId}`
  }, (payload) => {
    // Update ThinkingDisplay with stage progress
    updateThinkingDisplay(payload.new.current_stage);
    
    // Update ArtifactPanel with new KPI values
    updateArtifactPanel(payload.new);
    
    // Update PropertyCard badge when decision changes
    if (payload.new.zw_167_recommendation) {
      updatePropertyCard(payload.new.zw_167_recommendation);
    }
  })
  .subscribe();
```

---

## Composite Scoring Engine Integration

### HBU (30%) + CMA (30%) + ML (40%) = Decision

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              COMPOSITE SCORING FLOW                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         FROM DFD P4: 298 KPI ENGINE                              │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                                │
│         ┌──────────────────────────────┼──────────────────────────────┐                │
│         │                              │                              │                │
│         ▼                              ▼                              ▼                │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐       │
│  │    HBU ENGINE       │    │    CMA ENGINE       │    │    ML ENGINE        │       │
│  │    (30% Weight)     │    │    (30% Weight)     │    │    (40% Weight)     │       │
│  │                     │    │                     │    │                     │       │
│  │  ZW-221: Current Use│    │  ZW-233: Condition  │    │  ZW-135: 3rd Party  │       │
│  │  ZW-222: Highest Use│    │  ZW-235-240: Adj.   │    │  ZW-136: Price      │       │
│  │  ZW-223-226: 4 Tests│    │  ZW-241: Adj Value  │    │  ZW-137: Confidence │       │
│  │  ZW-227: HBU Score  │    │  ZW-242: Confidence │    │  ZW-146-147: SHAP   │       │
│  └──────────┬──────────┘    └──────────┬──────────┘    └──────────┬──────────┘       │
│             │                          │                          │                   │
│             │ 0-100                    │ 0-100                    │ 0-100            │
│             └──────────────────────────┼──────────────────────────┘                   │
│                                        │                                               │
│                                        ▼                                               │
│                         ┌─────────────────────────────┐                               │
│                         │   COMPOSITE CALCULATION     │                               │
│                         │                             │                               │
│                         │   Score = (HBU × 0.30) +    │                               │
│                         │           (CMA × 0.30) +    │                               │
│                         │           (ML × 0.40)       │                               │
│                         └──────────────┬──────────────┘                               │
│                                        │                                               │
│                                        ▼                                               │
│                         ┌─────────────────────────────┐                               │
│                         │    DECISION THRESHOLDS      │                               │
│                         │                             │                               │
│                         │  ZW-166 (Bid/Judgment):     │                               │
│                         │  • ≥75% → BID candidate     │                               │
│                         │  • 60-74% → REVIEW          │                               │
│                         │  • <60% → SKIP              │                               │
│                         │                             │                               │
│                         │  ZW-264 (Red Flags):        │                               │
│                         │  • Any TRUE → Auto-SKIP     │                               │
│                         └──────────────┬──────────────┘                               │
│                                        │                                               │
│                                        ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                              TO UI: ZW-167                                       │   │
│  │                                                                                   │   │
│  │    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                    │   │
│  │    │  🟢 BID     │      │  🟡 REVIEW  │      │  ⚪ SKIP    │                    │   │
│  │    │  (Green)    │      │  (Yellow)   │      │  (Gray)     │                    │   │
│  │    └─────────────┘      └─────────────┘      └─────────────┘                    │   │
│  │                                                                                   │   │
│  │    PropertyCard.jsx badge     MapboxMap.jsx pin color     FilterPanel.jsx       │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Mapbox Heatmap ↔ KPI Integration

### Heatmap Layers Using Specific KPIs

| Heatmap Layer | Source KPIs | Color Scale | Toggle ID |
|---------------|-------------|-------------|-----------|
| **Price Heatmap** | ZW-179 median_home_value | Blue (low) → Red (high) | layer-price |
| **Appreciation Heatmap** | ZW-198 appreciation_yoy | Red (neg) → Green (pos) | layer-appreciation |
| **Vacancy Heatmap** | ZW-186 vacancy_rate | Green (low) → Red (high) | layer-vacancy |
| **Income Heatmap** | ZW-178 median_household_income | Yellow → Green | layer-income |
| **ROI Heatmap** | ZW-173 estimated_roi | Red (neg) → Green (high) | layer-roi |
| **Risk Heatmap** | ZW-257 composite_risk_score | Green (0) → Red (100) | layer-risk |

### Property Pin Colors from ZW-167

```javascript
// MapboxMap.jsx - Pin color based on ZW-167 recommendation
const getPinColor = (recommendation) => {
  switch (recommendation) {
    case 'BID':    return '#22C55E'; // Green
    case 'REVIEW': return '#EAB308'; // Yellow  
    case 'SKIP':   return '#9CA3AF'; // Gray
    default:       return '#6B7280'; // Default gray
  }
};

// Pin size based on ZW-094 final_judgment
const getPinSize = (judgment) => {
  if (judgment > 500000) return 'large';
  if (judgment > 200000) return 'medium';
  return 'small';
};
```

---

## Report Generation: 298 KPIs → DOCX

### Report Template Structure

```
BIDDEED.AI PROPERTY REPORT
═══════════════════════════════════════════════════════════════

SECTION 1: EXECUTIVE SUMMARY
├── ZW-003: Address
├── ZW-167: Recommendation (BID/REVIEW/SKIP)
├── ZW-165: Max Bid Amount
├── ZW-094: Final Judgment
├── ZW-166: Bid/Judgment Ratio
├── ZW-173: Estimated ROI
└── ZW-257: Risk Score

SECTION 2: PROPERTY DETAILS (14 KPIs)
├── ZW-001 to ZW-012: Identification
└── ZW-151 to ZW-164: Physical

SECTION 3: ZONING ANALYSIS (62 KPIs)
├── ZW-013 to ZW-036: Base Zoning
├── ZW-037 to ZW-048: Uses
└── ZW-049 to ZW-074: Development

SECTION 4: FINANCIAL ANALYSIS (22 KPIs)
├── ZW-093 to ZW-114: Financial Metrics
└── Shapira Formula™ Calculation

SECTION 5: LIEN ANALYSIS (20 KPIs)
├── ZW-115 to ZW-134: Liens
├── Priority Diagram
└── Survival Analysis

SECTION 6: ML PREDICTIONS (16 KPIs)
├── ZW-135 to ZW-150: XGBoost Model
├── Confidence Score
└── Feature Importance

SECTION 7: MARKET ANALYSIS (44 KPIs)
├── ZW-177 to ZW-190: Demographics
├── ZW-191 to ZW-204: Market
└── ZW-205 to ZW-220: Comps

SECTION 8: HBU & CMA (28 KPIs)
├── ZW-221 to ZW-232: Highest & Best Use
└── ZW-233 to ZW-248: Comparable Market Analysis

SECTION 9: RISK ASSESSMENT (16 KPIs)
├── ZW-249 to ZW-258: Risk Scores
└── ZW-259 to ZW-264: Red Flags

SECTION 10: APPENDICES
├── BCPAO Photo
├── Comp Photos
├── Lien Documents
└── Source Citations
```

---

## GitHub Repository Structure

### All Documentation Deployed To:

```
breverdbidder/zonewise/
└── docs/
    ├── architecture/
    │   ├── ARCHITECTURE_DECISION_2026-01-25.md
    │   ├── FULL_STACK_SPECIFICATION.md
    │   ├── UI_UX_MAPBOX_SPLIT_SCREEN_SPECIFICATION.md
    │   ├── DFD_CLAUDE_AI_REAL_ESTATE_298_KPI.md
    │   └── MASTER_INTEGRATION.md  ← This document
    ├── data/
    │   ├── KPI_FRAMEWORK_298_COMPLETE.md
    │   └── DATA_FRAMEWORK_20_PHASES_10_STAGES.md
    ├── planning/
    │   └── EXECUTION_PLAN_12_WEEKS.md
    └── research/
        └── GITHUB_REPOSITORY_ANALYSIS.md

breverdbidder/competitive-intelligence/
└── docs/
    ├── architecture/
    │   ├── UI_UX_MAPBOX_SPLIT_SCREEN_SPECIFICATION.md
    │   └── DFD_CLAUDE_AI_REAL_ESTATE_298_KPI.md
    ├── KPI_FRAMEWORK_298_COMPLETE.md
    └── [Competitor PRDs: PropertyOnion, Reventure, Gridics, etc.]

breverdbidder/brevard-bidder-scraper/
└── docs/
    ├── KPI_FRAMEWORK_298_COMPLETE.md
    └── DFD_CLAUDE_AI_REAL_ESTATE_298_KPI.md
```

---

## Quick Reference: KPI Range by Feature

| Feature | Start KPI | End KPI | Count | Source |
|---------|-----------|---------|-------|--------|
| Property ID | ZW-001 | ZW-012 | 12 | BCPAO |
| Zoning | ZW-013 | ZW-074 | 62 | Municode |
| Auction | ZW-075 | ZW-092 | 18 | RealForeclose |
| Financial | ZW-093 | ZW-114 | 22 | Clerk/BCPAO |
| Liens | ZW-115 | ZW-134 | 20 | AcclaimWeb |
| ML | ZW-135 | ZW-150 | 16 | XGBoost |
| Physical | ZW-151 | ZW-164 | 14 | BCPAO |
| Investment | ZW-165 | ZW-176 | 12 | Calculated |
| Demographics | ZW-177 | ZW-190 | 14 | Census |
| Market | ZW-191 | ZW-204 | 14 | APIs |
| Comps | ZW-205 | ZW-220 | 16 | BCPAO/MLS |
| HBU | ZW-221 | ZW-232 | 12 | Analysis |
| CMA | ZW-233 | ZW-248 | 16 | Analysis |
| Risk | ZW-249 | ZW-258 | 10 | Calculated |
| Red Flags | ZW-259 | ZW-264 | 6 | Calculated |
| Development | ZW-265 | ZW-280 | 16 | Municode |
| Environmental | ZW-281 | ZW-298 | 18 | FEMA/GIS |
| **TOTAL** | **ZW-001** | **ZW-298** | **298** | **Multiple** |

---

*This master integration document connects the DFD, UI/UX specification, and 298 KPI framework into a unified "Claude AI for Real Estate" ecosystem.*
