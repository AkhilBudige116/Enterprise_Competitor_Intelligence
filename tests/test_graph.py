"""Integration tests for compiled LangGraph execution."""
import os
import pytest
from graph.graph import create_compiled_graph
from graph.state import CompetitorIntelligenceState
from services.research_service import ResearchService

def test_full_graph_execution():
    """Test end-to-end execution of the LangGraph multi-agent pipeline."""
    service = ResearchService()
    state = service.run_research(
        user_query="Compare NVIDIA and AMD in datacenter AI processors",
        companies=["NVIDIA", "AMD"],
        focus_areas=["Financial Performance", "AI Strategy", "Recent Developments"],
        max_retries=1
    )
    
    # Assert all shared state fields are populated properly
    assert state.get("companies") == ["NVIDIA", "AMD"]
    assert len(state.get("research_plan", [])) > 0
    assert len(state.get("normalized_evidence", [])) > 0
    assert "company_profiles" in state.get("competitor_analysis", {})
    assert "sections" in state.get("draft_report", {})
    assert len(state.get("draft_report", {}).get("sections", [])) == 13
    assert len(state.get("claims", [])) > 0
    assert len(state.get("verification_results", [])) > 0
    assert "hallucination_score" in state
    assert state.get("quality_status") in ["PASS", "FAIL"]
    
    # PDF should be generated
    pdf_path = state.get("pdf_path", "")
    assert pdf_path != ""
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # Non-empty valid PDF
