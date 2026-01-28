# ZoneWise Modal Pipeline

**Autonomous parallel scraping and enrichment for 67 FL counties**

[![Deploy to Modal](https://github.com/breverdbidder/zonewise/actions/workflows/modal-deploy.yml/badge.svg)](https://github.com/breverdbidder/zonewise/actions)

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ZONEWISE MODAL PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐               │
│  │  Claude AI    │───▶│  Claude Code  │───▶│    GitHub     │               │
│  │  (Architect)  │    │  (7hr agentic)│    │    Actions    │               │
│  └───────────────┘    └───────────────┘    └───────┬───────┘               │
│                                                     │                       │
│                                                     ▼                       │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                      MODAL.COM (Serverless)                       │      │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │      │
│  │  │ Phase 2-8    │  │ Stage 1-10   │  │ Census API   │           │      │
│  │  │ Scrapers     │  │ Processors   │  │ Integration  │           │      │
│  │  │  .map()      │  │  .map()      │  │              │           │      │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │      │
│  │         │                 │                  │                   │      │
│  │         └─────────────────┼──────────────────┘                   │      │
│  │                           ▼                                       │      │
│  │  ┌──────────────────────────────────────────────────────────┐   │      │
│  │  │              SUPABASE (PostgreSQL)                        │   │      │
│  │  │  • zoning_districts (273+)                               │   │      │
│  │  │  • parcel_zones (261K+)                                  │   │      │
│  │  │  • census_demographics                                    │   │      │
│  │  │  • location_scores                                        │   │      │
│  │  └──────────────────────────────────────────────────────────┘   │      │
│  └──────────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/breverdbidder/zonewise.git
cd zonewise

# 2. Install Modal CLI
pip install modal

# 3. Create Modal secrets
modal secret create zonewise-secrets \
  SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co \
  SUPABASE_KEY=eyJ... \
  CENSUS_API_KEY=8c6ef3cae05fd24b03c4e541d9eb11c2ba9c6589 \
  WALKSCORE_API_KEY=xxx \
  FIRECRAWL_API_KEY=fc-fa112951a2564765a2d146302774ac9b

# 4. Deploy to Modal
modal deploy src/app.py

# 5. Run nightly pipeline manually
modal run src/app.py

# 6. Run full county pipeline
modal run src/app.py --county brevard --full
```

## 20 ZoneWise Data Phases

| Phase | Category | Description | Status |
|-------|----------|-------------|--------|
| **FOUNDATION (1-5)** |||
| 1 | Property Identification | Parcel ID, Address, Owner | ✅ BCPAO |
| 2 | Base Zoning | Zone Code, Name, Category | ✅ Municode |
| 3 | Dimensional Standards | Setbacks, Height, FAR | ✅ Municode |
| 4 | Permitted Uses | By-right uses per district | 🔄 In Progress |
| 5 | Conditional Uses | CUP requirements | 🔄 In Progress |
| **ADVANCED (6-10)** |||
| 6 | Prohibited Uses | Not allowed uses | ⏳ Planned |
| 7 | Overlay Districts | Historic, Flood, Airport | 🔄 In Progress |
| 8 | Development Bonuses | Density/height bonuses ⭐ | 🔄 In Progress |
| 9 | Parking Requirements | Per-use parking | ⏳ Planned |
| 10 | Density/Intensity | Units/acre, FAR | ⏳ Planned |
| **SPECIALTY (11-15)** |||
| 11 | Short-Term Rentals | STR regulations | ⏳ Planned |
| 12 | ADU Regulations | ADU rules per district | ⏳ Planned |
| 13 | Historic/Design | Design standards | ❌ Skip |
| 14 | FLUM Designations | Future Land Use Map | ⏳ Planned |
| 15 | Entitlement Timelines | Processing times ⭐ | ✅ Complete |
| **INFRASTRUCTURE (16-20)** |||
| 16 | Ordinance Library | Full ordinance text | 🔄 In Progress |
| 17 | Ordinance Changes | Amendment tracking ⭐ | ⏳ Planned |
| 18 | Parcel Data | County appraiser APIs | ✅ BCPAO |
| 19 | Environmental Overlays | Flood zones, wetlands | ⏳ Planned |
| 20 | Census Demographics | Population, income | ✅ Census API |

⭐ = Competitive Advantage (neither Gridics nor Zoneomics has)

## 10-Stage Data Framework (Malabar POC)

| Stage | Component | Malabar | Titusville |
|-------|-----------|---------|------------|
| 1 | Zone Assignment | ✅ 100% | ✅ 78.2% |
| 2 | Zoning Districts | ✅ 13 | ✅ 40 |
| 3 | Dimensional Standards | ✅ Complete | ✅ 75% |
| 4 | Permitted Uses | ✅ Loaded | ⏳ Pending |
| 5 | Source URLs | ✅ Linked | ✅ 75% |
| 6 | Census Demographics | ✅ Integrated | ⚠️ Key expired |
| 7 | Location Scores | ✅ Walk/School/Crime | ⏳ Pending |
| 8 | Sales History | ✅ BCPAO | ⚠️ 0.1% |
| 9 | Building Records | ✅ BCPAO | ⚠️ 0.2% |
| 10 | Parcel-Zone Link | ✅ Complete | ✅ Complete |

## GIS API Catalog

### Brevard County Coverage

| Status | Parcels | % | Jurisdictions |
|--------|---------|---|---------------|
| ✅ WORKING | 133,350 | 51% | Unincorporated, Cocoa, Titusville |
| ⚠️ OUTAGE | 78,697 | 30% | Palm Bay (temporary 503) |
| 📋 MANUAL | 2,249 | 1% | Malabar (POC complete) |
| ❌ NO_ENDPOINT | 46,956 | 18% | Melbourne, smaller municipalities |

### Verified GIS Endpoints

```python
# Unincorporated Brevard (75,350 parcels)
url = "https://gis.brevardfl.gov/gissrv/rest/services/Planning_Development/Zoning_WKID2881/MapServer/0"
zone_field = "ZONING"

# Cocoa (29,882 parcels)
url = "https://services1.arcgis.com/Tex1uhbqnOZPx6qT/arcgis/rest/services/Public_View_Cocoa_Zoning_with_Split_Lots_June_2023_view/FeatureServer/1"
zone_field = "Zoning"

# Titusville (28,118 parcels)
url = "https://gis.titusville.com/arcgis/rest/services/CommunityDevelopment/MapServer/15"
zone_field = "Zone_Code"

# Palm Bay (78,697 parcels) - TEMPORARY OUTAGE
url = "https://gis.palmbayflorida.org/arcgis/rest/services/GrowthManagement/Zoning/MapServer/0"
zone_field = "ZONING"
```

### BCPAO Property Appraiser API

```python
# Search by parcel
GET https://www.bcpao.us/api/v1/search?parcel={parcel_id}

# Search by account
GET https://www.bcpao.us/api/v1/account/{account}

# GIS Layer (parcels with values)
GET https://gis.brevardfl.gov/gissrv/rest/services/Base_Map/Parcel_New_WKID2881/MapServer/5/query

# Photo URL pattern
https://www.bcpao.us/photos/{prefix}/{account}011.jpg
```

## Location Intelligence APIs

| API | Cost | Rate Limit | Use Case |
|-----|------|------------|----------|
| Walk Score | FREE | 5,000/day | Walkability scores |
| NCES Schools | FREE | Unlimited | School locations/data |
| Florida DOE | FREE | N/A | School grades (A-F) |
| FBI CDE | FREE | Unlimited | County crime data |
| FDLE | FREE | N/A | FL county crime |
| Census API | FREE | 500/day | Demographics |

### GitHub Repos Integrated

| Repo | Stars | Use Case |
|------|-------|----------|
| gboeing/osmnx | 5.4K | Walkability alternative |
| UDST/pandana | 400 | Accessibility metrics |
| fbi-cde/crime-data-api | ~100 | Crime data |

## Cost Analysis

### Modal Compute

| Resource | Free Tier | Usage |
|----------|-----------|-------|
| CPU | $30 credit | ~$0.0001/sec |
| Memory | Included | 256MB-32GB |
| Concurrent | 1000+ | No limit |

**Estimated Monthly Cost:** $0-10 for 67 counties

### API Costs

| Service | Cost | Monthly Estimate |
|---------|------|------------------|
| Supabase | FREE | $0 (within limits) |
| Census API | FREE | $0 |
| Walk Score | FREE | $0 (5K/day) |
| Firecrawl | $20/mo | Optional |

**Total: $0-30/month**

## Project Structure

```
zonewise-modal/
├── README.md
├── requirements.txt
├── .github/
│   └── workflows/
│       └── modal-deploy.yml     # CI/CD to Modal
├── config/
│   └── gis_endpoints.json       # Verified GIS catalog
├── src/
│   ├── __init__.py
│   ├── app.py                   # Main Modal app (20 phases + 10 stages)
│   ├── gis_catalog.py           # GIS endpoint configurations
│   ├── scrapers/
│   │   ├── municode.py          # Municode scraper
│   │   └── bcpao.py             # BCPAO property scraper
│   ├── enrichment/
│   │   └── location.py          # Location intelligence
│   └── apis/
│       ├── census.py            # Census API client
│       ├── walkscore.py         # Walk Score API
│       └── schools.py           # NCES/FL DOE schools
├── docs/
│   └── supabase_schema.sql      # Complete database schema
└── tests/
    └── test_gis.py
```

## Deployment

### GitHub Actions (Automatic)

Push to `main` → Automatic deployment to Modal

```yaml
# .github/workflows/modal-deploy.yml
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 4 * * *'  # 11 PM EST daily
```

### Manual Deployment

```bash
# Deploy app
modal deploy src/app.py

# Run nightly pipeline
modal run src/app.py

# Run specific county
modal run src/app.py --county brevard --full

# Run specific phase
modal run src/app.py --county brevard --phase 2
```

## Supabase Tables

See `docs/supabase_schema.sql` for complete schema.

### Core Tables

- `jurisdictions` - 17 Brevard, 1,100+ statewide
- `zoning_districts` - 273+ districts with DIMS
- `parcel_zones` - Parcel-to-zone assignments
- `dimensional_standards` - Setbacks, heights, density
- `permitted_uses` - Use matrix per district

### Location Intelligence

- `census_demographics` - ACS 5-year data by tract
- `location_scores` - Walk/School/Crime scores
- `sales_history` - Property transactions
- `building_details` - Building characteristics

## Roadmap

### Q1 2026

- [ ] Complete Brevard POC (17 jurisdictions)
- [ ] Expand to 8 Tier 1 FL counties
- [ ] Launch ZoneWise.ai MVP

### Q2 2026

- [ ] 67 FL counties coverage
- [ ] 1,000+ auctions/day processing
- [ ] MCP server for Claude integration

## Team

- **ZoneWise.AI** - Product Owner (20 min/day oversight)
- **Claude Opus 4.5** - AI Architect
- **Claude Code** - Agentic Engineer (7hr sessions)

---

Built by [ZoneWise.AI 2026](https://github.com/breverdbidder) | [ZoneWise.ai](https://zonewise.ai)
