"""The queue agent: plans a run, hands each claim to a claim agent and sums up."""

import json
from typing import Any, Literal, TypedDict

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, ModelCallLimitMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.tools import BaseTool, tool

from agent import claim, runs, tools
from agent.model import model, retry

MAX_REMINDERS = 2
CALLS_PER_CLAIM = 6
REMINDER = "The run is not finished. Check for missed claims, then call finish_run."


class Todo(TypedDict):
    """One item on the run's to-do list."""

    text: str
    status: Literal["to_do", "in_progress", "done", "for_handler"]


def waiting_claims() -> str:
    """Return the waiting claims, one short JSON line each."""
    claims = json.loads(tools.call("GET", "/api/claims"))
    fields = ("claim_id", "claim_type", "amount_claimed", "submitted_on", "failures")
    return "\n".join(
        json.dumps({f: c[f] for f in fields})
        for c in claims
        if c["status"] == "waiting"
    )


def queue_tools(run_id: str, claim_llm: BaseChatModel | None) -> list[BaseTool]:
    """Return the queue agent's tools, bound to its run."""

    @tool
    def list_waiting_claims() -> str:
        """List the waiting claims: id, type, amount, submitted date and failures."""
        return waiting_claims() or "No claims are waiting."

    @tool
    def update_todos(todos: list[Todo]) -> str:
        """Replace the run's to-do list. Each item has text and a status."""
        return tools.call("PUT", f"/api/runs/{run_id}/todos", {"todos": todos})

    @tool
    def work_claim(claim_id: str) -> str:
        """Hand one claim to a fresh claim agent; it reports back in one line."""
        return claim.work_claim(claim_id, run_id, claim_llm)

    @tool
    def finish_run(summary: str) -> str:
        """Finish the run with a short summary for the handlers."""
        return runs.finish_run(run_id, summary)

    return [list_waiting_claims, update_todos, work_claim, finish_run]


def run_queue(
    cap: int,
    llm: BaseChatModel | None = None,
    claim_llm: BaseChatModel | None = None,
) -> str:
    """Work the waiting claims, up to the cap, and return the run's summary."""
    run_id = runs.create_run(cap)
    middleware: list[AgentMiddleware[Any, Any, Any]] = [
        retry(),
        ModelCallLimitMiddleware(run_limit=CALLS_PER_CLAIM * cap + 10),
    ]
    agent = create_agent(
        llm or model(),
        tools=queue_tools(run_id, claim_llm),
        system_prompt=tools.call("GET", "/api/instructions/queue"),
        middleware=middleware,
    )
    task = f"Work the queue. This run is capped at {cap} claims."
    messages: list[AnyMessage | dict[str, Any]] = [HumanMessage(task)]
    try:
        for _ in range(MAX_REMINDERS + 1):
            messages = agent.invoke({"messages": messages})["messages"]
            if runs.latest_run()["finished_at"]:
                break
            messages.append(HumanMessage(REMINDER))
    finally:
        if not runs.latest_run()["finished_at"]:
            runs.stop_run(run_id, "Stopped before finishing")
    return runs.latest_run()["summary"]
