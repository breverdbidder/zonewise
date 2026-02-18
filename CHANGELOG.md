# Changelog

All notable changes to ZoneWise.AI monorepo are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### In Progress
- Phase 1 deep scraper (V4): Municode deep extraction targeting 237 jurisdictions
- Giant county adapters for Broward, Miami-Dade, Orange County
- Quality cleanup: fix 20.5% suspicious district codes

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
