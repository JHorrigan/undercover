"""The UnderCover Agent."""

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel

from agent.harness import build, model
from agent.tools import Context

load_dotenv(override=True)


def run(claim_id: str, thread_id: str, llm: BaseChatModel | None = None) -> str:
    """Run the agent on one claim and return its final reply."""
    agent = build(llm or model())
    result = agent.invoke(
        {"messages": [{"role": "user", "content": f"Decide claim {claim_id}."}]},
        config={"configurable": {"thread_id": thread_id}},
        context=Context(claim_id=claim_id),
    )
    return result["messages"][-1].text
