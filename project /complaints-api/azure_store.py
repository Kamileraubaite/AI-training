import time
from functools import lru_cache

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

import azure_index
import bm25
import chunk_index
import settings

# semantic ranker only ever reads the top 50 results, so we'll ask for that many and trim to top_k after
CANDIDATES = 50

# chunks per loaded request
BATCH = 100

NOT_BUILT = "The azure index is empty or missing. Build it with puython -m azure_build"

@lru_cache(maxsize=None)
def _credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()

def _endpoint() -> str:
    if not settings.AZURE_SEARCH_ENDPOINT:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT is not set"
                           "Example: export AZURE_SEARCH_ENDPOINT=https://<your-service>.search.windows.net")
    return settings.AZURE_SEARCH_ENDPOINT

@lru_cache(maxsize=None)
def search_client() -> SearchClient:
    return SearchClient(endpoint=_endpoint(), index_name=settings.AZURE_SEARCH_INDEX, credential=_credential())

@lru_cache(maxsize=None)
def index_client() -> SearchIndexClient:
    return SearchIndexClient(endpoint=_endpoint(), credential=_credential())

def count() -> int:
    try:
        return search_client().search(search_text="*", include_total_count=True, top=0).get_count()
    except ResourceNotFoundError:
        return 0

def search_with_vector(question: str, query_vector: list[float], top_k: int = 3, semantic: bool = True) -> list[dict]:
    search_text = "".join(bm25.tokenize(question)) or "*"

    options = {
        "search_text": search_text,
        "vector_queries": [VectorizedQuery(vector=query_vector, k_nearest_neighbors=CANDIDATES, fields=["embedding"])],
        "select": ["chunk_id", "doc_id", "title", "text"],
        "top": max(top_k, CANDIDATES),
    }

    if semantic:
        options["query_type"] = "semantic"
        options["semantic_configuration_name"] = settings.SEMANTIC_CONFIG
    
    try:
        results = list(search_client().search(**options))[:top_k]
    except ResourceNotFoundError:
        raise RuntimeError(NOT_BUILT)
    if not results:
        raise RuntimeError(NOT_BUILT)
    
        # Format Azure results for the banking API.
    hits = []

    for result in results:
        rerank = result.get("@search.reranker_score")
        fused = result.get("@search.score")

        hits.append({
            "id": result["doc_id"],
            "chunk_id": result["chunk_id"],
            "title": result["title"],
            "text": result["text"],
            "score": rerank if rerank is not None else fused,
            "rerank_score": rerank,
            "rrf": round(fused, 5),
        })

    return hits
    