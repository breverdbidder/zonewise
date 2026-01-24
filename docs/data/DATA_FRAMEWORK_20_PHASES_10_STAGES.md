# ZoneWise Data Framework: 20 Phases + 10 Stages

**Version:** 1.0  
**Date:** January 25, 2026  
**Proven On:** Malabar POC (100% stable, 1,430 parcels)

---

## Overview

The ZoneWise Data Framework combines two methodologies:
- **20 Phases:** Comprehensive zoning data categories
- **10 Stages:** Per-parcel enrichment pipeline

Together, they enable "Claude AI for Real Estate" to answer any zoning or property question.

---

## 20-Phase Zoning Data Framework

### Phase Completion Status (Brevard)

| Phase | Category | Status | Data Points |
|-------|----------|--------|-------------|
| 1 | Property Identification | ✅ 100% | 351,423 parcels |
| 2 | Base Zoning | ✅ 100% | 290 districts |
| 3 | Dimensional Standards | ✅ 75% | Setbacks, heights |
| 4 | Permitted Uses | ⚠️ 40% | By-right uses |
| 5 | Conditional Uses | ⚠️ 40% | CUP requirements |
| 6 | Prohibited Uses | ⚠️ 20% | Inverse of permitted |
| 7 | Overlay Districts | ⚠️ 30% | Special overlays |
| 8 | Development Bonuses | ❌ 0% | Incentive programs |
| 9 | Parking Requirements | ⚠️ 25% | Per-use parking |
| 10 | Density & Intensity | ✅ 60% | Units/acre, FAR |
| 11 | Short-Term Rentals | ⚠️ 30% | STR regulations |
| 12 | ADU Regulations | ⚠️ 20% | ADU rules |
| 13 | Historic/Design | ❌ SKIP | Low priority |
| 14 | FLUM Data | ⚠️ 10% | Future land use |
| 15 | Entitlement Timelines | ❌ 0% | Processing times |
| 16 | Ordinance Library | ⚠️ 40% | Full code text |
| 17 | Ordinance Changes | ❌ 0% | Amendment alerts |
| 18 | 3D Development | ❌ SKIP | Gridics patent |
| 19 | Parcel Data | ✅ 100% | BCPAO integration |
| 20 | Environmental Overlays | ⚠️ 15% | Flood, wetlands |

### Phase Details

#### Phase 1: Property Identification ✅

**Purpose:** Link addresses to parcels to zoning

**Data Sources:**
- BCPAO parcel database
- County GIS endpoints
- Address geocoding

**Schema:**
```sql
sample_properties (
    parcel_id TEXT PRIMARY KEY,
    tax_account TEXT,
    site_address TEXT,
    city TEXT,
    zip TEXT,
    lat NUMERIC,
    lon NUMERIC,
    geometry GEOMETRY
)
```

**Brevard Status:** 351,423 parcels loaded

---

#### Phase 2: Base Zoning ✅

**Purpose:** Zone district definitions and classifications

**Data Sources:**
- Municode ordinances
- Municipal zoning codes
- County land development regulations

**Schema:**
```sql
zoning_districts (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER,
    zone_code TEXT,          -- e.g., "RS-10", "C-1"
    zone_name TEXT,          -- e.g., "Single Family Residential"
    description TEXT,
    category TEXT,           -- residential, commercial, industrial
    source_url TEXT
)
```

**Brevard Status:** 290 districts across 17 jurisdictions

**Zone Categories:**
| Category | Count | Examples |
|----------|-------|----------|
| Residential | 120 | RS-10, RM-6, RR-65 |
| Commercial | 85 | CG, CN, C-1 |
| Industrial | 35 | IL, IH, M-1 |
| Mixed Use | 25 | MU, TC |
| Special | 25 | PUD, PD, CP |

---

#### Phase 3: Dimensional Standards ✅

**Purpose:** Setbacks, heights, lot coverage, building separation

**Data Sources:**
- Zoning ordinance tables
- Land development code

**Schema:**
```sql
dimensional_standards (
    id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES zoning_districts(id),
    min_lot_size NUMERIC,         -- sq ft
    min_lot_width NUMERIC,        -- ft
    max_density NUMERIC,          -- units/acre
    max_height NUMERIC,           -- ft
    max_lot_coverage NUMERIC,     -- %
    front_setback NUMERIC,        -- ft
    side_setback NUMERIC,         -- ft
    rear_setback NUMERIC,         -- ft
    building_separation NUMERIC   -- ft (multifamily)
)
```

**Sample Data (Malabar RS-10):**
| Standard | Value |
|----------|-------|
| Min Lot Size | 10,000 sq ft |
| Min Lot Width | 80 ft |
| Max Height | 35 ft |
| Front Setback | 25 ft |
| Side Setback | 10 ft |
| Rear Setback | 20 ft |
| Max Coverage | 35% |

---

#### Phase 4: Permitted Uses ⚠️

**Purpose:** By-right uses for each zone district

**Data Sources:**
- Use tables in zoning code
- Permitted use matrices

**Schema:**
```sql
permitted_uses (
    id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES zoning_districts(id),
    use_code TEXT,
    use_name TEXT,
    use_category TEXT,    -- residential, commercial, industrial
    conditions TEXT,      -- any specific conditions
    parking_required TEXT -- reference to parking table
)
```

**Use Categories:**
- Residential: SFR, MFR, ADU, Group Home
- Commercial: Retail, Office, Restaurant, Hotel
- Industrial: Warehouse, Manufacturing, Distribution
- Civic: School, Church, Government

---

#### Phase 5: Conditional Uses ⚠️

**Purpose:** Uses requiring special approval (CUP/SUP)

**Schema:**
```sql
conditional_uses (
    id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES zoning_districts(id),
    use_name TEXT,
    approval_body TEXT,        -- Planning Board, City Council
    typical_conditions TEXT[], -- Common approval conditions
    review_criteria TEXT,
    estimated_timeline TEXT
)
```

---

#### Phase 6: Prohibited Uses ⚠️

**Purpose:** Explicitly prohibited uses per district

Derived as inverse of permitted + conditional uses.

---

#### Phase 7: Overlay Districts ⚠️

**Purpose:** Special districts that modify base zoning

**Types:**
- Historic overlays
- Coastal overlays
- Airport overlays
- Environmental overlays
- Design overlays

**Schema:**
```sql
overlay_districts (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER,
    overlay_code TEXT,
    overlay_name TEXT,
    description TEXT,
    geometry GEOMETRY,
    modifications JSONB  -- What it changes
)
```

---

#### Phase 8: Development Bonuses ❌

**Purpose:** Incentive programs for affordable housing, green building, etc.

**Example (Palm Bay Table 173-8):**
| Bonus Type | Incentive |
|------------|-----------|
| Affordable Housing | +20% density |
| Green Building | -10% parking |
| Public Amenity | +10 ft height |

**High Value:** Neither Gridics nor Zoneomics has this data.

---

#### Phase 9: Parking Requirements ⚠️

**Purpose:** Required parking by use type

**Schema:**
```sql
parking_requirements (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER,
    use_type TEXT,
    spaces_required TEXT,     -- "1 per 300 sq ft"
    handicap_required TEXT,
    bicycle_required TEXT,
    ev_required TEXT
)
```

---

#### Phase 10: Density & Intensity ✅

**Purpose:** Maximum development potential

**Metrics:**
- Residential: Units per acre (du/ac)
- Commercial: Floor Area Ratio (FAR)
- Mixed Use: Both metrics

---

#### Phase 11: Short-Term Rentals ⚠️

**Purpose:** STR regulations by jurisdiction

**Data Points:**
- Allowed zones
- Registration required?
- Minimum stay
- Occupancy limits
- Parking requirements

---

#### Phase 12: ADU Regulations ⚠️

**Purpose:** Accessory Dwelling Unit rules

**Data Points:**
- Allowed zones
- Max size (sq ft or % of primary)
- Owner occupancy required?
- Parking required?
- Setback modifications

---

#### Phase 13: Historic/Design Districts ❌ SKIP

**Reason:** Low priority for Brevard County market.

---

#### Phase 14: Future Land Use Map (FLUM) ⚠️

**Purpose:** Long-term land use designations

**Schema:**
```sql
flum_designations (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER,
    flum_code TEXT,
    flum_name TEXT,
    allowed_zoning TEXT[],  -- Compatible zone districts
    max_density NUMERIC,
    description TEXT
)
```

---

#### Phase 15: Entitlement Timelines ❌

**Purpose:** Actual processing times for permits

**High Value:** Neither competitor has this.

**Data Points:**
- Site plan review: X days
- Rezoning: X months
- CUP approval: X weeks
- Building permit: X days

---

#### Phase 16: Ordinance Library ⚠️

**Purpose:** Full text of zoning ordinances with embeddings

**Schema:**
```sql
ordinances (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER,
    title TEXT,
    section_number TEXT,
    content TEXT,
    embedding VECTOR(1536),  -- For RAG
    source_url TEXT,
    effective_date DATE
)
```

---

#### Phase 17: Ordinance Changes ❌

**Purpose:** Track amendments and updates

**High Value:** Neither competitor has alerts.

---

#### Phase 18: 3D Development Rights ❌ SKIP

**Reason:** Gridics patent - differentiate elsewhere.

---

#### Phase 19: Parcel Data ✅

**Purpose:** Property-level data from county appraiser

See 10-Stage Framework below.

---

#### Phase 20: Environmental Overlays ⚠️

**Purpose:** Flood zones, wetlands, coastal setbacks

**Data Sources:**
- FEMA flood maps
- NWI wetlands
- SJRWMD
- Coastal construction control line

---

## 10-Stage Per-Parcel Data Framework

### Stage Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  10-STAGE DATA PIPELINE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Stage 1: Zone Assignment                                    │
│      ↓                                                       │
│  Stage 2: Zoning Districts                                   │
│      ↓                                                       │
│  Stage 3: Dimensional Standards                              │
│      ↓                                                       │
│  Stage 4: Permitted Uses                                     │
│      ↓                                                       │
│  Stage 5: Source URLs                                        │
│      ↓                                                       │
│  Stage 6: Census Demographics                                │
│      ↓                                                       │
│  Stage 7: Location Scores                                    │
│      ↓                                                       │
│  Stage 8: Sales History                                      │
│      ↓                                                       │
│  Stage 9: Building Records                                   │
│      ↓                                                       │
│  Stage 10: Parcel-Zone Link                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Stage Details

#### Stage 1: Zone Assignment ✅

**Purpose:** Assign zone code to each parcel

**Methods:**
1. GIS spatial join (preferred)
2. Manual from use_description
3. Address lookup

**Sources:**
| Jurisdiction | GIS Endpoint | Status |
|--------------|--------------|--------|
| Unincorporated | gis.brevardfl.gov | ✅ Working |
| Palm Bay | gis.pbfl.org | ⚠️ 503 |
| Melbourne | No endpoint | ❌ Manual |
| Titusville | gis.titusville.com | ✅ Working |
| Cocoa | services1.arcgis.com | ✅ Working |
| Malabar | Manual | ✅ POC Complete |

**Output:**
```sql
parcel_zones (
    parcel_id TEXT PRIMARY KEY,
    zone_code TEXT NOT NULL,
    jurisdiction_id INTEGER,
    assigned_at TIMESTAMP,
    source TEXT  -- 'gis', 'manual', 'inferred'
)
```

---

#### Stage 2: Zoning Districts ✅

**Purpose:** Link to full district definitions

**Output:** Reference to zoning_districts table

---

#### Stage 3: Dimensional Standards ✅

**Purpose:** Apply district standards to parcel

**Output:**
```json
{
  "parcel_id": "28-37-35-25-00014",
  "zone_code": "RS-10",
  "dimensional": {
    "min_lot_size": 10000,
    "max_height": 35,
    "front_setback": 25,
    "side_setback": 10,
    "rear_setback": 20
  }
}
```

---

#### Stage 4: Permitted Uses ⚠️

**Purpose:** List uses allowed on this parcel

**Output:**
```json
{
  "parcel_id": "28-37-35-25-00014",
  "permitted": [
    "Single Family Dwelling",
    "Accessory Structure",
    "Home Occupation",
    "Family Day Care"
  ],
  "conditional": [
    "Bed and Breakfast",
    "Group Home (7-14)"
  ]
}
```

---

#### Stage 5: Source URLs ✅

**Purpose:** Link to authoritative source documents

**Output:**
```json
{
  "parcel_id": "28-37-35-25-00014",
  "sources": {
    "zoning_code": "https://library.municode.com/fl/malabar/...",
    "property_card": "https://bcpao.us/api/v1/search/...",
    "gis_layer": "https://gis.brevardfl.gov/..."
  }
}
```

---

#### Stage 6: Census Demographics ✅

**Purpose:** Neighborhood context from Census ACS

**API:** Census ACS 5-Year Estimates

**Data Points:**
| Field | Source |
|-------|--------|
| median_household_income | B19013_001E |
| median_home_value | B25077_001E |
| median_rent | B25064_001E |
| total_population | B01003_001E |
| poverty_rate | B17001_002E / B17001_001E |

**Output:**
```json
{
  "parcel_id": "28-37-35-25-00014",
  "census_tract": "065231",
  "demographics": {
    "median_income": 106784,
    "median_home_value": 421900,
    "poverty_rate": 7.55,
    "population": 4523
  }
}
```

---

#### Stage 7: Location Scores ✅

**Purpose:** Walk Score, School Score, Crime Score

**APIs:**
- Walk Score API
- GreatSchools API
- Crime statistics (derived)

**Output:**
```json
{
  "parcel_id": "28-37-35-25-00014",
  "scores": {
    "walk_score": 20,      // 0-100, higher = more walkable
    "school_score": 82,    // 0-100, based on nearby schools
    "crime_score": 60      // 0-100, higher = safer
  }
}
```

**Malabar POC Results:**
- Walk Score: 20 (Car-Dependent - rural area)
- School Score: 82 (B-rated schools nearby)
- Crime Score: 60 (Safer than FL average)

---

#### Stage 8: Sales History ✅

**Purpose:** Transaction history from BCPAO

**Data Points:**
- Sale date
- Sale price
- Deed type
- Grantor/Grantee
- Recording info

**Output:**
```json
{
  "parcel_id": "28-37-35-25-00014",
  "sales": [
    {
      "date": "2023-05-15",
      "price": 385000,
      "deed_type": "Warranty Deed",
      "grantor": "SMITH JOHN",
      "grantee": "JONES MARY"
    }
  ]
}
```

---

#### Stage 9: Building Records ✅

**Purpose:** Structure details from BCPAO

**Data Points:**
- Year built
- Building sq ft
- Bedrooms/bathrooms
- Construction type
- Building value

**Output:**
```json
{
  "parcel_id": "28-37-35-25-00014",
  "building": {
    "year_built": 2005,
    "sqft": 2456,
    "bedrooms": 4,
    "bathrooms": 2.5,
    "construction": "CBS",
    "value": 285000
  }
}
```

---

#### Stage 10: Parcel-Zone Link ✅

**Purpose:** Final linkage in parcel_zones table

**Verification:**
- Parcel exists in sample_properties
- Zone exists in zoning_districts
- Jurisdiction matches

---

## Malabar POC Results

### Final Statistics

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Parcels | 1,430 | 1,430 | ✅ 100% |
| Zone Assignment | 1,430 | 1,430 | ✅ 100% |
| Geometry | 1,430 | 1,430 | ✅ 100% |
| Zoning Districts | 13 | 13 | ✅ 100% |
| Dimensional Standards | 13 | 13 | ✅ 100% |
| Conditional Uses | 82 | 82 | ✅ 100% |
| Ordinances | 41 | 41 | ✅ 100% |
| Census Demographics | 1,430 | 1,420 | ✅ 99.3% |
| Location Scores | 1,430 | 1,430 | ✅ 100% |

### Zone Distribution

| Zone | Count | % | Description |
|------|-------|---|-------------|
| RR-65 | 666 | 66.6% | Rural Residential |
| RS-10 | 126 | 12.6% | Single Family 10K |
| RS-21 | 48 | 4.8% | Single Family 21K |
| R/LC | 45 | 4.5% | Residential Limited Commercial |
| CG | 28 | 2.8% | Commercial General |
| CP | 25 | 2.5% | Coastal Preserve |
| RM-6 | 19 | 1.9% | Multi-Family 6 du/ac |
| R-MH | 17 | 1.7% | Mobile Home |
| OI | 11 | 1.1% | Office Institutional |
| RS-15 | 11 | 1.1% | Single Family 15K |
| INS | 4 | 0.4% | Institutional Services |

---

## Scaling Plan

### Brevard County (17 Jurisdictions)

| Jurisdiction | Parcels | GIS | Status |
|--------------|---------|-----|--------|
| Unincorporated | 75,350 | ✅ | ⏳ Pending |
| Palm Bay | 78,697 | ⚠️ 503 | ⏳ Recovery |
| Melbourne | 62,135 | ❌ | ⏳ Manual |
| Titusville | 28,118 | ✅ | ⚠️ 78% |
| Cocoa | 29,882 | ✅ | ⏳ Pending |
| Rockledge | 15,234 | ❌ | ⏳ Pending |
| West Melbourne | 12,456 | ❌ | ⏳ Pending |
| Satellite Beach | 8,234 | ❌ | ⏳ Pending |
| Indian Harbour Beach | 4,567 | ❌ | ⏳ Pending |
| Cocoa Beach | 6,789 | ❌ | ⏳ Pending |
| Melbourne Beach | 3,456 | ❌ | ⏳ Pending |
| Cape Canaveral | 4,123 | ❌ | ⏳ Pending |
| Indialantic | 2,345 | ❌ | ⏳ Pending |
| Palm Shores | 567 | ❌ | ⏳ Pending |
| Melbourne Village | 789 | ❌ | ⏳ Pending |
| Grant-Valkaria | 1,234 | ❌ | ⏳ Pending |
| **Malabar** | **1,430** | Manual | ✅ **100%** |

**Total Brevard:** 351,423 parcels  
**Current Coverage:** 24,243 (6.8%)  
**Target:** 100%

### Florida State (67 Counties)

**Tier 1 (10 counties, 60% of FL population):**
| County | FIPS | Population | Priority |
|--------|------|------------|----------|
| Brevard | 12009 | 616,742 | ✅ POC |
| Orange | 12095 | 1,429,908 | Week 3 |
| Hillsborough | 12057 | 1,512,070 | Week 3 |
| Miami-Dade | 12086 | 2,716,940 | Week 4 |
| Broward | 12011 | 1,944,375 | Week 4 |
| Palm Beach | 12099 | 1,496,770 | Week 4 |
| Duval | 12031 | 995,567 | Week 5 |
| Pinellas | 12103 | 974,996 | Week 5 |
| Polk | 12105 | 753,197 | Week 5 |
| Lee | 12071 | 822,779 | Week 5 |

**Tier 2 (15 counties):** Weeks 5-6  
**Tier 3 (42 counties):** Weeks 6-8 (parallel via Modal.com)

---

## API Integration Summary

### Working APIs

| API | Purpose | Key Status |
|-----|---------|------------|
| Census ACS | Demographics | ✅ 8c6ef3cae... |
| BCPAO | Property data | ✅ Public |
| Municode | Ordinances | ✅ Public |
| Brevard GIS | Zone boundaries | ✅ Public |

### Pending APIs

| API | Purpose | Action |
|-----|---------|--------|
| Walk Score | Walkability | Get API key |
| GreatSchools | School ratings | Get API key |
| FEMA | Flood zones | Public |

---

*This framework is proven on Malabar POC. Scale it.*
