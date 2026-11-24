"""The rules for decisions, payments, sign-off and the agent's steps."""

import sqlite3
from datetime import UTC, datetime
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field

from backend.claims import find, find_claim, setting


class Decision(BaseModel):
    """A decision on one claim."""

    decision: Literal["approve", "decline", "refer"]
    payout: float = Field(ge=0, allow_inf_nan=False, description="US dollars")
    reason: str = Field(description="Two or three sentences")
    section: str = Field(description="The policy wording section relied on")


class Payment(BaseModel):
    """A payment on an approved claim."""

    amount: float = Field(gt=0, allow_inf_nan=False, description="US dollars")


class SignOff(BaseModel):
    """A handler's sign-off on a payout over the limit."""

    handler_id: str


class Step(BaseModel):
    """One thing the agent did on a claim."""

    text: str
    cost: float = Field(
        ge=0, allow_inf_nan=False, description="Model cost in US dollars"
    )


def now() -> str:
    """Return the current time in UTC as an ISO string."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def payout_limit(connection: sqlite3.Connection) -> float:
    """Return the largest payout that needs no handler's sign-off."""
    return setting(connection, "company")["payout_approval_limit"]


def cents(amount: float) -> int:
    """Return an amount in whole cents, so amounts compare exactly."""
    return round(amount * 100)


def refuse(reason: str) -> HTTPException:
    """Return the error for a request the rules don't allow."""
    return HTTPException(409, reason)


def set_status(connection: sqlite3.Connection, claim_id: str, status: str) -> None:
    """Set a claim's status."""
    connection.execute(
        "UPDATE claims SET status = ? WHERE claim_id = ?", (status, claim_id)
    )


def find_decision(connection: sqlite3.Connection, claim_id: str) -> sqlite3.Row:
    """Return a claim's decision, or refuse when there is none."""
    row = connection.execute(
        "SELECT * FROM decisions WHERE claim_id = ?", (claim_id,)
    ).fetchone()
    if row is None:
        raise refuse(f"{claim_id} has no decision")
    return row


def status_after(connection: sqlite3.Connection, decision: Decision) -> str:
    """Return the status a claim moves to once this decision is recorded."""
    if decision.decision != "approve":
        return "decided"
    if decision.payout > payout_limit(connection):
        return "awaiting_signoff"
    return "in_progress"


def record_decision(
    connection: sqlite3.Connection, claim_id: str, decision: Decision
) -> None:
    """Record the decision on a claim in progress."""
    if find_claim(connection, claim_id)["status"] != "in_progress":
        raise refuse(f"{claim_id} is not in progress")
    if connection.execute(
        "SELECT 1 FROM decisions WHERE claim_id = ?", (claim_id,)
    ).fetchone():
        raise refuse(f"{claim_id} already has a decision")
    if decision.decision != "approve" and decision.payout != 0:
        raise refuse("A decline or a referral pays nothing")
    if decision.decision == "approve" and cents(decision.payout) == 0:
        raise refuse("An approval pays something; decline or refer instead")
    connection.execute(
        "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, NULL)",
        (
            claim_id,
            decision.decision,
            decision.payout,
            decision.reason,
            decision.section,
        ),
    )
    set_status(connection, claim_id, status_after(connection, decision))


def check_payment(
    connection: sqlite3.Connection, claim_id: str, payment: Payment
) -> None:
    """Refuse a payment the rules don't allow."""
    decision = find_decision(connection, claim_id)
    if decision["decision"] != "approve":
        raise refuse(f"{claim_id} was not approved")
    if cents(payment.amount) != cents(decision["payout"]):
        raise refuse(f"The approved payout is {decision['payout']:.2f}")
    if decision["payout"] > payout_limit(connection) and not decision["signed_off_by"]:
        raise refuse("A payout over the limit needs a handler's sign-off")
    if connection.execute(
        "SELECT 1 FROM payments WHERE claim_id = ?", (claim_id,)
    ).fetchone():
        raise refuse(f"{claim_id} is already paid")


def pay_claim(connection: sqlite3.Connection, claim_id: str, payment: Payment) -> None:
    """Pay an approved claim its approved payout, once the rules allow it."""
    check_payment(connection, claim_id, payment)
    payout = find_decision(connection, claim_id)["payout"]
    connection.execute(
        "INSERT INTO payments VALUES (?, ?, ?)", (claim_id, payout, now())
    )
    set_status(connection, claim_id, "decided")


def sign_off(connection: sqlite3.Connection, claim_id: str, request: SignOff) -> None:
    """Record a handler's sign-off on a claim waiting for one."""
    if find_claim(connection, claim_id)["status"] != "awaiting_signoff":
        raise refuse(f"{claim_id} is not waiting for sign-off")
    if find_decision(connection, claim_id)["signed_off_by"]:
        raise refuse(f"{claim_id} is already signed off")
    handler = find(connection, "handlers", "handler_id", request.handler_id)
    if not handler["can_approve_over_limit"]:
        raise refuse(f"{handler['name']} can't sign off a payout over the limit")
    connection.execute(
        "UPDATE decisions SET signed_off_by = ? WHERE claim_id = ?",
        (request.handler_id, claim_id),
    )


def record_step(connection: sqlite3.Connection, claim_id: str, step: Step) -> None:
    """Add one line to a claim's steps."""
    find_claim(connection, claim_id)
    connection.execute(
        "INSERT INTO steps (claim_id, recorded_at, text, cost) VALUES (?, ?, ?, ?)",
        (claim_id, now(), step.text, step.cost),
    )
