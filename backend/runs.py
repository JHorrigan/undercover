"""Starting the UnderCover Agent on a claim from the dashboard."""

import sqlite3
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from agent import main as agent
from backend import store
from backend.db import get_db

router = APIRouter(prefix="/api")
Db = Annotated[sqlite3.Connection, Depends(get_db)]


def run_in_background(claim_id: str) -> None:
    """Run the agent on one claim with a new thread."""
    agent.run(claim_id, f"{claim_id}-{uuid4().hex[:8]}")


@router.post("/claims/{claim_id}/run", operation_id="run_agent")
def run_agent(claim_id: str, tasks: BackgroundTasks, db: Db) -> dict[str, str]:
    """Start the UnderCover Agent on a waiting claim, in the background."""
    claim = store.claim_detail(db, claim_id)
    if claim is None:
        raise HTTPException(404, "Claim not found")
    if claim["status"] != "waiting":
        raise HTTPException(409, "Only a waiting claim can be run")
    tasks.add_task(run_in_background, claim_id)
    return {"status": "started"}
