"""Run the UnderCover Agent on one claim: uv run -m agent CLM-1001."""

import sys

from agent.claim import run_one

print(run_one(sys.argv[1]))
