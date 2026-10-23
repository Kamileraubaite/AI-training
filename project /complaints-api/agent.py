"""This is the tool-use loop"""

import knowledge_store as knowledge
from llm import MODEL, client
from data import COMPLAINTS, PRODUCTS

# Agent system prompt
# This tells the model how to behave and what rules to follow when answering
# These set of rules then guide the model, and the code controls the flow of the conversation

AGENT_SYSTEM_PROMPT = (
    "You are a banking complaints assistant with access to tools to search " 
    "a knowledge base and also find similar historic complaints. Use the tools" 
    "whenever a question needs supporting information you don't already have, do " 
    "not guess. Cite documents and complaint ID`s in your final answer. If the" 
    "tool returns nothing relevant or the provided evidence is insufficient, say so."
    "Do not invent compensation amounts or assume past complaint outcomes apply to a new case."
    "Your overall guidance is for staff review, not to provide a final decision." 
)

# Describe the document search tool and the input it requires
# This doesn't run the search
SEARCH_TOOL = {
    "name": "search_knowledge_base",
    "description": (
        "Search the banking knowledge base for complaint handling policies, "
        "product terms, customer support guidance and redress methodology."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query",
            },
        },
        "required": ["query"],
    },
}

# Describe the tool for finding similar resolved complaints
HISTORIC_COMPLAINT_TOOL = {
    "name": "find_similar_complaints",
    "description": (
        "Find similar resolved complaints for a complaint ID, "
        "using its recorded theme and product type. "
        "Past outcomes are comparisons, not decisions for the current complaint."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "complaint_id": {
                "type": "string",
                "description": "The complaint ID, for example CMP-001",
            },
        },
        "required": ["complaint_id"],
    },
}

# Limit the number of Claude calls made during one agent request
MAX_ITERATIONS = 4

# Run the agent until it answers or reaches the iteration limit
def ask_with_tools(question: str) -> dict:
    messages = [{"role": "user", "content": question}]
    total_input_tokens = 0
    total_output_tokens = 0
    tool_calls_made = 0

    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=AGENT_SYSTEM_PROMPT,
            tools=[SEARCH_TOOL, HISTORIC_COMPLAINT_TOOL],
            messages=messages,
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # Return the text when Claude stops requesting tools
        if response.stop_reason != "tool_use":
            final_text = next(
                (b.text for b in response.content if b.type == "text"), ""
            )

            return {
                "answer": final_text,
                "completed": response.stop_reason == "end_turn",
                "tool_calls_made": tool_calls_made,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "stop_reason": response.stop_reason,
            }

        # Add Claude's tool requests to the conversation
        tool_blocks = [b for b in response.content if b.type == "tool_use"]
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tool_block in tool_blocks:
            result_text, is_error = _execute_tool(
                tool_block.name, tool_block.input
            )
            if not is_error:
                tool_calls_made += 1

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_block.id,
                "content": result_text,
                "is_error": is_error,
            })

        # Send the tool results back to Claude
        messages.append({"role": "user", "content": tool_results})

    # Report that the agent reached its limit without completing
    return {
        "answer": "",
        "completed": False,
        "tool_calls_made": tool_calls_made,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "stop_reason": "max_iterations",
    }

# Execute document searches and return results or errors to the model
def _execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:

        # Find historic complaints when the model requests a comparison.
    if name == "find_similar_complaints":
        if "complaint_id" not in tool_input:
            return 'Error: missing required field "complaint_id"', True

        try:
            results = find_similar_complaints(tool_input["complaint_id"])
        except Exception as e:
            return f"Error: {e}", True

        if not results:
            return "No similar historic complaints found", False

        formatted = "\n\n".join(
            f"[{r['id']}] Theme: {r['theme']}\n"
            f"Description: {r['description']}\n"
            f"Outcome: {r['outcome']}\n"
            f"Resolution: {r['resolution_summary']}"
            for r in results
        )
        return formatted, False

    # guard 1 - checking the tool
    if name != "search_knowledge_base":
        return f"Unknown tool: {name}", True
    
    # quard 2 - the tool may be right but its useless without its one argument 
    if "query" not in tool_input:
        return 'Error: missing required field "query"', True

    try:
        results = knowledge.search(tool_input["query"], top_k=3)
    except Exception as e:
        return f"Error: {e}", True

    if not results:
        return "No relevant documents found", False

    formatted = "\n\n".join(
        f"[{r['id']}] {r['title']} (score {r['score']:.2f})\n{r['text']}"
        for r in results
    )
    return formatted, False


# Find resolved complaints with the same theme and product type.
def find_similar_complaints(complaint_id: str) -> list[dict]:
    complaint = next(
        (c for c in COMPLAINTS if c["id"] == complaint_id), None
    )
    if complaint is None:
        raise ValueError("Complaint not found")

    if complaint["theme"] == "unclassified":
        raise ValueError("Classify the complaint theme before comparing past cases")

    product_types = {
        p["id"]: p["product_type"] for p in PRODUCTS
    }
    product_type = product_types.get(complaint["product_id"])
    if product_type is None:
        raise ValueError("Complaint product not found")

    matches = [
        c for c in COMPLAINTS
        if c["id"] != complaint_id
        and c["status"] == "resolved"
        and c["theme"] == complaint["theme"]
        and product_types.get(c["product_id"]) == product_type
        and c["resolved_date"] is not None
        and c["resolved_date"] < complaint["received_date"]
    ]

    # Prefer the same product, then the most recently resolved cases.
    matches.sort(
        key=lambda c: (
            c["product_id"] == complaint["product_id"],
            c["resolved_date"],
        ),
        reverse=True,
    )
    return matches[:3]