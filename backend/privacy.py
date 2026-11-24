"""Withholding a customer's personal details from what the agent reads."""

from datetime import date
from typing import Any

WITHHELD = "[withheld]"


def personal_details(customer: dict) -> list[str]:
    """Return the customer's date of birth, in the ways it is written, and contacts."""
    born = date.fromisoformat(customer["date_of_birth"])
    return [
        customer["date_of_birth"],
        f"{born:%B} {born.day}, {born.year}",
        f"{born.day} {born:%B} {born.year}",
        f"{born.month:02}/{born.day:02}/{born.year}",
        customer["address"]["street"],
        customer["email"],
        customer["phone"],
    ]


def withhold(value: Any, details: list[str]) -> Any:
    """Replace each personal detail wherever it appears in a record."""
    if isinstance(value, str):
        for detail in details:
            value = value.replace(detail, WITHHELD)
        return value
    if isinstance(value, list):
        return [withhold(item, details) for item in value]
    if isinstance(value, dict):
        return {key: withhold(item, details) for key, item in value.items()}
    return value
