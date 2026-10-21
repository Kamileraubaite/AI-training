# Banking Complaints Intelligence UI

A Streamlit interface for the Banking Complaints Intelligence API.

All records and documents are synthetic. AI guidance is a draft
for staff review.

## Features

- Ask the agent questions and view its answer, successful tool-call
  count and token usage.
- Show a warning when the agent does not complete.
- Search documents and view each result's title, text and similarity score.
- Select a complaint and stream its draft summary.
- Filter complaints by status and severity in the complaint triage table.

## Set up on macOS

Run these commands from inside `complaints-ui`.
Python 3.12 was used for development.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The UI has its own virtual environment, separate from the API.

## Start the API first

Follow the setup instructions in `../complaints-api/README.md`.

The API must be running at:

http://127.0.0.1:8000

Build the document index using `POST /knowledge/index` before
using document search or asking questions that need documents.

## Start the UI

In a separate terminal, from `complaints-ui`, run:

```bash
.venv/bin/python -m streamlit run app.py
```

Open:

http://localhost:8501

Keep both the API and UI running.

## Configuration

The backend address is set through `API_URL` in `app.py`.

The UI does not need Anthropic or Voyage API keys.
Those keys belong in the API's environment.

## Try the features

### Ask the agent

Ask:

“For CMP-001, find similar historic complaints and search the
mortgage payment guidance. What evidence should staff check?”

The interface displays the answer, successful tool calls,
input tokens and output tokens.

### Search documents

Search:

“What evidence should staff check when a customer disputes a
mortgage late-payment fee?”

With the slider set to 3, the interface displays up to three results.
Search-only includes weak matches; scores are similarity measures,
not confidence probabilities.

### Complaint summary

Select `CMP-001` and click **Get summary**.
The draft summary appears as text arrives from the API.

### Complaint triage

Select status `open` and severity `high`, then click
**Show complaints**.

With the original synthetic data, this returns `CMP-007`.

## Troubleshooting

- If the API cannot be reached, check that it is running on port 8000.
- If the document index is not ready, run `POST /knowledge/index`.
- If a provider times out or reaches its rate limit, the interface
  displays an error message.
- If the agent reaches its limit, try a more specific question.

## Limitations

AI outputs require staff review. The interface does not approve
complaint outcomes or compensation.

Changes to structured records reset when the API process restarts.