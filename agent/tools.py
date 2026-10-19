"""The UnderCover agents' tools. Each one calls the backend's API.

A tool gets its claim or run from the agent's context (`ToolRuntime`), never from
the model, so a claim agent can only act on the claim it was given.
"""

from dataclasses import dataclass
from typing import Any, Literal, TypedDict

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from agent import backend
from agent.backend import text

ERROR_CHARS = 300


@dataclass
class ClaimContext:
    """A claim agent's context: the one claim it works."""

    claim_id: str


@dataclass
class RunContext:
    """The queue agent's context: its run, and the claim agent it hands claims to."""

    run_id: str
    claim_agent: Runnable[Any, Any]


class Todo(TypedDict):
    """One item on the run's to-do list."""

    text: str
    status: Literal["to_do", "in_progress", "done", "for_handler"]


@tool
def get_claim(runtime: ToolRuntime[ClaimContext]) -> str:
    """Get your claim: the story, the items claimed, the documents and its status."""
    return text("GET", f"/api/claims/{runtime.context.claim_id}")


@tool
def get_policy(policy_id: str) -> str:
    """Get a policy: the plan, add-ons, purchase date, trip and travelers."""
    return text("GET", f"/api/policies/{policy_id}")


@tool
def get_customer(customer_id: str) -> str:
    """Get a customer with their earlier claims."""
    return text("GET", f"/api/customers/{customer_id}")


@tool
def list_plans() -> str:
    """List the plans with their limits, waiting periods, deductibles and add-ons."""
    return text("GET", "/api/plans")


@tool
def list_documents() -> str:
    """List the numbered sections of the policy wording and the claims manual."""
    return text("GET", "/api/documents")


@tool
def read_section(
    document: Literal["policy_wording", "claims_manual"], section: str
) -> str:
    """Read one numbered section of the policy wording or the claims manual."""
    return text("GET", f"/api/documents/{document}/sections/{section}")


@tool
def record_decision(
    decision: Literal["approve", "decline", "refer"],
    payout: float,
    reason: str,
    policy_section: str,
    runtime: ToolRuntime[ClaimContext],
) -> str:
    """Record your claim's decision, with the payout, the reason and the section."""
    body = {
        "decision": decision,
        "payout": payout,
        "reason": reason,
        "policy_section": policy_section,
    }
    return text("POST", f"/api/claims/{runtime.context.claim_id}/decision", body)


@tool
def pay_claim(amount: float, runtime: ToolRuntime[ClaimContext]) -> str:
    """Pay your approved claim its payout in US dollars."""
    claim_id = runtime.context.claim_id
    return text("POST", f"/api/claims/{claim_id}/payment", {"amount": amount})


@tool
def list_waiting_claims() -> str:
    """List the claims waiting in the queue, with their failures so far."""
    return text("GET", "/api/claims?status=waiting")


@tool
def update_todos(todos: list[Todo], runtime: ToolRuntime[RunContext]) -> str:
    """Replace the run's to-do list. Each item has text and a status."""
    run_id = runtime.context.run_id
    return text("PUT", f"/api/runs/{run_id}/todos", {"todos": todos})


@tool
def work_claim(claim_id: str, runtime: ToolRuntime[RunContext]) -> str:
    """Hand one claim to a fresh claim agent; it reports back in one line."""
    return work(claim_id, runtime.context)


@tool
def finish_run(summary: str, runtime: ToolRuntime[RunContext]) -> str:
    """Finish the run with a short summary for the handlers."""
    run_id = runtime.context.run_id
    return text("POST", f"/api/runs/{run_id}/finish", {"summary": summary})


CLAIM_TOOLS = [
    get_claim,
    get_policy,
    get_customer,
    list_plans,
    list_documents,
    read_section,
    record_decision,
    pay_claim,
]
QUEUE_TOOLS = [list_waiting_claims, update_todos, work_claim, finish_run]


def work(claim_id: str, context: RunContext) -> str:
    """Work one claim in the run's claim agent and report the outcome in one line."""
    start = {"run_id": context.run_id}
    started = backend.request("POST", f"/api/claims/{claim_id}/start", start)
    if not started.is_success:
        return f"{claim_id} not started: {started.text}"
    task = {"messages": [HumanMessage(f"Decide claim {claim_id}.")]}
    try:
        context.claim_agent.invoke(task, context=ClaimContext(claim_id))
    except Exception as exc:  # one bad claim must never stop the run
        return fail(claim_id, f"{type(exc).__name__}: {exc}"[:ERROR_CHARS])
    claim = backend.data("GET", f"/api/claims/{claim_id}")
    if claim["status"] == "in_progress":
        return fail(claim_id, "Stopped without recording a decision")
    return report(claim)


def fail(claim_id: str, error: str) -> str:
    """Record a failure on the claim and report where the claim went."""
    claim = backend.data("POST", f"/api/claims/{claim_id}/fail", {"error": error})
    if claim["status"] == "needs_handler":
        return f"{claim_id} failed: {error}. Left for a handler"
    return f"{claim_id} failed: {error}. Back in the queue"


def report(claim: dict[str, Any]) -> str:
    """Report a decided claim in one line: its decision, payout and payment."""
    decision = claim["decision"]
    paid = "paid" if claim["payment"] else "not paid"
    if claim["status"] == "awaiting_signoff":
        paid = "waiting for sign-off"
    payout = f"${decision['payout']:,.2f}"
    return f"{claim['claim_id']}: {decision['decision']}, {payout}, {paid}"
