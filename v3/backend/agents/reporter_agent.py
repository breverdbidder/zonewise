"""
ZoneWise V3 - Reporter Agent (Response Synthesis)
Extends OpenManus BaseAgent pattern.

Responsibilities:
- Synthesize outputs from multiple agents
- Format responses for chat interface
- Generate summaries and reports
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import structlog

from agents.base import BaseAgent, BaseTool, ToolCollection, ToolResult, AgentState, Message

logger = structlog.get_logger()


class SynthesizeResponseTool(BaseTool):
    """Synthesize multi-agent results into coherent response"""
    
    name: str = "synthesize_response"
    description: str = "Combine outputs from multiple agents into a unified response"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "agent_results": {
                "type": "object",
                "description": "Dictionary of agent name -> result"
            },
            "original_query": {
                "type": "string",
                "description": "The user's original question"
            }
        },
        "required": ["agent_results"]
    }

    async def execute(
        self, 
        agent_results: Dict[str, Any],
        original_query: str = ""
    ) -> str:
        """Synthesize response from multiple agents"""
        sections = []
        
        # Priority order for synthesis
        priority_order = ["zoning", "cma", "hbu", "ml"]
        
        for agent_type in priority_order:
            result = agent_results.get(agent_type)
            if result and not (isinstance(result, dict) and result.get("error")):
                sections.append(self._format_section(agent_type, result))
        
        # Add any other results not in priority order
        for agent_type, result in agent_results.items():
            if agent_type not in priority_order and result:
                sections.append(self._format_section(agent_type, result))
        
        if not sections:
            return "I couldn't gather enough information to provide a complete analysis. Please try a more specific query."
        
        # Combine sections
        response = "\n\n---\n\n".join(sections)
        
        # Add summary if multiple sections
        if len(sections) > 1:
            response = f"**Comprehensive Analysis**\n\n{response}"
            response += "\n\n---\n\n*Analysis complete. Ask follow-up questions for more details.*"
        
        return response

    def _format_section(self, agent_type: str, result: Any) -> str:
        """Format a single agent's result"""
        if isinstance(result, str):
            return result
        
        headers = {
            "zoning": "📍 Zoning Information",
            "cma": "💰 Market Analysis",
            "hbu": "🏗️ Highest & Best Use",
            "ml": "🤖 ML Predictions"
        }
        
        header = headers.get(agent_type, f"📊 {agent_type.title()} Analysis")
        
        if isinstance(result, dict):
            # Format dict as key-value pairs
            lines = [f"**{header}**", ""]
            for key, value in result.items():
                if key not in ["error", "raw_data"]:
                    formatted_key = key.replace("_", " ").title()
                    lines.append(f"- **{formatted_key}:** {value}")
            return "\n".join(lines)
        
        return f"**{header}**\n\n{str(result)}"


class FormatForChatTool(BaseTool):
    """Format analysis for chat interface"""
    
    name: str = "format_for_chat"
    description: str = "Format technical analysis for conversational chat display"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "analysis": {"type": "string", "description": "Raw analysis text"},
            "format_type": {
                "type": "string", 
                "enum": ["brief", "detailed", "bullet"],
                "description": "Output format style"
            }
        },
        "required": ["analysis"]
    }

    async def execute(
        self, 
        analysis: str, 
        format_type: str = "detailed"
    ) -> str:
        """Format for chat"""
        if format_type == "brief":
            # Extract first paragraph or key point
            lines = analysis.split("\n")
            key_lines = [l for l in lines if l.strip() and not l.startswith("#")]
            return key_lines[0] if key_lines else analysis[:200]
        
        elif format_type == "bullet":
            # Convert to bullet points
            lines = analysis.split("\n")
            bullets = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    bullets.append(f"• {line}")
                elif line.startswith("-"):
                    bullets.append(f"• {line[1:].strip()}")
            return "\n".join(bullets[:10])  # Max 10 bullets
        
        else:  # detailed
            return analysis


class GenerateSummaryTool(BaseTool):
    """Generate executive summary of analysis"""
    
    name: str = "generate_summary"
    description: str = "Generate an executive summary from detailed analysis"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "parcel_id": {"type": "string", "description": "Parcel ID"},
            "analyses": {
                "type": "object",
                "description": "Dictionary of analysis results"
            }
        },
        "required": ["parcel_id"]
    }

    async def execute(
        self, 
        parcel_id: str, 
        analyses: Dict[str, Any] = None
    ) -> str:
        """Generate executive summary"""
        from services.supabase_client import get_supabase
        
        supabase = get_supabase()
        
        # Get basic parcel info
        parcel = await supabase.table("fl_parcels").select(
            "address, zone_code, lot_size_sqft, assessed_value"
        ).eq("parcel_id", parcel_id).single().execute()
        
        if not parcel.data:
            return f"Could not generate summary for parcel {parcel_id}"
        
        data = parcel.data
        analyses = analyses or {}
        
        # Build summary
        summary_parts = [
            f"## Executive Summary: {parcel_id}",
            "",
            f"**Address:** {data.get('address', 'N/A')}",
            f"**Zone:** {data.get('zone_code', 'Unknown')}",
            f"**Lot Size:** {data.get('lot_size_sqft', 0):,} sq ft",
            f"**Assessed Value:** ${data.get('assessed_value', 0):,}",
            ""
        ]
        
        # Add analysis highlights
        if analyses.get("ml"):
            ml = analyses["ml"]
            if isinstance(ml, dict) and ml.get("predicted_value"):
                summary_parts.append(f"**ML Predicted Value:** ${ml['predicted_value']:,}")
        
        if analyses.get("hbu"):
            hbu = analyses["hbu"]
            if isinstance(hbu, dict) and hbu.get("recommended_use"):
                summary_parts.append(f"**Recommended Use:** {hbu['recommended_use']}")
        
        if analyses.get("cma"):
            cma = analyses["cma"]
            if isinstance(cma, dict) and cma.get("estimated_value"):
                summary_parts.append(f"**CMA Value:** ${cma['estimated_value']:,}")
        
        summary_parts.extend([
            "",
            "---",
            "*For detailed analysis, ask specific questions about zoning, valuation, or development potential.*"
        ])
        
        return "\n".join(summary_parts)


class ReporterAgent(BaseAgent):
    """Response Synthesis and Reporting Agent.
    
    Combines outputs from specialized agents into coherent, user-friendly
    responses for the chat interface.
    """

    name: str = "ReporterAgent"
    description: str = "Specialist for synthesizing multi-agent outputs into clear responses"
    domain: str = "reporter"
    
    system_prompt: str = """You are a technical writer specializing in real estate analysis.

Your responsibilities:
1. Synthesize outputs from multiple specialist agents
2. Present information clearly and concisely
3. Highlight key findings and recommendations
4. Handle conflicting information gracefully

Writing guidelines:
- Use markdown formatting for structure
- Lead with the most important information
- Include relevant numbers and data points
- Add context where helpful
- Note uncertainties or limitations

Always tailor the response to the user's original question."""

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            SynthesizeResponseTool(),
            FormatForChatTool(),
            GenerateSummaryTool()
        )
    )

    # Store results from other agents
    agent_results: Dict[str, Any] = Field(default_factory=dict)

    async def step(self) -> str:
        """Execute reporting step"""
        user_messages = [m for m in self.memory.messages if m.role == "user"]
        if not user_messages:
            return "No query to process"
        
        query = user_messages[-1].content
        
        # Check if we have results to synthesize
        if self.agent_results:
            result = await self._synthesize_results(query)
        else:
            result = await self._generate_summary(query)
        
        self.memory.add_assistant_message(result)
        self.state = AgentState.FINISHED
        return result

    async def _synthesize_results(self, query: str) -> str:
        """Synthesize multi-agent results"""
        tool = self.available_tools.get_tool("synthesize_response")
        result = await tool(
            agent_results=self.agent_results,
            original_query=query
        )
        return result.output if isinstance(result, ToolResult) else result

    async def _generate_summary(self, query: str) -> str:
        """Generate parcel summary"""
        import re
        
        parcel_pattern = r'\d{2}-\d{2}-\d{2}-[\d\w.-]+'
        parcel_match = re.search(parcel_pattern, query)
        
        if not parcel_match:
            return "Please provide a parcel ID to generate a summary."
        
        tool = self.available_tools.get_tool("generate_summary")
        result = await tool(parcel_id=parcel_match.group())
        return result.output if isinstance(result, ToolResult) else result

    def add_agent_result(self, agent_name: str, result: Any) -> None:
        """Add a result from another agent"""
        self.agent_results[agent_name] = result

    def clear_results(self) -> None:
        """Clear stored agent results"""
        self.agent_results = {}
