"""Shared LangGraph state contract."""
from typing import TypedDict, List, Dict, Any, Optional
import operator
from typing_extensions import Annotated

class CompetitorIntelligenceState(TypedDict, total=False):
    """LangGraph shared state carrying evidence, analysis, and verification results across nodes."""
    user_query: str
    companies: List[str]
    research_scope: Dict[str, Any]
    research_plan: List[Dict[str, Any]]
    
    # Raw research outputs from parallel agents
    web_results: List[Dict[str, Any]]
    financial_results: List[Dict[str, Any]]
    news_results: List[Dict[str, Any]]
    
    # Normalized evidence
    normalized_evidence: List[Dict[str, Any]]
    
    # Strategic analysis & report
    competitor_analysis: Dict[str, Any]
    draft_report: Dict[str, Any]
    
    # Verification & Quality Gate
    claims: List[Dict[str, Any]]
    verification_results: List[Dict[str, Any]]
    evaluation_scores: Dict[str, Any]
    hallucination_score: float
    support_rate: float
    quality_status: str  # PASS | FAIL
    
    # Self-correction state
    retry_count: int
    max_retries: int
    failed_claim_ids: List[str]
    targeted_queries: List[Dict[str, Any]]
    
    # Final outputs
    final_report: Dict[str, Any]
    pdf_path: str
    errors: List[str]
    current_step: str
