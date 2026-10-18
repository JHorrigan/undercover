import pytest

CLAIM = "/api/claims/CLM-1001"


def decide(client, decision="approve", payout=420.0):
    return client.post(
        f"{CLAIM}/decision",
        json={
            "decision": decision,
            "payout": payout,
            "reason": "Covered delay with receipts.",
            "policy_section": "3. Trip Delay",
        },
    )


def pay(client, amount):
    return client.post(f"{CLAIM}/payment", json={"amount": amount})


def test_start_claim(client):
    assert client.post(f"{CLAIM}/start").json()["status"] == "in_progress"
    assert client.post(f"{CLAIM}/start").status_code == 409


def test_approve_under_limit_then_pay(client):
    assert decide(client).json()["status"] == "decided"
    claim = pay(client, 420.0).json()
    assert claim["payment"]["amount"] == 420.0
    assert claim["decision"]["policy_section"] == "3. Trip Delay"


@pytest.mark.parametrize("decision", ["decline", "refer"])
def test_decline_and_refer_are_decided(client, decision):
    assert decide(client, decision, 0).json()["status"] == "decided"
    assert pay(client, 420.0).status_code == 409


def test_payout_only_on_approve(client):
    assert decide(client, "decline", 100).status_code == 422


def test_second_decision_is_409(client):
    decide(client)
    assert decide(client).status_code == 409


def test_over_limit_waits_for_sign_off(client):
    assert decide(client, payout=1500.0).json()["status"] == "awaiting_signoff"
    blocked = pay(client, 1500.0)
    assert blocked.status_code == 403
    assert "sign-off" in blocked.json()["detail"]
    claim = client.get(CLAIM).json()
    assert claim["payment"] is None
    assert claim["status"] == "awaiting_signoff"


def test_sign_off_pays_and_decides(client):
    decide(client, payout=1500.0)
    claim = client.post(f"{CLAIM}/sign-off", json={"handler_id": "HND-01"}).json()
    assert claim["status"] == "decided"
    assert claim["payment"]["amount"] == 1500.0
    assert claim["sign_off"]["handler_id"] == "HND-01"
    assert pay(client, 1500.0).status_code == 409


def test_sign_off_rules(client):
    sign_off = {"handler_id": "HND-01"}
    assert client.post(f"{CLAIM}/sign-off", json=sign_off).status_code == 409
    decide(client, payout=1500.0)
    unknown = {"handler_id": "HND-99"}
    assert client.post(f"{CLAIM}/sign-off", json=unknown).status_code == 403


def test_payment_rules(client):
    assert pay(client, 420.0).status_code == 409
    decide(client)
    assert pay(client, 500.0).status_code == 422
    pay(client, 420.0)
    assert pay(client, 420.0).status_code == 409


def test_steps(client):
    client.post(f"{CLAIM}/steps", json={"kind": "tool", "text": "get_claim"})
    client.post(f"{CLAIM}/steps", json={"kind": "result", "text": "the claim"})
    steps = client.get(f"{CLAIM}/steps").json()
    assert [s["text"] for s in steps] == ["get_claim", "the claim"]
    assert client.get("/api/claims/CLM-9999/steps").status_code == 404
