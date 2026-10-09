from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from voyageai.error import RateLimitError, Timeout, VoyageError
import llm
import os
import anthropic
import grounding

# Minimum similarity required for a document to support an answer.
RELEVANCE_FLOOR = float(os.getenv("RELEVANCE_FLOOR", "0.45"))

import knowledge_store as knowledge

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# The question and how many results to return.
class Question(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=8)

# Embed every document and upsert it into Chroma.
@router.post("/index")
def rebuild_index() -> dict:
    try:
        tokens = knowledge.build_index()
    except Timeout:
        raise HTTPException(status_code=504, detail="Embedding provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Embedding provider rate limited")
    except VoyageError:
        raise HTTPException(status_code=502, detail="Embedding provider unavailable")

    return {"indexed": knowledge.count(), "embedding_tokens": tokens}

# Retrieval only: no Claude call, just what was found and how closely it matched.
@router.post("/search")
def search(q: Question) -> dict:
    try:
        results = knowledge.search(q.question, q.top_k)
    # Raised when nothing has been indexed yet, which is not the same as a provider failure.
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Timeout:
        raise HTTPException(status_code=504, detail="Embedding provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Embedding provider rate limited")
    except VoyageError:
        raise HTTPException(status_code=502, detail="Embedding provider unavailable")

    return {"question": q.question, "results": results}

# Retrieve relevant documents, then answer or refuse.
@router.post("/ask")
def ask(q: Question) -> dict:
    # Find documents relevant to the question.
    try:
        hits = knowledge.search(q.question, q.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Timeout:
        raise HTTPException(status_code=504, detail="Embedding provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Embedding provider rate limited")
    except VoyageError:
        raise HTTPException(status_code=502, detail="Embedding provider unavailable")

    # Keep only documents that meet the relevance floor.
    usable = [hit for hit in hits if hit["score"] >= RELEVANCE_FLOOR]

    # Refuse before calling Claude if no documents qualify.
    if not usable:
        return {
            "question": q.question,
            "answer": None,
            "refused": True,
            "reason": "No document in the corpus is relevant to that question.",
            "sources": [],
        }

    # Include document IDs so Claude can cite its evidence.
    context = "\n\n".join(f"[{h['id']}] {h['title']}\n{h['text']}" for h in usable)

    try:
        result = llm.answer_from_context(q.question, context)
    except anthropic.APITimeoutError:
        raise HTTPException(status_code=504, detail="Answer provider timed out")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Answer provider rate limited")
    except (anthropic.APIConnectionError, anthropic.APIStatusError):
        raise HTTPException(status_code=502, detail="Answer provider unavailable")

    # Return the answer, supporting sources and token usage.
    return {
        "question": q.question,
        "answer": result["answer"],
        "refused": False,
        "sources": [{"id": h["id"],"title": h["title"],"score": round(h["score"], 3),}for h in usable],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "stop_reason": result["stop_reason"],
        "grounding": grounding.check_citations(result["answer"],[h["id"] for h in usable],
),
    }