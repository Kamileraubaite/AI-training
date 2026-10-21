# Banking Complaints Intelligence API

This training project helps banking staff review complaints, search
supporting documents and generate draft AI guidance.

All customer records and documents are synthetic. AI outputs require
staff review and do not approve complaint outcomes or compensation.

## Features

- Customer and product records with create, read, update and delete endpoints.
- Complaint records with filters, including status, severity and theme.
- Claude summaries, streaming summaries and structured complaint analysis.
- An input-token estimate endpoint for complaint summaries.
- Persistent document search using Voyage embeddings and Chroma.
- Grounded answers with sources, citation checks and a relevance-based refusal rule.
- An agent with document search and similar historic complaint search tools.
- An agent limit of four Claude calls per request.

The Streamlit interface is in the separate `complaints-ui` folder.

## Set up the API on macOS

Run these commands from inside `complaints-api`.
Python 3.12 was used for development.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Set your real API keys in the same terminal:

```bash
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_KEY"
export VOYAGE_API_KEY="YOUR_VOYAGE_KEY"
```

These variables last for the current terminal session.
Do not commit real keys to Git.

Optional configuration:

```bash
export CLAUDE_MODEL="claude-haiku-4-5-20251001"
export EMBED_MODEL="voyage-3-lite"
export CHROMA_PATH="./chroma_store"
```

The relevance floor defaults to `0.45`. To change it, set this
environment variable before starting the API:

```bash
export RELEVANCE_FLOOR="0.45"
```

## Start the API

```bash
.venv/bin/python -m uvicorn main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

Leave the API running while using the Streamlit interface.

## Build the document index

With the API running, execute `POST /knowledge/index` in Swagger,
or use another terminal:

```bash
curl -X POST http://127.0.0.1:8000/knowledge/index
```

This calls Voyage to embed the documents and upserts them into Chroma.

Chroma stores the index persistently, so restarting the API does not
require reindexing. Run indexing again after changing documents.
If the embedding model changes, recreate the collection and reindex
before searching.

Customer, product and complaint changes are stored in memory and
reset when the API process restarts.

## Main endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Check that the API is running |
| GET / POST | `/customers` | List or create customers |
| GET / PUT / DELETE | `/customers/{customer_id}` | Read, update or delete a customer |
| GET / POST | `/products` | List or create products |
| GET / PUT / DELETE | `/products/{product_id}` | Read, update or delete a product |
| GET / POST | `/complaints` | List or create complaints |
| GET / PUT | `/complaints/{complaint_id}` | Read or update a complaint |
| POST | `/insights/{complaint_id}/summary` | Generate a draft summary |
| GET | `/insights/{complaint_id}/summary/stream` | Stream a draft summary |
| POST | `/insights/{complaint_id}/summary/estimate` | Count summary input tokens |
| POST | `/insights/{complaint_id}/analyse` | Propose a complaint classification and next step |
| POST | `/knowledge/index` | Embed and index documents |
| POST | `/knowledge/search` | Retrieve documents with similarity scores |
| POST | `/knowledge/ask` | Answer from qualifying documents or refuse |
| POST | `/agent/ask` | Ask the tool-using complaints assistant |

Customers and products linked to complaints cannot be deleted.

## Relevance floor

I chose `0.45` after testing banking questions and unrelated questions.

A floor of `0.50` excluded useful policies: the Complaint Handling
Policy scored `0.475`, and the large-print support policy scored
`0.468`. A floor of `0.45` retained both.

In mortgage and card-fee examples, less relevant documents scored
around `0.409–0.424`. A floor of `0.35` admitted these matches,
while `0.45` excluded them.

Unrelated chocolate-cake and bicycle-repair questions were refused.

This is a starting threshold based on a small test set, rather than
a proven best value for every question.

The floor applies to `/knowledge/ask`. Search-only returns the top
matches, including results below the floor. The agent currently
calls search directly without applying this threshold.

## Run the automated tests

From `complaints-api`, run:

```bash
ANTHROPIC_API_KEY=sk-fake VOYAGE_API_KEY=vo-fake \
.venv/bin/python -m pytest -q
```

The existing tests replace external calls with fake responses.
Fake keys are only for these tests; running real features requires
valid provider keys.

Tests cover summaries, streaming behaviour, structured analysis
responses, grounded answering, refusal without calling Claude,
citation checks and the agent iteration limit.

## Example agent question

Send this to `POST /agent/ask`:

```json
{
  "question": "For complaint CMP-001, find similar historic complaints and search the mortgage payment guidance. What evidence should staff check before recommending an outcome?"
}
```

## Limitations

- Similar historic outcomes do not determine a new complaint's outcome.
- Similarity scores are not confidence probabilities.
- Citation checks validate source IDs and citation placement, not
  whether every claim is supported by its source.
- Prompts guide Claude's behaviour but do not guarantee correctness.
- This is a training prototype, not a production banking system.
