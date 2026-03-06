# ZONEWISE STRUCTURE CLEANUP — 3 Missions, 1 Session
# Claude Code Directive | March 6, 2026 | Owner: Ariel Shapira

## SESSION OVERVIEW
Execute 3 sequential missions to complete ZoneWise.AI's Claude Code structure compliance. Order matters — Mission 2 before Mission 3.

**Estimated time:** 45-60 minutes | **Auth:** GitHub token from env or `gh auth status`
**Repos touched:** zonewise-web, zonewise-desktop, zonewise-agents, zonewise (monorepo)

## GLOBAL RULES
- Zero human intervention. Blocked? 3 retries, then log to PROJECT_STATE.json and move to next mission.
- Read before delete. Never delete a workflow or skill without reading it first.
- Diff before replace. Never replace a skill copy without diffing against canonical.
- One commit per mission. Not one giant commit across all 3.
- Push to main. All repos deploy from main — no feature branches for cleanup work.
- Verify after each mission before starting the next.

---

# ══════════════════════════════════════════════════════════════
# MISSION 1: Clean Dead Workflows — zonewise-web
# ══════════════════════════════════════════════════════════════

## Objective
Delete dead/one-off debugging workflows from `breverdbidder/zonewise-web/.github/workflows/`. Currently 22 workflow files. Target: ≤13.

## Step 1: Clone
```bash
git clone https://github.com/breverdbidder/zonewise-web.git
cd zonewise-web
```

## Step 2: Classify every workflow

**KEEP (12 files) — Do NOT delete:**

| File | Reason |
|------|--------|
| `ci.yml` | Core CI pipeline |
| `deploy.yml` | Primary deployment |
| `deploy-prod.yml` | Production deployment |
| `deploy-loans.yml` | Feature deploy (loans module) |
| `deploy-michael.yml` | Feature deploy (Michael swimming module) |
| `deploy-migration.yml` | Database migration deploy |
| `deploy-onboarding.yml` | Feature deploy (onboarding) |
| `plan-enforcement-agent.yml` | Agentic plan enforcement — shared across repos |
| `react-doctor.yml` | Code health monitoring |
| `security-checks.yml` | Security audit pipeline |
| `upstream-health.yml` | Upstream dependency monitoring |
| `webhook_notify.yml` | Notification infrastructure |

**DELETE (10 files) — One-off debug/fix scripts:**

| File | Why Delete |
|------|-----------|
| `dns-debug.yml` | One-off DNS debugging during migration |
| `fix-deploy.yml` | One-off deploy fix — superseded by deploy.yml |
| `fix-vercel-domains.yml` | One-off Vercel domain fix — issue resolved |
| `switch-dns.yml` | One-off DNS switch — migration complete |
| `vinext-benchmark.yml` | Vinext experiment benchmarking — experiment over |
| `vinext-debug.yml` | Vinext debugging — experiment over |
| `vinext-deploy-fixed.yml` | Vinext deploy attempt — experiment over |
| `vinext-fixed-deploy.yml` | Vinext deploy retry — experiment over |
| `vinext-inspect.yml` | Vinext inspection — experiment over |
| `vinext-wrangler-deploy.yml` | Vinext Wrangler deploy — experiment over |

## Step 3: Verify before deleting
For EACH file marked DELETE, open it and confirm:
1. It has NO `schedule:` trigger (cron jobs must not be deleted)
2. It is NOT referenced by other workflows via `workflow_call` or `workflow_dispatch`
3. It does NOT contain unique secrets or environment setup other files depend on

**If ANY check fails → move the file to KEEP and adjust the count.**

## Step 4: Delete confirmed dead workflows
```bash
git rm .github/workflows/dns-debug.yml
git rm .github/workflows/fix-deploy.yml
git rm .github/workflows/fix-vercel-domains.yml
git rm .github/workflows/switch-dns.yml
git rm .github/workflows/vinext-benchmark.yml
git rm .github/workflows/vinext-debug.yml
git rm .github/workflows/vinext-deploy-fixed.yml
git rm .github/workflows/vinext-fixed-deploy.yml
git rm .github/workflows/vinext-inspect.yml
git rm .github/workflows/vinext-wrangler-deploy.yml
```

## Step 5: Update PROJECT_STATE.json
Update `workflows_active` to new count, set `workflows_dead_estimate` to 0, add to `recent_decisions`:
```json
{"date": "2026-03-06", "decision": "Deleted 10 dead workflows", "rationale": "One-off debug/fix scripts from Vercel/DNS migration. 22→12."}
```

## Step 6: Commit and push
```bash
git add -A
git commit -m "chore: delete 10 dead debug/fix workflows (22→12)

Removed: dns-debug, fix-deploy, fix-vercel-domains, switch-dns,
vinext-benchmark, vinext-debug, vinext-deploy-fixed,
vinext-fixed-deploy, vinext-inspect, vinext-wrangler-deploy

All verified: no cron triggers removed, no cross-workflow deps broken."

git push origin main
```

## Verify Mission 1
```bash
ls .github/workflows/ | wc -l
# Expected: 12. If >13, re-audit.
```

---

# ══════════════════════════════════════════════════════════════
# MISSION 2: Deduplicate Shared Skills
# ══════════════════════════════════════════════════════════════

## Objective
5 identical skills (`agent-browser`, `auction-pipeline`, `build-with-agent-team`, `e2e-test`, `supabase`) are duplicated across 4 repos (15 total copies). Replace 3 repos' copies with pointer files referencing the monorepo canonical source.

## Current State
```
SKILL                    zonewise    zonewise-web  zonewise-desktop  zonewise-agents
─────────────────────── ─────────── ──────────── ──────────────── ────────────────
agent-browser            ✅ CANONICAL  COPY          COPY              COPY
auction-pipeline         ✅ CANONICAL  COPY          COPY              COPY
build-with-agent-team    ✅ CANONICAL  COPY          COPY              COPY
e2e-test                 ✅ CANONICAL  COPY          COPY              COPY
supabase                 ✅ CANONICAL  COPY          COPY              COPY
```

## Step 1: Clone remaining repos (if not already cloned)
```bash
git clone https://github.com/breverdbidder/zonewise.git
git clone https://github.com/breverdbidder/zonewise-desktop.git
git clone https://github.com/breverdbidder/zonewise-agents.git
# zonewise-web already cloned from Mission 1
```

## Step 2: Diff each skill against canonical
```bash
SKILLS="agent-browser auction-pipeline build-with-agent-team e2e-test supabase"
for SKILL in $SKILLS; do
  echo "=== $SKILL ==="
  for REPO in zonewise-web zonewise-desktop zonewise-agents; do
    CANONICAL="zonewise/.claude/skills/$SKILL/"
    COPY="$REPO/.claude/skills/$SKILL/"
    if [ -d "$COPY" ]; then
      echo "  $REPO:"
      diff -rq "$CANONICAL" "$COPY" 2>/dev/null && echo "    IDENTICAL" || echo "    ⚠️ DIVERGED"
    fi
  done
done
```

**Record results.** If copies have diverged:
1. Read both versions
2. Merge the better/newer content INTO the monorepo canonical version
3. Commit to monorepo FIRST before touching other repos

## Step 3: Create pointer files
For each of the 5 skills in each of the 3 non-monorepo repos, replace the skill directory contents with a single SKILL.md pointer.

**Pointer template** (customize `SKILL_NAME` and `SUMMARY` per skill):

```markdown
# SKILL_NAME — Shared Skill (Pointer)

> **Canonical source:** [zonewise/.claude/skills/SKILL_NAME/](https://github.com/breverdbidder/zonewise/tree/main/.claude/skills/SKILL_NAME)

## What This Skill Does
SUMMARY

## Fetch Full Instructions
```bash
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/breverdbidder/zonewise/contents/.claude/skills/SKILL_NAME/SKILL.md" | \
  python3 -c "import sys,json,base64; print(base64.b64decode(json.load(sys.stdin)['content']).decode())"
```

This skill is shared across 4 ZoneWise repos. To prevent stale copies,
the canonical version lives in the monorepo. Update there only.
```

**Summaries by skill:**

| Skill | Summary |
|-------|---------|
| `agent-browser` | Browser automation patterns for web scraping and testing with Puppeteer/Playwright |
| `auction-pipeline` | Foreclosure auction data processing pipeline (BidDeed.AI integration) |
| `build-with-agent-team` | Multi-agent coordination patterns for LangGraph agent teams |
| `e2e-test` | End-to-end testing patterns with Playwright for ZoneWise applications |
| `supabase` | Supabase database operations: queries, upserts, migrations, RLS policies |

## Step 4: Apply to each repo
For each of `zonewise-web`, `zonewise-desktop`, `zonewise-agents`:

```bash
cd <REPO>
for SKILL in agent-browser auction-pipeline build-with-agent-team e2e-test supabase; do
  # Delete all files in skill dir
  find .claude/skills/$SKILL/ -type f -delete
  # Write pointer SKILL.md (use template above with correct SKILL_NAME and SUMMARY)
done
```

## Step 5: Update CLAUDE.md in each repo
Append to each repo's CLAUDE.md:

```markdown
## SHARED SKILLS
5 skills in `.claude/skills/` are pointers to the canonical monorepo (`zonewise`).
If you need full instructions, the pointer file contains a curl command to fetch them.
Canonical source: https://github.com/breverdbidder/zonewise/tree/main/.claude/skills/
```

Also add to the monorepo CLAUDE.md:

```markdown
## CANONICAL SKILLS
This repo is the single source of truth for 5 shared skills:
agent-browser, auction-pipeline, build-with-agent-team, e2e-test, supabase.
When updating these skills, changes propagate (other repos reference this copy).
Repo-specific skills (everest-github-deployment, zonewise-63kpi-reports, etc.) stay local.
```

## Step 6: Commit and push each repo
```bash
for REPO in zonewise zonewise-web zonewise-desktop zonewise-agents; do
  cd $REPO
  git add -A
  git commit -m "refactor: deduplicate 5 shared skills → monorepo pointers

Shared skills (agent-browser, auction-pipeline, build-with-agent-team,
e2e-test, supabase) now point to canonical versions in zonewise monorepo.
Prevents skill drift when only one repo's copy gets updated."
  git push origin main
  cd ..
done
```

## Verify Mission 2
```bash
for REPO in zonewise-web zonewise-desktop zonewise-agents; do
  echo "=== $REPO ==="
  for SKILL in agent-browser auction-pipeline build-with-agent-team e2e-test supabase; do
    if grep -q "Canonical source" "$REPO/.claude/skills/$SKILL/SKILL.md" 2>/dev/null; then
      echo "  ✅ $SKILL → pointer"
    else
      echo "  ❌ $SKILL → still full copy"
    fi
  done
done
# Expected: 15 ✅, 0 ❌
```

---

# ══════════════════════════════════════════════════════════════
# MISSION 3: Update Monorepo REPO_MAP.md
# ══════════════════════════════════════════════════════════════

## Objective
Update `breverdbidder/zonewise/REPO_MAP.md` to reflect March 2026 reality: add `zonewise-scraper-v4` as ACTIVE, move `zonewise-modal` to LEGACY, update architecture diagram, add compliance table.

## Step 1: Navigate to monorepo
```bash
cd zonewise  # already cloned from Mission 2
```

## Step 2: Apply all edits to REPO_MAP.md

### 2A: Update header
```
**Last Updated**: 2026-03-06
```

### 2B: Replace "THE PROBLEM" section with:
```markdown
## CURRENT STATUS (As of Mar 6, 2026)

6 active repos. All at 9/9 Claude Code structure compliance.
Shared skills canonicalized in monorepo with pointer files in other repos.
AgentQL deprecated — replaced by Firecrawl+Gemini+Claude waterfall in scraper-v4.

**This document is the single source of truth for what goes where.**
```

### 2C: Update ACTIVE REPOS table
```markdown
### ✅ ACTIVE REPOS (Use These)

| # | Repo | Purpose | Deploys To | Status |
|---|------|---------|------------|--------|
| 1 | **`zonewise`** | **MONOREPO** — Core codebase, canonical skills, agents, MCP server, migrations | None (dev only) | ✅ ACTIVE — 9/9 structure, canonical skill source |
| 2 | **`zonewise-web`** | **MARKETING SITE** — Next.js homepage at zonewise.ai | Vercel → zonewise.ai | ✅ ACTIVE — 9/9 structure |
| 3 | **`zonewise-desktop`** | **DESKTOP APP** — CraftAgents OSS v0.4.0 fork with ZoneWise skills | Vercel → zonewise.app | ✅ ACTIVE — 9/9 structure |
| 4 | **`zonewise-agents`** | **NLP BACKEND** — FastAPI agent API on Render | Render → zonewise-agents.onrender.com | ✅ ACTIVE — 9/9 structure |
| 5 | **`zonewise-scraper-v4`** | **DATA PIPELINE** — Firecrawl+Gemini+Claude waterfall for 67 FL counties | GitHub Actions nightly 11PM EST | ✅ ACTIVE — 9/9 structure, replaced zonewise-modal |
```

### 2D: Add new LEGACY section (between ACTIVE and REFERENCE)
```markdown
### ⚠️ LEGACY REPOS (Do Not Use for New Work)

| # | Repo | Purpose | Status |
|---|------|---------|--------|
| 6 | `zonewise-modal` | Old AgentQL-based 67-county scraper on Modal.com | ⚠️ LEGACY — AgentQL deprecated Mar 6, 2026. Replaced by `zonewise-scraper-v4`. Do NOT run new scrape jobs here. |
```

### 2E: Renumber REFERENCE REPOS starting from 7
```markdown
### 🗄️ REFERENCE REPOS (Read-Only / Docs)

| # | Repo | Purpose | Status |
|---|------|---------|--------|
| 7 | `zonewise-lobster` | Moltbot Lobster workflow experiment | 🧪 EXPERIMENT — Never replaced agents |
| 8 | `zonewise-rebrand-mission` | Claude Code mission doc for navy+orange rebrand | 📄 DOCS ONLY |
| 9 | `zonewise-traycer-specs` | Traycer auto-plan specifications | 📄 DOCS ONLY |
```

### 2F: DEAD REPOS renumber to 10
```markdown
### ❌ DEAD REPOS (Archive or Delete)

| # | Repo | Why |
|---|------|-----|
| 10 | `zonewise-skills` | Already archived. Replaced by skills inside `zonewise-desktop` and `zonewise` |
```

### 2G: Replace architecture diagram
```markdown
## WHAT SERVES WHAT

```
┌──────────────────────────────────────────────────────────────────────┐
│                      PRODUCTION SERVICES                              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  zonewise.ai (Marketing)            zonewise.app (Desktop)            │
│  ┌────────────────────────┐         ┌─────────────────────────┐      │
│  │  Vercel                 │         │  Vercel                  │     │
│  │  Repo: zonewise-web     │         │  Repo: zonewise-desktop  │     │
│  │  Next.js + Inter font   │         │  CraftAgents v0.4.0      │     │
│  │  Brand: #1E3A5F + #F59E0B│        │  Skills + Sources        │     │
│  └────────────────────────┘         └─────────────────────────┘      │
│                                                │                      │
│                                                │ connects to          │
│                                                ▼                      │
│                                     ┌─────────────────────────┐      │
│  zonewise-agents.onrender.com ◄─────│  Render                  │     │
│                                     │  zonewise-agents          │     │
│                                     │  FastAPI NLP Backend      │     │
│                                     └───────────┬─────────────┘      │
│                                                 │                     │
│                                                 ▼                     │
│                                     ┌─────────────────────────┐      │
│                                     │  Supabase                 │     │
│                                     │  mocerqjnksmhcjzxrewo     │     │
│                                     │  Tables:                   │     │
│                                     │   - jurisdictions (368)    │     │
│                                     │   - zoning_districts       │     │
│                                     │   - zone_standards         │     │
│                                     │   - permitted_uses         │     │
│                                     │   - overlay_districts      │     │
│                                     │   - parcel_zones           │     │
│                                     └───────────┬─────────────┘      │
│                                                 ▲                     │
│                                                 │ populates           │
│                                     ┌─────────────────────────┐      │
│                                     │  GitHub Actions           │     │
│                                     │  Nightly 11PM EST         │     │
│                                     │  Repo: zonewise-scraper-v4│     │
│                                     │  Waterfall Pipeline:       │     │
│                                     │   Firecrawl → Markdown     │     │
│                                     │   Gemini → Structured JSON │     │
│                                     │   Claude → Complex Fallback│     │
│                                     └─────────────────────────┘      │
│                                                                       │
│  zonewise (monorepo) = Development workspace, NOT deployed            │
│  zonewise-modal = ⚠️ LEGACY (AgentQL deprecated, do not use)         │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```
```

### 2H: Update "WHEN TO USE WHICH REPO"
```markdown
## WHEN TO USE WHICH REPO

| Task | Repo | Why |
|------|------|-----|
| Edit homepage / marketing / pricing | `zonewise-web` | Vercel auto-deploys to zonewise.ai |
| Edit desktop app / CraftAgents skills / sources | `zonewise-desktop` | CraftAgents workspace |
| Edit NLP backend / agent functions / API endpoints | `zonewise-agents` | Render auto-deploys |
| **Scrape zoning data / pipeline work / extraction** | **`zonewise-scraper-v4`** | **Active pipeline — Firecrawl+Gemini+Claude** |
| Claude Code development / full-stack work / MCP server | `zonewise` | Monorepo workspace |
| Supabase schema / migrations | `zonewise` (migrations/) | Schema source of truth |
| ~~Edit data pipeline / scraper / AgentQL~~ | ~~`zonewise-modal`~~ | ~~⚠️ LEGACY — use scraper-v4 instead~~ |
```

### 2I: Update SKILLS LOCATION MAP
```markdown
## SKILLS LOCATION MAP

| Location | Skills | Status |
|----------|--------|--------|
| `zonewise/.claude/skills/` | **12 skills** — 5 shared (canonical) + 7 ZoneWise-specific | ✅ CANONICAL SOURCE |
| `zonewise-web/.claude/skills/` | 5 pointer files → reference monorepo | ✅ POINTERS ONLY |
| `zonewise-desktop/.claude/skills/` | 5 pointer files → reference monorepo | ✅ POINTERS ONLY |
| `zonewise-agents/.claude/skills/` | 5 pointer files → reference monorepo | ✅ POINTERS ONLY |
| `zonewise-scraper-v4/.claude/skills/` | 2 repo-specific (scraper-pipeline, code-review) | ✅ LOCAL ONLY |
| `zonewise-desktop/zonewise/skills/` | 12 CraftAgents skills (threejs-*, mapbox, etc.) | ✅ DESKTOP ONLY |
| `zonewise-skills` (repo) | Legacy skills | ❌ ARCHIVED — ignore |

**RULE**: Shared Claude Code skills → update in `zonewise/.claude/skills/` ONLY.
```

### 2J: Add new CLAUDE CODE STRUCTURE COMPLIANCE section
```markdown
## CLAUDE CODE STRUCTURE COMPLIANCE

All active repos achieved 9/9 on Mar 6, 2026:

| Check | zonewise | web | desktop | agents | scraper-v4 |
|-------|:--------:|:---:|:-------:|:------:|:----------:|
| CLAUDE.md | ✅ | ✅ | ✅ | ✅ | ✅ |
| TODO.md | ✅ | ✅ | ✅ | ✅ | ✅ |
| PROJECT_STATE.json | ✅ | ✅ | ✅ | ✅ | ✅ |
| .claude/ | ✅ | ✅ | ✅ | ✅ | ✅ |
| tests/ | ✅ | ✅ | ✅ | ✅ | ✅ |
| docs/ | ✅ | ✅ | ✅ | ✅ | ✅ |
| .github/workflows/ | ✅ | ✅ | ✅ | ✅ | ✅ |
| .env.example | ✅ | ✅ | ✅ | ✅ | ✅ |
| REPO_MAP.md | ✅ | ✅ | ✅ | ✅ | ✅ |

**Score: 45/45 (10.0/10.0)**
```

### 2K: Update REPO DESCRIPTIONS table
```markdown
## REPO DESCRIPTIONS

| Repo | Description |
|------|-------------|
| `zonewise` | ZoneWise.AI Monorepo — Core codebase, canonical skills, agents, MCP server |
| `zonewise-web` | ZoneWise.AI Marketing Site — Next.js homepage at zonewise.ai (Vercel) |
| `zonewise-desktop` | ZoneWise Desktop — CraftAgents OSS fork with ZoneWise skills (Vercel → zonewise.app) |
| `zonewise-agents` | ZoneWise Agent API — FastAPI NLP backend on Render (Supabase + 67 counties) |
| `zonewise-scraper-v4` | ZoneWise Data Pipeline — Firecrawl+Gemini+Claude waterfall for FL zoning extraction |
| `zonewise-modal` | ⚠️ LEGACY — Old AgentQL scraper, replaced by zonewise-scraper-v4 |
```

## Step 3: Update PROJECT_STATE.json
Add to `recent_decisions`:
```json
{"date": "2026-03-06", "decision": "REPO_MAP.md v2 — added scraper-v4, deprecated modal, updated architecture", "rationale": "Stale since Feb 8. scraper-v4 exists, AgentQL deprecated, all repos at 9/9."}
```

## Step 4: Commit and push
```bash
git add REPO_MAP.md PROJECT_STATE.json
git commit -m "docs: REPO_MAP.md v2 — add scraper-v4, deprecate modal

- Added zonewise-scraper-v4 as ACTIVE repo #5
- Moved zonewise-modal to LEGACY (AgentQL deprecated Mar 6)
- Updated architecture diagram with waterfall pipeline
- Added Claude Code compliance table (45/45)
- Updated skills map with dedup pointers
- Refreshed 'When to use which repo' routing

Last updated: Feb 8 → Mar 6, 2026"

git push origin main
```

## Verify Mission 3
```bash
grep -c "scraper-v4" REPO_MAP.md    # ≥5
grep -c "LEGACY" REPO_MAP.md        # ≥2
grep "Last Updated" REPO_MAP.md     # 2026-03-06
```

---

# ══════════════════════════════════════════════════════════════
# POST-SESSION CHECKLIST
# ══════════════════════════════════════════════════════════════

After all 3 missions:
- [ ] zonewise-web: ≤13 workflows remaining
- [ ] zonewise-web/desktop/agents: 5 pointer skills each (15 total pointers)
- [ ] zonewise monorepo: REPO_MAP.md updated with scraper-v4, modal deprecated
- [ ] All PROJECT_STATE.json files updated with recent_decisions
- [ ] All repos pushed to main, verified on GitHub

## ABORT CONDITIONS
- Workflow has `schedule:` trigger → KEEP it, adjust count
- Skill copy diverged from canonical → MERGE first, don't overwrite
- Git push fails → `git pull --rebase` first, retry
- >3 failures on any mission → Log and move to next mission
