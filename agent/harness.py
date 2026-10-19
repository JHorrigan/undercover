"""The UnderCover harness: the model, the middleware and the two agents.

The queue agent plans a run and hands each claim to the claim agent with the
`work_claim` tool. The claim agent decides one claim, and its middleware logs every
step on the claim for the dashboard.
"""

import os
from collections.abc import Callable
from typing import Any, cast

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    ModelCallLimitMiddleware,
    ModelRetryMiddleware,
    after_model,
)
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime
from langgraph.types import Command
from pydantic import SecretStr

from agent import backend, tools
from agent.tools import ClaimContext, RunContext

load_dotenv(override=True)

OPENROUTER_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "deepseek/deepseek-v4.1-flash"
TIMEOUT_SECONDS = 120
RESULT_CHARS = 300
CALLS_PER_CLAIM = 6
MAX_REMINDERS = 2
REMINDER = "The run is not finished. Work any claim still waiting, then finish_run."
DOCUMENT_NAMES = {"policy_wording": "Policy wording", "claims_manual": "Claims manual"}


def model() -> ChatOpenAI:
    """Return the model named in MODEL_NAME, or DeepSeek V4.1 Flash by default."""
    name = os.getenv("MODEL_NAME")
    return ChatOpenAI(
        model=name or DEFAULT_MODEL,
        base_url=OPENROUTER_URL,
        api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]),
        reasoning_effort=None if name else "low",
        timeout=TIMEOUT_SECONDS,
    )


def retry() -> ModelRetryMiddleware[Any, Any]:
    """Retry a failed model call twice, then raise so the claim is put right."""
    return ModelRetryMiddleware[Any, Any](max_retries=2, on_failure="error")


def add_step(claim_id: str, kind: str, text: str) -> None:
    """Log one step on a claim for the dashboard."""
    backend.data("POST", f"/api/claims/{claim_id}/steps", {"kind": kind, "text": text})


def result_step(call: dict[str, Any], result: ToolMessage) -> tuple[str, str]:
    """Describe a tool's result as a step: the section read, or the result itself."""
    if call["name"] == "read_section" and result.text.startswith("## "):
        document = DOCUMENT_NAMES[call["args"]["document"]]
        return "read", f"{document}: {result.text.splitlines()[0][3:]}"
    return "result", f"{call['name']}: {result.text[:RESULT_CHARS]}"


class StepLog(AgentMiddleware[AgentState[Any], ClaimContext, Any]):
    """Log each step the claim agent takes on its claim, for the dashboard."""

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command[Any]],
    ) -> ToolMessage | Command[Any]:
        """Log the tool the agent calls, and what it got back."""
        call = request.tool_call
        # LangChain types a tool call's runtime without the agent's context schema.
        claim_id = cast(ClaimContext, request.runtime.context).claim_id
        add_step(claim_id, "tool", f"{call['name']} {call['args']}")
        result = handler(request)
        if isinstance(result, ToolMessage):
            add_step(claim_id, *result_step(dict(call), result))
        return result

    def after_model(
        self, state: AgentState[Any], runtime: Runtime[ClaimContext]
    ) -> None:
        """Log the agent's reply once it stops calling tools."""
        message = state["messages"][-1]
        if isinstance(message, AIMessage) and not message.tool_calls and message.text:
            add_step(runtime.context.claim_id, "reply", message.text)


@after_model(can_jump_to=["model"])
def remind_to_finish(
    state: AgentState[Any], runtime: Runtime[RunContext]
) -> dict[str, Any] | None:
    """Send the queue agent back to work if it stops before finishing its run."""
    message = state["messages"][-1]
    if isinstance(message, AIMessage) and message.tool_calls:
        return None
    reminders = sum(m.text == REMINDER for m in state["messages"])
    if reminders >= MAX_REMINDERS or get_run(runtime.context.run_id)["finished_at"]:
        return None
    return {"messages": [HumanMessage(REMINDER)], "jump_to": "model"}


def instructions(agent: str) -> str:
    """Return one agent's instructions from the backend."""
    return backend.request("GET", f"/api/instructions/{agent}").raise_for_status().text


def claim_agent(llm: BaseChatModel | None = None) -> Runnable[Any, Any]:
    """Build the claim agent, which decides one claim and logs each step on it."""
    return create_agent(
        llm or model(),
        tools=tools.CLAIM_TOOLS,
        system_prompt=instructions("claim"),
        middleware=[retry(), StepLog()],
        context_schema=ClaimContext,
    )


def queue_agent(llm: BaseChatModel | None, cap: int) -> Runnable[Any, Any]:
    """Build the queue agent, which works a run's claims through the claim agent."""
    middleware: list[AgentMiddleware[Any, RunContext, Any]] = [
        retry(),
        ModelCallLimitMiddleware(run_limit=CALLS_PER_CLAIM * cap + 10),
        remind_to_finish,
    ]
    return create_agent(
        llm or model(),
        tools=tools.QUEUE_TOOLS,
        system_prompt=instructions("queue"),
        middleware=middleware,
        context_schema=RunContext,
    )


def get_run(run_id: str) -> dict[str, Any]:
    """Return a run with its to-do list and summary."""
    return backend.data("GET", f"/api/runs/{run_id}")


def new_run(cap: int) -> str:
    """Create a run capped at a number of claims and return its id."""
    return backend.data("POST", "/api/runs", {"cap": cap})["run_id"]


def close_run(run_id: str, summary: str) -> None:
    """Close a run that has not finished, with a summary of why."""
    if not get_run(run_id)["finished_at"]:
        backend.data("POST", f"/api/runs/{run_id}/stop", {"summary": summary})


def run_queue(
    cap: int,
    llm: BaseChatModel | None = None,
    claim_llm: BaseChatModel | None = None,
) -> str:
    """Work the waiting claims, up to the cap, and return the run's summary."""
    run_id = new_run(cap)
    context = RunContext(run_id, claim_agent(claim_llm))
    task = {"messages": [HumanMessage(f"Work the queue. The cap is {cap} claims.")]}
    try:
        queue_agent(llm, cap).invoke(task, context=context)
    finally:
        close_run(run_id, "Stopped before finishing")
    return get_run(run_id)["summary"]


def run_one(claim_id: str, llm: BaseChatModel | None = None) -> str:
    """Work one named claim in a run of its own and return its one-line report."""
    run_id = new_run(1)
    report = tools.work(claim_id, RunContext(run_id, claim_agent(llm)))
    close_run(run_id, report)
    return report
