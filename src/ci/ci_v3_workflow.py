#!/usr/bin/env python3
"""
CI V3 Workflow — Integrates Battle Plan Generator with CI V2 5-Part Analysis
=============================================================================

This orchestrates the FULL competitive intelligence pipeline:

CI V2 (existing):
  Part 1: Surface Intelligence (website clone, tech detection)
  Part 2: Product Requirements Document (PRD)
  Part 3: Technical Specifications (PRS)
  Part 4: Strategic Analysis (SWOT, positioning)
  Part 5: Traffic & Market Intelligence (SimilarWeb, SEO)

CI V3 (new — codified from Claude's PropZone workflow):
  Part 6: Battle Plan Generation (KPI mapping, cost analysis, execution plan)
  Part 7: React Battle Card Rendering (interactive dashboard artifact)

The workflow runs all 7 parts and produces:
- JSON battle plan (Supabase storage)
- React JSX battle card (Claude artifact)
- DOCX competitive report (downloadable)
- Supabase records (competitor_clones + competitor_analyses)

Author: Ariel Shapira / Everest Capital USA
"""

import json
import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

# CI V3 imports
from battle_plan_generator import (
    BattlePlanOrchestrator,
    BattlePlan,
    BattlePlanRenderer,
    CompetitorDiscovery,
    ConfidenceLevel,
)

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


# =============================================================================
# CI V2 PARTS (Surface Intel, PRD, PRS, Strategic, Traffic)
# =============================================================================

@dataclass
class CIV2Result:
    """Result from one part of CI V2 analysis."""
    part_number: int
    part_name: str
    confidence: int  # 0-100
    findings: Dict[str, Any]
    recommendations: List[str]
    status: str  # "complete", "partial", "failed"


class TechStackDetector:
    """Part 1 enhancement: Detect competitor's tech stack from page source."""
    
    TECH_SIGNATURES = {
        # Frontend
        "react": ['"react"', "react.production", "_reactRootContainer", "__NEXT_DATA__"],
        "next.js": ["__NEXT_DATA__", "_next/static", "next/router"],
        "vue.js": ["__vue__", "vue.runtime", "v-if", "v-for"],
        "angular": ["ng-version", "angular.io", "ng-app"],
        "svelte": ["__svelte"],
        # Maps
        "mapbox": ["mapbox-gl", "api.mapbox.com", "mapboxgl"],
        "google_maps": ["maps.googleapis.com", "google.maps"],
        "leaflet": ["leaflet.js", "L.map"],
        "esri_arcgis": ["arcgis", "esri", "js.arcgis.com"],
        # Backend hints
        "django": ["csrfmiddlewaretoken", "django"],
        "rails": ["csrf-token", "data-turbo"],
        "node_express": ["x-powered-by: Express"],
        # Analytics
        "google_analytics": ["google-analytics.com", "gtag", "ga.js"],
        "segment": ["cdn.segment.com", "analytics.js"],
        "hotjar": ["hotjar.com"],
        # Hosting
        "cloudflare": ["cf-ray", "cloudflare"],
        "vercel": ["vercel", ".vercel.app"],
        "aws": ["amazonaws.com", "aws-"],
        "heroku": [".herokuapp.com"],
        # CMS / Other
        "wordpress": ["wp-content", "wp-includes"],
        "intercom": ["intercom.io", "intercomSettings"],
        "stripe": ["stripe.com", "Stripe"],
    }
    
    def detect(self, pages: Dict[str, str]) -> Dict[str, Any]:
        """Scan pages for technology signatures."""
        detected = {}
        all_content = " ".join(pages.values()).lower()
        
        for tech, signatures in self.TECH_SIGNATURES.items():
            matches = [sig for sig in signatures if sig.lower() in all_content]
            if matches:
                detected[tech] = {
                    "confidence": min(100, len(matches) * 40),
                    "signatures_found": matches,
                    "category": self._categorize(tech),
                }
        
        return detected
    
    def _categorize(self, tech: str) -> str:
        categories = {
            "react": "frontend", "next.js": "frontend", "vue.js": "frontend",
            "angular": "frontend", "svelte": "frontend",
            "mapbox": "mapping", "google_maps": "mapping", "leaflet": "mapping",
            "esri_arcgis": "mapping",
            "django": "backend", "rails": "backend", "node_express": "backend",
            "google_analytics": "analytics", "segment": "analytics", "hotjar": "analytics",
            "cloudflare": "hosting", "vercel": "hosting", "aws": "hosting", "heroku": "hosting",
            "wordpress": "cms", "intercom": "support", "stripe": "payments",
        }
        return categories.get(tech, "other")


class TrafficIntelligence:
    """Part 5: Traffic and market intelligence."""
    
    async def analyze(self, competitor_url: str) -> Dict[str, Any]:
        """
        Gather traffic intelligence. 
        Free sources: BuiltWith, Wayback, hiring pages.
        Paid: SimilarWeb API (if key available).
        """
        import httpx
        
        results = {
            "monthly_visits_estimate": "Unknown (requires SimilarWeb API)",
            "top_countries": [],
            "traffic_sources": {},
            "technology_profile_url": "",
            "hiring_signals": [],
            "wayback_snapshots": 0,
        }
        
        domain = competitor_url.replace("https://", "").replace("http://", "").split("/")[0]
        
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                # BuiltWith (free basic info)
                results["technology_profile_url"] = f"https://builtwith.com/{domain}"
                
                # Wayback Machine CDX API (count snapshots)
                try:
                    resp = await client.get(
                        f"http://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=1&fl=timestamp",
                        timeout=10
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results["wayback_snapshots"] = len(data) - 1  # minus header
                        if len(data) > 1:
                            results["first_seen"] = data[1][0][:8]  # YYYYMMDD
                except Exception:
                    pass
                
                # Check for careers/jobs page (hiring signals)
                for path in ["/careers", "/jobs", "/about/careers", "/company/careers"]:
                    try:
                        resp = await client.get(f"https://{domain}{path}", timeout=10)
                        if resp.status_code == 200 and len(resp.text) > 500:
                            results["hiring_signals"].append(f"Active careers page at {path}")
                            # Look for tech keywords in job listings
                            text = resp.text.lower()
                            for tech in ["python", "react", "node", "aws", "postgresql", "gis", "mapbox"]:
                                if tech in text:
                                    results["hiring_signals"].append(f"Hiring for: {tech}")
                            break
                    except Exception:
                        continue
                
        except Exception as e:
            logger.error(f"Traffic intel error: {e}")
        
        return results


# =============================================================================
# CI V3 FULL WORKFLOW
# =============================================================================

class CIV3Workflow:
    """
    Complete CI V3 workflow: runs CI V2 (5 parts) + CI V3 (battle plan + battle card).
    
    Usage:
        workflow = CIV3Workflow()
        result = await workflow.execute(
            competitor_name="Gridics/PropZone",
            competitor_url="https://propzone.gridics.com",
            extra_urls=["https://developer.gridics.com/plans"],
            our_product="ZoneWise.AI",
        )
    """
    
    def __init__(self):
        self.battle_plan_orchestrator = BattlePlanOrchestrator()
        self.tech_detector = TechStackDetector()
        self.traffic_intel = TrafficIntelligence()
    
    async def execute(
        self,
        competitor_name: str,
        competitor_url: str,
        extra_urls: List[str] = None,
        our_product: str = "ZoneWise.AI",
        skip_traffic: bool = False,
    ) -> Dict[str, Any]:
        """Execute complete CI V3 pipeline."""
        
        start_time = datetime.now()
        results = {
            "competitor": competitor_name,
            "url": competitor_url,
            "analysis_date": start_time.isoformat(),
            "parts": {},
            "battle_plan": None,
            "execution_time_seconds": 0,
        }
        
        # ─── PART 1: Surface Intelligence (tech stack + page discovery) ───
        logger.info("═══ PART 1: Surface Intelligence ═══")
        discovery = CompetitorDiscovery()
        extra_paths = []
        if extra_urls:
            from urllib.parse import urlparse
            for url in extra_urls:
                extra_paths.append(urlparse(url).path)
        
        pages = await discovery.discover(competitor_url, extra_paths)
        
        # Fetch extra-domain URLs too
        if extra_urls:
            import httpx
            async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                for url in extra_urls:
                    try:
                        resp = await client.get(url)
                        if resp.status_code == 200:
                            pages[url] = resp.text
                    except Exception:
                        pass
        
        tech_stack = self.tech_detector.detect(pages)
        
        results["parts"]["part_1_surface_intel"] = CIV2Result(
            part_number=1,
            part_name="Surface Intelligence",
            confidence=70,
            findings={
                "pages_discovered": len(pages),
                "page_urls": list(pages.keys()),
                "tech_stack": tech_stack,
            },
            recommendations=[
                f"Tech stack detected: {', '.join(tech_stack.keys())}",
                f"Fetched {len(pages)} accessible pages",
            ],
            status="complete",
        )
        
        # ─── PART 5: Traffic Intelligence ───
        if not skip_traffic:
            logger.info("═══ PART 5: Traffic Intelligence ═══")
            traffic = await self.traffic_intel.analyze(competitor_url)
            
            results["parts"]["part_5_traffic"] = CIV2Result(
                part_number=5,
                part_name="Traffic & Market Intelligence",
                confidence=30,  # Low without paid SimilarWeb
                findings=traffic,
                recommendations=traffic.get("hiring_signals", []),
                status="partial",
            )
        
        # ─── PART 6: Battle Plan (CI V3) ───
        logger.info("═══ PART 6: Battle Plan Generation ═══")
        plan = await self.battle_plan_orchestrator.run(
            competitor_name=competitor_name,
            competitor_url=competitor_url,
            extra_urls=extra_urls,
        )
        
        # Merge tech stack + traffic into plan
        plan.tech_stack = tech_stack
        if not skip_traffic and "part_5_traffic" in results["parts"]:
            plan.traffic_data = results["parts"]["part_5_traffic"].findings
            plan.hiring_signals = results["parts"]["part_5_traffic"].findings.get("hiring_signals", [])
            plan.confidence_scores["part_5_traffic_intelligence"] = 30
        
        results["battle_plan"] = plan
        
        # ─── PART 7: Battle Card Rendering ───
        logger.info("═══ PART 7: Battle Card Generation ═══")
        battle_card_data = self._generate_battle_card_data(plan)
        results["battle_card_data"] = battle_card_data
        
        results["execution_time_seconds"] = (datetime.now() - start_time).total_seconds()
        
        await discovery.close()
        
        logger.info(f"✅ CI V3 Pipeline complete in {results['execution_time_seconds']:.1f}s")
        return results
    
    def _generate_battle_card_data(self, plan: BattlePlan) -> Dict:
        """Generate structured data for React battle card rendering."""
        return {
            "header": {
                "title": f"{plan.competitor_name} — Competitive Battle Plan",
                "subtitle": "ZoneWise.AI Competitive Intelligence V3",
                "stats": {
                    "total_parcels": "10.8M",
                    "total_kpis": 63,
                    "monthly_cost": f"${plan.total_monthly_cost:.0f}",
                    "phases_status": f"{plan.phases_complete}/{plan.phases_partial}/{plan.phases_not_started}",
                },
            },
            "tabs": [
                {
                    "id": "competitive_intel",
                    "label": "⚔️ Competitive Intel",
                    "data": {
                        "pricing_tiers": plan.pricing_tiers,
                        "strengths": plan.strengths,
                        "weaknesses": plan.weaknesses,
                        "tech_stack": plan.tech_stack,
                        "features_count": len(plan.features),
                    },
                },
                {
                    "id": "cost_strategy",
                    "label": "💰 Cost Strategy",
                    "data": {
                        "our_cost": plan.total_monthly_cost,
                        "competitor_cost": plan.competitor_equivalent_cost,
                        "cost_ratio": plan.cost_advantage_ratio,
                        "sources": [asdict(ds) for ds in plan.data_sources],
                    },
                },
                {
                    "id": "kpi_comparison",
                    "label": "📊 63 KPIs vs Competitor",
                    "data": {
                        "wins": plan.kpis_we_win,
                        "matches": plan.kpis_we_match,
                        "losses": plan.kpis_we_lose,
                        "unique": plan.kpis_unique_to_us,
                        "by_category": self._group_kpis_by_category(plan.kpi_mappings),
                    },
                },
                {
                    "id": "architecture",
                    "label": "🏗️ Architecture",
                    "data": {
                        "phases": [asdict(p) for p in plan.phases],
                        "complete": plan.phases_complete,
                        "partial": plan.phases_partial,
                        "not_started": plan.phases_not_started,
                    },
                },
                {
                    "id": "action_plan",
                    "label": "📋 Action Plan",
                    "data": {
                        "weeks": [asdict(w) for w in plan.execution_weeks],
                        "total_weeks": plan.total_timeline_weeks,
                        "total_budget": plan.total_budget,
                    },
                },
            ],
            "confidence_scores": plan.confidence_scores,
            "traffic_data": plan.traffic_data,
            "hiring_signals": plan.hiring_signals,
        }
    
    def _group_kpis_by_category(self, mappings) -> Dict[str, Dict]:
        """Group KPI mappings by category for chart rendering."""
        categories = {}
        for m in mappings:
            cat = m.kpi_category
            if cat not in categories:
                categories[cat] = {"total": 0, "win": 0, "match": 0, "lose": 0, "unique": 0}
            categories[cat]["total"] += 1
            categories[cat][m.position.value] += 1
        return categories


# =============================================================================
# SUPABASE STORAGE
# =============================================================================

async def store_ci_v3_results(results: Dict) -> Optional[str]:
    """Store full CI V3 results in Supabase."""
    if not SUPABASE_KEY:
        logger.warning("No Supabase key — results not stored")
        return None
    
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            }
            
            plan = results["battle_plan"]
            
            # Store in competitor_clones
            payload = {
                "competitor_name": plan.competitor_name,
                "website_url": plan.competitor_url,
                "clone_date": plan.analysis_date,
                "confidence_scores": plan.confidence_scores,
                "metadata": {
                    "ci_version": "3.0",
                    "kpis": {"win": plan.kpis_we_win, "match": plan.kpis_we_match, "lose": plan.kpis_we_lose},
                    "cost": {"ours": plan.total_monthly_cost, "theirs": plan.competitor_equivalent_cost},
                    "phases": {"done": plan.phases_complete, "partial": plan.phases_partial, "todo": plan.phases_not_started},
                    "tech_stack": plan.tech_stack,
                    "traffic": plan.traffic_data,
                    "execution_time": results.get("execution_time_seconds"),
                },
            }
            
            resp = await client.post(
                f"{SUPABASE_URL}/rest/v1/competitor_clones",
                headers=headers,
                json=payload,
            )
            
            if resp.status_code in (200, 201):
                data = resp.json()
                clone_id = data[0]["id"] if isinstance(data, list) else data.get("id")
                logger.info(f"✅ Stored CI V3 results: {clone_id}")
                
                # Store individual analyses
                for part_key, part_result in results.get("parts", {}).items():
                    if isinstance(part_result, CIV2Result):
                        analysis_payload = {
                            "clone_id": clone_id,
                            "analysis_type": part_key,
                            "confidence_score": part_result.confidence,
                            "findings": part_result.findings,
                            "recommendations": part_result.recommendations,
                        }
                        await client.post(
                            f"{SUPABASE_URL}/rest/v1/competitor_analyses",
                            headers=headers,
                            json=analysis_payload,
                        )
                
                return clone_id
            else:
                logger.error(f"Storage failed: {resp.status_code}")
                
    except Exception as e:
        logger.error(f"CI V3 storage error: {e}")
    
    return None


# =============================================================================
# CLI
# =============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CI V3 — Full Competitive Intelligence Pipeline")
    parser.add_argument("--name", required=True, help="Competitor name")
    parser.add_argument("--url", required=True, help="Competitor URL")
    parser.add_argument("--extra-urls", nargs="*", help="Additional URLs")
    parser.add_argument("--output", default="ci_v3_results.json", help="Output JSON file")
    parser.add_argument("--skip-traffic", action="store_true", help="Skip traffic analysis")
    parser.add_argument("--store", action="store_true", help="Store in Supabase")
    parser.add_argument("-v", "--verbose", action="store_true")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    
    workflow = CIV3Workflow()
    results = await workflow.execute(
        competitor_name=args.name,
        competitor_url=args.url,
        extra_urls=args.extra_urls,
        skip_traffic=args.skip_traffic,
    )
    
    if args.store:
        await store_ci_v3_results(results)
    
    # Serialize (handle dataclass objects)
    def serialize(obj):
        if hasattr(obj, '__dict__') and hasattr(obj, '__dataclass_fields__'):
            return asdict(obj)
        if isinstance(obj, ConfidenceLevel):
            return obj.value
        return str(obj)
    
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=serialize)
    
    print(f"\n✅ CI V3 results saved to {args.output}")
    
    plan = results["battle_plan"]
    print(f"   Competitor: {plan.competitor_name}")
    print(f"   Features found: {len(plan.features)}")
    print(f"   Tech stack: {', '.join(plan.tech_stack.keys()) if plan.tech_stack else 'Not detected'}")
    print(f"   KPIs: {plan.kpis_we_win} unique / {plan.kpis_we_match} match / {plan.kpis_we_lose} lose")
    print(f"   Cost: ${plan.total_monthly_cost}/mo vs ${plan.competitor_equivalent_cost:,.0f}")
    print(f"   Phases: {plan.phases_complete}✅ {plan.phases_partial}⚠️ {plan.phases_not_started}❌")
    print(f"   Timeline: {plan.total_timeline_weeks} weeks")
    print(f"   Execution: {results['execution_time_seconds']:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
