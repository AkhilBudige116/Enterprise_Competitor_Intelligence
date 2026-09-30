"""High-level execution service for competitor intelligence workflows."""
from typing import Dict, Any, List, Optional, Callable
from graph.graph import create_compiled_graph
from graph.state import CompetitorIntelligenceState
from utils.logger import get_logger

logger = get_logger("ResearchService")

class ResearchService:
    """Service to coordinate graph execution, progress streaming, and artifact management."""
    
    def __init__(self):
        self.graph = create_compiled_graph()

    def run_research(
        self,
        user_query: str,
        companies: Optional[List[str]] = None,
        focus_areas: Optional[List[str]] = None,
        date_range: Optional[str] = "Last 12 Months",
        max_retries: int = 2,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> CompetitorIntelligenceState:
        logger.info(f"Starting competitor intelligence run for query: '{user_query}'")
        
        initial_state: CompetitorIntelligenceState = {
            "user_query": user_query,
            "companies": companies or [],
            "research_scope": {
                "companies": companies or [],
                "focus_areas": focus_areas or [
                    "Financial Performance",
                    "AI Strategy & Architecture",
                    "Recent Developments & M&A",
                    "Competitive Advantages & Moats",
                    "Risks & Regulatory Challenges"
                ],
                "date_range": date_range
            },
            "research_plan": [],
            "web_results": [],
            "financial_results": [],
            "news_results": [],
            "normalized_evidence": [],
            "competitor_analysis": {},
            "draft_report": {},
            "claims": [],
            "verification_results": [],
            "evaluation_scores": {},
            "hallucination_score": 0.0,
            "support_rate": 1.0,
            "quality_status": "PASS",
            "retry_count": 0,
            "max_retries": max_retries,
            "failed_claim_ids": [],
            "targeted_queries": [],
            "final_report": {},
            "pdf_path": "",
            "errors": [],
            "current_step": "Initiating Workflow"
        }

        # Step mapping for progress estimation
        step_progress = {
            "input_validator": (10, "Validating parameters & scoping cohort..."),
            "planner": (20, "Planning Agent decomposing tasks..."),
            "parallel_research": (40, "Parallel agents retrieving Web, Financial & News data..."),
            "evidence_normalizer": (55, "Normalizing, weighting & deduplicating evidence..."),
            "competitor_analyst": (68, "Competitor Analysis Agent generating comparison matrix & SWOT..."),
            "synthesizer": (78, "Synthesis Agent authoring 13-section report..."),
            "claim_extractor": (84, "Extracting atomic factual claims for audit..."),
            "verifier": (90, "Fact Verification Agent testing claims against evidence..."),
            "evaluator": (94, "Computing Ragas metrics & Hallucination Score..."),
            "targeted_research": (82, "Quality Gate triggered targeted self-correction..."),
            "pdf_generator": (100, "Compiling ReportLab Executive PDF...")
        }

        final_state = initial_state
        for event in self.graph.stream(initial_state):
            for node_name, node_output in event.items():
                logger.info(f"Completed Graph Node: {node_name}")
                if isinstance(node_output, dict):
                    final_state = {**final_state, **node_output}
                
                if progress_callback and node_name in step_progress:
                    pct, msg = step_progress[node_name]
                    progress_callback(msg, pct)

        return final_state

def run_competitor_research(
    query: str,
    companies: Optional[List[str]] = None,
    focus_areas: Optional[List[str]] = None
) -> CompetitorIntelligenceState:
    """Convenience helper to run research synchronously."""
    service = ResearchService()
    return service.run_research(
        user_query=query,
        companies=companies,
        focus_areas=focus_areas
    )
