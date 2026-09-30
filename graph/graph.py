"""LangGraph workflow assembly with parallel research and quality self-correction loop."""
from langgraph.graph import StateGraph, START, END
from graph.state import CompetitorIntelligenceState
from graph.nodes import (
    input_validator_node,
    planner_node,
    parallel_research_node,
    evidence_normalizer_node,
    competitor_analyst_node,
    synthesizer_node,
    claim_extractor_node,
    verifier_node,
    evaluator_node,
    targeted_research_node,
    pdf_generator_node
)
from graph.routers import quality_gate_router

def build_competitor_intelligence_graph() -> StateGraph:
    """Constructs the complete StateGraph for the multi-agent competitor intelligence system."""
    workflow = StateGraph(CompetitorIntelligenceState)
    
    # 1. Register all nodes
    workflow.add_node("input_validator", input_validator_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("parallel_research", parallel_research_node)
    workflow.add_node("evidence_normalizer", evidence_normalizer_node)
    workflow.add_node("competitor_analyst", competitor_analyst_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("claim_extractor", claim_extractor_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("targeted_research", targeted_research_node)
    workflow.add_node("pdf_generator", pdf_generator_node)
    
    # 2. Add sequential and parallel routing edges
    workflow.add_edge(START, "input_validator")
    workflow.add_edge("input_validator", "planner")
    workflow.add_edge("planner", "parallel_research")
    workflow.add_edge("parallel_research", "evidence_normalizer")
    workflow.add_edge("evidence_normalizer", "competitor_analyst")
    workflow.add_edge("competitor_analyst", "synthesizer")
    workflow.add_edge("synthesizer", "claim_extractor")
    workflow.add_edge("claim_extractor", "verifier")
    workflow.add_edge("verifier", "evaluator")
    
    # 3. Conditional Quality Gate Edge
    workflow.add_conditional_edges(
        "evaluator",
        quality_gate_router,
        {
            "pdf_generator": "pdf_generator",
            "targeted_research": "targeted_research"
        }
    )
    
    # 4. Self-Correction Loop: Route back from targeted research to synthesizer
    workflow.add_edge("targeted_research", "synthesizer")
    
    # 5. Output termination
    workflow.add_edge("pdf_generator", END)
    
    return workflow

def create_compiled_graph():
    """Compile and return runnable LangGraph instance."""
    builder = build_competitor_intelligence_graph()
    return builder.compile()
