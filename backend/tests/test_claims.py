import shutil
from contextlib import closing

from backend.db import connect
from backend.seed import read, seed


def count(table):
    with closing(connect()) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]  # noqa: S608


def test_seed_loads_every_record(seeded):
    assert count("claims") == 25
    assert count("policies") == 50
    assert count("customers") == 49
    assert count("handlers") == 3
    assert count("plans") == 3


def test_seed_needs_nothing_from_the_evals(tmp_path, monkeypatch):
    shutil.copytree("data", tmp_path / "data", ignore=shutil.ignore_patterns("evals"))
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    seed(read("claims.json"))
    assert count("claims") == 25


def test_queue_lists_every_claim_waiting(client):
    queue = client.get("/api/claims").json()
    assert len(queue) == 25
    assert {claim["status"] for claim in queue} == {"waiting"}
    assert [claim["submitted_on"] for claim in queue] == sorted(
        claim["submitted_on"] for claim in queue
    )


def test_get_claim_in_full(client):
    claim = client.get("/api/claims/CLM-1001").json()
    assert claim["claim_id"] == "CLM-1001"
    assert len(claim["items"]) == 3
    assert claim["documents"]
    assert claim["status"] == "waiting"
    assert claim["decision"] is None
    assert claim["payment"] is None
    assert claim["steps"] == []


def test_unknown_claim_is_not_found(client):
    assert client.get("/api/claims/CLM-0000").status_code == 404
