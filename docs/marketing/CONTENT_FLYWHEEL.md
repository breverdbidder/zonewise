# ZoneWise Content Flywheel Strategy

> **Version:** 1.0 | **Last Updated:** January 18, 2026  
> **Origin:** Adapted from BidDeed.AI 5-Agent Flywheel Architecture  
> **Status:** Pre-Launch Planning

---

## Executive Summary

The Content Flywheel is ZoneWise's **autonomous marketing engine** — a self-reinforcing system where every zoning query generates content, content generates leads, leads generate more queries, and more queries improve the AI. Following the BidDeed.AI model, this operates with **0 human hours/week** once deployed.

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE ZONEWISE FLYWHEEL                        │
│                                                                 │
│    ┌──────────────┐                     ┌──────────────┐       │
│    │   CONTENT    │──────────────────→  │    LEADS     │       │
│    └──────────────┘                     └──────────────┘       │
│           ↑                                    │                │
│           │                                    ↓                │
│    ┌──────────────┐                     ┌──────────────┐       │
│    │ OPTIMIZATION │  ←────────────────  │   QUERIES    │       │
│    └──────────────┘                     └──────────────┘       │
│                                                                 │
│    Each rotation: Content improves, leads increase,            │
│    queries compound, AI gets smarter                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5-Agent Architecture

### LangGraph Stages Integration

The Content Flywheel extends ZoneWise's core pipeline with marketing automation:

```
Core Pipeline (Stages 1-4):
├── Stage 1: Property Fetch
├── Stage 2: Zoning Analysis
├── Stage 3: Compliance Check
├── Stage 4: Report Generation

Content Flywheel (Stages 5-9):
├── Stage 5: Content Generation Agent
├── Stage 6: Content Distribution Agent
├── Stage 7: Engagement Tracking Agent
├── Stage 8: Conversion Attribution Agent
└── Stage 9: Optimization Agent
```

---

## Agent Specifications

### Agent 1: Content Generation

**Purpose:** Transform zoning queries and analysis into multi-platform marketing content.

**Inputs:**
- Daily query patterns (most searched districts, common violations)
- Compliance analysis results
- Ordinance updates detected
- User questions (anonymized)

**Outputs:**
- LinkedIn posts (professional insights)
- Twitter/X threads (educational, 6-8 tweets)
- Blog articles (SEO-optimized)
- Email newsletters (weekly roundup)

**Content Templates:**

```python
CONTENT_TEMPLATES = {
    "district_spotlight": {
        "linkedin": "🏗️ District Deep Dive: {district} in {city}\n\n"
                   "Key facts developers need to know:\n"
                   "• Max height: {max_height} ft\n"
                   "• Lot coverage: {lot_coverage}%\n"
                   "• Front setback: {front_setback} ft\n\n"
                   "Common compliance issue: {common_violation}\n\n"
                   "Check any Brevard property instantly → zonewise.com",
        
        "twitter": "🧵 Thread: Everything you need to know about {district} zoning in {city}, FL\n\n"
                  "1/ Basic facts: {district} is a {use_type} district covering {area_description}",
    },
    
    "ordinance_update": {
        "linkedin": "⚠️ ZONING ALERT: {city} just updated {ordinance_section}\n\n"
                   "What changed: {change_summary}\n\n"
                   "Impact on developers: {impact}\n\n"
                   "Full analysis → zonewise.com/updates/{city}",
    },
    
    "compliance_tip": {
        "twitter": "💡 Quick tip: The #{1} compliance mistake in {city}?\n\n"
                  "{mistake_description}\n\n"
                  "How to avoid it: {solution}\n\n"
                  "Free compliance check → zonewise.com",
    },
    
    "market_insight": {
        "linkedin": "📊 This week in Brevard County zoning:\n\n"
                   "• {queries_count} compliance checks run\n"
                   "• Top searched district: {top_district}\n"
                   "• Most common question: \"{common_question}\"\n\n"
                   "The AI-powered answer: {answer_preview}...\n\n"
                   "Try ZoneWise free → zonewise.com",
    }
}
```

**Smart Router Configuration:**

```python
# Cost optimization: 90% FREE tier for content generation
CONTENT_GEN_ROUTING = {
    "district_spotlight": "FREE",      # Gemini 2.5 Flash
    "ordinance_update": "STANDARD",    # Claude Haiku (accuracy critical)
    "compliance_tip": "FREE",          # Gemini 2.5 Flash
    "market_insight": "FREE",          # Gemini 2.5 Flash
    "blog_article": "STANDARD",        # Claude Sonnet (long-form quality)
}
```

---

### Agent 2: Content Distribution

**Purpose:** Publish content to all platforms with optimal timing and formatting.

**Platforms:**

| Platform | API | Auth | Cost |
|----------|-----|------|------|
| LinkedIn | Official API | OAuth 2.0 | Free |
| Twitter/X | Official API | OAuth 2.0 | Free tier |
| Email | Resend | API Key | $0.001/email |
| Blog | Cloudflare Pages | Deploy hook | Free |

**Distribution Logic:**

```python
DISTRIBUTION_SCHEDULE = {
    "linkedin": {
        "best_times": ["08:00", "12:00", "17:00"],  # EST
        "frequency": "1x daily",
        "content_types": ["district_spotlight", "market_insight", "ordinance_update"]
    },
    "twitter": {
        "best_times": ["09:00", "13:00", "19:00"],  # EST
        "frequency": "2-3x daily",
        "content_types": ["compliance_tip", "thread", "quick_fact"]
    },
    "email": {
        "frequency": "1x weekly (Friday)",
        "content_types": ["weekly_roundup"]
    },
    "blog": {
        "frequency": "2x weekly",
        "content_types": ["district_spotlight", "guide", "case_study"]
    }
}
```

**Automation Flow:**

```
GitHub Actions (Daily 8 AM EST):
├── Query Supabase for pending content
├── Format for each platform
├── Call platform APIs
├── Log to content_distribution table
└── Update content status → "PUBLISHED"
```

---

### Agent 3: Engagement Tracking

**Purpose:** Collect performance metrics from all platforms.

**Metrics Collected:**

| Metric | LinkedIn | Twitter | Email | Blog |
|--------|----------|---------|-------|------|
| Impressions | ✓ | ✓ | - | ✓ (pageviews) |
| Engagements | ✓ | ✓ | - | - |
| Clicks | ✓ | ✓ | ✓ | ✓ (CTAs) |
| Shares/Retweets | ✓ | ✓ | - | - |
| Comments | ✓ | ✓ | - | - |
| Open Rate | - | - | ✓ | - |
| Conversions | ✓ (UTM) | ✓ (UTM) | ✓ (UTM) | ✓ (UTM) |

**Supabase Schema:**

```sql
CREATE TABLE engagement_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content_library(id),
    platform VARCHAR NOT NULL,
    impressions INTEGER DEFAULT 0,
    engagements INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    engagement_rate FLOAT,
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for performance queries
CREATE INDEX idx_engagement_content ON engagement_metrics(content_id);
CREATE INDEX idx_engagement_platform ON engagement_metrics(platform);
```

**Collection Schedule:**

```
GitHub Actions (Daily 11 PM EST):
├── Fetch LinkedIn analytics (last 24h)
├── Fetch Twitter analytics (last 24h)
├── Fetch Resend email stats
├── Query Plausible for blog metrics
├── Calculate engagement rates
└── Insert into engagement_metrics
```

---

### Agent 4: Conversion Attribution

**Purpose:** Connect content performance to actual leads and signups.

**UTM Strategy:**

```
All ZoneWise links include:
├── utm_source: linkedin | twitter | email | blog
├── utm_medium: post | thread | newsletter | article
├── utm_campaign: {content_id}
└── utm_content: {variant_id} (for A/B tests)

Example:
zonewise.com?utm_source=linkedin&utm_medium=post&utm_campaign=district_r1_melbourne&utm_content=v1
```

**Attribution Model:**

```python
# First-touch attribution (simple, accurate for content marketing)
def attribute_lead(lead_id: str, utm_params: dict):
    """
    Attributes a new lead to the content that generated it.
    """
    return {
        "lead_id": lead_id,
        "content_id": utm_params.get("utm_campaign"),
        "source": utm_params.get("utm_source"),
        "medium": utm_params.get("utm_medium"),
        "variant": utm_params.get("utm_content"),
        "attributed_at": datetime.now()
    }
```

**Supabase Schema:**

```sql
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR,
    name VARCHAR,
    source VARCHAR,      -- utm_source
    medium VARCHAR,      -- utm_medium
    campaign VARCHAR,    -- utm_campaign
    tier VARCHAR,        -- free | pro | team
    status VARCHAR DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE conversion_attribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id),
    content_id UUID REFERENCES content_library(id),
    source VARCHAR,
    medium VARCHAR,
    campaign VARCHAR,
    touchpoints INTEGER DEFAULT 1,
    attributed_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Agent 5: Optimization Loop

**Purpose:** Analyze what works and automatically improve content strategy.

**Optimization Inputs:**

```python
OPTIMIZATION_DATA = {
    "top_performers": [
        # Content pieces with highest engagement
    ],
    "worst_performers": [
        # Content to avoid replicating
    ],
    "best_times": {
        # Actual engagement by posting time
    },
    "best_topics": {
        # Districts/topics driving most conversions
    },
    "conversion_rates": {
        # By platform, content type, topic
    }
}
```

**Optimization Actions:**

| Insight | Automated Action |
|---------|------------------|
| District X posts perform 3x better | Increase frequency for District X |
| Tuesday 9 AM has highest engagement | Shift primary posting to Tuesday 9 AM |
| Compliance tips convert better than spotlights | Generate more compliance tips |
| Email subject line A beats B | Use A pattern for future emails |
| Twitter threads outperform single tweets | Convert more content to threads |

**AI-Powered Insights:**

```python
async def generate_optimization_insights(metrics: dict) -> dict:
    """
    Uses AI to analyze patterns and recommend changes.
    """
    prompt = f"""
    Analyze this content marketing data and provide 3 actionable insights:
    
    Top 5 performing content:
    {metrics['top_performers']}
    
    Conversion rates by platform:
    {metrics['conversion_rates']}
    
    Engagement by time of day:
    {metrics['engagement_by_time']}
    
    Format: JSON with keys: insight, action, expected_impact
    """
    
    # Route to FREE tier (analysis, not content creation)
    response = await smart_router.route(prompt, tier="FREE")
    return response
```

**Feedback Loop:**

```
Weekly Optimization Cycle:
├── Monday: Collect all metrics from past week
├── Tuesday: AI analyzes patterns, generates insights
├── Wednesday: Apply insights to content templates
├── Thursday-Sunday: New content uses optimized strategy
└── Repeat
```

---

## Cost Analysis

### Monthly Costs (Based on BidDeed.AI Model)

| Component | Cost/Week | Monthly | Annual |
|-----------|-----------|---------|--------|
| Content Generation (Agent 1) | $5 | $20 | $240 |
| Distribution APIs (Agent 2) | $2 | $8 | $96 |
| Engagement Tracking (Agent 3) | $1 | $4 | $48 |
| Email (Resend) | $2.50 | $10 | $120 |
| Smart Router (90% FREE) | $2 | $8 | $96 |
| **Total** | **$12.50** | **$50** | **$600** |

### Comparison to Alternatives

| Solution | Monthly Cost | Automation | AI-Native |
|----------|--------------|------------|-----------|
| **ZoneWise Flywheel** | **$50** | **95%** | **Yes** |
| Buffer Pro | $120 | 30% | No |
| Hootsuite Team | $600 | 40% | No |
| HubSpot Marketing | $800 | 60% | Partial |
| Agency Retainer | $3,000+ | 0% | No |

**ZoneWise Advantage:** 93% cheaper than Buffer + fully automated + AI-native

---

## Success Metrics (KPIs)

### Input Metrics

| Metric | Q1 Target | Q2 Target |
|--------|-----------|-----------|
| Content pieces/week | 10 | 20 |
| Platforms active | 3 | 4 |
| Cost per content piece | $5 | $3 |

### Output Metrics

| Metric | Q1 Target | Q2 Target |
|--------|-----------|-----------|
| Total impressions/week | 5,000 | 20,000 |
| Total engagements/week | 250 | 1,000 |
| Total clicks/week | 50 | 200 |
| Leads generated/week | 5 | 20 |

### Efficiency Metrics

| Metric | Q1 Target | Q2 Target |
|--------|-----------|-----------|
| Cost per lead | $10 | $5 |
| Cost per customer | $100 | $50 |
| ROI | 5x | 10x |
| Automation rate | 90% | 98% |

### Growth Metrics

| Metric | Q1 Target | Q2 Target |
|--------|-----------|-----------|
| MoM impression growth | 50% | 30% |
| MoM lead growth | 40% | 25% |
| Viral coefficient | 1.1 | 1.3 |

---

## Implementation Timeline

### Phase 1: Foundation (Week 1-2)

- [ ] Deploy Supabase schema (content_library, engagement_metrics, leads)
- [ ] Build Agent 1 (Content Generation)
- [ ] Create content templates for 4 types
- [ ] Test with sample zoning data
- [ ] Generate first content batch

### Phase 2: Distribution (Week 3-4)

- [ ] Build Agent 2 (Distribution)
- [ ] Set up LinkedIn API OAuth
- [ ] Set up Twitter API OAuth
- [ ] Configure Resend for email
- [ ] Deploy GitHub Actions workflow
- [ ] Publish first automated content

### Phase 3: Tracking (Week 5-6)

- [ ] Build Agent 3 (Engagement Tracking)
- [ ] Integrate platform analytics APIs
- [ ] Set up daily metrics collection
- [ ] Build Supabase metrics dashboard
- [ ] First weekly report generated

### Phase 4: Attribution (Week 7-8)

- [ ] Build Agent 4 (Conversion Attribution)
- [ ] Implement UTM tracking on all links
- [ ] Connect leads table
- [ ] Calculate first conversion rates
- [ ] Attribution report dashboard

### Phase 5: Optimization (Week 9-10)

- [ ] Build Agent 5 (Optimization)
- [ ] AI-powered insights generation
- [ ] A/B testing framework
- [ ] Close the optimization loop
- [ ] Full flywheel operational

---

## Supabase Schema (Complete)

```sql
-- Content Flywheel Schema for ZoneWise
-- Run in Supabase SQL Editor

-- Content library (all generated content)
CREATE TABLE content_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_type VARCHAR NOT NULL,  -- district_spotlight, compliance_tip, etc.
    topic VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    body TEXT NOT NULL,
    platform VARCHAR NOT NULL,  -- linkedin, twitter, email, blog
    status VARCHAR DEFAULT 'draft',  -- draft, scheduled, published
    district VARCHAR,  -- if district-specific
    jurisdiction VARCHAR,  -- if jurisdiction-specific
    smart_router_model VARCHAR,
    generation_cost DECIMAL(10,6),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

-- Distribution queue
CREATE TABLE content_distribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content_library(id),
    platform VARCHAR NOT NULL,
    scheduled_time TIMESTAMPTZ NOT NULL,
    status VARCHAR DEFAULT 'pending',  -- pending, published, failed
    platform_post_id VARCHAR,  -- ID from platform after publishing
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

-- Engagement metrics
CREATE TABLE engagement_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content_library(id),
    platform VARCHAR NOT NULL,
    impressions INTEGER DEFAULT 0,
    engagements INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    engagement_rate FLOAT,
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leads
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR,
    name VARCHAR,
    source VARCHAR,
    medium VARCHAR,
    campaign VARCHAR,
    tier VARCHAR DEFAULT 'free',
    status VARCHAR DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversion attribution
CREATE TABLE conversion_attribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id),
    content_id UUID REFERENCES content_library(id),
    source VARCHAR,
    medium VARCHAR,
    campaign VARCHAR,
    touchpoints INTEGER DEFAULT 1,
    attributed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optimization insights
CREATE TABLE optimization_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    week_start DATE NOT NULL,
    top_performers JSONB,
    insights JSONB,
    actions_taken JSONB,
    applied BOOLEAN DEFAULT FALSE,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Flywheel metrics (weekly rollup)
CREATE TABLE flywheel_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    week_start DATE NOT NULL,
    content_generated INTEGER DEFAULT 0,
    posts_published INTEGER DEFAULT 0,
    total_impressions INTEGER DEFAULT 0,
    total_engagements INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    leads_generated INTEGER DEFAULT 0,
    conversion_rate FLOAT,
    cost_per_lead FLOAT,
    total_cost DECIMAL(10,2),
    roi FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_content_type ON content_library(content_type);
CREATE INDEX idx_content_platform ON content_library(platform);
CREATE INDEX idx_content_status ON content_library(status);
CREATE INDEX idx_distribution_status ON content_distribution(status);
CREATE INDEX idx_engagement_content ON engagement_metrics(content_id);
CREATE INDEX idx_leads_source ON leads(source, medium, campaign);
CREATE INDEX idx_attribution_content ON conversion_attribution(content_id);
```

---

## GitHub Actions Workflow

```yaml
# .github/workflows/content_flywheel.yml
name: ZoneWise Content Flywheel

on:
  schedule:
    - cron: '0 8 * * *'  # Daily 8 AM EST (13:00 UTC)
  workflow_dispatch:
    inputs:
      stage:
        description: 'Stage to run'
        required: false
        default: 'all'

env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  LINKEDIN_ACCESS_TOKEN: ${{ secrets.LINKEDIN_ACCESS_TOKEN }}
  TWITTER_BEARER_TOKEN: ${{ secrets.TWITTER_BEARER_TOKEN }}
  RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}

jobs:
  content-generation:
    runs-on: ubuntu-latest
    if: ${{ github.event.inputs.stage == 'all' || github.event.inputs.stage == 'generation' }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python src/flywheel/content_generation_agent.py
      
  content-distribution:
    runs-on: ubuntu-latest
    needs: content-generation
    if: ${{ github.event.inputs.stage == 'all' || github.event.inputs.stage == 'distribution' }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python src/flywheel/content_distribution_agent.py

  engagement-tracking:
    runs-on: ubuntu-latest
    if: ${{ github.event.inputs.stage == 'all' || github.event.inputs.stage == 'tracking' }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python src/flywheel/engagement_tracking_agent.py

  weekly-optimization:
    runs-on: ubuntu-latest
    if: ${{ github.event.schedule == '0 8 * * 1' }}  # Mondays only
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python src/flywheel/optimization_agent.py
```

---

## Integration with GTM Strategy

The Content Flywheel supports the overall GTM strategy (see [GTM_STRATEGY.md](./GTM_STRATEGY.md)):

| GTM Channel | Flywheel Role |
|-------------|---------------|
| MCP Marketplace (40%) | N/A (organic discovery) |
| Content SEO (30%) | **Primary driver** — blog articles indexed |
| AI Outreach (20%) | Flywheel generates outreach content |
| Community/PLG (10%) | Social posts drive community engagement |

The flywheel is **not a replacement** for MCP marketplace distribution — it's an **amplifier** that generates awareness and drives traffic to the MCP installation.

---

## Related Documents

- [GTM_STRATEGY.md](./GTM_STRATEGY.md) — Overall go-to-market strategy
- [MARKETING_PLAYBOOK.md](./MARKETING_PLAYBOOK.md) — Channel tactics
- [PRICING.md](./PRICING.md) — Pricing tiers
- [COMPETITIVE_ANALYSIS.md](./COMPETITIVE_ANALYSIS.md) — Competitive landscape
- [LAUNCH_CHECKLIST.md](./LAUNCH_CHECKLIST.md) — Launch requirements

---

*Content Flywheel architecture adapted from BidDeed.AI by Claude AI Architect.*
