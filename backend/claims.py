"""Reading claims and the queue."""

import json
import sqlite3

from fastapi import HTTPException


def list_claims(connection: sqlite3.Connection) -> list[dict]:
    """Return the queue: every claim's headline fields and status, oldest first."""
    rows = connection.execute(
        """
        SELECT claim_id,
               record ->> '$.claim_type' AS claim_type,
               record ->> '$.summary' AS summary,
               record ->> '$.submitted_on' AS submitted_on,
               record ->> '$.amount_claimed' AS amount_claimed,
               status
        FROM claims
        ORDER BY submitted_on, claim_id
        """
    ).fetchall()
    return [dict(row) for row in rows]


def find_claim(connection: sqlite3.Connection, claim_id: str) -> dict:
    """Return one claim's record and status, or a 404."""
    row = connection.execute(
        "SELECT status, record FROM claims WHERE claim_id = ?", (claim_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, f"No claim {claim_id}")
    return {**json.loads(row["record"]), "status": row["status"]}


def get_claim(connection: sqlite3.Connection, claim_id: str) -> dict:
    """Return one claim in full, with its decision, payment and steps."""
    claim = find_claim(connection, claim_id)
    decision = connection.execute(
        "SELECT decision, payout, reason, section, signed_off_by FROM decisions"
        " WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    payment = connection.execute(
        "SELECT amount, paid_at FROM payments WHERE claim_id = ?", (claim_id,)
    ).fetchone()
    steps = connection.execute(
        "SELECT recorded_at, text, cost FROM steps WHERE claim_id = ? ORDER BY step_id",
        (claim_id,),
    ).fetchall()
    return {
        **claim,
        "decision": dict(decision) if decision else None,
        "payment": dict(payment) if payment else None,
        "steps": [dict(step) for step in steps],
    }
