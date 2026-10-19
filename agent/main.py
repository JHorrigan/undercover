"""The UnderCover Agent."""

from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from agent import tools
from agent.model import model

RESULT_CHARS = 300


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


def start(claim_id: str) -> str:
    """Mark the claim in progress and return the agent's instructions."""
    with tools.backend() as client:
        client.post(f"/api/claims/{claim_id}/start").raise_for_status()
        return client.get("/api/instructions").raise_for_status().text


def run(claim_id: str, thread_id: str, llm: BaseChatModel | None = None) -> str:
    """Run the agent on one claim, logging each step, and return its final reply."""
    instructions = start(claim_id)
    agent = create_agent(llm or model(), tools=tools.TOOLS, system_prompt=instructions)
    reply = ""
    for update in agent.stream(
        {"messages": [{"role": "user", "content": f"Decide claim {claim_id}."}]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode="updates",
    ):
        for message in messages_in(update):
            for kind, text in describe(message):
                add_step(claim_id, kind, text)
            reply = message.text
    return reply


def messages_in(update: dict[str, Any]) -> list[BaseMessage]:
    """Return the new messages in one streamed update from the agent."""
    return [m for node in update.values() if node for m in node.get("messages", [])]
