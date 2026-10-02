from fastapi import APIRouter, Depends, HTTPException
from anthropic import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from fastapi.responses import StreamingResponse

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
    
# Estimate the input tokens required for a complaint summary.
@router.get("/{complaint_id}/summary/estimate")
def estimate(
    complaint: dict = Depends(get_complaint_or_404),
) -> dict:
    try:
        return {
            "id": complaint["id"],
            "estimated_input_tokens": llm.estimate_input_tokens(complaint),
            "model": llm.MODEL,
        }
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Claude request timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Claude rate limit reached")
    except (APIConnectionError, APIStatusError):
        raise HTTPException(status_code=502, detail="Claude service unavailable")
    
# Stream a draft complaint summary as its text becomes available.
@router.get("/{complaint_id}/summary/stream")
def stream_summary(
    complaint: dict = Depends(get_complaint_or_404),
):
    return StreamingResponse(
        llm.stream_complaint_summary(complaint),
        media_type="text/plain",
    )

# Generate structured complaint analysis for staff review.
@router.post("/{complaint_id}/analyse")
def analyse(
    complaint: dict = Depends(get_complaint_or_404),
) -> dict:
    try:
        return llm.analyse_complaint(complaint)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Claude request timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Claude rate limit reached")
    except (APIConnectionError, APIStatusError):
        raise HTTPException(status_code=502, detail="Claude service unavailable")