"""Claim Extractor Agent: Splits draft sections into atomic checkable propositions."""
from typing import List, Dict, Any
import re
from config.settings import get_llm
from prompts.verifier import CLAIM_EXTRACTION_PROMPT
from utils.logger import get_logger
from utils.helpers import safe_json_parse
from langchain_core.messages import HumanMessage

logger = get_logger("ClaimExtractor")

class ClaimExtractor:
    """Decomposes report text into atomic testable statements."""
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()

    def extract_claims(self, draft_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        logger.info("Extracting atomic claims from draft report...")
        sections = draft_report.get("sections", [])
        
        # Select high-priority sections for deep verification
        text_samples = []
        for s in sections:
            title = s.get("title", "")
            content = s.get("content", "")
            if title in ["Executive Summary", "Financial Comparison", "Market Overview", "Recent Developments", "Strengths and Differentiators"]:
                text_samples.append(f"Section [{title}]:\n{content}")

        joined_draft = "\n\n".join(text_samples)
        
        try:
            prompt = CLAIM_EXTRACTION_PROMPT.format(draft_text=joined_draft[:4000])
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            parsed = safe_json_parse(response.content)
            if parsed and "claims" in parsed and len(parsed["claims"]) >= 3:
                logger.info(f"Successfully extracted {len(parsed['claims'])} atomic claims via LLM.")
                return parsed["claims"]
        except Exception as e:
            logger.warning(f"Claim extraction LLM error: {e}. Using deterministic claim splitter.")

        return self._rule_based_claim_extraction(sections)

    def _rule_based_claim_extraction(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        claims = []
        claim_idx = 1
        
        for s in sections:
            sec_title = s.get("title", "General")
            content = s.get("content", "")
            # Split into sentences
            sentences = re.split(r"(?<=[.!?])\s+", content)
            
            for sent in sentences:
                clean_sent = sent.strip()
                if len(clean_sent) < 25 or clean_sent.startswith("#") or clean_sent.startswith("1."):
                    continue
                # Pick sentences with factual assertions or numbers or company names
                is_factual = bool(re.search(r"(\$|\%|\d+|margin|revenue|architecture|datacenter|accelerator|market)", clean_sent, re.I))
                if is_factual and len(claims) < 18:
                    is_mat = (sec_title in ["Executive Summary", "Financial Comparison"])
                    claims.append({
                        "claim_id": f"clm-{claim_idx:02d}",
                        "text": clean_sent,
                        "section_name": sec_title,
                        "company_tag": "All",
                        "is_material": is_mat
                    })
                    claim_idx += 1
                    
        return claims
