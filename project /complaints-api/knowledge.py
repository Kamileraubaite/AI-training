"""Embedding mechanics... nothing in here knows about FastAPI"""

import math
import os

import voyageai

# The Voyage AI embedding model we are using
EMBED_MODEL = os.environ.get("EMBED_MODEL", "voyage-3-lite")

# Create a Voyage AI client so we can use the embedding API
voyage = voyageai.Client(
    api_key=os.environ["VOYAGE_API_KEY"],
    max_retries=3,
    timeout=30,
)


# Convert a list of text strings into embedding vectors.
# input_type tells Voyage whether these are documents or a query.
def embed_texts(texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    result = voyage.embed(texts=texts, model=EMBED_MODEL, input_type=input_type)

    # Return the embedding vectors and the number of tokens used
    return result.embeddings, result.total_tokens

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    return dot / (norm_a * norm_b) 
