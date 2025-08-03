
from typing import TypedDict, List, Dict, Any


class LanggraphState(TypedDict):
    subject: str
    description: str
    category: str
    retrieved_docs: List[Dict[str, Any]]
    draft_response: str
    review_result: Dict[str, Any]
    review_attempts: int
    final_response: str
    query_embedding: List[float]
