"""Starting the UnderCover Agent on a claim from the dashboard."""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from agent import claim as agent
from backend import run_store, store
from backend.db import get_db

router = APIRouter(prefix="/api")
Db = Annotated[sqlite3.Connection, Depends(get_db)]


@router.post("/claims/{claim_id}/run", operation_id="run_agent")
def run_agent(claim_id: str, tasks: BackgroundTasks, db: Db) -> dict[str, str]:
    """Start the UnderCover Agent on a waiting claim, in the background."""
    claim = store.claim_detail(db, claim_id)
    if claim is None:
        raise HTTPException(404, "Claim not found")
    if claim["status"] != "waiting":
        raise HTTPException(409, "Only a waiting claim can be run")
    if run_store.running(db):
        raise HTTPException(409, "A run is already going")
    tasks.add_task(agent.run_one, claim_id)
    return {"status": "started"}
