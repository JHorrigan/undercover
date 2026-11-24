"""Reading claims, the queue, policies, history and the wording."""

import json
import sqlite3

from fastapi import HTTPException

from backend.db import data_dir
from backend.privacy import personal_details, withhold


def find(connection: sqlite3.Connection, table: str, key: str, value: str) -> dict:
    """Return one record from a table by its key, or a 404."""
    row = connection.execute(
        f"SELECT record FROM {table} WHERE {key} = ?",  # noqa: S608 - fixed names
        (value,),
    ).fetchone()
    if row is None:
        raise HTTPException(404, f"No {value}")
    return json.loads(row["record"])


def setting(connection: sqlite3.Connection, name: str) -> dict:
    """Return one of the company's settings."""
    return find(connection, "settings", "name", name)


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


def get_claim_evidence(connection: sqlite3.Connection, claim_id: str) -> dict:
    """Return the claim as the agent reads it, with personal details withheld."""
    claim = find_claim(connection, claim_id)
    customer = find(connection, "customers", "customer_id", claim["customer_id"])
    del claim["status"]
    return withhold(claim, personal_details(customer))


def take_next_claim(connection: sqlite3.Connection) -> dict | None:
    """Move the oldest waiting claim to in progress and return it, or None."""
    row = connection.execute(
        """
        UPDATE claims SET status = 'in_progress'
        WHERE claim_id = (
            SELECT claim_id FROM claims WHERE status = 'waiting'
            ORDER BY record ->> '$.submitted_on', claim_id LIMIT 1
        )
        RETURNING claim_id
        """
    ).fetchone()
    return find_claim(connection, row["claim_id"]) if row else None


def get_policy(connection: sqlite3.Connection, claim_id: str) -> dict:
    """Return the claim's policy, its plan's limits and the rules for add-ons."""
    policy = find(
        connection,
        "policies",
        "policy_id",
        find_claim(connection, claim_id)["policy_id"],
    )
    return {
        "policy": policy,
        "plan": find(connection, "plans", "plan", policy["plan"]),
        "plan_rules": setting(connection, "plan_rules"),
    }


def get_claim_history(connection: sqlite3.Connection, claim_id: str) -> list[dict]:
    """Return the customer's earlier claims, with none of their personal details."""
    customer_id = find_claim(connection, claim_id)["customer_id"]
    return find(connection, "customers", "customer_id", customer_id)["previous_claims"]


def get_policy_wording(connection: sqlite3.Connection) -> dict:
    """Return the policy wording in force and its version."""
    return {
        "version": setting(connection, "company")["policy_wording_version"],
        "text": (data_dir() / "policy_wording.md").read_text(encoding="utf-8"),
    }
