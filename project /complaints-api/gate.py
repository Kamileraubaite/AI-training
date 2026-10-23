"""
The relevance gate - does a retrieved chunk deserve to reach the model?
"""

def is_usable(hit: dict, cosine_floor: float, rerank_floor: float) -> bool:
    if hit.get("exact_match"):
        return True
    if hit.get("rerank_score") is not None:
        return hit["rerank_score"] >= rerank_floor
    return hit["score"] >= cosine_floor