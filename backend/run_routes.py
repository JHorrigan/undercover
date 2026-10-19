"""Runs: starting the agents, a run's to-do list, and finishing it."""

import sqlite3
from typing import Any, Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from agent import harness
from backend import run_store, store
from backend.db import Db
from backend.reads import found

router = APIRouter(prefix="/api")


class NewRun(BaseModel):
    """A run capped at a number of claims."""

    cap: int = Field(ge=1)


class Todo(BaseModel):
    """One item on a run's to-do list."""

    text: str = Field(min_length=1)
    status: Literal["to_do", "in_progress", "done", "for_handler"]


class Todos(BaseModel):
    """A run's whole to-do list."""

    todos: list[Todo]


class Finish(BaseModel):
    """The summary that ends a run."""

    summary: str = Field(min_length=1)


def open_run_or_error(db: sqlite3.Connection, run_id: str) -> dict[str, Any]:
    """Return a run that is still going, or raise 404 or 409."""
    run = run_store.run_row(db, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    if run["finished_at"]:
        raise HTTPException(409, "This run has finished")
    return run


@router.post("/runs", operation_id="create_run")
def create_run(new_run: NewRun, db: Db) -> dict[str, str]:
    """Create a run capped at a number of claims; only one runs at a time."""
    if run_store.running(db):
        raise HTTPException(409, "A run is already going")
    run_id = run_store.create_run(db, new_run.cap)
    db.commit()
    return {"run_id": run_id}


@router.get("/runs/latest", operation_id="get_latest_run")
def get_latest_run(db: Db) -> dict[str, Any] | None:
    """Get the latest run with its to-do list and summary, or null."""
    return run_store.latest_run(db)


@router.get("/runs/{run_id}", operation_id="get_run")
def get_run(run_id: str, db: Db) -> dict[str, Any]:
    """Get one run with its to-do list and summary."""
    return found(run_store.run(db, run_id), "Run")


@router.put("/runs/{run_id}/todos", operation_id="update_todos")
def update_todos(run_id: str, todos: Todos, db: Db) -> dict[str, str]:
    """Replace a run's to-do list."""
    open_run_or_error(db, run_id)
    run_store.replace_todos(db, run_id, [t.model_dump() for t in todos.todos])
    db.commit()
    return {"status": "ok"}


@router.post("/runs/{run_id}/finish", operation_id="finish_run")
def finish_run(run_id: str, finish: Finish, db: Db) -> dict[str, str]:
    """Finish a run with a summary, unless a waiting claim is within its cap."""
    run = open_run_or_error(db, run_id)
    if missed := run_store.missed_claims(db, run):
        raise HTTPException(409, f"Waiting claims within the cap: {', '.join(missed)}")
    run_store.finish(db, run_id, finish.summary)
    db.commit()
    return {"status": "finished"}


@router.post("/runs/{run_id}/stop", operation_id="stop_run")
def stop_run(run_id: str, finish: Finish, db: Db) -> dict[str, str]:
    """Close a run that could not finish, with the reason it stopped."""
    open_run_or_error(db, run_id)
    run_store.finish(db, run_id, finish.summary)
    db.commit()
    return {"status": "stopped"}


@router.post("/runs/start", operation_id="start_run")
def start_run(new_run: NewRun, tasks: BackgroundTasks, db: Db) -> dict[str, str]:
    """Start the queue agent on the waiting claims up to a cap, in the background."""
    if run_store.running(db):
        raise HTTPException(409, "A run is already going")
    tasks.add_task(harness.run_queue, new_run.cap)
    return {"status": "started"}


@router.post("/claims/{claim_id}/run", operation_id="run_agent")
def run_agent(claim_id: str, tasks: BackgroundTasks, db: Db) -> dict[str, str]:
    """Start the UnderCover Agent on one waiting claim, in the background."""
    if found(store.claim_detail(db, claim_id), "Claim")["status"] != "waiting":
        raise HTTPException(409, "Only a waiting claim can be run")
    if run_store.running(db):
        raise HTTPException(409, "A run is already going")
    tasks.add_task(harness.run_one, claim_id)
    return {"status": "started"}
