from pathlib import Path

from langchain_core.messages import AIMessage, ToolMessage

from agent import harness, tools
from agent.backend import client as real_client
from agent.tests.conftest import StubModel, decide, stub
from agent.tools import RunContext
from backend import run_routes


class FailingModel(StubModel):
    """A stub model that raises a provider error a set number of times first."""

    failures: int = 0

    def _generate(self, *args, **kwargs):
        if self.failures:
            self.failures -= 1
            raise RuntimeError("Provider returned 502")
        return super()._generate(*args, **kwargs)


def steps(client, claim_id="CLM-1001"):
    return client.get(f"/api/claims/{claim_id}/steps").json()


def claim(client, claim_id="CLM-1001"):
    return client.get(f"/api/claims/{claim_id}").json()


def work(llm, claim_id="CLM-1001", run_id=None):
    run_id = run_id or harness.new_run(1)
    return tools.work(claim_id, RunContext(run_id, harness.claim_agent(llm)))


def test_run_one_approves_and_pays(use_test_backend):
    report = harness.run_one("CLM-1001", stub(*decide("CLM-1001")))
    assert report == "CLM-1001: approve, $420.00, paid"
    logged = steps(use_test_backend)
    assert logged[0]["text"] == "get_claim {}"
    assert [s["text"] for s in logged if s["kind"] == "read"] == [
        "Policy wording: 3. Trip Delay",
        "Claims manual: 10. Meals without receipts",
    ]
    assert (logged[-1]["kind"], logged[-1]["text"]) == ("reply", "CLM-1001: approve.")
    assert use_test_backend.get("/api/runs/latest").json()["summary"] == report


def test_claim_tools_act_only_on_the_agents_claim():
    for tool in (tools.get_claim, tools.record_decision, tools.pay_claim):
        assert "claim_id" not in tool.args


def test_payment_over_limit_is_blocked(use_test_backend):
    report = harness.run_one("CLM-1001", stub(*decide("CLM-1001", 1500.0)))
    assert report == "CLM-1001: approve, $1,500.00, waiting for sign-off"
    assert "Error 403" in steps(use_test_backend)[-2]["text"]


def test_model_error_is_retried():
    flaky = FailingModel(messages=iter(decide("CLM-1001")), failures=1)
    assert harness.run_one("CLM-1001", flaky) == "CLM-1001: approve, $420.00, paid"


def test_failed_claim_goes_back_in_the_queue(use_test_backend):
    report = work(FailingModel(messages=iter([]), failures=3))
    assert report.startswith("CLM-1001 failed: RuntimeError: Provider returned 502")
    assert report.endswith("Back in the queue")
    assert claim(use_test_backend)["status"] == "waiting"
    assert steps(use_test_backend)[-1]["kind"] == "error"


def test_failed_single_claim_closes_its_run(use_test_backend):
    report = harness.run_one("CLM-1001", FailingModel(messages=iter([]), failures=3))
    assert report.endswith("Back in the queue")
    run = use_test_backend.get("/api/runs/latest").json()
    assert run["finished_at"]
    assert run["summary"] == report


def test_stopping_without_a_decision_is_a_failure(use_test_backend):
    report = work(stub(*decide("CLM-1001")[:2], AIMessage(content="I can't decide.")))
    assert "Stopped without recording a decision" in report
    assert claim(use_test_backend)["failures"] == 1


def test_failing_twice_leaves_claim_for_handler(use_test_backend):
    run_id = harness.new_run(1)
    work(FailingModel(messages=iter([]), failures=3), run_id=run_id)
    report = work(FailingModel(messages=iter([]), failures=3), run_id=run_id)
    assert report.endswith("Left for a handler")
    assert claim(use_test_backend)["status"] == "needs_handler"


def test_claim_not_started_is_reported():
    run_id = harness.new_run(1)
    work(stub(*decide("CLM-1001")), run_id=run_id)
    report = work(stub(), "CLM-1002", run_id)
    assert report.startswith("CLM-1002 not started:")
    assert "cap of 1" in report


def test_tools_read_records():
    assert '"plan":"premium"' in tools.get_policy.invoke({"policy_id": "POL-2001"})
    assert "Maya Patel" in tools.get_customer.invoke({"customer_id": "CUS-3001"})
    assert "economy" in tools.list_plans.invoke({})
    assert "Repeat claims" in tools.list_documents.invoke({})
    section = {"document": "claims_manual", "section": "9"}
    assert tools.read_section.invoke(section).startswith("## 9. Repeat claims")
    missing = {"document": "claims_manual", "section": "99"}
    assert tools.read_section.invoke(missing).startswith("Error 404")


def test_claim_instructions():
    text = harness.instructions("claim")
    assert text.startswith("# Working a claim")
    assert "claims manual" in text
    assert "evals" not in text


def test_agent_only_uses_the_api():
    for source in Path(harness.__file__).parent.glob("*.py"):
        code = source.read_text(encoding="utf-8")
        for forbidden in ("pathlib", "open(", "data/", "evals", "sqlite"):
            assert forbidden not in code, f"{source.name} uses {forbidden}"


def test_backend_address_comes_from_the_environment(monkeypatch):
    monkeypatch.delenv("UNDERCOVER_API", raising=False)
    assert str(real_client().base_url) == "http://127.0.0.1:8000"
    monkeypatch.setenv("UNDERCOVER_API", "http://127.0.0.1:8100")
    assert str(real_client().base_url) == "http://127.0.0.1:8100"


def test_run_agent_route(monkeypatch, use_test_backend):
    client = use_test_backend
    started = []
    monkeypatch.setattr(run_routes.harness, "run_one", started.append)
    assert client.post("/api/claims/CLM-1001/run").json() == {"status": "started"}
    assert started == ["CLM-1001"]
    assert client.post("/api/claims/CLM-9999/run").status_code == 404
    run_id = harness.new_run(1)
    assert client.post("/api/claims/CLM-1002/run").status_code == 409
    client.post("/api/claims/CLM-1002/start", json={"run_id": run_id})
    assert client.post("/api/claims/CLM-1002/run").status_code == 409


def test_model_name(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("MODEL_NAME", raising=False)
    default = harness.model()
    assert default.model_name == "deepseek/deepseek-v4.1-flash"
    assert default.reasoning_effort == "low"
    monkeypatch.setenv("MODEL_NAME", "openrouter/free")
    assert harness.model().model_name == "openrouter/free"


def test_section_read_is_a_read_step():
    call = {"name": "read_section", "args": {"document": "claims_manual"}}
    read = ToolMessage(content="## 9. Repeat claims\nText.", tool_call_id="1")
    assert harness.result_step(call, read) == (
        "read",
        "Claims manual: 9. Repeat claims",
    )
    missing = ToolMessage(content="Error 404: Section not found", tool_call_id="2")
    assert harness.result_step(call, missing)[0] == "result"
