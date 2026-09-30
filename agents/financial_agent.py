"""Financial Intelligence Agent: Collects structured financial metrics and valuation profiles."""
from typing import List, Dict, Any
from tools.financial_provider import BaseFinancialProvider, get_financial_provider
from utils.logger import get_logger

logger = get_logger("FinancialAgent")

class FinancialAgent:
    """Collects structured financial, valuation, margin, and growth data."""
    
    def __init__(self, provider: BaseFinancialProvider = None):
        self.provider = provider or get_financial_provider()

    def run(self, companies: List[str], tasks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"FinancialAgent analyzing companies: {companies}")
        evidence_list = []
        metrics_table = []
        
        for company in companies:
            fin_metrics = self.provider.get_company_financials(company)
            metrics_table.append(fin_metrics)
            
            ev_records = self.provider.get_financial_evidence(company)
            evidence_list.extend(ev_records)

        return {
            "financial_evidence": evidence_list,
            "financial_metrics": metrics_table
        }
