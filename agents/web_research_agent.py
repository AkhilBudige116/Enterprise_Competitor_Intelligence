"""Web Research Agent: Uses Tavily and search tools to collect technical & strategic evidence."""
from typing import List, Dict, Any
from tools.tavily_tool import TavilySearchTool
from utils.logger import get_logger

logger = get_logger("WebResearchAgent")

class WebResearchAgent:
    """Collects company, product, strategy, partnership, and market evidence."""
    
    def __init__(self, search_tool: TavilySearchTool = None):
        self.search_tool = search_tool or TavilySearchTool()

    def run(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"WebResearchAgent starting execution for {len(tasks)} tasks.")
        all_evidence = []
        for task in tasks:
            if task.get("agent_type") != "web":
                continue
            query = task.get("query", "")
            company = task.get("target_company")
            results = self.search_tool.search(query=query, company_tag=company)
            all_evidence.extend(results)
            
        logger.info(f"WebResearchAgent collected {len(all_evidence)} raw evidence records.")
        return all_evidence
