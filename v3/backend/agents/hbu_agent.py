"""
ZoneWise V3 - HBU Agent
Performs Highest and Best Use analysis using Claude Sonnet 4.5 for complex reasoning.
"""

from typing import Optional
import structlog

from services.llm_router import LLMRouter

logger = structlog.get_logger()


class HBUAgent:
    """
    Agent for Highest and Best Use (HBU) analysis.
    
    HBU Analysis follows four criteria:
    1. Legally Permissible - What uses are allowed by zoning?
    2. Physically Possible - What can the lot support?
    3. Financially Feasible - What uses are profitable?
    4. Maximum Productivity - What produces highest value?
    """
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
    
    async def execute(
        self,
        parcel_id: Optional[str] = None,
        zoning_data: Optional[dict] = None,
        cma_data: Optional[dict] = None,
    ) -> dict:
        """Execute HBU analysis."""
        logger.info("HBU agent executing", parcel_id=parcel_id)
        
        result = {
            "hbu_score": 0,
            "recommended_use": None,
            "alternative_uses": [],
            "analysis": {
                "legally_permissible": [],
                "physically_possible": [],
                "financially_feasible": [],
                "maximum_productivity": None,
            },
            "reasoning": "",
            "confidence": 0.0,
        }
        
        try:
            # Step 1: Analyze legally permissible uses
            if zoning_data:
                permitted_uses = zoning_data.get("allowed_uses", {}).get("by_right", [])
                conditional_uses = zoning_data.get("allowed_uses", {}).get("conditional", [])
                result["analysis"]["legally_permissible"] = permitted_uses + conditional_uses
            
            # Step 2: Assess physical constraints
            if zoning_data:
                standards = zoning_data.get("dimensional_standards", {})
                result["analysis"]["physically_possible"] = self._assess_physical(standards)
            
            # Step 3: Financial feasibility (uses CMA data)
            if cma_data:
                result["analysis"]["financially_feasible"] = self._assess_financial(
                    result["analysis"]["legally_permissible"],
                    cma_data,
                )
            
            # Step 4: Determine maximum productivity (use LLM for reasoning)
            hbu_result = await self._determine_hbu(
                legally_permissible=result["analysis"]["legally_permissible"],
                physically_possible=result["analysis"]["physically_possible"],
                financially_feasible=result["analysis"]["financially_feasible"],
                zoning_data=zoning_data,
                cma_data=cma_data,
            )
            
            result.update(hbu_result)
            
            logger.info(
                "HBU agent completed",
                score=result["hbu_score"],
                recommended=result["recommended_use"],
            )
            
        except Exception as e:
            logger.error("HBU agent error", error=str(e))
            result["error"] = str(e)
        
        return result
    
    def _assess_physical(self, standards: dict) -> list:
        """Assess what's physically possible given dimensional standards."""
        possible = []
        
        min_lot = standards.get("min_lot_size", 0)
        max_density = standards.get("max_density", 0)
        max_height = standards.get("max_height", 0)
        max_far = standards.get("max_far", 0)
        
        # Single family is almost always possible
        if min_lot > 0:
            possible.append({
                "use": "Single Family Residential",
                "max_units": 1,
                "max_sqft": int(min_lot * max_far) if max_far else None,
            })
        
        # Multi-family based on density
        if max_density and max_density > 1:
            possible.append({
                "use": "Multi-Family Residential",
                "max_units": int(max_density * (min_lot / 43560)) if min_lot else None,
                "max_sqft": int(min_lot * max_far) if max_far and min_lot else None,
            })
        
        # Commercial if height allows
        if max_height and max_height >= 35:
            possible.append({
                "use": "Commercial",
                "max_stories": max_height // 12,
                "max_sqft": int(min_lot * max_far) if max_far and min_lot else None,
            })
        
        return possible
    
    def _assess_financial(self, legal_uses: list, cma_data: dict) -> list:
        """Assess financial feasibility of uses."""
        feasible = []
        estimated_value = cma_data.get("estimated_value", 0)
        
        if not estimated_value:
            return []
        
        for use in legal_uses:
            use_lower = use.lower()
            
            # Estimate NOI multipliers by use type
            if "single" in use_lower or "sfr" in use_lower:
                feasible.append({
                    "use": use,
                    "estimated_value": estimated_value,
                    "cap_rate": 0.06,
                    "noi": estimated_value * 0.06,
                })
            elif "duplex" in use_lower or "multi" in use_lower:
                feasible.append({
                    "use": use,
                    "estimated_value": estimated_value * 1.3,  # Premium for MF
                    "cap_rate": 0.07,
                    "noi": estimated_value * 1.3 * 0.07,
                })
            elif "commercial" in use_lower:
                feasible.append({
                    "use": use,
                    "estimated_value": estimated_value * 1.5,
                    "cap_rate": 0.08,
                    "noi": estimated_value * 1.5 * 0.08,
                })
        
        # Sort by NOI
        feasible.sort(key=lambda x: x.get("noi", 0), reverse=True)
        
        return feasible
    
    async def _determine_hbu(
        self,
        legally_permissible: list,
        physically_possible: list,
        financially_feasible: list,
        zoning_data: Optional[dict],
        cma_data: Optional[dict],
    ) -> dict:
        """Use LLM to determine HBU and generate reasoning."""
        
        # Build context for LLM
        context = f"""
        Analyze the Highest and Best Use for this property:
        
        LEGALLY PERMISSIBLE USES:
        {legally_permissible}
        
        PHYSICALLY POSSIBLE:
        {physically_possible}
        
        FINANCIALLY FEASIBLE (sorted by NOI):
        {financially_feasible}
        
        ZONING DATA:
        {zoning_data}
        
        CMA DATA:
        Estimated Value: ${cma_data.get('estimated_value', 'Unknown') if cma_data else 'Unknown'}
        
        Determine:
        1. The single BEST use (maximum productivity)
        2. Alternative viable uses
        3. HBU Score (0-100)
        4. Brief reasoning
        """
        
        try:
            response = await self.llm_router.generate(
                prompt=context,
                model_tier="standard",  # Claude Sonnet for complex reasoning
                system_prompt="You are a real estate appraiser expert in Highest and Best Use analysis.",
            )
            
            # Parse response (simplified - would use structured output in production)
            # For now, use heuristic scoring
            score = 50  # Base score
            
            if financially_feasible:
                score += 20  # Has feasible uses
            if len(financially_feasible) > 2:
                score += 10  # Multiple options
            if cma_data and cma_data.get("estimated_value"):
                score += 10  # Has value estimate
            if cma_data and cma_data.get("confidence", 0) > 0.7:
                score += 10  # High confidence
            
            recommended = None
            if financially_feasible:
                recommended = financially_feasible[0].get("use")
            
            return {
                "hbu_score": min(100, score),
                "recommended_use": recommended,
                "alternative_uses": [f.get("use") for f in financially_feasible[1:3]],
                "reasoning": response[:500] if response else "Analysis based on zoning and market data.",
                "confidence": min(0.95, score / 100),
            }
            
        except Exception as e:
            logger.warning("LLM HBU analysis failed", error=str(e))
            return {
                "hbu_score": 50,
                "recommended_use": financially_feasible[0].get("use") if financially_feasible else None,
                "alternative_uses": [],
                "reasoning": "Automated analysis based on available data.",
                "confidence": 0.5,
            }
