# ZoneWise Real-Time Appraisal Intelligence (RAI)
## Product Requirements Document v1.0
**Date:** January 20, 2026
**Author:** AI Architect (Claude)
**Status:** FOUNDATIONAL PRIORITY

---

## Executive Summary

ZoneWise RAI transforms the traditional appraisal report process from a **6-month-stale document** into a **real-time intelligence system** powered by 298 KPIs. This creates defensible competitive moat and immediate customer value.

**Reference:** Analyzed `Appraisal-Report.pdf` (EquiValue Appraisal LLC, January 2020) - a USPAP-compliant multi-family appraisal demonstrating industry-standard format and methodology.

---

## Problem Statement

Traditional appraisal reports:
- **Stale by design:** 30-90 days from engagement to delivery
- **Manual data gathering:** Appraisers spend 60%+ time on data collection
- **Point-in-time snapshot:** No ongoing monitoring or alerts
- **Expensive:** $3,000-$15,000+ per commercial appraisal
- **No integration:** Delivered as static PDFs, no actionable workflow

**The uploaded report is 6 years old** - demonstrating how quickly appraisal intelligence becomes obsolete.

---

## Solution: ZoneWise RAI

### Core Value Proposition

> "Every property in Florida analyzed against 298 KPIs, updated in real-time, delivered as investor-ready reports with one click."

### Three Delivery Modes

| Mode | Use Case | Update Frequency | Price Point |
|------|----------|------------------|-------------|
| **Snapshot Report** | Pre-auction due diligence | On-demand | $99/property |
| **Monitoring Dashboard** | Portfolio tracking | Daily | $49/property/month |
| **Full Appraisal Package** | Formal valuation support | Weekly refresh | $499/property |

---

## 298 KPI → Appraisal Section Mapping

### 1. LETTER OF TRANSMITTAL (Auto-Generated)
*No KPIs - Template with property/client variables*

### 2. SUMMARY OF SALIENT FACTS (25 KPIs)

| KPI Code | KPI Name | Data Source | Appraisal Use |
|----------|----------|-------------|---------------|
| SUM-001 | Property Address | BCPAO/Parcel | Legal identification |
| SUM-002 | Parcel ID | BCPAO | Tax record linkage |
| SUM-003 | Legal Description | BCPAO | Title verification |
| SUM-004 | Total Acreage | BCPAO | Site area |
| SUM-005 | Current Owner | BCPAO | Chain of title |
| SUM-006 | Last Sale Date | BCPAO | Sale history |
| SUM-007 | Last Sale Price | BCPAO | Prior value benchmark |
| SUM-008 | Assessed Value - Land | BCPAO | Tax basis |
| SUM-009 | Assessed Value - Improvements | BCPAO | Tax basis |
| SUM-010 | Total Assessed Value | BCPAO | Tax burden context |
| SUM-011 | Annual Property Taxes | Tax Collector | Operating expense |
| SUM-012 | Tax Payment Status | Tax Collector | Delinquency check |
| SUM-013 | Zoning Code | Jurisdiction | Use restrictions |
| SUM-014 | Zoning Description | Jurisdiction | Permitted uses |
| SUM-015 | FEMA Flood Zone | FEMA | Risk assessment |
| SUM-016 | Effective Date | System | Report timestamp |
| SUM-017 | Property Type Classification | ML Model | Asset class |
| SUM-018 | Gross Building Area | BCPAO | Size metric |
| SUM-019 | Year Built | BCPAO | Age/condition |
| SUM-020 | Number of Units | BCPAO | Multi-family metric |
| SUM-021 | Construction Type | BCPAO | Replacement cost |
| SUM-022 | Quality Grade | ML Model | Condition rating |
| SUM-023 | Current Listing Status | MLS/Public | Market exposure |
| SUM-024 | Days on Market | MLS/Public | Absorption metric |
| SUM-025 | Listing Price | MLS/Public | Ask price benchmark |

### 3. MARKET AREA ANALYSIS (52 KPIs)

#### Economic Indicators (15)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| MKT-001 | Population (MSA) | Census API |
| MKT-002 | Population Growth Rate | Census API |
| MKT-003 | Median Household Income | Census API |
| MKT-004 | Income Growth Rate | Census API |
| MKT-005 | Unemployment Rate | BLS |
| MKT-006 | Employment Growth | BLS |
| MKT-007 | Major Employers | Web Scrape |
| MKT-008 | Industry Concentration | BLS |
| MKT-009 | GDP Growth (Metro) | BEA |
| MKT-010 | Cost of Living Index | Council for Community |
| MKT-011 | Poverty Rate | Census API |
| MKT-012 | Education Level | Census API |
| MKT-013 | Age Demographics | Census API |
| MKT-014 | Household Size | Census API |
| MKT-015 | Rental Household % | Census API |

#### Real Estate Market (20)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| MKT-016 | Median Home Value | Zillow/Redfin |
| MKT-017 | YoY Price Change | Zillow/Redfin |
| MKT-018 | Price Per SF | MLS Aggregated |
| MKT-019 | Inventory Level | MLS |
| MKT-020 | Months of Supply | MLS |
| MKT-021 | Days on Market (Median) | MLS |
| MKT-022 | List-to-Sale Ratio | MLS |
| MKT-023 | New Construction Permits | Census Building Permits |
| MKT-024 | Foreclosure Rate | RealtyTrac |
| MKT-025 | Vacancy Rate | Census ACS |
| MKT-026 | Rental Rate Growth | Zillow/RentCafe |
| MKT-027 | Cap Rate (Market) | CoStar/CBRE |
| MKT-028 | Absorption Rate | MLS/CoStar |
| MKT-029 | New Supply Pipeline | CoStar |
| MKT-030 | Investor Purchase % | Deed Records |
| MKT-031 | Cash Purchase % | Deed Records |
| MKT-032 | Distressed Sale % | Deed Records |
| MKT-033 | Mortgage Rate (30yr) | Freddie Mac |
| MKT-034 | Affordability Index | NAHB |
| MKT-035 | Price-to-Rent Ratio | Calculated |

#### Location Quality (17)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| MKT-036 | Walk Score | Walk Score API |
| MKT-037 | Transit Score | Walk Score API |
| MKT-038 | Bike Score | Walk Score API |
| MKT-039 | School Rating (Elementary) | GreatSchools |
| MKT-040 | School Rating (Middle) | GreatSchools |
| MKT-041 | School Rating (High) | GreatSchools |
| MKT-042 | Crime Index | NeighborhoodScout |
| MKT-043 | Distance to Employment | Google Maps |
| MKT-044 | Distance to Hospital | Google Maps |
| MKT-045 | Distance to Airport | Google Maps |
| MKT-046 | Distance to Beach | Google Maps |
| MKT-047 | Grocery Access | Google Places |
| MKT-048 | Restaurant Density | Google Places |
| MKT-049 | Retail Access | Google Places |
| MKT-050 | Park Proximity | Google Places |
| MKT-051 | Traffic Volume (AADT) | FDOT |
| MKT-052 | Road Frontage Type | GIS |

### 4. PROPERTY DESCRIPTION (35 KPIs)

#### Site Analysis (12)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| SITE-001 | Lot Size (Acres) | BCPAO |
| SITE-002 | Lot Size (SF) | BCPAO |
| SITE-003 | Lot Dimensions | BCPAO |
| SITE-004 | Shape Factor | GIS Calculated |
| SITE-005 | Topography | USGS/LiDAR |
| SITE-006 | Street Frontage (Feet) | GIS |
| SITE-007 | Access Points | Aerial/GIS |
| SITE-008 | Utilities Available | Jurisdiction |
| SITE-009 | Easements | AcclaimWeb |
| SITE-010 | Wetland Percentage | SJRWMD |
| SITE-011 | Environmental Issues | EPA/DEP |
| SITE-012 | Corner Lot Flag | GIS |

#### Improvements (23)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| IMP-001 | Total Living Area (SF) | BCPAO |
| IMP-002 | Building Count | BCPAO |
| IMP-003 | Stories | BCPAO |
| IMP-004 | Unit Count | BCPAO |
| IMP-005 | Unit Mix (BR Distribution) | BCPAO/Inspection |
| IMP-006 | Average Unit Size | BCPAO |
| IMP-007 | Parking Spaces | BCPAO/Inspection |
| IMP-008 | Parking Ratio | Calculated |
| IMP-009 | Year Built | BCPAO |
| IMP-010 | Effective Age | Inspection/ML |
| IMP-011 | Remaining Economic Life | ML Model |
| IMP-012 | Construction Quality | BCPAO/Inspection |
| IMP-013 | Condition Rating | Inspection/ML |
| IMP-014 | Roof Type/Age | Inspection |
| IMP-015 | HVAC Type/Age | Inspection |
| IMP-016 | Amenities Score | Listing/Inspection |
| IMP-017 | ADA Compliance | Inspection |
| IMP-018 | Deferred Maintenance | Inspection/ML |
| IMP-019 | Capital Needs (5yr) | ML Model |
| IMP-020 | Energy Efficiency Rating | ML Model |
| IMP-021 | Insurance Cost/SF | Quote API |
| IMP-022 | Replacement Cost/SF | Marshall & Swift |
| IMP-023 | Depreciation % | Calculated |

### 5. HIGHEST & BEST USE ANALYSIS (28 KPIs)

#### Legally Permissible (8)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| HBU-001 | Zoning Designation | Jurisdiction |
| HBU-002 | Permitted Uses List | Zoning Code |
| HBU-003 | Conditional Uses List | Zoning Code |
| HBU-004 | Density Allowed (units/acre) | Zoning Code |
| HBU-005 | FAR Allowed | Zoning Code |
| HBU-006 | Height Limit | Zoning Code |
| HBU-007 | Setback Requirements | Zoning Code |
| HBU-008 | Overlay Districts | Jurisdiction |

#### Physically Possible (6)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| HBU-009 | Buildable Area | GIS Calculated |
| HBU-010 | Max Building Footprint | Zoning + Site |
| HBU-011 | Max Unit Count | Density × Acres |
| HBU-012 | Soil Bearing Capacity | Soils Data |
| HBU-013 | Flood Risk Impact | FEMA |
| HBU-014 | Environmental Constraints | Combined |

#### Financially Feasible (8)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| HBU-015 | Land Value Residual | ML Model |
| HBU-016 | Development Cost/Unit | Marshall Swift |
| HBU-017 | Market Rent/Unit | Rent Comps |
| HBU-018 | Stabilized NOI Potential | Pro Forma |
| HBU-019 | Required Cap Rate | Market |
| HBU-020 | Development Yield | Calculated |
| HBU-021 | Profit Margin % | Calculated |
| HBU-022 | Payback Period | Calculated |

#### Maximally Productive (6)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| HBU-023 | Current Use Value | Income/Sales |
| HBU-024 | Alt Use 1 Value | Pro Forma |
| HBU-025 | Alt Use 2 Value | Pro Forma |
| HBU-026 | Alt Use 3 Value | Pro Forma |
| HBU-027 | HBU Conclusion | ML Ranking |
| HBU-028 | Value Uplift Potential | Max - Current |

### 6. VALUATION - SALES COMPARISON (48 KPIs)

#### Comparable Selection (12)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| CMP-001 | Comp 1 Address | MLS/Deed |
| CMP-002 | Comp 1 Sale Price | Deed |
| CMP-003 | Comp 1 Sale Date | Deed |
| CMP-004 | Comp 1 Price/SF | Calculated |
| CMP-005 | Comp 1 Price/Unit | Calculated |
| CMP-006 | Comp 1 Distance | GIS |
| CMP-007 | Comp 1 Similarity Score | ML Model |
| CMP-008 | Comp 1 Time Adjustment | Market Trend |
| CMP-009 | Comp 1 Location Adjustment | ML Model |
| CMP-010 | Comp 1 Physical Adjustment | ML Model |
| CMP-011 | Comp 1 Adjusted Price | Calculated |
| CMP-012 | Comp 1 Cap Rate | Calculated |
*Repeat CMP-001 through CMP-012 for Comps 2-4 = 48 KPIs*

#### Sales Comparison Synthesis (12)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| SCA-001 | Comparable Range Low | Comps |
| SCA-002 | Comparable Range High | Comps |
| SCA-003 | Median Adjusted Price | Comps |
| SCA-004 | Average Adjusted Price | Comps |
| SCA-005 | Weighted Average Price | ML Weights |
| SCA-006 | Adjustment Magnitude | QC Metric |
| SCA-007 | Market Conditions Trend | Time Adj |
| SCA-008 | Sales Comparison Value | Reconciled |
| SCA-009 | Confidence Score | ML Model |
| SCA-010 | Value Per SF Indicated | Calculated |
| SCA-011 | Value Per Unit Indicated | Calculated |
| SCA-012 | Gross Rent Multiplier | Market |

### 7. VALUATION - INCOME APPROACH (45 KPIs)

#### Revenue (15)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| INC-001 | Potential Gross Income | Rent Roll × Market |
| INC-002 | Market Rent/Unit (1BR) | Rent Comps |
| INC-003 | Market Rent/Unit (2BR) | Rent Comps |
| INC-004 | Market Rent/Unit (3BR) | Rent Comps |
| INC-005 | Contract Rent Total | Rent Roll |
| INC-006 | Rent Premium/Discount | Contract vs Market |
| INC-007 | Other Income - Parking | Rent Roll |
| INC-008 | Other Income - Laundry | Rent Roll |
| INC-009 | Other Income - Pet Fees | Rent Roll |
| INC-010 | Other Income - Storage | Rent Roll |
| INC-011 | Other Income - Late Fees | Rent Roll |
| INC-012 | Vacancy Rate (Subject) | Rent Roll |
| INC-013 | Vacancy Rate (Market) | CoStar/REIS |
| INC-014 | Credit Loss | Historical |
| INC-015 | Effective Gross Income | Calculated |

#### Expenses (18)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| EXP-001 | Real Estate Taxes | Tax Collector |
| EXP-002 | Insurance | Quote/Historical |
| EXP-003 | Utilities - Common Area | Historical |
| EXP-004 | Utilities - Owner Paid | Historical |
| EXP-005 | Management Fee % | Market/Historical |
| EXP-006 | Management Fee $ | Calculated |
| EXP-007 | Payroll | Historical |
| EXP-008 | Repairs & Maintenance | Historical |
| EXP-009 | Contract Services | Historical |
| EXP-010 | Marketing/Advertising | Historical |
| EXP-011 | Administrative | Historical |
| EXP-012 | Professional Fees | Historical |
| EXP-013 | Reserves | Industry Standard |
| EXP-014 | Total Operating Expenses | Calculated |
| EXP-015 | Expense Ratio | Calculated |
| EXP-016 | Expense/Unit | Calculated |
| EXP-017 | Expense/SF | Calculated |
| EXP-018 | Expense Growth Rate | Historical |

#### Capitalization (12)
| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| CAP-001 | Net Operating Income | Calculated |
| CAP-002 | NOI/Unit | Calculated |
| CAP-003 | NOI/SF | Calculated |
| CAP-004 | Market Cap Rate | CoStar/Survey |
| CAP-005 | Band of Investment Rate | Calculated |
| CAP-006 | Built-Up Cap Rate | Risk Analysis |
| CAP-007 | Selected Cap Rate | Reconciled |
| CAP-008 | Direct Cap Value | NOI/Cap |
| CAP-009 | DCF Value (10yr) | Pro Forma |
| CAP-010 | Reversion Cap Rate | Market +50bp |
| CAP-011 | Discount Rate | Market |
| CAP-012 | Income Approach Value | Reconciled |

### 8. VALUATION - COST APPROACH (20 KPIs)

| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| CST-001 | Land Value | Comparable Sales |
| CST-002 | Land Value/Acre | Calculated |
| CST-003 | Land Value/Unit | Calculated |
| CST-004 | Replacement Cost New | Marshall Swift |
| CST-005 | RCN/SF | Calculated |
| CST-006 | Physical Depreciation % | Age/Life |
| CST-007 | Physical Depreciation $ | Calculated |
| CST-008 | Functional Obsolescence % | Inspection |
| CST-009 | Functional Obsolescence $ | Calculated |
| CST-010 | External Obsolescence % | Market |
| CST-011 | External Obsolescence $ | Calculated |
| CST-012 | Total Depreciation % | Sum |
| CST-013 | Total Depreciation $ | Sum |
| CST-014 | Depreciated Value | RCN - Deprec |
| CST-015 | Site Improvements | Estimate |
| CST-016 | Total Improvement Value | Calculated |
| CST-017 | Cost Approach Value | Land + Improvements |
| CST-018 | Insurable Value | RCN excl Land |
| CST-019 | Cost/Unit | Calculated |
| CST-020 | Cost/SF | Calculated |

### 9. RECONCILIATION (15 KPIs)

| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| REC-001 | Sales Comparison Value | From SCA |
| REC-002 | Sales Comparison Weight | Appraiser |
| REC-003 | Income Approach Value | From INC |
| REC-004 | Income Approach Weight | Appraiser |
| REC-005 | Cost Approach Value | From CST |
| REC-006 | Cost Approach Weight | Appraiser |
| REC-007 | Weighted Average Value | Calculated |
| REC-008 | Value Range Low | -10% |
| REC-009 | Value Range High | +10% |
| REC-010 | Final Value Opinion | Rounded |
| REC-011 | Value/SF | Calculated |
| REC-012 | Value/Unit | Calculated |
| REC-013 | Overall Cap Rate | Value/NOI |
| REC-014 | Exposure Time | Market |
| REC-015 | Marketing Time | Market |

### 10. RISK & OPPORTUNITY (20 KPIs) - **ZoneWise Exclusive**

| KPI Code | KPI Name | Data Source |
|----------|----------|-------------|
| RSK-001 | Title Risk Score | AcclaimWeb ML |
| RSK-002 | Lien Priority Status | Lien Analysis |
| RSK-003 | Senior Debt Outstanding | AcclaimWeb |
| RSK-004 | Tax Certificate Status | RealTDM |
| RSK-005 | Code Violation Flag | Jurisdiction |
| RSK-006 | Environmental Risk | EPA/DEP |
| RSK-007 | Flood Insurance Required | FEMA |
| RSK-008 | Hurricane Risk Rating | AIR/RMS |
| RSK-009 | Market Risk Score | Volatility ML |
| RSK-010 | Tenant Concentration | Rent Roll |
| RSK-011 | Value Add Opportunity | Gap Analysis |
| RSK-012 | Rent Increase Potential | Market vs Contract |
| RSK-013 | Expense Reduction Potential | Benchmark |
| RSK-014 | Repositioning Opportunity | Use Analysis |
| RSK-015 | Development Upside | HBU vs Current |
| RSK-016 | Exit Probability (12mo) | ML Model |
| RSK-017 | Expected IRR | Pro Forma |
| RSK-018 | Downside Scenario Value | Stress Test |
| RSK-019 | Upside Scenario Value | Optimistic |
| RSK-020 | ZoneWise Confidence Score | Ensemble ML |

---

## Total KPI Count by Section

| Section | KPI Count |
|---------|-----------|
| Summary of Salient Facts | 25 |
| Market Area Analysis | 52 |
| Property Description | 35 |
| Highest & Best Use | 28 |
| Sales Comparison | 60 |
| Income Approach | 45 |
| Cost Approach | 20 |
| Reconciliation | 15 |
| Risk & Opportunity | 20 |
| **TOTAL** | **300** |

*Note: 298 in original spec; 300 provides complete coverage with 2 reserved for future expansion*

---

## Data Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZONEWISE RAI ENGINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   BCPAO API  │  │ Census API   │  │  MLS/Zillow  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐          │
│  │ AcclaimWeb   │  │  Tax Coll.   │  │   CoStar     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └────────────┬────┴────┬────────────┘                   │
│                      │         │                                │
│              ┌───────▼─────────▼───────┐                        │
│              │    DATA LAKE (Supabase) │                        │
│              │   • raw_property_data   │                        │
│              │   • kpi_values          │                        │
│              │   • market_snapshots    │                        │
│              └───────────┬─────────────┘                        │
│                          │                                      │
│              ┌───────────▼─────────────┐                        │
│              │     KPI CALCULATOR      │                        │
│              │   • 298 KPI Formulas    │                        │
│              │   • ML Models (XGBoost) │                        │
│              │   • Validation Rules    │                        │
│              └───────────┬─────────────┘                        │
│                          │                                      │
│              ┌───────────▼─────────────┐                        │
│              │   REPORT GENERATOR      │                        │
│              │   • DOCX Engine         │                        │
│              │   • PDF Renderer        │                        │
│              │   • Branding Layer      │                        │
│              └───────────┬─────────────┘                        │
│                          │                                      │
│              ┌───────────▼─────────────┐                        │
│              │   DELIVERY SYSTEM       │                        │
│              │   • API Endpoint        │                        │
│              │   • Email Distribution  │                        │
│              │   • Dashboard Embed     │                        │
│              └─────────────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Additions

```sql
-- Real-Time Appraisal Report Queue
CREATE TABLE appraisal_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parcel_id VARCHAR(50) NOT NULL,
    report_type VARCHAR(20) CHECK (report_type IN ('SNAPSHOT', 'MONITORING', 'FULL')),
    client_id UUID REFERENCES clients(id),
    effective_date TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'PENDING',
    kpi_values JSONB,
    generated_docx_url TEXT,
    generated_pdf_url TEXT,
    zonewise_score DECIMAL(5,2),
    value_opinion DECIMAL(15,2),
    confidence_level DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- KPI Values per Report
CREATE TABLE report_kpi_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES appraisal_reports(id) ON DELETE CASCADE,
    kpi_code VARCHAR(20) REFERENCES kpi_definitions(kpi_code),
    raw_value TEXT,
    formatted_value TEXT,
    data_source VARCHAR(100),
    source_date TIMESTAMPTZ,
    confidence VARCHAR(20) CHECK (confidence IN ('HIGH', 'MEDIUM', 'LOW', 'ESTIMATED')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Report Templates
CREATE TABLE report_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(100) NOT NULL,
    property_type VARCHAR(50),
    template_docx_path TEXT,
    section_config JSONB,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Report Output Format

### File Naming Convention
```
ZoneWise_RAI_{ParcelID}_{ReportType}_{YYYYMMDD}.docx
ZoneWise_RAI_{ParcelID}_{ReportType}_{YYYYMMDD}.pdf
```

### Example:
```
ZoneWise_RAI_2711230000010010_SNAPSHOT_20260120.docx
```

### Report Sections (Auto-Generated)

1. **Cover Page** - ZoneWise branded, property photo, key metrics
2. **Executive Summary** - One-page decision brief with ZoneWise Score
3. **Property Overview** - Salient facts, photos, aerial view
4. **Market Analysis** - Dynamic charts, trend lines, forecast
5. **Valuation Summary** - Three approaches reconciled
6. **Risk Assessment** - Heat map, flags, recommendations
7. **Data Sources** - Transparency on all 298 KPIs
8. **Appendix** - Supporting data, comp sheets, maps

---

## Competitive Advantage

| Feature | Traditional Appraisal | ZoneWise RAI |
|---------|----------------------|--------------|
| Turnaround | 2-4 weeks | Instant |
| Update Frequency | One-time | Continuous |
| Data Points | ~50 manual | 298 automated |
| Cost | $3,000-$15,000 | $99-$499 |
| ML Predictions | None | XGBoost ensemble |
| Risk Scoring | Subjective | Quantified |
| Integration | PDF only | API + Dashboard |

---

## Phase 1 Implementation (4 Weeks)

### Week 1: Data Pipeline
- [ ] Map all 298 KPIs to data sources
- [ ] Build API integrations for 10 primary sources
- [ ] Create kpi_values table and populate for Brevard County

### Week 2: KPI Calculator
- [ ] Implement calculation formulas for all KPIs
- [ ] Integrate existing ML models (XGBoost)
- [ ] Build validation and quality checks

### Week 3: Report Generator
- [ ] Create DOCX template with all sections
- [ ] Build dynamic content injection
- [ ] Add charting and visualization

### Week 4: Delivery System
- [ ] API endpoint for report generation
- [ ] Queue system for batch processing
- [ ] Dashboard integration

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Report Generation Time | <30 seconds | API logs |
| KPI Coverage | 100% (298/298) | Automated check |
| Data Freshness | <24 hours | Source timestamps |
| Customer Satisfaction | >4.5/5 | Survey |
| Revenue per Report | $150 avg | Stripe |

---

## Next Steps

1. **IMMEDIATE:** Deploy 298 KPI schema to Supabase
2. **THIS WEEK:** Build report DOCX generator with docx-js
3. **NEXT WEEK:** Integrate first 10 data sources
4. **MONTH 1:** Launch beta with 3 pilot customers

---

*This document establishes ZoneWise RAI as the foundational product capability that transforms static appraisal reports into real-time property intelligence.*
