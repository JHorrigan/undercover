"""Score the agent's decisions against the handlers', as discovery defined it.

The cost table and the measures are in docs/discovery/07_evals.md.
"""

from collections import Counter

WRONG_DECLINE = 1500.0
NEEDLESS_REFERRAL = 50.0
LABELS = ("approve", "decline", "refer")


def payout_matches(agent: dict, handler: dict) -> bool:
    """True when the decision matches and the payout is right to the cent."""
    return agent["decision"] == handler["decision"] and round(
        agent["payout"] * 100
    ) == round(handler["payout"] * 100)


def wrong_decline(agent: dict, handler: dict) -> bool:
    """True when the agent declined a claim the handler didn't decline."""
    return agent["decision"] == "decline" and handler["decision"] != "decline"


def mistake_cost(agent: dict, handler: dict) -> float:
    """Return what a wrong decision costs, from the cost table."""
    if wrong_decline(agent, handler):
        return WRONG_DECLINE
    if agent["decision"] == "approve" and handler["decision"] != "approve":
        return agent["payout"]
    if agent["decision"] == "refer" and handler["decision"] != "refer":
        return NEEDLESS_REFERRAL
    return 0.0


def kappa(pairs: list[tuple[str, str]]) -> float:
    """Return Cohen's kappa for agreement between two sets of decisions."""
    total = len(pairs)
    observed = sum(a == b for a, b in pairs) / total
    agent = Counter(a for a, _ in pairs)
    handler = Counter(b for _, b in pairs)
    expected = sum(agent[label] * handler[label] for label in LABELS) / total**2
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def straight_through(agent: dict, limit: float) -> bool:
    """True when no handler was needed: a decline, or an approval paid in the limit."""
    approved_and_paid = agent["decision"] == "approve" and agent["paid"]
    return agent["decision"] == "decline" or (
        approved_and_paid and agent["payout"] <= limit
    )


def score(results: list[dict], handlers: dict[str, dict], limit: float) -> dict:
    """Score each claim's result against the handler's decision on it."""
    pairs = [(result, handlers[result["claim_id"]]) for result in results]
    total = len(pairs)
    return {
        "claims": total,
        "decision_accuracy": sum(a["decision"] == h["decision"] for a, h in pairs)
        / total,
        "accuracy": sum(payout_matches(a, h) for a, h in pairs) / total,
        "kappa": kappa([(a["decision"], h["decision"]) for a, h in pairs]),
        "wrong_declines": sum(wrong_decline(a, h) for a, h in pairs),
        "cost_of_mistakes": sum(mistake_cost(a, h) for a, h in pairs),
        "straight_through_rate": sum(straight_through(a, limit) for a, _ in pairs)
        / total,
        "paid_over_limit": sum(a["paid"] and a["payout"] > limit for a, _ in pairs),
        "model_cost_per_claim": sum(a["cost"] for a, _ in pairs) / total,
    }
