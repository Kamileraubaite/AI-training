"""Embedding and retrieval mechanics... nothing in here will know about FastAPI"""

import math
import os

import voyageai

# Import the documents that we want to search through
from documents import DOCUMENTS 

# The voyage AI embedding model we are using
EMBED_MODEL = "voyage-3-lite"


# Create a Voyage AI client so we can use the embedding API
voyage = voyageai.Client(
    # Get the API key from the environment variable VOYAGE_API_KEY
    api_key=os.environ["VOYAGE_API_KEY"],
    # Retry the request up to 3 times if it fails
    max_retries=3,
    # Stop waiting for a response after 3 seconds
    timeout=3
)

def count() -> int:
    return len(INDEX)


# Stores our documents and their embedding vectors in memory
# the in-memory index... a list of dicts (exactly like FIRMS last week.)
# Each item in INDEX will be a dictionary
INDEX: list[dict] = []


#------------------------------------------------------------------------------

"""Convert a list of text strings into embedding vectors."""
def embed_texts(texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    
    # Send the text to Voayage AI and create embeddings
    # # input_type: tells Voyage whether these are docs or a query
    result = voyage.embed(texts=texts, model=EMBED_MODEL, input_type=input_type)
    
    # returns the embedding vectors and the number of tokens used
    return result.embeddings, result.total_tokens

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """How close are two vectors in direction, ignoring their length 
    1.0 means identical direction
    0.0 means unrelated
    -1.0 means opposite direction
    """

    # Multiply matching values in the two vectors and add them together
    # This calculated the dot product

    dot = sum(x * y for x, y in zip(a, b))
    # Clculate the length(magnitude) of each vector
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    # Divide the dot product by the lengths of both vectors
    # A higher result means the vectors are more similar
    return dot / (norm_a * norm_b)

def build_index() -> int:
    """Embed every document once and hold the vectors in memory"""

    # Remove anything that was previously stored in INDEX
    INDEX.clear()

    # Get the body text from every document
    texts = [doc["body"] for doc in DOCUMENTS]

    # Turn all document bodies into embedding vectors
    vectors, tokens = embed_texts(texts, input_type="document")

    # Match each document with its embedding vectors
    for doc, vector in zip(DOCUMENTS, vectors):

        # Store the document with its embedding vector in the INDEX
        INDEX.append({
            "id": doc["id"],
            "title": doc["title"],
            "text": doc["body"],
            "vector": vector
        })
    return tokens
        # Return how many tokens were used in the embeddings

# Search the prepared index using a question            
def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question... then score it against everything in the index"""
    # top_k controls how many results we return
    # If no value is supplied, it defaults to 3

    # An empty list is treated as False
    # Stop with a helpful error if the index has no documents
    if not INDEX:
        raise RuntimeError("Index is empty. Call build_index() first.")
    
     # Put the question inside a list because embed_texts expects one
    # "_" holds the token count, which we do not need here
    query_vectors, _ = embed_texts([question], input_type="query")

     # The result is a list of vectors
    # We sent one question, so take its vector at position 0
    query_vector = query_vectors[0]

    # Build a new list containing one result dictionary per document
    # "entry" refers to each dictionary already stored in INDEX
    scored = [
        {
            "id": entry["id"],
            "title": entry["title"],
            # Use "body" because that is the key stored in the index
            "text": entry["text"],
            # Compare the question vector with this document's vector
            # Store the resulting similarity score with the document
            "score": cosine_similarity(query_vector, entry["vector"])
        }
        for entry in INDEX
    ]
    # Rank the results by their similarity scores
# sort() rearranges this list in place
# lambda item: item["score"] tells Python to sort by the score
# reverse=True puts the highest scores first

    scored.sort(key=lambda item: item["score"], reverse=True)
    # STEP 6: Return the first top_k results

    # With top_k=3, [:3] returns positions 0, 1 and 2
    # By contrast, [3] would return only the fourth result
    return scored[:top_k]



## pa-1oIWqfTqEKg28GX73igoRMGvprYshZPWN057ay6qoAU