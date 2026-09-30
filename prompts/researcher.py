"""Prompts for targeted re-research and query refinement."""

TARGETED_RESEARCH_PROMPT = """You are a Targeted Research Strategist.
The verification stage detected unsupported or contradicted factual claims during report evaluation.
Your task is to generate laser-focused search queries to find hard evidence for these specific failed claims.

Failed Claims:
{failed_claims}

Target Companies:
{companies}

Generate 2-4 high-precision search queries specifically designed to verify, confirm, or correct these claims.
Return valid JSON:
{{
  "targeted_queries": [
    {{
      "query": "Precision query string",
      "target_company": "Company name",
      "agent_type": "web|financial|news",
      "reason": "Why this query addresses the failed claim"
    }}
  ]
}}
"""
