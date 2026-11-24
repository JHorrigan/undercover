"""The agent's instructions, kept with the backend so a change is reviewed like code."""

from pathlib import Path

INSTRUCTIONS = Path(__file__).parent / "instructions.md"


def get_instructions() -> dict:
    """Return the agent's instructions."""
    return {"text": INSTRUCTIONS.read_text(encoding="utf-8")}
