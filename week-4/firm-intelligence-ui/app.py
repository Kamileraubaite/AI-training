import streamlit as st
import httpx

API_URL = "http://127.0.0.1:8000"


# Each function calls one of our existing API endpoints.
# Nothing here runs the agent or searches Chroma directly.

def ask_agent(question: str) -> dict:
    response = httpx.post(
        f"{API_URL}/agent/ask",
        json={"question": question},
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()


def search_documents(question: str) -> dict:
    response = httpx.post(
        f"{API_URL}/knowledge/search",
        json={"question": question, "top_k": 3},
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()


def get_firms() -> list[dict]:
    response = httpx.get(
        f"{API_URL}/firms",
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def stream_summary(firm_id: int):
    # Yield each piece of text as it arrives.
    # This follows the same pattern as your llm.stream_firm_summary().
    with httpx.stream(
        "GET",
        f"{API_URL}/firms/{firm_id}/summary/stream",
        timeout=120.0,
    ) as response:
        response.raise_for_status()

        for text in response.iter_text():
            yield text


def show_http_error(status: int) -> None:
    # Similar to the error mapping in your API routers.
    if status == 429:
        st.error("Rate limit reached. Try again later.")
    elif status == 504:
        st.error("The provider timed out.")
    elif status == 502:
        st.error("The provider is unavailable.")
    elif status == 404:
        st.error("The firm or endpoint was not found.")
    elif status == 422:
        st.error("Please check the information you entered.")
    else:
        st.error(f"The request failed. Status code: {status}")


st.title("Firm Intelligence")

ask_tab, search_tab, summary_tab = st.tabs(
    ["Ask", "Search only", "Firm summary"]
)


# --------------------------------------------------
# FEATURE 1 — Ask the agent
# --------------------------------------------------

with ask_tab:
    question = st.text_input("Type your question")

    if st.button("Ask"):
        if not question.strip():
            st.warning("Please enter a question.")

        else:
            try:
                with st.spinner("Finding an answer..."):
                    result = ask_agent(question.strip())

                if result["completed"]:
                    st.write(result["answer"])

                elif result["stop_reason"] == "iteration_limit":
                    st.warning(
                        "The agent reached its limit. "
                        "Try a more specific question."
                    )

                else:
                    st.warning("The agent did not finish its answer.")

                st.write("Tool calls:", result["tool_calls_made"])
                st.write("Input tokens:", result["input_tokens"])
                st.write("Output tokens:", result["output_tokens"])

            except httpx.TimeoutException:
                st.error("The request took too long.")

            except httpx.HTTPStatusError as e:
                show_http_error(e.response.status_code)

            except httpx.RequestError:
                st.error("Could not reach the API. Check it is running.")

            except (ValueError, KeyError, TypeError):
                st.error("The API returned an unexpected answer format.")


# --------------------------------------------------
# FEATURE 2 — Search without generating an answer
# --------------------------------------------------

with search_tab:
    question = st.text_input("Search the documents")

    if st.button("Search"):
        if not question.strip():
            st.warning("Please enter a search question.")

        else:
            try:
                with st.spinner("Searching..."):
                    result = search_documents(question.strip())

                if not result["results"]:
                    st.info("No documents were returned.")

                # Loop through every result returned by the API.
                for document in result["results"]:
                    st.write(document["title"])
                    st.write("Score:", round(document["score"], 3))
                    st.write(document["text"])

            except httpx.TimeoutException:
                st.error("The search took too long.")

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 409:
                    st.warning("The index is not ready. Build it first.")
                else:
                    show_http_error(e.response.status_code)

            except httpx.RequestError:
                st.error("Could not reach the API. Check it is running.")

            except (ValueError, KeyError, TypeError):
                st.error("The API returned an unexpected search format.")


# --------------------------------------------------
# FEATURE 3 — Stream a firm summary
# --------------------------------------------------

with summary_tab:
    try:
        # Read the current firms from your API.
        firms = get_firms()
        firm_ids = [firm["id"] for firm in firms]

        if not firm_ids:
            st.info("No firms are available.")

        else:
            firm_id = st.selectbox("Choose a firm ID", firm_ids)

            if st.button("Get summary"):
                summary = ""
                summary_area = st.empty()

                with st.spinner("Writing the summary..."):
                    for text in stream_summary(firm_id):
                        summary += text
                        summary_area.write(summary)

                if not summary.strip():
                    st.warning("No summary text was returned.")

    except httpx.TimeoutException:
        st.error(
            "The request timed out. "
            "Any summary text shown may be incomplete."
        )

    except httpx.HTTPStatusError as e:
        show_http_error(e.response.status_code)

    except httpx.RequestError:
        st.error(
            "The connection failed. Check the API is running. "
            "Any summary text shown may be incomplete."
        )

    except (ValueError, KeyError, TypeError):
        st.error("The API returned an unexpected firm list.")