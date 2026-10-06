import httpx
import streamlit as st


# Your FastAPI backend runs separately at this address.
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Firm Intelligence", layout="wide")
st.title("Firm Intelligence")

# Put each feature in its own tab.
ask_tab, search_tab, summary_tab = st.tabs(
    ["Ask the agent", "Search documents", "Firm summary"]
)


# ---------------------------------------------------------
# Shared error handling
# ---------------------------------------------------------

def show_http_error(status_code: int) -> None:
    """Show a helpful message for an unsuccessful API response."""
    # These are the status codes our FastAPI routers deliberately raise
    # (see agent.py / insights.py) instead of letting an error crash through
    # as a bare 500, so we translate each one into plain English here.
    messages = {
        422: "The API rejected the input. Please check your question.",
        429: "The AI provider's rate limit was reached. Try again later.",
        502: "The AI provider is unavailable or could not complete the request.",
        504: "The AI provider timed out. Please try again.",
    }

    # .get() with a default means an unlisted status code (e.g. 500) still
    # shows something useful instead of a raw KeyError.
    st.error(
        messages.get(
            status_code,
            f"The request failed with HTTP status {status_code}.",
        )
    )


# ---------------------------------------------------------
# Feature 1: Ask the agent
# ---------------------------------------------------------

with ask_tab:
    st.subheader("Ask a question")

    # A form waits until the user presses Ask before submitting, so the API
    # isn't called on every keystroke — only once, when the button is pressed.
    with st.form("ask_form"):
        question = st.text_input(
            "Your question",
            placeholder="How is profit per equity partner calculated?",
        )
        ask_submitted = st.form_submit_button("Ask")

    # This whole block only runs on the render right after the button was
    # pressed. On every other render (e.g. switching tabs) it's skipped.
    if ask_submitted:
        question = question.strip()

        if not question:
            # Guard clause: don't bother calling the API with nothing to ask.
            st.warning("Please enter a question.")

        else:
            try:
                # The agent can take a while because it may call tools
                # (e.g. search) itself before answering, so we use a long
                # timeout and show a spinner while we wait.
                with st.spinner("The agent is working..."):
                    # Send the question to your real API.
                    response = httpx.post(
                        f"{API_URL}/agent/ask",
                        json={"question": question},
                        timeout=120.0,
                    )

                    # raise_for_status() turns a 4xx/5xx response into an
                    # exception, so a failed call jumps straight to the
                    # except blocks below instead of continuing with junk data.
                    response.raise_for_status()

                    # Convert the response JSON into a Python dictionary.
                    result = response.json()

                # Defensive check: if the API ever returned something that
                # isn't a JSON object (e.g. a bare string), fail loudly here
                # rather than crashing later on result["answer"].
                if not isinstance(result, dict):
                    raise ValueError("Expected a dictionary.")

                # Read the required fields before displaying the result. If
                # any key is missing, this raises KeyError, which is caught
                # below and shown as a clear error instead of a stack trace.
                answer = result["answer"]
                completed = result["completed"]
                tool_calls = result["tool_calls_made"]
                input_tokens = result["input_tokens"]
                output_tokens = result["output_tokens"]

                # "completed" is False when the agent hit its iteration or
                # output limit without finishing — the request still
                # succeeded (200 OK), it just didn't reach a final answer.
                if completed:
                    st.markdown(answer)
                else:
                    st.warning(
                        "The agent did not finish answering. "
                        "It may have reached its iteration or output limit. "
                        "Try a more specific question."
                    )

                    # Even an incomplete run may have produced partial
                    # useful text, so show it if there is any.
                    if answer:
                        st.markdown(answer)

                # The challenge requires showing tool call count and token
                # usage "somewhere on screen" — three metric columns side by
                # side is a simple way to surface all of it at once.
                tools_col, input_col, output_col = st.columns(3)

                tools_col.metric("Tool calls", tool_calls)
                input_col.metric("Input tokens", input_tokens)
                output_col.metric("Output tokens", output_tokens)

            # Order matters here: httpx.TimeoutException is a *subclass* of
            # httpx.RequestError, so it must be caught first, or the more
            # general RequestError branch below would swallow it and we'd
            # lose the more specific "it timed out" message.
            except httpx.TimeoutException:
                st.error(
                    "The UI timed out waiting for the API. "
                    "The backend may still be processing the question."
                )

            # Raised by response.raise_for_status() above for any 4xx/5xx.
            except httpx.HTTPStatusError as exc:
                show_http_error(exc.response.status_code)

            # Anything else that goes wrong at the network level (API not
            # running, DNS failure, connection refused, etc).
            except httpx.RequestError:
                st.error(
                    "Could not communicate with the API. "
                    "Check that FastAPI is running on port 8000."
                )

            # Catches the isinstance() check above, any missing dict key,
            # and any wrong type used where a string/int was expected — i.e.
            # "the API responded, but not in the shape we expected."
            except (ValueError, KeyError, TypeError):
                st.error(
                    "The agent API returned an unexpected response. "
                    "Check that it returns an answer, completed status, "
                    "tool_calls_made, input_tokens and output_tokens."
                )


# ---------------------------------------------------------
# Feature 2: Search without generating an answer
# ---------------------------------------------------------

with search_tab:
    st.subheader("Search documents")
    st.write("Find relevant documents without asking the AI to write an answer.")

    with st.form("search_form"):
        search_question = st.text_input(
            "Search question",
            placeholder="Which documents discuss partner compensation?",
        )

        # Your API's Question model validates top_k with ge=0, le=8, so the
        # slider is capped at 8 to match — the UI can't send a value the
        # backend would reject.
        top_k = st.slider(
            "Maximum number of results",
            min_value=1,
            max_value=8,
            value=3,
        )

        search_submitted = st.form_submit_button("Search")

    if search_submitted:
        search_question = search_question.strip()

        if not search_question:
            st.warning("Please enter a search question.")

        else:
            try:
                # This hits /knowledge/search, which only retrieves matching
                # documents — unlike /agent/ask, it never calls the model, so
                # a much shorter timeout is safe here.
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

                # Your search endpoint wraps the list inside "results".
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

                    # Display every document returned by the API — the
                    # challenge requires listing *every* result with its
                    # title and score, not just the top one.
                    for document in results:
                        st.markdown(f"**{document['title']}**")
                        st.caption(
                            f"Document: {document['id']} | "
                            f"Score: {document['score']:.3f}"
                        )
                        st.write(document["text"])
                        st.divider()

            except httpx.HTTPStatusError as exc:
                # 409 is what /knowledge/search returns specifically when
                # the index hasn't been built yet (knowledge.search raises
                # RuntimeError, which the router maps to 409). The challenge
                # asks for this to be handled differently from any other
                # failure, so it gets its own branch with actionable advice
                # instead of falling through to the generic error message.
                if exc.response.status_code == 409:
                    st.warning(
                        "The document index is not ready. "
                        "Build it using POST /knowledge/index, "
                        "then search again."
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
                st.error(
                    "The search API returned an unexpected response. "
                    "Each result should include id, title, score and text."
                )


# ---------------------------------------------------------
# Feature 3: Streaming firm summary
# ---------------------------------------------------------

with summary_tab:
    st.subheader("Firm summary")
    st.write("Stream a firm's summary from the API as it is generated.")

    # Fetch the real firm list from GET /firms instead of hardcoding ids 1-5.
    # The challenge requires this to work "for every firm id currently in
    # the data" — reading live from the API means it stays correct even if
    # firms are added or removed later.
    firm_options: list[dict] = []
    firms_load_error = None

    try:
        firms_response = httpx.get(f"{API_URL}/firms", timeout=10.0)
        firms_response.raise_for_status()
        firm_options = firms_response.json()

        if not isinstance(firm_options, list):
            raise ValueError("Expected a list of firms.")

    except httpx.RequestError:
        firms_load_error = "Could not reach the API to load the list of firms."

    except httpx.HTTPStatusError as exc:
        firms_load_error = f"Loading firms failed with HTTP status {exc.response.status_code}."

    except (ValueError, TypeError):
        firms_load_error = "The firms API returned an unexpected response."

    if firms_load_error:
        st.warning(firms_load_error)

    with st.form("summary_form"):
        if firm_options:
            # format_func controls only the label shown to the user; the
            # underlying value stored in selected_firm is still the full
            # firm dict, so we can read its real id below.
            selected_firm = st.selectbox(
                "Firm",
                options=firm_options,
                format_func=lambda firm: f"{firm['id']} — {firm['name']}",
            )
            firm_id = selected_firm["id"] if selected_firm else None
        else:
            # If the firm list couldn't be loaded, fall back to letting the
            # user type an id directly rather than blocking the feature.
            firm_id = st.number_input("Firm id", min_value=1, step=1)

        summary_submitted = st.form_submit_button("Get summary")

    if summary_submitted:
        # st.empty() reserves a spot on the page we can keep overwriting.
        # Re-rendering it with a growing string on every chunk is what
        # makes the summary appear to "type itself out" live, instead of
        # waiting for the whole response and printing it in one go.
        summary_placeholder = st.empty()
        summary_text = ""

        try:
            # httpx.stream() opens the connection and gives us the response
            # incrementally, unlike httpx.get()/post() above which buffer
            # the entire body before returning. That's what lets us read
            # and display the summary as the backend generates it.
            with httpx.stream(
                "GET",
                f"{API_URL}/firms/{firm_id}/summary/stream",
                timeout=120.0,
            ) as response:
                # We check status_code manually (rather than calling
                # raise_for_status) so we can tell the two failure modes
                # apart before consuming the streamed body: a 404 means a
                # bad firm id, anything else is a generic backend failure.
                if response.status_code == 404:
                    st.error(f"No firm with id {firm_id}.")

                elif response.status_code >= 400:
                    show_http_error(response.status_code)

                else:
                    # iter_text() yields the response body piece by piece as
                    # it arrives over the wire. Each piece gets appended to
                    # the running total and repainted into the placeholder.
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







