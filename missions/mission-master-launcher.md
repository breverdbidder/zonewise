# ZONEWISE STRUCTURE CLEANUP — Master Mission File
# Claude Code Session Directive
# Date: March 6, 2026 | Owner: Ariel Shapira

## SESSION OVERVIEW
You are executing 3 sequential missions to complete ZoneWise.AI's Claude Code structure compliance. Execute them in order — Mission 3 depends on Mission 2's output.

**Estimated time:** 45-60 minutes total
**Repos touched:** zonewise-web, zonewise-desktop, zonewise-agents, zonewise (monorepo)
**Auth:** Use GitHub token from environment or `gh auth status`

---

## MISSION SEQUENCE

### Mission 1: Clean Dead Workflows (15 min)
**Repo:** `zonewise-web`
**Action:** Delete 9-10 dead debug/fix GitHub Actions workflows
**File:** See `mission-1-clean-dead-workflows.md` for full instructions

**Quick version:**
```bash
cd zonewise-web
# Verify each file has NO cron trigger and NO cross-workflow references, then:
git rm .github/workflows/{dns-debug,fix-deploy,fix-vercel-domains,switch-dns,vinext-benchmark,vinext-debug,vinext-deploy-fixed,vinext-fixed-deploy,vinext-inspect,vinext-wrangler-deploy}.yml
# Update PROJECT_STATE.json workflows_active count
git commit -m "chore: delete 10 dead debug/fix workflows (22→12)"
git push origin main
```

**Verify:** `ls .github/workflows/ | wc -l` → ≤13

---

### Mission 2: Deduplicate Shared Skills (20 min)
**Repos:** `zonewise` (canonical), `zonewise-web`, `zonewise-desktop`, `zonewise-agents`
**Action:** Replace 15 duplicate skill copies with pointer files
**File:** See `mission-2-deduplicate-skills.md` for full instructions

**Quick version:**
1. Diff all 5 shared skills between monorepo and 3 other repos
2. Merge any diverged changes INTO monorepo
3. Replace each copy with a pointer SKILL.md containing: summary + canonical URL + curl fetch command
4. Update CLAUDE.md in all 4 repos
5. Push all 4 repos

**Verify:** `grep -l "canonical monorepo" */. claude/skills/*/SKILL.md` → 15 matches

---

### Mission 3: Update REPO_MAP.md (15 min)
**Repo:** `zonewise` (monorepo)
**Action:** Add scraper-v4, deprecate zonewise-modal, update architecture diagram
**File:** See `mission-3-update-repo-map.md` for full instructions

**Quick version:**
1. Add `zonewise-scraper-v4` as ACTIVE repo #5
2. Move `zonewise-modal` to new LEGACY section
3. Replace architecture diagram (Modal.com → GitHub Actions scraper-v4)
4. Add Claude Code compliance table (45/45)
5. Update skills location map with dedup pointers
6. Push to main

**Verify:** `grep -c "scraper-v4" REPO_MAP.md` → ≥5

---

## EXECUTION RULES

1. **Order matters.** Mission 2 before Mission 3 — the REPO_MAP update references skill deduplication.
2. **Read before delete.** Never delete a workflow or skill without reading it first.
3. **Diff before replace.** Never replace a skill copy without diffing against canonical.
4. **Commit per mission.** One commit per mission, not one giant commit.
5. **Verify after each mission.** Run the verify command before starting the next mission.
6. **Zero human intervention.** If blocked, try 3 alternatives. Log blockers to PROJECT_STATE.json.
7. **Push to main.** All repos deploy from main — no feature branches for cleanup work.

## ABORT CONDITIONS
- If a workflow marked for deletion has a `schedule:` cron trigger → KEEP it, adjust the count
- If a skill copy has diverged significantly from canonical → MERGE first, don't overwrite
- If a git push fails → Check for branch protection, try `git pull --rebase` first
- If >3 failures on any mission → Log to PROJECT_STATE.json and move to next mission

## POST-SESSION CHECKLIST
After all 3 missions complete:
- [ ] zonewise-web: ≤13 workflows remaining
- [ ] zonewise-web/desktop/agents: 5 pointer skills each (15 total)
- [ ] zonewise REPO_MAP.md: updated with scraper-v4, modal deprecated
- [ ] All PROJECT_STATE.json files updated with recent_decisions
- [ ] All pushes verified on GitHub

## LAUNCH COMMAND
```bash
# Start Claude Code with this file as context
claude --dangerously-skip-permissions \
  --context mission-master-launcher.md \
  --context mission-1-clean-dead-workflows.md \
  --context mission-2-deduplicate-skills.md \
  --context mission-3-update-repo-map.md \
  "Execute all 3 missions in order. Start with Mission 1."
```

## ALTERNATIVE: AUTO MODE (After March 12, 2026)
```bash
claude --enable-auto-mode \
  --context mission-master-launcher.md \
  "Execute all 3 ZoneWise cleanup missions sequentially."
```
