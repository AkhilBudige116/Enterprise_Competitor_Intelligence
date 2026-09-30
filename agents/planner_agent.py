"""Planning Agent: Decomposes natural language requests into structured multi-agent tasks."""
from typing import Dict, Any, List
from config.settings import get_llm
from prompts.planner import PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE
from utils.logger import get_logger
from utils.helpers import safe_json_parse
from langchain_core.messages import SystemMessage, HumanMessage

logger = get_logger("PlannerAgent")

class PlannerAgent:
    """Interprets the user request and creates explicit tasks for research agents."""
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()

    def plan(self, user_query: str, companies: List[str] = None, scope: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info(f"Generating research plan for query: '{user_query}'")
        scope = scope or {}
        focus_areas = scope.get("focus_areas", ["Financial Performance", "AI Strategy", "Recent News", "Moats & Risks"])
        date_range = scope.get("date_range", "Last 12 Months")
        
        prompt_text = PLANNER_USER_TEMPLATE.format(
            user_query=user_query,
            focus_areas=", ".join(focus_areas) if isinstance(focus_areas, list) else str(focus_areas),
            date_range=date_range
        )
        
        try:
            messages = [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=prompt_text)
            ]
            response = self.llm.invoke(messages)
            parsed = safe_json_parse(response.content)
            if parsed and "tasks" in parsed:
                logger.info(f"Successfully planned {len(parsed['tasks'])} research tasks.")
                return parsed
        except Exception as e:
            logger.warning(f"Planner LLM parsing failed: {e}. Generating deterministic plan.")
            
        return self._generate_fallback_plan(user_query, companies, focus_areas)

    def _generate_fallback_plan(self, user_query: str, companies: List[str], focus_areas: List[str]) -> Dict[str, Any]:
        """Generate reliable deterministic plan when LLM is offline or non-responsive."""
        target_comps = companies or []
        if not target_comps:
            q_lower = user_query.lower()
            detected = []
            for candidate in ["NVIDIA", "AMD", "Intel", "Apple", "Microsoft", "Google", "Amazon", "Meta", "Tesla", "Qualcomm", "TSMC"]:
                if candidate.lower() in q_lower:
                    detected.append(candidate)
            target_comps = detected if detected else ["NVIDIA", "AMD", "Intel"]

        tasks = []
        task_idx = 1
        for comp in target_comps:
            # Web research tasks
            tasks.append({
                "task_id": f"task-{task_idx:02d}",
                "agent_type": "web",
                "target_company": comp,
                "query": f"{comp} AI architecture datacenter product roadmap competitive strategy",
                "objective": f"Identify {comp}'s core AI accelerators, software ecosystem, and architecture",
                "priority": 1
            })
            task_idx += 1
            
            # Financial intelligence task
            tasks.append({
                "task_id": f"task-{task_idx:02d}",
                "agent_type": "financial",
                "target_company": comp,
                "query": f"{comp} quarterly earnings valuation gross margin revenue growth",
                "objective": f"Fetch latest financial metrics, revenue, and margins for {comp}",
                "priority": 1
            })
            task_idx += 1
            
            # News intelligence task
            tasks.append({
                "task_id": f"task-{task_idx:02d}",
                "agent_type": "news",
                "target_company": comp,
                "query": f"{comp} recent announcements strategic partnerships regulatory supply chain",
                "objective": f"Capture recent announcements, M&A, and market developments for {comp}",
                "priority": 2
            })
            task_idx += 1

        return {
            "target_companies": target_comps,
            "market_sector": "Technology / Enterprise AI",
            "research_objective": f"Comprehensive competitive benchmarking for {', '.join(target_comps)}",
            "strategy_summary": "Parallel tri-agent intelligence gathering across Web, Financial fundamentals, and News recency.",
            "tasks": tasks
        }
