"""
ZoneWise V3 - Agent Orchestrator
Coordinates multiple specialized agents for zoning intelligence.
Replaces OpenManus default UI with custom ShadCNBlocks frontend.
"""

import asyncio
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import structlog

from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from agents.zoning_agent import ZoningAgent
from agents.cma_agent import CMAAgent
from agents.hbu_agent import HBUAgent
from agents.ml_agent import MLAgent
from agents.reporter_agent import ReporterAgent
from services.llm_router import LLMRouter

logger = structlog.get_logger()


class AgentTask(str, Enum):
    """Task types that can be assigned to agents."""
    ZONING_LOOKUP = "zoning_lookup"
    CMA_ANALYSIS = "cma_analysis"
    HBU_ANALYSIS = "hbu_analysis"
    ML_PREDICTION = "ml_prediction"
    REPORT_GENERATION = "report_generation"


@dataclass
class AgentState:
    """State passed between agents in the workflow."""
    # Input
    user_query: str
    session_id: str
    map_context: dict = field(default_factory=dict)
    selected_parcel: Optional[str] = None
    conversation_history: list = field(default_factory=list)
    
    # Processing
    detected_intent: Optional[str] = None
    extracted_entities: dict = field(default_factory=dict)
    pending_tasks: list = field(default_factory=list)
    
    # Agent results
    zoning_result: Optional[dict] = None
    cma_result: Optional[dict] = None
    hbu_result: Optional[dict] = None
    ml_result: Optional[dict] = None
    
    # Output
    response: Optional[str] = None
    map_actions: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    confidence: float = 0.0


class MapAction(BaseModel):
    """Action to be performed on the map."""
    type: str  # highlight, zoom, filter, layer
    payload: dict
    label: str


class ChatResponse(BaseModel):
    """Response to be sent to the chat frontend."""
    id: str
    content: str
    intent: Optional[str] = None
    confidence: float = 0.0
    entities: dict = {}
    map_actions: list[MapAction] = []
    suggestions: list[str] = []
    sources: list[dict] = []


class AgentOrchestrator:
    """
    Coordinates multiple specialized agents to process user queries.
    
    Architecture:
    - Coordinator: Decomposes tasks and routes to agents
    - Zoning Agent: Zone lookup, rules, dimensional standards
    - CMA Agent: Comparable market analysis
    - HBU Agent: Highest and best use analysis
    - ML Agent: XGBoost price/probability predictions
    - Reporter Agent: Synthesizes results into natural language
    """
    
    def __init__(self):
        self.llm_router = LLMRouter()
        self.zoning_agent = ZoningAgent(self.llm_router)
        self.cma_agent = CMAAgent(self.llm_router)
        self.hbu_agent = HBUAgent(self.llm_router)
        self.ml_agent = MLAgent()
        self.reporter_agent = ReporterAgent(self.llm_router)
        self.workflow = self._build_workflow()
        
        logger.info("AgentOrchestrator initialized", agents=["zoning", "cma", "hbu", "ml", "reporter"])
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for agent orchestration."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("coordinator", self._coordinator_node)
        workflow.add_node("parallel_agents", self._parallel_agents_node)
        workflow.add_node("reporter", self._reporter_node)
        
        # Set entry point
        workflow.set_entry_point("coordinator")
        
        # Add edges
        workflow.add_conditional_edges(
            "coordinator",
            self._route_from_coordinator,
            {
                "parallel": "parallel_agents",
                "direct": "reporter",
            }
        )
        workflow.add_edge("parallel_agents", "reporter")
        workflow.add_edge("reporter", END)
        
        return workflow.compile()
    
    async def _coordinator_node(self, state: AgentState) -> AgentState:
        """
        Coordinator agent: Analyzes query and determines which agents to invoke.
        Uses Claude Sonnet 4.5 for complex reasoning.
        """
        logger.info("Coordinator analyzing query", query=state.user_query[:100])
        
        # Use LLM to classify intent and extract entities
        classification = await self.llm_router.classify_intent(
            query=state.user_query,
            context=state.map_context,
            parcel_id=state.selected_parcel,
        )
        
        state.detected_intent = classification.get("intent")
        state.extracted_entities = classification.get("entities", {})
        
        # Determine which agents to invoke based on intent
        intent_to_tasks = {
            "feasibility_check": [AgentTask.ZONING_LOOKUP, AgentTask.HBU_ANALYSIS],
            "zoning_lookup": [AgentTask.ZONING_LOOKUP],
            "allowed_uses": [AgentTask.ZONING_LOOKUP],
            "dimensional_standards": [AgentTask.ZONING_LOOKUP],
            "hbu_analysis": [AgentTask.ZONING_LOOKUP, AgentTask.CMA_ANALYSIS, AgentTask.HBU_ANALYSIS, AgentTask.ML_PREDICTION],
            "cma_request": [AgentTask.CMA_ANALYSIS],
            "value_estimate": [AgentTask.CMA_ANALYSIS, AgentTask.ML_PREDICTION],
            "geographic_search": [AgentTask.ZONING_LOOKUP],
            "parcel_comparison": [AgentTask.ZONING_LOOKUP, AgentTask.CMA_ANALYSIS],
            "report_request": [AgentTask.ZONING_LOOKUP, AgentTask.CMA_ANALYSIS, AgentTask.HBU_ANALYSIS, AgentTask.ML_PREDICTION],
            "definition": [],  # Direct to reporter
            "greeting": [],  # Direct to reporter
        }
        
        state.pending_tasks = intent_to_tasks.get(state.detected_intent, [AgentTask.ZONING_LOOKUP])
        
        logger.info(
            "Coordinator completed",
            intent=state.detected_intent,
            tasks=len(state.pending_tasks),
        )
        
        return state
    
    def _route_from_coordinator(self, state: AgentState) -> str:
        """Route to parallel agents or directly to reporter."""
        if not state.pending_tasks:
            return "direct"
        return "parallel"
    
    async def _parallel_agents_node(self, state: AgentState) -> AgentState:
        """Execute multiple agents in parallel for efficiency."""
        logger.info("Executing agents in parallel", tasks=[t.value for t in state.pending_tasks])
        
        tasks = []
        
        if AgentTask.ZONING_LOOKUP in state.pending_tasks:
            tasks.append(self._run_zoning_agent(state))
        
        if AgentTask.CMA_ANALYSIS in state.pending_tasks:
            tasks.append(self._run_cma_agent(state))
        
        if AgentTask.HBU_ANALYSIS in state.pending_tasks:
            tasks.append(self._run_hbu_agent(state))
        
        if AgentTask.ML_PREDICTION in state.pending_tasks:
            tasks.append(self._run_ml_agent(state))
        
        # Run all agents concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results (they update state in place)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Agent failed", error=str(result))
        
        return state
    
    async def _run_zoning_agent(self, state: AgentState) -> None:
        """Run zoning agent and update state."""
        try:
            result = await self.zoning_agent.execute(
                parcel_id=state.selected_parcel,
                query=state.user_query,
                entities=state.extracted_entities,
            )
            state.zoning_result = result
        except Exception as e:
            logger.error("Zoning agent failed", error=str(e))
            state.zoning_result = {"error": str(e)}
    
    async def _run_cma_agent(self, state: AgentState) -> None:
        """Run CMA agent and update state."""
        try:
            result = await self.cma_agent.execute(
                parcel_id=state.selected_parcel,
                query=state.user_query,
                zoning_data=state.zoning_result,
            )
            state.cma_result = result
        except Exception as e:
            logger.error("CMA agent failed", error=str(e))
            state.cma_result = {"error": str(e)}
    
    async def _run_hbu_agent(self, state: AgentState) -> None:
        """Run HBU agent and update state."""
        try:
            result = await self.hbu_agent.execute(
                parcel_id=state.selected_parcel,
                zoning_data=state.zoning_result,
                cma_data=state.cma_result,
            )
            state.hbu_result = result
        except Exception as e:
            logger.error("HBU agent failed", error=str(e))
            state.hbu_result = {"error": str(e)}
    
    async def _run_ml_agent(self, state: AgentState) -> None:
        """Run ML agent and update state."""
        try:
            result = await self.ml_agent.execute(
                parcel_id=state.selected_parcel,
                features=state.extracted_entities,
            )
            state.ml_result = result
        except Exception as e:
            logger.error("ML agent failed", error=str(e))
            state.ml_result = {"error": str(e)}
    
    async def _reporter_node(self, state: AgentState) -> AgentState:
        """
        Reporter agent: Synthesizes all results into a natural language response.
        Also generates map actions and follow-up suggestions.
        """
        logger.info("Reporter synthesizing response")
        
        result = await self.reporter_agent.execute(
            query=state.user_query,
            intent=state.detected_intent,
            zoning_data=state.zoning_result,
            cma_data=state.cma_result,
            hbu_data=state.hbu_result,
            ml_data=state.ml_result,
            map_context=state.map_context,
        )
        
        state.response = result.get("response", "I couldn't process your request.")
        state.map_actions = result.get("map_actions", [])
        state.suggestions = result.get("suggestions", [])
        state.sources = result.get("sources", [])
        state.confidence = result.get("confidence", 0.5)
        
        return state
    
    async def process_query(
        self,
        query: str,
        session_id: str,
        map_context: Optional[dict] = None,
        selected_parcel: Optional[str] = None,
        conversation_history: Optional[list] = None,
    ) -> ChatResponse:
        """
        Main entry point for processing user queries.
        
        Args:
            query: User's natural language query
            session_id: Unique session identifier
            map_context: Current map state (bounds, zoom, layers)
            selected_parcel: ID of selected parcel (if any)
            conversation_history: Previous messages for context
        
        Returns:
            ChatResponse with content, map actions, and suggestions
        """
        logger.info(
            "Processing query",
            session_id=session_id,
            query=query[:100],
            has_parcel=selected_parcel is not None,
        )
        
        # Create initial state
        initial_state = AgentState(
            user_query=query,
            session_id=session_id,
            map_context=map_context or {},
            selected_parcel=selected_parcel,
            conversation_history=conversation_history or [],
        )
        
        # Run workflow
        try:
            final_state = await self.workflow.ainvoke(initial_state)
        except Exception as e:
            logger.error("Workflow failed", error=str(e))
            return ChatResponse(
                id=session_id,
                content="I encountered an error processing your request. Please try again.",
                confidence=0.0,
            )
        
        # Build response
        import uuid
        response = ChatResponse(
            id=str(uuid.uuid4()),
            content=final_state.response or "I couldn't generate a response.",
            intent=final_state.detected_intent,
            confidence=final_state.confidence,
            entities=final_state.extracted_entities,
            map_actions=[
                MapAction(**action) for action in final_state.map_actions
            ],
            suggestions=final_state.suggestions,
            sources=final_state.sources,
        )
        
        logger.info(
            "Query processed",
            intent=response.intent,
            confidence=response.confidence,
            map_actions=len(response.map_actions),
            suggestions=len(response.suggestions),
        )
        
        return response


# Singleton instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create the agent orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
