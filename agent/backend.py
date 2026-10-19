"""The agents' one way to reach the UnderCover backend's API."""

import os
from typing import Any

import httpx

DEFAULT_API = "http://127.0.0.1:8000"


def client() -> httpx.Client:
    """Return a client for the backend at UNDERCOVER_API."""
    return httpx.Client(base_url=os.getenv("UNDERCOVER_API", DEFAULT_API), timeout=30)


def request(
    method: str, path: str, body: dict[str, Any] | None = None
) -> httpx.Response:
    """Send one request to the backend."""
    with client() as http:
        return http.request(method, path, json=body)


def text(method: str, path: str, body: dict[str, Any] | None = None) -> str:
    """Call the backend for a tool: the response, or the error for the model to read."""
    response = request(method, path, body)
    if response.is_success:
        return response.text
    return f"Error {response.status_code}: {response.text}"


def data(method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    """Call the backend for the harness: the JSON response, raising on an error."""
    return request(method, path, body).raise_for_status().json()
