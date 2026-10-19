"""Stub models and a test backend for the agent tests. No test calls a real model."""

from contextlib import nullcontext

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from agent import tools
from backend.main import app

MODEL_ERROR = "<model error>"


class StubModel(GenericFakeChatModel):
    """A chat model that gives scripted replies; MODEL_ERROR in the script raises."""

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, *args, **kwargs):
        result = super()._generate(*args, **kwargs)
        if result.generations[0].message.content == MODEL_ERROR:
            raise RuntimeError("Provider returned 502")
        return result


def broken_claim():
    """A claim agent's script whose model fails on every try, retries included."""
    return [AIMessage(content=MODEL_ERROR)] * 3


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
