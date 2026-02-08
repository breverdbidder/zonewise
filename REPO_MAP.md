---
name: "ZoneWise Repo Map"
description: "Single source of truth for all ZoneWise.AI repos, services, and deployments"
---

# ZoneWise.AI — Repo Map & System Architecture
**Last Updated**: 2026-02-08
**Owner**: Ariel Shapira

---

## THE PROBLEM (As of Feb 8, 2026)

9 repos. Conflicting descriptions. "DEPRECATED" services that are still running.
"ARCHIVED" repos that aren't actually archived. Skills duplicated across 3 repos.
No single document says what goes where.

**This document fixes that.**

---

## REPO REGISTRY

### ✅ ACTIVE REPOS (Use These)

| # | Repo | Purpose | Deploys To | Status |
|---|------|---------|------------|--------|
| 1 | **`zonewise`** | **MONOREPO** — Core codebase, Claude Code skills, agents, pipeline, MCP server, data, scripts, migrations | None (dev only) | ✅ ACTIVE — 571 files, CLAUDE.md, PROJECT_STATE.json |
| 2 | **`zonewise-web`** | **MARKETING SITE** — Next.js homepage at zonewise.ai | Vercel → zonewise.ai (5 projects!) | ✅ ACTIVE — Serves live site despite "ARCHIVED" description |
| 3 | **`zonewise-desktop`** | **DESKTOP APP** — CraftAgents OSS v0.4.0 fork with ZoneWise skills/sources | Vercel → zonewise.app | ✅ ACTIVE — Electron + skills + themes |
| 4 | **`zonewise-modal`** | **DATA PIPELINE** — 67-county AgentQL scraper | Modal.com (serverless) | ✅ ACTIVE — GitHub Issue #14, Feb 5-19 sprint |
| 5 | **`zonewise-agents`** | **NLP BACKEND** — FastAPI agent API on Render | Render → zonewise-agents.onrender.com | ⚠️ ACTIVE but description says "DEPRECATED" |

### 🗄️ REFERENCE REPOS (Read-Only / Docs)

| # | Repo | Purpose | Status |
|---|------|---------|--------|
| 6 | `zonewise-lobster` | Moltbot Lobster workflow experiment | 🧪 EXPERIMENT — Never replaced agents, description is wrong |
| 7 | `zonewise-rebrand-mission` | Claude Code mission doc for navy+orange rebrand | 📄 DOCS ONLY (30KB) |
| 8 | `zonewise-traycer-specs` | Traycer auto-plan specifications | 📄 DOCS ONLY (32KB) |

### ❌ DEAD REPOS (Archive or Delete)

| # | Repo | Why |
|---|------|-----|
| 9 | `zonewise-skills` | Already archived. Replaced by skills inside `zonewise-desktop` and `zonewise` |

---

## WHAT SERVES WHAT

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION SERVICES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  zonewise.ai (Marketing)          zonewise.app (Desktop)         │
│  ┌──────────────────────┐         ┌───────────────────────┐     │
│  │  Vercel               │         │  Vercel                │    │
│  │  Repo: zonewise-web   │         │  Repo: zonewise-desktop│    │
│  │  5 Vercel projects!   │         │  CraftAgents v0.4.0    │    │
│  │  (zonewise-moat,      │         │  Skills + Sources      │    │
│  │   zonewise-ai,        │         └───────────────────────┘    │
│  │   zonewise-data,      │                   │                   │
│  │   zonewise-web,       │                   │ connects to       │
│  │   zonewise-mvp)       │                   ▼                   │
│  └──────────────────────┘         ┌───────────────────────┐     │
│                                    │  Render                │    │
│                                    │  zonewise-agents       │    │
│  zonewise-agents.onrender.com ◄────│  FastAPI NLP Backend   │    │
│                                    │  Repo: zonewise-agents │    │
│                                    └───────────┬───────────┘    │
│                                                │                 │
│                                                ▼                 │
│                                    ┌───────────────────────┐    │
│                                    │  Supabase              │    │
│                                    │  mocerqjnksmhcjzxrewo  │    │
│                                    │  Tables:               │    │
│                                    │   - jurisdictions      │    │
│                                    │   - zoning_districts   │    │
│                                    │   - zone_standards     │    │
│                                    │   - overlay_districts  │    │
│                                    │   - parcel_zones       │    │
│                                    └───────────┬───────────┘    │
│                                                ▲                 │
│                                                │ populates       │
│                                    ┌───────────────────────┐    │
│                                    │  Modal.com             │    │
│                                    │  67-County Scraper     │    │
│                                    │  Repo: zonewise-modal  │    │
│                                    │  AgentQL + Firecrawl   │    │
│                                    └───────────────────────┘    │
│                                                                  │
│  zonewise (monorepo) = Development workspace, NOT deployed       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## VERCEL PROJECT CLEANUP NEEDED

`zonewise-web` has **5 Vercel projects** connected. This is excessive:

| Vercel Project | Status | Action |
|----------------|--------|--------|
| `zonewise-moat` | ❌ FAILED on last deploy | **DELETE** — stale project |
| `zonewise-ai` | ✅ Deployed | Keep — but which domain? |
| `zonewise-data` | ✅ Deployed | **DELETE** — redundant |
| `zonewise-web` | ✅ Deployed | Keep as primary |
| `zonewise-mvp` | ✅ Deployed | **DELETE** — redundant |

**TARGET**: 1 Vercel project (`zonewise-web`) → 1 domain (`zonewise.ai`)

---

## DESCRIPTION FIXES NEEDED

| Repo | Current Description | Correct Description |
|------|--------------------|--------------------|
| `zonewise-web` | "ARCHIVED - Replaced by Craft Agents viewer" | "ZoneWise.AI Marketing Site — zonewise.ai homepage (Next.js + Vercel)" |
| `zonewise-agents` | "⚠️ DEPRECATED - Replaced by zonewise-lobster" | "ZoneWise Agent API — NLP backend on Render (FastAPI + Supabase)" |
| `zonewise-lobster` | "replaces zonewise-agents and zonewise-skills" | "🧪 EXPERIMENT — Moltbot Lobster workflow POC (not in production)" |

---

## SKILLS LOCATION MAP

Skills exist in 3 places. This must be consolidated:

| Location | Skills | Status |
|----------|--------|--------|
| `zonewise/.claude/skills/` | 7 Claude Code skills (district-lookup, site-analysis, mcp-server, etc.) | ✅ For Claude Code sessions |
| `zonewise-desktop/zonewise/skills/` | 12 CraftAgents skills (threejs-*, mapbox, etc.) + NEW zonewise-intelligence master prompt | ✅ For CraftAgents desktop |
| `zonewise-skills` (repo) | Legacy skills | ❌ ARCHIVED — ignore |

**RULE**: Claude Code skills → `zonewise/.claude/skills/`. CraftAgents skills → `zonewise-desktop/zonewise/skills/`.

---

## WHEN TO USE WHICH REPO

| Task | Repo | Why |
|------|------|-----|
| Edit homepage / marketing / pricing | `zonewise-web` | Vercel auto-deploys to zonewise.ai |
| Edit desktop app / CraftAgents skills / sources | `zonewise-desktop` | CraftAgents workspace |
| Edit NLP backend / agent functions / API endpoints | `zonewise-agents` | Render auto-deploys |
| Edit data pipeline / scraper / AgentQL | `zonewise-modal` | Modal.com serverless |
| Claude Code development / full-stack work / MCP server | `zonewise` | Monorepo workspace |
| Supabase schema / migrations | `zonewise` (migrations/) | Schema source of truth |

---

## IMMEDIATE CLEANUP ACTIONS

### Priority 1: Fix Descriptions (5 min)
```bash
# Fix zonewise-web
gh repo edit breverdbidder/zonewise-web --description "ZoneWise.AI Marketing Site — Next.js homepage deployed to zonewise.ai via Vercel"

# Fix zonewise-agents
gh repo edit breverdbidder/zonewise-agents --description "ZoneWise Agent API — FastAPI NLP backend on Render (Supabase + 67 counties)"

# Fix zonewise-lobster
gh repo edit breverdbidder/zonewise-lobster --description "🧪 EXPERIMENT — Moltbot Lobster workflow POC (not in production)"
```

### Priority 2: Clean Vercel (10 min)
- Go to vercel.com/dashboard
- Delete projects: zonewise-moat, zonewise-data, zonewise-mvp
- Keep: zonewise-web (primary, zonewise.ai domain)
- Keep: zonewise-desktop deployment (zonewise.app domain)

### Priority 3: Archive Dead Repos
- `zonewise-rebrand-mission` → Archive (mission complete)
- `zonewise-traycer-specs` → Archive (specs captured)

---

## ENVIRONMENT VARIABLES

| Service | Variable | Where Stored |
|---------|----------|-------------|
| Render (zonewise-agents) | `SUPABASE_URL`, `SUPABASE_KEY` | Render Dashboard env vars |
| Modal (zonewise-modal) | `AGENTQL_API_KEY`, `SUPABASE_KEY` | GitHub Secrets |
| Vercel (zonewise-web) | None needed (static site) | — |
| CraftAgents Desktop | `ANTHROPIC_API_KEY`, `SUPABASE_KEY` | Local ~/.craft-agent/ |
| Mapbox | Token in memory | `pk.eyJ1...` (everest18 account) |

---

## GOLDEN RULE

> **Before pushing code, ask: "Which repo owns this?"**
> - Marketing → `zonewise-web`
> - Desktop/Skills → `zonewise-desktop`
> - API/Backend → `zonewise-agents`
> - Scraping → `zonewise-modal`
> - Everything else → `zonewise`
