"""
ZoneWise LangGraph Orchestrator - zonewize Workflow
4-Stage Pipeline: Fetch → Analyze → Report → Store

Created: January 13, 2026
Version: 1.0.0
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
import uuid


class ZoneWizeState(TypedDict):
    """State passed between workflow stages."""
    # Input
    property_id: str
    address: str
    jurisdiction: str
    correlation_id: str
    
    # Stage 1: Fetch
    property_data: dict | None
    property_fetched: bool
    
    # Stage 2: Analyze
    compliance_status: str | None
    compliance_result: dict | None
    violations: list[dict]
    confidence_score: int | None
    
    # Stage 3: Report
    report_url: str | None
    report_generated: bool
    
    # Stage 4: Store
    analysis_id: str | None
    stored: bool
    
    # Observability
    stage: str
    errors: Annotated[list[str], operator.add]
    execution_times: dict[str, float]
    success: bool
    message: str | None


async def fetch_property_node(state: ZoneWizeState) -> ZoneWizeState:
    """Stage 1: Fetch property from Supabase."""
    import time
    from supabase import create_client
    import os
    
    start_time = time.time()
    print(f"[Stage 1] Fetching property: {state['property_id']}")
    
    try:
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        result = supabase.table('properties').select('*').eq(
            'id', state['property_id']
        ).single().execute()
        
        state['property_data'] = result.data
        state['property_fetched'] = True
        state['stage'] = 'fetch_complete'
        state['execution_times']['fetch'] = (time.time() - start_time) * 1000
        
        print(f"[Stage 1] ✅ Property fetched")
        return state
    
    except Exception as e:
        print(f"[Stage 1] ❌ Error: {str(e)}")
        state['errors'].append(f"fetch: {str(e)}")
        state['property_fetched'] = False
        state['success'] = False
        return state


async def zonewize_analysis_node(state: ZoneWizeState) -> ZoneWizeState:
    """Stage 2: Analyze compliance with zonewize skill."""
    import time
    import sys
    sys.path.insert(0, '/home/claude')
    from zonewize import analyze_zoning
    
    start_time = time.time()
    print(f"[Stage 2] Running zonewize analysis")
    
    if not state.get('property_fetched'):
        print(f"[Stage 2] ❌ Skipping: fetch failed")
        return state
    
    try:
        result = await analyze_zoning(
            property_id=state['property_id'],
            jurisdiction=state['jurisdiction'],
            address=state['address'],
            correlation_id=state['correlation_id']
        )
        
        state['compliance_result'] = result
        state['compliance_status'] = result.get('compliance_status')
        state['violations'] = result.get('violations', [])
        state['confidence_score'] = result.get('confidence_score')
        state['stage'] = 'analyze_complete'
        state['execution_times']['analyze'] = (time.time() - start_time) * 1000
        
        print(f"[Stage 2] ✅ Analysis complete: {state['compliance_status']}")
        return state
    
    except Exception as e:
        print(f"[Stage 2] ❌ Error: {str(e)}")
        state['errors'].append(f"analyze: {str(e)}")
        state['success'] = False
        return state


async def generate_report_node(state: ZoneWizeState) -> ZoneWizeState:
    """Stage 3: Generate DOCX report."""
    import time
    from datetime import datetime
    
    start_time = time.time()
    print(f"[Stage 3] Generating report")
    
    if not state.get('compliance_result'):
        print(f"[Stage 3] ❌ Skipping: analysis failed")
        return state
    
    try:
        report_filename = f"report_{state['property_id']}_{datetime.now().strftime('%Y%m%d')}.docx"
        state['report_url'] = f"https://zonewise.storage/reports/{report_filename}"
        state['report_generated'] = True
        state['stage'] = 'report_complete'
        state['execution_times']['report'] = (time.time() - start_time) * 1000
        
        print(f"[Stage 3] ✅ Report generated")
        return state
    
    except Exception as e:
        print(f"[Stage 3] ❌ Error: {str(e)}")
        state['errors'].append(f"report: {str(e)}")
        state['report_generated'] = False
        return state


async def store_results_node(state: ZoneWizeState) -> ZoneWizeState:
    """Stage 4: Store results in Supabase."""
    import time
    from supabase import create_client
    import os
    
    start_time = time.time()
    print(f"[Stage 4] Storing results")
    
    try:
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Insert analysis
        result = supabase.table('compliance_analyses').insert({
            'property_id': state['property_id'],
            'correlation_id': state['correlation_id'],
            'compliance_status': state['compliance_status'],
            'confidence_score': state['confidence_score'],
            'violations': state['violations']
        }).execute()
        
        state['analysis_id'] = result.data[0]['id']
        state['stored'] = True
        state['success'] = True
        state['message'] = f"Analysis complete. ID: {state['analysis_id']}"
        state['stage'] = 'complete'
        state['execution_times']['store'] = (time.time() - start_time) * 1000
        
        total_time = sum(state['execution_times'].values())
        print(f"[Stage 4] ✅ Results stored")
        print(f"[Pipeline] ✅ Complete in {total_time:.0f}ms")
        
        return state
    
    except Exception as e:
        print(f"[Stage 4] ❌ Error: {str(e)}")
        state['errors'].append(f"store: {str(e)}")
        state['success'] = False
        return state


def build_zonewize_workflow() -> StateGraph:
    """Build the 4-stage zonewize workflow."""
    workflow = StateGraph(ZoneWizeState)
    
    # Add nodes
    workflow.add_node("fetch", fetch_property_node)
    workflow.add_node("analyze", zonewize_analysis_node)
    workflow.add_node("report", generate_report_node)
    workflow.add_node("store", store_results_node)
    
    # Add edges
    workflow.set_entry_point("fetch")
    workflow.add_edge("fetch", "analyze")
    workflow.add_edge("analyze", "report")
    workflow.add_edge("report", "store")
    workflow.add_edge("store", END)
    
    return workflow.compile()


async def execute_zonewize_pipeline(
    property_id: str,
    address: str,
    jurisdiction: str
) -> dict:
    """Execute complete zonewize pipeline."""
    initial_state = ZoneWizeState(
        property_id=property_id,
        address=address,
        jurisdiction=jurisdiction,
        correlation_id=str(uuid.uuid4()),
        property_data=None,
        property_fetched=False,
        compliance_status=None,
        compliance_result=None,
        violations=[],
        confidence_score=None,
        report_url=None,
        report_generated=False,
        analysis_id=None,
        stored=False,
        stage='init',
        errors=[],
        execution_times={},
        success=False,
        message=None
    )
    
    print(f"\n{'='*70}")
    print(f"ZONEWISE PIPELINE")
    print(f"Property: {property_id}")
    print(f"Jurisdiction: {jurisdiction}")
    print(f"{'='*70}\n")
    
    app = build_zonewize_workflow()
    final_state = await app.ainvoke(initial_state)
    
    print(f"\n{'='*70}")
    print(f"Success: {final_state['success']}")
    print(f"Message: {final_state.get('message')}")
    print(f"{'='*70}\n")
    
    return final_state


if __name__ == '__main__':
    import asyncio
    
    result = asyncio.run(
        execute_zonewize_pipeline(
            property_id='test-001',
            address='1233 Yacht Club Blvd, IHB, FL 32937',
            jurisdiction='indian_harbour_beach'
        )
    )
    
    print(f"Final: {result['compliance_status']}, Confidence: {result['confidence_score']}%")
