"""Fixtures shared by the backend and agent tests."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.seed import read, seed


@pytest.fixture
def seeded(tmp_path, monkeypatch):
    """Point the backend at a fresh temporary database, seeded from data/."""
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    seed(read("claims.json"))


@pytest.fixture
def client(seeded):
    """Return a test client for the backend on the seeded database."""
    return TestClient(app)
