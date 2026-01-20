"""
ZoneWise Appraisal Orchestrator
LangGraph-based orchestration of the Three Approaches to Value

Pipeline:
1. Property Data (BCPAO) → 
2. Sales Comparison Approach →
3. Cost Approach →
4. Income Approach →
5. Reconciliation →
6. Final Report

© 2026 ZoneWise - Ariel Shapira
"""

import asyncio
import logging
from typing import Dict, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None

from ..data_sources.bcpao_client import BCPAOClient, BCPAOProperty
from ..data_sources.supabase_client import SupabaseClient
from .sales_comparison_agent import SalesComparisonAgent, SalesComparisonResult
from .cost_approach_agent import CostApproachAgent, CostApproachResult
from .income_approach_agent import IncomeApproachAgent, IncomeApproachResult

logger = logging.getLogger(__name__)


class AppraisalStage(str, Enum):
    """Stages in the appraisal pipeline."""
    INIT = "init"
    PROPERTY_DATA = "property_data"
    SALES_COMPARISON = "sales_comparison"
    COST_APPROACH = "cost_approach"
    INCOME_APPROACH = "income_approach"
    RECONCILIATION = "reconciliation"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class AppraisalState:
    """State passed through the appraisal pipeline."""
    # Input
    parcel_id: str
    address: Optional[str] = None
    analysis_id: Optional[str] = None
    
    # Stage tracking
    current_stage: AppraisalStage = AppraisalStage.INIT
    stages_completed: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    
    # Property data
    subject_property: Optional[Dict] = None
    
    # Agent results
    sales_comparison_result: Optional[Dict] = None
    cost_approach_result: Optional[Dict] = None
    income_approach_result: Optional[Dict] = None
    
    # Final output
    reconciliation: Optional[Dict] = None
    final_value: Optional[float] = None
    recommendation: Optional[str] = None
    confidence: Optional[str] = None
    
    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class AppraisalResult:
    """Final appraisal result."""
    parcel_id: str
    address: str
    analysis_id: str
    
    # Three Approaches
    sales_comparison_value: float
    cost_approach_value: float
    income_approach_value: float
    
    # Reconciliation
    reconciled_value: float
    value_range_low: float
    value_range_high: float
    
    # Weights used
    sales_weight: float
    cost_weight: float
    income_weight: float
    most_applicable: str
    
    # Final
    final_value_opinion: float
    recommendation: str  # BID, REVIEW, SKIP
    max_bid: Optional[float] = None
    confidence: str = "MEDIUM"
    
    # Metadata
    stages_completed: list = field(default_factory=list)
    processing_time_seconds: float = 0
    report_narrative: str = ""
    created_at: str = ""


class AppraisalOrchestrator:
    """
    Main orchestrator for property appraisal.
    
    Coordinates three approaches and reconciles to final value.
    
    Usage:
        orchestrator = AppraisalOrchestrator()
        result = await orchestrator.appraise("26-37-35-77-00042.0")
        
        # Or with address
        result = await orchestrator.appraise_by_address("200 Jason Ct, Satellite Beach, FL")
    """
    
    def __init__(self, use_langgraph: bool = True):
        self.bcpao = BCPAOClient()
        self.supabase = SupabaseClient()
        
        # Initialize agents
        self.sales_agent = SalesComparisonAgent()
        self.cost_agent = CostApproachAgent()
        self.income_agent = IncomeApproachAgent()
        
        # Reconciliation weights by property type
        self.weights = {
            "single_family_owner": {"sales": 60, "cost": 25, "income": 15},
            "single_family_rental": {"sales": 40, "cost": 20, "income": 40},
            "multi_family": {"sales": 30, "cost": 20, "income": 50},
            "new_construction": {"sales": 30, "cost": 50, "income": 20},
            "special_purpose": {"sales": 20, "cost": 60, "income": 20},
            "default": {"sales": 50, "cost": 25, "income": 25},
        }
        
        # Build LangGraph if available
        self.graph = self._build_graph() if use_langgraph and LANGGRAPH_AVAILABLE else None
    
    def _build_graph(self):
        """Build LangGraph state machine."""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        # Define state type for LangGraph
        class GraphState(TypedDict):
            parcel_id: str
            address: Optional[str]
            analysis_id: Optional[str]
            current_stage: str
            subject_property: Optional[Dict]
            sales_result: Optional[Dict]
            cost_result: Optional[Dict]
            income_result: Optional[Dict]
            final_result: Optional[Dict]
            errors: list
        
        # Create graph
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("get_property", self._node_get_property)
        workflow.add_node("sales_comparison", self._node_sales_comparison)
        workflow.add_node("cost_approach", self._node_cost_approach)
        workflow.add_node("income_approach", self._node_income_approach)
        workflow.add_node("reconcile", self._node_reconcile)
        
        # Add edges
        workflow.set_entry_point("get_property")
        workflow.add_edge("get_property", "sales_comparison")
        workflow.add_edge("sales_comparison", "cost_approach")
        workflow.add_edge("cost_approach", "income_approach")
        workflow.add_edge("income_approach", "reconcile")
        workflow.add_edge("reconcile", END)
        
        return workflow.compile()
    
    async def appraise(
        self,
        parcel_id: str,
        property_type: str = "single_family_owner",
        judgment_amount: float = None,
        store_results: bool = True
    ) -> AppraisalResult:
        """
        Perform complete property appraisal.
        
        Args:
            parcel_id: BCPAO parcel ID
            property_type: Type for weight selection
            judgment_amount: For foreclosure max bid calculation
            store_results: Whether to store in Supabase
            
        Returns:
            AppraisalResult with complete analysis
        """
        start_time = datetime.now()
        logger.info(f"Starting appraisal for {parcel_id}")
        
        state = AppraisalState(
            parcel_id=parcel_id,
            started_at=start_time.isoformat()
        )
        
        try:
            # 1. Get property data
            state = await self._stage_property_data(state)
            
            # 2. Create analysis record
            if store_results:
                state.analysis_id = await self.supabase.create_analysis(
                    parcel_id,
                    state.address or ""
                )
            
            # 3. Run three approaches (can be parallel)
            sales_task = self._stage_sales_comparison(state)
            cost_task = self._stage_cost_approach(state)
            income_task = self._stage_income_approach(state)
            
            # Execute in parallel
            sales_state, cost_state, income_state = await asyncio.gather(
                sales_task, cost_task, income_task,
                return_exceptions=True
            )
            
            # Handle results
            if not isinstance(sales_state, Exception):
                state.sales_comparison_result = sales_state.sales_comparison_result
                state.stages_completed.append("sales_comparison")
            
            if not isinstance(cost_state, Exception):
                state.cost_approach_result = cost_state.cost_approach_result
                state.stages_completed.append("cost_approach")
            
            if not isinstance(income_state, Exception):
                state.income_approach_result = income_state.income_approach_result
                state.stages_completed.append("income_approach")
            
            # 4. Reconcile
            state = await self._stage_reconciliation(state, property_type)
            
            # 5. Calculate max bid (for foreclosures)
            max_bid = None
            if judgment_amount and state.final_value:
                max_bid = self._calculate_max_bid(state.final_value, judgment_amount)
            
            # 6. Build result
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            result = AppraisalResult(
                parcel_id=parcel_id,
                address=state.address or "",
                analysis_id=state.analysis_id or "",
                
                sales_comparison_value=state.reconciliation.get("sales_value", 0),
                cost_approach_value=state.reconciliation.get("cost_value", 0),
                income_approach_value=state.reconciliation.get("income_value", 0),
                
                reconciled_value=state.final_value or 0,
                value_range_low=state.reconciliation.get("value_low", 0),
                value_range_high=state.reconciliation.get("value_high", 0),
                
                sales_weight=state.reconciliation.get("sales_weight", 50),
                cost_weight=state.reconciliation.get("cost_weight", 25),
                income_weight=state.reconciliation.get("income_weight", 25),
                most_applicable=state.reconciliation.get("most_applicable", "Sales Comparison"),
                
                final_value_opinion=state.final_value or 0,
                recommendation=state.recommendation or "REVIEW",
                max_bid=max_bid,
                confidence=state.confidence or "MEDIUM",
                
                stages_completed=state.stages_completed,
                processing_time_seconds=processing_time,
                report_narrative=state.reconciliation.get("narrative", ""),
                created_at=end_time.isoformat()
            )
            
            # 7. Store final reconciliation
            if store_results and state.analysis_id:
                await self._store_reconciliation(state.analysis_id, result)
            
            logger.info(f"Appraisal complete: ${result.final_value_opinion:,.0f} in {processing_time:.1f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Appraisal failed: {e}")
            state.errors.append(str(e))
            raise
    
    async def appraise_by_address(
        self,
        address: str,
        **kwargs
    ) -> AppraisalResult:
        """Appraise property by address."""
        subject = await self.bcpao.search_by_address(address)
        if not subject:
            raise ValueError(f"Could not find property: {address}")
        
        return await self.appraise(subject.parcel_id, **kwargs)
    
    # ==========================================
    # PIPELINE STAGES
    # ==========================================
    
    async def _stage_property_data(self, state: AppraisalState) -> AppraisalState:
        """Stage 1: Get property data."""
        logger.info(f"Stage 1: Getting property data for {state.parcel_id}")
        
        subject = await self.bcpao.get_property(state.parcel_id)
        
        if not subject:
            raise ValueError(f"Property not found: {state.parcel_id}")
        
        state.subject_property = asdict(subject)
        state.address = subject.address
        state.current_stage = AppraisalStage.PROPERTY_DATA
        state.stages_completed.append("property_data")
        
        return state
    
    async def _stage_sales_comparison(self, state: AppraisalState) -> AppraisalState:
        """Stage 2: Sales Comparison Approach."""
        logger.info("Stage 2: Sales Comparison Approach")
        
        try:
            result = await self.sales_agent.analyze(
                state.parcel_id,
                state.analysis_id,
                store_results=bool(state.analysis_id)
            )
            state.sales_comparison_result = asdict(result)
            state.current_stage = AppraisalStage.SALES_COMPARISON
            
        except Exception as e:
            logger.error(f"Sales comparison failed: {e}")
            state.errors.append(f"Sales comparison: {e}")
        
        return state
    
    async def _stage_cost_approach(self, state: AppraisalState) -> AppraisalState:
        """Stage 3: Cost Approach."""
        logger.info("Stage 3: Cost Approach")
        
        try:
            subject = BCPAOProperty(**state.subject_property)
            result = await self.cost_agent.analyze(
                subject,
                state.analysis_id,
                store_results=bool(state.analysis_id)
            )
            state.cost_approach_result = asdict(result)
            state.current_stage = AppraisalStage.COST_APPROACH
            
        except Exception as e:
            logger.error(f"Cost approach failed: {e}")
            state.errors.append(f"Cost approach: {e}")
        
        return state
    
    async def _stage_income_approach(self, state: AppraisalState) -> AppraisalState:
        """Stage 4: Income Approach."""
        logger.info("Stage 4: Income Approach")
        
        try:
            subject = BCPAOProperty(**state.subject_property)
            result = await self.income_agent.analyze(
                subject,
                state.analysis_id,
                store_results=bool(state.analysis_id)
            )
            state.income_approach_result = asdict(result)
            state.current_stage = AppraisalStage.INCOME_APPROACH
            
        except Exception as e:
            logger.error(f"Income approach failed: {e}")
            state.errors.append(f"Income approach: {e}")
        
        return state
    
    async def _stage_reconciliation(
        self,
        state: AppraisalState,
        property_type: str
    ) -> AppraisalState:
        """Stage 5: Reconcile three approaches."""
        logger.info("Stage 5: Reconciliation")
        
        # Get values
        sales_value = 0
        cost_value = 0
        income_value = 0
        
        if state.sales_comparison_result:
            sales_value = state.sales_comparison_result.get("indicated_value", 0)
        
        if state.cost_approach_result:
            cost_value = state.cost_approach_result.get("indicated_value", 0)
        
        if state.income_approach_result:
            income_value = state.income_approach_result.get("indicated_value", 0)
        
        # Get weights
        weights = self.weights.get(property_type, self.weights["default"])
        
        # Weighted average (only use approaches that succeeded)
        total_weight = 0
        weighted_sum = 0
        
        if sales_value > 0:
            weighted_sum += sales_value * weights["sales"]
            total_weight += weights["sales"]
        
        if cost_value > 0:
            weighted_sum += cost_value * weights["cost"]
            total_weight += weights["cost"]
        
        if income_value > 0:
            weighted_sum += income_value * weights["income"]
            total_weight += weights["income"]
        
        reconciled_value = weighted_sum / total_weight if total_weight > 0 else 0
        reconciled_value = round(reconciled_value / 1000) * 1000
        
        # Determine most applicable
        values = {"Sales Comparison": sales_value, "Cost": cost_value, "Income": income_value}
        most_applicable = max(values, key=lambda k: weights.get(k.lower().split()[0], 0))
        
        # Value range
        valid_values = [v for v in [sales_value, cost_value, income_value] if v > 0]
        value_low = min(valid_values) if valid_values else reconciled_value * 0.90
        value_high = max(valid_values) if valid_values else reconciled_value * 1.10
        
        # Confidence
        completed = len([v for v in [sales_value, cost_value, income_value] if v > 0])
        spread = (value_high - value_low) / reconciled_value if reconciled_value > 0 else 1
        
        if completed >= 3 and spread < 0.15:
            confidence = "HIGH"
        elif completed >= 2 and spread < 0.25:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        # Recommendation
        recommendation = "REVIEW"  # Default
        
        # Generate narrative
        narrative = self._generate_reconciliation_narrative(
            state.address or state.parcel_id,
            sales_value, cost_value, income_value,
            weights, reconciled_value, most_applicable, confidence
        )
        
        state.reconciliation = {
            "sales_value": sales_value,
            "cost_value": cost_value,
            "income_value": income_value,
            "sales_weight": weights["sales"],
            "cost_weight": weights["cost"],
            "income_weight": weights["income"],
            "value_low": value_low,
            "value_high": value_high,
            "reconciled_value": reconciled_value,
            "most_applicable": most_applicable,
            "narrative": narrative
        }
        
        state.final_value = reconciled_value
        state.confidence = confidence
        state.recommendation = recommendation
        state.current_stage = AppraisalStage.RECONCILIATION
        state.stages_completed.append("reconciliation")
        
        return state
    
    def _calculate_max_bid(self, arv: float, judgment: float) -> float:
        """Calculate max bid for foreclosure using BidDeed formula."""
        # (ARV × 70%) - Repairs - $10K - MIN($25K, 15% ARV)
        repairs = 25000  # Default estimate
        cushion = min(25000, arv * 0.15)
        
        max_bid = (arv * 0.70) - repairs - 10000 - cushion
        
        return round(max(0, max_bid), 0)
    
    def _generate_reconciliation_narrative(
        self,
        address: str,
        sales_value: float,
        cost_value: float,
        income_value: float,
        weights: Dict,
        final_value: float,
        most_applicable: str,
        confidence: str
    ) -> str:
        """Generate reconciliation narrative."""
        
        narrative = f"""
FINAL VALUE RECONCILIATION
Property: {address}
Date: {datetime.now().strftime('%B %d, %Y')}

INDICATED VALUES BY APPROACH:

1. Sales Comparison Approach: ${sales_value:,.0f}
   Weight Applied: {weights['sales']}%
   
2. Cost Approach: ${cost_value:,.0f}
   Weight Applied: {weights['cost']}%
   
3. Income Approach: ${income_value:,.0f}
   Weight Applied: {weights['income']}%

RECONCILIATION:

The {most_applicable} Approach was given the most weight in this analysis
due to the availability of reliable market data and the nature of the property.

The three approaches indicate a value range of ${min(v for v in [sales_value, cost_value, income_value] if v > 0):,.0f} 
to ${max(sales_value, cost_value, income_value):,.0f}.

FINAL VALUE OPINION: ${final_value:,.0f}

Confidence Level: {confidence}

This value opinion is based on market conditions as of the effective date
and assumes a reasonable exposure time on the open market.
"""
        return narrative.strip()
    
    async def _store_reconciliation(self, analysis_id: str, result: AppraisalResult):
        """Store reconciliation in Supabase."""
        try:
            recon_data = {
                "sales_comparison_value": result.sales_comparison_value,
                "sales_comparison_weight": result.sales_weight,
                "cost_approach_value": result.cost_approach_value,
                "cost_approach_weight": result.cost_weight,
                "income_approach_value": result.income_approach_value,
                "income_approach_weight": result.income_weight,
                "value_low": result.value_range_low,
                "value_high": result.value_range_high,
                "final_value": result.final_value_opinion,
                "most_applicable_approach": result.most_applicable,
                "narrative": result.report_narrative
            }
            
            await self.supabase.store_reconciliation(analysis_id, recon_data)
            
            # Update analysis record
            await self.supabase.update_analysis(
                analysis_id,
                zonewise_score=result.confidence == "HIGH" and 85 or (result.confidence == "MEDIUM" and 70 or 55),
                recommendation=result.recommendation,
                max_bid=result.max_bid,
                confidence=result.confidence == "HIGH" and 90 or (result.confidence == "MEDIUM" and 75 or 60)
            )
            
        except Exception as e:
            logger.error(f"Error storing reconciliation: {e}")
    
    # ==========================================
    # LANGGRAPH NODES (if available)
    # ==========================================
    
    async def _node_get_property(self, state: Dict) -> Dict:
        """LangGraph node for property data."""
        subject = await self.bcpao.get_property(state["parcel_id"])
        return {**state, "subject_property": asdict(subject) if subject else None}
    
    async def _node_sales_comparison(self, state: Dict) -> Dict:
        """LangGraph node for sales comparison."""
        try:
            result = await self.sales_agent.analyze(state["parcel_id"], state.get("analysis_id"))
            return {**state, "sales_result": asdict(result)}
        except Exception as e:
            return {**state, "errors": state.get("errors", []) + [str(e)]}
    
    async def _node_cost_approach(self, state: Dict) -> Dict:
        """LangGraph node for cost approach."""
        try:
            subject = BCPAOProperty(**state["subject_property"])
            result = await self.cost_agent.analyze(subject, state.get("analysis_id"))
            return {**state, "cost_result": asdict(result)}
        except Exception as e:
            return {**state, "errors": state.get("errors", []) + [str(e)]}
    
    async def _node_income_approach(self, state: Dict) -> Dict:
        """LangGraph node for income approach."""
        try:
            subject = BCPAOProperty(**state["subject_property"])
            result = await self.income_agent.analyze(subject, state.get("analysis_id"))
            return {**state, "income_result": asdict(result)}
        except Exception as e:
            return {**state, "errors": state.get("errors", []) + [str(e)]}
    
    async def _node_reconcile(self, state: Dict) -> Dict:
        """LangGraph node for reconciliation."""
        # Implementation would mirror _stage_reconciliation
        return state
    
    async def close(self):
        """Close all connections."""
        await self.bcpao.close()
        await self.supabase.close()
        await self.sales_agent.close()
        await self.cost_agent.close()
        await self.income_agent.close()
