from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from agent import main
from claims.research import evaluate


class StubModel(GenericFakeChatModel):
    """A chat model that gives scripted replies in place of a real model."""

    def bind_tools(self, tools, **kwargs):
        return self


def deciding(verdict):
    """Return a stub model factory that records this decision at $0.01 a call."""
    usage = {"token_usage": {"cost": 0.01}}
    args = {"decision": verdict, "payout": 0, "reason": "As read.", "section": "9"}

    def model():
        return StubModel(
            messages=iter(
                [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {"name": "record_decision", "args": args, "id": "1"}
                        ],
                        response_metadata=usage,
                    ),
                    AIMessage(content="Done.", response_metadata=usage),
                ]
            )
        )

    return model


def isolate(monkeypatch):
    """Run on a spare port, and put the environment back after the test."""
    monkeypatch.setattr(evaluate, "EVAL_URL", "http://127.0.0.1:8013")
    monkeypatch.setenv("DATABASE_PATH", "unused.db")
    monkeypatch.setenv("BACKEND_URL", "http://127.0.0.1:8013")


def test_evaluate_runs_a_set_end_to_end(monkeypatch):
    isolate(monkeypatch)
    monkeypatch.setattr(main, "model", deciding("refer"))
    scored = evaluate.report("tiny", evaluate.run("tiny"))
    _, handlers = evaluate.claims_and_decisions("tiny")
    referred = sum(decision["decision"] == "refer" for decision in handlers.values())
    scores = scored["scores"]
    assert scores["claims"] == 5
    assert {result["decision"] for result in scored["results"]} == {"refer"}
    assert scores["decision_accuracy"] == referred / 5
    assert scores["straight_through_rate"] == 0
    assert scores["model_cost_per_claim"] == 0.02


def test_the_security_claim_passes_when_declined(monkeypatch):
    isolate(monkeypatch)
    monkeypatch.setattr(main, "model", deciding("decline"))
    scored = evaluate.report("security", evaluate.run("security"))
    assert scored["scores"]["security_pass"] is True


def test_save_names_the_record_by_date_and_set(monkeypatch, tmp_path):
    monkeypatch.setattr(evaluate, "RESULTS", tmp_path)
    path = evaluate.save({"set": "tiny", "scores": {}, "results": []})
    assert path.name.endswith("-tiny.json")
    assert path.read_text().startswith("{")
