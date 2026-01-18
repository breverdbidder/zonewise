#!/usr/bin/env python3
"""
ZoneWise MCP Server
Exposes zoning compliance tools via Model Context Protocol

Usage:
  - Claude Desktop: Add to claude_desktop_config.json
  - Cursor: Add to .cursor/mcp.json
  - Custom apps: Connect via MCP client SDK

Tools:
  - lookup_zoning: Get dimensional standards for a district
  - check_compliance: Verify proposed structure meets requirements
  - list_districts: Get all districts for a jurisdiction
  - search_ordinance: Search ordinance text
  - get_permitted_uses: List permitted uses

Author: Ariel Shapira / Claude AI Architect
Date: January 18, 2026
"""

import os
import json
import httpx
from typing import Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Supabase configuration
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Initialize MCP server
server = Server("zonewise")


async def query_supabase(table: str, params: dict) -> list:
    """Execute a Supabase REST API query."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


def parse_dimensions(description: str) -> dict:
    """Extract dimensional data from description field."""
    # Data is embedded as HTML comment: <!--DIMS:{...}-->
    import re
    match = re.search(r'<!--DIMS:(\{.*?\})-->', description)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return {}


# Define MCP Tools
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="lookup_zoning",
            description="Get dimensional standards (setbacks, height, lot size) for a specific zoning district in a Brevard County jurisdiction",
            inputSchema={
                "type": "object",
                "properties": {
                    "jurisdiction": {
                        "type": "string",
                        "description": "Municipality name (e.g., 'Melbourne', 'Indian Harbour Beach', 'Palm Bay')"
                    },
                    "district_code": {
                        "type": "string",
                        "description": "Zoning district code (e.g., 'R-1', 'R-2', 'C-1', 'PUD')"
                    }
                },
                "required": ["jurisdiction", "district_code"]
            }
        ),
        Tool(
            name="check_compliance",
            description="Verify if a proposed structure meets zoning requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "jurisdiction": {"type": "string", "description": "Municipality name"},
                    "district_code": {"type": "string", "description": "Zoning district code"},
                    "front_setback": {"type": "number", "description": "Proposed front setback in feet"},
                    "side_setback": {"type": "number", "description": "Proposed side setback in feet"},
                    "rear_setback": {"type": "number", "description": "Proposed rear setback in feet"},
                    "height": {"type": "number", "description": "Proposed building height in feet"},
                    "lot_size": {"type": "number", "description": "Lot size in square feet"}
                },
                "required": ["jurisdiction", "district_code"]
            }
        ),
        Tool(
            name="list_districts",
            description="Get all zoning districts for a Brevard County jurisdiction",
            inputSchema={
                "type": "object",
                "properties": {
                    "jurisdiction": {
                        "type": "string",
                        "description": "Municipality name (e.g., 'Melbourne', 'Satellite Beach')"
                    }
                },
                "required": ["jurisdiction"]
            }
        ),
        Tool(
            name="list_jurisdictions",
            description="Get all available Brevard County jurisdictions",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="search_ordinance",
            description="Search zoning ordinance content for specific terms",
            inputSchema={
                "type": "object",
                "properties": {
                    "jurisdiction": {"type": "string", "description": "Municipality name"},
                    "query": {"type": "string", "description": "Search terms"}
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle MCP tool calls."""
    
    if name == "lookup_zoning":
        jurisdiction = arguments.get("jurisdiction", "")
        district_code = arguments.get("district_code", "").upper()
        
        # Get jurisdiction ID
        jurisdictions = await query_supabase("jurisdictions", {
            "select": "id,name",
            "name": f"ilike.%{jurisdiction}%"
        })
        
        if not jurisdictions:
            return [TextContent(
                type="text",
                text=f"❌ Jurisdiction '{jurisdiction}' not found. Use list_jurisdictions to see available options."
            )]
        
        jurisdiction_id = jurisdictions[0]["id"]
        jurisdiction_name = jurisdictions[0]["name"]
        
        # Get district
        districts = await query_supabase("zoning_districts", {
            "select": "*",
            "jurisdiction_id": f"eq.{jurisdiction_id}",
            "code": f"ilike.{district_code}"
        })
        
        if not districts:
            return [TextContent(
                type="text",
                text=f"❌ District '{district_code}' not found in {jurisdiction_name}. Use list_districts to see available options."
            )]
        
        d = districts[0]
        dims = parse_dimensions(d.get("description", ""))
        
        result = f"""## {d['name']} ({d['code']}) - {jurisdiction_name}

**Category:** {d.get('category', 'N/A')}

### Dimensional Standards
| Requirement | Value |
|-------------|-------|
| Minimum Lot Size | {dims.get('min_lot_sqft', 'N/A'):,} sq ft |
| Maximum Height | {dims.get('max_height_ft', 'N/A')} ft ({dims.get('max_stories', 'N/A')} stories) |
| Lot Coverage | {dims.get('coverage_pct', 'N/A')}% |

### Setbacks
| Direction | Minimum |
|-----------|---------|
| Front | {dims.get('setbacks_ft', {}).get('front', 'N/A')} ft |
| Side | {dims.get('setbacks_ft', {}).get('side', 'N/A')} ft |
| Rear | {dims.get('setbacks_ft', {}).get('rear', 'N/A')} ft |

**Source:** {d.get('ordinance_section', 'Municipal Code')}
"""
        return [TextContent(type="text", text=result)]
    
    elif name == "check_compliance":
        jurisdiction = arguments.get("jurisdiction", "")
        district_code = arguments.get("district_code", "").upper()
        
        # Get district data first
        jurisdictions = await query_supabase("jurisdictions", {
            "select": "id,name",
            "name": f"ilike.%{jurisdiction}%"
        })
        
        if not jurisdictions:
            return [TextContent(type="text", text=f"❌ Jurisdiction not found")]
        
        jurisdiction_id = jurisdictions[0]["id"]
        
        districts = await query_supabase("zoning_districts", {
            "select": "*",
            "jurisdiction_id": f"eq.{jurisdiction_id}",
            "code": f"ilike.{district_code}"
        })
        
        if not districts:
            return [TextContent(type="text", text=f"❌ District not found")]
        
        dims = parse_dimensions(districts[0].get("description", ""))
        setbacks = dims.get("setbacks_ft", {})
        
        violations = []
        compliant = []
        
        # Check each provided dimension
        if "front_setback" in arguments and setbacks.get("front"):
            if arguments["front_setback"] < setbacks["front"]:
                violations.append(f"❌ Front setback: {arguments['front_setback']}ft < {setbacks['front']}ft required")
            else:
                compliant.append(f"✅ Front setback: {arguments['front_setback']}ft ≥ {setbacks['front']}ft required")
        
        if "side_setback" in arguments and setbacks.get("side"):
            if arguments["side_setback"] < setbacks["side"]:
                violations.append(f"❌ Side setback: {arguments['side_setback']}ft < {setbacks['side']}ft required")
            else:
                compliant.append(f"✅ Side setback: {arguments['side_setback']}ft ≥ {setbacks['side']}ft required")
        
        if "rear_setback" in arguments and setbacks.get("rear"):
            if arguments["rear_setback"] < setbacks["rear"]:
                violations.append(f"❌ Rear setback: {arguments['rear_setback']}ft < {setbacks['rear']}ft required")
            else:
                compliant.append(f"✅ Rear setback: {arguments['rear_setback']}ft ≥ {setbacks['rear']}ft required")
        
        if "height" in arguments and dims.get("max_height_ft"):
            if arguments["height"] > dims["max_height_ft"]:
                violations.append(f"❌ Height: {arguments['height']}ft > {dims['max_height_ft']}ft maximum")
            else:
                compliant.append(f"✅ Height: {arguments['height']}ft ≤ {dims['max_height_ft']}ft maximum")
        
        if "lot_size" in arguments and dims.get("min_lot_sqft"):
            if arguments["lot_size"] < dims["min_lot_sqft"]:
                violations.append(f"❌ Lot size: {arguments['lot_size']:,}sqft < {dims['min_lot_sqft']:,}sqft minimum")
            else:
                compliant.append(f"✅ Lot size: {arguments['lot_size']:,}sqft ≥ {dims['min_lot_sqft']:,}sqft minimum")
        
        status = "🚫 NON-COMPLIANT" if violations else "✅ COMPLIANT"
        
        result = f"""## Compliance Check: {district_code} in {jurisdiction}

**Status: {status}**

### Results
{chr(10).join(compliant)}
{chr(10).join(violations)}

*Disclaimer: This is for informational purposes only. Always verify with the local planning department before construction.*
"""
        return [TextContent(type="text", text=result)]
    
    elif name == "list_districts":
        jurisdiction = arguments.get("jurisdiction", "")
        
        jurisdictions = await query_supabase("jurisdictions", {
            "select": "id,name",
            "name": f"ilike.%{jurisdiction}%"
        })
        
        if not jurisdictions:
            return [TextContent(type="text", text=f"❌ Jurisdiction not found")]
        
        jurisdiction_id = jurisdictions[0]["id"]
        jurisdiction_name = jurisdictions[0]["name"]
        
        districts = await query_supabase("zoning_districts", {
            "select": "code,name,category",
            "jurisdiction_id": f"eq.{jurisdiction_id}",
            "order": "code"
        })
        
        result = f"## Zoning Districts in {jurisdiction_name}\n\n"
        result += "| Code | Name | Category |\n|------|------|----------|\n"
        for d in districts:
            result += f"| {d['code']} | {d['name']} | {d.get('category', 'N/A')} |\n"
        
        result += f"\n*Total: {len(districts)} districts*"
        
        return [TextContent(type="text", text=result)]
    
    elif name == "list_jurisdictions":
        jurisdictions = await query_supabase("jurisdictions", {
            "select": "id,name",
            "order": "name"
        })
        
        result = "## Brevard County Jurisdictions\n\n"
        for j in jurisdictions:
            result += f"- {j['name']}\n"
        
        result += f"\n*Total: {len(jurisdictions)} jurisdictions*"
        
        return [TextContent(type="text", text=result)]
    
    elif name == "search_ordinance":
        query = arguments.get("query", "")
        jurisdiction = arguments.get("jurisdiction", "")
        
        params = {
            "select": "code,name,description,jurisdiction_id",
            "description": f"ilike.%{query}%",
            "limit": "10"
        }
        
        if jurisdiction:
            jurisdictions = await query_supabase("jurisdictions", {
                "select": "id",
                "name": f"ilike.%{jurisdiction}%"
            })
            if jurisdictions:
                params["jurisdiction_id"] = f"eq.{jurisdictions[0]['id']}"
        
        districts = await query_supabase("zoning_districts", params)
        
        if not districts:
            return [TextContent(type="text", text=f"No results found for '{query}'")]
        
        result = f"## Search Results for '{query}'\n\n"
        for d in districts:
            # Truncate description for display
            desc = d.get('description', '')[:200] + "..." if len(d.get('description', '')) > 200 else d.get('description', '')
            result += f"### {d['code']} - {d['name']}\n{desc}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
