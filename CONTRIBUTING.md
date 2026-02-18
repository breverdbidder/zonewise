# Contributing to ZoneWise.AI

Thank you for your interest in contributing.

## Setup

```bash
git clone https://github.com/breverdbidder/zonewise.git
cd zonewise
pip install -r requirements.txt
cp .env.example .env
```

## Workflow

1. Check `TODO.md` for current sprint priorities
2. Create a branch: `git checkout -b feat/your-feature`
3. Make changes, add tests
4. Run the full check: `pytest tests/ -v && ruff check src/ tests/`
5. Submit a PR against `main`

## Commit Convention

```
feat: add new county scraper adapter
fix: retry logic on Municode 429 rate limit
chore: update dependencies
docs: improve AGENTS.md security section
test: add coverage for phase_extractors
refactor: split scraper into fetcher + parser
```

## What We Need

- **New county adapters** — see `src/scrapers/` for existing patterns
- **Test coverage** — any untested module in `src/`
- **Documentation fixes** — typos, outdated info, unclear instructions
- **Bug reports** — open an issue with reproduction steps

## What We Don't Need

- Changes to `migrations/` without discussion (irreversible)
- New root-level `.md` files for AI session logs (use `docs/missions/`)
- Code that introduces new required external dependencies without justification

## Code Standards

- Python: type hints required, `ruff` for lint, `mypy` for types
- TypeScript: strict mode, no `any`
- Tests: 85% coverage minimum
- Commits: no secrets, no hardcoded API keys

## Questions?

Open an issue or check `CLAUDE.md` for project context.
