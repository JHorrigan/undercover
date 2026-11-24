import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.utils.function_calling import convert_to_openai_tool

from agent import api as agent_api
from agent import harness, main, tools, worker
from backend.main import app

CLAIM = "CLM-1001"


class StubModel(GenericFakeChatModel):
    """A chat model that gives scripted replies in place of a real model."""

    def bind_tools(self, tools, **kwargs):
        return self


def call(name, args=None, cost=0.0):
    """Return a scripted model reply that calls one tool."""
    return AIMessage(
        content="",
        tool_calls=[{"name": name, "args": args or {}, "id": name}],
        response_metadata={"token_usage": {"cost": cost}},
    )


def stub(*replies):
    """Return a stub model that gives these replies, then a final answer."""
    final = AIMessage(
        content="Done.", response_metadata={"token_usage": {"cost": 0.001}}
    )
    return StubModel(messages=iter([*replies, final]))


@pytest.fixture
def api(client, monkeypatch):
    """Send the agent's API calls to the test database, with CLM-1001 in progress."""
    monkeypatch.setattr(agent_api, "backend", lambda: TestClient(app))
    while client.post("/api/queue/next").json()["claim_id"] != CLAIM:
        pass
    return client


def decision(verdict, payout):
    """Return the arguments for a decision on CLM-1001."""
    return {
        "decision": verdict,
        "payout": payout,
        "reason": "The flight was canceled and the costs are covered.",
        "section": "3. Trip Delay",
    }


def test_the_agent_approves_and_pays_a_claim(api):
    llm = stub(
        call("get_claim_evidence", cost=0.002),
        call("get_policy"),
        call("get_policy_wording"),
        call("record_decision", decision("approve", 420)),
        call("pay_claim", {"amount": 420}),
    )
    assert main.run(CLAIM, CLAIM, llm) == "Done."
    claim = api.get(f"/api/claims/{CLAIM}").json()
    assert claim["status"] == "decided"
    assert claim["decision"]["decision"] == "approve"
    assert claim["payment"]["amount"] == 420


def test_a_payment_over_the_limit_is_held_for_sign_off(api):
    llm = stub(
        call("record_decision", decision("approve", 1500)),
        call("pay_claim", {"amount": 1500}),
    )
    result = harness.build(llm).invoke(
        {"messages": [{"role": "user", "content": f"Decide claim {CLAIM}."}]},
        context=tools.Context(claim_id=CLAIM),
    )
    replies = [message.text for message in result["messages"] if message.type == "tool"]
    assert replies == [
        "Done.",
        "Refused: A payout over the limit needs a handler's sign-off",
    ]
    claim = api.get(f"/api/claims/{CLAIM}").json()
    assert claim["status"] == "awaiting_signoff"
    assert claim["payment"] is None


def test_each_tool_call_and_model_cost_is_recorded(api):
    main.run(
        CLAIM, CLAIM, stub(call("get_claim_evidence", cost=0.002), call("get_policy"))
    )
    steps = api.get(f"/api/claims/{CLAIM}").json()["steps"]
    texts = [step["text"] for step in steps]
    assert texts == [
        "Chose get_claim_evidence",
        "get_claim_evidence",
        "Chose get_policy",
        "get_policy",
        "Chose to reply",
    ]
    assert steps[0]["cost"] == pytest.approx(0.002)


def test_no_tool_takes_the_claim_id_from_the_model():
    for tool in tools.TOOLS:
        properties = convert_to_openai_tool(tool)["function"]["parameters"][
            "properties"
        ]
        assert "claim_id" not in properties, tool.name
        assert "runtime" not in properties, tool.name


def test_the_worker_decides_every_waiting_claim(client, monkeypatch):
    monkeypatch.setattr(agent_api, "backend", lambda: TestClient(app))
    worked = []
    monkeypatch.setattr(
        worker, "run", lambda claim_id, thread_id: worked.append(claim_id)
    )
    assert worker.work_queue() == 25
    assert len(set(worked)) == 25
    assert client.post("/api/queue/next").json() is None


def test_model_name(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("MODEL_NAME", raising=False)
    assert harness.model().model_name == "openai/gpt-6-luna"
    monkeypatch.setenv("MODEL_NAME", "openrouter/free")
    assert harness.model().model_name == "openrouter/free"
