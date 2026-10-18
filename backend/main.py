"""The UnderCover backend."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend import reads
from backend.db import connect, create_schema
from backend.seed import seed


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create and seed the database on startup."""
    conn = connect()
    create_schema(conn)
    seed(conn)
    conn.close()
    yield


app = FastAPI(title="UnderCover", lifespan=lifespan)
app.include_router(reads.router)


@app.get("/api/health", operation_id="health")
def health() -> dict[str, str]:
    """Check that the backend is running."""
    return {"status": "ok"}
