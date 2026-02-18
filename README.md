# ZoneWise.AI — Monorepo 🏛️

**AI-powered zoning intelligence for all 67 Florida counties.**

[![CI](https://github.com/breverdbidder/zonewise/actions/workflows/test.yml/badge.svg)](https://github.com/breverdbidder/zonewise/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](./CHANGELOG.md)

> Query zoning regulations, setbacks, permitted uses, and dimensional standards for any Florida parcel using AI-powered natural language.

**Production:** [zonewise.ai](https://zonewise.ai)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ZoneWise.AI System                           │
│                                                                       │
│  zonewise-web          zonewise-modal         zonewise-desktop        │
│  (Next.js UI)          (67-county scraper)    (CraftAgents fork)     │
│       │                      │                       │               │
│       └──────────────────────┼───────────────────────┘               │
│                              ▼                                        │
│                    ┌─────────────────┐                                │
│                    │    Supabase     │  ← Single source of truth      │
│                    │  PostgreSQL     │                                 │
│                    │  10.8M parcels  │                                 │
│                    │  5,321 districts│                                 │
│                    │  67 counties    │                                 │
│                    └─────────────────┘                                │
│                              │                                        │
│                    ┌─────────▼─────────┐                              │
│                    │  FastAPI Backend  │  ← zonewise-agents            │
│                    │  (Render.com)     │    NLP + Claude API           │
│                    └───────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

## Repos

| Repo | Purpose | Deploys To | Status |
|------|---------|------------|--------|
| **[zonewise](https://github.com/breverdbidder/zonewise)** | Monorepo — scripts, migrations, pipeline, skills | Dev only | ✅ Active |
| **[zonewise-web](https://github.com/breverdbidder/zonewise-web)** | Marketing + product UI (Next.js 14) | Vercel → zonewise.ai | ✅ Active |
| **[zonewise-modal](https://github.com/breverdbidder/zonewise-modal)** | 67-county AgentQL scraper | Modal.com | ✅ Active |
| **[zonewise-desktop](https://github.com/breverdbidder/zonewise-desktop)** | CraftAgents fork + ZoneWise skills | Vercel → zonewise.app | ✅ Active |
| **[zonewise-agents](https://github.com/breverdbidder/zonewise-agents)** | FastAPI NLP backend | Render.com | ✅ Active |

## Data Moat

| Asset | Count |
|-------|-------|
| Florida Counties | 67 |
| Jurisdictions | ~1,100 |
| Zoning Districts | 5,321 |
| Parcels (FDOT) | 10.8M |
| GIS Polygons | 10,092 |

## Quick Start

```bash
git clone https://github.com/breverdbidder/zonewise.git
cd zonewise
pip install -r requirements.txt
cp .env.example .env  # add your API keys

# Run migrations
psql $DATABASE_URL < migrations/001_initial.sql

# Test single county scrape
python scripts/run_county.py --county brevard --dry-run
```

## Development

```bash
# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full workflow.

## Stack

| Layer | Technology |
|-------|------------|
| Scraper | AgentQL + Modal.com (serverless) |
| Database | Supabase (PostgreSQL, Auth, Realtime) |
| AI | Claude Sonnet 4.5 / Opus 4.6 |
| Frontend | Next.js 14, Tailwind CSS, Mapbox GL |
| Backend | FastAPI (Python 3.11) |
| Hosting | Vercel (web), Render (API), Modal (scraper) |
| Orchestration | LangGraph + GitHub Actions |

## License

MIT — see [LICENSE](./LICENSE)

---

**Data is the moat. ZoneWise is the truth.** 🏛️
