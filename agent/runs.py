"""The agent runner's calls to the backend for runs."""

from typing import Any

from agent import tools


def create_run(cap: int) -> str:
    """Create a run capped at a number of claims and return its id."""
    with tools.backend() as client:
        response = client.post("/api/runs", json={"cap": cap}).raise_for_status()
        return response.json()["run_id"]


def finish_run(run_id: str, summary: str) -> str:
    """Finish a run with a summary; returns the backend's refusal if it has one."""
    return tools.call("POST", f"/api/runs/{run_id}/finish", {"summary": summary})


def get_claim(claim_id: str) -> dict[str, Any]:
    """Return a claim with its status and outcome."""
    with tools.backend() as client:
        return client.get(f"/api/claims/{claim_id}").raise_for_status().json()
