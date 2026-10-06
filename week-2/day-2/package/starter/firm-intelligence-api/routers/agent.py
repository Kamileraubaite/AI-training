from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

import logging  # CHANGED: WAS A HALF-TYPED "im" LINE THAT CRASHED THE WHOLE APP
import agent

# CHANGED: logger WAS USED BELOW BUT NEVER CREATED
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])

class AgentQuestion(BaseModel):
    # Remove spaces at the beginning and end before validation.
    model_config = ConfigDict(str_strip_whitespace=True)

    # Reject missing, empty or whitespace-only questions.
    question: str = Field(min_length=1)

@router.post("/ask")
def ask(q: AgentQuestion) -> dict:
    """Send a validated question to the agent and return its result."""
    try:
        # Return the agent's dictionary unchanged.
        return agent.ask_with_tools(q.question)

    # Check timeout before connection errors because it is a subtype.
    except APITimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="The AI provider timed out. Please try again.",
        ) from exc

    except RateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail="The AI provider's rate limit was reached. Try again later.",
        ) from exc

    except APIStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI provider could not complete the request.",
        ) from exc

    except Exception as exc:
        # Give the caller a controlled JSON error, not a bare crash.
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the question.",
        ) from exc