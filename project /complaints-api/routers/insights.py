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
    
# Stream a draft complaint summary as its text becomes available.
@router.get("/{complaint_id}/summary/stream")
def stream_summary(
    complaint: dict = Depends(get_complaint_or_404),
):
    chunks = llm.stream_complaint_summary(complaint)

    # Read the first chunk before responding, because the status code
    # cannot be changed once streaming has started.
    try:
        first = next(chunks, "")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Claude request timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Claude rate limit reached")
    except (APIConnectionError, APIStatusError):
        raise HTTPException(status_code=502, detail="Claude service unavailable")

    # Send the first chunk, then the rest. A failure part-way through
    # ends the text with a visible marker instead of a silent cut-off.
    def body():
        yield first
        try:
            yield from chunks
        except (APIConnectionError, APIStatusError, APITimeoutError, RateLimitError):
            yield "\n\n[Summary interrupted: Claude service error]"

    return StreamingResponse(body(), media_type="text/plain")

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