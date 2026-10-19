"""The policy wording and the claims manual, served one numbered section at a time."""

import re
import sqlite3
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from backend import store
from backend.db import Db

router = APIRouter(prefix="/api/documents")
Document = Literal["policy_wording", "claims_manual"]

HEADING = re.compile(r"^## (\d+)\. (.+)$", re.MULTILINE)


def sections(markdown: str) -> dict[str, tuple[str, str]]:
    """Split Markdown at its numbered headings into {number: (title, text)}."""
    matches = list(HEADING.finditer(markdown))
    ends = [m.start() for m in matches[1:]] + [len(markdown)]
    return {
        m[1]: (m[2], markdown[m.start() : end].strip())
        for m, end in zip(matches, ends, strict=True)
    }


def document_sections(
    db: sqlite3.Connection, document: str
) -> dict[str, tuple[str, str]]:
    """Return the sections of one seeded document."""
    return sections(store.record(db, "document", document))


@router.get("", operation_id="list_documents")
def list_documents(db: Db) -> dict[str, list[dict[str, str]]]:
    """List the sections of the policy wording and the claims manual."""
    return {
        document: [
            {"section": number, "title": title}
            for number, (title, _) in document_sections(db, document).items()
        ]
        for document in ("policy_wording", "claims_manual")
    }


@router.get(
    "/{document}/sections/{section}",
    operation_id="read_section",
    response_class=PlainTextResponse,
)
def read_section(document: Document, section: str, db: Db) -> str:
    """Read one numbered section of the policy wording or the claims manual."""
    found = document_sections(db, document).get(section)
    if found is None:
        raise HTTPException(404, "Section not found")
    return found[1]
