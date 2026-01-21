"""
ZoneWise V3 - CMA Agent (Comparable Market Analysis)
Extends OpenManus BaseAgent pattern.

Responsibilities:
- Find comparable properties within radius
- Calculate value adjustments
- Estimate property values with confidence scores
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import structlog

from agents.base import BaseAgent, BaseTool, ToolCollection, ToolResult, AgentState

logger = structlog.get_logger()


class FindComparablesTool(BaseTool):
    """Find comparable sales near a subject property"""
    
    name: str = "find_comparables"
    description: str = "Find comparable property sales within a specified radius"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "parcel_id": {"type": "string", "description": "Subject parcel ID"},
            "radius_miles": {"type": "number", "description": "Search radius in miles"},
            "max_results": {"type": "integer", "description": "Maximum comparables to return"}
        },
        "required": ["parcel_id"]
    }

    async def execute(
        self, 
        parcel_id: str, 
        radius_miles: float = 1.0,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Find comparable properties"""
        from services.supabase_client import get_supabase
        
        supabase = get_supabase()
        
        # Get subject property
        subject = await supabase.table("fl_parcels").select(
            "parcel_id, address, lot_size_sqft, assessed_value, zone_code, geometry"
        ).eq("parcel_id", parcel_id).single().execute()
        
        if not subject.data:
            return {"error": "Subject parcel not found"}
        
        # Find comparables using PostGIS
        # ST_DWithin for radius search in meters (1 mile = 1609.34 meters)
        radius_meters = radius_miles * 1609.34
        
        comps = await supabase.rpc(
            "find_comparable_sales",
            {
                "subject_parcel_id": parcel_id,
                "search_radius_meters": radius_meters,
                "max_results": max_results
            }
        ).execute()
        
        return comps.data if comps.data else []


class CalculateAdjustmentsTool(BaseTool):
    """Calculate value adjustments between subject and comps"""
    
    name: str = "calculate_adjustments"
    description: str = "Calculate adjustment factors between subject property and comparables"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "subject": {"type": "object", "description": "Subject property data"},
            "comparables": {"type": "array", "description": "List of comparable properties"}
        },
        "required": ["subject", "comparables"]
    }

    async def execute(
        self, 
        subject: Dict[str, Any], 
        comparables: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate adjustments for each comparable"""
        adjusted_comps = []
        
        subject_sqft = subject.get("lot_size_sqft", 0) or subject.get("living_area_sqft", 0)
        
        for comp in comparables:
            comp_sqft = comp.get("lot_size_sqft", 0) or comp.get("living_area_sqft", 0)
            comp_price = comp.get("sale_price", 0)
            
            if not comp_price or not comp_sqft:
                continue
            
            # Calculate adjustments
            adjustments = {}
            total_adjustment = 0
            
            # Size adjustment ($50/sqft for lot, $150/sqft for living area)
            if subject_sqft and comp_sqft:
                sqft_diff = subject_sqft - comp_sqft
                size_adj = sqft_diff * 50  # Simplified adjustment
                adjustments["size"] = size_adj
                total_adjustment += size_adj
            
            # Age adjustment (if year built available)
            if subject.get("year_built") and comp.get("year_built"):
                age_diff = comp["year_built"] - subject["year_built"]
                age_adj = age_diff * 1000  # $1000/year
                adjustments["age"] = age_adj
                total_adjustment += age_adj
            
            # Location adjustment (distance-based)
            distance = comp.get("distance_miles", 0)
            if distance > 0.5:
                loc_adj = -distance * 5000  # Penalty for distance
                adjustments["location"] = loc_adj
                total_adjustment += loc_adj
            
            adjusted_comps.append({
                "parcel_id": comp.get("parcel_id"),
                "address": comp.get("address"),
                "sale_price": comp_price,
                "sale_date": comp.get("sale_date"),
                "adjustments": adjustments,
                "total_adjustment": total_adjustment,
                "adjusted_value": comp_price + total_adjustment
            })
        
        return adjusted_comps


class EstimateValueTool(BaseTool):
    """Estimate value from adjusted comparables"""
    
    name: str = "estimate_value"
    description: str = "Estimate property value from adjusted comparable sales"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "adjusted_comps": {"type": "array", "description": "Adjusted comparables"}
        },
        "required": ["adjusted_comps"]
    }

    async def execute(self, adjusted_comps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate estimated value with confidence"""
        if not adjusted_comps:
            return {"error": "No comparables provided"}
        
        adjusted_values = [c["adjusted_value"] for c in adjusted_comps if c.get("adjusted_value")]
        
        if not adjusted_values:
            return {"error": "No valid adjusted values"}
        
        # Calculate statistics
        import statistics
        
        mean_value = statistics.mean(adjusted_values)
        median_value = statistics.median(adjusted_values)
        
        # Calculate confidence based on variance
        if len(adjusted_values) >= 2:
            std_dev = statistics.stdev(adjusted_values)
            cv = (std_dev / mean_value) * 100 if mean_value else 0
            # Lower CV = higher confidence
            confidence = max(0.5, min(0.95, 1 - (cv / 50)))
        else:
            confidence = 0.6
        
        return {
            "estimated_value": round(median_value, -3),  # Round to nearest $1000
            "value_range": {
                "low": round(min(adjusted_values), -3),
                "high": round(max(adjusted_values), -3)
            },
            "confidence": round(confidence, 2),
            "comp_count": len(adjusted_values),
            "methodology": "Sales Comparison Approach"
        }


class CMAAgent(BaseAgent):
    """Comparable Market Analysis Agent.
    
    Specializes in finding comparable sales and estimating property values
    using the sales comparison approach.
    """

    name: str = "CMAAgent"
    description: str = "Specialist for comparable market analysis and property valuation"
    domain: str = "cma"
    
    system_prompt: str = """You are a real estate valuation expert specializing in the sales comparison approach.

Your responsibilities:
1. Find comparable sales near subject properties
2. Calculate appropriate adjustments for differences
3. Reconcile adjusted values into a final estimate
4. Provide confidence levels for your estimates

Key adjustment factors:
- Location (same neighborhood preferred)
- Size (lot size and living area)
- Age and condition
- Features and amenities
- Sale date (time adjustments)

Always explain your methodology and cite comparable sales data."""

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            FindComparablesTool(),
            CalculateAdjustmentsTool(),
            EstimateValueTool()
        )
    )

    async def step(self) -> str:
        """Execute CMA analysis step"""
        user_messages = [m for m in self.memory.messages if m.role == "user"]
        if not user_messages:
            return "No query to process"
        
        query = user_messages[-1].content
        result = await self._run_cma_analysis(query)
        
        self.memory.add_assistant_message(result)
        self.state = AgentState.FINISHED
        return result

    async def _run_cma_analysis(self, query: str) -> str:
        """Run full CMA analysis pipeline"""
        import re
        
        # Extract parcel ID from query
        parcel_pattern = r'\d{2}-\d{2}-\d{2}-[\d\w.-]+'
        parcel_match = re.search(parcel_pattern, query)
        
        if not parcel_match:
            return "Please provide a parcel ID to run a comparable market analysis."
        
        parcel_id = parcel_match.group()
        
        # Step 1: Find comparables
        find_tool = self.available_tools.get_tool("find_comparables")
        comps_result = await find_tool(parcel_id=parcel_id, radius_miles=1.0, max_results=5)
        
        if isinstance(comps_result, ToolResult) and comps_result.error:
            return f"Error finding comparables: {comps_result.error}"
        
        comps = comps_result.output if isinstance(comps_result, ToolResult) else comps_result
        
        if not comps or (isinstance(comps, dict) and comps.get("error")):
            return f"No comparable sales found within 1 mile of parcel {parcel_id}"
        
        # Step 2: Get subject property details
        from services.supabase_client import get_supabase
        supabase = get_supabase()
        subject = await supabase.table("fl_parcels").select("*").eq("parcel_id", parcel_id).single().execute()
        
        if not subject.data:
            return f"Subject parcel {parcel_id} not found"
        
        # Step 3: Calculate adjustments
        adj_tool = self.available_tools.get_tool("calculate_adjustments")
        adjusted = await adj_tool(subject=subject.data, comparables=comps)
        
        adjusted_comps = adjusted.output if isinstance(adjusted, ToolResult) else adjusted
        
        # Step 4: Estimate value
        est_tool = self.available_tools.get_tool("estimate_value")
        estimate = await est_tool(adjusted_comps=adjusted_comps)
        
        est_data = estimate.output if isinstance(estimate, ToolResult) else estimate
        
        if isinstance(est_data, dict) and est_data.get("error"):
            return f"Could not estimate value: {est_data['error']}"
        
        # Format response
        return f"""**Comparable Market Analysis**

**Subject Property:** {parcel_id}
**Address:** {subject.data.get('address', 'N/A')}

---

**Estimated Value:** ${est_data['estimated_value']:,}
**Value Range:** ${est_data['value_range']['low']:,} - ${est_data['value_range']['high']:,}
**Confidence:** {est_data['confidence']*100:.0f}%

---

**Comparable Sales Used:** {est_data['comp_count']}

| Address | Sale Price | Adjusted Value |
|---------|-----------|----------------|
{self._format_comps_table(adjusted_comps)}

**Methodology:** {est_data['methodology']}

*Note: This is an automated estimate. Consult a licensed appraiser for official valuations.*"""

    def _format_comps_table(self, comps: List[Dict]) -> str:
        """Format comparables as markdown table rows"""
        rows = []
        for comp in comps[:5]:
            addr = comp.get('address', 'N/A')[:30]
            sale = f"${comp.get('sale_price', 0):,}"
            adj = f"${comp.get('adjusted_value', 0):,.0f}"
            rows.append(f"| {addr} | {sale} | {adj} |")
        return "\n".join(rows) if rows else "| No comparables | - | - |"
