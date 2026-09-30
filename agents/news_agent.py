"""News Intelligence Agent: Identifies recent announcements and date-aware developments."""
from typing import List, Dict, Any
from tools.news_provider import NewsSearchTool
from utils.logger import get_logger

logger = get_logger("NewsAgent")

class NewsAgent:
    """Collects recent announcements, M&A, partnerships, and market updates."""
    
    def __init__(self, news_tool: NewsSearchTool = None):
        self.news_tool = news_tool or NewsSearchTool()

    def run(self, companies: List[str], tasks: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        logger.info(f"NewsAgent gathering developments for: {companies}")
        news_evidence = []
        for company in companies:
            items = self.news_tool.search_news(company_name=company)
            news_evidence.extend(items)
            
        logger.info(f"NewsAgent collected {len(news_evidence)} news records.")
        return news_evidence
