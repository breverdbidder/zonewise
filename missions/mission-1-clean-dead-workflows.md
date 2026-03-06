# MISSION 1: Clean Dead Workflows — zonewise-web

## OBJECTIVE
Delete dead/one-off debugging workflows from `breverdbidder/zonewise-web/.github/workflows/`. Currently 22 workflow files. Target: ≤13 essential workflows.

## CONTEXT
The zonewise-web repo accumulated one-off debugging and fix workflows during Vercel/DNS migration issues. These are dead weight — they waste CI minutes, confuse future Claude Code sessions, and pollute the workflow list.

## EXECUTION PLAN

### Step 1: Clone the repo
```bash
git clone https://github.com/breverdbidder/zonewise-web.git
cd zonewise-web
```

### Step 2: Audit every workflow
Before deleting anything, read each workflow file and classify it. Use this decision matrix:

| Classification | Action | Criteria |
|---------------|--------|----------|
| KEEP | Do not touch | Has `schedule:` cron, is `ci.yml`, is active deployment, or is security/monitoring |
| DELETE | Remove file | One-off debug/fix, duplicate deploy, or references dead infrastructure |
| REVIEW | Read contents first | Ambiguous name — could be active |

### Step 3: Apply this pre-audited classification

**KEEP (13 files) — Do NOT delete:**
| File | Reason |
|------|--------|
| `ci.yml` | Core CI pipeline |
| `deploy.yml` | Primary deployment |
| `deploy-prod.yml` | Production deployment |
| `deploy-loans.yml` | Feature-specific deploy (loans module) |
| `deploy-michael.yml` | Feature-specific deploy (Michael swimming module) |
| `deploy-migration.yml` | Database migration deploy |
| `deploy-onboarding.yml` | Feature-specific deploy (onboarding) |
| `plan-enforcement-agent.yml` | Agentic plan enforcement — shared across repos |
| `react-doctor.yml` | Code health monitoring |
| `security-checks.yml` | Security audit pipeline |
| `upstream-health.yml` | Upstream dependency monitoring |
| `webhook_notify.yml` | Notification infrastructure |

**DELETE (9 files) — One-off debug/fix scripts:**
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

**IMPORTANT:** Before deleting, open each file marked DELETE and verify:
1. It has NO `schedule:` trigger (cron jobs must not be deleted)
2. It is NOT referenced by other workflows via `workflow_call` or `workflow_dispatch`
3. It does NOT contain unique secrets or environment setup that other files depend on

If ANY of these checks fail, move the file to KEEP and note why.

### Step 4: Delete confirmed dead workflows
```bash
# Only after Step 3 verification
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

### Step 5: Update PROJECT_STATE.json
```bash
# Update the workflows_active and workflows_dead_estimate counts
# Read PROJECT_STATE.json, update:
#   "workflows_active": <new count after deletion>,
#   "workflows_dead_estimate": 0,
# Add to recent_decisions:
#   {"date": "YYYY-MM-DD", "decision": "Deleted N dead workflows", "rationale": "..."}
```

### Step 6: Commit and push
```bash
git add -A
git commit -m "chore: delete N dead debug/fix workflows

Removed one-off debugging and fix workflows accumulated during
Vercel/DNS migration. Reduces workflow count from 22 to ~13.

Deleted: dns-debug, fix-deploy, fix-vercel-domains, switch-dns,
vinext-benchmark, vinext-debug, vinext-deploy-fixed,
vinext-fixed-deploy, vinext-inspect, vinext-wrangler-deploy

All remaining workflows verified: no cron triggers removed,
no cross-workflow dependencies broken."

git push origin main
```

### Step 7: Verify
```bash
ls .github/workflows/ | wc -l
# Expected: 12-13 files
# If more than 13, re-audit
```

## RULES
- NEVER delete a workflow that has `schedule:` (cron trigger)
- NEVER delete without reading the file first
- If unsure, KEEP the file
- Commit message must list every deleted file
- Update PROJECT_STATE.json with the change
- Zero human intervention required

## SUCCESS CRITERIA
- [ ] Dead workflows deleted (target: 9-10 files removed)
- [ ] Remaining workflows verified (no broken cross-references)
- [ ] PROJECT_STATE.json updated
- [ ] Single commit pushed to main
- [ ] `ls .github/workflows/ | wc -l` returns ≤13
