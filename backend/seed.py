"""Seed the database from UnderCover's records in data/.

Only the files listed here are read. data/evals/ and data/security/ are never opened.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any

DATA = Path(__file__).parent.parent / "data"

KEYED_FILES = {
    "claim": ("claims.json", "claim_id"),
    "policy": ("policies.json", "policy_id"),
    "customer": ("customers.json", "customer_id"),
    "handler": ("handlers.json", "handler_id"),
}
DOCUMENTS = ("policy_wording", "claims_manual")


def read_json(name: str) -> Any:
    """Read one JSON file from data/."""
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def insert(conn: sqlite3.Connection, kind: str, id_: str, body: object) -> None:
    """Store one record as JSON."""
    conn.execute(
        "INSERT INTO records (kind, id, body) VALUES (?, ?, ?)",
        (kind, id_, json.dumps(body)),
    )


def seed(conn: sqlite3.Connection) -> None:
    """Load the records into an empty database; do nothing if already seeded."""
    if conn.execute("SELECT 1 FROM records LIMIT 1").fetchone():
        return
    for kind, (name, key) in KEYED_FILES.items():
        for row in read_json(name):
            insert(conn, kind, row[key], row)
    plans = read_json("plans.json")
    insert(conn, "plans", "all", plans)
    insert(conn, "company", "settings", read_json("company.json"))
    for name in DOCUMENTS:
        insert(
            conn, "document", name, (DATA / f"{name}.md").read_text(encoding="utf-8")
        )
    conn.executemany(
        "INSERT INTO claims (claim_id, status) VALUES (?, 'waiting')",
        [
            (row[0],)
            for row in conn.execute("SELECT id FROM records WHERE kind = 'claim'")
        ],
    )
    conn.commit()
