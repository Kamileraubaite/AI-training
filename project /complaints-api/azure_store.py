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

NOT_BUILT = "The azure index is empty or missing. Build it with python -m azure_build"

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

# Find identifiers containing numbers, such as PRD-003
def _identifiers(text: str) -> set[str]:
    return {token for token in bm25.tokenize(text) if any(ch.isdigit() for ch in token)}

def count() -> int:
    try:
        return search_client().search(search_text="*", include_total_count=True, top=0).get_count()
    except ResourceNotFoundError:
        return 0

def search_with_vector(question: str, query_vector: list[float], top_k: int = 3, semantic: bool = True) -> list[dict]:
    search_text = " ".join(bm25.tokenize(question)) or "*"

    options = {
        "search_text": search_text,
        "vector_queries": [VectorizedQuery(vector=query_vector, k_nearest_neighbors=CANDIDATES, fields="embedding")],
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
    wanted = _identifiers(question)
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
            "exact_match": bool(wanted & set(bm25.tokenize(result["text"]))),
        })

    return hits

def _local_chunks(strategy:str) -> list[dict]:
    
    chunk_index.build(strategy)

    stored = chunk_index.collection_for(strategy).get(include=["embeddings", "documents", "metadatas"])

    return [
        {
            "chunk_key": azure_index.key_for(chunk_id),
            "chunk_id": chunk_id,
            "doc_id": meta["doc_id"],
            "title": meta["title"],
            "text": text,
            "embedding": [float(number) for number in vector],
        }
        for chunk_id, vector, text, meta in zip(stored["ids"], stored["embeddings"], stored["documents"], stored["metadatas"])
    ]
def _wait_until_counted(expected: int, seconds:int = 30) -> None:
    """
    New documents become searchable a moment after upload, so we wait for the countto catchup
    """
    deadline = time.time() + seconds
    while time.time() < deadline:
        if count() >= expected:
            return
        time.sleep(1)
    raise RuntimeError(f"Uploaded {expected} chunks, butthe index reports {count()} after {seconds} seconds")

def build_index(strategy: str) -> int:
    """
    Drop and recreate the Azure index... then load every chunk.... return chunk count
    """
    docs = _local_chunks(strategy)
    keys = [doc["chunk_key"] for doc in docs]
    if len(set(keys)) != len(keys):
        # the ids of doc-1#01 and doc-1_01 would both become doc-1_01
        raise RuntimeError("Two chunk ids turn into the same Azure key, so chunks would overwrite each other. ")
    # check the vector sizes
    bad = [doc for doc in docs if len(doc["embedding"]) != azure_index.DIMENSIONS]
    if bad:
        raise RuntimeError(f"{bad[0]['chunk_id']} has {len(bad[0]['embedding'])} numbers per vector, but the index expects {azure_index.DIMENSIONS}. Did the embedding model change?")
    
    name = settings.AZURE_SEARCH_INDEX
    try:
        index_client().delete_index(name)
    except ResourceNotFoundError:
        pass
    index_client().create_index(azure_index.index_definition(name))

    for start in range(0, len(docs), BATCH):
        results = search_client().upload_documents(documents=docs[start:start+BATCH])
        failed = [result for result in results if not result.succeeded]
        if failed:
            raise RuntimeError(f"Azure rejected {len(failed)} chunks. First: {failed[0].key}: {failed[0].error_message}")
        
    # wait, then report 
    _wait_until_counted(len(docs))
    return len(docs)
    