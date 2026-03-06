# MISSION 3: Update Monorepo REPO_MAP.md

## OBJECTIVE
Update `breverdbidder/zonewise/REPO_MAP.md` to reflect current reality as of March 2026. Three critical changes: add `zonewise-scraper-v4` as ACTIVE, move `zonewise-modal` to LEGACY/DEPRECATED, and update the architecture diagram.

## CONTEXT
REPO_MAP.md was last updated Feb 8, 2026. Since then:
- `zonewise-scraper-v4` was created as the replacement data pipeline (Firecrawl + Gemini + Claude waterfall)
- AgentQL was deprecated on Mar 6, 2026 (downgraded to Starter $0/mo)
- `zonewise-modal` is now LEGACY — its AgentQL-based pipeline is replaced by scraper-v4
- All 5 active repos now have 9/9 Claude Code structure compliance (TODO.md, PROJECT_STATE.json, REPO_MAP.md, .claude/, etc.)
- The "WHEN TO USE WHICH REPO" table needs a scraper-v4 entry
- The architecture diagram still shows `zonewise-modal` as the active data pipeline

## EXECUTION PLAN

### Step 1: Clone the monorepo
```bash
git clone https://github.com/breverdbidder/zonewise.git
cd zonewise
```

### Step 2: Read current REPO_MAP.md
```bash
cat REPO_MAP.md
```

### Step 3: Apply ALL of the following edits

#### 3A: Update header metadata
```
**Last Updated**: 2026-03-06
```

#### 3B: Update "THE PROBLEM" section
Replace the Feb 8 framing with current status:
```markdown
## CURRENT STATUS (As of Mar 6, 2026)

6 active repos. All at 9/9 Claude Code structure compliance.
Shared skills canonicalized in monorepo with pointer files in other repos.
AgentQL deprecated — replaced by Firecrawl+Gemini+Claude waterfall in scraper-v4.

**This document is the single source of truth for what goes where.**
```

#### 3C: Update ACTIVE REPOS table
**Add scraper-v4 as row 6. Update zonewise-modal row.**

New table:
```markdown
### ✅ ACTIVE REPOS (Use These)

| # | Repo | Purpose | Deploys To | Status |
|---|------|---------|------------|--------|
| 1 | **`zonewise`** | **MONOREPO** — Core codebase, canonical skills, agents, MCP server, migrations | None (dev only) | ✅ ACTIVE — 9/9 structure, canonical skill source |
| 2 | **`zonewise-web`** | **MARKETING SITE** — Next.js homepage at zonewise.ai | Vercel → zonewise.ai | ✅ ACTIVE — 9/9 structure |
| 3 | **`zonewise-desktop`** | **DESKTOP APP** — CraftAgents OSS v0.4.0 fork with ZoneWise skills | Vercel → zonewise.app | ✅ ACTIVE — 9/9 structure |
| 4 | **`zonewise-agents`** | **NLP BACKEND** — FastAPI agent API on Render | Render → zonewise-agents.onrender.com | ✅ ACTIVE — 9/9 structure |
| 5 | **`zonewise-scraper-v4`** | **DATA PIPELINE** — Firecrawl+Gemini+Claude waterfall scraper for 67 FL counties | GitHub Actions nightly 11PM EST | ✅ ACTIVE — 9/9 structure, replaced zonewise-modal |
```

#### 3D: Move zonewise-modal to LEGACY section
Create a new section between ACTIVE and REFERENCE:

```markdown
### ⚠️ LEGACY REPOS (Do Not Use for New Work)

| # | Repo | Purpose | Status |
|---|------|---------|--------|
| 6 | `zonewise-modal` | Old AgentQL-based 67-county scraper on Modal.com | ⚠️ LEGACY — AgentQL deprecated Mar 6, 2026. Replaced by `zonewise-scraper-v4`. Do NOT run new scrape jobs here. |
```

#### 3E: Update REFERENCE REPOS
Keep existing entries, renumber starting from 7:

```markdown
### 🗄️ REFERENCE REPOS (Read-Only / Docs)

| # | Repo | Purpose | Status |
|---|------|---------|--------|
| 7 | `zonewise-lobster` | Moltbot Lobster workflow experiment | 🧪 EXPERIMENT — Never replaced agents |
| 8 | `zonewise-rebrand-mission` | Claude Code mission doc for navy+orange rebrand | 📄 DOCS ONLY |
| 9 | `zonewise-traycer-specs` | Traycer auto-plan specifications | 📄 DOCS ONLY |
```

#### 3F: Update DEAD REPOS
```markdown
### ❌ DEAD REPOS (Archive or Delete)

| # | Repo | Why |
|---|------|-----|
| 10 | `zonewise-skills` | Already archived. Replaced by skills inside `zonewise-desktop` and `zonewise` |
```

#### 3G: Update architecture diagram
Replace the `WHAT SERVES WHAT` diagram. Key change: `zonewise-modal` box → `zonewise-scraper-v4` box with new pipeline description:

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

#### 3H: Update "WHEN TO USE WHICH REPO" table
Add scraper-v4, update modal entry:

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

#### 3I: Update SKILLS LOCATION MAP
Reflect the deduplication work (Mission 2):

```markdown
## SKILLS LOCATION MAP

| Location | Skills | Status |
|----------|--------|--------|
| `zonewise/.claude/skills/` | **12 skills** — 5 shared (canonical source) + 7 ZoneWise-specific | ✅ CANONICAL SOURCE |
| `zonewise-web/.claude/skills/` | 5 pointer files → reference monorepo | ✅ POINTERS ONLY |
| `zonewise-desktop/.claude/skills/` | 5 pointer files → reference monorepo | ✅ POINTERS ONLY |
| `zonewise-agents/.claude/skills/` | 5 pointer files → reference monorepo | ✅ POINTERS ONLY |
| `zonewise-scraper-v4/.claude/skills/` | 2 repo-specific skills (scraper-pipeline, code-review) | ✅ LOCAL ONLY |
| `zonewise-desktop/zonewise/skills/` | 12 CraftAgents skills (threejs-*, mapbox, etc.) | ✅ DESKTOP ONLY |
| `zonewise-skills` (repo) | Legacy skills | ❌ ARCHIVED — ignore |

**RULE**: Shared Claude Code skills → update in `zonewise/.claude/skills/` ONLY.
Repo-specific skills → stay in their respective repos.
```

#### 3J: Update DESCRIPTION FIXES section
Remove fixes that have already been applied. Add scraper-v4:

```markdown
## REPO DESCRIPTIONS

| Repo | Description |
|------|----|
| `zonewise` | ZoneWise.AI Monorepo — Core codebase, canonical skills, agents, MCP server |
| `zonewise-web` | ZoneWise.AI Marketing Site — Next.js homepage at zonewise.ai (Vercel) |
| `zonewise-desktop` | ZoneWise Desktop — CraftAgents OSS fork with ZoneWise skills (Vercel → zonewise.app) |
| `zonewise-agents` | ZoneWise Agent API — FastAPI NLP backend on Render (Supabase + 67 counties) |
| `zonewise-scraper-v4` | ZoneWise Data Pipeline — Firecrawl+Gemini+Claude waterfall for FL zoning extraction |
| `zonewise-modal` | ⚠️ LEGACY — Old AgentQL scraper, replaced by zonewise-scraper-v4 |
```

#### 3K: Add CLAUDE CODE STRUCTURE COMPLIANCE section (new)
```markdown
## CLAUDE CODE STRUCTURE COMPLIANCE

All active repos achieved 9/9 compliance on Mar 6, 2026:

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

### Step 4: Update PROJECT_STATE.json
Add to `recent_decisions`:
```json
{
  "date": "2026-03-06",
  "decision": "REPO_MAP.md v2 — added scraper-v4, deprecated zonewise-modal, updated architecture diagram",
  "rationale": "REPO_MAP was stale since Feb 8. Scraper-v4 exists, AgentQL deprecated, all repos at 9/9 compliance."
}
```

### Step 5: Commit and push
```bash
git add REPO_MAP.md PROJECT_STATE.json
git commit -m "docs: update REPO_MAP.md v2 — add scraper-v4, deprecate zonewise-modal

Major updates to single source of truth:
- Added zonewise-scraper-v4 as ACTIVE repo (#5)
- Moved zonewise-modal to LEGACY (AgentQL deprecated Mar 6)
- Updated architecture diagram with waterfall pipeline
- Added Claude Code structure compliance table (45/45)
- Updated skills location map with dedup pointers
- Updated 'When to use which repo' routing table
- Refreshed repo descriptions

Last updated: Feb 8, 2026 → Mar 6, 2026"

git push origin main
```

### Step 6: Verify
```bash
# Verify key sections exist
grep -c "scraper-v4" REPO_MAP.md    # Should be >= 5
grep -c "LEGACY" REPO_MAP.md        # Should be >= 2
grep -c "9/9" REPO_MAP.md           # Should be >= 1
grep "Last Updated" REPO_MAP.md     # Should show 2026-03-06
```

## RULES
- Do NOT delete any content from the Vercel cleanup section — those may still be pending
- Keep the GOLDEN RULE section at the bottom, update if needed
- Keep the ENVIRONMENT VARIABLES section, update if any changed
- The architecture diagram MUST show scraper-v4 (not zonewise-modal) as the active pipeline
- Use the exact repo names — never abbreviate
- Zero human intervention required

## SUCCESS CRITERIA
- [ ] `Last Updated` shows `2026-03-06`
- [ ] `zonewise-scraper-v4` appears in ACTIVE REPOS table
- [ ] `zonewise-modal` appears in LEGACY section (not ACTIVE)
- [ ] Architecture diagram shows scraper-v4 with waterfall pipeline
- [ ] Skills location map reflects deduplication
- [ ] Claude Code compliance table shows 45/45
- [ ] Pushed to main
