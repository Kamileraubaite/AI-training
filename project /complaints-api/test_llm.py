from fastapi.testclient import TestClient

import llm
from main import app

client = TestClient(app)

FAKE_SUMMARY = {
    "id": "CMP-001",
    "summary": "The customer disputes a mortgage late-payment fee.",
    "input_tokens": 120,
    "output_tokens": 95,
    "stop_reason": "end_turn",
}


# Check that the summary endpoint returns text and token usage.
def test_summary_returns_text_and_usage(monkeypatch):
    monkeypatch.setattr(
        llm,
        "summarise_complaint",
        lambda complaint: FAKE_SUMMARY,
    )

    response = client.post("/insights/CMP-001/summary")

    assert response.status_code == 200
    assert response.json() == FAKE_SUMMARY