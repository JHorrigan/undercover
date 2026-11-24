"""The UnderCover backend."""

import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend import claims, decisions, instructions
from backend.db import get_db

app = FastAPI(title="UnderCover")
Db = Annotated[sqlite3.Connection, Depends(get_db)]


@app.exception_handler(RequestValidationError)
async def invalid_request(_: Request, error: RequestValidationError) -> JSONResponse:
    """Say what was wrong with a request without echoing its input back."""
    detail = [
        {key: problem[key] for key in ("loc", "msg", "type")}
        for problem in error.errors()
    ]
    return JSONResponse({"detail": detail}, status_code=422)


@app.get("/api/health", operation_id="health")
def health() -> dict[str, str]:
    """Check that the backend is running."""
    return {"status": "ok"}


@app.get("/api/claims", operation_id="list_claims")
def list_claims(db: Db) -> list[dict]:
    """List the claims queue, oldest first, with each claim's status."""
    return claims.list_claims(db)


@app.get("/api/handlers", operation_id="list_handlers")
def list_handlers(db: Db) -> list[dict]:
    """List the handlers and whether each can sign off a payout over the limit."""
    return claims.list_handlers(db)


@app.post("/api/queue/next", operation_id="take_next_claim")
def take_next_claim(db: Db) -> dict | None:
    """Move the oldest waiting claim to in progress and return it, or null."""
    return claims.take_next_claim(db)


@app.get("/api/claims/{claim_id}", operation_id="get_claim")
def get_claim(claim_id: str, db: Db) -> dict:
    """Get one claim in full, with its decision, payment and steps."""
    return claims.get_claim(db, claim_id)


@app.get("/api/claims/{claim_id}/evidence", operation_id="get_claim_evidence")
def get_claim_evidence(claim_id: str, db: Db) -> dict:
    """Get the claim as the agent reads it, with personal details withheld."""
    return claims.get_claim_evidence(db, claim_id)


@app.get("/api/claims/{claim_id}/policy", operation_id="get_policy")
def get_policy(claim_id: str, db: Db) -> dict:
    """Get the claim's policy, its plan's limits and the rules for add-ons."""
    return claims.get_policy(db, claim_id)


@app.get("/api/claims/{claim_id}/history", operation_id="get_claim_history")
def get_claim_history(claim_id: str, db: Db) -> list[dict]:
    """Get the customer's earlier claims, without their personal details."""
    return claims.get_claim_history(db, claim_id)


@app.get("/api/policy-wording", operation_id="get_policy_wording")
def get_policy_wording(db: Db) -> dict:
    """Get the policy wording in force and its version."""
    return claims.get_policy_wording(db)


@app.get("/api/instructions", operation_id="get_instructions")
def get_instructions() -> dict:
    """Get the agent's instructions."""
    return instructions.get_instructions()


@app.post("/api/claims/{claim_id}/decision", operation_id="record_decision")
def record_decision(claim_id: str, decision: decisions.Decision, db: Db) -> None:
    """Record the decision on a claim in progress."""
    decisions.record_decision(db, claim_id, decision)


@app.post("/api/claims/{claim_id}/payment", operation_id="pay_claim")
def pay_claim(claim_id: str, payment: decisions.Payment, db: Db) -> None:
    """Pay an approved claim the amount approved, once the rules allow it."""
    decisions.pay_claim(db, claim_id, payment)


@app.post("/api/claims/{claim_id}/sign-off", operation_id="sign_off")
def sign_off(claim_id: str, request: decisions.SignOff, db: Db) -> None:
    """Sign off a payout over the limit, as a handler allowed to."""
    decisions.sign_off(db, claim_id, request)


@app.post("/api/claims/{claim_id}/steps", operation_id="record_step")
def record_step(claim_id: str, step: decisions.Step, db: Db) -> None:
    """Add one line to the steps the agent has taken on a claim."""
    decisions.record_step(db, claim_id, step)
