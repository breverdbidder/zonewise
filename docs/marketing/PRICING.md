# ZoneWise Pricing Strategy

> **Version:** 1.0 | **Last Updated:** January 18, 2026  
> **Status:** Pre-Launch Pricing

---

## Pricing Philosophy

### Price Against Alternatives, Not Costs

ZoneWise prices against what customers **currently pay**, not what it costs to serve them:

| Alternative | Cost | Time |
|-------------|------|------|
| Zoning Consultant | $150-500/hour | 2-5 days |
| DIY Research | Free | 4-8 hours |
| Trial & Error (permits) | $500-2,000 (resubmissions) | Weeks |
| ZoneWise | **$0.99-2.99/query** | **Seconds** |

**Key Insight:** A single consultant hour ($150-500) = 50-500 ZoneWise queries.

---

## Pricing Tiers

### Tier Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        ZONEWISE PRICING                         │
├────────────┬──────────┬────────────┬────────────┬──────────────┤
│    FREE    │   PRO    │    TEAM    │ ENTERPRISE │   API-ONLY   │
├────────────┼──────────┼────────────┼────────────┼──────────────┤
│   $0/mo    │  $99/mo  │  $299/mo   │  Custom    │  Pay-as-go   │
├────────────┼──────────┼────────────┼────────────┼──────────────┤
│ 10 queries │   100    │    500     │ Unlimited  │ $0.50/query  │
│  /month    │ /month   │  /month    │            │              │
└────────────┴──────────┴────────────┴────────────┴──────────────┘
```

### Tier Details

#### FREE ($0/month)

**Target:** Solo investors, tire-kickers, viral acquisition

| Feature | Included |
|---------|----------|
| Queries | 10/month |
| MCP Tools | All 5 tools |
| Jurisdictions | Brevard County |
| Support | Community only |
| Branding | "Powered by ZoneWise" |

**Conversion Goal:** 10% → Pro within 60 days

---

#### PRO ($99/month)

**Target:** Active investors, small developers, individual architects

| Feature | Included |
|---------|----------|
| Queries | 100/month |
| MCP Tools | All 5 tools |
| Jurisdictions | All available (Brevard + expansion) |
| Support | Email (48hr response) |
| Branding | None |
| Export | PDF reports |
| History | 90-day query history |

**Value Proposition:** 100 queries = $0.99/query vs. $150+/hour consultant

---

#### TEAM ($299/month)

**Target:** Development firms, architecture practices, title companies

| Feature | Included |
|---------|----------|
| Queries | 500/month |
| MCP Tools | All 5 tools |
| Jurisdictions | All available |
| Users | Up to 5 seats |
| Support | Priority email (24hr) |
| Branding | None |
| Export | PDF + DOCX reports |
| History | 1-year query history |
| API Access | Basic (100 calls/day) |

**Value Proposition:** Team workflow + API access for internal tools

---

#### ENTERPRISE (Custom)

**Target:** Large developers, municipalities, title insurance companies

| Feature | Included |
|---------|----------|
| Queries | Unlimited |
| Users | Unlimited seats |
| Support | Dedicated Slack + SLA |
| API Access | Full (no rate limits) |
| Custom | White-label option |
| Data | Bulk export, custom jurisdictions |
| Compliance | SOC 2 report (when available) |

**Starting Price:** $999/month (negotiable based on volume)

---

#### API-ONLY (Pay-as-you-go)

**Target:** Developers integrating ZoneWise into their apps

| Feature | Included |
|---------|----------|
| Pricing | $0.50/query |
| Volume Discounts | 10K+: $0.40, 50K+: $0.30 |
| Rate Limits | 1,000/day (upgradeable) |
| Support | Developer docs + email |

**Use Cases:** PropTech apps, title company integrations, real estate platforms

---

## Unit Economics

### Cost Structure (Per Query)

| Component | Cost | Notes |
|-----------|------|-------|
| AI Processing (Smart Router) | $0.02 | 90% Gemini FREE, 10% paid |
| Supabase | $0.001 | Database + storage |
| Render | $0.005 | Compute |
| **Total COGS** | **~$0.03** | Per query |

### Margin Analysis by Tier

| Tier | Revenue/Query | COGS | Gross Margin |
|------|---------------|------|--------------|
| Free | $0 | $0.03 | -100% (CAC) |
| Pro | $0.99 | $0.03 | **97%** |
| Team | $0.60 | $0.03 | **95%** |
| Enterprise | ~$0.30 | $0.03 | **90%** |
| API | $0.50 | $0.03 | **94%** |

### Break-Even Analysis

**Monthly Fixed Costs:**
- Render: $25/mo (Starter)
- Supabase: $25/mo (Pro)
- Domain/Cloudflare: $20/mo
- **Total:** $70/mo

**Break-Even:** 1 Pro subscriber ($99) or ~140 API queries

---

## Pricing Psychology

### Anchoring

Landing page shows consultant comparison first:

```
┌─────────────────────────────────────────┐
│  "Zoning consultants charge $150-500/hr │
│   ZoneWise: Unlimited queries for $99"  │
└─────────────────────────────────────────┘
```

### Decoy Effect

Team tier positioned to make Pro look affordable and Enterprise reasonable:

```
Free → Pro ($99) → Team ($299) → Enterprise
              ↑
        "Most Popular" badge
```

### Loss Aversion

Free tier messaging at query 8:

```
"⚠️ 2 queries remaining this month. 
Don't lose access to your zoning data.
Upgrade to Pro for unlimited checks →"
```

---

## Upgrade Triggers

### Free → Pro

| Trigger | Timing | Message |
|---------|--------|---------|
| Query 8 | In-app | "3 queries remaining" |
| Query 10 | In-app | "Upgrade for unlimited" |
| Query 11 | Block | "You've used all free queries" |
| 7 days after signup | Email | "How was your first week?" |
| 30 days no upgrade | Email | "Your queries reset. Ready for Pro?" |

### Pro → Team

| Trigger | Timing | Message |
|---------|--------|---------|
| Query 80 | In-app | "Running low. Team = 5x queries" |
| 3rd month | Email | "Invite your team for $60/seat" |
| API request | In-app | "API access with Team plan" |

### Team → Enterprise

| Trigger | Timing | Action |
|---------|--------|--------|
| Query 400 | In-app | "Talk to us about unlimited" |
| 5+ users requested | Automated | Sales outreach (human) |
| API limit hit | Automated | Enterprise upsell email |

---

## Discounting Policy

### Allowed Discounts

| Scenario | Discount | Approval |
|----------|----------|----------|
| Annual prepay | 20% (2 months free) | Automatic |
| Non-profit/edu | 50% | Manual review |
| Beta users | 30% lifetime | Grandfathered |
| Competitive switch | 25% first year | Case-by-case |

### Never Discount

- Free tier limits (maintains viral loop)
- API pricing (sets precedent)
- Enterprise below $499/mo (qualification signal)

---

## Competitive Pricing

### Market Comparison

| Competitor | Pricing | ZoneWise Position |
|------------|---------|-------------------|
| Zoning Consultant | $150-500/hr | 99%+ cheaper |
| PropertyShark | $99-399/mo | Similar, AI-native |
| CoStar | $500+/mo | 80% cheaper |
| Generic AI (ChatGPT) | $20/mo | More accurate |

### Positioning

```
Price ↑
      │    CoStar ($500+)
      │         │
      │         │
      │    ZoneWise Team ($299)
      │         │
      │    PropertyShark ($99-199)
      │    ZoneWise Pro ($99)
      │         │
      │    ChatGPT ($20)
      │    ZoneWise Free ($0)
      └──────────────────────────→ Accuracy
              Low            High
```

**ZoneWise Sweet Spot:** PropertyShark price + CoStar accuracy

---

## Revenue Projections

### Q1 2026 (Launch Quarter)

| Month | Free | Pro | Team | MRR |
|-------|------|-----|------|-----|
| Feb | 30 | 3 | 0 | $297 |
| Mar | 60 | 7 | 1 | $992 |
| Apr | 100 | 12 | 2 | $1,786 |

**Q1 Total MRR:** ~$1,800

### Q2 2026

| Month | Free | Pro | Team | Enterprise | MRR |
|-------|------|-----|------|------------|-----|
| May | 150 | 20 | 4 | 0 | $3,176 |
| Jun | 220 | 35 | 6 | 1 | $5,764 |
| Jul | 300 | 50 | 8 | 1 | $7,749 |

**Q2 Exit MRR:** ~$7,500 ($90K ARR run rate)

### Year 1 Target

- **MRR:** $15,000 ($180K ARR)
- **Subscribers:** 150 paid (mix of Pro/Team/Enterprise)
- **Free users:** 1,000+

---

## Pricing Experiments

### Planned Tests

| Test | Hypothesis | Timeline |
|------|------------|----------|
| $79 vs $99 Pro | Lower price → higher volume | Q2 |
| $199 Team | Simpler tier structure | Q2 |
| Query packs | One-time purchase option | Q3 |
| Annual discount | 2 mo vs 3 mo free | Q2 |

### A/B Testing Framework

```
Control: Current pricing
Variant: Test pricing
Sample: 50/50 new signups
Duration: 4 weeks minimum
Success: Higher LTV, not just conversion
```

---

## Implementation

### Stripe Products

```javascript
// Stripe product IDs (to be created)
const PRODUCTS = {
  pro_monthly: 'price_zonewise_pro_99',
  pro_annual: 'price_zonewise_pro_948', // $79/mo
  team_monthly: 'price_zonewise_team_299',
  team_annual: 'price_zonewise_team_2868', // $239/mo
  api_query: 'price_zonewise_api_050', // metered
};
```

### Supabase Schema

```sql
-- User subscriptions
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  tier TEXT CHECK (tier IN ('free', 'pro', 'team', 'enterprise', 'api')),
  queries_limit INTEGER,
  queries_used INTEGER DEFAULT 0,
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Query metering
CREATE TABLE query_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  query_type TEXT,
  tokens_used INTEGER,
  cost_usd DECIMAL(10,6),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Related Documents

- [GTM_STRATEGY.md](./GTM_STRATEGY.md) — Overall go-to-market strategy
- [MARKETING_PLAYBOOK.md](./MARKETING_PLAYBOOK.md) — Marketing execution
- [COMPETITIVE_ANALYSIS.md](./COMPETITIVE_ANALYSIS.md) — Competitive landscape

---

*Pricing strategy by Claude AI Architect. Review quarterly.*
