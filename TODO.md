# ZoneWise TODO - Sprint 1 Progress Tracker

> Last updated: 2026-02-06 by Claude Opus 4.6
> Sprint: Week 1-3 Foundation + Automation + Brevard Complete

---

## Day 1-2: Foundation Setup (2026-02-06)

- [x] Create `migrations/005_zone_standards.sql` - Zone standards table with constraints, indexes, RLS
- [x] Create `migrations/006_permitted_uses.sql` - Permitted uses + permission_types + use_categories tables
- [x] Create GitHub Actions workflow to deploy migrations (`deploy-zone-migrations.yml`)
- [x] Configure AgentQL Pro API key (`config/agentql.env`)
- [x] Test Brevard County pilot scrape (Melbourne, jurisdiction_id=1)
  - AgentQL + Playwright: 216KB content, 53 Municode links found
  - 28 Melbourne districts confirmed in database
  - 690 Melbourne ordinances already exist
- [x] Validate Opus 4.6 adaptive thinking + streaming patterns (4/4 tests passed)
  - Basic completion: 5.36s
  - Streaming: 12.58s (2.01s to first chunk)
  - Extended thinking: 59.25s (937 chars thinking)
  - Structured extraction: 4.01s (valid JSON, 4 permitted + 4 conditional uses)
- [x] Create TODO.md tracking all tasks
- [ ] Push changes and trigger migration deployment via GitHub Actions
- [ ] Verify zone_standards and permitted_uses tables created in Supabase

## Day 3-4: Automation Infrastructure

- [ ] Set up Modal.com parallel scraper (`src/scrapers/modal_scraper.py`)
- [ ] Build template detector for ordinance classification
- [ ] Set up Claude Batch Processor for overnight extraction
- [ ] Create validation pipeline (GitHub Actions daily check)

## Day 5: Ground Truth Dataset

- [ ] Manually verify 50 Brevard districts as validation baseline
- [ ] Create ground truth JSON for automated testing

## Week 2: Brevard Phase 4 (Permitted Uses)

- [ ] Define structured output schema (Pydantic models)
- [ ] Extract permitted uses for 5 pilot jurisdictions
- [ ] QA batch results and iterate on extraction prompts
- [ ] Scale to all 17 Brevard jurisdictions
- [ ] Target: 273 districts x 50+ uses each

## Week 2: Brevard Phases 7-8

- [ ] Map overlay districts for all Brevard jurisdictions
- [ ] Extract development bonuses (Palm Bay Table 173-8 + others)
- [ ] Verify Palm Bay's 9 known bonuses are preserved

## Week 3: Orange County Pilot

- [ ] Base zoning districts for Orange County
- [ ] Dimensional standards for ~50 Orange districts
- [ ] Compare Orange vs Brevard extraction accuracy

---

## Database State (as of 2026-02-06)

| Table | Rows | Status |
|-------|------|--------|
| jurisdictions | 369 | Active |
| zoning_districts | 351 | Active (28 Melbourne) |
| ordinances | 2,190 | Active (690 Melbourne) |
| dimensional_standards | 13 | Needs population |
| allowed_uses | 0 | Empty - ready for Phase 4 |
| development_bonuses | exists | Ready for Phase 8 |
| overlay_districts | exists | Ready for Phase 7 |
| conditional_uses | exists | Ready |
| zone_standards | PENDING | Migration created, awaiting deployment |
| permitted_uses | PENDING | Migration created, awaiting deployment |

## Key Findings

- AgentQL Pro + Playwright renders Municode JS content successfully (216KB vs 4KB without JS)
- Valid `allowed_uses.use_type` values: `by-right`, `conditional`, `prohibited`
- Claude Sonnet 4.5 extended thinking works for complex zoning analysis
- Streaming delivers first chunk in ~2s for real-time UX
- Structured extraction reliably produces valid JSON from ordinance text

## Blockers

- Direct SQL execution requires database password (not available locally)
- Migration deployment depends on GitHub Actions with `SUPABASE_DB_PASSWORD` secret
- `gh` CLI not installable on this machine (Chocolatey access denied)
