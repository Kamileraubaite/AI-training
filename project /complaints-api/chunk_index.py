"""One Chroma collection per chunking strategy. """

import hashlib
import chromadb 

import chunking 
import knowledge 
from documents import DOCUMENTS

ALL_DOCS = DOCUMENTS

BATCH_SIZE = 128

chroma = chromadb.PersistentClient(path="./chroma_store")

# Give each strategy its own collection name.
def collection_name(strategy: str) -> str:
    return f"chunks_{strategy}"

# Open the strategy's collection, or create it if it does not exist.
def collection_for(strategy: str):
    return chroma.get_or_create_collection(
        name=collection_name(strategy),
        configuration={"hnsw": {"space": "cosine"}},
    )

# Embed chunks in batches and add up the token usage.
def embed_batched(texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    vectors: list[list[float]] = []
    tokens = 0

    for start in range(0, len(texts), BATCH_SIZE):
        batch_vectors, batch_tokens = knowledge.embed_texts(texts[start:start + BATCH_SIZE],input_type=input_type,)
        vectors.extend(batch_vectors)
        tokens += batch_tokens
    return vectors, tokens

# The fingerprint changes if the text, the model or the order changes... and stays put of nothing does. 
def fingerprint(chunks: list[dict]) -> str:
    # SHA-256 - A recipe that turns any text into a fixed-legth code (64 chars)
    digest = hashlib.sha256(knowledge.EMBED_MODEL.encode())
    for c in chunks:
        digest.update(f"{c['id']}\n{c['text']}\n".encode())
    return digest.hexdigest()[:16]  # first 16 chars is enough to detect changes

# Build the strategy's index only when its content or model has changed
def build(strategy: str, force: bool = False) -> dict:
    # pt 1
    chunks = chunking.chunk_corpus(ALL_DOCS, strategy)
    fp = fingerprint(chunks)
    col = collection_for(strategy)

    stored = col.get(limit=1, include=["metadatas"])["metadatas"]
    if not force and col.count() == len(chunks) and stored and stored[0].get("fingerprint") == fp:
        return {"strategy": strategy,"chunks": len(chunks),"embedding_tokens": 0,"rebuilt": False,}

    # Remove the previous collection before rebuilding
    try:
        chroma.delete_collection(name=collection_name(strategy))
    except Exception:
        pass

    col = collection_for(strategy)
    # Create embeddings for the banking document chunks
    vectors, tokens = embed_batched([c["text"] for c in chunks],input_type="document",)
    # Store each chunk with its source document and fingerprint
    col.upsert(
        ids=[c["id"] for c in chunks],
        embeddings=vectors,
        documents=[c["text"] for c in chunks],
        metadatas=[{"doc_id": c["doc_id"],"title": c["title"],"fingerprint": fp} for c in chunks]
    )
    return {"strategy": strategy,"chunks": len(chunks),"embedding_tokens": tokens,"rebuilt": True}

 # Search a strategy's index using question vectors already created.
def search_with_vector(strategy: str,query_vectors: list[list[float]],k: int) -> list[list[dict]]:
    col = collection_for(strategy)
    if col.count() == 0:
        raise RuntimeError(f"Index for '{strategy}' is empty. Please build it first.")

    results = col.query(query_embeddings=query_vectors,n_results=min(k, col.count()))

    return [
        [
            {"id": meta["doc_id"],"chunk_id": chunk_id,"title": meta["title"],"text": text,"score": 1 - distance}
            for chunk_id, text, meta, distance in zip(ids, docs, metas, dists)
        ]
        for ids, docs, metas, dists in zip(
        results["ids"],results["documents"],results["metadatas"],results["distances"],
        )
    ]

def cosine_for(strategy: str, query_vector: list[float], chunk_ids: list[str]) -> dict[str, float]:
    if not chunk_ids:
        return {}
    
    stored = collection_for(strategy).get(ids=chunk_ids, include=["embeddings", "metadatas"])

    return {
        chunk_id: float(knowledge.cosine_similarity(query_vector, list(vector)))
        for chunk_id, vector in zip(stored["ids"], stored["embeddings"])
    }
