# 1. set up some fake building blocks 
# 2. create a fake model (that keeps going)
# 3. sub in our fakes from step 1
# 4. hit our endpoint
# 5. check it stopped
# pretend the model never stops... check your code stops it anyway

from fastapi.testclient import TestClient

import agent
from main import app

client = TestClient(app)

class FakeToolUseBlock:
    # CHANGED: REMOVED THE TRAILING COMMAS. THEY TURNED THESE THREE VALUES INTO TUPLES, NOT STRINGS
    type = "tool_use"
    id = "toolu_01"
    name = "search_knowledge_base"
    # CHANGED: __init__ NOW ACCEPTS THE INPUT DICT THAT THE TEST PASSES IN, AND STORES IT
    def __init__(self, input):
        self.input = input

class FakeUsage:
    def __init__(self, i, o):
        self.input_tokens, self.output_tokens = i, o

class FakeResponse:
    def __init__(self, content, stop_reason, usage):
        self.content, self.stop_reason, self.usage = content, stop_reason, usage


def test_agent_stops_at_max_interactions_instead_of_looping_forever(monkeypatch): 
    def fake_create(**kwargs):
        return FakeResponse(
            [FakeToolUseBlock({"query": "anyting"})], "tool_use", FakeUsage(100, 15)
        )
        
    monkeypatch.setattr(agent.client.messages, "create", fake_create) 
    monkeypatch.setattr(
        agent.knowledge, "search",
        lambda q, top_k=3 : [{"id": "doc-001", "title": "t", "text": "x", "score": 0.5 }]
    ) 

    response = client.post("/agent/ask", json={"question": "never resolves"})
    body = response.json()


    assert response.status_code == 200

    # assert - completed

    # CHANGED: WAS "== True". HITTING THE LIMIT MEANS THE AGENT DID NOT COMPLETE
    assert body["completed"] == False

    # assert - stop_reason

    # CHANGED: WAS "max_interactions". agent.py NOW RETURNS "max_iterations"
    assert body["stop_reason"] == "max_iterations"

    # assert - tool_calls_made

    # CHANGED: WAS agent.MAX_INTERACTIONS, WHICH DOES NOT EXIST. THE REAL NAME IS MAX_ITERATIONS
    assert body["tool_calls_made"] == agent.MAX_ITERATIONS



