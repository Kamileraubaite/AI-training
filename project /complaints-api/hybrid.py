"""
Hybrid search: Combined vector search and keyword search, merged by rank.
"""

from functools import lru_cache

import bm25 
import chunk_index
import chunking 
import fusion

POOL = 10

# keyword index 
@lru_cache(maxsize=None)
def keyword_index(strategy):
    return bm25.BM25Index(chunking.chunk_corpus(chunk_index.ALL_DOCS, strategy))

# Identifiers - # Finds query tokens containing numbers, such as "003" from PRD-003
def identifiers(text):
    return {token for token in bm25.tokenize(text) if any(ch.isdigit() for ch in token)}

# is_usable 
    # this is our gate, in one line
        # pass if cosine reach the floor OR the chunk shares a number with the question
def is_usable(hit, floor):
    return hit["score"] >= floor

def search_with_vector(strategy: str, question: str, query_vector: list[float], top_k: int = 3, pool: int = POOL) -> list[dict]:
    vector_hits = chunk_index.search_with_vector(strategy, [query_vector], k=pool)[0]
    keyword_hits = keyword_index(strategy).search(question, k=pool)

    fused = fusion.reciprocal_rank_fusion([
        [hit["chunk_id"] for hit in vector_hits],
        [hit["chunk"]["id"] for hit in keyword_hits],
    ])[:top_k]

    by_vector = {hit["chunk_id"]: hit for hit in vector_hits}
    by_keyword = {hit["chunk"]["id"]: hit["chunk"] for hit in keyword_hits}

    keyword_only = [chunk_id for chunk_id in by_keyword if chunk_id not in by_vector]
    extra_cosine = chunk_index.cosine_for(strategy, query_vector, keyword_only)

    unknown = [chunk_id for chunk_id in keyword_only if chunk_id not in extra_cosine]
    if unknown:
        raise RuntimeError(f"{unknown[0]} is in the keyword index but not in the vector index. Rebuild the strategy's index.")

    wanted = identifiers(question)

    hits = []
    for chunk_id, rrf in fused:
        if chunk_id in by_vector:
            hit = by_vector[chunk_id] 
        else:
            chunk = by_keyword[chunk_id]
            hit = {
                "id": chunk["doc_id"],
                "chunk_id": chunk_id,
                "title": chunk["title"],
                "text": chunk["text"],
                "score": extra_cosine[chunk_id],
            }
        hit["found_by"] = [name for name, found in (("vector", chunk_id in by_vector), ("keyword", chunk_id in by_keyword)) if found]
        hit["exact_match"] = bool(wanted & set(bm25.tokenize(hit["text"])))
        hit["rrf"] = round(rrf, 5)
        hits.append(hit)
    
    return hits

