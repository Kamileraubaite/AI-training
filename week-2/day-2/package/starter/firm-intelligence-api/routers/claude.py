import anthropic, inspect
c = anthropic.Anthropic(api_key="anything")

# Does the method it called actually exist?
print([m for m in dir(c.messages) if not m.startswith("_")])

# Does every parameter it used actually exist?
print(list(inspect.signature(c.messages.create).parameters))

# Does every field it reads off the response actually exist?
from anthropic.types import Message
print(list(Message.model_fields))





Anthropic retry with cost · PY
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
