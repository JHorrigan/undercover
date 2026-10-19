"""Queries for runs: the cap, the to-do list, failures and recovery."""

import sqlite3
from typing import Any
from uuid import uuid4

from backend import store

MAX_FAILURES = 2


def create_run(conn: sqlite3.Connection, cap: int) -> str:
    """Store a new run and return its id."""
    run_id = f"RUN-{uuid4().hex[:8]}"
    conn.execute(
        "INSERT INTO runs (run_id, cap, started_at) VALUES (?, ?, ?)",
        (run_id, cap, store.now()),
    )
    return run_id


def run_row(conn: sqlite3.Connection, run_id: str) -> dict[str, Any] | None:
    """Return one run without its to-do list, or None."""
    row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
    return dict(row) if row else None


def running(conn: sqlite3.Connection) -> bool:
    """Return whether a run is still going."""
    sql = "SELECT 1 FROM runs WHERE finished_at IS NULL"
    return conn.execute(sql).fetchone() is not None


def latest_run(conn: sqlite3.Connection) -> dict[str, Any] | None:
    """Return the latest run with its to-do list, or None before any run."""
    row = conn.execute("SELECT * FROM runs ORDER BY rowid DESC").fetchone()
    if row is None:
        return None
    return dict(row) | {"todos": todos(conn, row["run_id"])}


def todos(conn: sqlite3.Connection, run_id: str) -> list[dict[str, str]]:
    """Return a run's to-do list in order."""
    rows = conn.execute(
        "SELECT text, status FROM todos WHERE run_id = ? ORDER BY position", (run_id,)
    ).fetchall()
    return [dict(row) for row in rows]


def replace_todos(
    conn: sqlite3.Connection, run_id: str, items: list[dict[str, str]]
) -> None:
    """Replace a run's to-do list."""
    conn.execute("DELETE FROM todos WHERE run_id = ?", (run_id,))
    conn.executemany(
        "INSERT INTO todos VALUES (?, ?, ?, ?)",
        [(run_id, i, item["text"], item["status"]) for i, item in enumerate(items)],
    )


def claims_taken(conn: sqlite3.Connection, run_id: str) -> set[str]:
    """Return the claims a run has started."""
    sql = "SELECT claim_id FROM run_claims WHERE run_id = ?"
    return {row["claim_id"] for row in conn.execute(sql, (run_id,))}


def take_claim(conn: sqlite3.Connection, run_id: str, claim_id: str) -> None:
    """Count a claim against a run's cap."""
    conn.execute("INSERT OR IGNORE INTO run_claims VALUES (?, ?)", (run_id, claim_id))


def missed_claims(conn: sqlite3.Connection, run: dict[str, Any]) -> list[str]:
    """Return the waiting claims still within a run's cap."""
    taken = claims_taken(conn, run["run_id"])
    waiting = [id_ for id_, s in store.statuses(conn).items() if s == "waiting"]
    retries = [id_ for id_ in waiting if id_ in taken]
    room = run["cap"] - len(taken)
    return retries + [id_ for id_ in waiting if id_ not in taken][: max(room, 0)]


def finish(conn: sqlite3.Connection, run_id: str, summary: str) -> None:
    """Close a run with its summary."""
    conn.execute(
        "UPDATE runs SET finished_at = ?, summary = ? WHERE run_id = ?",
        (store.now(), summary, run_id),
    )


def fail_claim(conn: sqlite3.Connection, claim_id: str, error: str) -> None:
    """Requeue a claim that failed before its decision, or leave it for a handler."""
    if store.statuses(conn)[claim_id] != "in_progress":
        return
    store.insert_step(conn, claim_id, "error", error)
    conn.execute(
        "UPDATE claims SET failures = failures + 1 WHERE claim_id = ?", (claim_id,)
    )
    failed = store.failures(conn, claim_id) >= MAX_FAILURES
    status = "needs_handler" if failed else "waiting"
    store.set_status(conn, claim_id, status)


def recover(conn: sqlite3.Connection) -> None:
    """Fail claims left in progress and close runs left open by a stopped process."""
    stuck = [id_ for id_, s in store.statuses(conn).items() if s == "in_progress"]
    for claim_id in stuck:
        fail_claim(conn, claim_id, "Interrupted: the backend restarted")
    conn.execute(
        "UPDATE runs SET finished_at = ?, summary = 'Interrupted' "
        "WHERE finished_at IS NULL",
        (store.now(),),
    )
    conn.commit()
