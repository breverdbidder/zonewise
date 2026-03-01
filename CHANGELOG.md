# Changelog

All notable changes to ZoneWise.AI monorepo are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### In Progress
- Sprint 7: Full-stack integration (auction dashboard, API endpoints, desktop panel)
- Phase 1 deep scraper (V4): Municode deep extraction targeting 237 jurisdictions
- Giant county adapters for Broward, Miami-Dade, Orange County
- Quality cleanup: fix 20.5% suspicious district codes

---

## [0.3.0] — 2026-03-01

### Added (Sprint 7: Full-Stack Integration)
- Auction API: 8 endpoints in BidDeed.AI FastAPI service (health, list, detail, summary, map pins, county, trigger)
- Web API routes: `/api/auctions`, `/api/auctions/summary`, `/api/auctions/[id]` in zonewise-web
- Auction dashboard page with table/map toggle, filters, summary cards
- Top navigation bar for Dashboard/Auctions routing
- Desktop auction panel in zonewise-desktop viewer
- Data patch: 5 addresses filled, 11 vacant land flagged, 5 unresolvable tagged

### Data
- 287 total auction rows across 9 Florida counties
- Brevard enrichment: 94.5% with addresses, 100% with defendants
- 11 vacant land parcels identified and classified
- 4 condos flagged (3 Palm Beach, 1 Broward)

---

## [0.2.1] — 2026-02-28

### Added (Sprint 6.1: BECA Browser Automation)
- Firecrawl Actions browser automation for BECA case lookup
- 74/74 Brevard foreclosure cases enriched (100% success rate)
- 5-step action chain: disclaimer → General Public → Case Search → JS fill → submit
- Timeout fix: 60000ms for older cases (default caused 408)

### Data
- 182/182 Brevard defendants enriched (100%)
- 172/182 Brevard addresses enriched (94.5%)
- 10 rows without address: UNKNOWN HEIRS, estates, out-of-state defendants

---

## [0.2.0] — 2026-02-28

### Added (Sprint 6: Data Cleanup)
- `is_condo` column: 4 condos flagged (3 Palm Beach, 1 Broward)
- BCPAO GIS Reference Doc (`docs/BCPAO_GIS_REFERENCE.md`)
- Annotation system for unresolvable rows (74 Brevard rows annotated)

### Removed
- 8 Orange County legacy rows (backed up to insights)

### Data
- Row count: 287 (down from 295)
- 66 historical foreclosures annotated as HISTORICAL
- 8 active rows annotated as NOT ON CLERK PAGE

---

## [0.1.1] — 2026-02-28

### Added (Sprint 5: Enrichment Gap-Fill)
- BCPAO GIS TaxAcct integration for Brevard tax deed parcels
- Owner names, centroids, land values, lot sqft via GIS API
- 11/11 Brevard tax deed rows enriched
- Match rate: 82% (67/82 addressable auctions)

### Data
- Hillsborough 100%, Duval 100%, Pinellas 100%, Polk 100%
- Miami-Dade 94%, Palm Beach 92%, Lee 90%

---

## [0.1.0] — 2026-02-08

### Added
- 67-county AgentQL scraper via Modal.com (V3.1 full run complete)
- 5,321 zoning districts across Florida
- 1,179 dimensional standards
- 7,505 permitted uses
- Phase 6–20 extractors (dimensional standards + uses + parcels)
- GIS client for ArcGIS REST APIs
- Incremental update logic
- CI test suite with 85% coverage threshold
- Supabase integration (PostgreSQL + Auth + Realtime)
- LangGraph orchestration for multi-agent pipeline
- AGENTS.md — agent working protocol
- SECURITY.md — vulnerability reporting policy

### Infrastructure
- Modal.com serverless workers for parallel county scraping
- GitHub Actions: test, deploy, nightly scrape workflows
- Supabase `multi_county_auctions` table for cross-county data
- `master_index` table as single source of truth for repos/files/docs

### Data
- V3.1 67-county full run: 5,321 districts, 224/369 cities OK, $3.47 LLM cost, 29.9 min
- V2.1 free-tier run: 5,395 districts, 1,179 standards, 7,505 uses, 39/67 counties, $0.00 LLM cost
- Brevard County pilot: 28 Melbourne districts, 690 ordinances, 53 Municode links

---

[Unreleased]: https://github.com/breverdbidder/zonewise/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/breverdbidder/zonewise/releases/tag/v0.1.0
