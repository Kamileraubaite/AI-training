"""Persistent Chroma storage and search... nothing in here knows about FastAPI"""

import os

import chromadb

from documents import DOCUMENTS
from knowledge import embed_texts

chroma = chromadb.PersistentClient(path=os.environ.get("CHROMA_PATH", "./chroma_store"))

# cosine is set explicitly because Chroma's default is a different distance
collection = chroma.get_or_create_collection(
    name="complaint_documents",
    configuration={"hnsw": {"space": "cosine"}},
)

def count() -> int:
    return collection.count()

# Embed every document and hand the vectors to Chroma.
# upsert (not add) so running this twice overwrites instead of failing or duplicating.
def build_index() -> int:
    texts = [doc["body"] for doc in DOCUMENTS]
    vectors, tokens = embed_texts(texts, input_type="document")

    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        embeddings=vectors,
        documents=texts,
        metadatas=[
            {"title": doc["title"], "type": doc["type"], "date": doc["date"]}
            for doc in DOCUMENTS
        ],
    )
    return tokens

# Embed the question and let Chroma find the closest documents.
# Chroma returns distance (lower is closer), so score = 1 - distance (higher is closer).
def search(question: str, top_k: int = 3) -> list[dict]:
    # Stop with a clear error if nothing has been indexed yet
    if collection.count() == 0:
        raise RuntimeError("Index is empty. Call build_index() first.")

    query_vectors, _ = embed_texts([question], input_type="query")

    result = collection.query(query_embeddings=query_vectors, n_results=top_k)

    return [
        {
            "id": doc_id,
            "title": metadata["title"],
            "text": text,
            "score": 1 - distance,
        }
        for doc_id, text, metadata, distance in zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]
