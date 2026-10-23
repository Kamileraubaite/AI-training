from functools import lru_cache
from langchain_anthropic import ChatAnthropic
import llm

# Create a LangChain version of our Claude model.
@lru_cache
def chat_model(max_tokens: int = 500) -> ChatAnthropic:
    return ChatAnthropic(
        model=llm.MODEL,
        max_tokens=max_tokens,
        timeout=30,
        max_retries=3,
    )