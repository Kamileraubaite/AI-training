
"""The /knowledge/ask flow as a LangGraph graph.

    START -> retrieve -> gate -+-> answer -> check -> END
                               |
                               +-> refuse --------> END

Each node does one job and returns only what it changes.
"""

from typing import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

import context, gate, grounding
import knowledge_store as knowledge
import lc_model, llm


REFUSAL_REASON = "No document in the corpus is relevant to that question."


class AskState(TypedDict, total=False):
    question: str
    top_k: int
    cosine_floor: float
    rerank_floor: float
    hits: list[dict]
    usable: list[dict]
    answer: str
    input_tokens: int
    output_tokens: int
    stop_reason: str
    result: dict


def retrieve(state: AskState) -> AskState:
    return {"hits": knowledge.search(state["question"], state["top_k"])}


def apply_gate(state: AskState) -> AskState:
    usable = [
        hit for hit in state["hits"]
        if gate.is_usable(hit, state["cosine_floor"], state["rerank_floor"])
    ]
    return {"usable": usable}


# This is a conditional edge, not a node.
# It chooses whether to answer or refuse.
def after_gate(state: AskState) -> str:
    return "answer" if state["usable"] else "refuse"
