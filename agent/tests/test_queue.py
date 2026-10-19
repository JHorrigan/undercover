import pytest
from langchain_core.messages import AIMessage

from agent import queue, runs
from agent.tests.conftest import broken_claim, call_tool, decide, stub
from backend import runs as run_routes


@pytest.fixture(autouse=True)
def no_retry_wait(monkeypatch):
    monkeypatch.setattr(
        "langchain.agents.middleware.model_retry.time.sleep", lambda _: None
    )


def todos(*items):
    return call_tool(
        "update_todos",
        {"todos": [{"text": f"Work {c}", "status": s} for c, s in items]},
    )


def work(claim_id):
    return call_tool("work_claim", {"claim_id": claim_id})


def finish(summary="Two claims decided."):
    return call_tool("finish_run", {"summary": summary})


def status(claim_id):
    return runs.get_claim(claim_id)["status"]


def test_cap_leaves_the_rest_waiting(use_test_backend):
    plan = stub(
        call_tool("list_waiting_claims", {}),
        todos(("CLM-1001", "to_do"), ("CLM-1002", "to_do")),
        work("CLM-1001"),
        work("CLM-1002"),
        work("CLM-1003"),
        todos(("CLM-1001", "done"), ("CLM-1002", "done")),
        finish(),
        AIMessage(content="Finished."),
    )
    claims = stub(*decide("CLM-1001"), *decide("CLM-1002", 0, "decline"))
    assert queue.run_queue(2, plan, claims) == "Two claims decided."
    queue_list = use_test_backend.get("/api/claims").json()
    decided = [c["claim_id"] for c in queue_list if c["status"] == "decided"]
    assert decided == ["CLM-1001", "CLM-1002"]
    assert sum(c["status"] == "waiting" for c in queue_list) == 23
    assert status("CLM-1003") == "waiting"
    run = runs.latest_run()
    assert run["todos"] == [
        {"text": "Work CLM-1001", "status": "done"},
        {"text": "Work CLM-1002", "status": "done"},
    ]


def test_failed_claim_does_not_stop_the_run_and_is_tried_again():
    plan = stub(
        work("CLM-1001"),
        work("CLM-1002"),
        work("CLM-1001"),
        finish(),
        AIMessage(content="."),
    )
    claims = stub(*broken_claim(), *decide("CLM-1002"), *decide("CLM-1001"))
    queue.run_queue(2, plan, claims)
    assert status("CLM-1002") == "decided"
    assert status("CLM-1001") == "decided"
    assert runs.get_claim("CLM-1001")["failures"] == 1
    assert runs.latest_run()["summary"] == "Two claims decided."


def test_claim_failing_twice_is_left_for_a_handler():
    plan = stub(
        work("CLM-1001"),
        work("CLM-1001"),
        todos(("CLM-1001", "for_handler")),
        finish("CLM-1001 left for a handler."),
        AIMessage(content="."),
    )
    queue.run_queue(1, plan, stub(*broken_claim(), *broken_claim()))
    assert status("CLM-1001") == "needs_handler"
    assert runs.latest_run()["todos"][0]["status"] == "for_handler"


def test_missed_claims_are_caught_before_finishing():
    plan = stub(
        work("CLM-1001"),
        finish("Too early."),
        work("CLM-1002"),
        finish(),
        AIMessage(content="."),
    )
    queue.run_queue(2, plan, stub(*decide("CLM-1001"), *decide("CLM-1002")))
    assert status("CLM-1002") == "decided"
    assert runs.latest_run()["summary"] == "Two claims decided."


def test_agent_that_stops_early_is_reminded():
    plan = stub(
        AIMessage(content="All done."),
        work("CLM-1001"),
        finish("One claim decided."),
        AIMessage(content="."),
    )
    assert queue.run_queue(1, plan, stub(*decide("CLM-1001"))) == "One claim decided."


def test_run_that_never_finishes_is_stopped():
    plan = stub(*[AIMessage(content="All done.")] * 3)
    assert queue.run_queue(1, plan, stub()) == "Stopped before finishing"
    assert runs.latest_run()["finished_at"]


def test_start_run_route(monkeypatch, use_test_backend):
    started = []
    monkeypatch.setattr(run_routes.queue, "run_queue", started.append)
    response = use_test_backend.post("/api/runs/start", json={"cap": 1})
    assert response.json() == {"status": "started"}
    assert started == [1]
    runs.create_run(1)
    assert use_test_backend.post("/api/runs/start", json={"cap": 1}).status_code == 409


def test_queue_instructions():
    text = queue.tools.call("GET", "/api/instructions/queue")
    assert text.startswith("# Running the queue")
    assert "finish_run" in text
