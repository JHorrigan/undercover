"""Stub models and a test backend for the agent tests. No test calls a real model."""

from contextlib import nullcontext

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from agent import tools
from backend.main import app


class StubModel(GenericFakeChatModel):
    """A chat model that gives scripted replies in place of a real model."""

    def bind_tools(self, tools, **kwargs):
        return self


def call_tool(name, args, id_="1"):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": id_}])


def stub(*messages):
    return StubModel(messages=iter(messages))


def decide(claim_id, payout=420.0, decision="approve"):
    """A claim agent's script: read the claim and a section, decide, pay, reply."""
    body = {
        "claim_id": claim_id,
        "decision": decision,
        "payout": payout,
        "reason": "A covered delay with receipts.",
        "policy_section": "3. Trip Delay",
    }
    messages = [
        call_tool("get_claim", {"claim_id": claim_id}),
        call_tool("read_section", {"document": "policy_wording", "section": "3"}),
        call_tool("read_section", {"document": "claims_manual", "section": "10"}),
        call_tool("record_decision", body),
    ]
    if decision == "approve":
        messages.append(
            call_tool("pay_claim", {"claim_id": claim_id, "amount": payout})
        )
    return [*messages, AIMessage(content=f"{claim_id}: {decision}.")]


@pytest.fixture(autouse=True)
def use_test_backend(monkeypatch):
    with TestClient(app) as started:
        monkeypatch.setattr(tools, "backend", lambda: nullcontext(started))
        yield started
