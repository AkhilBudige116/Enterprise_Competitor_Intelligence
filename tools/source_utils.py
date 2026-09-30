"""Source reliability weighting, evidence deduplication, and ranking utilities."""
import re
from typing import List, Dict, Any
from urllib.parse import urlparse
from schemas.evidence import EvidenceRecord

TIER_1_DOMAINS = {
    "sec.gov", "investor.nvidia.com", "ir.amd.com", "intc.com", "reuters.com",
    "bloomberg.com", "wsj.com", "ft.com", "cnbc.com", "sec.gov/edgar"
}

TIER_2_DOMAINS = {
    "techcrunch.com", "theverge.com", "anandtech.com", "tomshardware.com",
    "venturebeat.com", "tomshardware.com", "semianalysis.com", "arstechnica.com",
    "nature.com", "ieee.org", "arxiv.org", "zdnet.com", "forbes.com"
}

def compute_source_weight(source_url: str, source_type: str = "web") -> float:
    """Assigns reliability weight from 0.0 to 1.0 based on domain authority and source type."""
    if not source_url:
        return 0.50
        
    if source_type == "financial":
        return 0.95
        
    try:
        domain = urlparse(source_url).netloc.lower()
        # Remove www.
        if domain.startswith("www."):
            domain = domain[4:]
            
        for t1 in TIER_1_DOMAINS:
            if t1 in domain:
                return 0.95
                
        for t2 in TIER_2_DOMAINS:
            if t2 in domain:
                return 0.85
                
        if domain.endswith(".edu") or domain.endswith(".gov"):
            return 0.90
            
        if domain.endswith(".org"):
            return 0.80
            
        return 0.70
    except Exception:
        return 0.60

def _normalize_text(text: str) -> str:
    """Normalize text for similarity checks."""
    return re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).strip()

def deduplicate_evidence(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate evidence records by normalized URL and excerpt fingerprint."""
    seen_urls = set()
    seen_snippets = set()
    unique_records = []
    
    for rec in records:
        url = rec.get("source_url", "").strip().lower()
        excerpt = _normalize_text(rec.get("excerpt", "")[:120])
        
        # If url is unique and excerpt is non-empty
        if url and url not in seen_urls:
            seen_urls.add(url)
            if excerpt:
                seen_snippets.add(excerpt)
            unique_records.append(rec)
        elif excerpt and excerpt not in seen_snippets:
            seen_snippets.add(excerpt)
            unique_records.append(rec)
        elif not url and not excerpt:
            unique_records.append(rec)
            
    return unique_records

def rank_evidence(
    records: List[Dict[str, Any]],
    target_companies: List[str],
    top_k: int = 40
) -> List[Dict[str, Any]]:
    """Rank evidence by reliability weight, relevance, and company tags."""
    if not records:
        return []
        
    def score_record(rec: Dict[str, Any]) -> float:
        weight = rec.get("reliability_weight", 0.7)
        claim_text = (rec.get("claim", "") + " " + rec.get("excerpt", "")).lower()
        
        # Boost if target companies are mentioned
        company_matches = sum(1 for c in target_companies if c.lower() in claim_text)
        tag_matches = len(rec.get("company_tags", []))
        
        # Boost for recent news or hard numbers
        has_numbers = 1 if re.search(r"\$\d+|\d+\%|\d+\s*(billion|million|trillion)", claim_text) else 0
        
        return weight * 1.5 + (company_matches * 0.4) + (tag_matches * 0.2) + (has_numbers * 0.3)

    sorted_records = sorted(records, key=score_record, reverse=True)
    return sorted_records[:top_k]
