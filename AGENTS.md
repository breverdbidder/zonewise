# AGENTS.md — ZoneWise.AI Monorepo

This file defines the default working protocol for AI coding agents in this repository.  
**Scope:** entire repository.

---

## Project Identity

ZoneWise.AI is a Florida zoning intelligence platform. It scrapes, structures, and serves zoning data from all 67 Florida counties via AI-powered natural language interfaces.

```
Stack: Python 3.11 · FastAPI · Next.js 14 · Supabase · Modal.com · LangGraph
```

---

## Architecture Principles

- **Trait/interface-driven:** scrapers, extractors, and providers are swappable via config
- **Data-first:** all decisions deferred to Supabase as single source of truth
- **Zero manual work:** every data update runs autonomously via GitHub Actions or Modal
- **Fail loudly:** prefer explicit errors over silent fallbacks

---

## Working Rules for Agents

### ✅ DO
- Read `CLAUDE.md` for project-specific context before starting
- Check `TODO.md` for the current sprint task before inventing new work
- Update `PROJECT_STATE.json` after significant architectural changes
- Write tests for new extractors/scrapers before considering done
- Commit frequently with descriptive messages (`feat:`, `fix:`, `chore:`, `docs:`)
- Use `ruff` for linting, `mypy` for type checking
- All secrets via environment variables — never hardcode

### ❌ NEVER
- Commit `.env`, `.env.production`, or any file containing real API keys
- Commit AI session artifacts: `CLAUDE_CODE_MISSION*.md`, `PASTE_INTO_CLAUDE_CODE.md`, `OPUS_*_MISSION.md`
- Push directly to `main` without a passing test run
- Broaden filesystem or network scope in scrapers without explicit security review
- Use `print()` for production logging — use the `logging` module
- Create new files in repo root without justification

---

## High-Risk Surfaces

Treat these paths with extra care — changes here require explicit testing:

| Path | Risk | Why |
|------|------|-----|
| `src/scrapers/` | High | External HTTP + anti-bot bypass logic |
| `migrations/` | Critical | Irreversible database changes |
| `scripts/` | High | Production data manipulation |
| `.github/workflows/` | High | Runs with elevated GitHub Actions permissions |

---

## Testing Requirements

```bash
# All tests must pass before merging to main
pytest tests/ -v --cov=src --cov-fail-under=85

# Lint must pass
ruff check src/ tests/

# Type check
mypy src/ --ignore-missing-imports
```

New scrapers require:
- Unit tests with mocked HTTP responses
- Integration tests marked `@pytest.mark.integration`
- At least one test covering error/retry behavior

---

## Commit Convention

```
feat: add Miami-Dade county GIS adapter
fix: retry logic on Municode rate limit (429)
chore: update dependencies
docs: update AGENTS.md with new high-risk surfaces
test: add coverage for phase_extractors edge cases
refactor: split scraper into fetcher + parser layers
```

---

## Directory Map

```
zonewise/
├── src/                   # Core Python source
│   ├── scrapers/          # County-specific scrapers
│   ├── extractors/        # Data extraction logic
│   └── skills/            # Claude skills (TOML + SKILL.md)
├── migrations/            # SQL migrations (sequential, numbered)
├── scripts/               # Operational scripts (run manually or via Actions)
├── tests/                 # All test suites
│   ├── unit/
│   └── integration/
├── docs/                  # Documentation
│   └── missions/          # Archived Claude Code mission logs
├── .github/workflows/     # CI/CD (keep minimal and maintained)
├── CLAUDE.md              # AI architect context
├── AGENTS.md              # This file — agent working protocol
├── TODO.md                # Current sprint tasks
├── PROJECT_STATE.json     # Live system state
└── CHANGELOG.md           # Version history
```

---

## Secrets Reference

All secrets live in GitHub Actions secrets or Modal secrets — never in files.

| Secret Name | Used By |
|-------------|---------|
| `SUPABASE_URL` | All services |
| `SUPABASE_SERVICE_ROLE_KEY` | Migrations, scrapers |
| `ANTHROPIC_API_KEY` | Claude extraction |
| `AGENTQL_API_KEY` | AgentQL scraper |
| `MODAL_TOKEN_ID` | Modal deployments |
| `MAPBOX_TOKEN` | Web frontend (via Vercel env) |

---

## Escalation Protocol

1. Try to solve autonomously (3 attempts minimum)
2. Log blocker to Supabase `insights` table
3. Only then surface to Ariel: **"BLOCKED: [issue]. Tried: [attempts]. Recommend: [solution]. Approve?"**
