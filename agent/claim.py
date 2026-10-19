"""The claim agent: works one claim from a clean start and reports back in a line."""

from typing import Any
from uuid import uuid4

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from agent import runs, tools
from agent.model import model, retry

RESULT_CHARS = 300
ERROR_CHARS = 300
MAX_ATTEMPTS = 2
WHERE_NEXT = {
    "waiting": "Back in the queue",
    "needs_handler": "Left for a handler",
}


def section_read(message: ToolMessage) -> str | None:
    """Return 'Claims manual: 9. Repeat claims' for a section the agent read."""
    document, _, text = message.text.partition("\n## ")
    if message.name != "read_section" or not text:
        return None
    return f"{document}: {text.splitlines()[0]}"


def describe(message: BaseMessage) -> list[tuple[str, str]]:
    """Turn one agent message into steps for the dashboard, as (kind, text)."""
    if isinstance(message, ToolMessage):
        if read := section_read(message):
            return [("read", read)]
        return [("result", f"{message.name}: {message.text[:RESULT_CHARS]}")]
    if isinstance(message, AIMessage) and message.tool_calls:
        return [("tool", f"{c['name']} {c['args']}") for c in message.tool_calls]
    return [("reply", message.text)] if message.text else []


def add_step(claim_id: str, kind: str, text: str) -> None:
    """Log one step on the claim in the backend."""
    tools.call("POST", f"/api/claims/{claim_id}/steps", {"kind": kind, "text": text})


def instructions() -> str:
    """Return the claim agent's instructions."""
    return tools.call("GET", "/api/instructions/claim")


def run_claim(claim_id: str, llm: BaseChatModel | None = None) -> None:
    """Run the claim agent on a started claim from a clean thread, logging each step."""
    agent = create_agent(
        llm or model(),
        tools=tools.TOOLS,
        system_prompt=instructions(),
        middleware=[retry()],
    )
    for update in agent.stream(
        {"messages": [{"role": "user", "content": f"Decide claim {claim_id}."}]},
        config={"configurable": {"thread_id": f"{claim_id}-{uuid4().hex[:8]}"}},
        stream_mode="updates",
    ):
        for message in messages_in(update):
            for kind, text in describe(message):
                add_step(claim_id, kind, text)


def work_claim(claim_id: str, run_id: str, llm: BaseChatModel | None = None) -> str:
    """Work one claim in a fresh claim agent and report back in one line."""
    started = tools.call("POST", f"/api/claims/{claim_id}/start", {"run_id": run_id})
    if started.startswith("Error"):
        return f"{claim_id} not started: {started}"
    try:
        run_claim(claim_id, llm)
    except Exception as exc:  # one bad claim must never stop the run
        return failed(claim_id, f"{type(exc).__name__}: {exc}"[:ERROR_CHARS])
    return outcome(runs.get_claim(claim_id))


def failed(claim_id: str, error: str) -> str:
    """Record a failure on the claim and report where the claim went."""
    tools.call("POST", f"/api/claims/{claim_id}/fail", {"error": error})
    status = runs.get_claim(claim_id)["status"]
    return f"{claim_id} failed: {error}. {WHERE_NEXT[status]}"


def outcome(claim: dict[str, Any]) -> str:
    """Report a worked claim in one line: its decision and payout."""
    if claim["status"] == "in_progress":
        return failed(claim["claim_id"], "Stopped without recording a decision")
    decision = claim["decision"]
    paid = "paid" if claim["payment"] else "not paid"
    if claim["status"] == "awaiting_signoff":
        paid = "waiting for sign-off"
    payout = f"${decision['payout']:,.2f}"
    return f"{claim['claim_id']}: {decision['decision']}, {payout}, {paid}"


def run_one(claim_id: str, llm: BaseChatModel | None = None) -> str:
    """Run one named claim in its own run, trying it again if it fails once."""
    run_id = runs.create_run(1)
    report = ""
    for _ in range(MAX_ATTEMPTS):
        report = work_claim(claim_id, run_id, llm)
        if runs.get_claim(claim_id)["status"] != "waiting":
            break
    runs.finish_run(run_id, report)
    return report


def messages_in(update: dict[str, Any]) -> list[BaseMessage]:
    """Return the new messages in one streamed update from the agent."""
    return [m for node in update.values() if node for m in node.get("messages", [])]
