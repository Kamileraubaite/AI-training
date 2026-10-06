from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from voyageai.error import RateLimitError, Timeout, VoyageError

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
