# ZoneWise Launch Checklist

> **Target Launch:** Q1 2026 (Week 8)  
> **Status:** 🔴 Pre-Launch  
> **Last Updated:** January 18, 2026

---

## Launch Readiness Score

```
┌─────────────────────────────────────────────────────────────┐
│                   LAUNCH READINESS: 35%                     │
├─────────────────────────────────────────────────────────────┤
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│                                                             │
│ Product: 40%  │  Marketing: 20%  │  Operations: 30%        │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation (Weeks 1-2)

### Data Infrastructure

- [ ] **Replace synthetic data with real ordinances**
  - [ ] Melbourne (25 districts)
  - [ ] Palm Bay (30 districts)
  - [ ] Satellite Beach (8 districts)
  - [ ] Indian Harbour Beach (6 districts)
  - [ ] Remaining 13 jurisdictions
  - **Owner:** Claude Code
  - **Blocker:** Municode JS rendering

- [ ] **Validate extraction accuracy**
  - [ ] Cross-reference 10 properties with manual lookup
  - [ ] Document any parsing failures
  - [ ] Confidence score per jurisdiction
  - **Owner:** Claude AI

- [ ] **Set up ordinance update pipeline**
  - [ ] GitHub Action for weekly scraping
  - [ ] Change detection + alerting
  - [ ] 7-day cache TTL implemented
  - **Owner:** Claude Code

### MCP Server

- [x] **MCP server skeleton deployed** (`src/mcp/zonewise_mcp_server.py`)
- [ ] **All 5 tools functional**
  - [ ] `lookup_zoning` — returns district + dimensions
  - [ ] `check_compliance` — validates proposed development
  - [ ] `list_districts` — returns all districts for jurisdiction
  - [ ] `list_jurisdictions` — returns available jurisdictions
  - [ ] `search_ordinance` — keyword search in ordinance text
  - **Owner:** Claude Code

- [ ] **MCP server deployed to Render**
  - [ ] Production URL active
  - [ ] Health check endpoint
  - [ ] Error logging to Supabase
  - **Owner:** Claude Code

- [ ] **MCP testing complete**
  - [ ] Claude Desktop integration verified
  - [ ] Cursor integration verified
  - [ ] Edge cases documented
  - **Owner:** Claude AI

---

## Phase 2: Beta Testing (Week 3)

### User Recruitment

- [ ] **Identify beta testers**
  - [ ] 5-10 from BidDeed.AI user base
  - [ ] Mix of: investors, developers, architects
  - [ ] Brevard County properties preferred
  - **Owner:** Ariel

- [ ] **Beta invitation sent**
  - [ ] MCP installation instructions
  - [ ] Feedback form link
  - [ ] Discord/Slack channel for support
  - **Owner:** Claude AI

### Beta Monitoring

- [ ] **Usage tracking active**
  - [ ] Query volume by user
  - [ ] Tool invocation breakdown
  - [ ] Error rate monitoring
  - **Owner:** Claude Code

- [ ] **Feedback collection**
  - [ ] Accuracy issues logged
  - [ ] Feature requests captured
  - [ ] NPS survey (end of beta)
  - **Owner:** Claude AI

- [ ] **Iteration cycle**
  - [ ] Daily bug fixes
  - [ ] Weekly feature updates
  - [ ] Beta user communication
  - **Owner:** Claude Code

---

## Phase 3: Marketing Prep (Week 4)

### MCP Marketplace

- [ ] **Claude Desktop submission**
  - [ ] MCP manifest validated
  - [ ] Description optimized (see MARKETING_PLAYBOOK.md)
  - [ ] Screenshots/demo prepared
  - **Owner:** Claude Code

- [ ] **Cursor submission**
  - [ ] MCP manifest validated
  - [ ] Cursor-specific docs created
  - **Owner:** Claude Code

### Landing Page

- [ ] **zonewise.com deployed**
  - [ ] Domain configured (Cloudflare)
  - [ ] Landing page live
  - [ ] MCP installation CTA prominent
  - **Owner:** Claude Code

- [ ] **Landing page content**
  - [ ] Hero: Value prop + demo
  - [ ] Pricing table
  - [ ] FAQ section
  - [ ] Trust signals (accuracy, citations)
  - **Owner:** Claude AI

- [ ] **Analytics configured**
  - [ ] Plausible or Umami installed
  - [ ] Conversion tracking (MCP install clicks)
  - [ ] UTM parameter handling
  - **Owner:** Claude Code

### Documentation

- [ ] **User docs complete**
  - [ ] MCP installation guide
  - [ ] Tool reference (all 5 tools)
  - [ ] Common use cases
  - [ ] Troubleshooting FAQ
  - **Owner:** Claude AI

- [ ] **API docs (if applicable)**
  - [ ] REST endpoint documentation
  - [ ] Authentication guide
  - [ ] Rate limits explained
  - **Owner:** Claude AI

---

## Phase 4: Content Blitz (Weeks 5-6)

### SEO Content

- [ ] **District pages created (189)**
  - [ ] Template finalized
  - [ ] Melbourne districts (25)
  - [ ] Palm Bay districts (30)
  - [ ] All remaining districts
  - **Owner:** Claude Code

- [ ] **Evergreen guides (10)**
  - [ ] "ADU Compliance in Florida"
  - [ ] "Understanding Setback Requirements"
  - [ ] "Brevard County Zoning Overview"
  - [ ] 7 more TBD based on keyword research
  - **Owner:** Claude AI

- [ ] **Pages indexed by Google**
  - [ ] Sitemap submitted
  - [ ] Search Console configured
  - [ ] Initial rankings tracked
  - **Owner:** Claude Code

### Social Presence

- [ ] **LinkedIn company page**
  - [ ] Profile complete
  - [ ] First 5 posts scheduled
  - **Owner:** Claude AI

- [ ] **X/Twitter account**
  - [ ] Profile complete
  - [ ] Launch announcement drafted
  - **Owner:** Claude AI

- [ ] **BiggerPockets presence**
  - [ ] Profile created
  - [ ] First forum responses (helpful, not promotional)
  - **Owner:** Claude AI

---

## Phase 5: Outreach Setup (Week 7)

### AI Outreach Agent

- [ ] **Target list compiled**
  - [ ] Permit applicants (last 90 days)
  - [ ] LinkedIn profiles (RE investors + architects)
  - [ ] BiggerPockets members
  - **Owner:** Claude Code

- [ ] **Email sequences created**
  - [ ] Permit applicant sequence (2 emails)
  - [ ] Investor sequence (2 emails)
  - [ ] Architect sequence (2 emails)
  - **Owner:** Claude AI

- [ ] **LinkedIn sequences created**
  - [ ] Connection request template
  - [ ] Follow-up message template
  - **Owner:** Claude AI

- [ ] **Outreach tooling configured**
  - [ ] Email sending (Loops.so or Resend)
  - [ ] LinkedIn automation (manual initially)
  - [ ] Response tracking
  - **Owner:** Claude Code

---

## Phase 6: Content Flywheel Setup (Week 7)

> 📘 **Full documentation:** [CONTENT_FLYWHEEL.md](./CONTENT_FLYWHEEL.md)

### Flywheel Infrastructure

- [ ] **Deploy Supabase schema**
  - [ ] content_library table
  - [ ] content_distribution table
  - [ ] engagement_metrics table
  - [ ] leads table
  - [ ] conversion_attribution table
  - **Owner:** Claude Code

- [ ] **Build Agent 1 (Content Generation)**
  - [ ] Content templates (4 types)
  - [ ] Smart Router integration (90% FREE)
  - [ ] Test with sample zoning data
  - **Owner:** Claude Code

- [ ] **Build Agent 2 (Distribution)**
  - [ ] LinkedIn API OAuth setup
  - [ ] Twitter API OAuth setup
  - [ ] Resend email integration
  - [ ] GitHub Actions workflow
  - **Owner:** Claude Code

### Flywheel Activation (Post-Launch)

- [ ] **Build Agents 3-5**
  - [ ] Agent 3: Engagement Tracking
  - [ ] Agent 4: Conversion Attribution
  - [ ] Agent 5: Optimization Loop
  - **Owner:** Claude Code
  - **Timeline:** Weeks 9-10

---

## Phase 7: Launch (Week 8)

### Pre-Launch (Day -3 to Day -1)

- [ ] **Final system check**
  - [ ] All MCP tools working
  - [ ] Landing page live
  - [ ] Payment flow tested (Stripe)
  - [ ] Support email configured
  - **Owner:** All

- [ ] **Launch assets ready**
  - [ ] Launch announcement (email, social)
  - [ ] Product Hunt draft (optional)
  - [ ] BiggerPockets post draft
  - **Owner:** Claude AI

- [ ] **Beta users notified**
  - [ ] Thank you + special offer
  - [ ] Ask for testimonials
  - **Owner:** Claude AI

### Launch Day (Day 0)

- [ ] **Announcements published**
  - [ ] LinkedIn post
  - [ ] X/Twitter thread
  - [ ] BiggerPockets post
  - [ ] Email to beta users
  - **Owner:** Claude AI

- [ ] **MCP marketplace live**
  - [ ] Claude Desktop listing active
  - [ ] Cursor listing active
  - **Owner:** Verify

- [ ] **Monitoring active**
  - [ ] Error alerts configured
  - [ ] Query volume dashboard
  - [ ] Social mention tracking
  - **Owner:** Claude Code

### Post-Launch (Day 1-7)

- [ ] **Daily standup**
  - [ ] Query volume review
  - [ ] Error triage
  - [ ] User feedback review
  - **Owner:** Claude AI

- [ ] **Outreach activated**
  - [ ] First batch of emails sent
  - [ ] LinkedIn connections initiated
  - **Owner:** Claude Code

- [ ] **Week 1 retrospective**
  - [ ] Metrics vs. targets
  - [ ] Top issues identified
  - [ ] Week 2 priorities set
  - **Owner:** Claude AI + Ariel

---

## Launch Blockers

### Critical (Must Fix Before Launch)

| Blocker | Status | Owner | ETA |
|---------|--------|-------|-----|
| Synthetic data → Real ordinances | 🔴 Not Started | Claude Code | Week 2 |
| MCP tools functional | 🟡 Partial | Claude Code | Week 2 |
| Landing page | 🔴 Not Started | Claude Code | Week 4 |

### High (Should Fix Before Launch)

| Issue | Status | Owner | ETA |
|-------|--------|-------|-----|
| Stripe integration | 🔴 Not Started | Claude Code | Week 4 |
| User authentication | 🔴 Not Started | Claude Code | Week 3 |
| Usage metering | 🔴 Not Started | Claude Code | Week 3 |

### Medium (Can Launch Without)

| Issue | Status | Owner | ETA |
|-------|--------|-------|-----|
| Full 189 district pages | 🔴 Not Started | Claude Code | Week 6 |
| AI outreach automation | 🔴 Not Started | Claude Code | Week 7 |
| Referral program | 🔴 Not Started | Claude Code | Post-launch |

---

## Launch Criteria

### Go / No-Go Decision

**Must Have (All Required):**
- [ ] Real ordinance data for top 5 jurisdictions (80% of volume)
- [ ] All 5 MCP tools working correctly
- [ ] Landing page with MCP installation CTA
- [ ] Basic error monitoring

**Should Have (3 of 5):**
- [ ] Stripe payment integration
- [ ] User authentication (Supabase Auth)
- [ ] 50+ district pages indexed
- [ ] Beta user testimonials
- [ ] AI outreach ready to activate

**Nice to Have (0 required):**
- [ ] Full 189 district pages
- [ ] Product Hunt launch
- [ ] Referral program
- [ ] Multi-county expansion started

---

## Post-Launch Priorities

### Week 9-10: Stabilization

1. Monitor and fix production issues
2. Respond to user feedback
3. Optimize MCP tool responses
4. Begin county expansion research

### Week 11-12: Growth

1. Activate AI outreach at scale
2. Complete remaining district pages
3. First paid customer acquisition push
4. Q2 planning

---

## Related Documents

- [GTM_STRATEGY.md](./GTM_STRATEGY.md) — Overall strategy
- [CONTENT_FLYWHEEL.md](./CONTENT_FLYWHEEL.md) — **5-Agent autonomous marketing engine**
- [MARKETING_PLAYBOOK.md](./MARKETING_PLAYBOOK.md) — Marketing tactics
- [PRICING.md](./PRICING.md) — Pricing details
- [COMPETITIVE_ANALYSIS.md](./COMPETITIVE_ANALYSIS.md) — Competitive intel

---

*Checklist maintained by Claude AI Architect. Update daily during launch phase.*
