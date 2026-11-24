"""Build a fresh database from UnderCover's records in data/."""

import json
import sqlite3
from typing import Any

from backend.db import SCHEMA, connect, data_dir, database_path


def read(name: str) -> Any:
    """Read one JSON file from the data folder."""
    return json.loads((data_dir() / name).read_text(encoding="utf-8"))


def add_claims(connection: sqlite3.Connection, claims: list[dict]) -> None:
    """Add claims to the queue, each one waiting."""
    connection.executemany(
        "INSERT INTO claims VALUES (?, 'waiting', ?)",
        [(claim["claim_id"], json.dumps(without_status(claim))) for claim in claims],
    )


def without_status(claim: dict) -> dict:
    """Drop the source system's status, since the queue keeps its own."""
    return {key: value for key, value in claim.items() if key != "status"}


def add_records(
    connection: sqlite3.Connection, table: str, key: str, records: list[dict]
) -> None:
    """Add records keyed by one of their fields."""
    connection.executemany(
        f"INSERT INTO {table} VALUES (?, ?)",  # noqa: S608 - table names are fixed in this module
        [(record[key], json.dumps(record)) for record in records],
    )


def seed(claims: list[dict]) -> None:
    """Replace the database with the records in data/ and the given claims."""
    database_path().unlink(missing_ok=True)
    connection = connect()
    connection.executescript(SCHEMA)
    plans = read("plans.json")
    add_records(connection, "policies", "policy_id", read("policies.json"))
    add_records(connection, "customers", "customer_id", read("customers.json"))
    add_records(connection, "handlers", "handler_id", read("handlers.json"))
    add_records(connection, "plans", "plan", plans.pop("plans"))
    connection.executemany(
        "INSERT INTO settings VALUES (?, ?)",
        [
            ("company", json.dumps(read("company.json"))),
            ("plan_rules", json.dumps(plans)),
        ],
    )
    add_claims(connection, claims)
    connection.commit()
    connection.close()


if __name__ == "__main__":
    seed(read("claims.json"))
    print(f"Seeded {database_path()}")
