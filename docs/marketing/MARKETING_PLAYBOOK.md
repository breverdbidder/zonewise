# ZoneWise Marketing Playbook

> **Version:** 1.0 | **Last Updated:** January 18, 2026  
> **Owner:** AI Marketing Agent (Autonomous)

---

## Marketing Philosophy

Following Lemkin's AI sales transformation model, ZoneWise marketing operates with:

- **Zero human marketers** — AI generates all content
- **MCP-first distribution** — Let users discover via AI assistants
- **Value demonstration over persuasion** — Show, don't tell

---

## Channel Strategy

### 1. MCP Marketplace (Primary - 40% of Acquisition)

**Goal:** Be the default zoning tool when developers ask Claude/Cursor about zoning.

#### Actions

| Action | Timeline | Owner |
|--------|----------|-------|
| Submit to Claude Desktop MCP Registry | Week 4 | Claude Code |
| Submit to Cursor MCP Directory | Week 4 | Claude Code |
| Create MCP installation docs | Week 3 | Claude AI |
| Monitor registry rankings | Weekly | Automated |

#### MCP Tool Descriptions (SEO-Optimized)

```json
{
  "name": "zonewise",
  "description": "Real-time Florida zoning compliance. Check setbacks, lot coverage, building height, and allowed uses for any parcel in Brevard County. Expand to 67 FL counties in 2026.",
  "tools": [
    {
      "name": "lookup_zoning",
      "description": "Get zoning district, dimensional requirements, and allowed uses for a Florida parcel"
    },
    {
      "name": "check_compliance",
      "description": "Verify if a proposed development complies with local zoning ordinances"
    },
    {
      "name": "search_ordinance",
      "description": "Search municipal zoning codes for specific requirements"
    }
  ]
}
```

#### Success Metrics

- Installs: 100 (Q1), 500 (Q2)
- Tool invocations: 1,000/mo (Q1), 5,000/mo (Q2)
- MCP registry ranking: Top 10 in "real estate" category

---

### 2. Content SEO (30% of Acquisition)

**Goal:** Rank for "[jurisdiction] zoning requirements" and "[district] setback rules."

#### Content Architecture

```
zonewise.com/
├── /zoning/brevard/                    ← County hub
│   ├── /melbourne/                     ← City pages (17)
│   │   ├── /r-1/                       ← District pages (189)
│   │   ├── /r-2/
│   │   └── ...
│   └── /satellite-beach/
├── /guides/
│   ├── /adu-compliance-florida/        ← Evergreen guides
│   ├── /setback-requirements-explained/
│   └── /variance-process-brevard/
└── /tools/
    └── /zoning-lookup/                 ← Free tool (lead gen)
```

#### Content Templates

**District Page Template (189 pages):**

```markdown
# [District Code] Zoning - [City], FL

## Quick Facts
- **District:** [Code] - [Name]
- **Jurisdiction:** [City], Brevard County
- **Primary Use:** [Residential/Commercial/Industrial]

## Dimensional Requirements

| Requirement | Value |
|-------------|-------|
| Min Lot Size | [X] sq ft |
| Min Lot Width | [X] ft |
| Front Setback | [X] ft |
| Side Setback | [X] ft |
| Rear Setback | [X] ft |
| Max Height | [X] ft |
| Max Lot Coverage | [X]% |

## Allowed Uses
[List from ordinance]

## Conditional Uses
[List requiring special approval]

## Common Questions

### Can I build an ADU in [District]?
[AI-generated answer based on ordinance]

### What's the variance process?
[Link to city variance procedures]

---

*Data sourced from [City] Municipal Code, Chapter [X]. Last verified: [Date].*
*Need instant compliance checks? [Try ZoneWise MCP →](link)*
```

#### Content Production Schedule

| Week | Content | Volume |
|------|---------|--------|
| 5 | Melbourne districts | 25 pages |
| 5 | Palm Bay districts | 30 pages |
| 6 | Satellite Beach + IHB | 20 pages |
| 6 | Remaining cities | 50 pages |
| 7 | Evergreen guides | 10 pages |
| 8 | Tool landing pages | 5 pages |

**Total: 140 pages in 4 weeks** (AI-generated, human-reviewed)

#### SEO Targets

| Keyword | Monthly Volume | Difficulty | Target Rank |
|---------|---------------|------------|-------------|
| brevard county zoning | 320 | Low | #1-3 |
| melbourne fl zoning map | 210 | Low | #1-3 |
| satellite beach setback requirements | 40 | Very Low | #1 |
| florida adu zoning laws | 880 | Medium | #5-10 |
| [district] zoning [city] fl | Long-tail | Very Low | #1 |

---

### 3. AI Outreach Agent (20% of Acquisition)

**Goal:** Replace SDR function with automated, personalized outreach.

#### Target Lists

**Source 1: Permit Applicants**
- Scrape public permit records from Brevard County
- Filter: New construction, ADU, commercial permits
- Trigger: Within 7 days of permit application

**Source 2: Real Estate Investors**
- LinkedIn: "Real Estate Investor" + "Brevard County"
- BiggerPockets: Space Coast REI group members
- Foreclosure auction bidders (from BidDeed.AI)

**Source 3: Architects/Engineers**
- AIA Florida membership (public)
- LinkedIn: "Architect" + Florida
- Firms with <50 employees (decision-makers accessible)

#### Outreach Sequences

**Sequence A: Permit Applicant**

```
Day 0 (Email):
Subject: Your [permit type] at [address] - quick zoning check

Hey [First Name],

Noticed you just filed for [permit type] at [address]. 

Before you get too far into plans, have you verified the [key zoning requirement]? 

I built a tool that checks this instantly - takes 10 seconds: [link]

No signup needed for first query.

-ZoneWise Bot

---

Day 3 (Follow-up if no click):
Subject: Re: [address] zoning

Quick follow-up - the [district] district at [address] has a [specific requirement] that catches a lot of people.

Worth a 10-second check: [link]
```

**Sequence B: Real Estate Investor**

```
Day 0 (LinkedIn):
Hi [First Name] - saw you're active in Brevard County real estate.

I'm curious: how do you currently check zoning before bidding on properties?

Built an AI tool that does instant compliance checks. Would love your feedback if you have 2 min to try it.

---

Day 5 (if connected, no response):
No worries if you're slammed. 

Left a free tool here if useful: zonewise.com/tools/zoning-lookup

Works for any Brevard County parcel.
```

#### Outreach Volume Targets

| Week | Emails | LinkedIn | Total |
|------|--------|----------|-------|
| 7 | 100 | 50 | 150 |
| 8 | 200 | 100 | 300 |
| 9+ | 300 | 150 | 450/week |

**Expected Conversion:**
- Email open rate: 40%
- Click rate: 8%
- Tool usage: 50% of clicks
- Free → Paid: 10%

**Pipeline:** 450 outreach → 180 opens → 14 clicks → 7 tool users → 0.7 paid/week

---

### 4. Community/PLG (10% of Acquisition)

**Goal:** Create viral loop through free tier and community presence.

#### Free Tier Strategy

```
┌─────────────────────────────────────────┐
│           FREE TIER (Viral Loop)        │
├─────────────────────────────────────────┤
│ • 10 queries/month                      │
│ • All MCP tools available               │
│ • No credit card required               │
│ • "Powered by ZoneWise" watermark       │
├─────────────────────────────────────────┤
│ Upgrade Triggers:                       │
│ • Query 8: "3 queries remaining"        │
│ • Query 10: "Upgrade for unlimited"     │
│ • Query 11: Hard block + upgrade CTA    │
└─────────────────────────────────────────┘
```

#### Community Presence

| Platform | Strategy | Frequency |
|----------|----------|-----------|
| BiggerPockets | Answer zoning questions, link tool | 3x/week |
| Reddit r/realestateinvesting | Helpful comments, no spam | 2x/week |
| LinkedIn | Zoning tips, case studies | Daily |
| X/Twitter | Florida zoning news, tool updates | Daily |

#### Referral Program (Post-Launch)

```
┌─────────────────────────────────────────┐
│           REFERRAL MECHANICS            │
├─────────────────────────────────────────┤
│ Referrer: +20 free queries/referral     │
│ Referee: 30-day free Pro trial          │
│ Tracking: Unique referral links         │
│ Payout: At referee's first paid month   │
└─────────────────────────────────────────┘
```

---

## Brand Guidelines

### Voice & Tone

| Attribute | Description |
|-----------|-------------|
| **Expert** | Speaks with authority on zoning matters |
| **Efficient** | Values user's time, no fluff |
| **Direct** | Gets to the point, action-oriented |
| **Helpful** | Genuinely wants to solve problems |

**Do:** "The R-1 district requires 25ft front setback. Your proposed 20ft won't comply."  
**Don't:** "We're so excited to help you with your zoning journey! Let's explore together..."

### Visual Identity

| Element | Specification |
|---------|---------------|
| Primary Color | #1E3A5F (Navy) |
| Accent Color | #E3F2FD (Light Blue) |
| Success | #E8F5E9 (Green) |
| Warning | #FFF3E0 (Orange) |
| Error | #FFEBEE (Red) |
| Font | Inter (headings), System (body) |

### Messaging Framework

**Tagline Options:**
1. "Zoning compliance in seconds, not weeks."
2. "AI-powered zoning. Zero guesswork."
3. "Ask your AI assistant about zoning. We'll answer."

**Value Props (Priority Order):**
1. **Speed:** Instant answers vs. days of research
2. **Accuracy:** Real ordinance data, not generic AI
3. **Integration:** Works inside your existing AI workflow
4. **Cost:** Fraction of consultant fees

---

## Campaign Calendar

### Pre-Launch (Weeks 1-4)

| Week | Campaign | Channel | Goal |
|------|----------|---------|------|
| 1 | "Building in public" thread | X/Twitter | Awareness |
| 2 | Beta waitlist | Landing page | 50 signups |
| 3 | Beta invites | Email | 10 active testers |
| 4 | MCP registry submission | Claude/Cursor | Visibility |

### Launch (Weeks 5-8)

| Week | Campaign | Channel | Goal |
|------|----------|---------|------|
| 5 | District pages live | SEO | Index 50+ pages |
| 6 | "Free zoning check" promo | LinkedIn/BP | 100 tool uses |
| 7 | AI outreach activation | Email/LinkedIn | 150 touches |
| 8 | Launch announcement | All channels | 50 MCP installs |

### Post-Launch (Weeks 9+)

| Cadence | Activity | Owner |
|---------|----------|-------|
| Daily | Social posts (AI-generated) | Automated |
| Weekly | Community engagement | AI Agent |
| Weekly | Outreach sequences | AI Agent |
| Monthly | SEO content refresh | Claude Code |
| Monthly | Performance review | Ariel (30 min) |

---

## Measurement & Analytics

### Tracking Stack

```
┌─────────────────────────────────────────┐
│            ANALYTICS STACK              │
├─────────────────────────────────────────┤
│ Website: Plausible (privacy-first)      │
│ MCP: Custom Supabase events             │
│ Email: Loops.so or Resend               │
│ Attribution: UTM + first-touch          │
└─────────────────────────────────────────┘
```

### KPI Dashboard

| Metric | Source | Frequency |
|--------|--------|-----------|
| MCP installs | Registry API | Daily |
| Queries/day | Supabase | Real-time |
| Website traffic | Plausible | Daily |
| Email open rate | Loops | Per campaign |
| Conversion rate | Supabase | Weekly |
| MRR | Stripe | Real-time |

### Attribution Model

```
First Touch Attribution:
├── MCP Marketplace → organic_mcp
├── Google Search → organic_seo
├── LinkedIn → outreach_linkedin
├── Email → outreach_email
├── Referral → referral_{user_id}
└── Direct → direct
```

---

## Budget Allocation

### Q1 2026 Marketing Budget: $0

All marketing is AI-generated and distributed through free channels:

| Activity | Cost | Notes |
|----------|------|-------|
| Content creation | $0 | Claude AI |
| SEO tools | $0 | Google Search Console |
| Email platform | $0 | Free tier (< 1K contacts) |
| Social scheduling | $0 | Manual or Buffer free |
| Analytics | $0 | Plausible free tier |

### Q2 2026 Potential Spend

| Activity | Budget | Trigger |
|----------|--------|---------|
| LinkedIn Ads | $500/mo | If organic < 100 installs |
| Content upgrade | $200/mo | If SEO stalls |
| Email platform | $50/mo | If > 1K contacts |

---

## Competitive Response Plan

### If Competitor Enters

**Scenario A: Generic AI tool adds zoning**
- Response: Emphasize accuracy (real data vs. training cutoff)
- Action: Case study showing ZoneWise accuracy vs. competitor

**Scenario B: Funded startup launches**
- Response: Move faster on multi-county expansion
- Action: Accelerate to 67 FL counties, create switching costs

**Scenario C: Incumbent (CoStar/PropertyShark) adds AI**
- Response: Emphasize MCP-native, developer-friendly
- Action: Double down on community, open-source components

---

## Related Documents

- [GTM_STRATEGY.md](./GTM_STRATEGY.md) — Overall go-to-market strategy
- [PRICING.md](./PRICING.md) — Pricing strategy and tiers
- [COMPETITIVE_ANALYSIS.md](./COMPETITIVE_ANALYSIS.md) — Competitive landscape
- [LAUNCH_CHECKLIST.md](./LAUNCH_CHECKLIST.md) — Launch requirements

---

*Playbook maintained by Claude AI Architect. Updates automated via GitHub Actions.*
