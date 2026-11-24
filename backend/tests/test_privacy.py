import json

import pytest

from backend.privacy import WITHHELD, personal_details, withhold
from backend.seed import read


@pytest.mark.parametrize(
    ("claim_id", "detail"),
    [("CLM-1016", "February 3, 1965"), ("CLM-1008", "Rural Route 2, Box 39")],
)
def test_the_agent_never_reads_a_customers_personal_details(client, claim_id, detail):
    evidence = json.dumps(client.get(f"/api/claims/{claim_id}/evidence").json())
    assert detail not in evidence
    assert WITHHELD in evidence
    assert detail in json.dumps(client.get(f"/api/claims/{claim_id}").json())


def test_no_claim_shows_the_agent_its_customers_details(client):
    customers = {
        customer["customer_id"]: customer for customer in read("customers.json")
    }
    for claim in client.get("/api/claims").json():
        evidence = client.get(f"/api/claims/{claim['claim_id']}/evidence").json()
        text = json.dumps(evidence)
        for detail in personal_details(customers[evidence["customer_id"]]):
            assert detail not in text, claim["claim_id"]


def test_withhold_reaches_every_string():
    record = {
        "story": "Born 1965-02-03.",
        "items": [{"note": "1965-02-03"}],
        "amount": 5,
    }
    assert withhold(record, ["1965-02-03"]) == {
        "story": f"Born {WITHHELD}.",
        "items": [{"note": WITHHELD}],
        "amount": 5,
    }
