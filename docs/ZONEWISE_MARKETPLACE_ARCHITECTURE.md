# ZoneWise Marketplace Architecture
**Version:** 1.0.0  
**Date:** January 13, 2026  
**AI Architect:** Claude Sonnet 4.5  
**Pattern Source:** obra/superpowers-marketplace analysis

---

## Executive Summary

ZoneWise implements a **jurisdiction-as-plugin** marketplace architecture to handle the heterogeneous requirements of 17+ Brevard County jurisdictions. Unlike BidDeed.AI's uniform multi-county approach (same pipeline, different data sources), ZoneWise faces genuinely different workflows, submittal processes, and regulatory requirements per jurisdiction.

**Core Insight:** Jurisdictions aren't just configuration changes - they're distinct orchestration graphs requiring modular, versioned plugins.

---

## Architecture Overview

### Three-Layer System

```
┌─────────────────────────────────────────────────────────┐
│              ZONEWISE MARKETPLACE LAYER                  │
│  - Jurisdiction Registry (registry.json)                │
│  - Version Management (semver)                           │
│  - Plugin Discovery & Installation                       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              CORE ORCHESTRATOR LAYER                     │
│  - 12-Stage SPD Pipeline (Discovery → Approval)         │
│  - LangGraph Base Graphs                                │
│  - Shared Nodes (Firecrawl, Claude API, Supabase)      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│           JURISDICTION PLUGIN LAYER                      │
│  - Custom Workflow Implementations                       │
│  - Jurisdiction-Specific Scrapers                        │
│  - Submittal Format Handlers                            │
│  - Regulatory Logic                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Jurisdiction Registry (`registry.json`)

**Purpose:** Central metadata store for all supported jurisdictions

```json
{
  "version": "1.0.0",
  "last_updated": "2026-01-13T00:00:00Z",
  "jurisdictions": {
    "melbourne": {
      "repo": "breverdbidder/zonewise-melbourne",
      "version": "1.2.0",
      "display_name": "City of Melbourne",
      "contact": {
        "department": "Planning & Zoning",
        "phone": "321-608-7500",
        "email": "planningandzoning@melbourneflorida.org"
      },
      "workflows": {
        "submittal": "electronic",
        "plan_review": "multi-stage",
        "approval": "commission"
      },
      "firecrawl": {
        "base_url": "https://www.melbourneflorida.org/departments/planning-zoning",
        "patterns": [
          "/site-plan-review",
          "/zoning-applications",
          "/development-standards"
        ]
      },
      "fees": {
        "base_application": 750,
        "per_acre": 100,
        "plan_review": 500
      },
      "timeline": {
        "initial_review_days": 30,
        "total_approval_days": 90
      },
      "requirements": {
        "traffic_study_threshold_units": 50,
        "environmental_review_required": true,
        "pre_application_meeting_required": true
      }
    },
    "titusville": {
      "repo": "breverdbidder/zonewise-titusville",
      "version": "1.0.0",
      "display_name": "City of Titusville",
      "contact": {
        "department": "Community Development",
        "phone": "321-567-3702",
        "email": "planning@titusville.com"
      },
      "workflows": {
        "submittal": "in-person",
        "plan_review": "single-stage",
        "approval": "staff-level"
      },
      "firecrawl": {
        "base_url": "https://www.titusville.com/departments/community_development",
        "patterns": [
          "/site-plan",
          "/land-development"
        ]
      },
      "fees": {
        "base_application": 500,
        "per_acre": 75,
        "plan_review": 350
      },
      "timeline": {
        "initial_review_days": 21,
        "total_approval_days": 60
      },
      "requirements": {
        "traffic_study_threshold_units": 100,
        "environmental_review_required": false,
        "pre_application_meeting_required": false
      }
    },
    "unincorporated-brevard": {
      "repo": "breverdbidder/zonewise-unincorporated",
      "version": "1.1.0",
      "display_name": "Unincorporated Brevard County",
      "contact": {
        "department": "Planning & Development",
        "phone": "321-633-2069",
        "email": "planning@brevardfl.gov"
      },
      "workflows": {
        "submittal": "electronic",
        "plan_review": "multi-department",
        "approval": "planning-board"
      },
      "firecrawl": {
        "base_url": "https://www.brevardfl.gov/PlanningAndDevelopment",
        "patterns": [
          "/SitePlanReview",
          "/DevelopmentReview",
          "/LandDevelopmentCode"
        ]
      },
      "fees": {
        "base_application": 1000,
        "per_acre": 150,
        "plan_review": 750
      },
      "timeline": {
        "initial_review_days": 45,
        "total_approval_days": 120
      },
      "requirements": {
        "traffic_study_threshold_units": 25,
        "environmental_review_required": true,
        "pre_application_meeting_required": true,
        "concurrency_review_required": true
      }
    },
    "cocoa-beach": {
      "repo": "breverdbidder/zonewise-cocoa-beach",
      "version": "0.9.0",
      "display_name": "City of Cocoa Beach",
      "status": "beta",
      "contact": {
        "department": "Planning & Development Services",
        "phone": "321-868-3258",
        "email": "planning@cityofcocoabeach.com"
      },
      "workflows": {
        "submittal": "electronic",
        "plan_review": "single-stage",
        "approval": "city-commission"
      },
      "firecrawl": {
        "base_url": "https://www.cityofcocoabeach.com/planning",
        "patterns": [
          "/site-development",
          "/land-use"
        ]
      },
      "fees": {
        "base_application": 650,
        "per_acre": 85,
        "plan_review": 400
      },
      "timeline": {
        "initial_review_days": 30,
        "total_approval_days": 75
      },
      "requirements": {
        "traffic_study_threshold_units": 75,
        "environmental_review_required": true,
        "coastal_zone_compliance": true,
        "pre_application_meeting_required": false
      }
    }
  }
}
```

---

## 2. Core Orchestrator Layer

**Repository:** `breverdbidder/zonewise`  
**Purpose:** Shared 12-stage SPD pipeline base

### 12-Stage SPD Pipeline

```python
# core/orchestrator/spd_pipeline.py

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import AnyMessage
import operator

class SPDState(TypedDict):
    """Base state for all jurisdictions - extended by plugins"""
    project_id: str
    jurisdiction: str
    messages: Annotated[list[AnyMessage], operator.add]
    current_stage: int
    stage_results: dict
    errors: list
    
    # Stage-specific data (populated by jurisdiction plugins)
    discovery_data: dict
    scraping_results: dict
    requirement_analysis: dict
    document_prep: dict
    submittal_package: dict
    plan_review_tracking: dict
    revision_rounds: list
    fee_calculations: dict
    approval_status: dict
    timeline_tracking: dict
    compliance_checks: dict
    final_approval: dict

# Shared nodes used by all jurisdictions
from core.nodes.discovery_node import discovery_node
from core.nodes.firecrawl_node import firecrawl_scraper
from core.nodes.requirement_analysis import analyze_requirements
from core.nodes.document_prep import prepare_documents
from core.nodes.fee_calculator import calculate_fees
from core.nodes.compliance_checker import check_compliance
from core.nodes.error_handler import handle_error

def create_base_graph() -> StateGraph:
    """Creates base SPD pipeline graph - extended by jurisdiction plugins"""
    graph = StateGraph(SPDState)
    
    # Add shared nodes
    graph.add_node("discovery", discovery_node)
    graph.add_node("scraping", firecrawl_scraper)
    graph.add_node("requirement_analysis", analyze_requirements)
    graph.add_node("document_prep", prepare_documents)
    graph.add_node("fee_calculation", calculate_fees)
    graph.add_node("compliance_check", check_compliance)
    graph.add_node("error", handle_error)
    
    # Base edges (jurisdiction plugins add custom edges)
    graph.set_entry_point("discovery")
    graph.add_edge("discovery", "scraping")
    graph.add_edge("scraping", "requirement_analysis")
    
    return graph
```

---

## 3. Jurisdiction Plugin Layer

**Pattern:** Each jurisdiction = separate repo implementing plugin interface

### Plugin Interface

```python
# core/interfaces/jurisdiction_plugin.py

from abc import ABC, abstractmethod
from typing import Dict, Any
from langgraph.graph import StateGraph

class JurisdictionPlugin(ABC):
    """Interface that all jurisdiction plugins must implement"""
    
    @property
    @abstractmethod
    def jurisdiction_id(self) -> str:
        """Unique identifier matching registry.json"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Semver version (e.g., '1.2.0')"""
        pass
    
    @abstractmethod
    def extend_state(self, base_state: Dict) -> Dict:
        """Add jurisdiction-specific state fields"""
        pass
    
    @abstractmethod
    def extend_graph(self, base_graph: StateGraph) -> StateGraph:
        """Add jurisdiction-specific nodes and edges"""
        pass
    
    @abstractmethod
    def validate_requirements(self, project_data: Dict) -> Dict[str, Any]:
        """Check project meets jurisdiction requirements"""
        pass
    
    @abstractmethod
    def format_submittal(self, documents: Dict) -> bytes:
        """Format documents per jurisdiction specs"""
        pass
    
    @abstractmethod
    def parse_review_response(self, response: str) -> Dict:
        """Parse jurisdiction's review comments"""
        pass
```

### Example: Melbourne Plugin (Abbreviated)

```python
# zonewise-melbourne/melbourne_plugin.py

from core.interfaces.jurisdiction_plugin import JurisdictionPlugin
from langgraph.graph import StateGraph
from typing import Dict, Any

class MelbournePlugin(JurisdictionPlugin):
    
    @property
    def jurisdiction_id(self) -> str:
        return "melbourne"
    
    @property
    def version(self) -> str:
        return "1.2.0"
    
    def extend_graph(self, base_graph: StateGraph) -> StateGraph:
        """Add Melbourne's multi-stage review workflow"""
        
        # Add Melbourne-specific nodes
        base_graph.add_node("pre_app_meeting", self.schedule_pre_app)
        base_graph.add_node("traffic_study", self.commission_traffic_study)
        base_graph.add_node("environmental_review", self.conduct_env_review)
        base_graph.add_node("electronic_submittal", self.submit_electronic)
        
        # Add conditional routing
        base_graph.add_conditional_edges(
            "requirement_analysis",
            self.check_pre_app_required,
            {
                "required": "pre_app_meeting",
                "not_required": "document_prep"
            }
        )
        
        return base_graph
    
    def validate_requirements(self, project_data: Dict) -> Dict[str, Any]:
        """Melbourne-specific validation"""
        validation = {"valid": True, "errors": [], "warnings": []}
        
        # Check unit threshold for traffic study
        if project_data.get("units", 0) >= 50:
            if "traffic_study" not in project_data.get("documents", []):
                validation["errors"].append(
                    "Traffic study required for projects ≥50 units"
                )
                validation["valid"] = False
        
        return validation
```

---

## 4. Plugin Management CLI

```python
# cli/zonewise_cli.py

import click
import json
import requests
from pathlib import Path

REGISTRY_URL = "https://raw.githubusercontent.com/breverdbidder/zonewise/main/registry.json"

@click.group()
def cli():
    """ZoneWise Jurisdiction Plugin Manager"""
    pass

@cli.command()
@click.option('--jurisdiction', '-j', required=True)
@click.option('--version', '-v', default='latest')
def install(jurisdiction: str, version: str):
    """Install a jurisdiction plugin"""
    
    registry = requests.get(REGISTRY_URL).json()
    
    if jurisdiction not in registry['jurisdictions']:
        click.echo(f"❌ Jurisdiction '{jurisdiction}' not found")
        return
    
    jur_config = registry['jurisdictions'][jurisdiction]
    target_version = jur_config['version'] if version == 'latest' else version
    
    click.echo(f"📦 Installing {jur_config['display_name']} v{target_version}...")
    
    # Installation logic...
    
    click.echo(f"✅ Installed {jurisdiction} v{target_version}")

@cli.command()
def list():
    """List available jurisdictions"""
    
    registry = requests.get(REGISTRY_URL).json()
    
    click.echo("\n📍 Available Jurisdictions:\n")
    
    for jur_id, config in registry['jurisdictions'].items():
        status = config.get('status', 'stable')
        status_icon = "🟢" if status == "stable" else "🟡"
        
        click.echo(f"{status_icon} {config['display_name']}")
        click.echo(f"   ID: {jur_id}")
        click.echo(f"   Version: {config['version']}")
        click.echo()
```

---

## Versioning Strategy

**Format:** `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes to plugin interface
- **MINOR:** New features, backward compatible
- **PATCH:** Bug fixes, documentation

**Release Channels:**
- `stable` - Production ready
- `beta` - Testing phase
- `alpha` - Development
- `experimental` - Proof of concept

---

## Deployment Architecture

### GitHub Actions Workflow

```yaml
# .github/workflows/jurisdiction_deploy.yml

name: Deploy Jurisdiction Plugin

on:
  workflow_dispatch:
    inputs:
      jurisdiction:
        description: 'Jurisdiction to deploy'
        required: true

jobs:
  test-plugin:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run plugin tests
        run: |
          pytest tests/plugins/${{ github.event.inputs.jurisdiction }}/ -v
  
  deploy-plugin:
    needs: test-plugin
    runs-on: ubuntu-latest
    steps:
      - name: Update registry
        run: |
          python scripts/update_registry.py \
            --jurisdiction ${{ github.event.inputs.jurisdiction }}
```

---

## Data Schema (Supabase)

```sql
-- Core project tracking
CREATE TABLE zonewise_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    plugin_version TEXT NOT NULL,
    status TEXT NOT NULL,
    current_stage INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Per-stage outputs
CREATE TABLE zonewise_stage_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES zonewise_projects(id),
    stage_number INT NOT NULL,
    result JSONB NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Plan review tracking
CREATE TABLE zonewise_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES zonewise_projects(id),
    review_number INT NOT NULL,
    status TEXT NOT NULL,
    comments JSONB DEFAULT '[]'::jsonb
);
```

---

## Cost Structure

### Development Costs (Per Jurisdiction)

| Phase | Hours | Cost @ $150/hr |
|-------|-------|----------------|
| Discovery & Requirements | 8 | $1,200 |
| Plugin Development | 16 | $2,400 |
| Testing & QA | 8 | $1,200 |
| Documentation | 4 | $600 |
| **Total** | **36** | **$5,400** |

### Operational Costs

- **Firecrawl:** $0.001/page × 50 pages = $0.05/scrape
- **Claude API:** ~$0.15/project (90% FREE Smart Router)
- **Supabase:** $25/month
- **GitHub Actions:** Free tier sufficient
- **Cloudflare Pages:** Free tier sufficient

**Monthly OpEx:** ~$30

---

## Rollout Plan

### Q1 2026: Core 5 Jurisdictions

| Jurisdiction | Priority | Launch Date |
|--------------|----------|-------------|
| Unincorporated Brevard | P0 | Jan 27 |
| Melbourne | P0 | Feb 3 |
| Titusville | P1 | Feb 10 |
| Cocoa Beach | P1 | Feb 17 |
| Palm Bay | P1 | Feb 24 |

### Q2 2026: Remaining 12

All 17 Brevard jurisdictions live by Jun 30, 2026.

---

## Success Metrics

### Plugin Quality
- Test Coverage: >80%
- Interface Compliance: 100%
- Error Rate: <5% per stage

### Operational
- Scraping Success: >95%
- API Latency: <2s per stage (p95)
- Cost Per Project: <$1

### Business
- Time to Approval: -30% by Q2
- Rejection Rate: -50% by Q2
- Developer Throughput: 2 → 8 projects/week
- ROI: >$10K saved per project

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Plugin interface changes | Medium | High | Semantic versioning |
| Website changes | High | Medium | Monitoring + updates |
| API rate limits | Low | Medium | Circuit breakers |
| Data privacy | Low | Critical | No PII storage |

---

## Future Enhancements

### Phase 2 (Q3 2026)
- Multi-state expansion (Orange, Polk)
- API Marketplace for 3rd party plugins
- White-label licensing

### Phase 3 (Q4 2026)
- Predictive approval scores
- Document intelligence (auto-extract)
- Timeline optimization
- Real-time compliance AI

---

## Appendix: BidDeed.AI vs ZoneWise

| Dimension | BidDeed.AI | ZoneWise |
|-----------|------------|----------|
| Domain | Foreclosure auctions | Site plans |
| Data uniformity | High | Low |
| Workflow variation | Minimal | High |
| Orchestration | Single graph | Plugin graphs |
| Expansion model | Config-driven | Plugin-driven |

**Key Insight:** BidDeed.AI uses multi-county *configuration*, ZoneWise uses multi-jurisdiction *plugins*.

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-13 | Claude Sonnet 4.5 | Initial |

**AI Architect:** Claude Sonnet 4.5  
**Target Repo:** breverdbidder/zonewise  
**Review Cycle:** Quarterly

---

**END OF DOCUMENT**
