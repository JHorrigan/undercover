"""Run the UnderCover Agent: uv run -m agent CLM-1001, or uv run -m agent --cap 5."""

import sys

from agent.claim import run_one
from agent.queue import run_queue

if sys.argv[1] == "--cap":
    print(run_queue(int(sys.argv[2])))
else:
    print(run_one(sys.argv[1]))
