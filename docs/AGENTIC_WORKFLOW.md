# Shapira Agentic Workflow v1.0

> Multi-Agent Orchestration: Ariel → Claude AI → Traycer → Claude Code → Greptile → Deploy
> Last updated: 2026-02-09

## Pipeline

```
Ariel (Issue) → Traycer (Plan) → Claude AI (Review) → Claude Code (Execute) → Greptile (QA) → GitHub Actions (Deploy)
```

## Agent Roles

| Agent | Role | Trigger |
|-------|------|---------|
| **Ariel** | Create GitHub Issue with spec, apply `traycer` label | Business need |
| **Traycer** | Auto-decompose into phases, file-level plans | `traycer` label on Issue |
| **Claude AI** | Architecture review, .claude/tasks/ creation | Ariel pastes Traycer plan |
| **Claude Code** | Autonomous coding, testing, PR creation | .claude/tasks/ files |
| **Greptile** | Full-codebase PR review, bug/security detection | PR opened |
| **GitHub Actions** | CI/CD, deploy to Cloudflare/Render | Push to main |

## Traycer Protocol

1. Create Issue with clear spec (what, why, acceptance criteria)
2. Apply label: `traycer`
3. Traycer auto-comments with phased implementation plan
4. Review plan → approve or iterate
5. Hand off to Claude Code for execution

## Claude Code Task Format

Tasks live in `.claude/tasks/` — see TEMPLATE.md.

## Greptile Config

`greptile.json` in repo root defines coding standards enforced on every PR.

## Observability

All agent events logged to Supabase `agent_events` table:
- agent, event_type, tool, repo, tokens_used, issue_number, phase, status, metadata

## Daily Workflow (20 min)

1. **Morning (5 min)**: Check Greptile reviews, merge clean PRs
2. **Issues (5 min)**: Create 1-3 Issues with `traycer` label
3. **Architect (5 min)**: Claude AI reviews Traycer plans, creates tasks
4. **Launch (5 min)**: Point Claude Code at tasks, let it run

## Cost

| Service | Monthly |
|---------|---------|
| Claude Max | $100 |
| Traycer | $0 (free tier) |
| Greptile | $20 |
| GitHub/Supabase/Cloudflare | $0 |
| **Total** | **~$120** |
