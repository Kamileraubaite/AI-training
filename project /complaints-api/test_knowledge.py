"""Knowledge endpoint tests. No Voyage calls, no Anthropic calls, no network."""

from fastapi.testclient import TestClient

import knowledge_store as knowledge
import llm
from main import app

client = TestClient(app)

STRONG_HIT = {
    "id": "doc-004",
    "title": "Mortgage Product Terms: Payments and Charges",
    "text": "When a fee is disputed, check the due date and bank receipt date.",
    "score": 0.81,
}
WEAK_HIT = {
    "id": "doc-003",
    "title": "Complaint Handling Guidance",
    "text": "Staff should review complaint records.",
    "score": 0.12,
}
FAKE_ANSWER = {
    "answer": "Check the due date and bank receipt date [doc-004].",
    "input_tokens": 400,
    "output_tokens": 30,
    "stop_reason": "end_turn",
}


# Return retrieved documents from the search-only endpoint.
def test_search_returns_ranked_hits(monkeypatch):
    monkeypatch.setattr(knowledge, "search", lambda q, k=3: [STRONG_HIT])

    response = client.post("/knowledge/search",json={"question": "What evidence should staff check for a disputed fee?"})
    assert response.status_code == 200
    assert response.json()["results"][0]["id"] == "doc-004"


# Report an empty index as a conflict.
def test_search_before_indexing_is_409(monkeypatch):
    def not_built(q, k=3):
        raise RuntimeError("Index is empty. Call build_index() first.")

    monkeypatch.setattr(knowledge, "search", not_built)

    response = client.post("/knowledge/search",json={"question": "What is the complaint handling policy?"})
    assert response.status_code == 409


# Return an answer with its retrieved sources and token usage.
def test_ask_answers_and_cites_sources(monkeypatch):
    monkeypatch.setattr(knowledge, "search", lambda q, k=3: [STRONG_HIT])
    monkeypatch.setattr(llm, "answer_from_context", lambda q, c: FAKE_ANSWER)

    body = client.post("/knowledge/ask",json={"question": "What evidence should staff check for a disputed fee?"}).json()

    assert body["refused"] is False
    assert body["sources"][0]["id"] == "doc-004"
    assert body["input_tokens"] == 400


# Refuse before calling Claude when no document is relevant enough.
def test_ask_refuses_without_calling_the_model(monkeypatch):
    monkeypatch.setattr(knowledge, "search", lambda q, k=3: [WEAK_HIT])

    def must_not_be_called(q, c):
        raise AssertionError("The model was called despite no relevant context")

    monkeypatch.setattr(llm, "answer_from_context", must_not_be_called)

    body = client.post("/knowledge/ask",json={"question": "How do I bake a chocolate cake?"}).json()
    assert body["refused"] is True
    assert body["answer"] is None
    assert body["sources"] == []


# Reject an empty question before searching or generating an answer.
def test_empty_question_is_rejected_before_any_work():
    response = client.post("/knowledge/ask", json={"question": ""})

    assert response.status_code == 422


# Reject requests for more results than the API allows.
def test_top_k_is_bounded():
    response = client.post("/knowledge/search",json={"question": "Mortgage payment terms", "top_k": 99})
    assert response.status_code == 422


# Flag a citation to a document that was not supplied to Claude.
def test_ask_reports_a_citation_to_a_source_it_never_retrieved(monkeypatch):
    drifting = { **FAKE_ANSWER,"answer": "Check the due date and bank receipt date [doc-003]."}
    monkeypatch.setattr(knowledge, "search", lambda q, k=3: [STRONG_HIT])
    monkeypatch.setattr(llm, "answer_from_context", lambda q, c: drifting)

    body = client.post("/knowledge/ask",json={"question": "What evidence should staff check for a disputed fee?"}).json()
    assert body["grounding"]["passed"] is False
    assert body["grounding"]["invalid"] == ["doc-003"]