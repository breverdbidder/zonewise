"""
ZoneWise V3 - Reporter Agent
Synthesizes all agent results into natural language responses.
Generates map actions and follow-up suggestions.
Uses Claude Sonnet 4.5 for high-quality output.
"""

from typing import Optional
import structlog

from services.llm_router import LLMRouter

logger = structlog.get_logger()


class ReporterAgent:
    """
    Agent for synthesizing results into user-friendly responses.
    
    Responsibilities:
    - Generate natural language responses
    - Create map actions (highlight, zoom, filter)
    - Suggest follow-up questions
    - Format data for display
    """
    
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
    
    async def execute(
        self,
        query: str,
        intent: Optional[str],
        zoning_data: Optional[dict] = None,
        cma_data: Optional[dict] = None,
        hbu_data: Optional[dict] = None,
        ml_data: Optional[dict] = None,
        map_context: Optional[dict] = None,
    ) -> dict:
        """Generate response from agent results."""
        logger.info("Reporter agent executing", intent=intent)
        
        result = {
            "response": "",
            "map_actions": [],
            "suggestions": [],
            "sources": [],
            "confidence": 0.5,
        }
        
        try:
            # Generate response based on intent
            if intent in ["greeting", "definition"]:
                # Simple responses don't need full synthesis
                result["response"] = await self._generate_simple_response(query, intent)
                result["suggestions"] = self._get_general_suggestions()
            else:
                # Full synthesis for analytical intents
                result["response"] = await self._synthesize_response(
                    query=query,
                    intent=intent,
                    zoning_data=zoning_data,
                    cma_data=cma_data,
                    hbu_data=hbu_data,
                    ml_data=ml_data,
                )
                
                # Generate map actions
                result["map_actions"] = self._generate_map_actions(
                    intent=intent,
                    zoning_data=zoning_data,
                    map_context=map_context,
                )
                
                # Generate suggestions
                result["suggestions"] = self._generate_suggestions(
                    intent=intent,
                    zoning_data=zoning_data,
                    hbu_data=hbu_data,
                )
                
                # Compile sources
                result["sources"] = self._compile_sources(
                    zoning_data=zoning_data,
                    cma_data=cma_data,
                )
                
                # Calculate confidence
                result["confidence"] = self._calculate_confidence(
                    zoning_data=zoning_data,
                    cma_data=cma_data,
                    hbu_data=hbu_data,
                    ml_data=ml_data,
                )
            
            logger.info(
                "Reporter agent completed",
                response_length=len(result["response"]),
                map_actions=len(result["map_actions"]),
            )
            
        except Exception as e:
            logger.error("Reporter agent error", error=str(e))
            result["response"] = "I encountered an error generating the response. Please try again."
            result["error"] = str(e)
        
        return result
    
    async def _generate_simple_response(self, query: str, intent: str) -> str:
        """Generate simple responses for greetings and definitions."""
        if intent == "greeting":
            return (
                "Hello! I'm your AI Zoning Expert. I can help you with:\n\n"
                "• **Zoning lookups** - Find zone codes and permitted uses\n"
                "• **Feasibility analysis** - Check what you can build\n"
                "• **Value estimates** - Get CMA and ML predictions\n"
                "• **HBU analysis** - Determine highest and best use\n\n"
                "Try clicking on a parcel on the map, or ask me anything about zoning!"
            )
        
        # For definitions, use LLM
        try:
            response = await self.llm_router.generate(
                prompt=f"Define this real estate/zoning term in 2-3 sentences for a developer: {query}",
                model_tier="free",  # Simple task, use Gemini Flash
                system_prompt="You are a helpful real estate expert. Be concise and practical.",
            )
            return response
        except:
            return "I couldn't find a definition for that term. Please try rephrasing."
    
    async def _synthesize_response(
        self,
        query: str,
        intent: Optional[str],
        zoning_data: Optional[dict],
        cma_data: Optional[dict],
        hbu_data: Optional[dict],
        ml_data: Optional[dict],
    ) -> str:
        """Synthesize full response from all agent data."""
        
        # Build context for LLM
        context_parts = []
        
        if zoning_data and not zoning_data.get("error"):
            context_parts.append(f"""
ZONING INFORMATION:
- Zone Code: {zoning_data.get('zone_code', 'Unknown')}
- Zone Category: {zoning_data.get('zone_category', 'Unknown')}
- Jurisdiction: {zoning_data.get('jurisdiction', 'Unknown')}
- Allowed Uses (by-right): {', '.join(zoning_data.get('allowed_uses', {}).get('by_right', [])[:5])}
- Dimensional Standards: {zoning_data.get('dimensional_standards', {})}
""")
        
        if cma_data and not cma_data.get("error"):
            context_parts.append(f"""
MARKET ANALYSIS:
- Estimated Value: ${cma_data.get('estimated_value', 0):,.0f}
- Value Range: ${cma_data.get('value_range', {}).get('low', 0):,.0f} - ${cma_data.get('value_range', {}).get('high', 0):,.0f}
- Comparables Found: {len(cma_data.get('comparables', []))}
- CMA Confidence: {cma_data.get('confidence', 0):.0%}
""")
        
        if hbu_data and not hbu_data.get("error"):
            context_parts.append(f"""
HIGHEST AND BEST USE:
- HBU Score: {hbu_data.get('hbu_score', 0)}/100
- Recommended Use: {hbu_data.get('recommended_use', 'Unknown')}
- Alternative Uses: {', '.join(hbu_data.get('alternative_uses', []))}
""")
        
        if ml_data and not ml_data.get("error"):
            context_parts.append(f"""
ML PREDICTIONS:
- Predicted Value: ${ml_data.get('predicted_value', 0):,.0f}
- Win Probability: {ml_data.get('win_probability', 0):.0%}
- Model Confidence: {ml_data.get('value_confidence', 0):.0%}
""")
        
        if not context_parts:
            return "I couldn't gather enough information to answer your question. Please try selecting a parcel on the map first."
        
        # Generate response
        prompt = f"""
USER QUESTION: {query}

AVAILABLE DATA:
{''.join(context_parts)}

Generate a helpful, conversational response that:
1. Directly answers the user's question
2. Highlights the most important findings
3. Uses specific numbers from the data
4. Is 3-5 sentences for simple questions, more for complex analysis
5. Does NOT use markdown headers or bullet points (use natural paragraphs)
"""
        
        try:
            response = await self.llm_router.generate(
                prompt=prompt,
                model_tier="standard",  # Claude Sonnet for quality
                system_prompt="You are a helpful AI zoning expert. Be conversational and informative.",
            )
            return response
        except Exception as e:
            logger.warning("LLM synthesis failed", error=str(e))
            return self._fallback_response(zoning_data, cma_data, hbu_data)
    
    def _fallback_response(
        self,
        zoning_data: Optional[dict],
        cma_data: Optional[dict],
        hbu_data: Optional[dict],
    ) -> str:
        """Generate fallback response without LLM."""
        parts = []
        
        if zoning_data:
            zone = zoning_data.get("zone_code", "Unknown")
            parts.append(f"This property is zoned {zone}.")
            
            uses = zoning_data.get("allowed_uses", {}).get("by_right", [])
            if uses:
                parts.append(f"Permitted uses include: {', '.join(uses[:3])}.")
        
        if hbu_data:
            score = hbu_data.get("hbu_score", 0)
            rec = hbu_data.get("recommended_use", "")
            if rec:
                parts.append(f"The recommended use is {rec} with an HBU score of {score}/100.")
        
        if cma_data:
            value = cma_data.get("estimated_value")
            if value:
                parts.append(f"Estimated market value is ${value:,.0f}.")
        
        return " ".join(parts) if parts else "I found limited information for this property."
    
    def _generate_map_actions(
        self,
        intent: Optional[str],
        zoning_data: Optional[dict],
        map_context: Optional[dict],
    ) -> list:
        """Generate map actions based on response."""
        actions = []
        
        if intent == "geographic_search" and zoning_data:
            # Highlight parcels with matching zone
            zone_code = zoning_data.get("zone_code")
            if zone_code:
                actions.append({
                    "type": "filter",
                    "payload": {"zone_code": zone_code},
                    "label": f"Show all {zone_code} parcels",
                })
        
        if intent in ["feasibility_check", "hbu_analysis", "zoning_lookup"]:
            # Offer to show on map
            actions.append({
                "type": "highlight",
                "payload": {"duration_ms": 5000},
                "label": "Highlight on map",
            })
        
        if intent == "parcel_comparison":
            actions.append({
                "type": "layer",
                "payload": {"layer_id": "hbu", "visible": True},
                "label": "Show HBU scores layer",
            })
        
        return actions
    
    def _generate_suggestions(
        self,
        intent: Optional[str],
        zoning_data: Optional[dict],
        hbu_data: Optional[dict],
    ) -> list:
        """Generate follow-up suggestions."""
        suggestions = []
        
        # Intent-based suggestions
        if intent == "zoning_lookup":
            suggestions.extend([
                "What can I build on this property?",
                "What are the setback requirements?",
                "Run a full HBU analysis",
            ])
        elif intent == "feasibility_check":
            suggestions.extend([
                "What's the estimated value?",
                "Show me comparable properties",
                "Generate a report",
            ])
        elif intent == "hbu_analysis":
            suggestions.extend([
                "Show me similar high-scoring properties",
                "What are the risks?",
                "Generate investment report",
            ])
        else:
            # General suggestions
            suggestions.extend([
                "Tell me about the zoning",
                "What's the HBU score?",
                "Find similar properties",
            ])
        
        return suggestions[:4]  # Max 4 suggestions
    
    def _compile_sources(
        self,
        zoning_data: Optional[dict],
        cma_data: Optional[dict],
    ) -> list:
        """Compile data sources for citation."""
        sources = []
        
        if zoning_data:
            jurisdiction = zoning_data.get("jurisdiction", "")
            if jurisdiction:
                sources.append({
                    "name": f"{jurisdiction} Zoning Code",
                    "type": "zoning",
                })
        
        if cma_data and cma_data.get("comparables"):
            sources.append({
                "name": "MLS/Public Records",
                "type": "cma",
                "count": len(cma_data.get("comparables", [])),
            })
        
        return sources
    
    def _calculate_confidence(
        self,
        zoning_data: Optional[dict],
        cma_data: Optional[dict],
        hbu_data: Optional[dict],
        ml_data: Optional[dict],
    ) -> float:
        """Calculate overall response confidence."""
        confidences = []
        
        if zoning_data and not zoning_data.get("error"):
            confidences.append(0.9)  # Zoning is usually reliable
        
        if cma_data and cma_data.get("confidence"):
            confidences.append(cma_data["confidence"])
        
        if hbu_data and hbu_data.get("confidence"):
            confidences.append(hbu_data["confidence"])
        
        if ml_data and ml_data.get("value_confidence"):
            confidences.append(ml_data["value_confidence"])
        
        if not confidences:
            return 0.5
        
        return sum(confidences) / len(confidences)
