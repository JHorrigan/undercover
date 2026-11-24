"""The SQLite database: where it lives, its tables and its connection."""

import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path

SCHEMA = """
CREATE TABLE claims (
    claim_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    record TEXT NOT NULL
);
CREATE TABLE policies (policy_id TEXT PRIMARY KEY, record TEXT NOT NULL);
CREATE TABLE customers (customer_id TEXT PRIMARY KEY, record TEXT NOT NULL);
CREATE TABLE plans (plan TEXT PRIMARY KEY, record TEXT NOT NULL);
CREATE TABLE handlers (handler_id TEXT PRIMARY KEY, record TEXT NOT NULL);
CREATE TABLE settings (name TEXT PRIMARY KEY, record TEXT NOT NULL);
CREATE TABLE decisions (
    claim_id TEXT PRIMARY KEY REFERENCES claims,
    decision TEXT NOT NULL,
    payout REAL NOT NULL,
    reason TEXT NOT NULL,
    section TEXT NOT NULL,
    signed_off_by TEXT REFERENCES handlers
);
CREATE TABLE payments (
    claim_id TEXT PRIMARY KEY REFERENCES claims,
    amount REAL NOT NULL,
    paid_at TEXT NOT NULL
);
CREATE TABLE steps (
    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id TEXT NOT NULL REFERENCES claims,
    recorded_at TEXT NOT NULL,
    text TEXT NOT NULL,
    cost REAL NOT NULL
);
"""


def database_path() -> Path:
    """Return the database file, from DATABASE_PATH or the local default."""
    return Path(os.getenv("DATABASE_PATH", "backend/undercover.db"))


def data_dir() -> Path:
    """Return the folder of business data, from DATA_DIR or the local default."""
    return Path(os.getenv("DATA_DIR", "data"))


def connect() -> sqlite3.Connection:
    """Open the database with rows readable by column name."""
    connection = sqlite3.connect(database_path(), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db() -> Iterator[sqlite3.Connection]:
    """Give a request its own connection, committed and closed afterwards."""
    connection = connect()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
