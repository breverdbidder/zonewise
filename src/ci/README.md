# ZoneWise.AI Competitive Intelligence V3

## Battle Plan Generator — Codified from Claude's PropZone Workflow

### What This Is

This module codifies the **exact workflow** Claude used to create the Gridics/PropZone competitive battle plan on Feb 5, 2026. Instead of manually running web searches, fetching pages, and searching past chats, this pipeline automates all 10 steps.

### Architecture

```
CI V2 (existing — 5 parts):
├── Part 1: Surface Intelligence (website clone, tech detection)
├── Part 2: Product Requirements Document (PRD)
├── Part 3: Technical Specifications (PRS)
├── Part 4: Strategic Analysis (SWOT, positioning)
└── Part 5: Traffic & Market Intelligence

CI V3 (new — 2 additional parts):
├── Part 6: Battle Plan Generation
│   ├── Step 1: DISCOVER — Fetch competitor pages
│   ├── Step 2: PRICING — Extract API pricing / plans
│   ├── Step 3: FEATURES — Extract product features & data points
│   ├── Step 4: CONTEXT — Load our 63 KPIs + 20 Phases + Supabase status
│   ├── Step 5: COMPARE — Map competitor features to our framework
│   ├── Step 6: COST — Calculate cost-optimized acquisition strategy
│   ├── Step 7: GAPS — Identify win/match/lose positions
│   ├── Step 8: PLAN — Generate execution timeline with budget
│   ├── Step 9: RENDER — Output as JSON for React battle card
│   └── Step 10: STORE — Persist to Supabase
└── Part 7: React Battle Card Rendering (interactive dashboard)
```

### Files

| File | Description |
|------|-------------|
| `battle_plan_generator.py` | Core 10-step pipeline (orchestrator, models, engines) |
| `ci_v3_workflow.py` | Full CI V3 workflow integrating V2 parts + battle plan |
| `README.md` | This file |

### Usage

```bash
# CLI
python ci_v3_workflow.py \
  --name "Gridics/PropZone" \
  --url "https://propzone.gridics.com" \
  --extra-urls "https://developer.gridics.com/plans" "https://gridics.com/real-estate-solutions/" \
  --store \
  -v

# Python
from ci_v3_workflow import CIV3Workflow

workflow = CIV3Workflow()
results = await workflow.execute(
    competitor_name="Gridics/PropZone",
    competitor_url="https://propzone.gridics.com",
    extra_urls=["https://developer.gridics.com/plans"],
)

plan = results["battle_plan"]
print(f"KPIs: {plan.kpis_we_win} win / {plan.kpis_we_match} match")
```

### Data Models

- **BattlePlan** — Complete output with all 5 sections
- **CompetitorFeature** — Single feature with confidence level
- **KPIMapping** — Maps competitor feature to our 63 KPIs
- **DataSource** — Cost-optimized data acquisition source
- **PhaseStatus** — Status of our 20 phases vs competitor
- **ExecutionWeek** — Week-by-week implementation plan

### Confidence Levels

| Level | Meaning |
|-------|---------|
| CONFIRMED | Directly observed on competitor site |
| INFERRED | Logical deduction from confirmed data |
| UNVERIFIED | Industry hypothesis requiring validation |

### Known Limitation

Gridics blocks automated scrapers (Cloudflare 403). The pipeline works best when:
1. **Initial recon** is done via Claude's web_search (gets past Cloudflare)
2. **Structured analysis** runs through this pipeline using cached page data
3. **Anti-detection scraping** uses AgentQL for subsequent deep scrapes

### Supabase Tables

- `competitor_clones` — Master record per competitor analysis
- `competitor_analyses` — Individual part results (7 parts)
- `feature_comparisons` — KPI-level comparison data

### Integration Points

- **GitHub**: `breverdbidder/zonewise` → `src/ci/`
- **Supabase**: `mocerqjnksmhcjzxrewo` → `competitor_*` tables
- **CI V2**: Existing prompts in `docs/competitive-intelligence/prompts/`
- **Reports**: `src/reports/zonewise_63kpi_report_generator.js`

### Version History

- **v3.0.0** (2026-02-05): Codified from Claude's PropZone battle plan workflow
- **v2.2.0** (2026-01-19): Added Gridics data source methodology
- **v2.1.0** (2026-01-12): Initial CI V2 with 5-part analysis

---
*ZoneWise.AI — USA Real Estate Decoded!*
