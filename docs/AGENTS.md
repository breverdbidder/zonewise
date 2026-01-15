# AGENTS.md - Multi-Agent CrewAI Architecture

**Last Updated:** January 15, 2026  
**AI Architect:** Claude AI (Opus 4.5)  
**Product Owner:** Ariel Shapira

---

## Architecture Decision Record

### Why CrewAI Multi-Agent Over Single-Agent

On January 14, 2026, the AI Architect made a deliberate decision to adopt CrewAI multi-agent architecture for both ZoneWise and BidDeed.AI platforms.

| Evaluation Criteria | Score |
|---------------------|-------|
| Execution Speed | 5.76x faster than LangGraph in benchmarks |
| Role-Based Fit | Natural mapping to domain-specific agents |
| Enterprise Adoption | 60% Fortune 500, $18M funding |
| Production Proven | Battle-tested, not experimental |
| Python-First | Clean API, easy integration |

**Competitive Advantage:**

| Platform | Agent Model | Our Advantage |
|----------|-------------|---------------|
| Claude.ai | Single agent | Specialized experts per domain |
| Lovable | Single agent | Parallel execution possible |
| Manus | Single agent | Better error isolation |
| **ZoneWise / BidDeed.AI** | **Multi-agent CrewAI** | Role-based, sequential handoffs |

---

## Unified Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  E2B AI Artifacts UI (Split-screen chat + artifacts)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 1: CREWAI ORCHESTRATION               │
│  Role-based agents with defined responsibilities            │
│  Sequential or hierarchical process flows                   │
│  Task handoffs with context preservation                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 2: LANGGRAPH STATE                    │
│  Supabase checkpoints for persistence                       │
│  Time-travel debugging capability                           │
│  Human-in-the-loop gates (when needed)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 3: CHATDEV PATTERNS                   │
│  Review loop counters (max 3 iterations)                    │
│  "<INFO> Finished" approval signals                         │
│  Agent-to-agent handoff protocols                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 4: SMART ROUTER                       │
│  FREE (90%):    Gemini 2.5 Flash                           │
│  ULTRA_CHEAP:   DeepSeek V3.2 ($0.28/1M)                   │
│  BALANCED:      Claude Sonnet 4.5                          │
│  PREMIUM:       Claude Opus 4.5 (complex reasoning only)   │
└─────────────────────────────────────────────────────────────┘
```

---

## ZoneWise Agent Crew

**Domain:** Building permits, site plan development, code compliance  
**Repo:** `breverdbidder/zonewise`

### Agent Definitions

```python
from crewai import Agent, Task, Crew, Process

# Agent 1: Discovery Specialist
discovery_agent = Agent(
    role="Discovery Specialist",
    goal="Parse project requirements from client input. Extract parcel ID, address, project type.",
    backstory="""You are an expert at understanding building permit requirements 
    across 17 Brevard County jurisdictions. You can quickly identify project scope,
    required permits, and relevant zoning classifications.""",
    tools=[parcel_lookup, address_geocode, jurisdiction_identifier],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)

# Agent 2: Zoning Analyst
zoning_agent = Agent(
    role="Zoning Analyst", 
    goal="Determine setbacks, height limits, lot coverage, and zoning compliance.",
    backstory="""You are a certified zoning expert who has reviewed thousands of 
    site plans. You know every setback requirement, variance procedure, and 
    conditional use provision in Brevard County.""",
    tools=[jurisdiction_db, bcpao_api, setback_calculator],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)

# Agent 3: Building Code Expert
code_review_agent = Agent(
    role="Building Code Expert",
    goal="Check Florida Building Code 8th Edition compliance across 10 critical areas.",
    backstory="""You are a licensed building inspector with expertise in FBC 8th Edition.
    Your 10-point checklist covers: setbacks, ADA compliance, fire separation, 
    stormwater, tree preservation, parking, utilities, signage, landscaping, and egress.""",
    tools=[fbc_database, violation_logger, code_reference],
    llm="anthropic/claude-sonnet-4-5-20250929",  # BALANCED - needs reasoning
    verbose=True,
    max_iter=3  # ChatDev pattern: max 3 review iterations
)

# Agent 4: Pre-Submission QA
qa_agent = Agent(
    role="Pre-Submission QA Specialist",
    goal="Final review before jurisdiction submission. Generate PDF submittal package.",
    backstory="""You are the final gatekeeper before permit submission. You verify
    all requirements are met, documents are complete, and fees are calculated.""",
    tools=[checklist_validator, pdf_generator, fee_calculator],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)
```

### Task Definitions

```python
# Task 1: Discovery
discovery_task = Task(
    description="""Parse client requirements for {project_name}. 
    Extract: parcel ID, address, project type, jurisdiction, zoning classification.
    Output: Structured ProjectRequirements object.""",
    agent=discovery_agent,
    expected_output="ProjectRequirements JSON with parcel_id, address, jurisdiction, zoning"
)

# Task 2: Zoning Analysis
zoning_task = Task(
    description="""Analyze zoning for parcel {parcel_id} in {jurisdiction}.
    Calculate: front/rear/side setbacks, max height, lot coverage percentage.
    Check: variance requirements, conditional use provisions.""",
    agent=zoning_agent,
    context=[discovery_task],  # Depends on discovery
    expected_output="ZoningAnalysis JSON with setbacks, height_limit, coverage_max, variances"
)

# Task 3: Code Review
code_review_task = Task(
    description="""Run 10-point FBC compliance check:
    1. Setbacks compliance
    2. ADA accessibility  
    3. Fire separation distances
    4. Stormwater management
    5. Tree preservation
    6. Parking requirements
    7. Utility connections
    8. Signage compliance
    9. Landscaping buffer
    10. Egress requirements
    
    Output violations list with severity (CRITICAL/MAJOR/MINOR).""",
    agent=code_review_agent,
    context=[zoning_task],
    expected_output="CodeReview JSON with violations[], overall_status, approval_message"
)

# Task 4: QA Review
qa_task = Task(
    description="""Final QA review before submission.
    Verify: all documents present, calculations correct, fees accurate.
    Generate: PDF submittal package with cover sheet.
    Signal: '<INFO> Finished' when approved.""",
    agent=qa_agent,
    context=[code_review_task],
    expected_output="QAReport JSON with status, pdf_url, fee_total, submission_ready"
)
```

### Crew Assembly

```python
# ZoneWise Crew
zonewise_crew = Crew(
    agents=[discovery_agent, zoning_agent, code_review_agent, qa_agent],
    tasks=[discovery_task, zoning_task, code_review_task, qa_task],
    process=Process.sequential,  # Permit workflow = strict sequence
    verbose=2,
    memory=True,  # Enable conversation memory
    embedder={
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"}
    }
)

# Execute
result = zonewise_crew.kickoff(inputs={
    "project_name": "Bliss Palm Bay",
    "parcel_id": "28-37-S02-00B-0035-0"
})
```

---

## BidDeed.AI Agent Crew

**Domain:** Foreclosure auctions, lien analysis, property valuation  
**Repo:** `breverdbidder/brevard-bidder-scraper`

### Agent Definitions

```python
from crewai import Agent, Task, Crew, Process

# Agent 1: Discovery Agent
discovery_agent = Agent(
    role="Auction Discovery Specialist",
    goal="Scrape RealForeclose for upcoming auctions. Extract case numbers, plaintiffs, judgment amounts.",
    backstory="""You monitor brevard.realforeclose.com daily for new foreclosure listings.
    You identify which auctions are worth analyzing based on judgment amounts and property types.""",
    tools=[realforeclose_scraper, auction_calendar],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)

# Agent 2: Scraper Agent  
scraper_agent = Agent(
    role="Property Data Specialist",
    goal="Gather property details from BCPAO, photos, parcel boundaries, and ownership history.",
    backstory="""You are an expert at extracting data from Brevard County Property Appraiser.
    You use anti-detection techniques and can parse PDF documents with BECA scraping.""",
    tools=[bcpao_scraper, beca_scraper, photo_extractor],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)

# Agent 3: Title Agent
title_agent = Agent(
    role="Title Search Specialist",
    goal="Search AcclaimWeb for all recorded liens, mortgages, and encumbrances.",
    backstory="""You perform comprehensive title searches on vaclmweb1.brevardclerk.us.
    You identify all parties with recorded interests in the property.""",
    tools=[acclaimweb_scraper, party_name_search, document_retriever],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)

# Agent 4: Lien Priority Agent (CRITICAL - uses Opus)
lien_priority_agent = Agent(
    role="Lien Priority Analyst",
    goal="""Determine lien priority and identify scenarios where senior liens survive foreclosure.
    CRITICAL: Detect HOA foreclosures where first mortgage survives.""",
    backstory="""You are a Florida foreclosure law expert. You understand that:
    - Mortgage foreclosures wipe junior liens
    - HOA foreclosures do NOT wipe senior mortgages
    - Tax deed sales have different priority rules
    You NEVER guess - you only report findings from actual recorded documents.""",
    tools=[lien_priority_calculator, senior_mortgage_detector],
    llm="anthropic/claude-opus-4-5-20251101",  # PREMIUM - high stakes reasoning
    verbose=True,
    max_iter=3
)

# Agent 5: Tax Certificate Agent
tax_agent = Agent(
    role="Tax Certificate Specialist",
    goal="Check RealTDM for outstanding tax certificates and delinquent taxes.",
    backstory="""You search the tax collector's records for any outstanding certificates
    that could affect title or require additional payoff at closing.""",
    tools=[realtdm_scraper, tax_calculator],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)

# Agent 6: Demographics Agent
demographics_agent = Agent(
    role="Neighborhood Analyst",
    goal="Analyze Census data for income levels, vacancy rates, and market indicators.",
    backstory="""You provide neighborhood context using Census API data.
    You identify optimal zip codes for investment based on income and vacancy metrics.""",
    tools=[census_api, neighborhood_scorer],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)

# Agent 7: ML Prediction Agent
ml_agent = Agent(
    role="ML Prediction Specialist",
    goal="Run XGBoost model to predict third-party purchase probability and sale prices.",
    backstory="""You operate the BidDeed.AI ML model (64.4% accuracy).
    You track 28 plaintiff patterns and generate probability scores.""",
    tools=[xgboost_predictor, plaintiff_analyzer],
    llm="deepseek/deepseek-chat",  # ULTRA_CHEAP tier
    verbose=True
)

# Agent 8: Valuation Agent
valuation_agent = Agent(
    role="Property Valuation Expert",
    goal="""Calculate max bid using formula:
    (ARV × 70%) - Repairs - $10K - MIN($25K, 15% × ARV)""",
    backstory="""You calculate After Repair Value and estimate repairs.
    You apply the Everest Capital max bid formula consistently.""",
    tools=[arv_calculator, repair_estimator, max_bid_formula],
    llm="anthropic/claude-sonnet-4-5-20250929",  # BALANCED - financial calculations
    verbose=True
)

# Agent 9: Decision Agent
decision_agent = Agent(
    role="Bid Decision Maker",
    goal="""Apply bid/judgment ratio thresholds:
    - ≥75% = BID
    - 60-74% = REVIEW  
    - <60% = SKIP""",
    backstory="""You make final BID/REVIEW/SKIP recommendations based on 
    risk-adjusted returns and lien priority analysis.""",
    tools=[decision_logger, risk_scorer],
    llm="anthropic/claude-sonnet-4-5-20250929",  # BALANCED
    verbose=True
)

# Agent 10: Report Agent
report_agent = Agent(
    role="Report Generation Specialist",
    goal="Generate one-page DOCX reports with BCPAO photos and ML predictions.",
    backstory="""You create professional auction analysis reports using the
    BidDeed.AI template with color-coded recommendations.""",
    tools=[docx_generator, photo_inserter, pdf_converter],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)

# Agent 11: Disposition Agent
disposition_agent = Agent(
    role="Post-Auction Tracker",
    goal="Track auction outcomes and update historical database.",
    backstory="""You monitor auction results and record actual sale prices,
    winning bidders, and outcome accuracy for ML model training.""",
    tools=[outcome_tracker, database_updater],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)

# Agent 12: Archive Agent
archive_agent = Agent(
    role="Data Archive Specialist",
    goal="Store completed analyses in historical_auctions table for future ML training.",
    backstory="""You maintain the historical_auctions table (1,393+ rows) and
    ensure data quality for continuous model improvement.""",
    tools=[supabase_inserter, data_validator],
    llm="gemini/gemini-2.5-flash",  # FREE tier
    verbose=True
)
```

### Crew Assembly

```python
# BidDeed.AI Crew (12-Stage Pipeline)
biddeed_crew = Crew(
    agents=[
        discovery_agent,      # Stage 1
        scraper_agent,        # Stage 2
        title_agent,          # Stage 3
        lien_priority_agent,  # Stage 4 (CRITICAL)
        tax_agent,            # Stage 5
        demographics_agent,   # Stage 6
        ml_agent,             # Stage 7
        valuation_agent,      # Stage 8
        decision_agent,       # Stage 9
        report_agent,         # Stage 10
        disposition_agent,    # Stage 11
        archive_agent         # Stage 12
    ],
    tasks=[
        discovery_task, scraper_task, title_task, lien_task,
        tax_task, demographics_task, ml_task, valuation_task,
        decision_task, report_task, disposition_task, archive_task
    ],
    process=Process.sequential,
    verbose=2,
    memory=True
)

# Execute for auction date
result = biddeed_crew.kickoff(inputs={
    "auction_date": "2026-01-21",
    "county": "brevard"
})
```

---

## LangGraph State Management

Both platforms use LangGraph for state persistence:

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver

# Supabase checkpoint configuration
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://postgres:...@mocerqjnksmhcjzxrewo.supabase.co:5432/postgres"
)

# State schema
class AuctionState(TypedDict):
    parcel_id: str
    case_number: str
    judgment_amount: float
    liens: list[dict]
    arv: float
    max_bid: float
    recommendation: Literal["BID", "REVIEW", "SKIP"]
    report_url: str
    
# Workflow with checkpoints
workflow = StateGraph(AuctionState)
workflow.add_node("crew", lambda s: biddeed_crew.kickoff(s))
workflow.set_entry_point("crew")

# Compile with persistence
app = workflow.compile(checkpointer=checkpointer)

# Execute with thread_id for resumability
result = app.invoke(
    {"parcel_id": "12-34-56-78-90"},
    config={"configurable": {"thread_id": "auction-2026-01-21"}}
)
```

---

## ChatDev Patterns Integration

Both crews implement ChatDev review patterns:

```python
# Pattern 1: Loop counters (max 3 iterations)
code_review_agent = Agent(
    ...
    max_iter=3,  # Stop after 3 review cycles
)

# Pattern 2: Approval signals
qa_task = Task(
    description="""...\nSignal '<INFO> Finished' when approved.""",
    ...
)

# Pattern 3: Dual-language communication (for debugging)
# Agents can output in both natural language and structured JSON
```

---

## Smart Router Configuration

```python
# router_config.py
ROUTER_TIERS = {
    "FREE": {
        "model": "gemini/gemini-2.5-flash",
        "cost": 0.0,
        "use_for": ["discovery", "scraping", "archiving", "reports"]
    },
    "ULTRA_CHEAP": {
        "model": "deepseek/deepseek-chat",  # V3.2
        "cost": 0.28,  # per 1M tokens
        "use_for": ["ml_predictions", "pattern_matching"]
    },
    "BALANCED": {
        "model": "anthropic/claude-sonnet-4-5-20250929",
        "cost": 3.0,  # per 1M tokens
        "use_for": ["valuation", "decision", "code_review"]
    },
    "PREMIUM": {
        "model": "anthropic/claude-opus-4-5-20251101",
        "cost": 15.0,  # per 1M tokens
        "use_for": ["lien_priority", "complex_legal_reasoning"]
    }
}

# Target: 90% FREE tier processing
```

---

## WebSocket Streaming (E2B Pattern)

```python
# FastAPI WebSocket endpoint
@router.websocket("/ws/analyze/{case_number}")
async def stream_analysis(websocket: WebSocket, case_number: str):
    await websocket.accept()
    
    crew = BidDeedCrew()
    
    async for event in crew.process_auction(case_number):
        await websocket.send_json({
            "type": "agent_update",
            "agent": event.agent_role,
            "message": event.message,
            "stage": event.stage,  # 1-12
            "artifact": event.artifact if event.artifact else None
        })
    
    await websocket.close()
```

---

## Deployment

### GitHub Actions (Daily 11 PM EST)

```yaml
# .github/workflows/daily_auction.yml
name: Daily Auction Analysis
on:
  schedule:
    - cron: '0 4 * * *'  # 11 PM EST = 4 AM UTC
  
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run BidDeed.AI Crew
        run: python -m biddeed.crew --counties brevard,orange,seminole
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

### Render.com (50+ Counties)

When multi-county exceeds 50 counties, deploy to Render for compute scaling:

```yaml
# render.yaml
services:
  - type: worker
    name: biddeed-crew
    runtime: python
    plan: standard
    buildCommand: pip install -r requirements.txt
    startCommand: python -m biddeed.crew --all-florida
```

---

## Metrics & Monitoring

Track in Supabase `daily_metrics` table:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| FREE tier % | 90% | <80% |
| Lien Priority accuracy | 95% | <90% |
| Report generation time | <30s | >60s |
| API cost per auction | <$0.50 | >$1.00 |
| ML prediction accuracy | 64.4% | <60% |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-15 | Initial CrewAI architecture |
| - | 2026-01-14 | ZoneWise CrewAI design decision |
| - | 2025-12 | BidDeed.AI V13.4.0 12-stage pipeline |

---

*This document is the source of truth for multi-agent architecture across both platforms.*
