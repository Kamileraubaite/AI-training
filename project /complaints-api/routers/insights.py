from fastapi import APIRouter, Depends, HTTPException
from anthropic import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

import llm
from routers.complaints import get_complaint_or_404

router = APIRouter(prefix="/insights", tags=["insights"])


# Generate a draft summary for an existing complaint.
@router.post("/{complaint_id}/summary")
def summarise(
    complaint: dict = Depends(get_complaint_or_404),
) -> dict:
    try:
        return llm.summarise_complaint(complaint)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Claude request timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Claude rate limit reached")
    except (APIConnectionError, APIStatusError):
        raise HTTPException(status_code=502, detail="Claude service unavailable")