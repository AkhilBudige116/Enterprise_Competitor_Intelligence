"""Custom Hallucination Scoring and Support Rate calculator matching PRD specifications."""
from typing import List, Dict, Any
from schemas.claims import ClaimStatus
from config.thresholds import QualityThresholds
from utils.logger import get_logger

logger = get_logger("HallucinationScore")

def calculate_hallucination_metrics(
    verification_results: List[Dict[str, Any]],
    thresholds: QualityThresholds = QualityThresholds()
) -> Dict[str, Any]:
    """Calculate transparent hallucination score and claim statistics per PRD requirements.
    
    Formulas:
      Support Rate = Supported Claims / Total Checkable Claims
      Unsupported Rate = Unsupported Claims / Total Checkable Claims
      Hallucination Score (%) = Unsupported Claims / Total Checkable Claims * 100
    """
    total = len(verification_results)
    if total == 0:
        return {
            "total_claims": 0,
            "supported_count": 0,
            "partially_supported_count": 0,
            "unsupported_count": 0,
            "contradicted_count": 0,
            "insufficient_evidence_count": 0,
            "support_rate": 1.0,
            "unsupported_rate": 0.0,
            "hallucination_score": 0.0,
            "material_unsupported_count": 0,
            "quality_status": "PASS",
            "passed_gate": True,
            "reasons": []
        }

    supported = 0
    partially_supported = 0
    unsupported = 0
    contradicted = 0
    insufficient = 0
    material_unsupported = 0

    for item in verification_results:
        status_str = str(item.get("status", "")).strip()
        is_material = bool(item.get("is_material", False))
        
        # Check matching enum or string
        if status_str in (ClaimStatus.SUPPORTED.value, "Supported"):
            supported += 1
        elif status_str in (ClaimStatus.PARTIALLY_SUPPORTED.value, "Partially Supported"):
            partially_supported += 1
        elif status_str in (ClaimStatus.UNSUPPORTED.value, "Unsupported"):
            unsupported += 1
            if is_material:
                material_unsupported += 1
        elif status_str in (ClaimStatus.CONTRADICTED.value, "Contradicted"):
            contradicted += 1
            unsupported += 1  # Contradicted claims also count towards unsupported
            if is_material:
                material_unsupported += 1
        elif status_str in (ClaimStatus.INSUFFICIENT_EVIDENCE.value, "Insufficient Evidence"):
            insufficient += 1

    # PRD Metric Calculations
    effective_supported = supported + (0.5 * partially_supported)
    support_rate = round(effective_supported / total, 4)
    unsupported_rate = round(unsupported / total, 4)
    hallucination_score = round((unsupported / total) * 100.0, 2)

    # Evaluate against thresholds
    reasons = []
    passed = True

    if hallucination_score > thresholds.max_hallucination_score:
        passed = False
        reasons.append(
            f"Hallucination score ({hallucination_score:.1f}%) exceeds maximum threshold ({thresholds.max_hallucination_score:.1f}%)."
        )

    if support_rate < thresholds.min_support_rate:
        passed = False
        reasons.append(
            f"Support rate ({support_rate * 100:.1f}%) below minimum required ({thresholds.min_support_rate * 100:.1f}%)."
        )

    if material_unsupported > 0:
        passed = False
        reasons.append(f"{material_unsupported} material claim(s) in critical sections lack evidence.")

    quality_status = "PASS" if passed else "FAIL"
    logger.info(
        f"Evaluation Results -> Total: {total}, Supported: {supported}, "
        f"Unsupported: {unsupported}, Hallucination Score: {hallucination_score}%, Status: {quality_status}"
    )

    return {
        "total_claims": total,
        "supported_count": supported,
        "partially_supported_count": partially_supported,
        "unsupported_count": unsupported,
        "contradicted_count": contradicted,
        "insufficient_evidence_count": insufficient,
        "support_rate": support_rate,
        "unsupported_rate": unsupported_rate,
        "hallucination_score": hallucination_score,
        "material_unsupported_count": material_unsupported,
        "quality_status": quality_status,
        "passed_gate": passed,
        "reasons": reasons
    }
