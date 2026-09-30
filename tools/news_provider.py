"""Date-aware News Intelligence Search Tool."""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.logger import get_logger
from utils.helpers import current_timestamp_iso
from tools.tavily_tool import TavilySearchTool
from tools.source_utils import compute_source_weight

logger = get_logger("NewsProvider")

class NewsSearchTool:
    """Specialized tool for gathering date-stamped announcements, strategic moves, and partnerships."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.tavily = TavilySearchTool(api_key=api_key)

    def search_news(
        self,
        company_name: str,
        query_context: str = "strategic announcements partnerships product launch",
        max_results: int = 4
    ) -> List[Dict[str, Any]]:
        """Search recent news and extract date-aware evidence."""
        query = f"{company_name} {query_context} recent news"
        logger.info(f"Gathering news intelligence for {company_name}: '{query}'")
        
        raw_results = self.tavily.search(
            query=query,
            company_tag=company_name,
            topic="news",
            max_results=max_results
        )
        
        news_records = []
        for item in raw_results:
            rec = item.copy()
            rec["source_type"] = "news"
            rec["reliability_weight"] = compute_source_weight(rec.get("source_url", ""), "news")
            
            # Format claim to highlight recent developments
            rec["claim"] = f"Recent Development [{company_name}]: {rec.get('claim', '')}"
            news_records.append(rec)
            
        return news_records
