from fastapi.testclient import TestClient
import anthropic
import llm
from main import app

client = TestClient(app)

FAKE_SUMMARY = {
    "id": "CMP-001","summary": "The customer disputes a mortgage late-payment fee.",
    "input_tokens": 120,"output_tokens": 95,"stop_reason": "end_turn",
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

# Check that the streaming endpoint returns all the summary text.
def test_stream_yields_chunks(monkeypatch):
    monkeypatch.setattr(llm,"stream_complaint_summary",lambda complaint: iter(["Complaint ", "summary"]),)
    with client.stream("GET", "/insights/CMP-001/summary/stream") as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())
    assert body == "Complaint summary"

# Check that the endpoint returns structured complaint analysis.
def test_analysis_returns_structured_data(monkeypatch):
    analysis = llm.ComplaintAnalysis(
        issue_summary="The customer disputes a late-payment fee.",
        recorded_theme="late_payment_fee",
        recorded_severity="medium",
        missing_information=["Payment receipt date"],
        suggested_next_steps=["Check the payment records"],
    )

    fake_response = {
        "id": "CMP-001",
        "analysis": analysis,
        "input_tokens": 120,
        "output_tokens": 95,
        "stop_reason": "end_turn",
    }

    monkeypatch.setattr(llm, "analyse_complaint", lambda complaint: fake_response)
    response = client.post("/insights/CMP-001/analyse")
    assert response.status_code == 200
    assert response.json()["analysis"] == analysis.model_dump()