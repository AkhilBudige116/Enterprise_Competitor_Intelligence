"""Tests for Hallucination Scoring and Support Rate formulas."""
import pytest
from evaluation.hallucination_score import calculate_hallucination_metrics
from config.thresholds import QualityThresholds
from schemas.claims import ClaimStatus

def test_hallucination_score_perfect():
    """Test perfect score where all claims are supported."""
    ver_results = [
        {"claim_id": "c1", "text": "Claim 1", "status": ClaimStatus.SUPPORTED.value, "is_material": True},
        {"claim_id": "c2", "text": "Claim 2", "status": ClaimStatus.SUPPORTED.value, "is_material": False},
        {"claim_id": "c3", "text": "Claim 3", "status": ClaimStatus.SUPPORTED.value, "is_material": False},
        {"claim_id": "c4", "text": "Claim 4", "status": ClaimStatus.SUPPORTED.value, "is_material": False}
    ]
    
    metrics = calculate_hallucination_metrics(ver_results)
    assert metrics["total_claims"] == 4
    assert metrics["supported_count"] == 4
    assert metrics["unsupported_count"] == 0
    assert metrics["support_rate"] == 1.0
    assert metrics["hallucination_score"] == 0.0
    assert metrics["quality_status"] == "PASS"

def test_hallucination_score_failure():
    """Test quality gate rejection when hallucination exceeds threshold."""
    ver_results = [
        {"claim_id": "c1", "text": "Claim 1", "status": ClaimStatus.SUPPORTED.value, "is_material": False},
        {"claim_id": "c2", "text": "Claim 2", "status": ClaimStatus.UNSUPPORTED.value, "is_material": False},
        {"claim_id": "c3", "text": "Claim 3", "status": ClaimStatus.CONTRADICTED.value, "is_material": False},
        {"claim_id": "c4", "text": "Claim 4", "status": ClaimStatus.UNSUPPORTED.value, "is_material": False}
    ]
    
    thresholds = QualityThresholds(max_hallucination_score=15.0, min_support_rate=0.70)
    metrics = calculate_hallucination_metrics(ver_results, thresholds)
    
    assert metrics["total_claims"] == 4
    assert metrics["unsupported_count"] == 3
    assert metrics["hallucination_score"] == 75.0
    assert metrics["quality_status"] == "FAIL"
    assert len(metrics["reasons"]) > 0

def test_material_claim_failure():
    """Test rejection when a material executive claim is unsupported."""
    ver_results = [
        {"claim_id": "c1", "text": "Claim 1", "status": ClaimStatus.SUPPORTED.value, "is_material": False},
        {"claim_id": "c2", "text": "Claim 2", "status": ClaimStatus.SUPPORTED.value, "is_material": False},
        {"claim_id": "c3", "text": "Claim 3", "status": ClaimStatus.SUPPORTED.value, "is_material": False},
        {"claim_id": "c4", "text": "Material Claim", "status": ClaimStatus.UNSUPPORTED.value, "is_material": True}
    ]
    
    metrics = calculate_hallucination_metrics(ver_results)
    assert metrics["material_unsupported_count"] == 1
    assert metrics["quality_status"] == "FAIL"
