"""
ZoneWise V3 - HBU Agent (Highest and Best Use)
Extends OpenManus BaseAgent pattern.

Responsibilities:
- Analyze legally permissible uses
- Evaluate physical feasibility
- Assess financial viability
- Rank development scenarios
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import structlog

from agents.base import BaseAgent, BaseTool, ToolCollection, ToolResult, AgentState

logger = structlog.get_logger()


class LegalUsesAnalysisTool(BaseTool):
    """Analyze legally permissible uses for a parcel"""
    
    name: str = "analyze_legal_uses"
    description: str = "Determine legally permissible uses based on zoning and land use regulations"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "parcel_id": {"type": "string", "description": "Parcel ID to analyze"}
        },
        "required": ["parcel_id"]
    }

    async def execute(self, parcel_id: str) -> Dict[str, Any]:
        """Analyze legal uses"""
        from services.supabase_client import get_supabase
        
        supabase = get_supabase()
        
        # Get parcel zoning
        parcel = await supabase.table("fl_parcels").select(
            "zone_code, jurisdiction, flood_zone, wetlands_pct"
        ).eq("parcel_id", parcel_id).single().execute()
        
        if not parcel.data:
            return {"error": "Parcel not found"}
        
        zone_code = parcel.data["zone_code"]
        
        # Get zone rules
        zone = await supabase.table("fl_zoning_districts").select(
            "permitted_uses, conditional_uses, prohibited_uses"
        ).eq("zone_code", zone_code).single().execute()
        
        # Environmental constraints
        constraints = []
        if parcel.data.get("flood_zone") in ["A", "AE", "V", "VE"]:
            constraints.append("FEMA flood zone - requires elevation certificate")
        if parcel.data.get("wetlands_pct", 0) > 20:
            constraints.append("Significant wetlands - may require mitigation")
        
        return {
            "parcel_id": parcel_id,
            "zone_code": zone_code,
            "permitted_uses": zone.data.get("permitted_uses", []) if zone.data else [],
            "conditional_uses": zone.data.get("conditional_uses", []) if zone.data else [],
            "environmental_constraints": constraints,
            "rezoning_potential": self._assess_rezoning_potential(zone_code)
        }

    def _assess_rezoning_potential(self, zone_code: str) -> str:
        """Assess likelihood of successful rezoning"""
        # Simplified logic - would be more complex in production
        if zone_code.startswith("AU") or zone_code.startswith("AA"):
            return "HIGH - Agricultural zones often support upzoning"
        if zone_code.startswith("RS"):
            return "MEDIUM - Residential upzoning possible in growth areas"
        if zone_code.startswith("BU") or zone_code.startswith("IU"):
            return "LOW - Already commercial/industrial"
        return "UNKNOWN"


class PhysicalFeasibilityTool(BaseTool):
    """Analyze physical feasibility of development"""
    
    name: str = "analyze_physical_feasibility"
    description: str = "Evaluate physical constraints and development capacity"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "parcel_id": {"type": "string", "description": "Parcel ID to analyze"}
        },
        "required": ["parcel_id"]
    }

    async def execute(self, parcel_id: str) -> Dict[str, Any]:
        """Analyze physical feasibility"""
        from services.supabase_client import get_supabase
        
        supabase = get_supabase()
        
        # Get parcel details
        parcel = await supabase.table("fl_parcels").select(
            "lot_size_sqft, lot_width_ft, lot_depth_ft, zone_code, "
            "topography, soil_type, utilities_available, road_frontage_ft"
        ).eq("parcel_id", parcel_id).single().execute()
        
        if not parcel.data:
            return {"error": "Parcel not found"}
        
        # Get zone dimensional standards
        zone = await supabase.table("fl_zoning_districts").select(
            "min_lot_size_sqft, min_lot_width_ft, max_height_ft, "
            "max_lot_coverage_pct, front_setback_ft, side_setback_ft, rear_setback_ft"
        ).eq("zone_code", parcel.data["zone_code"]).single().execute()
        
        if not zone.data:
            return {"error": "Zone rules not found"}
        
        # Calculate buildable area
        lot_sqft = parcel.data.get("lot_size_sqft", 0)
        coverage_pct = zone.data.get("max_lot_coverage_pct", 40) / 100
        buildable_sqft = lot_sqft * coverage_pct
        
        # Assess constraints
        constraints = []
        if lot_sqft < zone.data.get("min_lot_size_sqft", 0):
            constraints.append("Lot size below minimum - variance required")
        if parcel.data.get("utilities_available") == False:
            constraints.append("No utilities - connection costs apply")
        
        return {
            "parcel_id": parcel_id,
            "lot_size_sqft": lot_sqft,
            "buildable_area_sqft": round(buildable_sqft),
            "max_height_ft": zone.data.get("max_height_ft", 35),
            "setbacks": {
                "front_ft": zone.data.get("front_setback_ft", 25),
                "side_ft": zone.data.get("side_setback_ft", 7.5),
                "rear_ft": zone.data.get("rear_setback_ft", 20)
            },
            "utilities_available": parcel.data.get("utilities_available", True),
            "road_frontage_ft": parcel.data.get("road_frontage_ft", 0),
            "physical_constraints": constraints,
            "development_capacity_score": self._score_capacity(
                lot_sqft, buildable_sqft, len(constraints)
            )
        }

    def _score_capacity(self, lot_sqft: float, buildable_sqft: float, constraint_count: int) -> int:
        """Score development capacity 0-100"""
        if lot_sqft == 0:
            return 0
        
        base_score = min(100, (buildable_sqft / 5000) * 50)  # Larger = better
        constraint_penalty = constraint_count * 15
        
        return max(0, min(100, int(base_score - constraint_penalty)))


class FinancialViabilityTool(BaseTool):
    """Analyze financial viability of development scenarios"""
    
    name: str = "analyze_financial_viability"
    description: str = "Evaluate ROI and financial feasibility of development scenarios"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "parcel_id": {"type": "string", "description": "Parcel ID"},
            "use_type": {"type": "string", "description": "Proposed development type"},
            "construction_cost_per_sqft": {"type": "number", "description": "Estimated construction cost"}
        },
        "required": ["parcel_id", "use_type"]
    }

    async def execute(
        self, 
        parcel_id: str, 
        use_type: str,
        construction_cost_per_sqft: float = None
    ) -> Dict[str, Any]:
        """Analyze financial viability"""
        from services.supabase_client import get_supabase
        
        supabase = get_supabase()
        
        # Get parcel and market data
        parcel = await supabase.table("fl_parcels").select(
            "lot_size_sqft, assessed_value, zone_code"
        ).eq("parcel_id", parcel_id).single().execute()
        
        if not parcel.data:
            return {"error": "Parcel not found"}
        
        # Default construction costs by use type
        default_costs = {
            "single-family": 175,
            "multi-family": 150,
            "retail": 125,
            "office": 140,
            "industrial": 85,
            "warehouse": 65
        }
        
        cost_per_sqft = construction_cost_per_sqft or default_costs.get(use_type.lower(), 150)
        
        # Estimate development scenario
        lot_sqft = parcel.data.get("lot_size_sqft", 0)
        buildable_sqft = lot_sqft * 0.35  # Assume 35% coverage
        
        # Simple pro forma
        land_cost = parcel.data.get("assessed_value", 0) * 1.2  # Market premium
        construction_cost = buildable_sqft * cost_per_sqft
        soft_costs = construction_cost * 0.15  # 15% soft costs
        total_development_cost = land_cost + construction_cost + soft_costs
        
        # Revenue estimates by use
        revenue_per_sqft = {
            "single-family": 350,
            "multi-family": 280,
            "retail": 250,
            "office": 220,
            "industrial": 150,
            "warehouse": 120
        }
        
        projected_value = buildable_sqft * revenue_per_sqft.get(use_type.lower(), 200)
        profit = projected_value - total_development_cost
        roi = (profit / total_development_cost * 100) if total_development_cost > 0 else 0
        
        return {
            "parcel_id": parcel_id,
            "use_type": use_type,
            "pro_forma": {
                "land_cost": round(land_cost),
                "construction_cost": round(construction_cost),
                "soft_costs": round(soft_costs),
                "total_development_cost": round(total_development_cost),
                "projected_value": round(projected_value),
                "projected_profit": round(profit),
                "roi_percent": round(roi, 1)
            },
            "viability_rating": self._rate_viability(roi),
            "assumptions": [
                f"Construction cost: ${cost_per_sqft}/sqft",
                "35% lot coverage assumed",
                "15% soft costs",
                "20% land premium over assessed"
            ]
        }

    def _rate_viability(self, roi: float) -> str:
        """Rate project viability"""
        if roi >= 25:
            return "EXCELLENT"
        if roi >= 15:
            return "GOOD"
        if roi >= 10:
            return "MARGINAL"
        if roi >= 0:
            return "POOR"
        return "NOT VIABLE"


class RankScenariosTool(BaseTool):
    """Rank development scenarios by HBU criteria"""
    
    name: str = "rank_scenarios"
    description: str = "Rank multiple development scenarios by highest and best use criteria"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "scenarios": {"type": "array", "description": "List of scenario analyses"}
        },
        "required": ["scenarios"]
    }

    async def execute(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank scenarios"""
        ranked = []
        
        for scenario in scenarios:
            # Score each criterion
            legal_score = 100 if not scenario.get("constraints") else 100 - len(scenario.get("constraints", [])) * 20
            physical_score = scenario.get("development_capacity_score", 50)
            financial_score = min(100, max(0, scenario.get("pro_forma", {}).get("roi_percent", 0) * 4))
            
            # Weighted average
            total_score = (legal_score * 0.3 + physical_score * 0.3 + financial_score * 0.4)
            
            ranked.append({
                **scenario,
                "hbu_score": round(total_score),
                "scores": {
                    "legal": legal_score,
                    "physical": physical_score,
                    "financial": financial_score
                }
            })
        
        # Sort by HBU score
        ranked.sort(key=lambda x: x["hbu_score"], reverse=True)
        
        return ranked


class HBUAgent(BaseAgent):
    """Highest and Best Use Analysis Agent.
    
    Analyzes properties to determine the most profitable legally permissible
    and physically possible use.
    """

    name: str = "HBUAgent"
    description: str = "Specialist for highest and best use analysis"
    domain: str = "hbu"
    
    system_prompt: str = """You are a real estate development analyst specializing in highest and best use (HBU) analysis.

HBU is defined as the reasonably probable use that:
1. Is LEGALLY PERMISSIBLE (zoning, deed restrictions, regulations)
2. Is PHYSICALLY POSSIBLE (size, shape, topography, utilities)
3. Is FINANCIALLY FEASIBLE (generates positive return)
4. Is MAXIMALLY PRODUCTIVE (highest value among feasible alternatives)

When analyzing properties:
- Consider current use vs. potential alternative uses
- Account for environmental and regulatory constraints
- Evaluate market demand for different use types
- Provide quantitative ROI analysis when possible

Always rank alternatives and justify your HBU conclusion."""

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            LegalUsesAnalysisTool(),
            PhysicalFeasibilityTool(),
            FinancialViabilityTool(),
            RankScenariosTool()
        )
    )

    async def step(self) -> str:
        """Execute HBU analysis step"""
        user_messages = [m for m in self.memory.messages if m.role == "user"]
        if not user_messages:
            return "No query to process"
        
        query = user_messages[-1].content
        result = await self._run_hbu_analysis(query)
        
        self.memory.add_assistant_message(result)
        self.state = AgentState.FINISHED
        return result

    async def _run_hbu_analysis(self, query: str) -> str:
        """Run complete HBU analysis"""
        import re
        
        parcel_pattern = r'\d{2}-\d{2}-\d{2}-[\d\w.-]+'
        parcel_match = re.search(parcel_pattern, query)
        
        if not parcel_match:
            return "Please provide a parcel ID for highest and best use analysis."
        
        parcel_id = parcel_match.group()
        
        # Step 1: Legal analysis
        legal_tool = self.available_tools.get_tool("analyze_legal_uses")
        legal_result = await legal_tool(parcel_id=parcel_id)
        legal_data = legal_result.output if isinstance(legal_result, ToolResult) else legal_result
        
        if isinstance(legal_data, dict) and legal_data.get("error"):
            return f"Error in legal analysis: {legal_data['error']}"
        
        # Step 2: Physical analysis
        physical_tool = self.available_tools.get_tool("analyze_physical_feasibility")
        physical_result = await physical_tool(parcel_id=parcel_id)
        physical_data = physical_result.output if isinstance(physical_result, ToolResult) else physical_result
        
        # Step 3: Financial analysis for top 3 permitted uses
        scenarios = []
        permitted_uses = legal_data.get("permitted_uses", [])[:3]
        
        if not permitted_uses:
            permitted_uses = ["single-family", "vacant"]
        
        financial_tool = self.available_tools.get_tool("analyze_financial_viability")
        
        for use_type in permitted_uses:
            fin_result = await financial_tool(parcel_id=parcel_id, use_type=use_type)
            fin_data = fin_result.output if isinstance(fin_result, ToolResult) else fin_result
            
            scenarios.append({
                "use_type": use_type,
                "constraints": legal_data.get("environmental_constraints", []),
                "development_capacity_score": physical_data.get("development_capacity_score", 50),
                "pro_forma": fin_data.get("pro_forma", {}) if isinstance(fin_data, dict) else {}
            })
        
        # Step 4: Rank scenarios
        rank_tool = self.available_tools.get_tool("rank_scenarios")
        ranked_result = await rank_tool(scenarios=scenarios)
        ranked = ranked_result.output if isinstance(ranked_result, ToolResult) else ranked_result
        
        # Format response
        return self._format_hbu_report(parcel_id, legal_data, physical_data, ranked)

    def _format_hbu_report(
        self, 
        parcel_id: str, 
        legal: Dict, 
        physical: Dict, 
        ranked: List[Dict]
    ) -> str:
        """Format HBU analysis report"""
        
        best = ranked[0] if ranked else {}
        
        return f"""**Highest and Best Use Analysis**

**Parcel:** {parcel_id}
**Current Zone:** {legal.get('zone_code', 'Unknown')}

---

## Legal Analysis
**Permitted Uses:** {', '.join(legal.get('permitted_uses', [])[:5]) or 'See ordinance'}
**Rezoning Potential:** {legal.get('rezoning_potential', 'Unknown')}
**Environmental Constraints:** {', '.join(legal.get('environmental_constraints', [])) or 'None identified'}

---

## Physical Analysis
**Lot Size:** {physical.get('lot_size_sqft', 0):,} sq ft
**Buildable Area:** {physical.get('buildable_area_sqft', 0):,} sq ft
**Max Height:** {physical.get('max_height_ft', 35)} ft
**Development Capacity Score:** {physical.get('development_capacity_score', 'N/A')}/100

---

## Financial Analysis (Top Scenarios)

| Use Type | ROI | Viability | HBU Score |
|----------|-----|-----------|-----------|
{self._format_scenarios_table(ranked)}

---

## HBU Conclusion

🏆 **Recommended Use:** {best.get('use_type', 'Undetermined').upper()}
**HBU Score:** {best.get('hbu_score', 'N/A')}/100
**Projected ROI:** {best.get('pro_forma', {}).get('roi_percent', 'N/A')}%

*This analysis should be verified by a qualified appraiser or development consultant.*"""

    def _format_scenarios_table(self, scenarios: List[Dict]) -> str:
        """Format scenarios as markdown table"""
        rows = []
        for s in scenarios[:5]:
            use = s.get('use_type', 'N/A')
            roi = f"{s.get('pro_forma', {}).get('roi_percent', 0):.1f}%"
            viability = s.get('pro_forma', {}).get('viability_rating', 'N/A') if isinstance(s.get('pro_forma'), dict) else 'N/A'
            score = s.get('hbu_score', 'N/A')
            rows.append(f"| {use} | {roi} | {viability} | {score} |")
        return "\n".join(rows) if rows else "| No scenarios | - | - | - |"
