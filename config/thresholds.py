"""Quality gate thresholds and evaluation constants."""
from dataclasses import dataclass

@dataclass
class QualityThresholds:
    """Configurable thresholds for the verification and quality gate loop."""
    # Minimum ratio of checkable claims that must be strictly Supported
    min_support_rate: float = 0.70
    
    # Maximum tolerated hallucination score (Unsupported Claims / Total Claims * 100)
    max_hallucination_score: float = 15.0
    
    # Minimum Ragas Faithfulness score (0.0 to 1.0)
    min_faithfulness: float = 0.75
    
    # Minimum Ragas Answer Relevancy score (0.0 to 1.0)
    min_answer_relevancy: float = 0.75
    
    # Minimum Context Precision score (0.0 to 1.0)
    min_context_precision: float = 0.70
    
    # Maximum number of self-correction re-research and revision retries
    max_retries: int = 2
    
    # Minimum reliability weight required for high-stakes financial/executive claims
    min_reliability_weight: float = 0.60
    
    # Search parameters
    max_search_results_per_query: int = 5
    search_depth: str = "advanced"  # 'basic' or 'advanced'
