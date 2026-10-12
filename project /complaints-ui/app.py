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

# Search supporting documents without generating an AI answer.
with search_tab:
    st.subheader("Search documents")
    st.write("Find relevant documents without asking the AI to write an answer.")

    with st.form("search_form"):
        search_question = st.text_input(
            "Search question",
            placeholder="What evidence should staff check for a disputed mortgage fee?",
        )

        top_k = st.slider(
            "Maximum number of results",
            min_value=1,
            max_value=8,
            value=3,
        )

        search_submitted = st.form_submit_button("Search")

        # Retrieve documents and display every result returned by the API.
    if search_submitted:
        search_question = search_question.strip()

        if not search_question:
            st.warning("Please enter a search question.")
        else:
            try:
                with st.spinner("Searching documents..."):
                    response = httpx.post(
                        f"{API_URL}/knowledge/search",
                        json={
                            "question": search_question,
                            "top_k": top_k,
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    data = response.json()

                results = data["results"]

                if not isinstance(results, list):
                    raise ValueError("Expected a list of documents.")

                if not results:
                    st.info("No documents were returned for this question.")
                else:
                    st.caption(f"{len(results)} document(s) returned.")
                    st.caption(
                        "Scores measure similarity, not confidence "
                        "that a document answers your question."
                    )

                    for document in results:
                        st.markdown(f"**{document['title']}**")
                        st.caption(
                            f"Document: {document['id']} | "
                            f"Score: {document['score']:.3f}"
                        )
                        st.write(document["text"])
                        st.divider()

            except httpx.HTTPStatusError as exc:
                # An unbuilt index needs a different message from other failures.
                if exc.response.status_code == 409:
                    st.warning(
                        "The document index is not ready. "
                        "Build it using POST /knowledge/index, then search again."
                    )
                else:
                    show_http_error(exc.response.status_code)

            except httpx.TimeoutException:
                st.error("The document search timed out. Please try again.")

            except httpx.RequestError:
                st.error(
                    "Could not communicate with the API. "
                    "Check that FastAPI is running on port 8000."
                )

            except (ValueError, KeyError, TypeError):
                st.error("The search API returned an unexpected response.")

# Load complaint records so staff can select one to summarise.
with summary_tab:
    st.subheader("Complaint summary")
    st.write("Stream a draft complaint summary as it is generated.")

    complaint_options: list[dict] = []
    complaints_load_error = None

    try:
        response = httpx.get(f"{API_URL}/complaints", timeout=10.0)
        response.raise_for_status()
        complaint_options = response.json()

        if not isinstance(complaint_options, list):
            raise ValueError("Expected a list of complaints.")

    except httpx.RequestError:
        complaints_load_error = "Could not reach the API to load complaints."

    except httpx.HTTPStatusError as exc:
        complaints_load_error = (
            f"Loading complaints failed with HTTP status "
            f"{exc.response.status_code}."
        )

    except (ValueError, TypeError):
        complaints_load_error = "The complaints API returned an unexpected response."

    if complaints_load_error:
        st.warning(complaints_load_error)

    # Select a complaint or enter its ID if the list is unavailable.
    with st.form("summary_form"):
        if complaint_options:
            selected_complaint = st.selectbox(
                "Complaint",
                options=complaint_options,
                format_func=lambda complaint: (
                    f"{complaint['id']} — {complaint['theme']}"
                ),
            )
            complaint_id = (
                selected_complaint["id"] if selected_complaint else None
            )
        else:
            complaint_id = st.text_input(
                "Complaint ID",
                placeholder="CMP-001",
            )

        summary_submitted = st.form_submit_button("Get summary")


    # Display the draft summary as text arrives from the API.
    if summary_submitted:
        complaint_id = (complaint_id or "").strip()

        if not complaint_id:
            st.warning("Please enter a complaint ID.")
        else:
            summary_placeholder = st.empty()
            summary_text = ""

            try:
                with httpx.stream(
                    "GET",
                    f"{API_URL}/insights/{complaint_id}/summary/stream",
                    timeout=120.0,
                ) as response:
                    if response.status_code == 404:
                        st.error(f"No complaint with ID {complaint_id}.")

                    elif response.status_code >= 400:
                        show_http_error(response.status_code)

                    else:
                        for chunk in response.iter_text():
                            if chunk:
                                summary_text += chunk
                                summary_placeholder.markdown(summary_text)

                        if not summary_text:
                            st.info("The API did not return any summary text.")

            except httpx.TimeoutException:
                st.error("The summary stream timed out. Please try again.")

            except httpx.RequestError:
                st.error(
                    "Could not communicate with the API. "
                    "Check that FastAPI is running on port 8000."
                )