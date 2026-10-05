from fastapi.testclient import TestClient
import anthropic
import pytest
from pydantic import ValidationError
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

# Check that the streaming endpoint returns all the summary text.
def test_stream_yields_chunks(monkeypatch):
    monkeypatch.setattr(llm,"stream_complaint_summary",lambda complaint: iter(["Complaint ", "summary"]),)
    with client.stream("GET", "/insights/CMP-001/summary/stream") as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())
    assert body == "Complaint summary"

# Check that a failure before any text arrives becomes a clear 504 response.
def test_stream_timeout_before_text_becomes_504(monkeypatch):
    def failing_stream(complaint):
        raise anthropic.APITimeoutError(request=None)
        yield
    monkeypatch.setattr(llm, "stream_complaint_summary", failing_stream)
    response = client.get("/insights/CMP-001/summary/stream")
    assert response.status_code == 504
    assert response.json()["detail"] == "Claude request timed out"

# Check that a failure part-way through the stream is shown to the client.
def test_stream_failure_midway_adds_marker(monkeypatch):
    def partial_stream(complaint):
        yield "Complaint "
        raise anthropic.APITimeoutError(request=None)
    monkeypatch.setattr(llm, "stream_complaint_summary", partial_stream)
    with client.stream("GET", "/insights/CMP-001/summary/stream") as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())
    assert body.startswith("Complaint ")
    assert "Summary interrupted" in body

# Check that the endpoint returns structured complaint analysis.
def test_analysis_returns_structured_data(monkeypatch):
    analysis = llm.ComplaintAnalysis(
        theme="late_payment_fee",
        severity="medium",
        recommended_next_step="Check the payment records against the fee date.",
        rationale="The customer disputes a late-payment fee.",
        missing_information=["Payment receipt date"],
        human_review_required=True,
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
    assert response.json()["analysis"] == analysis.model_dump(mode="json")

# Check that an invalid theme is rejected by the analysis model.
def test_analysis_rejects_unknown_theme():
    with pytest.raises(ValidationError):
        llm.ComplaintAnalysis(
            theme="made_up_theme",
            severity="low",
            recommended_next_step="Check records.",
            rationale="Reason.",
            missing_information=[],
            human_review_required=True,
        )
