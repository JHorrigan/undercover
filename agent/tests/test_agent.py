from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, ToolMessage

from agent import claim, model, runs, tools
from agent.tests.conftest import StubModel, decide, stub
from backend import runs as run_routes


class FailingModel(StubModel):
    """A stub model that raises a provider error a set number of times first."""

    failures: int = 0

    def _generate(self, *args, **kwargs):
        if self.failures:
            self.failures -= 1
            raise RuntimeError("Provider returned 502")
        return super()._generate(*args, **kwargs)


@pytest.fixture(autouse=True)
def no_retry_wait(monkeypatch):
    monkeypatch.setattr(
        "langchain.agents.middleware.model_retry.time.sleep", lambda _: None
    )


def steps(client, claim_id="CLM-1001"):
    return client.get(f"/api/claims/{claim_id}/steps").json()


def test_run_one_approves_and_pays(use_test_backend):
    report = claim.run_one("CLM-1001", stub(*decide("CLM-1001")))
    assert report == "CLM-1001: approve, $420.00, paid"
    reads = [s["text"] for s in steps(use_test_backend) if s["kind"] == "read"]
    assert reads == [
        "Policy wording: 3. Trip Delay",
        "Claims manual: 10. Meals without receipts",
    ]
    assert steps(use_test_backend)[-1]["kind"] == "reply"
    assert use_test_backend.get("/api/runs/latest").json()["summary"] == report


def test_payment_over_limit_is_blocked(use_test_backend):
    report = claim.run_one("CLM-1001", stub(*decide("CLM-1001", 1500.0)))
    assert report == "CLM-1001: approve, $1,500.00, waiting for sign-off"
    assert "Error 403" in steps(use_test_backend)[-2]["text"]


def test_model_error_is_retried(use_test_backend):
    flaky = FailingModel(messages=iter(decide("CLM-1001")), failures=1)
    assert claim.run_one("CLM-1001", flaky) == "CLM-1001: approve, $420.00, paid"


def test_failed_claim_goes_back_in_the_queue(use_test_backend):
    run_id = runs.create_run(1)
    broken = FailingModel(messages=iter([]), failures=3)
    report = claim.work_claim("CLM-1001", run_id, broken)
    assert report.startswith("CLM-1001 failed: RuntimeError: Provider returned 502")
    assert report.endswith("Back in the queue")
    assert runs.get_claim("CLM-1001")["status"] == "waiting"
    assert steps(use_test_backend)[-1]["kind"] == "error"


def test_stopping_without_a_decision_is_a_failure():
    run_id = runs.create_run(1)
    gives_up = stub(*decide("CLM-1001")[:2], AIMessage(content="I can't decide."))
    report = claim.work_claim("CLM-1001", run_id, gives_up)
    assert "Stopped without recording a decision" in report
    assert runs.get_claim("CLM-1001")["failures"] == 1


def test_failing_twice_leaves_claim_for_handler():
    broken = FailingModel(messages=iter([]), failures=6)
    report = claim.run_one("CLM-1001", broken)
    assert report.endswith("Left for a handler")
    assert runs.get_claim("CLM-1001")["status"] == "needs_handler"


def test_claim_not_started_is_reported():
    run_id = runs.create_run(1)
    claim.work_claim("CLM-1001", run_id, stub(*decide("CLM-1001")))
    report = claim.work_claim("CLM-1002", run_id, stub())
    assert report.startswith("CLM-1002 not started: Error 409")
    assert "cap of 1" in report


def test_tools_read_records():
    assert '"plan":"premium"' in tools.get_policy.invoke({"policy_id": "POL-2001"})
    assert "Maya Patel" in tools.get_customer.invoke({"customer_id": "CUS-3001"})
    assert "economy" in tools.list_plans.invoke({})
    assert "Repeat claims" in tools.list_documents.invoke({})
    section = {"document": "claims_manual", "section": "9"}
    assert tools.read_section.invoke(section).startswith(
        "Claims manual\n## 9. Repeat claims"
    )
    assert tools.get_claim.invoke({"claim_id": "CLM-9999"}).startswith("Error 404")


def test_claim_instructions():
    text = claim.instructions()
    assert text.startswith("# Working a claim")
    assert "claims manual" in text
    assert "evals" not in text


def test_agent_only_uses_the_api():
    for source in Path(claim.__file__).parent.glob("*.py"):
        code = source.read_text(encoding="utf-8")
        for forbidden in ("pathlib", "open(", "data/", "evals", "sqlite"):
            assert forbidden not in code, f"{source.name} uses {forbidden}"


def test_run_agent_route(monkeypatch, use_test_backend):
    client = use_test_backend
    started = []
    monkeypatch.setattr(run_routes.agent, "run_one", started.append)
    assert client.post("/api/claims/CLM-1001/run").json() == {"status": "started"}
    assert started == ["CLM-1001"]
    assert client.post("/api/claims/CLM-9999/run").status_code == 404
    run_id = runs.create_run(1)
    assert client.post("/api/claims/CLM-1002/run").status_code == 409
    client.post("/api/claims/CLM-1002/start", json={"run_id": run_id})
    assert client.post("/api/claims/CLM-1002/run").status_code == 409


def test_model_name(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("MODEL_NAME", raising=False)
    default = model.model()
    assert default.model_name == "deepseek/deepseek-v4.1-flash"
    assert default.reasoning_effort == "low"
    monkeypatch.setenv("MODEL_NAME", "openrouter/free")
    assert model.model().model_name == "openrouter/free"


def test_section_read_is_a_read_step():
    message = ToolMessage(
        content="Claims manual\n## 9. Repeat claims\nText.",
        name="read_section",
        tool_call_id="1",
    )
    assert claim.describe(message) == [("read", "Claims manual: 9. Repeat claims")]
    missing = ToolMessage(
        content="Claims manual\nError 404: missing",
        name="read_section",
        tool_call_id="2",
    )
    assert claim.describe(missing)[0][0] == "result"
