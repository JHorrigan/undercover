"""Run the UnderCover Agent: uv run -m agent --cap 5, or uv run -m agent CLM-1001."""

import argparse

from agent.harness import run_one, run_queue

parser = argparse.ArgumentParser(prog="uv run -m agent")
parser.add_argument("claim_id", nargs="?", help="work one named claim")
parser.add_argument("--cap", type=int, help="work the queue, up to this many claims")
args = parser.parse_args()
if args.cap:
    print(run_queue(args.cap))
elif args.claim_id:
    print(run_one(args.claim_id))
else:
    parser.error("give a claim id or --cap")
