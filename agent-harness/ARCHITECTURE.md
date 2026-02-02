# ZoneWise.AI Agent Harness Architecture

## Overview

This document defines the adoption of Cole Medin's "Your Claude Engineer" agent harness pattern for ZoneWise.AI commercial SaaS development. The architecture enables multi-session autonomous development with human-readable progress tracking.

**Repository**: `breverdbidder/zonewise-v2`  
**Deployment**: Vercel or Render  
**Tiers**: Free / $49 / $199 / $999 (Stripe)

---

## Core Innovation: The Meta-Progress Tracker Pattern

### Traditional vs. Agent Harness Approach

| Traditional | Agent Harness (Adopted) |
|-------------|------------------------|
| Store state in JSON files | Linear issues as state machine |
| Parse files to understand progress | Human-readable Kanban board |
| Custom checkpoint logic | Linear history = audit trail |
| Manual status updates | Automated issue transitions |

### Why Linear as State Machine

1. **Human Readable** - Team/stakeholders see real-time progress
2. **Natural Checkpoints** - Each issue update = commit point
3. **Built-in Audit Trail** - Linear tracks all changes
4. **No Custom Infrastructure** - Replace PROJECT_STATE.json complexity

---

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│            (Claude Sonnet 4.5 - High-level reasoning)        │
│                                                              │
│  • Reads current state from Linear                           │
│  • Decides which sub-agent to delegate to                    │
│  • Maintains fresh 200K context per session                  │
│  • Never accumulates full project history                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┬──────────────────┐
           ▼               ▼               ▼                  ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐      ┌──────────┐
    │  LINEAR  │    │  GITHUB  │    │  CODING  │      │  SLACK   │
    │  AGENT   │    │  AGENT   │    │  AGENT   │      │  AGENT   │
    │ (Haiku)  │    │ (Haiku)  │    │ (Sonnet) │      │ (Haiku)  │
    └──────────┘    └──────────┘    └──────────┘      └──────────┘
         │               │               │                  │
         ▼               ▼               ▼                  ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐      ┌──────────┐
    │  Linear  │    │  GitHub  │    │  Vercel  │      │  Slack   │
    │   API    │    │   API    │    │ /Render  │      │   API    │
    └──────────┘    └──────────┘    └──────────┘      └──────────┘
```

### Agent Responsibilities

#### Orchestrator Agent (Claude Sonnet 4.5)
- **Purpose**: High-level reasoning and delegation
- **Context**: Fresh 200K per session (no accumulation)
- **Tools**: Delegation only (no direct API calls)
- **Model**: `claude-sonnet-4-5-20250929`

#### Linear Agent (Claude Haiku 4.5)
- **Purpose**: Task management domain
- **Tools**: ~10-15 Linear-specific MCP tools
- **Operations**: Create/update/transition issues, manage sprints
- **Model**: `claude-haiku-4-5-20251001`

#### GitHub Agent (Claude Haiku 4.5)
- **Purpose**: Version control domain
- **Tools**: ~10-15 GitHub-specific MCP tools
- **Operations**: Create branches, PRs, commits, reviews
- **Model**: `claude-haiku-4-5-20251001`

#### Coding Agent (Claude Sonnet 4.5)
- **Purpose**: Implementation domain
- **Tools**: File system, shell, Playwright tests
- **Operations**: Write code, run tests, fix bugs
- **Model**: `claude-sonnet-4-5-20250929`

#### Slack Agent (Claude Haiku 4.5)
- **Purpose**: Communication domain
- **Tools**: ~5 Slack-specific MCP tools
- **Operations**: Post updates, notify stakeholders
- **Model**: `claude-haiku-4-5-20251001`

---

## Arcade MCP Gateway Integration

### Why Arcade

**Without Arcade:**
- Each service needs custom OAuth implementation
- Token management becomes complex
- Tool definitions must be manually maintained

**With Arcade:**
- Single OAuth flow for all services
- Automatic token refresh
- Tool discovery prevents prompt bloat
- Up to 91+ tools available

### Arcade Tool Categories for ZoneWise

| Category | Tools | Use Case |
|----------|-------|----------|
| Linear | Issues, Projects, Cycles | Task state machine |
| GitHub | Repos, PRs, Actions | Version control |
| Slack | Messages, Channels | Team communication |
| Stripe | Customers, Subscriptions | Billing (future) |
| Supabase | Tables, Functions | Database operations |

### Configuration

```yaml
# arcade-config.yaml
arcade:
  api_key: ${ARCADE_API_KEY}
  enabled_toolkits:
    - linear
    - github
    - slack
    - supabase
  
  # Tool filtering to reduce context
  tool_allowlist:
    linear:
      - createIssue
      - updateIssue
      - getIssue
      - listIssues
      - createCycle
    github:
      - createPullRequest
      - mergePullRequest
      - createBranch
      - getRepository
    slack:
      - postMessage
      - updateMessage
```

---

## App Spec Contract Pattern

### Purpose

The App Spec serves as a **formal contract** between human intent and AI execution:
- Version controllable
- Diffable (track spec changes)
- Parseable (agents reason about dependencies)

### ZoneWise App Spec Template

```json
{
  "project": {
    "name": "ZoneWise.AI",
    "repo": "breverdbidder/zonewise-v2",
    "deployment": "vercel",
    "database": "supabase"
  },
  "stripe": {
    "tiers": [
      {"name": "free", "price": 0, "limits": {"analyses": 5, "exports": 0}},
      {"name": "starter", "price": 49, "limits": {"analyses": 50, "exports": 10}},
      {"name": "pro", "price": 199, "limits": {"analyses": 500, "exports": 100}},
      {"name": "enterprise", "price": 999, "limits": {"analyses": -1, "exports": -1}}
    ]
  },
  "features": [
    {
      "id": "F001",
      "name": "Zoning Polygon Overlay",
      "description": "Display Brevard County zoning polygons on Mapbox map",
      "dependencies": [],
      "acceptance_criteria": [
        "10,092 polygons render correctly",
        "56 zoning codes display in legend",
        "Click polygon shows zoning details"
      ]
    },
    {
      "id": "F002",
      "name": "Parcel Search",
      "description": "Search parcels by address or parcel ID",
      "dependencies": ["F001"],
      "acceptance_criteria": [
        "Search returns results in <500ms",
        "Map zooms to selected parcel",
        "Parcel boundary highlighted"
      ]
    }
  ],
  "tasks": [
    {
      "id": "T001",
      "feature": "F001",
      "title": "Setup Mapbox GL JS integration",
      "dependencies": [],
      "estimated_hours": 2
    },
    {
      "id": "T002",
      "feature": "F001",
      "title": "Fetch zoning polygons from ESRI endpoint",
      "dependencies": ["T001"],
      "estimated_hours": 3
    }
  ]
}
```

---

## Linear Workflow Configuration

### Issue States (ZoneWise Project)

```
┌─────────┐    ┌────────────┐    ┌─────────────┐    ┌──────────┐    ┌────────┐
│ BACKLOG │ -> │ IN_SESSION │ -> │ IN_PROGRESS │ -> │ TESTING  │ -> │  DONE  │
└─────────┘    └────────────┘    └─────────────┘    └──────────┘    └────────┘
                     │                                    │
                     │           ┌──────────┐            │
                     └─────────> │ BLOCKED  │ <──────────┘
                                 └──────────┘
```

### Automation Rules

1. **Session Start**: Move BACKLOG items to IN_SESSION
2. **Code Started**: Auto-transition to IN_PROGRESS
3. **PR Created**: Auto-transition to TESTING
4. **Tests Pass**: Auto-transition to DONE
5. **Tests Fail**: Auto-transition to BLOCKED with failure details

### Labels

| Label | Meaning |
|-------|---------|
| `agent:orchestrator` | Managed by orchestrator |
| `agent:coding` | Assigned to coding agent |
| `priority:critical` | Must complete this session |
| `priority:high` | Should complete this session |
| `priority:normal` | Complete if time allows |
| `blocker` | Requires human intervention |

---

## Session Workflow

### Orchestrator Session Flow

```
1. READ Linear state (current issues, their statuses)
2. IDENTIFY highest priority incomplete tasks
3. DELEGATE to appropriate sub-agent:
   - Code changes -> Coding Agent
   - PR operations -> GitHub Agent
   - Status updates -> Linear Agent
   - Team notifications -> Slack Agent
4. WAIT for sub-agent completion
5. UPDATE Linear with results
6. REPEAT until session budget exhausted or tasks complete
7. POST summary to Slack
```

### Context Window Economics

| Agent | Context per Call | Cost Model |
|-------|-----------------|------------|
| Orchestrator | ~20K (Linear state only) | Per-session fixed |
| Linear Agent | ~10K (single operation) | Per-operation |
| GitHub Agent | ~15K (PR context) | Per-operation |
| Coding Agent | ~100K (file context) | Per-feature |
| Slack Agent | ~5K (message only) | Per-message |

**Total session cost**: Predictable, doesn't grow with project size

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

- [ ] Create Linear workspace and project
- [ ] Configure Arcade MCP gateway
- [ ] Setup orchestrator agent with delegation
- [ ] Create initial app spec for ZoneWise V2

### Phase 2: Sub-Agents (Week 2)

- [ ] Implement Linear Agent with state transitions
- [ ] Implement GitHub Agent with PR workflow
- [ ] Implement Coding Agent with Playwright tests
- [ ] Implement Slack Agent with progress updates

### Phase 3: Automation (Week 3)

- [ ] Configure Linear automation rules
- [ ] Setup GitHub Actions for CI/CD
- [ ] Create session scheduling (cron)
- [ ] Implement checkpoint/resume logic

### Phase 4: Production (Week 4)

- [ ] Deploy to Vercel/Render
- [ ] Configure Stripe integration
- [ ] Launch beta to initial users
- [ ] Monitor and iterate

---

## File Structure

```
zonewise-v2/
├── .github/
│   └── workflows/
│       └── agent-session.yml       # Scheduled agent sessions
├── agents/
│   ├── orchestrator/
│   │   ├── index.ts
│   │   └── prompts/
│   │       └── system.md
│   ├── linear/
│   │   ├── index.ts
│   │   └── tools.ts
│   ├── github/
│   │   ├── index.ts
│   │   └── tools.ts
│   ├── coding/
│   │   ├── index.ts
│   │   └── tools.ts
│   └── slack/
│       ├── index.ts
│       └── tools.ts
├── config/
│   ├── arcade.yaml
│   ├── app-spec.json
│   └── linear-workflow.yaml
├── src/
│   └── ... (ZoneWise application code)
├── tests/
│   └── playwright/
└── docs/
    └── AGENT_HARNESS_ARCHITECTURE.md
```

---

## Cost Optimization

### Model Selection by Agent

| Agent | Model | Cost/1M tokens | Justification |
|-------|-------|----------------|---------------|
| Orchestrator | Sonnet 4.5 | $3/$15 | Needs reasoning |
| Coding | Sonnet 4.5 | $3/$15 | Code quality critical |
| Linear | Haiku 4.5 | $0.25/$1.25 | Simple API calls |
| GitHub | Haiku 4.5 | $0.25/$1.25 | Simple API calls |
| Slack | Haiku 4.5 | $0.25/$1.25 | Simple messages |

### Estimated Monthly Cost

| Component | Sessions/Month | Tokens/Session | Cost |
|-----------|----------------|----------------|------|
| Orchestrator | 30 | 50K | $4.50 |
| Coding | 30 | 200K | $18.00 |
| Linear | 100 | 10K | $0.25 |
| GitHub | 50 | 15K | $0.19 |
| Slack | 30 | 5K | $0.04 |
| **Total** | - | - | **~$23/month** |

*Note: Claude Max subscription makes this essentially free for your usage*

---

## Success Metrics

### Productivity

- [ ] Tasks completed per session
- [ ] Time from spec to deployment
- [ ] Code quality (test coverage, linting)

### Reliability

- [ ] Session completion rate
- [ ] Error recovery success
- [ ] Rollback frequency

### Visibility

- [ ] Stakeholder satisfaction with Linear board
- [ ] Slack update engagement
- [ ] Time to identify blockers

---

## References

- [Your Claude Engineer Repository](https://github.com/coleam00/your-claude-engineer)
- [Archon Project](https://github.com/coleam00/archon)
- [Arcade.dev Platform](https://arcade.dev)
- [Linear API Documentation](https://linear.app/docs/api)
- [Claude Agent SDK](https://docs.anthropic.com/claude/docs)

---

*Document Version: 1.0*  
*Created: 2026-02-01*  
*Author: Claude AI Architect*
