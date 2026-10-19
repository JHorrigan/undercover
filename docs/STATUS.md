# Status

The claims pilot from `docs/PLAN.md` is built: all six phases are done and `npm run check` passes.

The harness from `docs/PLAN_HARNESS.md` is in progress: phases 1 to 4 are done (the queue agent: `uv run -m agent --cap 5`; the claim agent as a subagent with retries and failure handling; documents by section, the claims manual, DeepSeek V4.1 Flash by default; runs, the cap, to-do lists, failed claims and recovery in the backend). Delete `backend/undercover.db` to pick up the new tables.

## What's built

- **Backend** (`backend/`): FastAPI on SQLite at `backend/undercover.db`, or the path in `UNDERCOVER_DB`. It is seeded on startup from the files in `data/` listed in `backend/seed.py`, never from `data/evals/` or `data/security/`.
  - Reads (`reads.py`): `list_claims`, `get_claim`, `get_policy`, `get_customer`, `list_plans`, `list_handlers`, `get_policy_wording`, `get_instructions`.
  - Writes (`actions.py`): `start_claim`, `record_decision`, `pay_claim`, `sign_off_claim`, `add_step`, `list_steps`.
  - `run_agent` (`runs.py`) starts the agent on a waiting claim in the background.
  - The sign-off rule: an approval over $1,000 waits at `awaiting_signoff`, `pay_claim` returns 403 until a handler signs off, and the sign-off makes the payment.
- **Agent** (`agent/`): `run(claim_id, thread_id)` marks the claim in progress, loads its instructions from `GET /api/instructions` (the file `backend/instructions.md`), and logs each tool call and result as a step. Its tools in `agent/tools.py` only call the backend's API.
- **Dashboard** (`dashboard/`): the brand from `docs/BRAND.md`, light and dark.
  - `#/`: the queue with a status bar and a badge for each claim, refreshed every three seconds.
  - `#/claims/<id>`: the story, items, documents, policy and history; a button to run the agent; the decision, payout, reason and policy section; the agent's steps, polled every two seconds while it works; and the sign-off form for payouts over $1,000.
  - `#/instructions`: the agent's instructions, read only.
- **End-to-end tests** (`e2e/pilot.spec.ts`): the queue, a claim page, the sign-off rule and the instructions page. They run on their own backend (port 8100, a fresh `e2e/test.db`) and dashboard (port 5174), so they never touch the dev data or call a model.

## Claim statuses

`waiting`, then `in_progress` while the agent works, then `decided`, or `awaiting_signoff` for an approval over $1,000 until a handler signs off.

## Run it

- `npm run dev` starts the backend on port 8000 and the dashboard on http://localhost:5173.
- Run the agent from a claim's page, or with `uv run -m agent CLM-1001` while the backend is running.
- The agent uses `openai/gpt-6-luna`, or the model in `MODEL_NAME` such as `openrouter/free`. It needs `OPENROUTER_API_KEY` in `.env`.
- Delete `backend/undercover.db` to start again from the seed data.
- `npm run check` runs every check.

## Known limits

- If a run fails partway, for example on a model error, the claim stays `in_progress` and can't be run again. Delete the database to reset it.
- The instructions page shows the Markdown as plain text.

## Live checks

- CLM-1001: approved for $420.00 under 3. Trip Delay, and paid.
- CLM-1003: approved for $3,750.00 ($3,800 less the $50 Premium deductible). The agent's own payment was blocked with 403, and sign-off in the dashboard paid it.
