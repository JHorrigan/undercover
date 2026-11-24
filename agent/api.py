"""The agent's one way to reach the backend's API."""

import os
from typing import Any

import httpx


def backend() -> httpx.Client:
    """Return a client for the UnderCover backend, at BACKEND_URL or the default."""
    return httpx.Client(
        base_url=os.getenv("BACKEND_URL", "http://127.0.0.1:8000"), timeout=30
    )


def fetch(path: str) -> Any:
    """Read one resource from the backend."""
    with backend() as client:
        response = client.get(path)
    response.raise_for_status()
    return response.json()


def post(path: str, body: dict | None) -> httpx.Response:
    """Send a request to the backend and return its response."""
    with backend() as client:
        return client.post(path, json=body)


def send(path: str, body: dict) -> str:
    """Send a request the rules may refuse, and say what happened."""
    response = post(path, body)
    if response.status_code == httpx.codes.CONFLICT:
        return f"Refused: {response.json()['detail']}"
    response.raise_for_status()
    return "Done."


def record_step(claim_id: str, text: str, cost: float) -> None:
    """Add a line to the claim's steps, for the dashboard."""
    post(
        f"/api/claims/{claim_id}/steps", {"text": text, "cost": cost}
    ).raise_for_status()


def take_next_claim() -> dict | None:
    """Take the oldest waiting claim from the queue, or None when it is empty."""
    response = post("/api/queue/next", None)
    response.raise_for_status()
    return response.json()
