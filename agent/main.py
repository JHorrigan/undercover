"""The UnderCover Agent."""

import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from agent import tools

load_dotenv(override=True)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-6-luna"
RESULT_CHARS = 300


def model() -> ChatOpenAI:
    """Return the model named in MODEL_NAME, or GPT-6 Luna by default."""
    name = os.getenv("MODEL_NAME")
    return ChatOpenAI(
        model=name or DEFAULT_MODEL,
        base_url=OPENROUTER_BASE_URL,
        api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]),
        reasoning_effort=None if name else "low",
    )


def describe(message: BaseMessage) -> list[tuple[str, str]]:
    """Turn one agent message into steps for the dashboard, as (kind, text)."""
    if isinstance(message, ToolMessage):
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
