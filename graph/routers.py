"""Routing logic for quality gates and self-correction loop."""
from typing import Literal
from graph.state import CompetitorIntelligenceState
from utils.logger import get_logger

logger = get_logger("QualityRouter")

def quality_gate_router(state: CompetitorIntelligenceState) -> Literal["pdf_generator", "targeted_research"]:
    """Conditional router that decides whether to pass to PDF generation or route back to targeted research."""
    quality_status = state.get("quality_status", "PASS")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)
    failed_claims = state.get("failed_claim_ids", [])
    
    logger.info(
        f"Quality Gate Evaluation: Status='{quality_status}', Retry={retry_count}/{max_retries}, "
        f"Failed Claims Count={len(failed_claims)}"
    )

    # If passed, or if retry budget has been exhausted
    if quality_status == "PASS":
        logger.info("Quality Gate PASSED. Proceeding to Executive PDF generation.")
        return "pdf_generator"
        
    if retry_count >= max_retries:
        logger.warning(
            f"Quality Gate FAILED but max retries ({max_retries}) reached. "
            "Proceeding to PDF generation with explicit limitations."
        )
        return "pdf_generator"

    # Otherwise, trigger self-correction loop
    logger.info(f"Quality Gate FAILED. Routing to Targeted Re-Research (Attempt {retry_count + 1} of {max_retries}).")
    return "targeted_research"
