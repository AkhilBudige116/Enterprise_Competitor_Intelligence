"""Claim extraction and fact verification schemas."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

class ClaimStatus(str, Enum):
    SUPPORTED = "Supported"
    PARTIALLY_SUPPORTED = "Partially Supported"
    UNSUPPORTED = "Unsupported"
    CONTRADICTED = "Contradicted"
    INSUFFICIENT_EVIDENCE = "Insufficient Evidence"

class ClaimRecord(BaseModel):
    """An atomic factual statement extracted from draft synthesis."""
    claim_id: str = Field(default_factory=lambda: f"clm-{uuid.uuid4().hex[:6]}")
    text: str = Field(..., description="Atomic factual proposition")
    section_name: str = Field(default="General", description="Report section where claim originated")
    company_tag: Optional[str] = Field(None, description="Relevant company if applicable")
    is_material: bool = Field(default=False, description="Whether claim is high-impact (e.g. executive summary, key numbers)")

class ClaimVerificationResult(BaseModel):
    """Outcome of verifying an atomic claim against evidence pool."""
    claim_id: str
    text: str
    section_name: str = "General"
    status: ClaimStatus = ClaimStatus.UNSUPPORTED
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    rationale: str = Field(default="", description="Why this status was determined")

class VerificationSummary(BaseModel):
    """Aggregated metrics across all claims."""
    total_claims: int = 0
    supported_claims: int = 0
    partially_supported_claims: int = 0
    unsupported_claims: int = 0
    contradicted_claims: int = 0
    insufficient_evidence_claims: int = 0
    support_rate: float = 0.0
    unsupported_rate: float = 0.0
    hallucination_score: float = 0.0  # percentage 0-100
    quality_status: str = "PASS"      # PASS | FAIL
