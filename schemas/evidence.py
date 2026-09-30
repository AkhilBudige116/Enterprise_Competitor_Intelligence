"""Evidence schema contract matching PRD specifications."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from utils.helpers import current_timestamp_iso

class SourceType(str, Enum):
    WEB = "web"
    FINANCIAL = "financial"
    NEWS = "news"

class EvidenceRecord(BaseModel):
    """Evidence record contract carrying retrieved information across the multi-agent graph."""
    claim_id: str = Field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:8]}")
    claim: str = Field(..., description="Fact or observation retrieved from source")
    source_title: str = Field(..., description="Title of the source article or document")
    source_url: str = Field(..., description="URL or filing reference identifier")
    source_type: str = Field("web", description="Type of source: web | financial | news")
    retrieved_at: str = Field(default_factory=current_timestamp_iso, description="ISO timestamp")
    excerpt: str = Field(..., description="Direct quote or specific context supporting the claim")
    reliability_weight: float = Field(0.7, ge=0.0, le=1.0, description="Confidence/reliability weight (0.0 to 1.0)")
    company_tags: List[str] = Field(default_factory=list, description="Target companies referenced in this evidence")

    def to_dict(self) -> dict:
        return self.model_dump()
