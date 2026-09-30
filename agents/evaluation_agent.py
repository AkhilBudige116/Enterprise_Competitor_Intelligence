"""Evaluation Agent: Runs Ragas / DeepEval quality metrics and hallucination scoring."""
from typing import Dict, Any, List
from evaluation.hallucination_score import calculate_hallucination_metrics
from evaluation.ragas_evaluator import evaluate_ragas_metrics
from evaluation.deepeval_evaluator import evaluate_deepeval_metrics
from config.thresholds import QualityThresholds
from utils.logger import get_logger

logger = get_logger("EvaluationAgent")

class EvaluationAgent:
    """Evaluates report quality, calculates hallucination metrics, and determines quality gate verdict."""
    
    def __init__(self, thresholds: QualityThresholds = None):
        self.thresholds = thresholds or QualityThresholds()

    def evaluate(
        self,
        user_query: str,
        draft_report: Dict[str, Any],
        verification_results: List[Dict[str, Any]],
        normalized_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        logger.info("EvaluationAgent evaluating synthesized report...")
        
        # 1. Calculate custom Hallucination & Support Rate metrics
        hallucination_metrics = calculate_hallucination_metrics(
            verification_results=verification_results,
            thresholds=self.thresholds
        )
        
        # 2. Extract full text representation
        sections = draft_report.get("sections", [])
        draft_text = " ".join([s.get("content", "") for s in sections])
        
        # 3. Calculate Ragas metrics
        ragas_scores = evaluate_ragas_metrics(
            user_query=user_query,
            draft_report_text=draft_text,
            evidence_records=normalized_evidence
        )
        
        # 4. Calculate DeepEval metrics
        deepeval_scores = evaluate_deepeval_metrics(
            draft_report_text=draft_text,
            evidence_records=normalized_evidence
        )
        
        # Identify failed claim IDs for targeted re-research
        failed_ids = [
            v.get("claim_id") for v in verification_results
            if v.get("status") in ["Unsupported", "Contradicted", "Insufficient Evidence"]
        ]

        combined_scores = {
            **ragas_scores,
            **deepeval_scores,
            "support_rate": hallucination_metrics["support_rate"],
            "unsupported_rate": hallucination_metrics["unsupported_rate"],
            "hallucination_score": hallucination_metrics["hallucination_score"],
            "total_claims": hallucination_metrics["total_claims"],
            "supported_count": hallucination_metrics["supported_count"],
            "unsupported_count": hallucination_metrics["unsupported_count"],
            "quality_status": hallucination_metrics["quality_status"],
            "passed_gate": hallucination_metrics["passed_gate"],
            "reasons": hallucination_metrics["reasons"]
        }

        return {
            "evaluation_scores": combined_scores,
            "hallucination_score": hallucination_metrics["hallucination_score"],
            "support_rate": hallucination_metrics["support_rate"],
            "quality_status": hallucination_metrics["quality_status"],
            "failed_claim_ids": failed_ids
        }
