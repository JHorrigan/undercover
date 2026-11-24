import json
from contextlib import closing

import pytest

from backend.db import connect

CLAIM = "CLM-1001"


def take(client):
    """Take claims from the queue until CLM-1001 is in progress."""
    while client.post("/api/queue/next").json()["claim_id"] != CLAIM:
        pass


def decide(client, decision, payout):
    return client.post(
        f"/api/claims/{CLAIM}/decision",
        json={
            "decision": decision,
            "payout": payout,
            "reason": "Covered by the wording.",
            "section": "3. Trip Delay",
        },
    )


def pay(client, amount):
    return client.post(f"/api/claims/{CLAIM}/payment", json={"amount": amount})


def sign_off(client, handler_id):
    return client.post(f"/api/claims/{CLAIM}/sign-off", json={"handler_id": handler_id})


def status(client):
    return client.get(f"/api/claims/{CLAIM}").json()["status"]


def test_take_next_claim_takes_the_oldest_waiting(client):
    queue = client.get("/api/claims").json()
    taken = client.post("/api/queue/next").json()
    assert taken["claim_id"] == queue[0]["claim_id"]
    assert taken["status"] == "in_progress"
    assert client.post("/api/queue/next").json()["claim_id"] == queue[1]["claim_id"]


def test_take_next_claim_returns_null_when_the_queue_is_empty(client):
    for _ in range(25):
        client.post("/api/queue/next")
    assert client.post("/api/queue/next").json() is None


def test_approve_and_pay_within_the_limit(client):
    take(client)
    assert decide(client, "approve", 420).status_code == 200
    assert status(client) == "in_progress"
    assert pay(client, 420).status_code == 200
    claim = client.get(f"/api/claims/{CLAIM}").json()
    assert claim["status"] == "decided"
    assert claim["payment"]["amount"] == 420
    assert claim["decision"]["decision"] == "approve"


@pytest.mark.parametrize("decision", ["decline", "refer"])
def test_decline_or_refer_is_decided_and_pays_nothing(client, decision):
    take(client)
    assert decide(client, decision, 0).status_code == 200
    assert status(client) == "decided"
    assert pay(client, 100).json()["detail"] == f"{CLAIM} was not approved"


def test_decline_with_a_payout_is_refused(client):
    take(client)
    response = decide(client, "decline", 50)
    assert response.status_code == 409
    assert response.json()["detail"] == "A decline or a referral pays nothing"


def test_deciding_a_claim_not_in_progress_is_refused(client):
    assert (
        decide(client, "approve", 420).json()["detail"] == f"{CLAIM} is not in progress"
    )


def test_paying_without_a_decision_is_refused(client):
    assert pay(client, 420).json()["detail"] == f"{CLAIM} has no decision"


def test_paying_the_wrong_amount_is_refused(client):
    take(client)
    decide(client, "approve", 420)
    assert pay(client, 500).json()["detail"] == "The approved payout is 420.00"


def test_paying_twice_is_refused(client):
    take(client)
    decide(client, "approve", 420)
    pay(client, 420)
    assert pay(client, 420).json()["detail"] == f"{CLAIM} is already paid"


def test_over_the_limit_waits_for_sign_off(client):
    take(client)
    decide(client, "approve", 1500)
    assert status(client) == "awaiting_signoff"
    response = pay(client, 1500)
    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "A payout over the limit needs a handler's sign-off"
    )
    assert sign_off(client, "HND-01").status_code == 200
    assert pay(client, 1500).status_code == 200
    claim = client.get(f"/api/claims/{CLAIM}").json()
    assert claim["status"] == "decided"
    assert claim["decision"]["signed_off_by"] == "HND-01"
    assert claim["decision"]["signed_off_by_name"] == "Dana Whitfield"


def test_a_handler_without_the_right_cannot_sign_off(client):
    with closing(connect()) as connection:
        handler = {
            "handler_id": "HND-09",
            "name": "Sam Trainee",
            "can_approve_over_limit": False,
        }
        connection.execute(
            "INSERT INTO handlers VALUES (?, ?)", ("HND-09", json.dumps(handler))
        )
        connection.commit()
    take(client)
    decide(client, "approve", 1500)
    response = sign_off(client, "HND-09")
    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Sam Trainee can't sign off a payout over the limit"
    )


def test_sign_off_needs_a_claim_waiting_for_it(client):
    take(client)
    decide(client, "approve", 420)
    assert (
        sign_off(client, "HND-01").json()["detail"]
        == f"{CLAIM} is not waiting for sign-off"
    )


def test_record_step(client):
    client.post(
        f"/api/claims/{CLAIM}/steps", json={"text": "Read the policy", "cost": 0}
    )
    steps = client.get(f"/api/claims/{CLAIM}").json()["steps"]
    assert [(step["text"], step["cost"]) for step in steps] == [("Read the policy", 0)]


def test_policy_comes_with_its_plan(client):
    policy = client.get(f"/api/claims/{CLAIM}/policy").json()
    assert policy["policy"]["policy_id"] == "POL-2001"
    assert policy["plan"]["plan"] == "premium"
    assert "add_ons" in policy["plan_rules"]


def test_history_has_no_personal_details(client):
    history = client.get(f"/api/claims/{CLAIM}/history").json()
    assert history[0]["claim_id"] == "CLM-0412"
    text = json.dumps(history)
    for detail in ["1988-03-14", "Wayne Street", "maya.patel@example.com", "555 0143"]:
        assert detail not in text


def test_policy_wording_and_instructions(client):
    wording = client.get("/api/policy-wording").json()
    assert wording["version"] == "2026.1"
    assert "## 10. How we work out your payment" in wording["text"]
    assert (
        client.get("/api/instructions")
        .json()["text"]
        .startswith("# The UnderCover Agent")
    )


def test_every_operation_is_named_documented_and_has_no_optional_inputs(client):
    schema = client.get("/openapi.json").json()
    for path, operations in schema["paths"].items():
        for operation in operations.values():
            assert operation["operationId"], path
            assert operation["description"].count("\n") == 0, path
            assert all(
                parameter["required"] for parameter in operation.get("parameters", [])
            )
            body = (
                operation.get("requestBody", {})
                .get("content", {})
                .get("application/json")
            )
            if body:
                name = body["schema"]["$ref"].split("/")[-1]
                model = schema["components"]["schemas"][name]
                assert set(model["required"]) == set(model["properties"]), name


def test_a_payment_rounded_down_to_the_limit_still_waits_for_sign_off(client):
    take(client)
    decide(client, "approve", 1000.004)
    assert status(client) == "awaiting_signoff"
    assert pay(client, 1000).status_code == 409


def test_the_approved_payout_is_what_is_paid(client):
    take(client)
    decide(client, "approve", 420)
    assert pay(client, 420.001).status_code == 200
    assert client.get(f"/api/claims/{CLAIM}").json()["payment"]["amount"] == 420


def test_a_second_decision_is_refused(client):
    take(client)
    decide(client, "approve", 420)
    response = decide(client, "decline", 0)
    assert response.status_code == 409
    assert response.json()["detail"] == f"{CLAIM} already has a decision"


def test_an_approval_of_nothing_is_refused(client):
    take(client)
    response = decide(client, "approve", 0)
    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "An approval pays something; decline or refer instead"
    )


@pytest.mark.parametrize("amount", ["NaN", "Infinity"])
def test_impossible_amounts_are_rejected(client, amount):
    take(client)
    headers = {"content-type": "application/json"}
    url = f"/api/claims/{CLAIM}"
    decision = (
        f'{{"decision": "approve", "payout": {amount}, '
        '"reason": "Covered.", "section": "3. Trip Delay"}'
    )
    response = client.post(f"{url}/decision", content=decision, headers=headers)
    assert response.status_code == 422
    decide(client, "approve", 420)
    payment = f'{{"amount": {amount}}}'
    response = client.post(f"{url}/payment", content=payment, headers=headers)
    assert response.status_code == 422


def test_a_second_sign_off_is_refused(client):
    take(client)
    decide(client, "approve", 1500)
    sign_off(client, "HND-01")
    response = sign_off(client, "HND-02")
    assert response.status_code == 409
    assert response.json()["detail"] == f"{CLAIM} is already signed off"
