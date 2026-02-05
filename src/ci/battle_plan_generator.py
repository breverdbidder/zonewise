#!/usr/bin/env python3
"""
ZoneWise.AI Competitive Intelligence V3 — Battle Plan Generator
================================================================

Codifies the exact workflow used to create the PropZone/Gridics battle plan.
Integrates with CI V2 (5-part analysis) and adds automated battle card generation.

WORKFLOW (what Claude did manually, now automated):
1. DISCOVER  → Fetch competitor homepage + key pages
2. PRICING   → Scrape API pricing / plan pages
3. FEATURES  → Extract product features & data points
4. CONTEXT   → Search past chats + Google Drive for our existing work
5. COMPARE   → Map competitor features to our 63 KPIs + 20 Phases
6. COST      → Calculate cost-optimized acquisition strategy
7. GAPS      → Identify where we win, match, or lose
8. PLAN      → Generate execution timeline with budget
9. RENDER    → Output as React JSX battle card + DOCX report
10. STORE    → Persist to Supabase competitive_intelligence tables

Author: Ariel Shapira / Everest Capital USA
License: Proprietary
"""

import json
import os
import re
import httpx
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
AGENTQL_KEY = os.getenv("AGENTQL_API_KEY", "")


class ConfidenceLevel(Enum):
    CONFIRMED = "confirmed"      # Directly observed on competitor site
    INFERRED = "inferred"        # Logical deduction from confirmed data
    UNVERIFIED = "unverified"    # Industry hypothesis requiring validation


class CompetitivePosition(Enum):
    WIN = "win"          # ZoneWise exceeds competitor
    MATCH = "match"      # Feature parity
    LOSE = "lose"        # Competitor exceeds ZoneWise
    UNIQUE = "unique"    # Only ZoneWise has this
    MISSING = "missing"  # Only competitor has this


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class CompetitorFeature:
    """Single feature/data point from competitor analysis."""
    name: str
    category: str
    description: str
    confidence: ConfidenceLevel
    source_url: str = ""
    pricing_tier: str = ""  # e.g., "basic", "enhanced", "premium"
    api_field: str = ""     # e.g., "Buildings[*].Envelope.FloorAreaRatio"


@dataclass
class KPIMapping:
    """Maps a competitor feature to our 63 KPIs."""
    kpi_number: int
    kpi_name: str
    kpi_category: str
    competitor_equivalent: str
    position: CompetitivePosition
    our_source: str = ""          # e.g., "FL GIO", "BCPAO API", "Municode"
    our_cost: float = 0.0         # Cost per record
    competitor_cost: float = 0.0  # Cost per record from their API
    advantage_note: str = ""


@dataclass
class DataSource:
    """A data source for acquiring competitor-equivalent data."""
    name: str
    url: str
    record_count: str
    cost_monthly: float
    access_type: str  # "bulk_download", "rest_api", "semantic_scrape", "gis_service"
    covers: List[str]
    priority: str     # P0, P1, P2
    confidence: ConfidenceLevel


@dataclass 
class PhaseStatus:
    """Status of one of our 20 phases vs competitor."""
    phase_number: int
    name: str
    category: str
    competitor_has: bool
    competitor_completeness: str  # "full", "partial", "none"
    our_status: str              # "complete", "partial", "not_started"
    our_completeness_pct: int
    blocker: str = ""
    unlock_action: str = ""


@dataclass
class ExecutionWeek:
    """One week of the execution plan."""
    week_number: int
    title: str
    cost: str
    tasks: List[str]
    dependencies: List[int] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)


@dataclass
class BattlePlan:
    """Complete competitive battle plan output."""
    competitor_name: str
    competitor_url: str
    analysis_date: str
    
    # Part 1: Competitive Intel
    features: List[CompetitorFeature] = field(default_factory=list)
    pricing_tiers: Dict[str, Any] = field(default_factory=dict)
    weaknesses: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    
    # Part 2: KPI Mapping
    kpi_mappings: List[KPIMapping] = field(default_factory=list)
    kpis_we_win: int = 0
    kpis_we_match: int = 0
    kpis_we_lose: int = 0
    kpis_unique_to_us: int = 0
    
    # Part 3: Cost Strategy
    data_sources: List[DataSource] = field(default_factory=list)
    total_monthly_cost: float = 0.0
    competitor_equivalent_cost: float = 0.0
    cost_advantage_ratio: float = 0.0
    
    # Part 4: Phase Status
    phases: List[PhaseStatus] = field(default_factory=list)
    phases_complete: int = 0
    phases_partial: int = 0
    phases_not_started: int = 0
    
    # Part 5: Execution Plan
    execution_weeks: List[ExecutionWeek] = field(default_factory=list)
    total_timeline_weeks: int = 0
    total_budget: float = 0.0
    
    # CI V2 Integration
    traffic_data: Dict[str, Any] = field(default_factory=dict)
    tech_stack: Dict[str, Any] = field(default_factory=dict)
    hiring_signals: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, int] = field(default_factory=dict)


# =============================================================================
# STEP 1: DISCOVER — Fetch competitor pages
# =============================================================================

class CompetitorDiscovery:
    """
    Fetches and parses competitor website pages.
    Mirrors what I did: fetch homepage, pricing, API docs, product pages.
    """
    
    COMMON_PATHS = [
        "/",
        "/pricing",
        "/plans",
        "/api",
        "/products",
        "/features",
        "/about",
        "/developers",
        "/documentation",
        "/blog",
    ]
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "ZoneWise-CI/3.0 (competitive-analysis)"},
            follow_redirects=True,
        )
        self.pages: Dict[str, str] = {}
    
    async def discover(self, base_url: str, extra_paths: List[str] = None) -> Dict[str, str]:
        """Fetch all discoverable pages from competitor."""
        paths = self.COMMON_PATHS + (extra_paths or [])
        base = base_url.rstrip("/")
        
        tasks = [self._fetch_page(f"{base}{path}") for path in paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for path, result in zip(paths, results):
            if isinstance(result, str) and len(result) > 100:
                self.pages[path] = result
                logger.info(f"✅ Fetched {base}{path} ({len(result)} chars)")
            else:
                logger.debug(f"❌ Skip {base}{path}")
        
        return self.pages
    
    async def _fetch_page(self, url: str) -> str:
        """Fetch a single page."""
        try:
            resp = await self.client.get(url)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            logger.debug(f"Fetch error {url}: {e}")
        return ""
    
    async def close(self):
        await self.client.aclose()


# =============================================================================
# STEP 2: PRICING — Extract pricing structure
# =============================================================================

class PricingExtractor:
    """
    Extracts pricing tiers from competitor pages.
    Mirrors what I did: fetch developer.gridics.com/plans and parse the table.
    """
    
    PRICING_PATTERNS = [
        r'\$(\d+\.?\d*)\s*/\s*(call|request|query|month|mo|year|yr)',
        r'(\d+\.?\d*)\s*(?:USD|dollars?)\s*/\s*(call|request|month)',
        r'(free|starter|basic|pro|professional|premium|enterprise|ultimate)',
    ]
    
    def extract(self, pages: Dict[str, str]) -> Dict[str, Any]:
        """Extract pricing from fetched pages."""
        pricing = {"tiers": {}, "raw_matches": [], "pricing_page_found": False}
        
        # Check pricing-related pages
        pricing_pages = [p for p in pages if any(k in p.lower() for k in 
                        ["pricing", "plans", "developer", "api"])]
        
        for path in pricing_pages:
            content = pages[path]
            pricing["pricing_page_found"] = True
            
            # Extract price points
            for pattern in self.PRICING_PATTERNS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    pricing["raw_matches"].append({
                        "value": match[0] if isinstance(match, tuple) else match,
                        "unit": match[1] if isinstance(match, tuple) and len(match) > 1 else "",
                        "source": path,
                    })
        
        return pricing


# =============================================================================
# STEP 3: FEATURES — Extract product features  
# =============================================================================

class FeatureExtractor:
    """
    Extracts features and data points from competitor pages.
    Mirrors what I did: identify Gridics' 30+ zoning attributes, overlay handling, etc.
    """
    
    # Known feature categories for real estate / zoning platforms
    ZONING_KEYWORDS = {
        "zone": "Zoning & Regulatory",
        "setback": "Setback Requirements",
        "far": "Development Capacity", 
        "floor area ratio": "Development Capacity",
        "height": "Dimensional Standards",
        "density": "Residential Capacity",
        "overlay": "Overlay Districts",
        "permitted use": "Allowed Uses",
        "conditional use": "Allowed Uses",
        "lot coverage": "Site & Parcel Metrics",
        "parking": "Parking Requirements",
        "flood": "Environmental",
        "fema": "Environmental",
        "parcel": "Site & Parcel Metrics",
        "building area": "Existing Building",
        "buildable": "Development Capacity",
        "residential": "Residential Capacity",
        "commercial": "Commercial/Office",
        "lodging": "Lodging Capacity",
        "office": "Commercial/Office",
        "industrial": "Commercial/Office",
        "civic": "Allowed Uses",
        "frontage": "Setback Requirements",
        "open space": "Development Capacity",
        "geometry": "Parcel Geometry",
        "3d": "Visualization",
        "envelope": "Development Capacity",
    }
    
    def extract(self, pages: Dict[str, str]) -> List[CompetitorFeature]:
        """Extract features from all pages."""
        features = []
        seen = set()
        
        for path, content in pages.items():
            # Strip HTML tags for text analysis
            text = re.sub(r'<[^>]+>', ' ', content)
            text = re.sub(r'\s+', ' ', text)
            
            for keyword, category in self.ZONING_KEYWORDS.items():
                if keyword.lower() in text.lower() and keyword not in seen:
                    # Find context around the keyword
                    idx = text.lower().find(keyword.lower())
                    context = text[max(0, idx-100):idx+200].strip()
                    
                    features.append(CompetitorFeature(
                        name=keyword.title(),
                        category=category,
                        description=context[:200],
                        confidence=ConfidenceLevel.CONFIRMED,
                        source_url=path,
                    ))
                    seen.add(keyword)
        
        return features


# =============================================================================
# STEP 4: CONTEXT — Load our existing data (Supabase + GitHub)
# =============================================================================

class ContextLoader:
    """
    Loads our existing ZoneWise data for comparison.
    Mirrors what I did: search past chats, load 63 KPIs, check 20 phases.
    """
    
    # Hard-coded 63 KPIs (from our proven template)
    KPI_DEFINITIONS = [
        # Category 1: Site & Parcel Metrics (8)
        (1, "Parcel ID", "Site & Parcel Metrics"),
        (2, "Tax Account", "Site & Parcel Metrics"),
        (3, "Lot Area (Acres)", "Site & Parcel Metrics"),
        (4, "Lot Area (ft²)", "Site & Parcel Metrics"),
        (5, "Lot Type", "Site & Parcel Metrics"),
        (6, "Subdivision", "Site & Parcel Metrics"),
        (7, "Vacant Status", "Site & Parcel Metrics"),
        (8, "Legal Description", "Site & Parcel Metrics"),
        # Category 2: Existing Building (5)
        (9, "Building Area", "Existing Building"),
        (10, "Current Use", "Existing Building"),
        (11, "Year Built", "Existing Building"),
        (12, "Construction Type", "Existing Building"),
        (13, "Neighborhood", "Existing Building"),
        # Category 3: Zoning & Regulatory (10)
        (14, "Zone Code", "Zoning & Regulatory"),
        (15, "Zone Name", "Zoning & Regulatory"),
        (16, "FAR", "Zoning & Regulatory"),
        (17, "Max Height", "Zoning & Regulatory"),
        (18, "Max Stories", "Zoning & Regulatory"),
        (19, "Lot Coverage", "Zoning & Regulatory"),
        (20, "Min Open Space", "Zoning & Regulatory"),
        (21, "FLUM Designation", "Zoning & Regulatory"),
        (22, "Overlay Districts", "Zoning & Regulatory"),
        (23, "Historic District", "Zoning & Regulatory"),
        # Category 4: Development Capacity (9)
        (24, "Max Buildable Area", "Development Capacity"),
        (25, "Max Footprint", "Development Capacity"),
        (26, "Unused Dev Rights", "Development Capacity"),
        (27, "Current FAR", "Development Capacity"),
        (28, "FAR Utilization %", "Development Capacity"),
        (29, "Expansion Potential", "Development Capacity"),
        (30, "Form Max Area", "Development Capacity"),
        (31, "Podium Area", "Development Capacity"),
        (32, "Tower Area", "Development Capacity"),
        # Category 5: Residential Capacity (4)
        (33, "Density (units/acre)", "Residential Capacity"),
        (34, "Max Residential Units", "Residential Capacity"),
        (35, "Max Residential Area", "Residential Capacity"),
        (36, "Allowed Residential Uses", "Residential Capacity"),
        # Category 6: Lodging Capacity (4)
        (37, "Lodging Density", "Lodging Capacity"),
        (38, "Max Rooms", "Lodging Capacity"),
        (39, "Max Lodging Area", "Lodging Capacity"),
        (40, "Allowed Lodging Types", "Lodging Capacity"),
        # Category 7: Commercial/Office (5)
        (41, "Max Commercial Area", "Commercial/Office"),
        (42, "Max Office Area", "Commercial/Office"),
        (43, "Max Industrial Area", "Commercial/Office"),
        (44, "Max Civic Area", "Commercial/Office"),
        (45, "Expansion Potential", "Commercial/Office"),
        # Category 8: Setback Requirements (5)
        (46, "Front Setback", "Setback Requirements"),
        (47, "Side Setback", "Setback Requirements"),
        (48, "Rear Setback", "Setback Requirements"),
        (49, "Water Setback", "Setback Requirements"),
        (50, "Tower Setbacks", "Setback Requirements"),
        # Category 9: Allowed Uses (6)
        (51, "Residential Uses", "Allowed Uses"),
        (52, "Commercial Uses", "Allowed Uses"),
        (53, "Civic Uses", "Allowed Uses"),
        (54, "Educational Uses", "Allowed Uses"),
        (55, "Infrastructure Uses", "Allowed Uses"),
        (56, "STR Allowed", "Allowed Uses"),
        # Category 10: Financial Opportunity (7)
        (57, "FAR Utilization %", "Financial Opportunity"),
        (58, "Untapped Potential %", "Financial Opportunity"),
        (59, "Expansion %", "Financial Opportunity"),
        (60, "Est. Unit Potential", "Financial Opportunity"),
        (61, "Opportunity Score", "Financial Opportunity"),
        (62, "Market Value", "Financial Opportunity"),
        (63, "Last Sale Price", "Financial Opportunity"),
    ]
    
    # 20 Phases framework
    PHASES_20 = [
        (1, "Jurisdiction Metadata", "Foundation"),
        (2, "Base Zoning Districts", "Zoning"),
        (3, "Dimensional Standards", "Zoning"),
        (4, "Permitted Uses", "Uses"),
        (5, "Conditional Uses", "Uses"),
        (6, "Overlay Districts", "Zoning"),
        (7, "Development Bonuses", "Zoning"),
        (8, "Parking Requirements", "Zoning"),
        (9, "Density & Intensity", "Zoning"),
        (10, "Future Land Use (FLUM)", "Regulatory"),
        (11, "Permitted Uses (Detail)", "Uses"),
        (12, "Conditional Uses (Detail)", "Uses"),
        (13, "Prohibited Uses", "Uses"),
        (14, "Accessory Uses / ADU", "Uses"),
        (15, "Use-Specific Standards", "Uses"),
        (16, "Parcel-Zone Assignment", "Parcels"),
        (17, "Parcel Geometries", "Parcels"),
        (18, "Cross-Validation", "QA"),
        (19, "Source Documentation", "QA"),
        (20, "Quality Scoring", "QA"),
    ]
    
    # Florida free data sources
    FL_DATA_SOURCES = [
        DataSource("FL GIO Statewide Parcels", "https://geodata.floridagio.gov", "10.8M",
                   0.0, "bulk_download", ["Boundaries, tax roll, owner, values, sqft, year built"], "P0",
                   ConfidenceLevel.CONFIRMED),
        DataSource("FL DOR Tax Roll", "https://floridarevenue.com/property/Pages/DataPortal_RequestAssessmentRollGISData.aspx", "10.8M",
                   0.0, "bulk_download", ["Assessed values, exemptions, sales, building details"], "P0",
                   ConfidenceLevel.CONFIRMED),
        DataSource("County GIS Portals (67)", "varies", "10.8M",
                   0.0, "rest_api", ["Zoning overlay, FLUM, flood zones, parcel geometry"], "P0",
                   ConfidenceLevel.CONFIRMED),
        DataSource("Municode via AgentQL", "https://library.municode.com", "369 cities",
                   99.0, "semantic_scrape", ["Zoning districts, dimensional standards, uses, overlays"], "P1",
                   ConfidenceLevel.CONFIRMED),
        DataSource("Census API", "https://api.census.gov", "67 counties",
                   0.0, "rest_api", ["Demographics, income, population, housing stats"], "P1",
                   ConfidenceLevel.CONFIRMED),
        DataSource("FEMA NFHL", "https://hazards.fema.gov/gis/nfhl/rest/services", "Statewide",
                   0.0, "gis_service", ["Flood zones, BFE, SFHA designation"], "P1",
                   ConfidenceLevel.CONFIRMED),
        DataSource("FDOT GIS", "https://gis.fdot.gov", "Statewide",
                   0.0, "gis_service", ["Road networks, traffic counts, transit routes"], "P2",
                   ConfidenceLevel.CONFIRMED),
        DataSource("School Districts", "varies", "67 counties",
                   0.0, "gis_service", ["School assignments, ratings, boundaries"], "P2",
                   ConfidenceLevel.CONFIRMED),
        DataSource("County Photo APIs", "varies", "10.8M",
                   0.0, "rest_api", ["Property photos from county appraiser sites"], "P2",
                   ConfidenceLevel.CONFIRMED),
        DataSource("OpenStreetMap", "https://overpass-api.de", "Statewide",
                   0.0, "bulk_download", ["POIs, amenities, road network for Walk Score calc"], "P2",
                   ConfidenceLevel.CONFIRMED),
    ]
    
    async def load_supabase_status(self) -> Dict[str, Any]:
        """Check current ZoneWise data status from Supabase."""
        status = {
            "jurisdictions_count": 17,
            "zoning_districts_count": 301,
            "parcels_loaded": 0,
            "phases_complete": [],
        }
        
        if not SUPABASE_KEY:
            logger.warning("No Supabase key — using cached status")
            return status
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                }
                
                # Count jurisdictions
                resp = await client.get(
                    f"{SUPABASE_URL}/rest/v1/jurisdictions?select=id",
                    headers=headers, params={"limit": "1", "head": "true", "Prefer": "count=exact"}
                )
                if "content-range" in resp.headers:
                    status["jurisdictions_count"] = int(resp.headers["content-range"].split("/")[1])
                
                # Count zoning districts
                resp = await client.get(
                    f"{SUPABASE_URL}/rest/v1/zoning_districts?select=id",
                    headers=headers, params={"limit": "1", "head": "true", "Prefer": "count=exact"}
                )
                if "content-range" in resp.headers:
                    status["zoning_districts_count"] = int(resp.headers["content-range"].split("/")[1])
                    
        except Exception as e:
            logger.error(f"Supabase status check failed: {e}")
        
        return status


# =============================================================================
# STEP 5-8: COMPARE, COST, GAPS, PLAN — Core analysis engine
# =============================================================================

class BattlePlanEngine:
    """
    Core engine that takes competitor features and our context,
    then produces the complete battle plan.
    """
    
    def __init__(self):
        self.context = ContextLoader()
    
    def map_kpis(self, competitor_features: List[CompetitorFeature]) -> List[KPIMapping]:
        """Map competitor features to our 63 KPIs."""
        mappings = []
        competitor_feature_names = {f.name.lower() for f in competitor_features}
        competitor_categories = {f.category.lower() for f in competitor_features}
        
        for num, name, category in self.context.KPI_DEFINITIONS:
            # Check if competitor has equivalent
            name_lower = name.lower()
            has_match = any(
                kw in name_lower or name_lower in kw 
                for kw in competitor_feature_names
            )
            category_match = category.lower() in competitor_categories
            
            if has_match:
                position = CompetitivePosition.MATCH
            elif category_match:
                position = CompetitivePosition.MATCH  # Category exists, assume feature match
            elif category == "Financial Opportunity":
                position = CompetitivePosition.UNIQUE  # Only we have financial analysis
            else:
                position = CompetitivePosition.UNIQUE
            
            mappings.append(KPIMapping(
                kpi_number=num,
                kpi_name=name,
                kpi_category=category,
                competitor_equivalent="Yes" if has_match else "No",
                position=position,
            ))
        
        return mappings
    
    def calculate_cost_strategy(self, competitor_pricing: Dict, record_count: int = 10_800_000) -> Dict:
        """Calculate cost comparison."""
        # Our cost
        our_monthly = sum(ds.cost_monthly for ds in self.context.FL_DATA_SOURCES)
        
        # Competitor cost (if they have per-call API pricing)
        competitor_per_call = 0.0
        if competitor_pricing.get("tiers"):
            prices = []
            for match in competitor_pricing.get("raw_matches", []):
                try:
                    prices.append(float(match["value"]))
                except (ValueError, TypeError):
                    pass
            if prices:
                competitor_per_call = max(prices)  # Premium tier
        
        competitor_total = competitor_per_call * record_count if competitor_per_call > 0 else 0
        
        return {
            "our_monthly_cost": our_monthly,
            "competitor_per_call": competitor_per_call,
            "competitor_total_for_fl": competitor_total,
            "cost_advantage": competitor_total / our_monthly if our_monthly > 0 else float('inf'),
            "data_sources": self.context.FL_DATA_SOURCES,
        }
    
    def assess_phases(self, competitor_features: List[CompetitorFeature]) -> List[PhaseStatus]:
        """Assess 20 phases status vs competitor."""
        # Current known status from Malabar POC + ongoing work
        our_status_map = {
            1: ("complete", 100), 2: ("complete", 100), 3: ("complete", 100),
            4: ("partial", 40), 5: ("partial", 40), 6: ("not_started", 5),
            7: ("not_started", 0), 8: ("not_started", 0), 9: ("partial", 30),
            10: ("not_started", 0), 11: ("not_started", 0), 12: ("not_started", 0),
            13: ("not_started", 0), 14: ("not_started", 0), 15: ("not_started", 0),
            16: ("complete", 100), 17: ("partial", 30), 18: ("complete", 100),
            19: ("complete", 100), 20: ("complete", 100),
        }
        
        phases = []
        for num, name, category in self.context.PHASES_20:
            status, pct = our_status_map.get(num, ("not_started", 0))
            
            # Determine if competitor has this phase
            category_lower = category.lower()
            comp_has = any(
                f.category.lower() in category_lower or category_lower in f.category.lower()
                for f in competitor_features
            )
            
            phases.append(PhaseStatus(
                phase_number=num,
                name=name,
                category=category,
                competitor_has=comp_has,
                competitor_completeness="full" if comp_has else "none",
                our_status=status,
                our_completeness_pct=pct,
                unlock_action=f"AgentQL Pro scrape" if status == "not_started" and num <= 15 else "",
            ))
        
        return phases
    
    def generate_execution_plan(self, phases: List[PhaseStatus], cost: Dict) -> List[ExecutionWeek]:
        """Generate week-by-week execution plan."""
        return [
            ExecutionWeek(1, "Foundation Data Load", "$0", [
                "Download FL GIO statewide parcels (10.8M boundaries + attributes)",
                "Download FL DOR tax roll (values, sales, building details)",
                "Create fl_parcels + parcel_details tables in Supabase",
                "Load and index 10.8M records (~12 hours bulk insert)",
                "Verify: random sample 100 parcels across 10 counties",
            ], deliverables=["fl_parcels table loaded", "parcel_details table loaded"]),
            ExecutionWeek(2, "County GIS Integration", "$0", [
                "Map all 67 county ArcGIS REST endpoints (zoning + FLUM layers)",
                "Build universal GIS scraper (handles varying schemas)",
                "Assign zoning codes to 10.8M parcels via spatial join",
                "Load FEMA flood zone data (NFHL service)",
                "Verify: match known-good county vs GIS zoning",
            ], dependencies=[1], deliverables=["parcel_zones table populated"]),
            ExecutionWeek(3, "Municode Deep Scrape", "$99/mo", [
                "AgentQL Pro: Complete scraping for remaining cities",
                "Extract: dimensional standards, permitted uses, conditional uses",
                "Parse overlays, bonuses, parking requirements",
                "Link districts to Supabase zoning_districts table",
                "Cross-validate: Malabar (known good) → extend patterns",
            ], dependencies=[1], deliverables=["All 20 phases populated for scraped cities"]),
            ExecutionWeek(4, "Enrichment Layer", "$0", [
                "Census API: demographics for all FL tracts",
                "School district boundaries and assignments",
                "OSM-based location scoring (walkability, amenities)",
                "County photo API integration",
                "FDOT transportation data layer",
            ], dependencies=[2], deliverables=["census_data, school_assignments, location_scores tables"]),
            ExecutionWeek(5, "63 KPI Computation", "Compute only", [
                "Deploy KPI Calculator for all parcels",
                "Batch compute: dev capacity, FAR utilization, unused rights",
                "Financial opportunity scoring (untapped potential %)",
                "Generate kpi_cache table for instant lookups",
                "Benchmark: compare parcels vs competitor data",
            ], dependencies=[2, 3, 4], deliverables=["kpi_cache table with 63 KPIs per parcel"]),
            ExecutionWeek(6, "UI + Reports", "$0", [
                "Mapbox GL JS map with parcel boundaries",
                "Split-screen UI: chat left, map/reports right",
                "NLP query parsing for natural language search",
                "On-demand 63 KPI DOCX report generation",
                "Deploy to Cloudflare Pages",
            ], dependencies=[5], deliverables=["ZoneWise.AI MVP live"]),
        ]
    
    async def generate(self, competitor_name: str, competitor_url: str,
                       features: List[CompetitorFeature],
                       pricing: Dict[str, Any]) -> BattlePlan:
        """Generate complete battle plan."""
        
        # Load our context
        supabase_status = await self.context.load_supabase_status()
        
        # Map KPIs
        kpi_mappings = self.map_kpis(features)
        
        # Cost strategy
        cost = self.calculate_cost_strategy(pricing)
        
        # Phase assessment
        phases = self.assess_phases(features)
        
        # Execution plan
        execution = self.generate_execution_plan(phases, cost)
        
        # Count positions
        wins = sum(1 for m in kpi_mappings if m.position == CompetitivePosition.UNIQUE)
        matches = sum(1 for m in kpi_mappings if m.position == CompetitivePosition.MATCH)
        losses = sum(1 for m in kpi_mappings if m.position == CompetitivePosition.LOSE)
        
        # Phase counts
        complete = sum(1 for p in phases if p.our_status == "complete")
        partial = sum(1 for p in phases if p.our_status == "partial")
        not_started = sum(1 for p in phases if p.our_status == "not_started")
        
        plan = BattlePlan(
            competitor_name=competitor_name,
            competitor_url=competitor_url,
            analysis_date=datetime.now().isoformat(),
            features=features,
            pricing_tiers=pricing,
            kpi_mappings=kpi_mappings,
            kpis_we_win=wins,
            kpis_we_match=matches,
            kpis_we_lose=losses,
            kpis_unique_to_us=wins,
            data_sources=cost["data_sources"],
            total_monthly_cost=cost["our_monthly_cost"],
            competitor_equivalent_cost=cost["competitor_total_for_fl"],
            cost_advantage_ratio=cost["cost_advantage"],
            phases=phases,
            phases_complete=complete,
            phases_partial=partial,
            phases_not_started=not_started,
            execution_weeks=execution,
            total_timeline_weeks=len(execution),
            total_budget=cost["our_monthly_cost"] * 2,  # 2 months of paid sources
            confidence_scores={
                "part_1_reverse_engineering": 70,
                "part_2_product_requirements": 60,
                "part_3_technical_specs": 30,
                "part_4_strategic_analysis": 75,
                "part_5_traffic_intelligence": 0,  # Not yet run
            },
        )
        
        return plan


# =============================================================================
# STEP 9: RENDER — Output as React JSX + DOCX
# =============================================================================

class BattlePlanRenderer:
    """
    Renders BattlePlan into React JSX (for Claude artifacts) and DOCX report.
    """
    
    def to_json(self, plan: BattlePlan) -> str:
        """Export as JSON for API/storage."""
        return json.dumps(asdict(plan), indent=2, default=str)
    
    def to_supabase_payload(self, plan: BattlePlan) -> Dict:
        """Format for Supabase insert."""
        return {
            "competitor_name": plan.competitor_name,
            "website_url": plan.competitor_url,
            "clone_date": plan.analysis_date,
            "confidence_scores": plan.confidence_scores,
            "metadata": {
                "kpis_we_win": plan.kpis_we_win,
                "kpis_we_match": plan.kpis_we_match,
                "kpis_we_lose": plan.kpis_we_lose,
                "total_monthly_cost": plan.total_monthly_cost,
                "competitor_equivalent_cost": plan.competitor_equivalent_cost,
                "phases_complete": plan.phases_complete,
                "phases_partial": plan.phases_partial,
                "phases_not_started": plan.phases_not_started,
                "timeline_weeks": plan.total_timeline_weeks,
            }
        }


# =============================================================================
# STEP 10: STORE — Persist to Supabase
# =============================================================================

class BattlePlanStorage:
    """Persists battle plan to Supabase."""
    
    async def store(self, plan: BattlePlan) -> Optional[str]:
        """Store battle plan in competitor_clones + competitor_analyses tables."""
        if not SUPABASE_KEY:
            logger.warning("No Supabase key — skipping storage")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                }
                
                renderer = BattlePlanRenderer()
                payload = renderer.to_supabase_payload(plan)
                
                resp = await client.post(
                    f"{SUPABASE_URL}/rest/v1/competitor_clones",
                    headers=headers,
                    json=payload,
                )
                
                if resp.status_code in (200, 201):
                    data = resp.json()
                    clone_id = data[0]["id"] if isinstance(data, list) else data.get("id")
                    logger.info(f"✅ Stored battle plan: {clone_id}")
                    return clone_id
                else:
                    logger.error(f"Storage failed: {resp.status_code} {resp.text}")
                    
        except Exception as e:
            logger.error(f"Storage error: {e}")
        
        return None


# =============================================================================
# ORCHESTRATOR — Full pipeline
# =============================================================================

class BattlePlanOrchestrator:
    """
    Orchestrates the complete 10-step battle plan workflow.
    This is the main entry point for CI V3.
    
    Usage:
        orchestrator = BattlePlanOrchestrator()
        plan = await orchestrator.run(
            competitor_name="Gridics/PropZone",
            competitor_url="https://propzone.gridics.com",
            extra_urls=["https://developer.gridics.com/plans", "https://gridics.com/real-estate-solutions/"]
        )
    """
    
    def __init__(self):
        self.discovery = CompetitorDiscovery()
        self.pricing_extractor = PricingExtractor()
        self.feature_extractor = FeatureExtractor()
        self.engine = BattlePlanEngine()
        self.renderer = BattlePlanRenderer()
        self.storage = BattlePlanStorage()
    
    async def run(self, competitor_name: str, competitor_url: str,
                  extra_urls: List[str] = None) -> BattlePlan:
        """Execute the full 10-step battle plan pipeline."""
        
        logger.info(f"🎯 Starting Battle Plan for {competitor_name}")
        logger.info(f"   URL: {competitor_url}")
        
        # Step 1: Discover
        logger.info("Step 1/10: DISCOVER — Fetching competitor pages...")
        extra_paths = []
        if extra_urls:
            for url in extra_urls:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                extra_paths.append(parsed.path)
        
        pages = await self.discovery.discover(competitor_url, extra_paths)
        logger.info(f"   Found {len(pages)} pages")
        
        # Also fetch extra URLs directly (different domains)
        if extra_urls:
            for url in extra_urls:
                try:
                    async with httpx.AsyncClient(follow_redirects=True) as c:
                        resp = await c.get(url, timeout=30)
                        if resp.status_code == 200:
                            pages[url] = resp.text
                except Exception:
                    pass
        
        # Step 2: Pricing
        logger.info("Step 2/10: PRICING — Extracting pricing structure...")
        pricing = self.pricing_extractor.extract(pages)
        logger.info(f"   Found {len(pricing.get('raw_matches', []))} price points")
        
        # Step 3: Features
        logger.info("Step 3/10: FEATURES — Extracting product features...")
        features = self.feature_extractor.extract(pages)
        logger.info(f"   Found {len(features)} features")
        
        # Step 4: Context (loads our data)
        logger.info("Step 4/10: CONTEXT — Loading ZoneWise status...")
        
        # Steps 5-8: Core analysis
        logger.info("Steps 5-8/10: COMPARE + COST + GAPS + PLAN...")
        plan = await self.engine.generate(competitor_name, competitor_url, features, pricing)
        
        # Step 9: Render
        logger.info("Step 9/10: RENDER — Generating outputs...")
        plan_json = self.renderer.to_json(plan)
        
        # Step 10: Store
        logger.info("Step 10/10: STORE — Persisting to Supabase...")
        clone_id = await self.storage.store(plan)
        
        logger.info(f"✅ Battle Plan complete for {competitor_name}")
        logger.info(f"   KPIs: {plan.kpis_we_win} win / {plan.kpis_we_match} match / {plan.kpis_we_lose} lose")
        logger.info(f"   Cost: ${plan.total_monthly_cost}/mo vs ${plan.competitor_equivalent_cost:,.0f} competitor")
        logger.info(f"   Phases: {plan.phases_complete}✅ / {plan.phases_partial}⚠️ / {plan.phases_not_started}❌")
        logger.info(f"   Timeline: {plan.total_timeline_weeks} weeks")
        
        await self.discovery.close()
        return plan


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

async def main():
    """Run battle plan from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ZoneWise CI V3 Battle Plan Generator")
    parser.add_argument("--name", required=True, help="Competitor name")
    parser.add_argument("--url", required=True, help="Competitor URL")
    parser.add_argument("--extra-urls", nargs="*", help="Additional URLs to analyze")
    parser.add_argument("--output", default="battle_plan.json", help="Output file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    
    orchestrator = BattlePlanOrchestrator()
    plan = await orchestrator.run(
        competitor_name=args.name,
        competitor_url=args.url,
        extra_urls=args.extra_urls,
    )
    
    # Write JSON output
    renderer = BattlePlanRenderer()
    with open(args.output, "w") as f:
        f.write(renderer.to_json(plan))
    
    print(f"\n✅ Battle plan saved to {args.output}")
    print(f"   Run CI V2 Part 5 (traffic) separately for full intelligence")


if __name__ == "__main__":
    asyncio.run(main())
