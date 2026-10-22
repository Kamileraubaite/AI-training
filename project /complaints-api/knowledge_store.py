"""Persistent Chroma storage and search... nothing in here knows about FastAPI"""

import knowledge
import chunk_index
import hybrid 


# Chosen chunking strategy

CHUNK_STRATEGY = "sections_contextual"
SEARCH_MODE = "hybrid"

# chroma = chromadb.PersistentClient(path=os.environ.get("CHROMA_PATH", "./chroma_store"))

# # cosine is set explicitly because Chroma's default is a different distance
# collection = chroma.get_or_create_collection(
#     name="complaint_documents",
#     configuration={"hnsw": {"space": "cosine"}},
# )

def count() -> int:
    return chunk_index.collection_for(CHUNK_STRATEGY).count()

# Embed every document and hand the vectors to Chroma.
# upsert (not add) so running this twice overwrites instead of failing or duplicating.
def build_index() -> int:
    return chunk_index.build(CHUNK_STRATEGY)["embedding_tokens"]

# Embed the question and let Chroma find the closest documents.
# Chroma returns distance (lower is closer), so score = 1 - distance (higher is closer).
def search(question: str, top_k: int = 3) -> list[dict]:
    # Stop with a clear error if nothing has been indexed yet
    if count() == 0:
        raise RuntimeError("Index is empty. Call POST /knowledge/index first.")

    query_vectors, _ = knowledge.embed_texts([question], input_type="query")

    if SEARCH_MODE == "hybrid":
        return hybrid.search_with_vector(CHUNK_STRATEGY, question, query_vectors[0], top_k)
    return chunk_index.search_with_vector(CHUNK_STRATEGY, query_vectors, k=top_k)