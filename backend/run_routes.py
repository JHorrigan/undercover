"""Run operations: creating a run, its to-do list and finishing it."""

import sqlite3
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend import run_store
from backend.db import get_db

router = APIRouter(prefix="/api/runs")
Db = Annotated[sqlite3.Connection, Depends(get_db)]


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


@router.post("", operation_id="create_run")
def create_run(new_run: NewRun, db: Db) -> dict[str, str]:
    """Create a run capped at a number of claims; only one runs at a time."""
    if run_store.running(db):
        raise HTTPException(409, "A run is already going")
    run_id = run_store.create_run(db, new_run.cap)
    db.commit()
    return {"run_id": run_id}


@router.get("/latest", operation_id="get_latest_run")
def get_latest_run(db: Db) -> dict[str, Any] | None:
    """Get the latest run with its to-do list and summary, or null."""
    return run_store.latest_run(db)


@router.put("/{run_id}/todos", operation_id="update_todos")
def update_todos(run_id: str, todos: Todos, db: Db) -> dict[str, str]:
    """Replace a run's to-do list."""
    open_run_or_error(db, run_id)
    run_store.replace_todos(db, run_id, [t.model_dump() for t in todos.todos])
    db.commit()
    return {"status": "ok"}


@router.post("/{run_id}/finish", operation_id="finish_run")
def finish_run(run_id: str, finish: Finish, db: Db) -> dict[str, str]:
    """Finish a run with a summary, unless a waiting claim is within its cap."""
    run = open_run_or_error(db, run_id)
    if missed := run_store.missed_claims(db, run):
        raise HTTPException(409, f"Waiting claims within the cap: {', '.join(missed)}")
    run_store.finish(db, run_id, finish.summary)
    db.commit()
    return {"status": "finished"}
