"""Prompts for Claim Extraction and Fact-Checking Agents."""

CLAIM_EXTRACTION_PROMPT = """You are an Atomic Claim Extraction Specialist.
Your task is to analyze the draft report sections and decompose the text into discrete, testable, atomic factual statements.

Guidelines:
- Extract factual statements (claims about financial metrics, market share, product features, dates, strategic moves).
- Skip pure subjective commentary or stylistic transitions.
- Mark high-impact claims (e.g. from Executive Summary, financial figures, growth stats) as `is_material: true`.
- Extract 10-20 critical atomic claims from the text.

Report Draft to Extract From:
{draft_text}

Return valid JSON with the following schema:
{{
  "claims": [
    {{
      "claim_id": "clm-01",
      "text": "Specific atomic factual statement",
      "section_name": "Executive Summary",
      "company_tag": "Company Name",
      "is_material": true
    }}
  ]
}}
"""

FACT_CHECKER_PROMPT = """You are a Strict Fact Verification & Evidence Alignment Agent.
Your duty is to cross-verify extracted claims against the authoritative evidence pool.

For each claim:
1. Search the evidence records for explicit backing, partial backing, or contradicting information.
2. Assign one of the five formal verification statuses:
   - "Supported": The evidence directly and unambiguously corroborates the claim.
   - "Partially Supported": The evidence supports core parts of the claim, but lacks minor specifics.
   - "Unsupported": No direct evidence in the pool confirms the claim.
   - "Contradicted": The evidence directly contradicts or refutes the claim.
   - "Insufficient Evidence": The evidence is too vague, outdated, or ambiguous to confirm or refute.
3. Assign a confidence score from 0.0 to 1.0.
4. List the supporting evidence IDs and provide a brief rationale.

Evidence Pool:
{evidence_text}

Claims to Verify:
{claims_json}

Return valid JSON:
{{
  "verification_results": [
    {{
      "claim_id": "clm-01",
      "text": "Claim statement text",
      "section_name": "Section Name",
      "status": "Supported|Partially Supported|Unsupported|Contradicted|Insufficient Evidence",
      "confidence": 0.95,
      "supporting_evidence_ids": ["ev-01", "ev-02"],
      "citations": ["Title of source (URL)"],
      "rationale": "Clear explanation of verification verdict"
    }}
  ]
}}
"""
