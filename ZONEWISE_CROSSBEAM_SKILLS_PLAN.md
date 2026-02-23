# ZoneWise.AI — CrossBeam Skills Adoption Master Plan
## 67-County Florida Skill File Architecture

> **Status**: PLANNING → EXECUTION  
> **Created**: February 23, 2026  
> **Author**: Claude AI (Architect) + Ariel Shapira (Product Owner)  
> **Source**: CrossBeam `.claude/skills/` adapted for ZoneWise Supabase schema  

---

## Reality Snapshot (Verified from Supabase + GitHub)

| Asset | Current State | Target |
|-------|--------------|--------|
| Jurisdictions in DB | **1,100** (808+ verified) | 1,100 |
| Zoning districts | **5,321** | 8,000+ |
| Dimensional standards | **1,179** | 5,000+ |
| Permitted uses | **7,505** | 50,000+ |
| GIS polygons | **10,092** | 10,092 |
| FL parcels (FDOR) | **10.8M** | 10.8M |
| County skill files | **0** | **67** |
| CraftAgents skills | **12** (Brevard only) | **79** (12 + 67 county) |
| Skills manifest version | 1.1.0 | 2.0.0 |

---

## What We're Adapting from CrossBeam

CrossBeam built 28 skill reference files for California ADU permits (1 jurisdiction).  
We are building **67 county skill files** for Florida (1,100 jurisdictions).

### Direct Pattern Mapping

| CrossBeam (CA ADU) | ZoneWise (FL 67 Counties) |
|-------------------|--------------------------|
| `california-adu` skill (28 refs) | `county-{slug}` skill per county |
| City Research Skill — Mode 1: WebSearch | County Portal Discovery → portal URL validation |
| City Research Skill — Mode 2: WebFetch | Municode/county site extraction |
| City Research Skill — Mode 3: Browser Fallback | AgentQL semantic scrape (Modal container) |
| `adu-corrections-interpreter` workflow | `county-zoning-lookup` workflow |
| `city_discovery.json` output | `county_skill_data` → Supabase `jurisdictions` row |
| `city_research_findings.json` | `zone_standards` + `permitted_uses` rows |
| `extraction_gaps` → escalate | Circuit breaker → `insights` table → Traycer issue |

---

## Tool Chain Architecture

```
Ariel (20 min/day)
    │
    │ Strategic direction, cost approvals (>$10), schema changes
    ▼
Traycer.ai
    │ GitHub Issue → paste spec → apply 'traycer' label → auto-plan
    │ Creates GitHub Issues as task tracker
    ▼
Claude AI (Architect — this session)
    │ Designs skill file architecture, templates, data contracts
    │ Reviews Claude Code outputs via Greptile
    ▼
Claude Code (Agentic Engineer — 7hr sessions)
    │ Executes skill file generation, pushes to GitHub
    │ Writes scraper agents, wires Supabase inserts
    ▼
AgentQL (Scraping Engine)
    │ API Key: FCRgiir6... (GitHub Secrets: zonewise-modal)
    │ Semantic selectors for JS-heavy county portals
    ▼
Modal.com (Execution Layer)
    │ One container per county (67 parallel)
    │ Triggered by GitHub Actions nightly at 11 PM EST
    ▼
Supabase (Data Layer)
    │ mocerqjnksmhcjzxrewo.supabase.co
    │ Tables: jurisdictions, zoning_districts, zone_standards,
    │         permitted_uses, overlay_districts, fl_parcels
    ▼
Greptile (QA Gate)
    │ API Key: ukH9Hf1y... (VERIFIED Feb 9 2026)
    │ Indexed repos: zonewise-desktop, zonewise-web
    │ Code review on every PR before merge
    ▼
CraftAgents OSS Fork (zonewise-desktop)
    │ Skills deployed to: zonewise/skills/{county-slug}/
    │ Manifest: zonewise/skills/skills-manifest.yaml (v2.0.0)
    │ Progressive Disclosure: metadata → SKILL.md → references/
    ▼
Vercel (User-Facing)
    zonewise.ai (web) + zonewise.app (desktop viewer)
```

---

## Skill File Architecture

### Repository Placement

```
zonewise-desktop/
└── zonewise/
    └── skills/
        ├── skills-manifest.yaml          ← UPDATE to v2.0.0 (add 67 county entries)
        │
        ├── [EXISTING — 12 skills]
        │   ├── zoning-analysis/           ← EXTEND: currently Brevard only
        │   ├── bcpao-integration/         ← KEEP: Brevard-specific, untouched
        │   ├── property-valuation/
        │   ├── permit-lookup/
        │   └── ...
        │
        └── [NEW — 67 county skills]
            ├── county-alachua/
            │   ├── SKILL.md               ← Agent instructions
            │   └── references/
            │       ├── portal-urls.md     ← County portal endpoints
            │       ├── zoning-codes.md    ← All valid codes from DB
            │       └── quirks.md          ← Scraping gotchas
            ├── county-baker/
            ├── county-bay/
            ├── county-bradford/
            ├── county-brevard/            ← PRIORITY — most complete data
            ├── county-broward/
            ├── county-calhoun/
            ...
            └── county-washington/
```

### County Skill File Template (SKILL.md)

Each county skill file follows this exact structure:

```markdown
---
name: county-{slug}
description: >
  Zoning intelligence for {County Name} County, FL.
  {N} jurisdictions, {N} zoning districts in Supabase.
  Portal: {portal_type}. Use for parcel lookups, permitted use
  queries, dimensional standards. Triggers: any query mentioning
  {County Name}, county code {co_no}, or addresses in this county.
supabase_county_filter: "county=ilike.%25{County Name}%25"
co_no: {FDOR county number}
---

# {County Name} County — Zoning Intelligence

## Supabase Queries

### Find all jurisdictions in this county
GET /jurisdictions?county=ilike.%25{County Name}%25&select=id,name,data_completeness,municode_url

### Find zoning district by code
GET /zoning_districts?jurisdiction_id=eq.{id}&code=ilike.{code}

### Look up parcel
GET /fl_parcels?co_no=eq.{co_no}&parcel_id=eq.{parcel_id}&select=parcel_id,phy_addr1,phy_city,dor_uc,centroid_lat,centroid_lng

### Get dimensional standards
GET /zone_standards?zoning_district_id=eq.{id}

## 3-Mode Research Protocol (from CrossBeam)

### Mode 1 — Discovery (WebSearch, ~30s)
Trigger: portal_url unknown or stale (last_validated > 30 days)
Queries:
1. "{County Name} County Florida zoning map portal"
2. "{County Name} County Florida municode zoning ordinance"
3. "{County Name} County GIS ArcGIS zoning layer"
Output: Update portal_url in Supabase jurisdictions row

### Mode 2 — Extraction (WebFetch, ~60-90s)
Trigger: Mode 1 found portal URL
Target: Municode chapter for zoning districts + dimensional standards
Extract: zoning codes, permitted uses, setbacks, height limits
Output: INSERT/UPSERT to zoning_districts + zone_standards

### Mode 3 — AgentQL Fallback (Modal container)
Trigger: Mode 2 returns empty or portal requires JS rendering
Config: anti_scrape: {true|false}, rate_limit_rpm: {N}
Output: Same as Mode 2 via AgentQL semantic selectors

## County Data Profile

| Field | Value |
|-------|-------|
| FDOR co_no | {N} |
| Jurisdictions in DB | {N} |
| Zoning districts | {N} |
| Data completeness avg | {N}% |
| GIS polygons | {N} |
| Portal type | {municode|custom|arcgis|pdf} |
| Anti-scrape | {true|false} |
| Rate limit (rpm) | {N} |
| Test parcel | {parcel_id} |
| Last validated | {date} |

## Known Jurisdictions

| ID | Name | Completeness | Municode URL |
|----|------|-------------|-------------|
{rows from Supabase}

## Zoning Categories

{List of active zoning codes from zoning_districts table}

## Quirks & Gotchas

{Populated by Mode 1/2/3 during first scrape}

## Overlay Districts

{From overlay_districts table for this county}
```

---

## Traycer Protocol for This Work

All implementation tasks are created as GitHub Issues in `breverdbidder/zonewise` following:

```
GitHub Issue → paste spec → apply 'traycer' label → Submit
↓
Traycer auto-generates implementation plan as comments
↓
Claude Code executes against plan
↓
Greptile QA gate on PR
↓
Merge to main → auto-deploy
```

**Traycer Issues to Create:**

| Issue # | Title | Label | Scope |
|---------|-------|-------|-------|
| TBD | `[SKILL] County Skill Template + Generator Script` | traycer | Claude Code |
| TBD | `[SKILL] skills-manifest.yaml v2.0.0 with 67 county entries` | traycer | Claude Code |
| TBD | `[SKILL] Pilot: Brevard, Miami-Dade, Orange county skill files` | traycer | Claude Code |
| TBD | `[SCRAPER] Modal county agent reads skill file before scraping` | traycer | Claude Code |
| TBD | `[SCRAPER] 3-mode research flow per CrossBeam pattern` | traycer | Claude Code |
| TBD | `[SCRAPER] GitHub Action: nightly 67-county parallel Modal run` | traycer | Claude Code |
| TBD | `[DB] Supabase: add skill_file_path column to jurisdictions` | traycer | Claude Code |
| TBD | `[QA] Greptile: post-scrape validation against skill file` | traycer | Claude Code |

---

## Phase Plan with Checkpoints

---

### PHASE 0 — Foundation (Week of Feb 24)
**Goal**: Skill file template + generator + pilot 3 counties  
**Executor**: Claude Code (7hr session)  
**Repo**: `breverdbidder/zonewise-desktop` + `breverdbidder/zonewise`

#### TODO List

- [ ] **P0-001** Read CrossBeam `.claude/skills/adu-city-research/SKILL.md` (DONE — in context)
- [ ] **P0-002** Create `scripts/generate_county_skills.py` — reads Supabase, generates 67 SKILL.md files
- [ ] **P0-003** Generate pilot skill files: `county-brevard`, `county-miami-dade`, `county-orange`
- [ ] **P0-004** Add `skill_file_path` column to `jurisdictions` table (migration `007_skill_file_paths.sql`)
- [ ] **P0-005** Update `skills-manifest.yaml` → v2.0.0 with county skills category + 3 pilot entries
- [ ] **P0-006** Create Traycer GitHub Issues for all Phase 1 tasks
- [ ] **P0-007** Push to `breverdbidder/zonewise-desktop` branch `feat/county-skills`
- [ ] **P0-008** Greptile review: confirm no hardcoded keys, skill manifest valid YAML

**⛳ CHECKPOINT 0**: 3 pilot skill files live in zonewise-desktop, manifest updated, migration deployed  
**Verify**: `GET /jurisdictions?name=ilike.%25Brevard%25` returns row with `skill_file_path` populated  

---

### PHASE 1 — 3-Mode Research Flow (Week of Mar 2)
**Goal**: Port CrossBeam's city research skill as county research agent  
**Executor**: Claude Code  
**Repo**: `breverdbidder/zonewise` (monorepo agents/)

#### TODO List

- [ ] **P1-001** Create `agents/county_research_agent.py` (FastAPI endpoint + LangGraph workflow)
- [ ] **P1-002** Implement Mode 1 — Discovery (web_search → portal URL → UPDATE jurisdictions)
- [ ] **P1-003** Implement Mode 2 — Extraction (web_fetch → Municode parser → INSERT zone_standards)
- [ ] **P1-004** Implement Mode 3 — AgentQL fallback (Modal container spawn for anti_scrape counties)
- [ ] **P1-005** JSON handoff format between modes (mirrors CrossBeam `city_discovery.json` → `city_research_findings.json`)
- [ ] **P1-006** Circuit breaker: 3 failures → INSERT to `insights` table with `type='ESCALATE'`
- [ ] **P1-007** Wire skill file loader: agent reads `SKILL.md` from GitHub before executing any mode
- [ ] **P1-008** Unit tests: mock Municode responses for Brevard pilot
- [ ] **P1-009** Greptile QA: run post-implementation code review

**⛳ CHECKPOINT 1**: County research agent runs end-to-end for Brevard  
**Verify**: Agent reads `county-brevard/SKILL.md`, runs Mode 1→2, inserts ≥10 new zone_standards rows  

---

### PHASE 2 — Modal Parallel Execution (Week of Mar 9)
**Goal**: Nightly 67-county scrape via Modal containers  
**Executor**: Claude Code  
**Repo**: `breverdbidder/zonewise-modal`

#### TODO List

- [ ] **P2-001** Update `zonewise-modal` main script: load county skill file from GitHub at container start
- [ ] **P2-002** `county_config.json` — maps all 67 county slugs to `co_no`, skill file path, anti_scrape flag
- [ ] **P2-003** Modal `@app.function` per county with `rate_limit_rpm` from skill file
- [ ] **P2-004** GitHub Action: `.github/workflows/nightly-county-scrape.yml` — triggers 11 PM EST, spawns 67 Modal jobs
- [ ] **P2-005** Completion webhook: each job writes result to `daily_metrics` (county_id, records, errors, duration)
- [ ] **P2-006** AgentQL integration: Mode 3 fires automatically when `anti_scrape: true` in skill file
- [ ] **P2-007** Test with 3-county pilot (Brevard, Miami-Dade, Orange) before full 67
- [ ] **P2-008** Monitor: alert if any county `last_scraped > 26 hours`
- [ ] **P2-009** Traycer issue: create `[MONITOR] Nightly scrape health dashboard` for next sprint

**⛳ CHECKPOINT 2**: Nightly GitHub Action fires, all 3 pilot counties complete, daily_metrics populated  
**Verify**: GitHub Actions log shows 3/3 county jobs SUCCESS, Supabase `daily_metrics` has rows  

---

### PHASE 3 — All 67 County Skills (Mar 16 – Apr 6)
**Goal**: Complete skill files for all 67 FL counties  
**Executor**: Claude Code (batch generation via `generate_county_skills.py`)  
**Repo**: `breverdbidder/zonewise-desktop`

#### TODO List

- [ ] **P3-001** Run `generate_county_skills.py` — generates all 67 SKILL.md files from Supabase data
- [ ] **P3-002** Manual review pass: spot-check 10 county files for accuracy
- [ ] **P3-003** `skills-manifest.yaml` v2.0.0 final: all 67 county skills + updated categories
- [ ] **P3-004** Add county skills to CraftAgents Progressive Disclosure: level_1 metadata only (tokens: ~50 each)
- [ ] **P3-005** Greptile: validate all 67 SKILL.md files against template schema
- [ ] **P3-006** Wire `zonewise-intelligence` skill (existing) to use county skills as sub-skills
- [ ] **P3-007** Update `zoning-analysis` skill: extend from Brevard-only to all 67 counties via county skill lookup
- [ ] **P3-008** CraftAgents source `zonewise-supabase/config.json`: add `co_no` filter to `lookup_parcel` tool
- [ ] **P3-009** Enable Tool Search Beta: `header: advanced-tool-use-2025-11-20`, `defer_loading: true` for county tools
- [ ] **P3-010** Greptile indexed repos: add `zonewise` monorepo to Greptile index

**⛳ CHECKPOINT 3**: All 67 county SKILL.md files in zonewise-desktop, manifest v2.0.0 deployed  
**Verify**: `cat zonewise/skills/skills-manifest.yaml | grep "name: county-" | wc -l` = 67  

---

### PHASE 4 — Full Nightly Pipeline (Apr 7–21)
**Goal**: 67 counties live, nightly pipeline green, CraftAgents fully wired  
**Executor**: Claude Code  
**Repos**: All 5 active repos

#### TODO List

- [ ] **P4-001** Scale Modal to 67 parallel county jobs
- [ ] **P4-002** LiteLLM routing: DeepSeek V3.2 for Mode 1 (simple URL lookup), Sonnet 4.5 for Mode 2+3
- [ ] **P4-003** Supabase `insights` table: Traycer integration — ESCALATE rows auto-create GitHub Issues
- [ ] **P4-004** CraftAgents viewer: county selector dropdown → loads county skill metadata
- [ ] **P4-005** Mapbox layer: county boundary polygons from `fl_parcels` `co_no` field
- [ ] **P4-006** `zoning-analysis` skill updated: routes to county skill → Supabase → returns structured result
- [ ] **P4-007** Greptile: full QA sweep across all 5 repos pre-launch
- [ ] **P4-008** Validate: ≥95% of 67 counties complete nightly scrape

**⛳ CHECKPOINT 4**: Full nightly pipeline green for 7 consecutive nights  
**Verify**: `daily_metrics` table: 7 rows × 67 counties, all `status = 'SUCCESS'`  

---

### PHASE 5 — MVP Launch (May 2026)
**Goal**: Public launch, all acceptance criteria pass  
**Executor**: Ariel + Claude Code

#### TODO List

- [ ] **P5-001** Performance: p95 parcel lookup < 8s (load test 100 concurrent)
- [ ] **P5-002** Accuracy: spot-check 50 parcels across 10 counties vs ground truth
- [ ] **P5-003** Greptile final security audit: no exposed keys, all RLS active
- [ ] **P5-004** skills-manifest.yaml v2.0.0: `total_skills: 79` (12 existing + 67 county)
- [ ] **P5-005** Update README.md: 67 county coverage, CrossBeam attribution, architecture diagram
- [ ] **P5-006** Traycer retrospective issue: lessons learned, open items for Phase 3 expansion

**⛳ CHECKPOINT 5 (LAUNCH)**: All acceptance criteria pass, domain live, announce  
**Verify**: `zonewise.ai` loads < 2s, parcel query returns result with county skill attribution  

---

## 67 Florida County Registry

| # | County | FDOR co_no | Skill File | Jurisdictions in DB | Phase |
|---|--------|-----------|-----------|--------------------|----|
| 1 | Alachua | 01 | `county-alachua` | TBD | P3 |
| 2 | Baker | 02 | `county-baker` | TBD | P3 |
| 3 | Bay | 03 | `county-bay` | TBD | P3 |
| 4 | Bradford | 04 | `county-bradford` | TBD | P3 |
| 5 | **Brevard** | 05 | `county-brevard` | **17 (complete)** | **P0 PILOT** |
| 6 | Broward | 06 | `county-broward` | TBD | P3 |
| 7 | Calhoun | 07 | `county-calhoun` | TBD | P3 |
| 8 | Charlotte | 08 | `county-charlotte` | TBD | P3 |
| 9 | Citrus | 09 | `county-citrus` | TBD | P3 |
| 10 | Clay | 10 | `county-clay` | TBD | P3 |
| 11 | Collier | 11 | `county-collier` | TBD | P3 |
| 12 | Columbia | 12 | `county-columbia` | TBD | P3 |
| 13 | Miami-Dade | 13 | `county-miami-dade` | TBD | **P0 PILOT** |
| 14 | DeSoto | 14 | `county-desoto` | TBD | P3 |
| 15 | Dixie | 15 | `county-dixie` | TBD | P3 |
| 16 | Duval | 16 | `county-duval` | TBD | P3 |
| 17 | Escambia | 17 | `county-escambia` | TBD | P3 |
| 18 | Flagler | 18 | `county-flagler` | TBD | P3 |
| 19 | Franklin | 19 | `county-franklin` | TBD | P3 |
| 20 | Gadsden | 20 | `county-gadsden` | TBD | P3 |
| 21 | Gilchrist | 21 | `county-gilchrist` | TBD | P3 |
| 22 | Glades | 22 | `county-glades` | TBD | P3 |
| 23 | Gulf | 23 | `county-gulf` | TBD | P3 |
| 24 | Hamilton | 24 | `county-hamilton` | TBD | P3 |
| 25 | Hardee | 25 | `county-hardee` | TBD | P3 |
| 26 | Hendry | 26 | `county-hendry` | TBD | P3 |
| 27 | Hernando | 27 | `county-hernando` | TBD | P3 |
| 28 | Highlands | 28 | `county-highlands` | TBD | P3 |
| 29 | Hillsborough | 29 | `county-hillsborough` | TBD | P1 |
| 30 | Holmes | 30 | `county-holmes` | TBD | P3 |
| 31 | Indian River | 31 | `county-indian-river` | TBD | P3 |
| 32 | Jackson | 32 | `county-jackson` | TBD | P3 |
| 33 | Jefferson | 33 | `county-jefferson` | TBD | P3 |
| 34 | Lafayette | 34 | `county-lafayette` | TBD | P3 |
| 35 | Lake | 35 | `county-lake` | TBD | P3 |
| 36 | Lee | 36 | `county-lee` | TBD | P3 |
| 37 | Leon | 37 | `county-leon` | TBD | P3 |
| 38 | Levy | 38 | `county-levy` | TBD | P3 |
| 39 | Liberty | 39 | `county-liberty` | TBD | P3 |
| 40 | Madison | 40 | `county-madison` | TBD | P3 |
| 41 | Manatee | 41 | `county-manatee` | TBD | P3 |
| 42 | Marion | 42 | `county-marion` | TBD | P3 |
| 43 | Martin | 43 | `county-martin` | TBD | P3 |
| 44 | Monroe | 44 | `county-monroe` | TBD | P3 |
| 45 | Nassau | 45 | `county-nassau` | TBD | P3 |
| 46 | Okaloosa | 46 | `county-okaloosa` | TBD | P3 |
| 47 | Okeechobee | 47 | `county-okeechobee` | TBD | P3 |
| 48 | **Orange** | 48 | `county-orange` | TBD | **P0 PILOT** |
| 49 | Osceola | 49 | `county-osceola` | TBD | P3 |
| 50 | Palm Beach | 50 | `county-palm-beach` | TBD | P1 |
| 51 | Pasco | 51 | `county-pasco` | TBD | P3 |
| 52 | Pinellas | 52 | `county-pinellas` | TBD | P1 |
| 53 | Polk | 53 | `county-polk` | TBD | P3 |
| 54 | Putnam | 54 | `county-putnam` | TBD | P3 |
| 55 | St. Johns | 55 | `county-st-johns` | TBD | P3 |
| 56 | St. Lucie | 56 | `county-st-lucie` | TBD | P3 |
| 57 | Santa Rosa | 57 | `county-santa-rosa` | TBD | P3 |
| 58 | Sarasota | 58 | `county-sarasota` | TBD | P3 |
| 59 | Seminole | 59 | `county-seminole` | TBD | P3 |
| 60 | Sumter | 60 | `county-sumter` | TBD | P3 |
| 61 | Suwannee | 61 | `county-suwannee` | TBD | P3 |
| 62 | Taylor | 62 | `county-taylor` | TBD | P3 |
| 63 | Union | 63 | `county-union` | TBD | P3 |
| 64 | Volusia | 64 | `county-volusia` | TBD | P3 |
| 65 | Wakulla | 65 | `county-wakulla` | TBD | P3 |
| 66 | Walton | 66 | `county-walton` | TBD | P3 |
| 67 | Washington | 67 | `county-washington` | TBD | P3 |

**Priority order within Phase 1**: Hillsborough, Palm Beach, Pinellas (high volume, multiple jurisdictions)

---

## Escalation & Quality Gates

### Traycer Trigger Conditions
- County scraper fails 3+ consecutive nights → auto GitHub Issue
- Skill file `last_validated > 30 days` → Traycer issue `[SKILL] Revalidate {county}`
- New county portal detected (URL changed) → Traycer issue `[SKILL] Update {county} portal URL`

### Greptile QA Gates
Every PR must pass Greptile check before merge:
- No hardcoded API keys (AgentQL, Supabase, Anthropic)
- All Supabase queries use parameterized inputs
- Each new skill file validates against template schema
- Modal containers include error handling + circuit breaker

### Claude Code Session Protocol
Per `AGENTS.md` working rules:
1. Read `CLAUDE.md` before starting
2. Check `TODO.md` for current phase task
3. Update `PROJECT_STATE.json` after each milestone
4. Commit: `feat: add county-{slug} skill file`
5. Never push directly to `main` — branch + PR

---

## Next Immediate Action

**Right now**: Create Traycer GitHub Issue for P0-002 (generator script):

```
Title: [SKILL] County skill file generator from Supabase data
Body:
Generate scripts/generate_county_skills.py that:
1. Queries Supabase jurisdictions table (GROUP BY county)
2. For each of 67 counties, generates SKILL.md from template
3. Outputs to zonewise-desktop/zonewise/skills/county-{slug}/SKILL.md
4. Updates skills-manifest.yaml with all 67 entries
5. Writes skill_file_path back to Supabase jurisdictions rows

Schema refs: jurisdictions, zoning_districts, zone_standards, fl_parcels
Template: [link to this document]
Label: traycer
```

---

*Plan source: CrossBeam `.claude/skills/` + ZoneWise Supabase schema + CraftAgents OSS fork*  
*All data counts verified from `breverdbidder/zonewise` + `breverdbidder/zonewise-desktop` repos*
