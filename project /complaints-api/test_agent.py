from fastapi.testclient import TestClient

import agent
from main import app

client = TestClient(app)


# Represent a tool request from Claude.
class FakeToolUseBlock:
    type = "tool_use"
    id = "toolu_01"
    name = "search_knowledge_base"

    def __init__(self, input):
        self.input = input


# Represent the token usage returned by Claude.
class FakeUsage:
    def __init__(self, i, o):
        self.input_tokens, self.output_tokens = i, o


# Represent Claude's response without calling the provider.
class FakeResponse:
    def __init__(self, content, stop_reason, usage):
        self.content = content
        self.stop_reason = stop_reason
        self.usage = usage

# Check that repeated tool requests stop at the iteration limit.
def test_agent_stops_at_max_iterations(monkeypatch):
    def fake_create(**kwargs):
        return FakeResponse([FakeToolUseBlock({"query": "mortgage payment"})],"tool_use", FakeUsage(100, 15),)

    monkeypatch.setattr(agent.client.messages, "create", fake_create)
    monkeypatch.setattr(
        agent.knowledge,"search",
        lambda q, top_k=3: [{"id": "doc-004", "title": "Mortgage Product Terms", "text": "Check the payment due date and bank receipt date.","score": 0.5}]
        )

    response = client.post("/agent/ask",json={"question": "Check the mortgage payment guidance"})
    body = response.json()

    assert response.status_code == 200
    assert body["completed"] is False
    assert body["stop_reason"] == "max_iterations"
    assert body["tool_calls_made"] == agent.MAX_ITERATIONS