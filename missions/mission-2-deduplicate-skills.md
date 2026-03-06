# MISSION 2: Deduplicate Shared Skills Across ZoneWise Repos

## OBJECTIVE
5 identical skills (`agent-browser`, `auction-pipeline`, `build-with-agent-team`, `e2e-test`, `supabase`) are duplicated across 4 repos. Canonicalize them in the monorepo and replace copies in other repos with lightweight pointers.

## CONTEXT
When a skill is updated in one repo, the other 3 go stale. This causes Claude Code to follow outdated instructions depending on which repo it's working in. The monorepo (`zonewise`) is the canonical source — it already has all 5 plus 7 additional skills.

### Current State
```
SKILL                    zonewise  zonewise-web  zonewise-desktop  zonewise-agents
─────────────────────── ──────── ──────────── ──────────────── ────────────────
agent-browser            ✅        COPY          COPY              COPY
auction-pipeline         ✅        COPY          COPY              COPY
build-with-agent-team    ✅        COPY          COPY              COPY
e2e-test                 ✅        COPY          COPY              COPY
supabase                 ✅        COPY          COPY              COPY

Total duplicates: 15 copies (5 skills × 3 repos)
```

### Target State
```
SKILL                    zonewise  zonewise-web  zonewise-desktop  zonewise-agents
─────────────────────── ──────── ──────────── ──────────────── ────────────────
agent-browser            ✅ SRC    POINTER       POINTER           POINTER
auction-pipeline         ✅ SRC    POINTER       POINTER           POINTER
build-with-agent-team    ✅ SRC    POINTER       POINTER           POINTER
e2e-test                 ✅ SRC    POINTER       POINTER           POINTER
supabase                 ✅ SRC    POINTER       POINTER           POINTER
```

## EXECUTION PLAN

### Step 1: Clone all 4 repos
```bash
mkdir ~/zonewise-skills-dedup && cd ~/zonewise-skills-dedup
git clone https://github.com/breverdbidder/zonewise.git
git clone https://github.com/breverdbidder/zonewise-web.git
git clone https://github.com/breverdbidder/zonewise-desktop.git
git clone https://github.com/breverdbidder/zonewise-agents.git
```

### Step 2: Diff each skill against canonical monorepo version
For each of the 5 skills, compare the SKILL.md (and any other files) between monorepo and each copy:

```bash
SKILLS="agent-browser auction-pipeline build-with-agent-team e2e-test supabase"

for SKILL in $SKILLS; do
  echo "=== $SKILL ==="
  for REPO in zonewise-web zonewise-desktop zonewise-agents; do
    CANONICAL="zonewise/.claude/skills/$SKILL/"
    COPY="$REPO/.claude/skills/$SKILL/"
    if [ -d "$COPY" ]; then
      echo "  $REPO:"
      diff -rq "$CANONICAL" "$COPY" 2>/dev/null || echo "    IDENTICAL"
    fi
  done
done
```

**Record the diff results.** This determines whether copies have diverged or are truly identical.

### Step 3: Decide canonical direction

**IF copies are identical to monorepo:** Safe to replace with pointers.
**IF copies have diverged:** Merge changes INTO the monorepo version first, THEN replace copies with pointers.

For any diverged skill:
1. Read both versions carefully
2. The newer/better version wins
3. Update the monorepo canonical version
4. Commit to monorepo FIRST before touching other repos

### Step 4: Create pointer SKILL.md files
Replace each duplicated skill directory's contents with a single pointer file:

```markdown
# [SKILL_NAME] — Shared Skill

> **This skill is maintained in the canonical monorepo.**
> Source: [zonewise/.claude/skills/SKILL_NAME/](https://github.com/breverdbidder/zonewise/tree/main/.claude/skills/SKILL_NAME)

## Quick Reference
[Paste a 3-5 line summary of what this skill does — enough for Claude Code to know when to use it]

## Full Instructions
For the complete, up-to-date skill instructions, reference the canonical source at:
`https://github.com/breverdbidder/zonewise/tree/main/.claude/skills/SKILL_NAME/SKILL.md`

When working in this repo and this skill is needed, fetch the latest version:
```bash
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/breverdbidder/zonewise/contents/.claude/skills/SKILL_NAME/SKILL.md" | \
  python3 -c "import sys,json,base64; print(base64.b64decode(json.load(sys.stdin)['content']).decode())"
```

## Why This Is a Pointer
This skill is shared across 4 ZoneWise repos. To prevent stale copies,
the canonical version lives in the monorepo. See REPO_MAP.md for details.
```

### Step 5: Apply to each repo
For each of the 3 non-monorepo repos:

```bash
cd ~/zonewise-skills-dedup/zonewise-web  # (repeat for desktop, agents)

for SKILL in agent-browser auction-pipeline build-with-agent-team e2e-test supabase; do
  # Delete all files in the skill directory except SKILL.md
  find .claude/skills/$SKILL/ -type f ! -name "SKILL.md" -delete
  
  # Replace SKILL.md with pointer (use the template from Step 4)
  # Customize the summary line for each skill
done
```

**Pointer summaries by skill:**

| Skill | Summary |
|-------|---------|
| `agent-browser` | Browser automation patterns for web scraping and testing with Puppeteer/Playwright |
| `auction-pipeline` | Foreclosure auction data processing pipeline (BidDeed.AI integration) |
| `build-with-agent-team` | Multi-agent coordination patterns for LangGraph agent teams |
| `e2e-test` | End-to-end testing patterns with Playwright for ZoneWise applications |
| `supabase` | Supabase database operations: queries, upserts, migrations, RLS policies |

### Step 6: Update CLAUDE.md in each repo
Add a note to each repo's CLAUDE.md about shared skills:

```markdown
## SHARED SKILLS
5 skills in `.claude/skills/` are pointers to the canonical monorepo (`zonewise`).
If you need the full skill instructions, the pointer file contains a curl command to fetch them.
Canonical source: https://github.com/breverdbidder/zonewise/tree/main/.claude/skills/
```

### Step 7: Commit and push each repo
```bash
for REPO in zonewise-web zonewise-desktop zonewise-agents; do
  cd ~/zonewise-skills-dedup/$REPO
  git add -A
  git commit -m "refactor: replace 5 duplicated skills with monorepo pointers

Shared skills (agent-browser, auction-pipeline, build-with-agent-team,
e2e-test, supabase) now point to canonical versions in zonewise monorepo.

This prevents skill drift when only one repo's copy gets updated.
Full instructions available via pointer files in .claude/skills/*/SKILL.md"

  git push origin main
  cd ..
done
```

### Step 8: Update monorepo CLAUDE.md
Add to zonewise/CLAUDE.md:

```markdown
## CANONICAL SKILLS
This repo is the single source of truth for 5 shared skills used across all ZoneWise repos:
- agent-browser, auction-pipeline, build-with-agent-team, e2e-test, supabase

When updating these skills, changes automatically propagate (other repos reference this copy).
Repo-specific skills (everest-github-deployment, zonewise-63kpi-reports, etc.) stay local.
```

### Step 9: Verify
```bash
for REPO in zonewise-web zonewise-desktop zonewise-agents; do
  echo "=== $REPO ==="
  for SKILL in agent-browser auction-pipeline build-with-agent-team e2e-test supabase; do
    FILE="$REPO/.claude/skills/$SKILL/SKILL.md"
    if grep -q "canonical monorepo" "$FILE" 2>/dev/null; then
      echo "  ✅ $SKILL → pointer"
    else
      echo "  ❌ $SKILL → still full copy"
    fi
  done
done
```

## RULES
- NEVER delete a skill from the monorepo — it's the source of truth
- ALWAYS diff before replacing — diverged copies need merging first
- Pointer files must contain enough context for Claude Code to know WHEN to use the skill
- Pointer files must contain the curl command to fetch full instructions
- If a skill has files beyond SKILL.md (scripts, templates), those stay in the monorepo only
- Commit to monorepo FIRST if any merging is needed, then update other repos
- Zero human intervention required

## SUCCESS CRITERIA
- [ ] All 5 skills diffed against monorepo canonical versions
- [ ] Any diverged versions merged into monorepo
- [ ] 15 duplicate skill files replaced with pointer SKILL.md files (5 per repo × 3 repos)
- [ ] Each pointer contains: summary, canonical URL, curl fetch command
- [ ] CLAUDE.md updated in all 4 repos
- [ ] All 4 repos pushed to main
- [ ] Verification confirms all pointers in place
