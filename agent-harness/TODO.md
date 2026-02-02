# ZoneWise.AI Agent Harness Adoption TODO

**Project**: Agent Harness Pattern Adoption  
**Status**: In Progress  
**Started**: 2026-02-01  
**Target Completion**: 2026-02-28

---

## Phase 1: Foundation (Week 1) - Feb 1-7

### Infrastructure Setup
- [ ] Create Linear workspace "zonewise"
- [ ] Create Linear project from app-spec.json
- [ ] Sign up for Arcade.dev account
- [ ] Configure Arcade OAuth connections
  - [ ] Linear OAuth
  - [ ] GitHub OAuth (already have PAT)
  - [ ] Slack OAuth
- [ ] Create Slack workspace channel #zonewise-ai-updates

### Repository Setup
- [ ] Push ZONEWISE_AGENT_HARNESS_ARCHITECTURE.md to zonewise-v2 repo
- [ ] Push app-spec.json to zonewise-v2 repo
- [ ] Create `/agents` directory structure
- [ ] Create `/config` directory with arcade.yaml

---

## Phase 2: Sub-Agents (Week 2) - Feb 8-14

### Linear Agent
- [ ] Create `agents/linear/index.ts`
- [ ] Implement Linear MCP tool wrappers
- [ ] Test issue creation from app-spec tasks
- [ ] Test state transitions
- [ ] Add error handling and retry logic

### GitHub Agent  
- [ ] Create `agents/github/index.ts`
- [ ] Implement PR creation workflow
- [ ] Implement branch management
- [ ] Test commit operations
- [ ] Add merge conflict detection

### Coding Agent
- [ ] Create `agents/coding/index.ts`
- [ ] Configure file system tools
- [ ] Setup Playwright for testing
- [ ] Implement code review self-check
- [ ] Add lint/format automation

### Slack Agent
- [ ] Create `agents/slack/index.ts`
- [ ] Implement progress update templates
- [ ] Configure notification channels
- [ ] Add summary generation
- [ ] Test message formatting

---

## Phase 3: Orchestrator (Week 3) - Feb 15-21

### Core Logic
- [ ] Create `agents/orchestrator/index.ts`
- [ ] Implement Linear state reader
- [ ] Create delegation decision tree
- [ ] Add session budget management
- [ ] Implement checkpoint logic

### Prompts
- [ ] Create `agents/orchestrator/prompts/system.md`
- [ ] Define delegation rules
- [ ] Create task prioritization logic
- [ ] Add error recovery instructions

### Integration
- [ ] Connect orchestrator to sub-agents
- [ ] Test full delegation flow
- [ ] Implement response aggregation
- [ ] Add Slack summary posting

---

## Phase 4: Automation (Week 4) - Feb 22-28

### GitHub Actions
- [ ] Create `.github/workflows/agent-session.yml`
- [ ] Configure schedule (daily at 11 PM EST)
- [ ] Add manual trigger option
- [ ] Implement session timeout handling

### Linear Automation
- [ ] Configure auto-transition rules
- [ ] Setup label automation
- [ ] Create cycle/sprint templates
- [ ] Add blocker notifications

### Monitoring
- [ ] Create session metrics dashboard
- [ ] Add cost tracking
- [ ] Implement error alerting
- [ ] Setup Supabase logging

---

## Dependencies & Credentials

### Required Accounts
- [ ] Arcade.dev account
- [ ] Linear workspace
- [ ] Slack workspace (optional, can use existing)

### Required Secrets (GitHub)
- [ ] `ARCADE_API_KEY` - Arcade gateway key
- [ ] `LINEAR_API_KEY` - Linear access token
- [ ] `SLACK_BOT_TOKEN` - Slack bot token
- [ ] `ANTHROPIC_API_KEY` - Already exists

### Existing Secrets (Verified)
- [x] `GITHUB_PAT` - GitHub Personal Access Token
- [x] `SUPABASE_URL` - mocerqjnksmhcjzxrewo.supabase.co
- [x] `SUPABASE_ANON_KEY` - Exists
- [x] `MAPBOX_TOKEN` - pk.eyJ1IjoiZXZlcmVzdDE4...

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tasks completed per session | 5+ | Linear issue count |
| Session completion rate | 95% | Actions success rate |
| Time from spec to deploy | <2 weeks | Git history |
| Test coverage | 80% | Playwright reports |
| Human intervention | <10% | Manual issue count |

---

## Notes

- Start with manual Linear setup before automation
- Test each sub-agent independently before orchestrator
- Use Haiku for simple agents, Sonnet for coding
- Keep context fresh - don't accumulate history
- Checkpoint to Linear, not custom files

---

*Last Updated: 2026-02-01*
