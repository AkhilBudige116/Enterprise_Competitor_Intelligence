"""Schemas package for data contracts."""
from schemas.evidence import EvidenceRecord, SourceType
from schemas.research import ResearchPlan, ResearchTask, ResearchScope
from schemas.claims import ClaimRecord, ClaimVerificationResult, ClaimStatus
from schemas.report import FinalReport, ReportSection, CompanyProfile, ComparisonMatrix

__all__ = [
    "EvidenceRecord",
    "SourceType",
    "ResearchPlan",
    "ResearchTask",
    "ResearchScope",
    "ClaimRecord",
    "ClaimVerificationResult",
    "ClaimStatus",
    "FinalReport",
    "ReportSection",
    "CompanyProfile",
    "ComparisonMatrix",
]
