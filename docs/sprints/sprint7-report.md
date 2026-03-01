# Sprint 7 Report — Auction Dashboard Integration

**Date:** 2026-03-01
**Duration:** 1 day (continuation sprint)
**Repos touched:** brevard-bidder-scraper, zonewise-web

## Objectives
Close integration gap between enrichment pipeline and product UI.

## Delivered

### brevard-bidder-scraper (aada72e)
- Task 1: 21/21 address gaps patched — 5 addresses, 11 vacant land flags, 4 unresolvable tags
- Task 2: 8 FastAPI auction endpoints (standalone/CLI use, not deployed to Render)
- Files: src/api/main.py (+480 -103), src/enrichment/sprint7_data_patch.py (+298 new)

### zonewise-web (ddf93de + 3def268)
- Task 3: 3 Next.js API routes — /api/auctions, /summary, /[id]
- Task 4: Auction dashboard page — table, map, filters, summary cards, TopNav
- Task 5A: Removed auth guard (was blocking all visitors with redirect to nonexistent /login)
- Task 5B: Mapbox token configured in Vercel env vars
- Files: 13 files (+887 lines) + auth fix

### Architecture Decisions
- Next.js API routes are the primary data path for the dashboard (query Supabase directly)
- FastAPI endpoints in brevard-bidder-scraper remain for CLI/script use
- Render (zonewise-agents) unchanged — serves zoning chat, not auction data

## Data State
- 303 auctions across 9 counties
- 283 with addresses, 11 vacant land, 4 condos
- Brevard: 182, Broward: 24, Miami-Dade: 21, Lee: 20, Palm Beach: 15
- Hillsborough: 13, Polk: 13, Pinellas: 8, Duval: 7

## Known Issues
- 6 counties have corrupted fl_parcels data from ZoneWise import — affects enrichment match rates
- 20 remaining address gaps are genuinely unresolvable (vacant land, unknown heirs)

## Commits
| SHA | Repo | Description |
|-----|------|-------------|
| aada72e | brevard-bidder-scraper | Data patch + 8 API endpoints |
| ddf93de | zonewise-web | Dashboard, API routes, TopNav |
| 3def268 | zonewise-web | Auth guard removal fix |
| 7f344bc | brevard-bidder-scraper | Architecture decision docs |
