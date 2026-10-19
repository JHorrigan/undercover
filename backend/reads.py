"""Read operations: the queue, the records and the instructions."""

import sqlite3
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from backend import store
from backend.db import get_db

INSTRUCTIONS = Path(__file__).parent / "instructions"

router = APIRouter(prefix="/api")
Db = Annotated[sqlite3.Connection, Depends(get_db)]


def found(value: Any, what: str) -> Any:
    """Return the value, or raise 404 if it is missing."""
    if value is None:
        raise HTTPException(404, f"{what} not found")
    return value


@router.get("/claims", operation_id="list_claims")
def list_claims(db: Db) -> list[dict[str, Any]]:
    """List every claim in the queue with its status."""
    return store.claim_summaries(db)


@router.get("/claims/{claim_id}", operation_id="get_claim")
def get_claim(claim_id: str, db: Db) -> dict[str, Any]:
    """Get one claim in full, with its status and outcome."""
    return found(store.claim_detail(db, claim_id), "Claim")


@router.get("/policies/{policy_id}", operation_id="get_policy")
def get_policy(policy_id: str, db: Db) -> dict[str, Any]:
    """Get one policy: plan, add-ons, trip and travelers."""
    return found(store.record(db, "policy", policy_id), "Policy")


@router.get("/customers/{customer_id}", operation_id="get_customer")
def get_customer(customer_id: str, db: Db) -> dict[str, Any]:
    """Get one customer with their claim history."""
    return found(store.record(db, "customer", customer_id), "Customer")


@router.get("/plans", operation_id="list_plans")
def list_plans(db: Db) -> dict[str, Any]:
    """List the plans with their limits, deductibles and add-ons."""
    return store.record(db, "plans", "all")


@router.get("/handlers", operation_id="list_handlers")
def list_handlers(db: Db) -> list[dict[str, Any]]:
    """List the claims handlers."""
    return store.records(db, "handler")


@router.get(
    "/instructions/{agent}",
    operation_id="get_instructions",
    response_class=PlainTextResponse,
)
def get_instructions(agent: Literal["claim"]) -> str:
    """Get the instructions for one of the UnderCover agents, as Markdown."""
    return (INSTRUCTIONS / f"{agent}.md").read_text(encoding="utf-8")
