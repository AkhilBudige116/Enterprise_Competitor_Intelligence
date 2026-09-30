"""LangGraph Node implementations for Enterprise Competitor Intelligence."""
from typing import Dict, Any, List
from graph.state import CompetitorIntelligenceState
from agents.planner_agent import PlannerAgent
from agents.web_research_agent import WebResearchAgent
from agents.financial_agent import FinancialAgent
from agents.news_agent import NewsAgent
from agents.competitor_agent import CompetitorAnalysisAgent
from agents.synthesis_agent import SynthesisAgent
from agents.claim_extractor import ClaimExtractor
from agents.fact_checker_agent import FactCheckerAgent
from agents.evaluation_agent import EvaluationAgent
from tools.source_utils import deduplicate_evidence, rank_evidence
from tools.tavily_tool import TavilySearchTool
from utils.logger import get_logger
from utils.helpers import current_timestamp_iso
import os

logger = get_logger("GraphNodes")

def input_validator_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Validate user input, detect companies if missing, and initialize default state variables."""
    logger.info("--- [NODE] Input Validation ---")
    query = state.get("user_query", "").strip()
    companies = state.get("companies", [])
    
    if not query:
        query = "Compare NVIDIA, AMD, and Intel across financial performance, AI strategy, recent developments, competitive advantages, and risks."
        
    if not companies:
        # Extract default/mentioned companies
        q_lower = query.lower()
        candidates = ["NVIDIA", "AMD", "Intel", "Apple", "Microsoft", "Google", "Amazon", "Meta", "Tesla", "Qualcomm", "TSMC"]
        found = [c for c in candidates if c.lower() in q_lower]
        companies = found if found else ["NVIDIA", "AMD", "Intel"]

    scope = state.get("research_scope", {})
    if not scope.get("companies"):
        scope["companies"] = companies
    if not scope.get("research_objective"):
        scope["research_objective"] = f"Comparative strategic intelligence benchmark for {', '.join(companies)}"

    return {
        "user_query": query,
        "companies": companies,
        "research_scope": scope,
        "retry_count": state.get("retry_count", 0),
        "max_retries": state.get("max_retries", 2),
        "errors": [],
        "current_step": "Input Validation Completed"
    }

def planner_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Planning Agent decomposes research query into structured tasks."""
    logger.info("--- [NODE] Planning Agent ---")
    planner = PlannerAgent()
    plan_result = planner.plan(
        user_query=state.get("user_query", ""),
        companies=state.get("companies", []),
        scope=state.get("research_scope", {})
    )
    
    tasks = plan_result.get("tasks", [])
    detected_comps = plan_result.get("target_companies", state.get("companies", []))
    
    return {
        "research_plan": tasks,
        "companies": detected_comps,
        "current_step": f"Planned {len(tasks)} Research Tasks"
    }

def parallel_research_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Execute Web, Financial, and News intelligence gathering in parallel branches."""
    logger.info("--- [NODE] Parallel Multi-Agent Research ---")
    tasks = state.get("research_plan", [])
    companies = state.get("companies", [])
    
    # 1. Web Research Agent
    web_agent = WebResearchAgent()
    web_results = web_agent.run(tasks=tasks)
    
    # 2. Financial Intelligence Agent
    fin_agent = FinancialAgent()
    fin_data = fin_agent.run(companies=companies, tasks=tasks)
    fin_results = fin_data.get("financial_evidence", [])
    fin_metrics = fin_data.get("financial_metrics", [])
    
    # 3. News Intelligence Agent
    news_agent = NewsAgent()
    news_results = news_agent.run(companies=companies, tasks=tasks)
    
    logger.info(
        f"Parallel Research Completed -> Web: {len(web_results)}, "
        f"Financial: {len(fin_results)}, News: {len(news_results)}"
    )

    return {
        "web_results": web_results,
        "financial_results": fin_results,
        "news_results": news_results,
        "current_step": "Parallel Intelligence Gathered"
    }

def evidence_normalizer_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Aggregate, deduplicate, weight, and rank evidence from all research branches."""
    logger.info("--- [NODE] Evidence Normalization ---")
    web_res = state.get("web_results", [])
    fin_res = state.get("financial_results", [])
    news_res = state.get("news_results", [])
    existing_ev = state.get("normalized_evidence", [])
    
    raw_combined = existing_ev + web_res + fin_res + news_res
    deduped = deduplicate_evidence(raw_combined)
    ranked = rank_evidence(deduped, target_companies=state.get("companies", []), top_k=45)
    
    logger.info(f"Normalized evidence pool contains {len(ranked)} deduplicated records.")
    return {
        "normalized_evidence": ranked,
        "current_step": f"Evidence Normalized ({len(ranked)} sources)"
    }

def competitor_analyst_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Competitor Analysis Agent derives strategic profiles, SWOT, and comparison matrix."""
    logger.info("--- [NODE] Competitor Analysis Agent ---")
    analyst = CompetitorAnalysisAgent()
    analysis = analyst.analyze(
        companies=state.get("companies", []),
        normalized_evidence=state.get("normalized_evidence", []),
        research_scope=state.get("research_scope", {})
    )
    return {
        "competitor_analysis": analysis,
        "current_step": "Competitor Analysis Completed"
    }

def synthesizer_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Synthesis Agent produces the 13-section evidence-grounded report."""
    logger.info("--- [NODE] Synthesis Agent (13 Sections) ---")
    synthesizer = SynthesisAgent()
    
    targeted_feedback = None
    if state.get("retry_count", 0) > 0 and state.get("targeted_queries"):
        queries_str = ", ".join([q.get("query", "") for q in state.get("targeted_queries", [])])
        targeted_feedback = f"Prior verification flagged uncorroborated claims. Targeted research added fresh evidence for: {queries_str}. Revise claims accordingly."

    draft = synthesizer.synthesize(
        user_query=state.get("user_query", ""),
        companies=state.get("companies", []),
        normalized_evidence=state.get("normalized_evidence", []),
        competitor_analysis=state.get("competitor_analysis", {}),
        research_scope=state.get("research_scope", {}),
        targeted_feedback=targeted_feedback
    )
    
    return {
        "draft_report": draft,
        "current_step": "13-Section Report Synthesized"
    }

def claim_extractor_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Claim Extractor splits draft into atomic checkable propositions."""
    logger.info("--- [NODE] Claim Extraction ---")
    extractor = ClaimExtractor()
    claims = extractor.extract_claims(draft_report=state.get("draft_report", {}))
    return {
        "claims": claims,
        "current_step": f"Extracted {len(claims)} Atomic Claims"
    }

def verifier_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Fact Checker Agent verifies atomic claims against normalized evidence pool."""
    logger.info("--- [NODE] Fact Verification Agent ---")
    verifier = FactCheckerAgent()
    verification_results = verifier.verify_claims(
        claims=state.get("claims", []),
        normalized_evidence=state.get("normalized_evidence", [])
    )
    return {
        "verification_results": verification_results,
        "current_step": f"Verified {len(verification_results)} Claims"
    }

def evaluator_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Evaluation Agent calculates Ragas metrics, hallucination score, and quality status."""
    logger.info("--- [NODE] Evaluation & Quality Gate ---")
    evaluator = EvaluationAgent()
    eval_result = evaluator.evaluate(
        user_query=state.get("user_query", ""),
        draft_report=state.get("draft_report", {}),
        verification_results=state.get("verification_results", []),
        normalized_evidence=state.get("normalized_evidence", [])
    )
    return {
        "evaluation_scores": eval_result.get("evaluation_scores", {}),
        "hallucination_score": eval_result.get("hallucination_score", 0.0),
        "support_rate": eval_result.get("support_rate", 1.0),
        "quality_status": eval_result.get("quality_status", "PASS"),
        "failed_claim_ids": eval_result.get("failed_claim_ids", []),
        "current_step": f"Quality Gate Evaluated: {eval_result.get('quality_status', 'PASS')}"
    }

def targeted_research_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Self-correction loop: generates targeted search queries for failed claims and retrieves fresh evidence."""
    logger.info("--- [NODE] Targeted Re-Research (Self-Correction Loop) ---")
    retries = state.get("retry_count", 0) + 1
    failed_ids = state.get("failed_claim_ids", [])
    ver_results = state.get("verification_results", [])
    
    # Identify failed claim texts
    failed_claims = [v for v in ver_results if v.get("claim_id") in failed_ids]
    search_tool = TavilySearchTool()
    
    new_evidence = []
    targeted_queries = []
    for item in failed_claims[:3]:
        claim_text = item.get("text", "")
        # Generate targeted query
        query = f"evidence verification: {claim_text[:80]}"
        targeted_queries.append({"query": query, "claim_id": item.get("claim_id")})
        res = search_tool.search(query=query, max_results=3)
        new_evidence.extend(res)

    existing_ev = state.get("normalized_evidence", [])
    updated_ev = deduplicate_evidence(existing_ev + new_evidence)

    logger.info(f"Targeted research retrieved {len(new_evidence)} new evidence records on retry attempt {retries}.")
    return {
        "normalized_evidence": updated_ev,
        "retry_count": retries,
        "targeted_queries": targeted_queries,
        "current_step": f"Targeted Self-Correction (Retry {retries})"
    }

def pdf_generator_node(state: CompetitorIntelligenceState) -> Dict[str, Any]:
    """Report Agent / Service: Builds ReportLab Executive PDF and packages final report."""
    logger.info("--- [NODE] Executive PDF Generator ---")
    from reports.pdf_generator import generate_executive_pdf
    
    draft = state.get("draft_report", {})
    companies = state.get("companies", [])
    analysis = state.get("competitor_analysis", {})
    ver_results = state.get("verification_results", [])
    eval_scores = state.get("evaluation_scores", {})
    fin_metrics = [fin for fin in state.get("financial_results", []) if isinstance(fin, dict)]
    
    # Get financial data table from analysis or financial metrics
    fin_agent = FinancialAgent()
    fin_table = [fin_agent.provider.get_company_financials(c) for c in companies]

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"Competitor_Intelligence_Report_{'_'.join(companies[:3])}.pdf")
    
    try:
        generate_executive_pdf(
            output_path=pdf_path,
            report_data=draft,
            companies=companies,
            company_profiles=analysis.get("company_profiles", []),
            comparison_matrix=analysis.get("comparison_matrix", {}),
            financial_table=fin_table,
            verification_results=ver_results,
            evaluation_scores=eval_scores
        )
        logger.info(f"ReportLab Executive PDF generated at: {pdf_path}")
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        pdf_path = ""

    final_report = {
        **draft,
        "companies": companies,
        "company_profiles": analysis.get("company_profiles", []),
        "comparison_matrix": analysis.get("comparison_matrix", {}),
        "financial_table": fin_table,
        "verification_results": ver_results,
        "evaluation_scores": eval_scores,
        "pdf_path": pdf_path
    }

    return {
        "final_report": final_report,
        "pdf_path": pdf_path,
        "current_step": "Executive PDF Generated"
    }
