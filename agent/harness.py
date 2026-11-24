"""The harness: the model, the middleware that records steps, and building the agent."""

import json
import os
from collections.abc import Callable
from typing import Any, cast

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
    ToolCallRequest,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from pydantic import SecretStr

from agent.api import fetch, record_step
from agent.tools import TOOLS, Context

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-6-luna"


def model() -> ChatOpenAI:
    """Return the model named in MODEL_NAME, or GPT-6 Luna at low effort by default."""
    name = os.getenv("MODEL_NAME")
    return ChatOpenAI(
        model=name or DEFAULT_MODEL,
        base_url=OPENROUTER_BASE_URL,
        api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]),
        reasoning_effort=None if name else "low",
    )


def call_cost(message: AIMessage) -> float:
    """Return what one model call cost, as OpenRouter reports it."""
    return message.response_metadata["token_usage"]["cost"]


class RecordSteps(AgentMiddleware[AgentState[Any], Context]):
    """Record every model call, with its cost, and every tool call as a step."""

    def wrap_model_call(
        self,
        request: ModelRequest[Context],
        handler: Callable[[ModelRequest[Context]], ModelResponse[Any]],
    ) -> ModelResponse[Any]:
        """Record what the model chose to do next and what the call cost."""
        response = handler(request)
        message = response.result[-1]
        if isinstance(message, AIMessage):
            names = ", ".join(call["name"] for call in message.tool_calls)
            record_step(
                request.runtime.context.claim_id,
                f"Chose {names or 'to reply'}",
                call_cost(message),
            )
        return response

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command[Any]],
    ) -> ToolMessage | Command[Any]:
        """Record the tool called and its arguments."""
        # LangChain leaves the tool request's runtime untyped; the context is ours.
        context = cast(Context, request.runtime.context)
        call = request.tool_call
        args = json.dumps(call["args"]) if call["args"] else ""
        record_step(context.claim_id, f"{call['name']} {args}".strip(), 0)
        return handler(request)


def build(llm: BaseChatModel):
    """Build the UnderCover Agent with its tools, instructions and step recording."""
    return create_agent(
        llm,
        tools=TOOLS,
        system_prompt=fetch("/api/instructions")["text"],
        middleware=[RecordSteps()],
        context_schema=Context,
    )
