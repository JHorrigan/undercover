"""The UnderCover backend."""

import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI

from backend import claims
from backend.db import get_db

app = FastAPI(title="UnderCover")
Db = Annotated[sqlite3.Connection, Depends(get_db)]


@app.get("/api/health", operation_id="health")
def health() -> dict[str, str]:
    """Check that the backend is running."""
    return {"status": "ok"}


@app.get("/api/claims", operation_id="list_claims")
def list_claims(db: Db) -> list[dict]:
    """List the claims queue, oldest first, with each claim's status."""
    return claims.list_claims(db)


@app.get("/api/claims/{claim_id}", operation_id="get_claim")
def get_claim(claim_id: str, db: Db) -> dict:
    """Get one claim in full, with its decision, payment and steps."""
    return claims.get_claim(db, claim_id)
