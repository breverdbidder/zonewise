# ZoneWise 12-Week Execution Plan

**Version:** 1.0  
**Date:** January 25, 2026  
**Owner:** Ariel Shapira + Claude AI Team

---

## Overview

This plan takes ZoneWise from 6.8% Brevard coverage to **67-county Florida MVP** with a Claude AI-style split-screen interface.

### Current State
- Malabar POC: 100% stable (1,430 parcels)
- Brevard parcels: 351,423
- Zone coverage: 24,243 (6.8%)
- Jurisdictions: 17 Brevard

### Target State
- Florida counties: 67
- Zone coverage: 95%+
- UI: Split-screen chat + artifacts
- Status: **MVP LIVE**

---

## Team Structure

| Role | Entity | Weekly Hours | Responsibility |
|------|--------|--------------|----------------|
| Product Owner | Ariel Shapira | ~2.5 hrs (20 min/day) | Approve, unblock, strategic |
| AI Architect | Claude AI (Sonnet 4.5) | ~10 hrs | Design, plan, review |
| Agentic Engineer | Claude Code | ~21 hrs (3x 7-hr sessions) | Build, test, deploy |
| Code Analyst | Greptile | ~1 hr | Pre-session gap analysis |

---

## Weekly Rhythm

```
┌─────────────────────────────────────────────────────────────┐
│                    WEEKLY EXECUTION CYCLE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SUNDAY                                                      │
│  ├── Greptile: Query PRD gaps, get file-level tasks         │
│  ├── Claude AI: Review week, plan Claude Code session        │
│  └── Prepare: Session prompt engineering                     │
│                                                              │
│  MONDAY - THURSDAY                                           │
│  ├── Claude Code: 7-hour autonomous sessions                 │
│  ├── Focus: Data scraping + enrichment                       │
│  └── Output: Counties/features completed                     │
│                                                              │
│  FRIDAY                                                      │
│  ├── Ariel: 20-minute review                                 │
│  ├── Approve/redirect for next week                          │
│  └── Shabbat prep (finish 1hr before candles)               │
│                                                              │
│  SATURDAY - SUNDAY                                           │
│  ├── Modal.com: Nightly jobs run                             │
│  ├── Data accumulates automatically                          │
│  └── Ready for Monday                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Data Scaling (Weeks 1-6)

### Week 1-2: Brevard 100%

**Objective:** Complete zone assignment for all 351,423 Brevard parcels

#### Week 1: Major Jurisdictions

| Day | Task | Parcels | Owner |
|-----|------|---------|-------|
| Sun | Greptile audit, identify GIS gaps | - | Claude AI |
| Mon | Unincorporated Brevard | 75,350 | Claude Code |
| Tue | Palm Bay (recover from 503) | 78,697 | Claude Code |
| Wed | Melbourne | 62,135 | Claude Code |
| Thu | Titusville + Cocoa | 50,000 | Claude Code |
| Fri | Review, fix errors | - | Claude AI |

#### Week 2: Remaining Jurisdictions

| Day | Task | Parcels | Owner |
|-----|------|---------|-------|
| Sun | Plan remaining 12 jurisdictions | - | Claude AI |
| Mon | Rockledge, Satellite Beach, IHB | 15,000 | Claude Code |
| Tue | West Melbourne, Melbourne Beach | 12,000 | Claude Code |
| Wed | Cape Canaveral, Cocoa Beach | 8,000 | Claude Code |
| Thu | Palm Shores, Indialantic, Melbourne Village | 5,000 | Claude Code |
| Fri | Grant-Valkaria, Mims, validation | 5,000 | Claude Code |

**Exit Criteria:**
- [ ] 351,423 parcels in parcel_zones table
- [ ] 100% zone coverage
- [ ] All 17 jurisdictions complete
- [ ] Data quality validated

### Week 3-4: Modal.com Production

**Objective:** Deploy parallel compute for 67 counties

#### Week 3: Modal Setup

| Day | Task | Owner | Output |
|-----|------|-------|--------|
| Sun | Sign up Modal.com | Ariel (5 min) | Account active |
| Sun | Create zonewise-secrets | Ariel (2 min) | Credentials stored |
| Mon | Deploy Modal app from repo | Claude Code | App running |
| Tue | Test Brevard refresh | Claude Code | Verified |
| Wed | Add Orange County | Claude Code | 2nd county |
| Thu | Add Hillsborough County | Claude Code | 3rd county |
| Fri | Monitor, fix issues | Claude AI | Stable |

#### Week 4: Scale to 10 Counties

| Day | Task | Owner | Output |
|-----|------|-------|--------|
| Sun | Plan Tier 1 counties | Claude AI | Municode URLs |
| Mon | Miami-Dade, Broward | Claude Code | 2 counties |
| Tue | Palm Beach, Duval | Claude Code | 2 counties |
| Wed | Pinellas, Polk | Claude Code | 2 counties |
| Thu | Configure nightly cron | Claude Code | 11 PM EST |
| Fri | Verify all 10 running | Claude AI | Dashboard |

**Exit Criteria:**
- [ ] Modal.com account active
- [ ] 10 counties in parallel pipeline
- [ ] Nightly cron running at 11 PM EST
- [ ] Supabase writes verified

### Week 5-6: Complete Tier 1 & 2

**Objective:** Expand to 30+ counties

#### Week 5: Tier 2 Counties

| County | FIPS | Population | Municode |
|--------|------|------------|----------|
| Lee | 12071 | 822,779 | ✅ |
| Volusia | 12127 | 553,284 | ✅ |
| Seminole | 12117 | 480,587 | ✅ |
| Pasco | 12101 | 589,199 | ✅ |
| Sarasota | 12115 | 434,006 | ✅ |
| Manatee | 12081 | 403,253 | ✅ |
| Collier | 12021 | 393,973 | ✅ |

#### Week 6: Remaining Counties

- Add remaining 37 counties to pipeline
- Focus on Municode-available jurisdictions first
- Skip non-Municode counties for now (manual later)

**Exit Criteria:**
- [ ] 67 counties configured in Modal
- [ ] 50+ counties actively scraping
- [ ] Data quality >90% on Tier 1

---

## Phase 2: Infrastructure Hardening (Weeks 7-8)

### Week 7: Code Quality

| Task | Owner | Tool | Output |
|------|-------|------|--------|
| Codebase audit | Claude AI | Greptile | Issue list |
| Remove dead code | Claude Code | - | Clean repo |
| Refactor duplicates | Claude Code | - | DRY code |
| Add error handling | Claude Code | - | Robust |
| Improve logging | Claude Code | - | Observable |

### Week 8: Testing & Documentation

| Task | Owner | Output |
|------|-------|--------|
| Unit tests (>80% coverage) | Claude Code | pytest passing |
| Integration tests | Claude Code | E2E verified |
| API documentation | Claude AI | OpenAPI spec |
| Deployment guide | Claude AI | README updated |
| Architecture diagrams | Claude AI | Mermaid files |

**Exit Criteria:**
- [ ] Test coverage >80%
- [ ] All tests passing
- [ ] Documentation complete
- [ ] No critical Greptile issues

---

## Phase 3: UI + MVP (Weeks 9-12)

### Week 9: Frontend Foundation

**Objective:** Fork Open-claude, add Supabase + LiteLLM

| Day | Task | Files | Output |
|-----|------|-------|--------|
| Sun | Fork Open-claude repo | - | Local clone |
| Mon | Add Supabase client | `src/lib/supabase.js` | Auth working |
| Tue | Replace LLM factory | `src/lib/litellm.js` | AI responses |
| Wed | Connect ZoneWise data | `src/hooks/useZoning.js` | Queries work |
| Thu | Basic chat flow | - | E2E test |
| Fri | Deploy Cloudflare | - | Live URL |

**Key Files to Create:**
```
src/
├── lib/
│   ├── supabase.js          # Supabase client
│   ├── litellm.js           # LLM routing
│   └── langgraph.js         # Agent orchestration
├── hooks/
│   ├── useZoning.js         # Zoning queries
│   ├── useParcel.js         # Parcel lookups
│   └── useReport.js         # Report generation
└── config/
    └── agents.js            # Agent definitions
```

### Week 10: AI Integration

**Objective:** LangGraph agents + Smart Router

| Day | Task | Agent | Capability |
|-----|------|-------|------------|
| Sun | Agent scaffold | - | Base structure |
| Mon | Zoning Agent | zoning_agent | "What's the zoning for 123 Main St?" |
| Tue | Parcel Agent | parcel_agent | "Show me details for parcel X" |
| Wed | Report Agent | report_agent | "Generate zoning report PDF" |
| Thu | Smart Router | - | Cost optimization |
| Fri | Streaming | - | Real-time responses |

**Agent Definitions:**
```javascript
const agents = {
  zoning_agent: {
    name: "Zoning Agent",
    description: "Answers zoning questions",
    tools: ["query_zoning_districts", "query_dimensional_standards"],
    model: "gemini/gemini-2.5-flash" // FREE tier
  },
  parcel_agent: {
    name: "Parcel Agent", 
    description: "Looks up property information",
    tools: ["query_bcpao", "query_sample_properties"],
    model: "gemini/gemini-2.5-flash" // FREE tier
  },
  report_agent: {
    name: "Report Agent",
    description: "Generates PDF/DOCX reports",
    tools: ["generate_pdf", "generate_docx"],
    model: "anthropic/claude-sonnet-4-5" // QUALITY tier
  }
};
```

### Week 11: Artifacts

**Objective:** Build real estate-specific artifact components

| Day | Component | Features |
|-----|-----------|----------|
| Sun | ZoningReport.jsx | 20-phase display, dimensional table |
| Mon | ParcelMap.jsx | Leaflet, boundary overlay, nearby parcels |
| Tue | PropertyCard.jsx | Owner, value, sales history, photo |
| Wed | AuctionAnalysis.jsx | Max bid calc, liens, judgment ratio |
| Thu | PDF export | Download button, watermark |
| Fri | Polish | Transitions, loading states |

**Component Structure:**
```jsx
// ZoningReport.jsx
const ZoningReport = ({ parcelId }) => {
  const { data } = useZoning(parcelId);
  
  return (
    <div className="artifact-panel">
      <h2>20-Phase Zoning Analysis</h2>
      <PhaseList phases={data.phases} />
      <DimensionalTable standards={data.dimensional} />
      <PermittedUses uses={data.permitted} />
      <DownloadPDF data={data} />
    </div>
  );
};
```

### Week 12: Launch

**Objective:** Polish, test, deploy MVP

| Day | Task | Output |
|-----|------|--------|
| Sun | Bug bash | Issue list |
| Mon | Performance (<2s response) | Optimized |
| Tue | Mobile responsive | Works on phone |
| Wed | Error handling | User-friendly messages |
| Thu | 10 user scenarios test | All passing |
| Fri | **MVP LAUNCH** | 🚀 LIVE |

**Launch Checklist:**
- [ ] All Tier 1 features working
- [ ] Performance <2s for queries
- [ ] Mobile responsive
- [ ] Error handling graceful
- [ ] Monitoring active
- [ ] Backup running
- [ ] Domain configured
- [ ] SSL active

---

## Success Metrics

### Data Metrics (Weeks 1-8)

| Metric | Week 2 | Week 4 | Week 6 | Week 8 |
|--------|--------|--------|--------|--------|
| Brevard coverage | 100% | 100% | 100% | 100% |
| Counties in pipeline | 1 | 10 | 50 | 67 |
| Total parcels | 351K | 1M | 3M | 5M+ |
| Zone accuracy | 95% | 95% | 95% | 95% |

### UI Metrics (Weeks 9-12)

| Metric | Week 9 | Week 10 | Week 11 | Week 12 |
|--------|--------|---------|---------|---------|
| Pages working | 1 | 3 | 5 | All |
| Agents active | 0 | 3 | 3 | 3 |
| Artifacts | 0 | 1 | 4 | 5 |
| Response time | - | 5s | 3s | <2s |

---

## Risk Mitigation

| Risk | Mitigation | Owner |
|------|------------|-------|
| GIS API failures | Multiple endpoint catalog | Claude Code |
| Modal outage | GitHub Actions fallback | Claude AI |
| LLM costs spike | Smart Router caps | Claude AI |
| Solo founder burnout | Strict 20 min/day | Ariel |
| Scope creep | This document is law | Claude AI |

---

## Checkpoints

| Checkpoint | Date | Criteria |
|------------|------|----------|
| Brevard 100% | Week 2 end | 351K parcels zoned |
| Modal Production | Week 4 end | Nightly cron running |
| 67 Counties | Week 6 end | All configured |
| Code Quality | Week 8 end | >80% test coverage |
| UI Foundation | Week 9 end | Chat working |
| AI Agents | Week 10 end | 3 agents active |
| Artifacts | Week 11 end | 5 components |
| **MVP LAUNCH** | Week 12 end | 🚀 LIVE |

---

## Appendix: Claude Code Session Template

```markdown
# CLAUDE CODE MISSION: [SPECIFIC TASK]

## OBJECTIVE
[Clear, measurable goal]

## CONTEXT
- Current state: [X]
- Target state: [Y]
- Time budget: 7 hours

## CREDENTIALS
- Supabase URL: [SUPABASE_URL from GitHub Secrets]
- Supabase Key: [SERVICE_ROLE_KEY from GitHub Secrets]
- GitHub Token: [GITHUB_TOKEN from GitHub Secrets]

## TASKS
1. [Task 1]
2. [Task 2]
3. [Task 3]

## EXIT CRITERIA
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## RULES
- Execute autonomously, don't ask permission
- Commit frequently with descriptive messages
- Run tests before pushing
- Update PROJECT_STATE.json when done
- Only escalate if blocked after 3 attempts
```

---

*This plan is the single source of truth for ZoneWise execution. Follow it.*
