"""
ZoneWise V3 - MCP Client
Adapted from OpenManus MCP integration.

Provides connectivity to MCP (Model Context Protocol) servers for:
- External data sources (BCPAO, Census, Supabase)
- Tool discovery and execution
- Standardized service integration
"""

from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional
import structlog

from pydantic import BaseModel, Field

logger = structlog.get_logger()


class MCPToolResult(BaseModel):
    """Result from MCP tool execution"""
    output: Any = Field(default=None)
    error: Optional[str] = Field(default=None)
    
    def __bool__(self):
        return self.output is not None or self.error is not None


class MCPTool(BaseModel):
    """Represents a tool available from an MCP server"""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(default="", description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    server_id: str = Field(default="", description="Source MCP server")
    
    # Runtime attributes
    _session: Any = None
    _original_name: str = ""
    
    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    async def execute(self, **kwargs) -> MCPToolResult:
        """Execute the tool via MCP server"""
        if not self._session:
            return MCPToolResult(error="Not connected to MCP server")
        
        try:
            logger.info(f"Executing MCP tool: {self._original_name or self.name}")
            result = await self._session.call_tool(
                self._original_name or self.name, 
                kwargs
            )
            
            # Extract text content from result
            if hasattr(result, 'content'):
                content_parts = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        content_parts.append(item.text)
                output = ", ".join(content_parts) or "No output"
            else:
                output = str(result)
            
            return MCPToolResult(output=output)
            
        except Exception as e:
            logger.error(f"MCP tool execution failed", tool=self.name, error=str(e))
            return MCPToolResult(error=str(e))

    def to_param(self) -> Dict:
        """Convert to function call format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters or {"type": "object", "properties": {}},
            },
        }


class MCPClient(BaseModel):
    """
    MCP Client for ZoneWise.
    
    Connects to MCP servers and manages available tools through 
    the Model Context Protocol.
    
    Supported transports:
    - SSE (Server-Sent Events) for HTTP-based servers
    - stdio for local process-based servers
    """
    
    sessions: Dict[str, Any] = Field(default_factory=dict)
    exit_stacks: Dict[str, AsyncExitStack] = Field(default_factory=dict)
    tools: List[MCPTool] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True

    async def connect_sse(self, server_url: str, server_id: str = "") -> None:
        """Connect to an MCP server using SSE transport.
        
        Args:
            server_url: URL of the MCP server (e.g., http://localhost:3000/sse)
            server_id: Optional identifier for the server
        """
        try:
            from mcp import ClientSession
            from mcp.client.sse import sse_client
        except ImportError:
            logger.warning("MCP package not installed. Run: pip install mcp")
            return
        
        if not server_url:
            raise ValueError("Server URL is required")
        
        server_id = server_id or server_url
        
        # Disconnect existing connection if any
        if server_id in self.sessions:
            await self.disconnect(server_id)
        
        exit_stack = AsyncExitStack()
        self.exit_stacks[server_id] = exit_stack
        
        try:
            streams_context = sse_client(url=server_url)
            streams = await exit_stack.enter_async_context(streams_context)
            session = await exit_stack.enter_async_context(ClientSession(*streams))
            self.sessions[server_id] = session
            
            await self._discover_tools(server_id)
            logger.info(f"Connected to MCP server: {server_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server", server=server_id, error=str(e))
            await self.disconnect(server_id)
            raise

    async def connect_stdio(
        self, 
        command: str, 
        args: List[str] = None, 
        server_id: str = ""
    ) -> None:
        """Connect to an MCP server using stdio transport.
        
        Args:
            command: Command to start the server (e.g., "python", "node")
            args: Arguments for the command
            server_id: Optional identifier for the server
        """
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError:
            logger.warning("MCP package not installed. Run: pip install mcp")
            return
        
        if not command:
            raise ValueError("Server command is required")
        
        server_id = server_id or command
        args = args or []
        
        # Disconnect existing connection if any
        if server_id in self.sessions:
            await self.disconnect(server_id)
        
        exit_stack = AsyncExitStack()
        self.exit_stacks[server_id] = exit_stack
        
        try:
            server_params = StdioServerParameters(command=command, args=args)
            stdio_transport = await exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(read, write))
            self.sessions[server_id] = session
            
            await self._discover_tools(server_id)
            logger.info(f"Connected to MCP server via stdio: {server_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server", server=server_id, error=str(e))
            await self.disconnect(server_id)
            raise

    async def _discover_tools(self, server_id: str) -> None:
        """Discover and register tools from an MCP server"""
        session = self.sessions.get(server_id)
        if not session:
            return
        
        try:
            # Initialize session
            await session.initialize()
            
            # List available tools
            result = await session.list_tools()
            
            # Register tools
            for tool_info in result.tools:
                # Create prefixed name to avoid collisions
                prefixed_name = f"{server_id}_{tool_info.name}" if server_id else tool_info.name
                
                mcp_tool = MCPTool(
                    name=prefixed_name,
                    description=tool_info.description or f"Tool from {server_id}",
                    parameters=tool_info.inputSchema if hasattr(tool_info, 'inputSchema') else {},
                    server_id=server_id
                )
                mcp_tool._session = session
                mcp_tool._original_name = tool_info.name
                
                self.tools.append(mcp_tool)
                logger.debug(f"Registered MCP tool: {prefixed_name}")
            
            logger.info(f"Discovered {len(result.tools)} tools from {server_id}")
            
        except Exception as e:
            logger.error(f"Failed to discover tools", server=server_id, error=str(e))

    async def disconnect(self, server_id: str = "") -> None:
        """Disconnect from an MCP server.
        
        Args:
            server_id: Server to disconnect from. If empty, disconnects from all.
        """
        if server_id:
            servers = [server_id] if server_id in self.sessions else []
        else:
            servers = list(self.sessions.keys())
        
        for sid in servers:
            # Remove tools from this server
            self.tools = [t for t in self.tools if t.server_id != sid]
            
            # Close exit stack
            if sid in self.exit_stacks:
                try:
                    await self.exit_stacks[sid].aclose()
                except Exception as e:
                    logger.warning(f"Error closing MCP connection", server=sid, error=str(e))
                del self.exit_stacks[sid]
            
            # Remove session
            if sid in self.sessions:
                del self.sessions[sid]
            
            logger.info(f"Disconnected from MCP server: {sid}")

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_tools_for_server(self, server_id: str) -> List[MCPTool]:
        """Get all tools from a specific server"""
        return [t for t in self.tools if t.server_id == server_id]

    def to_params(self) -> List[Dict]:
        """Convert all tools to function call format"""
        return [tool.to_param() for tool in self.tools]

    @property
    def connected_servers(self) -> List[str]:
        """List of connected server IDs"""
        return list(self.sessions.keys())

    @property
    def tool_count(self) -> int:
        """Total number of available tools"""
        return len(self.tools)


# =============================================================================
# ZONEWISE MCP CONFIGURATION
# =============================================================================

class ZoneWiseMCPConfig(BaseModel):
    """Configuration for ZoneWise MCP connections"""
    
    servers: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "zonewise": {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "mcp_server.server"],
            "description": "ZoneWise MCP Server for zoning tools"
        },
        "supabase": {
            "type": "sse",
            "url": "http://localhost:3001/sse",
            "description": "Supabase MCP Server for database access"
        }
    })


async def create_mcp_client(config: ZoneWiseMCPConfig = None) -> MCPClient:
    """Factory function to create and configure MCP client.
    
    Args:
        config: Optional configuration. Uses defaults if not provided.
        
    Returns:
        Configured MCPClient instance
    """
    config = config or ZoneWiseMCPConfig()
    client = MCPClient()
    
    for server_id, server_config in config.servers.items():
        try:
            if server_config.get("type") == "sse":
                await client.connect_sse(
                    server_url=server_config.get("url", ""),
                    server_id=server_id
                )
            elif server_config.get("type") == "stdio":
                await client.connect_stdio(
                    command=server_config.get("command", ""),
                    args=server_config.get("args", []),
                    server_id=server_id
                )
        except Exception as e:
            logger.warning(f"Could not connect to MCP server", server=server_id, error=str(e))
    
    return client
