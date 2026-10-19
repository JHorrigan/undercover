"""Queries over the UnderCover database."""

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

SUMMARY_FIELDS = (
    "claim_id",
    "customer_id",
    "claim_type",
    "summary",
    "amount_claimed",
    "submitted_on",
)


def now() -> str:
    """Return the current time in UTC, to the second."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def set_status(conn: sqlite3.Connection, claim_id: str, status: str) -> None:
    """Move a claim to a new status."""
    conn.execute("UPDATE claims SET status = ? WHERE claim_id = ?", (status, claim_id))


def insert_step(conn: sqlite3.Connection, claim_id: str, kind: str, text: str) -> None:
    """Store one step the agent took on a claim."""
    conn.execute(
        "INSERT INTO steps (claim_id, at, kind, text) VALUES (?, ?, ?, ?)",
        (claim_id, now(), kind, text),
    )


def record(conn: sqlite3.Connection, kind: str, id_: str) -> Any:
    """Return one seeded record, or None if it doesn't exist."""
    row = conn.execute(
        "SELECT body FROM records WHERE kind = ? AND id = ?", (kind, id_)
    ).fetchone()
    return json.loads(row["body"]) if row else None


def records(conn: sqlite3.Connection, kind: str) -> list[Any]:
    """Return every seeded record of one kind, in id order."""
    rows = conn.execute(
        "SELECT body FROM records WHERE kind = ? ORDER BY id", (kind,)
    ).fetchall()
    return [json.loads(row["body"]) for row in rows]


def statuses(conn: sqlite3.Connection) -> dict[str, str]:
    """Return each claim's status by claim id."""
    rows = conn.execute("SELECT claim_id, status FROM claims").fetchall()
    return {row["claim_id"]: row["status"] for row in rows}


def claim_summaries(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return the queue: one short row per claim with its status."""
    names = {c["customer_id"]: c["name"] for c in records(conn, "customer")}
    status = statuses(conn)
    return [
        {field: claim[field] for field in SUMMARY_FIELDS}
        | {"customer_name": names[claim["customer_id"]]}
        | {"status": status[claim["claim_id"]]}
        for claim in records(conn, "claim")
    ]


def claim_detail(conn: sqlite3.Connection, claim_id: str) -> dict[str, Any] | None:
    """Return one claim in full with its status, or None if it doesn't exist."""
    claim = record(conn, "claim", claim_id)
    if claim is None:
        return None
    return claim | {
        "status": statuses(conn)[claim_id],
        "decision": row_for(conn, "decisions", claim_id),
        "payment": row_for(conn, "payments", claim_id),
        "sign_off": sign_off(conn, claim_id),
        "failures": failures(conn, claim_id),
    }


def failures(conn: sqlite3.Connection, claim_id: str) -> int:
    """Return how many times work on a claim has failed."""
    sql = "SELECT failures FROM claims WHERE claim_id = ?"
    return conn.execute(sql, (claim_id,)).fetchone()["failures"]


def sign_off(conn: sqlite3.Connection, claim_id: str) -> Any:
    """Return a claim's sign-off with the handler's name, or None."""
    row = row_for(conn, "sign_offs", claim_id)
    if row is None:
        return None
    return row | {"handler_name": record(conn, "handler", row["handler_id"])["name"]}


def row_for(conn: sqlite3.Connection, table: str, claim_id: str) -> Any:
    """Return a claim's row from one outcome table as a dict, or None."""
    row = conn.execute(
        f"SELECT * FROM {table} WHERE claim_id = ?",  # noqa: S608
        (claim_id,),
    ).fetchone()
    return dict(row) if row else None


def payout_limit(conn: sqlite3.Connection) -> float:
    """Return the payout above which a handler must sign off."""
    return record(conn, "company", "settings")["payout_approval_limit"]
