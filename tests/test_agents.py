"""Unit tests for individual agent modules."""
import pytest
from agents.planner_agent import PlannerAgent
from agents.web_research_agent import WebResearchAgent
from agents.financial_agent import FinancialAgent
from agents.competitor_agent import CompetitorAnalysisAgent
from agents.synthesis_agent import SynthesisAgent
from agents.claim_extractor import ClaimExtractor
from agents.fact_checker_agent import FactCheckerAgent
from agents.evaluation_agent import EvaluationAgent
from tools.tavily_tool import TavilySearchTool
from tools.financial_provider import FallbackFinancialProvider
from schemas.report import REQUIRED_SECTION_TITLES

def test_planner_agent():
    planner = PlannerAgent()
    plan = planner.plan(
        user_query="Compare NVIDIA and AMD in AI GPUs",
        companies=["NVIDIA", "AMD"]
    )
    assert "tasks" in plan
    assert len(plan["tasks"]) > 0
    assert "NVIDIA" in plan.get("target_companies", [])

def test_financial_agent():
    fin_agent = FinancialAgent(provider=FallbackFinancialProvider())
    res = fin_agent.run(companies=["NVIDIA", "AMD"])
    assert "financial_evidence" in res
    assert "financial_metrics" in res
    assert len(res["financial_metrics"]) == 2

def test_competitor_analysis_agent():
    analyst = CompetitorAnalysisAgent()
    evidence = [
        {"claim_id": "e1", "claim": "NVIDIA dominates AI training with CUDA", "source_type": "web", "reliability_weight": 0.9, "excerpt": "CUDA software moat", "company_tags": ["NVIDIA"]},
        {"claim_id": "e2", "claim": "AMD expands ROCm and Instinct MI300X", "source_type": "web", "reliability_weight": 0.85, "excerpt": "ROCm open source", "company_tags": ["AMD"]}
    ]
    analysis = analyst.analyze(companies=["NVIDIA", "AMD"], normalized_evidence=evidence)
    assert "company_profiles" in analysis
    assert "comparison_matrix" in analysis
    assert len(analysis["company_profiles"]) == 2

def test_synthesis_agent_13_sections():
    synth = SynthesisAgent()
    evidence = [
        {"claim_id": "e1", "claim": "NVIDIA reports record data center revenue", "source_title": "SEC 10-K", "source_url": "https://sec.gov", "excerpt": "Revenue $96B", "reliability_weight": 0.95}
    ]
    analysis = {
        "company_profiles": [{"company_name": "NVIDIA", "ticker": "NVDA", "overview": "Leader in AI", "key_products": ["H100", "Blackwell"], "ai_strategy": "Full stack"}],
        "comparison_matrix": {"dimensions": ["AI"], "companies": ["NVIDIA"], "data": {"AI": {"NVIDIA": "High"}}}
    }
    report = synth.synthesize(
        user_query="NVIDIA analysis",
        companies=["NVIDIA"],
        normalized_evidence=evidence,
        competitor_analysis=analysis
    )
    assert "sections" in report
    assert len(report["sections"]) == 13
    titles = [s["title"] for s in report["sections"]]
    assert "Executive Summary" in titles
    assert "Limitations" in titles
    assert "References" in titles

def test_claim_extractor_and_fact_checker():
    extractor = ClaimExtractor()
    draft = {
        "sections": [
            {"title": "Executive Summary", "content": "NVIDIA reported 122% revenue growth and maintains 75% gross margins."}
        ]
    }
    claims = extractor.extract_claims(draft)
    assert len(claims) > 0
    
    evidence = [
        {"claim_id": "e1", "source_title": "SEC Filing", "source_url": "https://sec.gov", "excerpt": "NVIDIA reported 122% revenue growth and maintains 75% gross margins.", "reliability_weight": 0.95}
    ]
    verifier = FactCheckerAgent()
    results = verifier.verify_claims(claims, evidence)
    assert len(results) == len(claims)
    assert results[0]["status"] in ["Supported", "Partially Supported"]
