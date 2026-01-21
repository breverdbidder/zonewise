"""
ZoneWise V3 - Base Agent (Adapted from OpenManus)
Source: https://github.com/FoundationAgents/OpenManus
License: MIT

Adapted for ZoneWise domain-specific agents with:
- Removed browser/sandbox dependencies
- Added Smart Router integration
- Enhanced for parallel LangGraph execution
"""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, model_validator
import structlog

logger = structlog.get_logger()


class AgentState(str, Enum):
    """Agent execution states"""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


class Role(str, Enum):
    """Message role options"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCall(BaseModel):
    """Represents a tool/function call in a message"""
    id: str
    type: str = "function"
    function: Dict[str, Any]


class Message(BaseModel):
    """Represents a chat message in the conversation"""
    role: str = Field(...)
    content: Optional[str] = Field(default=None)
    tool_calls: Optional[List[ToolCall]] = Field(default=None)
    name: Optional[str] = Field(default=None)
    tool_call_id: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

    def to_dict(self) -> dict:
        """Convert message to dictionary format"""
        message = {"role": self.role}
        if self.content is not None:
            message["content"] = self.content
        if self.tool_calls is not None:
            message["tool_calls"] = [tc.model_dump() for tc in self.tool_calls]
        if self.name is not None:
            message["name"] = self.name
        if self.tool_call_id is not None:
            message["tool_call_id"] = self.tool_call_id
        return message

    @classmethod
    def user_message(cls, content: str) -> "Message":
        return cls(role=Role.USER.value, content=content)

    @classmethod
    def assistant_message(cls, content: str) -> "Message":
        return cls(role=Role.ASSISTANT.value, content=content)

    @classmethod
    def system_message(cls, content: str) -> "Message":
        return cls(role=Role.SYSTEM.value, content=content)

    @classmethod
    def tool_message(cls, content: str, tool_call_id: str, name: str) -> "Message":
        return cls(
            role=Role.TOOL.value,
            content=content,
            tool_call_id=tool_call_id,
            name=name
        )


class Memory(BaseModel):
    """Agent memory store for conversation history"""
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = Field(default=100)

    def add_message(self, message: Message) -> None:
        """Add a message to memory"""
        self.messages.append(message)
        # Trim old messages if over limit
        if len(self.messages) > self.max_messages:
            # Keep system message + recent messages
            system_msgs = [m for m in self.messages if m.role == Role.SYSTEM.value]
            other_msgs = [m for m in self.messages if m.role != Role.SYSTEM.value]
            self.messages = system_msgs + other_msgs[-(self.max_messages - len(system_msgs)):]

    def add_user_message(self, content: str) -> None:
        self.add_message(Message.user_message(content))

    def add_assistant_message(self, content: str) -> None:
        self.add_message(Message.assistant_message(content))

    def get_messages(self) -> List[Dict]:
        """Get all messages as dictionaries"""
        return [m.to_dict() for m in self.messages]

    def clear(self) -> None:
        """Clear all messages except system"""
        self.messages = [m for m in self.messages if m.role == Role.SYSTEM.value]


class BaseAgent(BaseModel, ABC):
    """Abstract base class for ZoneWise agents.
    
    Adapted from OpenManus BaseAgent with ZoneWise-specific enhancements:
    - Smart Router integration for cost-optimized LLM calls
    - Parallel execution support for LangGraph
    - Domain-specific tool support
    
    Subclasses must implement the `step` method.
    """

    # Core attributes
    name: str = Field(..., description="Unique name of the agent")
    description: Optional[str] = Field(None, description="Agent description")

    # Prompts
    system_prompt: Optional[str] = Field(None, description="System-level instruction")
    next_step_prompt: Optional[str] = Field(None, description="Prompt for next action")

    # State management
    memory: Memory = Field(default_factory=Memory, description="Agent memory store")
    state: AgentState = Field(default=AgentState.IDLE, description="Current state")

    # Execution control
    max_steps: int = Field(default=10, description="Maximum steps before termination")
    current_step: int = Field(default=0, description="Current step in execution")
    
    # ZoneWise-specific
    domain: str = Field(default="zoning", description="Agent domain (zoning, cma, hbu, ml)")
    confidence_threshold: float = Field(default=0.7, description="Minimum confidence for responses")

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    @model_validator(mode="after")
    def initialize_agent(self) -> "BaseAgent":
        """Initialize agent with default settings"""
        if not isinstance(self.memory, Memory):
            self.memory = Memory()
        # Add system prompt to memory if provided
        if self.system_prompt and not any(
            m.role == Role.SYSTEM.value for m in self.memory.messages
        ):
            self.memory.add_message(Message.system_message(self.system_prompt))
        return self

    @asynccontextmanager
    async def state_context(self, new_state: AgentState):
        """Context manager for safe state transitions"""
        if not isinstance(new_state, AgentState):
            raise ValueError(f"Invalid state: {new_state}")

        previous_state = self.state
        self.state = new_state
        try:
            yield
        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"Agent {self.name} error", error=str(e))
            raise
        finally:
            if self.state != AgentState.ERROR:
                self.state = previous_state

    @abstractmethod
    async def step(self) -> str:
        """Execute a single step of the agent.
        
        Returns:
            str: Result of the step execution
        """
        pass

    async def run(self, request: Optional[str] = None) -> str:
        """Execute the agent's main loop.
        
        Args:
            request: Optional initial request to process
            
        Returns:
            str: Final result of agent execution
        """
        if request:
            self.memory.add_user_message(request)

        results = []
        
        async with self.state_context(AgentState.RUNNING):
            while self.current_step < self.max_steps:
                self.current_step += 1
                logger.info(
                    f"Agent {self.name} step {self.current_step}/{self.max_steps}"
                )
                
                try:
                    step_result = await self.step()
                    results.append(step_result)
                    
                    # Check if agent is done
                    if self.is_complete():
                        break
                        
                except Exception as e:
                    logger.error(f"Step {self.current_step} failed", error=str(e))
                    raise

        self.state = AgentState.FINISHED
        return self.format_results(results)

    def is_complete(self) -> bool:
        """Check if agent has completed its task.
        
        Override in subclasses for custom completion logic.
        """
        return self.state == AgentState.FINISHED

    def format_results(self, results: List[str]) -> str:
        """Format step results into final output.
        
        Override in subclasses for custom formatting.
        """
        return "\n".join(filter(None, results))

    def reset(self) -> None:
        """Reset agent to initial state"""
        self.current_step = 0
        self.state = AgentState.IDLE
        self.memory.clear()
        if self.system_prompt:
            self.memory.add_message(Message.system_message(self.system_prompt))


class ToolResult(BaseModel):
    """Represents the result of a tool execution"""
    output: Any = Field(default=None)
    error: Optional[str] = Field(default=None)
    confidence: float = Field(default=1.0)
    sources: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def __bool__(self):
        return self.output is not None or self.error is not None

    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        return str(self.output) if self.output else ""


class BaseTool(BaseModel, ABC):
    """Base class for ZoneWise tools.
    
    Adapted from OpenManus BaseTool with ZoneWise enhancements.
    """

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    async def __call__(self, **kwargs) -> ToolResult:
        """Execute the tool"""
        try:
            result = await self.execute(**kwargs)
            return ToolResult(output=result)
        except Exception as e:
            logger.error(f"Tool {self.name} failed", error=str(e))
            return ToolResult(error=str(e))

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        pass

    def to_param(self) -> Dict:
        """Convert tool to function call format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters or {"type": "object", "properties": {}},
            },
        }


class ToolCollection(BaseModel):
    """Collection of tools available to an agent"""
    
    tools: List[BaseTool] = Field(default_factory=list)

    def __init__(self, *tools: BaseTool, **data):
        super().__init__(**data)
        self.tools = list(tools)

    def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the collection"""
        self.tools.append(tool)

    def add_tools(self, *tools: BaseTool) -> None:
        """Add multiple tools"""
        self.tools.extend(tools)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def to_params(self) -> List[Dict]:
        """Convert all tools to function call format"""
        return [tool.to_param() for tool in self.tools]

    def __iter__(self):
        return iter(self.tools)

    def __len__(self):
        return len(self.tools)
