from fastapi.testclient import TestClient
import anthropic
import httpx
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
    monkeypatch.setattr(llm,"summarise_complaint",lambda complaint: FAKE_SUMMARY,)
    response = client.post("/insights/CMP-001/summary")
    assert response.status_code == 200
    assert response.json() == FAKE_SUMMARY

# Check that a Claude timeout becomes a clear 504 response.
def test_provider_timeout_becomes_504(monkeypatch):
    def boom(complaint):
        raise anthropic.APITimeoutError(request=None)
    monkeypatch.setattr(llm, "summarise_complaint", boom)
    response = client.post("/insights/CMP-001/summary")
    assert response.status_code == 504
    assert response.json()["detail"] == "Claude request timed out"

# Check that the estimate endpoint returns the input token count.
def test_estimate_returns_input_tokens(monkeypatch):
    monkeypatch.setattr(llm,"estimate_input_tokens",lambda complaint: 137,)
    response = client.get("/insights/CMP-001/summary/estimate")
    assert response.status_code == 200
    assert response.json()["estimated_input_tokens"] == 137
