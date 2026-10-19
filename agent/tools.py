"""The UnderCover Agent's tools. Each one is a call to the backend's API."""

from typing import Any, Literal

import httpx
from langchain_core.tools import tool

BACKEND_URL = "http://localhost:8000"


def backend() -> httpx.Client:
    """Return a client for the UnderCover backend."""
    return httpx.Client(base_url=BACKEND_URL, timeout=30)


def call(method: str, path: str, body: dict[str, Any] | None = None) -> str:
    """Call the backend and return the response text, with the status on an error."""
    with backend() as client:
        response = client.request(method, path, json=body)
    if response.is_success:
        return response.text
    return f"Error {response.status_code}: {response.text}"


@tool
def get_claim(claim_id: str) -> str:
    """Get a claim: the story, the items claimed, the documents and its status."""
    return call("GET", f"/api/claims/{claim_id}")


@tool
def get_policy(policy_id: str) -> str:
    """Get a policy: the plan, add-ons, purchase date, trip and travelers."""
    return call("GET", f"/api/policies/{policy_id}")


@tool
def get_customer(customer_id: str) -> str:
    """Get a customer with their earlier claims."""
    return call("GET", f"/api/customers/{customer_id}")


@tool
def list_plans() -> str:
    """List the plans with their limits, waiting periods, deductibles and add-ons."""
    return call("GET", "/api/plans")


DOCUMENT_NAMES = {"policy_wording": "Policy wording", "claims_manual": "Claims manual"}


@tool
def list_documents() -> str:
    """List the numbered sections of the policy wording and the claims manual."""
    return call("GET", "/api/documents")


@tool
def read_section(
    document: Literal["policy_wording", "claims_manual"], section: str
) -> str:
    """Read one numbered section of the policy wording or the claims manual."""
    text = call("GET", f"/api/documents/{document}/sections/{section}")
    return f"{DOCUMENT_NAMES[document]}\n{text}"


@tool
def record_decision(
    claim_id: str,
    decision: Literal["approve", "decline", "refer"],
    payout: float,
    reason: str,
    policy_section: str,
) -> str:
    """Record the decision on a claim, with the payout, the reason and the section."""
    body = {
        "decision": decision,
        "payout": payout,
        "reason": reason,
        "policy_section": policy_section,
    }
    return call("POST", f"/api/claims/{claim_id}/decision", body)


@tool
def pay_claim(claim_id: str, amount: float) -> str:
    """Pay an approved claim its payout in US dollars."""
    return call("POST", f"/api/claims/{claim_id}/payment", {"amount": amount})


TOOLS = [
    get_claim,
    get_policy,
    get_customer,
    list_plans,
    list_documents,
    read_section,
    record_decision,
    pay_claim,
]
