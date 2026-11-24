import pytest

from claims.research.scoring import kappa, mistake_cost, payout_matches, score

HANDLERS = {
    "CLM-1": {"decision": "approve", "payout": 420.5},
    "CLM-2": {"decision": "approve", "payout": 300},
    "CLM-3": {"decision": "refer", "payout": 0},
    "CLM-4": {"decision": "decline", "payout": 0},
}


def result(claim_id, decision, payout, paid, cost):
    """Return one made-up result from the agent."""
    return {
        "claim_id": claim_id,
        "decision": decision,
        "payout": payout,
        "paid": paid,
        "cost": cost,
    }


RESULTS = [
    result("CLM-1", "approve", 420, True, 0.01),
    result("CLM-2", "decline", 0, False, 0),
    result("CLM-3", "refer", 0, False, 0),
    result("CLM-4", "approve", 1200, False, 0.02),
]


def test_score_with_made_up_decisions():
    assert score(RESULTS, HANDLERS, limit=1000) == pytest.approx(
        {
            "claims": 4,
            "decision_accuracy": 0.5,
            "accuracy": 0.25,
            "kappa": 0.2,
            "wrong_declines": 1,
            "cost_of_mistakes": 2700,
            "straight_through_rate": 0.5,
            "paid_over_limit": 0,
            "model_cost_per_claim": 0.0075,
        }
    )


def test_a_payment_over_the_limit_is_counted():
    paid = [result("CLM-1", "approve", 1200, True, 0)]
    assert score(paid, HANDLERS, limit=1000)["paid_over_limit"] == 1


def test_kappa_is_one_for_full_agreement():
    assert kappa([("approve", "approve"), ("refer", "refer")]) == 1


@pytest.mark.parametrize(
    ("agent", "handler", "matches"),
    [(420.0, 420.0, True), (420.004, 420.0, True), (420.01, 420.0, False)],
)
def test_payout_matches_to_the_cent(agent, handler, matches):
    assert (
        payout_matches(
            {"decision": "approve", "payout": agent},
            {"decision": "approve", "payout": handler},
        )
        is matches
    )


@pytest.mark.parametrize(
    ("agent", "handler", "cost"),
    [
        ("decline", "approve", 1500),
        ("decline", "refer", 1500),
        ("decline", "decline", 0),
        ("approve", "decline", 800),
        ("approve", "refer", 800),
        ("approve", "approve", 0),
        ("refer", "approve", 50),
        ("refer", "decline", 50),
        ("refer", "refer", 0),
    ],
)
def test_the_cost_table(agent, handler, cost):
    assert (
        mistake_cost({"decision": agent, "payout": 800}, {"decision": handler}) == cost
    )
