"""Write operations: starting, deciding, paying and signing off claims."""

import sqlite3
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend import run_store, store
from backend.db import Db
from backend.run_routes import open_run_or_error

router = APIRouter(prefix="/api/claims/{claim_id}")


class Decision(BaseModel):
    """The agent's decision on a claim."""

    decision: Literal["approve", "decline", "refer"]
    payout: float = Field(ge=0)
    reason: str = Field(min_length=1)
    policy_section: str = Field(min_length=1)


class Payment(BaseModel):
    """A payment of the approved payout."""

    amount: float = Field(gt=0)


class SignOff(BaseModel):
    """A handler's sign-off on a payout over the limit."""

    handler_id: str


class Start(BaseModel):
    """The run that starts a claim."""

    run_id: str


class Failure(BaseModel):
    """What went wrong on a claim before its decision."""

    error: str = Field(min_length=1)


class Step(BaseModel):
    """One step the agent took on a claim."""

    kind: str
    text: str


def claim_or_404(db: sqlite3.Connection, claim_id: str) -> dict[str, Any]:
    """Return the claim with its outcome, or raise 404."""
    claim = store.claim_detail(db, claim_id)
    if claim is None:
        raise HTTPException(404, "Claim not found")
    return claim


def record_payment(db: sqlite3.Connection, claim_id: str, amount: float) -> None:
    """Store a payment."""
    db.execute(
        "INSERT INTO payments (claim_id, amount, paid_at) VALUES (?, ?, ?)",
        (claim_id, amount, store.now()),
    )


@router.post("/start", operation_id="start_claim")
def start_claim(claim_id: str, start: Start, db: Db) -> dict[str, Any]:
    """Mark a waiting claim as in progress for a run, within the run's cap."""
    if claim_or_404(db, claim_id)["status"] != "waiting":
        raise HTTPException(409, "Only a waiting claim can be started")
    run = open_run_or_error(db, start.run_id)
    taken = run_store.claims_taken(db, start.run_id)
    if claim_id not in taken and len(taken) >= run["cap"]:
        raise HTTPException(409, f"This run has used its cap of {run['cap']} claims")
    run_store.take_claim(db, start.run_id, claim_id)
    store.set_status(db, claim_id, "in_progress")
    db.commit()
    return claim_or_404(db, claim_id)


@router.post("/fail", operation_id="fail_claim")
def fail_claim(claim_id: str, failure: Failure, db: Db) -> dict[str, Any]:
    """Requeue a claim that failed before its decision, or leave it for a handler."""
    claim_or_404(db, claim_id)
    run_store.fail_claim(db, claim_id, failure.error)
    db.commit()
    return claim_or_404(db, claim_id)


@router.post("/decision", operation_id="record_decision")
def record_decision(claim_id: str, decision: Decision, db: Db) -> dict[str, Any]:
    """Record the decision on a claim: approve with a payout, decline or refer."""
    if claim_or_404(db, claim_id)["decision"]:
        raise HTTPException(409, "This claim already has a decision")
    if decision.decision != "approve" and decision.payout:
        raise HTTPException(422, "Only an approved claim has a payout")
    db.execute(
        "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?)",
        (claim_id, *decision.model_dump().values(), store.now()),
    )
    over_limit = (
        decision.decision == "approve" and decision.payout > store.payout_limit(db)
    )
    store.set_status(db, claim_id, "awaiting_signoff" if over_limit else "decided")
    db.commit()
    return claim_or_404(db, claim_id)


@router.post("/payment", operation_id="pay_claim")
def pay_claim(claim_id: str, payment: Payment, db: Db) -> dict[str, Any]:
    """Pay an approved claim; over the limit it needs a handler's sign-off first."""
    claim = claim_or_404(db, claim_id)
    decision = claim["decision"]
    if not decision or decision["decision"] != "approve":
        raise HTTPException(409, "Only an approved claim can be paid")
    if claim["payment"]:
        raise HTTPException(409, "This claim has already been paid")
    if payment.amount != decision["payout"]:
        raise HTTPException(422, f"The approved payout is {decision['payout']:.2f}")
    if payment.amount > store.payout_limit(db) and not claim["sign_off"]:
        raise HTTPException(
            403, "Payment blocked: a payout over the limit needs a handler's sign-off"
        )
    record_payment(db, claim_id, payment.amount)
    db.commit()
    return claim_or_404(db, claim_id)


@router.post("/sign-off", operation_id="sign_off_claim")
def sign_off_claim(claim_id: str, sign_off: SignOff, db: Db) -> dict[str, Any]:
    """Sign off a payout over the limit, which releases the payment."""
    claim = claim_or_404(db, claim_id)
    if claim["status"] != "awaiting_signoff":
        raise HTTPException(409, "This claim is not waiting for sign-off")
    handler = store.record(db, "handler", sign_off.handler_id)
    if not handler or not handler["can_approve_over_limit"]:
        raise HTTPException(403, "This handler cannot sign off payouts over the limit")
    db.execute(
        "INSERT INTO sign_offs VALUES (?, ?, ?)",
        (claim_id, sign_off.handler_id, store.now()),
    )
    record_payment(db, claim_id, claim["decision"]["payout"])
    store.set_status(db, claim_id, "decided")
    db.commit()
    return claim_or_404(db, claim_id)


@router.get("/steps", operation_id="list_steps")
def list_steps(claim_id: str, db: Db) -> list[dict[str, Any]]:
    """List the steps the agent has taken on a claim, oldest first."""
    claim_or_404(db, claim_id)
    rows = db.execute(
        "SELECT id, at, kind, text FROM steps WHERE claim_id = ? ORDER BY id",
        (claim_id,),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/steps", operation_id="add_step")
def add_step(claim_id: str, step: Step, db: Db) -> dict[str, str]:
    """Add a step the agent has taken on a claim."""
    claim_or_404(db, claim_id)
    store.insert_step(db, claim_id, step.kind, step.text)
    db.commit()
    return {"status": "ok"}
