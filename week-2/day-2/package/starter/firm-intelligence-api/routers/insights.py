from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import StreamingResponse

import llm
from routers.firms import get_firms_or_404

router = APIRouter(prefix="/firms", tags=["insights"])

# create a post enpoint for /firms/{firm_id}/summary
# it should take in a firm and find it (or not...)
# try to make the llm call to get a summary of the call
    # if unsuccessful raise an appropriate Error and status code



# added a post endpoint for /firms/{firm_id}/summary.
@router.post("/{firm_id}/summary")
# used the Depends feature to get the firm or raise a 404 if the firm doesnt exist
def get_firm_summary(firm: dict = Depends(get_firms_or_404)):
    try:
        # call the llm.summarise_firm function to get a summary of the firm
        summary = llm.summarise_firm(firm)
        return summary
    # catch any errors from the llm call and raise a 503 error with the error message
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Summary provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Summary provider rate limited")
    except APIStatusError:
        raise HTTPException(status_code=502, detail="Summary provider unavailable")
# also added insights router to main.py, so FastAPI can register the new endpoint
# Finally, ran the FastAPI server and tested the endpoint.

@router.get("/{firm_id}/summary/estimate")
def estimate(firm: dict = Depends(get_firms_or_404)):
    return {
        "id": firm["id"],
        "estimated_input_tokens": llm.estimate_input_tokens(firm),
        "model": llm.MODEL
    }


# curl http://127.0.0.1:8000/firms/1/summary/estimate to run to see the new get command

@router.get("/{firm_id}/summary/stream")
def stream_summary(firm: dict = Depends(get_firms_or_404)):
    return StreamingResponse(
        llm.stream_firm_summary(firm), 
        media_type="text/plain",
        )

# endpoint challenge
# POST endpoint at firms/firm_id/analysis
# tries to analyse firm... if not, raises appropriate exceptions(s)

@router.post("/{firm_id}/analyse")
def analyse_firm(firm: dict = Depends(get_firms_or_404)):
    try:
        analysis = llm.analyse_firm(firm)
        return analysis
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Analysis provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Analysis provider rate limited")
    except APIStatusError:
        raise HTTPException(status_code=502, detail="Analysis provider unavailable")
        
# curl -X POST http://127.0.0.1:8000/firms/1/analysis



"""
Wraps an Anthropic API call with:
  1. Exponential backoff retries (for rate limits / transient errors)
  2. Cost logging in USD, based on token usage
 
Requires: pip install anthropic
"""
 
import logging
import random
import time
 
import anthropic
 
logger = logging.getLogger("anthropic_client")
logging.basicConfig(level=logging.INFO)
 
# Prices are per 1M tokens (input, output). Update this table as Anthropic's
# pricing page changes — https://docs.claude.com/en/docs/about-claude/pricing
PRICING_PER_MTOK = {
    "claude-opus-5": (5.00, 25.00),
    "claude-sonnet-5": (3.00, 15.00),
    "claude-haiku-4-5-20251001": (1.00, 5.00),
}
 
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 529}
 
 
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return the USD cost of a call given its token usage."""
    if model not in PRICING_PER_MTOK:
        logger.warning("No pricing entry for model '%s'; cost logged as $0.00", model)
        return 0.0
    in_price, out_price = PRICING_PER_MTOK[model]
    return (input_tokens / 1_000_000) * in_price + (output_tokens / 1_000_000) * out_price
 
 
def call_with_retry_and_cost(
    client: anthropic.Anthropic,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    **create_kwargs,
):
    """
    Calls client.messages.create(**create_kwargs) with exponential backoff,
    and logs the dollar cost of the call once it succeeds.
 
    Backoff: delay = min(max_delay, base_delay * 2**attempt) + random jitter.
    Retries on rate limits (429), server errors (5xx), and connection errors.
    Raises the last exception if all retries are exhausted.
    """
    last_exception = None
 
    for attempt in range(max_retries + 1):
        try:
            response = client.messages.create(**create_kwargs)
 
            usage = response.usage
            cost = calculate_cost(
                model=create_kwargs.get("model", ""),
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
            )
            logger.info(
                "API call succeeded (model=%s, in=%d tok, out=%d tok, cost=$%.6f)",
                create_kwargs.get("model", "unknown"),
                usage.input_tokens,
                usage.output_tokens,
                cost,
            )
            return response
 
        except (anthropic.RateLimitError, anthropic.APIStatusError, anthropic.APIConnectionError) as e:
            last_exception = e
            status_code = getattr(e, "status_code", None)
 
            is_retryable = isinstance(e, (anthropic.RateLimitError, anthropic.APIConnectionError)) or (
                status_code in RETRYABLE_STATUS_CODES
            )
 
            if not is_retryable or attempt == max_retries:
                logger.error("API call failed permanently: %s", e)
                raise
 
            delay = min(max_delay, base_delay * (2**attempt)) + random.uniform(0, 1)
            logger.warning(
                "API call failed (attempt %d/%d): %s — retrying in %.1fs",
                attempt + 1,
                max_retries + 1,
                e,
                delay,
            )
            time.sleep(delay)
 
    raise last_exception
 
 
if __name__ == "__main__":
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
 
    response = call_with_retry_and_cost(
        client,
        model="claude-sonnet-5",
        max_tokens=200,
        messages=[{"role": "user", "content": "Say hello in one sentence."}],
    )
    print(response.content[0].text)
