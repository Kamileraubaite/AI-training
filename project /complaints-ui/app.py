import httpx
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Banking Complaints Intelligence", layout="wide")
st.title("Banking Complaints Intelligence")

ask_tab, search_tab, summary_tab, triage_tab = st.tabs(
    ["Ask the agent", "Search documents", "Complaint summary", "Complaint triage"]
)


# ---------------------------------------------------------
# Shared error handling
# ---------------------------------------------------------


# Show clear messages when an API request fails.
def show_http_error(status_code: int) -> None:
    messages = {
        422: "The API rejected the input. Please check what you entered.",
        429: "The AI provider's rate limit was reached. Try again later.",
        502: "The AI provider is unavailable or could not complete the request.",
        504: "The AI provider timed out. Please try again.",
    }

    st.error(
        messages.get(
            status_code,
            f"The request failed with HTTP status {status_code}.",
        )
    )


# ---------------------------------------------------------
# Feature 1: Ask the agent
# ---------------------------------------------------------

# Collect a question for the complaints agent.
with ask_tab:
    st.subheader("Ask a question")

    with st.form("ask_form"):
        question = st.text_input(
            "Your question",
            placeholder=(
                "For CMP-001, what guidance and historic complaints "
                "should staff review?"
            ),
        )
        ask_submitted = st.form_submit_button("Ask")

     # Send the submitted question to the API and display the result.
    if ask_submitted:
        question = question.strip()

        if not question:
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("The agent is working..."):
                    response = httpx.post(
                        f"{API_URL}/agent/ask",
                        json={"question": question},
                        timeout=120.0,
                    )
                    response.raise_for_status()
                    result = response.json()

                if not isinstance(result, dict):
                    raise ValueError("Expected a dictionary.")

                answer = result["answer"]
                completed = result["completed"]
                tool_calls = result["tool_calls_made"]
                input_tokens = result["input_tokens"]
                output_tokens = result["output_tokens"]

                if completed:
                    st.markdown(answer)
                else:
                    st.warning(
                        "The agent did not finish answering. "
                        "It may have reached its iteration or output limit. "
                        "Try a more specific question."
                    )
                    if answer:
                        st.markdown(answer)

                # Display tool calls and token usage for this request.
                tools_col, input_col, output_col = st.columns(3)
                tools_col.metric("Tool calls", tool_calls)
                input_col.metric("Input tokens", input_tokens)
                output_col.metric("Output tokens", output_tokens)

            except httpx.TimeoutException:
                st.error("The UI timed out waiting for the API.")

            except httpx.HTTPStatusError as exc:
                show_http_error(exc.response.status_code)

            except httpx.RequestError:
                st.error(
                    "Could not communicate with the API. "
                    "Check that FastAPI is running on port 8000."
                )

            except (ValueError, KeyError, TypeError):
                st.error("The agent API returned an unexpected response.")