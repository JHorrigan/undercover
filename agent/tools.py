"""The agent's tools: each one a thin call to the backend's API."""

from dataclasses import dataclass
from typing import Annotated, Literal

from langchain.tools import ToolRuntime, tool
from pydantic import Field

from agent.api import fetch, send


@dataclass
class Context:
    """What the agent is working on, set by code, never by the model."""

    claim_id: str


@tool
def get_claim_evidence(runtime: ToolRuntime[Context]) -> dict:
    """Read the claim: the customer's story, the items claimed and the documents."""
    return fetch(f"/api/claims/{runtime.context.claim_id}/evidence")


@tool
def get_policy(runtime: ToolRuntime[Context]) -> dict:
    """Read the customer's policy, its plan's limits and the rules for add-ons."""
    return fetch(f"/api/claims/{runtime.context.claim_id}/policy")


@tool
def get_claim_history(runtime: ToolRuntime[Context]) -> list:
    """Read the customer's earlier claims."""
    return fetch(f"/api/claims/{runtime.context.claim_id}/history")


@tool
def get_policy_wording() -> dict:
    """Read the policy wording in force."""
    return fetch("/api/policy-wording")


@tool
def record_decision(
    decision: Literal["approve", "decline", "refer"],
    payout: Annotated[float, Field(description="US dollars, 0 unless approved")],
    reason: Annotated[str, Field(description="Two or three plain sentences")],
    section: Annotated[str, Field(description="The wording section it rests on")],
    runtime: ToolRuntime[Context],
) -> str:
    """Record your decision on the claim."""
    body = {
        "decision": decision,
        "payout": payout,
        "reason": reason,
        "section": section,
    }
    return send(f"/api/claims/{runtime.context.claim_id}/decision", body)


@tool
def pay_claim(amount: float, runtime: ToolRuntime[Context]) -> str:
    """Pay an approved claim the payout you approved, in US dollars."""
    return send(f"/api/claims/{runtime.context.claim_id}/payment", {"amount": amount})


TOOLS = [
    get_claim_evidence,
    get_policy,
    get_claim_history,
    get_policy_wording,
    record_decision,
    pay_claim,
]
