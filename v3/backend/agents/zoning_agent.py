"""
ZoneWise V3 - Zoning Agent
Extends OpenManus BaseAgent pattern for domain-specific zoning intelligence.

Responsibilities:
- Zone code lookup by parcel ID or address
- Zoning rules and dimensional standards
- Permitted/conditional use determination
- Setback calculations
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import structlog

from agents.base import BaseAgent, BaseTool, ToolCollection, ToolResult, AgentState

logger = structlog.get_logger()


# =============================================================================
# ZONING TOOLS
# =============================================================================

class ZoneLookupTool(BaseTool):
    """Look up zoning information for a parcel"""
    
    name: str = "zone_lookup"
    description: str = "Look up zoning code and district for a given parcel ID or address"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "parcel_id": {
                "type": "string",
                "description": "Brevard County parcel ID (e.g., 25-37-22-00-00123.0-0000.00)"
            },
            "address": {
                "type": "string",
                "description": "Property address for lookup"
            }
        },
        "required": []
    }

    async def execute(self, parcel_id: str = None, address: str = None) -> Dict[str, Any]:
        """Execute zone lookup"""
        from services.supabase_client import get_supabase
        
        supabase = get_supabase()
        
        if parcel_id:
            result = await supabase.table("fl_parcels").select(
                "parcel_id, zone_code, zone_district, jurisdiction"
            ).eq("parcel_id", parcel_id).single().execute()
        elif address:
            result = await supabase.table("fl_parcels").select(
                "parcel_id, zone_code, zone_district, jurisdiction, address"
            ).ilike("address", f"%{address}%").limit(1).execute()
        else:
            raise ValueError("Either parcel_id or address must be provided")
        
        if result.data:
            return result.data
        return {"error": "Parcel not found"}


class ZoneRulesTool(BaseTool):
    """Get zoning rules and dimensional standards"""
    
    name: str = "zone_rules"
    description: str = "Get zoning rules, dimensional standards, and restrictions for a zone code"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "zone_code": {
                "type": "string",
                "description": "Zoning code (e.g., RS-1, BU-1, IU-1)"
            },
            "jurisdiction": {
                "type": "string",
                "description": "Municipality or county jurisdiction"
            }
        },
        "required": ["zone_code"]
    }

    async def execute(self, zone_code: str, jurisdiction: str = "Brevard County") -> Dict[str, Any]:
        """Execute zone rules lookup"""
        from services.supabase_client import get_supabase
        
        supabase = get_supabase()
        
        result = await supabase.table("fl_zoning_districts").select(
            "zone_code, zone_name, min_lot_size_sqft, min_lot_width_ft, "
            "max_height_ft, max_lot_coverage_pct, front_setback_ft, "
            "side_setback_ft, rear_setback_ft, permitted_uses, conditional_uses"
        ).eq("zone_code", zone_code).eq("jurisdiction", jurisdiction).single().execute()
        
        if result.data:
            return result.data
        return {"error": f"Zone code {zone_code} not found in {jurisdiction}"}


class PermittedUsesTool(BaseTool):
    """Check if a use is permitted in a zone"""
    
    name: str = "permitted_uses"
    description: str = "Check if a specific use is permitted, conditional, or prohibited in a zone"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "zone_code": {
                "type": "string",
                "description": "Zoning code"
            },
            "use_type": {
                "type": "string",
                "description": "Proposed use (e.g., single-family, multi-family, retail, office)"
            }
        },
        "required": ["zone_code", "use_type"]
    }

    async def execute(self, zone_code: str, use_type: str) -> Dict[str, Any]:
        """Check permitted uses"""
        from services.supabase_client import get_supabase
        
        supabase = get_supabase()
        
        result = await supabase.table("fl_zoning_districts").select(
            "permitted_uses, conditional_uses"
        ).eq("zone_code", zone_code).single().execute()
        
        if not result.data:
            return {"error": f"Zone code {zone_code} not found"}
        
        permitted = result.data.get("permitted_uses", []) or []
        conditional = result.data.get("conditional_uses", []) or []
        
        use_lower = use_type.lower()
        
        # Check if use is permitted
        for use in permitted:
            if use_lower in use.lower():
                return {
                    "use_type": use_type,
                    "zone_code": zone_code,
                    "status": "PERMITTED",
                    "conditions": None
                }
        
        # Check if use is conditional
        for use in conditional:
            if use_lower in use.lower():
                return {
                    "use_type": use_type,
                    "zone_code": zone_code,
                    "status": "CONDITIONAL",
                    "conditions": "Requires special exception or conditional use permit"
                }
        
        return {
            "use_type": use_type,
            "zone_code": zone_code,
            "status": "PROHIBITED",
            "conditions": None
        }


class SetbackCalculatorTool(BaseTool):
    """Calculate setbacks for a parcel"""
    
    name: str = "setback_calculator"
    description: str = "Calculate required setbacks based on zone and lot dimensions"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "parcel_id": {
                "type": "string",
                "description": "Parcel ID for setback calculation"
            },
            "lot_width_ft": {
                "type": "number",
                "description": "Lot width in feet (optional, will lookup if not provided)"
            },
            "lot_depth_ft": {
                "type": "number",
                "description": "Lot depth in feet (optional)"
            }
        },
        "required": ["parcel_id"]
    }

    async def execute(
        self, 
        parcel_id: str, 
        lot_width_ft: float = None, 
        lot_depth_ft: float = None
    ) -> Dict[str, Any]:
        """Calculate setbacks"""
        from services.supabase_client import get_supabase
        
        supabase = get_supabase()
        
        # Get parcel zone
        parcel = await supabase.table("fl_parcels").select(
            "zone_code, lot_size_sqft, jurisdiction"
        ).eq("parcel_id", parcel_id).single().execute()
        
        if not parcel.data:
            return {"error": "Parcel not found"}
        
        zone_code = parcel.data["zone_code"]
        jurisdiction = parcel.data.get("jurisdiction", "Brevard County")
        
        # Get zone rules
        zone = await supabase.table("fl_zoning_districts").select(
            "front_setback_ft, side_setback_ft, rear_setback_ft, "
            "min_lot_width_ft, corner_lot_setback_ft"
        ).eq("zone_code", zone_code).eq("jurisdiction", jurisdiction).single().execute()
        
        if not zone.data:
            return {"error": f"Zone {zone_code} rules not found"}
        
        return {
            "parcel_id": parcel_id,
            "zone_code": zone_code,
            "setbacks": {
                "front_ft": zone.data.get("front_setback_ft", 25),
                "side_ft": zone.data.get("side_setback_ft", 7.5),
                "rear_ft": zone.data.get("rear_setback_ft", 20),
                "corner_ft": zone.data.get("corner_lot_setback_ft", 15)
            },
            "buildable_area_note": "Subtract setbacks from lot dimensions for buildable envelope"
        }


# =============================================================================
# ZONING AGENT
# =============================================================================

class ZoningAgent(BaseAgent):
    """Specialized agent for Florida zoning intelligence.
    
    Extends OpenManus BaseAgent with domain-specific tools and knowledge
    for Brevard County and Florida zoning regulations.
    """

    name: str = "ZoningAgent"
    description: str = "Specialist for Florida zoning regulations, dimensional standards, and permitted uses"
    domain: str = "zoning"
    
    system_prompt: str = """You are a Florida zoning expert specializing in Brevard County regulations.
    
Your responsibilities:
1. Look up zoning codes for parcels by ID or address
2. Explain dimensional standards (setbacks, height, lot coverage)
3. Determine if uses are permitted, conditional, or prohibited
4. Calculate buildable envelopes based on setbacks

Always cite the specific zone code and jurisdiction in your responses.
When uncertain, recommend the user consult with the local planning department.

Available zones in Brevard County include:
- Residential: RS-1, RS-2, RS-3, RS-4, RS-5, RS-6, RM-4, RM-8, RM-12, RM-15
- Commercial: BU-1, BU-1-A, BU-2
- Industrial: IU-1, IU-2, IU-3
- Agricultural: AU, AA, AE
- Planned: PUD, PIP, RVP
"""

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            ZoneLookupTool(),
            ZoneRulesTool(),
            PermittedUsesTool(),
            SetbackCalculatorTool()
        )
    )

    async def step(self) -> str:
        """Execute a single step of zoning analysis"""
        # Get the last user message
        user_messages = [m for m in self.memory.messages if m.role == "user"]
        if not user_messages:
            return "No query to process"
        
        query = user_messages[-1].content
        
        # Analyze query intent
        intent = await self._detect_intent(query)
        
        # Execute appropriate tool
        if intent == "zone_lookup":
            result = await self._handle_zone_lookup(query)
        elif intent == "zone_rules":
            result = await self._handle_zone_rules(query)
        elif intent == "permitted_uses":
            result = await self._handle_permitted_uses(query)
        elif intent == "setbacks":
            result = await self._handle_setbacks(query)
        else:
            result = await self._handle_general_query(query)
        
        self.memory.add_assistant_message(result)
        self.state = AgentState.FINISHED
        return result

    async def _detect_intent(self, query: str) -> str:
        """Detect the intent of the query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["setback", "buildable", "envelope"]):
            return "setbacks"
        if any(word in query_lower for word in ["permit", "allow", "can i build", "conditional"]):
            return "permitted_uses"
        if any(word in query_lower for word in ["rule", "standard", "height", "coverage", "requirement"]):
            return "zone_rules"
        if any(word in query_lower for word in ["zone", "zoning", "what zone", "parcel"]):
            return "zone_lookup"
        return "general"

    async def _handle_zone_lookup(self, query: str) -> str:
        """Handle zone lookup queries"""
        tool = self.available_tools.get_tool("zone_lookup")
        
        # Extract parcel ID or address from query
        # Simple extraction - in production use LLM for entity extraction
        import re
        parcel_pattern = r'\d{2}-\d{2}-\d{2}-[\d\w.-]+'
        parcel_match = re.search(parcel_pattern, query)
        
        if parcel_match:
            result = await tool(parcel_id=parcel_match.group())
        else:
            # Assume it's an address query
            result = await tool(address=query)
        
        if result.error:
            return f"I couldn't find zoning information: {result.error}"
        
        data = result.output
        return f"""**Zoning Information**

- **Parcel ID:** {data.get('parcel_id', 'N/A')}
- **Zone Code:** {data.get('zone_code', 'Unknown')}
- **Zone District:** {data.get('zone_district', 'Unknown')}
- **Jurisdiction:** {data.get('jurisdiction', 'Brevard County')}

Would you like me to look up the dimensional standards for this zone?"""

    async def _handle_zone_rules(self, query: str) -> str:
        """Handle zone rules queries"""
        tool = self.available_tools.get_tool("zone_rules")
        
        # Extract zone code from query
        import re
        zone_pattern = r'[A-Z]{2,3}-?\d{1,2}-?[A-Z]?'
        zone_match = re.search(zone_pattern, query.upper())
        
        if not zone_match:
            return "Please provide a zone code (e.g., RS-1, BU-1, IU-2) to look up rules."
        
        result = await tool(zone_code=zone_match.group())
        
        if result.error:
            return f"I couldn't find rules for that zone: {result.error}"
        
        data = result.output
        return f"""**Zoning Rules for {data.get('zone_code', 'Unknown')}**

**{data.get('zone_name', 'Zone')}**

| Standard | Requirement |
|----------|-------------|
| Min Lot Size | {data.get('min_lot_size_sqft', 'N/A'):,} sq ft |
| Min Lot Width | {data.get('min_lot_width_ft', 'N/A')} ft |
| Max Height | {data.get('max_height_ft', 'N/A')} ft |
| Max Lot Coverage | {data.get('max_lot_coverage_pct', 'N/A')}% |
| Front Setback | {data.get('front_setback_ft', 'N/A')} ft |
| Side Setback | {data.get('side_setback_ft', 'N/A')} ft |
| Rear Setback | {data.get('rear_setback_ft', 'N/A')} ft |

**Permitted Uses:** {', '.join(data.get('permitted_uses', [])[:5]) or 'See local ordinance'}

Would you like me to check if a specific use is permitted?"""

    async def _handle_permitted_uses(self, query: str) -> str:
        """Handle permitted uses queries"""
        tool = self.available_tools.get_tool("permitted_uses")
        
        # Extract zone and use from query
        import re
        zone_pattern = r'[A-Z]{2,3}-?\d{1,2}-?[A-Z]?'
        zone_match = re.search(zone_pattern, query.upper())
        
        if not zone_match:
            return "Please provide a zone code to check permitted uses."
        
        # Common use types to check
        use_keywords = {
            "single": "single-family residential",
            "multi": "multi-family residential",
            "duplex": "duplex",
            "retail": "retail",
            "office": "office",
            "restaurant": "restaurant",
            "warehouse": "warehouse",
            "industrial": "industrial",
            "commercial": "commercial"
        }
        
        use_type = "residential"  # default
        for keyword, use in use_keywords.items():
            if keyword in query.lower():
                use_type = use
                break
        
        result = await tool(zone_code=zone_match.group(), use_type=use_type)
        
        if result.error:
            return f"Error checking permitted uses: {result.error}"
        
        data = result.output
        status_emoji = {
            "PERMITTED": "✅",
            "CONDITIONAL": "⚠️",
            "PROHIBITED": "❌"
        }
        
        return f"""**Use Determination**

{status_emoji.get(data['status'], '❓')} **{data['use_type']}** is **{data['status']}** in zone **{data['zone_code']}**

{f"*Conditions:* {data['conditions']}" if data.get('conditions') else ""}

Would you like me to check another use type?"""

    async def _handle_setbacks(self, query: str) -> str:
        """Handle setback calculation queries"""
        tool = self.available_tools.get_tool("setback_calculator")
        
        # Extract parcel ID from query
        import re
        parcel_pattern = r'\d{2}-\d{2}-\d{2}-[\d\w.-]+'
        parcel_match = re.search(parcel_pattern, query)
        
        if not parcel_match:
            return "Please provide a parcel ID to calculate setbacks."
        
        result = await tool(parcel_id=parcel_match.group())
        
        if result.error:
            return f"Error calculating setbacks: {result.error}"
        
        data = result.output
        setbacks = data.get('setbacks', {})
        
        return f"""**Setback Requirements for {data['parcel_id']}**

Zone: **{data['zone_code']}**

| Setback | Distance |
|---------|----------|
| Front | {setbacks.get('front_ft', 'N/A')} ft |
| Side (each) | {setbacks.get('side_ft', 'N/A')} ft |
| Rear | {setbacks.get('rear_ft', 'N/A')} ft |
| Corner (if applicable) | {setbacks.get('corner_ft', 'N/A')} ft |

*Note: {data.get('buildable_area_note', 'Verify with local planning department.')}*"""

    async def _handle_general_query(self, query: str) -> str:
        """Handle general zoning queries"""
        return """I can help you with:

1. **Zone Lookup** - Find the zoning for a parcel by ID or address
2. **Dimensional Standards** - Height, setbacks, lot coverage requirements
3. **Permitted Uses** - Check if a use is allowed in a zone
4. **Setback Calculations** - Calculate buildable envelope

Please provide a parcel ID or zone code to get started."""
