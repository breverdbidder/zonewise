# ZoneWise Skills Integration Guide
## Applying BidDeed.AI Skills Architecture to ZoneWise Ecosystem

**Created:** January 13, 2026  
**Ecosystems:** BidDeed.AI (foreclosure auctions) + ZoneWise (zoning intelligence)  
**Key Insight:** Separate products, shared architectural patterns

---

## Executive Summary

**ZoneWise** is a **separate agentic AI ecosystem** from BidDeed.AI, with its own:
- GitHub repository: `breverdbidder/zonewise`
- Supabase database (separate instance from BidDeed.AI)
- Product focus: Florida zoning intelligence (17 Brevard jurisdictions)
- Launch timeline: Q1 2026
- First skill: `zonewize` (zoning compliance analysis)

**Relationship to BidDeed.AI:**
- **Separate products** (different markets, databases, repos)
- **Shared architecture patterns** (Skills, ForecastEngines, Smart Router, observability)
- **Same tech stack** (GitHub Actions, LangGraph, Supabase, Cloudflare)
- **Same AI Architect** (Claude applying Skills Architecture to both)

---

## Part 1: Two Ecosystems, One Architecture

### **BidDeed.AI Ecosystem**
```
Repository: breverdbidder/brevard-bidder-scraper
Database: mocerqjnksmhcjzxrewo.supabase.co
Focus: Foreclosure auction intelligence
Counties: 3 now → 67 in Q1 2026
Skills: 16 deployed (lien-priority, max-bid, property-photos, etc.)
```

### **ZoneWise Ecosystem**
```
Repository: breverdbidder/zonewise
Database: [zonewise supabase instance]
Focus: Zoning compliance intelligence
Jurisdictions: 17 Brevard → statewide later
Skills: zonewize (first skill to be built)
```

### **Shared Architectural Patterns**

| Pattern | BidDeed.AI | ZoneWise |
|---------|------------|----------|
| **Skills Framework** | ✅ 16 skills | ✅ Starting with zonewize |
| **ForecastEngines** | ✅ 12 engines (93.7 avg) | 🔜 Compliance forecast, developability |
| **Smart Router** | ✅ 90% FREE tier | 🔜 Same cost optimization |
| **Observability** | ✅ structured_logger + metrics | 🔜 Same logging patterns |
| **MCP Integration** | ✅ Supabase + Cloudflare | 🔜 Supabase + Firecrawl |
| **Multi-locale** | ✅ 67 counties | 🔜 17 jurisdictions → statewide |
| **GitHub Actions** | ✅ Daily 11PM pipeline | 🔜 On-demand + scheduled |
| **Zero-loop execution** | ✅ 3-retry patterns | 🔜 Same patterns |

---

## Part 2: ZoneWise Repository Structure

### **Proposed Skills Directory Structure**

```
zonewise/
├── README.md
├── docs/
│   ├── CORE_PRINCIPLE.md
│   ├── GITHUB_SUPABASE_WORKFLOW.md
│   ├── PRD_AI_FIRST.md
│   ├── TECHNICAL_SPECS.md
│   ├── architecture/                      ← NEW: Apply BidDeed patterns
│   │   ├── SKILLS_ARCHITECTURE.md        ← Adapted from BidDeed.AI
│   │   ├── SKILLS_QUICKSTART_GUIDE.md    ← Adapted from BidDeed.AI
│   │   └── ZONEWISE_ORCHESTRATION_MAP.md ← ZoneWise-specific pipeline
│   └── competitive-intelligence/
├── infrastructure/
├── scripts/
├── src/                                    ← NEW: Core application code
│   ├── skills/                            ← NEW: ZoneWise skills directory
│   │   ├── zonewize/                      ← FIRST SKILL
│   │   │   ├── SKILL.md                   ← Documentation
│   │   │   ├── CHANGELOG.md               ← Version history
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py                ← Core compliance logic
│   │   │   ├── scraper.py                 ← Firecrawl integration
│   │   │   ├── parser.py                  ← Ordinance parsing
│   │   │   └── forecaster.py              ← Compliance prediction
│   │   └── (future skills: developability, variance-probability, etc.)
│   ├── forecast_engines/                  ← NEW: ZoneWise ForecastEngines
│   │   ├── compliance_forecast/
│   │   └── development_potential/
│   ├── orchestrator/                      ← NEW: LangGraph workflows
│   │   ├── zonewize_workflow.py
│   │   └── report_generation_workflow.py
│   ├── observability/                     ← NEW: Logging/metrics
│   │   ├── structured_logger.py
│   │   ├── metrics.py
│   │   └── error_tracker.py
│   ├── mcp/                               ← NEW: MCP server integrations
│   │   ├── supabase_mcp.py
│   │   └── firecrawl_mcp.py
│   └── utils/
├── tests/                                  ← NEW: Test suite
│   ├── test_zonewize/
│   ├── test_forecast_engines/
│   └── fixtures/
├── .github/
│   └── workflows/
│       ├── zonewize-pipeline.yml          ← Daily scraping + analysis
│       └── test.yml                       ← CI/CD testing
└── supabase/                              ← Supabase specific
    ├── migrations/
    └── seed.sql
```

---

## Part 3: The `zonewize` Skill Specification

### **Skill Identity**

```yaml
skill_name: zonewize
ecosystem: ZoneWise (NOT BidDeed.AI)
repository: breverdbidder/zonewise
database: ZoneWise Supabase instance (separate from BidDeed.AI)
tier: core (foundational skill for ZoneWise)
```

### **Purpose**

Analyzes property zoning compliance for 17 Brevard County jurisdictions by:
1. Scraping jurisdiction ordinance pages (Firecrawl)
2. Parsing zoning codes and regulations
3. Comparing property characteristics against allowed uses
4. Generating compliance reports with violation details

### **Inputs**

```python
{
    "property_id": str,         # Unique ID in ZoneWise database
    "parcel_id": str,           # County parcel ID
    "address": str,             # Full property address
    "jurisdiction": str,        # One of 17 Brevard jurisdictions
    "property_type": str,       # residential, commercial, industrial
    "current_use": str,         # Actual current use
    "proposed_use": str         # Optional: for development analysis
}
```

### **Outputs**

```python
{
    "compliance_status": str,   # COMPLIANT, NON_COMPLIANT, UNKNOWN, MANUAL_REVIEW
    "zoning_district": str,     # e.g., "R-1", "C-2", "I-1"
    "allowed_uses": list[str],  # Permitted uses in this zone
    "violations": list[dict],   # Specific violations found
        # Each violation: {type, description, severity, code_reference}
    "confidence_score": int,    # 0-100, how confident is analysis
    "requires_variance": bool,  # Does proposed use need variance
    "ordinance_sections": list[str],  # Relevant ordinance sections
    "last_updated": str,        # When ordinance was last scraped
    "data_source": str,         # "firecrawl", "cache", "manual"
    "execution_time_ms": float,
    "cost_usd": float
}
```

### **Execution Workflow**

```
┌─────────────────────────────────────────────────────────┐
│          zonewize Skill Execution Flow                  │
└─────────────────────────────────────────────────────────┘

Step 1: Check Cache
    ↓
Is ordinance cached (<7 days old)?
    ├─ YES → Use cached data (fast path)
    │        Skip Steps 2-3
    │
    └─ NO → Continue to Step 2

Step 2: Scrape Ordinance (Firecrawl MCP)
    ↓
jurisdiction_config = JURISDICTION_CONFIGS[jurisdiction]
ordinance_url = jurisdiction_config['ordinance_url']
firecrawl_result = call_firecrawl_mcp(ordinance_url)
    │
    ├─ SUCCESS → Continue to Step 3
    │
    └─ FAILURE → Try Fallback 1 (cached data even if old)
                 └─ Still FAILURE → Fallback 2 (flag for manual review)

Step 3: Parse Ordinance
    ↓
Parse HTML/PDF to extract:
- Zoning district definitions
- Allowed uses by district
- Dimensional requirements (setbacks, height, lot size)
- Special conditions/restrictions
    │
    ↓
Cache parsed data (7 day TTL)

Step 4: Analyze Compliance
    ↓
Compare property against:
✓ Allowed uses (is current/proposed use permitted?)
✓ Dimensional requirements (meets setbacks, height?)
✓ Special conditions (HOA, overlay districts?)
    │
    ↓
Generate violations list (if any)

Step 5: Confidence Scoring
    ↓
Calculate confidence based on:
- Data recency (newer = higher confidence)
- Ordinance clarity (clear rules = higher)
- Property data completeness (more data = higher)
- Edge cases detected (ambiguity = lower)

Step 6: Return Results
    ↓
Log to observability system:
- structured_logger.info('zonewize_completed')
- log_metric('zonewize_execution_ms', time)
- log_metric('zonewize_compliance_rate', compliant ? 1 : 0)
    │
    ↓
Return compliance report
```

### **Zero-Loop Compliance**

```python
# NEVER blocks pipeline - always returns a result

Primary: Firecrawl scrape → parse → analyze
    ↓ (if fails)
Fallback 1: Use cached data (even if >7 days old)
    ↓ (if fails)
Fallback 2: Return MANUAL_REVIEW status
    └─ Log: "zonewize_manual_review_required"
    └─ Continue pipeline with flagged status
```

### **Cost Optimization**

```
Firecrawl API:
- Cost: $5/1000 pages
- Rate: 1 page per property (ordinance page)
- Cost per property: $0.005

LLM Usage:
- Tier: Gemini 2.5 Flash (FREE)
- Use case: Parse ordinance text, extract rules
- Tokens: ~500 per property
- Cost: $0.00

Caching Strategy:
- Cache ordinances: 7 days TTL
- Expected cache hit rate: 85% (same jurisdictions)
- Effective cost: $0.005 × 15% = $0.00075/property

Total: $0.00075 per property average
```

### **Multi-Jurisdiction Support**

```python
# jurisdiction_configs.json
{
  "indian_harbour_beach": {
    "full_name": "Indian Harbour Beach",
    "ordinance_url": "https://library.municode.com/fl/indian_harbour_beach",
    "zoning_map_url": "https://ihb.maps.arcgis.com/...",
    "contact": "planning@ihb-fl.gov",
    "phone": "(321) 773-2200"
  },
  "melbourne": {
    "full_name": "City of Melbourne",
    "ordinance_url": "https://library.municode.com/fl/melbourne",
    "zoning_map_url": "https://melbourne.maps.arcgis.com/...",
    "contact": "planning@melbourneflorida.org",
    "phone": "(321) 608-7500"
  },
  // ... 15 more jurisdictions
}

def analyze_zoning(property_id, jurisdiction):
    config = JURISDICTION_CONFIGS[jurisdiction]  # Parameterized!
    # Same code works for all 17 jurisdictions
```

---

## Part 4: Applying BidDeed.AI Skills Architecture to ZoneWise

### **Step 1: Copy Skills Documentation to ZoneWise**

```bash
# Copy Skills Architecture patterns to ZoneWise repo
cp docs/architecture/SKILLS_ARCHITECTURE.md zonewise/docs/architecture/
cp docs/architecture/SKILLS_QUICKSTART_GUIDE.md zonewise/docs/architecture/

# Adapt to ZoneWise context:
# - Replace "BidDeed.AI" with "ZoneWise"
# - Replace "foreclosure auction" with "zoning compliance"
# - Replace "properties/month" with "analyses/month"
# - Keep all patterns: Smart Router, ForecastEngines, observability, etc.
```

### **Step 2: Set Up ZoneWise-Specific Orchestration**

```python
# src/orchestrator/zonewize_workflow.py

from langgraph.graph import StateGraph
from typing import TypedDict

class ZoneWizeState(TypedDict):
    property_id: str
    jurisdiction: str
    compliance_status: str
    violations: list
    report_path: str

workflow = StateGraph(ZoneWizeState)

# Node 1: Fetch property data from Supabase
workflow.add_node("fetch_property", fetch_property_node)

# Node 2: Run zonewize skill
workflow.add_node("analyze_compliance", zonewize_skill_node)

# Node 3: Generate compliance report (DOCX)
workflow.add_node("generate_report", report_generation_node)

# Node 4: Store results in Supabase
workflow.add_node("store_results", supabase_storage_node)

# Edges
workflow.add_edge("fetch_property", "analyze_compliance")
workflow.add_edge("analyze_compliance", "generate_report")
workflow.add_edge("generate_report", "store_results")

# Entry and exit
workflow.set_entry_point("fetch_property")
workflow.set_finish_point("store_results")

# Compile
zonewize_app = workflow.compile()
```

### **Step 3: Implement Observability (Same Patterns as BidDeed.AI)**

```python
# src/observability/structured_logger.py
# (Identical to BidDeed.AI implementation)

# ZoneWise Supabase tables:
CREATE TABLE zonewise_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    value NUMERIC NOT NULL,
    labels JSONB,
    correlation_id UUID,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE zonewise_errors (
    id BIGSERIAL PRIMARY KEY,
    error_type TEXT NOT NULL,
    error_message TEXT,
    skill_name TEXT,
    context JSONB,
    correlation_id UUID,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

# Metrics to track:
- zonewize_execution_ms
- zonewize_compliance_rate (% compliant)
- zonewize_cache_hit_rate
- zonewize_firecrawl_cost_usd
- zonewize_manual_review_rate
```

### **Step 4: Build zonewize Using SKILLS_QUICKSTART_GUIDE.md**

Follow the exact same template from BidDeed.AI:

**Phase 1: Planning (5 min)**
- Fill out skill definition template ✅ (done above)

**Phase 2: Structure (10 min)**
```bash
mkdir -p src/skills/zonewize
cd src/skills/zonewize
touch SKILL.md CHANGELOG.md __init__.py
touch analyzer.py scraper.py parser.py forecaster.py
```

**Phase 3: SKILL.md (15 min)**
- Copy template from SKILLS_QUICKSTART_GUIDE.md
- Adapt to zonewize context
- Document all inputs, outputs, workflow

**Phase 4: Implementation (30 min)**
```python
# src/skills/zonewize/analyzer.py

from src.observability import structured_logger, log_metric, track_error
from src.mcp.firecrawl_mcp import scrape_ordinance
import time

async def analyze_zoning(property_id, jurisdiction, correlation_id):
    """
    Main zonewize skill entry point.
    Follows zero-loop execution pattern.
    """
    start = time.time()
    
    structured_logger.info(
        'zonewize_started',
        extra={
            'correlation_id': correlation_id,
            'property_id': property_id,
            'jurisdiction': jurisdiction
        }
    )
    
    try:
        # Primary: Scrape ordinance
        ordinance = await scrape_ordinance(jurisdiction)
        
        # Parse ordinance
        rules = parse_ordinance(ordinance)
        
        # Analyze compliance
        result = check_compliance(property_id, rules)
        
        # Log success
        log_metric('zonewize_execution_ms', (time.time()-start)*1000)
        log_metric('zonewize_compliant', 1 if result['compliant'] else 0)
        
        return result
        
    except Exception as e:
        # Fallback: Try cached data
        try:
            cached = get_cached_ordinance(jurisdiction)
            if cached:
                result = check_compliance(property_id, cached)
                log_metric('zonewize_cache_fallback', 1)
                return result
        except:
            pass
        
        # Final fallback: Manual review
        track_error(
            error_type='zonewize_analysis_failed',
            skill_name='zonewize',
            context={'property_id': property_id, 'jurisdiction': jurisdiction}
        )
        
        return {
            'compliance_status': 'MANUAL_REVIEW',
            'confidence_score': 0,
            'requires_manual': True
        }
```

**Phase 5: Testing (15 min)**
```python
# tests/test_zonewize/test_analyzer.py

def test_ihb_residential_compliant():
    """Test IHB R-1 residential property"""
    result = analyze_zoning(
        property_id='test-001',
        jurisdiction='indian_harbour_beach',
        correlation_id='test-corr-1'
    )
    
    assert result['compliance_status'] == 'COMPLIANT'
    assert result['zoning_district'] == 'R-1'
    assert 'single_family' in result['allowed_uses']

def test_melbourne_commercial_violation():
    """Test Melbourne commercial with setback violation"""
    result = analyze_zoning(
        property_id='test-002',
        jurisdiction='melbourne',
        correlation_id='test-corr-2'
    )
    
    assert result['compliance_status'] == 'NON_COMPLIANT'
    assert len(result['violations']) > 0
    assert any(v['type'] == 'setback' for v in result['violations'])
```

**Phase 6: Deploy to GitHub (5 min)**
```bash
cd /repo/zonewise
git add src/skills/zonewize/
git add tests/test_zonewize/
git commit -m "feat(zonewize): Add zoning compliance skill

- Primary: Firecrawl scrape → parse → analyze
- Fallback 1: Cached ordinance data
- Fallback 2: Manual review flag
- Zero-loop compliant
- 85% test coverage
- $0.00075/property cost"

git push origin main
```

**Phase 7: Integration (5 min)**
```python
# Update zonewize_workflow.py to use the skill
def zonewize_skill_node(state: ZoneWizeState):
    result = analyze_zoning(
        property_id=state['property_id'],
        jurisdiction=state['jurisdiction'],
        correlation_id=state.get('correlation_id')
    )
    
    return {
        'compliance_status': result['compliance_status'],
        'violations': result['violations'],
        'confidence_score': result['confidence_score']
    }
```

---

## Part 5: ZoneWise ForecastEngines (Future)

Following BidDeed.AI's ForecastEngine pattern, ZoneWise will build:

### **1. Compliance Forecast ForecastEngine**
```
Purpose: Predict likelihood of compliance for proposed development
ML Model: XGBoost trained on historical variance approvals
LLM: Gemini 2.5 Flash for ordinance interpretation
Target Score: 95/100
```

### **2. Development Potential ForecastEngine**
```
Purpose: Calculate max buildable square footage given constraints
ML Model: Regression model on setbacks, FAR, height limits
LLM: DeepSeek V3.2 for edge case reasoning
Target Score: 93/100
```

### **3. Variance Approval Probability ForecastEngine**
```
Purpose: Predict P(variance approved) based on historical data
ML Model: Classification model on variance history
LLM: Claude Sonnet 4.5 for complex legal reasoning
Target Score: 90/100
```

---

## Part 6: Deployment Checklist for ZoneWise

Before deploying zonewize skill to production:

- [ ] SKILLS_ARCHITECTURE.md adapted for ZoneWise
- [ ] SKILLS_QUICKSTART_GUIDE.md copied to ZoneWise repo
- [ ] zonewize skill implemented (analyzer, scraper, parser)
- [ ] Jurisdiction configs for all 17 Brevard jurisdictions
- [ ] Firecrawl MCP integration working
- [ ] Zero-loop compliance verified (3 fallbacks tested)
- [ ] Observability integrated (structured_logger, metrics, errors)
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests (Firecrawl mocked)
- [ ] E2E tests (3 jurisdictions: IHB, Melbourne, Palm Bay)
- [ ] Cost optimization verified ($0.00075/property)
- [ ] Supabase schema deployed
- [ ] GitHub Actions workflow created
- [ ] Documentation complete

---

## Part 7: Key Differences Between Ecosystems

| Aspect | BidDeed.AI | ZoneWise |
|--------|------------|----------|
| **Market** | Real estate investors | Developers, architects, homeowners |
| **Data Source** | RealForeclose, BCPAO, AcclaimWeb | Municode, government portals |
| **Key Metric** | Max bid amount | Compliance status |
| **Pipeline** | 12 stages (Discovery → Archive) | 4 stages (Fetch → Analyze → Report → Store) |
| **Frequency** | Daily 11PM (scheduled) | On-demand (user-initiated) |
| **Cost/Unit** | $0.0004/property | $0.00075/property |
| **Supabase** | mocerqjnksmhcjzxrewo | [zonewise instance] |
| **Primary Skill** | lien-priority-forecast | zonewize |

---

## Summary

**ZoneWise is a separate ecosystem that APPLIES BidDeed.AI patterns:**

✅ **Same Skills Architecture** (documentation, patterns, best practices)  
✅ **Same tech stack** (GitHub, Supabase, LangGraph, Smart Router)  
✅ **Same observability** (structured_logger, metrics, errors)  
✅ **Same quality bar** (80%+ tests, zero-loop, multi-locale)  

❌ **Different repositories** (zonewise repo, not brevard-bidder-scraper)  
❌ **Different databases** (separate Supabase instances)  
❌ **Different domains** (zoning vs foreclosures)  

**Next Actions:**

1. Copy SKILLS_ARCHITECTURE.md to zonewise/docs/architecture/
2. Adapt to ZoneWise context (replace BidDeed.AI references)
3. Build zonewize skill using SKILLS_QUICKSTART_GUIDE.md template
4. Deploy to zonewise repo (NOT BidDeed.AI repo)
5. Set up ZoneWise Supabase with observability tables
6. Launch Q1 2026

---

**END OF INTEGRATION GUIDE**