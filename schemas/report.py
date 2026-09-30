"""Report structures and 13-section schemas."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from utils.helpers import current_timestamp_iso

class ReportSection(BaseModel):
    """A single structured section of the executive report."""
    section_id: int
    title: str
    content: str
    subsections: Optional[Dict[str, str]] = None
    table_data: Optional[List[Dict[str, Any]]] = None
    citations: List[str] = Field(default_factory=list)

class CompanyProfile(BaseModel):
    """Deep-dive profile for an individual competitor."""
    company_name: str
    ticker: Optional[str] = None
    headquarters: Optional[str] = None
    overview: str = ""
    key_products: List[str] = Field(default_factory=list)
    ai_strategy: str = ""
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    market_share_notes: str = ""

class ComparisonMatrix(BaseModel):
    """Cross-company dimensional matrix."""
    dimensions: List[str] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    data: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # dimension -> {company: value}

REQUIRED_SECTION_TITLES = [
    "Executive Summary",
    "Research Scope and Methodology",
    "Market Overview",
    "Company Profiles",
    "Financial Comparison",
    "Recent Developments",
    "Competitive Landscape",
    "Strengths and Differentiators",
    "Risks and Opportunities",
    "Strategic Insights",
    "AI Research Quality Metrics",
    "Limitations",
    "References"
]

class FinalReport(BaseModel):
    """Complete 13-section executive briefing report."""
    title: str = "Enterprise Multi-Agent Competitor Intelligence Report"
    subtitle: str = "Comprehensive Autonomous Strategic Benchmarking"
    generated_at: str = Field(default_factory=current_timestamp_iso)
    companies: List[str] = Field(default_factory=list)
    sections: List[ReportSection] = Field(default_factory=list)
    company_profiles: List[CompanyProfile] = Field(default_factory=list)
    comparison_matrix: Optional[ComparisonMatrix] = None
    financial_table: Optional[List[Dict[str, Any]]] = None
    quality_summary: Optional[Dict[str, Any]] = None
    pdf_path: Optional[str] = None
