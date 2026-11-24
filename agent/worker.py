"""Work the queue: take the next waiting claim and decide it, until none are left."""

from agent.api import take_next_claim
from agent.main import run


def work_queue() -> int:
    """Decide every waiting claim, one at a time, and return how many were decided."""
    decided = 0
    while claim := take_next_claim():
        claim_id = claim["claim_id"]
        print(f"{claim_id}: working")
        run(claim_id, thread_id=claim_id)
        decided += 1
    return decided


if __name__ == "__main__":
    print(f"Queue empty after {work_queue()} claims")
