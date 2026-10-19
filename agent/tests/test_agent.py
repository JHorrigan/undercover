from contextlib import nullcontext
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage

from agent import main, model, tools
from backend import runs
from backend.main import app


class StubModel(GenericFakeChatModel):
    """A chat model that gives scripted replies in place of a real model."""

    def bind_tools(self, tools, **kwargs):
        return self


def call_tool(name, args, id_):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": id_}])


def decision(payout):
    return {
        "claim_id": "CLM-1001",
        "decision": "approve",
        "payout": payout,
        "reason": "A covered delay with receipts.",
        "policy_section": "3. Trip Delay",
    }


def stub(payout):
    return StubModel(
        messages=iter(
            [
                call_tool("get_claim", {"claim_id": "CLM-1001"}, "1"),
                call_tool("record_decision", decision(payout), "2"),
                call_tool("pay_claim", {"claim_id": "CLM-1001", "amount": payout}, "3"),
                AIMessage(content="Decided."),
            ]
        )
    )


@pytest.fixture(autouse=True)
def use_test_backend(monkeypatch):
    with TestClient(app) as started:
        monkeypatch.setattr(tools, "backend", lambda: nullcontext(started))
        yield


def claim():
    with TestClient(app) as client:
        return client.get("/api/claims/CLM-1001").json()


def test_run_approves_and_pays():
    assert main.run("CLM-1001", "thread-1", stub(420.0)) == "Decided."
    result = claim()
    assert result["status"] == "decided"
    assert result["payment"]["amount"] == 420.0
    with TestClient(app) as client:
        steps = client.get("/api/claims/CLM-1001/steps").json()
    assert [s["kind"] for s in steps] == [
        "tool",
        "result",
        "tool",
        "result",
        "tool",
        "result",
        "reply",
    ]


def test_payment_over_limit_is_blocked():
    main.run("CLM-1001", "thread-1", stub(1500.0))
    result = claim()
    assert result["status"] == "awaiting_signoff"
    assert result["payment"] is None
    with TestClient(app) as client:
        steps = client.get("/api/claims/CLM-1001/steps").json()
    assert "Error 403" in steps[-2]["text"]


def test_tools_read_records():
    assert '"plan":"premium"' in tools.get_policy.invoke({"policy_id": "POL-2001"})
    assert "Maya Patel" in tools.get_customer.invoke({"customer_id": "CUS-3001"})
    assert "economy" in tools.list_plans.invoke({})
    assert "Repeat claims" in tools.list_documents.invoke({})
    section = {"document": "claims_manual", "section": "9"}
    assert tools.read_section.invoke(section).startswith(
        "Claims manual\n## 9. Repeat claims"
    )
    assert tools.get_claim.invoke({"claim_id": "CLM-9999"}).startswith("Error 404")


def test_agent_only_uses_the_api():
    for source in Path(main.__file__).parent.glob("*.py"):
        code = source.read_text(encoding="utf-8")
        for forbidden in ("pathlib", "open(", "data/", "evals", "sqlite"):
            assert forbidden not in code, f"{source.name} uses {forbidden}"


def test_run_agent_route(monkeypatch, client):
    started = []
    monkeypatch.setattr(runs.agent, "run", lambda claim_id, _: started.append(claim_id))
    assert client.post("/api/claims/CLM-1001/run").json() == {"status": "started"}
    assert started == ["CLM-1001"]
    assert client.post("/api/claims/CLM-9999/run").status_code == 404
    run = client.post("/api/runs", json={"cap": 1}).json()
    client.post("/api/claims/CLM-1002/start", json=run)
    assert client.post("/api/claims/CLM-1002/run").status_code == 409


def test_model_name(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("MODEL_NAME", raising=False)
    default = model.model()
    assert default.model_name == "deepseek/deepseek-v4.1-flash"
    assert default.reasoning_effort == "low"
    monkeypatch.setenv("MODEL_NAME", "openrouter/free")
    assert model.model().model_name == "openrouter/free"


def test_section_read_is_a_read_step():
    message = ToolMessage(
        content="Claims manual\n## 9. Repeat claims\nText.",
        name="read_section",
        tool_call_id="1",
    )
    assert main.describe(message) == [("read", "Claims manual: 9. Repeat claims")]
    missing = ToolMessage(
        content="Claims manual\nError 404: missing",
        name="read_section",
        tool_call_id="2",
    )
    assert main.describe(missing)[0][0] == "result"
