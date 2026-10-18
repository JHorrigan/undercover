import json
from pathlib import Path

from backend.main import app
from backend.seed import DATA


def test_list_claims(client):
    claims = client.get("/api/claims").json()
    assert len(claims) == 25
    assert {c["status"] for c in claims} == {"waiting"}
    first = claims[0]
    assert first["claim_id"] == "CLM-1001"
    assert first["customer_name"] == "Maya Patel"


def test_get_claim(client):
    claim = client.get("/api/claims/CLM-1001").json()
    assert claim["status"] == "waiting"
    assert claim["story"].startswith("My flight home from Rome")
    assert len(claim["items"]) == 3
    assert len(claim["documents"]) == 4


def test_missing_records_are_404(client):
    assert client.get("/api/claims/CLM-9999").status_code == 404
    assert client.get("/api/policies/POL-0000").status_code == 404
    assert client.get("/api/customers/CUS-0000").status_code == 404


def test_policy_and_customer(client):
    policy = client.get("/api/policies/POL-2001").json()
    assert policy["plan"] == "premium"
    customer = client.get("/api/customers/CUS-3001").json()
    assert customer["previous_claims"][0]["claim_id"] == "CLM-0412"


def test_plans_and_handlers(client):
    plans = client.get("/api/plans").json()
    assert [p["plan"] for p in plans["plans"]] == ["economy", "premium", "first"]
    handlers = client.get("/api/handlers").json()
    assert [h["handler_id"] for h in handlers] == ["HND-01", "HND-02", "HND-03"]


def test_documents(client):
    wording = client.get("/api/policy-wording").text
    assert wording.startswith("# UnderCover Travel Insurance: Policy Wording")
    assert client.get("/api/instructions").text.startswith("# UnderCover Agent")


def test_seed_never_opens_evals_or_security(client, monkeypatch, tmp_path):
    opened: list[Path] = []
    read_text = Path.read_text

    def spy(self, *args, **kwargs):
        opened.append(self.resolve())
        return read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", spy)
    monkeypatch.setenv("UNDERCOVER_DB", str(tmp_path / "spied.db"))
    with type(client)(app):
        pass
    assert opened
    hidden = [(DATA / "evals").resolve(), (DATA / "security").resolve()]
    assert not [p for p in opened if any(p.is_relative_to(h) for h in hidden)]


def test_queue_is_only_the_queue(client):
    queue = json.loads((DATA / "claims.json").read_text(encoding="utf-8"))
    ids = {c["claim_id"] for c in client.get("/api/claims").json()}
    assert ids == {c["claim_id"] for c in queue}
    assert client.get("/api/claims/CLM-1901").status_code == 404


def test_every_operation_is_documented():
    for path in app.openapi()["paths"].values():
        for operation in path.values():
            assert operation["operationId"]
            assert operation["description"]
