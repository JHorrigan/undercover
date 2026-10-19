import sqlite3

from fastapi.testclient import TestClient

from backend.db import db_path
from backend.main import app


def new_run(client, cap):
    return client.post("/api/runs", json={"cap": cap}).json()["run_id"]


def start(client, claim_id, run_id):
    return client.post(f"/api/claims/{claim_id}/start", json={"run_id": run_id})


def fail(client, claim_id):
    return client.post(f"/api/claims/{claim_id}/fail", json={"error": "Timed out"})


def finish(client, run_id):
    return client.post(f"/api/runs/{run_id}/finish", json={"summary": "Done."})


def decline(client, claim_id):
    body = {
        "decision": "decline",
        "payout": 0,
        "reason": "Not covered.",
        "policy_section": "9. General exclusions",
    }
    return client.post(f"/api/claims/{claim_id}/decision", json=body)


def test_no_run_yet(client):
    assert client.get("/api/runs/latest").json() is None


def test_one_run_at_a_time(client):
    run_id = new_run(client, 2)
    assert client.post("/api/runs", json={"cap": 1}).status_code == 409
    assert client.post("/api/runs", json={"cap": 0}).status_code == 422
    assert client.get("/api/runs/latest").json()["run_id"] == run_id


def test_cap_limits_new_claims(client):
    run_id = new_run(client, 2)
    assert start(client, "CLM-1001", run_id).json()["status"] == "in_progress"
    assert start(client, "CLM-1002", run_id).status_code == 200
    refused = start(client, "CLM-1003", run_id)
    assert refused.status_code == 409
    assert "cap of 2" in refused.json()["detail"]
    fail(client, "CLM-1001")
    assert start(client, "CLM-1001", run_id).status_code == 200


def test_start_needs_an_open_run(client):
    assert start(client, "CLM-1001", "RUN-missing").status_code == 404
    run_id = new_run(client, 1)
    assert finish(client, run_id).status_code == 409
    start(client, "CLM-1001", run_id)
    decline(client, "CLM-1001")
    assert finish(client, run_id).status_code == 200
    assert start(client, "CLM-1002", run_id).status_code == 409
    assert finish(client, run_id).status_code == 409


def test_fail_twice_leaves_claim_for_handler(client):
    run_id = new_run(client, 1)
    start(client, "CLM-1001", run_id)
    claim = fail(client, "CLM-1001").json()
    assert (claim["status"], claim["failures"]) == ("waiting", 1)
    start(client, "CLM-1001", run_id)
    claim = fail(client, "CLM-1001").json()
    assert (claim["status"], claim["failures"]) == ("needs_handler", 2)
    steps = client.get("/api/claims/CLM-1001/steps").json()
    assert [s["kind"] for s in steps] == ["error", "error"]


def test_fail_leaves_decided_claim(client):
    run_id = new_run(client, 1)
    start(client, "CLM-1001", run_id)
    decline(client, "CLM-1001")
    claim = fail(client, "CLM-1001").json()
    assert (claim["status"], claim["failures"]) == ("decided", 0)
    assert fail(client, "CLM-9999").status_code == 404


def test_todos(client):
    run_id = new_run(client, 2)
    todos = [
        {"text": "Work CLM-1002", "status": "done"},
        {"text": "Work CLM-1001", "status": "in_progress"},
    ]
    put = client.put(f"/api/runs/{run_id}/todos", json={"todos": todos})
    assert put.status_code == 200
    assert client.get("/api/runs/latest").json()["todos"] == todos
    bad = [{"text": "Work CLM-1003", "status": "skipped"}]
    assert (
        client.put(f"/api/runs/{run_id}/todos", json={"todos": bad}).status_code == 422
    )


def test_finish_refuses_missed_claims(client):
    run_id = new_run(client, 2)
    start(client, "CLM-1001", run_id)
    fail(client, "CLM-1001")
    refused = finish(client, run_id)
    assert refused.status_code == 409
    assert (
        refused.json()["detail"] == "Waiting claims within the cap: CLM-1001, CLM-1002"
    )
    start(client, "CLM-1001", run_id)
    decline(client, "CLM-1001")
    start(client, "CLM-1002", run_id)
    decline(client, "CLM-1002")
    assert finish(client, run_id).json() == {"status": "finished"}
    run = client.get("/api/runs/latest").json()
    assert (run["summary"], run["finished_at"] is not None) == ("Done.", True)


def test_restart_recovers_stuck_claims_and_runs(client):
    run_id = new_run(client, 1)
    start(client, "CLM-1001", run_id)
    with TestClient(app) as restarted:
        claim = restarted.get("/api/claims/CLM-1001").json()
        run = restarted.get("/api/runs/latest").json()
    assert (claim["status"], claim["failures"]) == ("waiting", 1)
    assert run["summary"] == "Interrupted"
    conn = sqlite3.connect(db_path())
    assert conn.execute("SELECT count(*) FROM runs").fetchone() == (1,)


def test_stop_closes_a_run_with_missed_claims(client):
    run_id = new_run(client, 1)
    body = {"summary": "Stopped before finishing"}
    assert client.post(f"/api/runs/{run_id}/stop", json=body).status_code == 200
    assert client.get("/api/runs/latest").json()["summary"] == body["summary"]
    assert client.post(f"/api/runs/{run_id}/stop", json=body).status_code == 409
