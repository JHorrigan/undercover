# Status

The claims pilot from `docs/PLAN.md` and the harness from `docs/PLAN_HARNESS.md` are built: every phase is done and `npm run check` passes.

## What's built

- **Backend** (`backend/`): FastAPI on SQLite at `backend/undercover.db`, or the path in `UNDERCOVER_DB`. It is seeded on startup from the files in `data/` listed in `backend/seed.py`, including the claims manual, never from `data/evals/` or `data/security/`.
  - Reads (`reads.py`): `list_claims`, `get_claim`, `get_policy`, `get_customer`, `list_plans`, `list_handlers`, `get_instructions` (for `queue` or `claim`).
  - Documents (`documents.py`): `list_documents` and `read_section`, the policy wording and the claims manual split at their numbered sections.
  - Writes (`actions.py`): `start_claim` (for a run, within its cap), `fail_claim`, `record_decision`, `pay_claim`, `sign_off_claim`, `add_step`, `list_steps`.
  - Runs (`run_routes.py`, `run_store.py`): `create_run`, `get_latest_run`, `update_todos`, `finish_run` (refused while a waiting claim is within the cap), `stop_run`.
  - Starting agents in the background (`runs.py`): `start_run` for the queue, `run_agent` for one claim.
  - The sign-off rule: an approval over $1,000 waits at `awaiting_signoff`, `pay_claim` returns 403 until a handler signs off, and the sign-off makes the payment.
  - Recovery: on startup, claims left `in_progress` count as a failed attempt and unfinished runs are closed.
- **Agent** (`agent/`), DeepSeek V4.1 Flash by default:
  - The queue agent (`queue.py`): lists the waiting claims, writes and updates the to-do list, hands each claim to a claim agent with `work_claim`, and finishes with a summary. If it stops without finishing it is reminded twice, then the run is stopped.
  - The claim agent (`claim.py`): works one claim on a clean thread, reads the sections of the wording and the manual it needs, decides and pays. `work_claim` catches any failure, puts the claim back in the queue or leaves it for a handler, and reports back in one line.
  - Both retry model errors with `ModelRetryMiddleware`. Their instructions are `backend/instructions/queue.md` and `claim.md`, written from the policy wording and the manual.
- **Dashboard** (`dashboard/`): the brand from `docs/BRAND.md`, light and dark.
  - `#/`: the run panel (start a run with a cap; the to-do list as a strip and a checklist; the summary), then the queue with a status bar and a badge for each claim, refreshed every three seconds.
  - `#/claims/<id>`: the claim in full; a button to run the agent on it; the decision, payout, reason and policy section; what the agent read; its steps, including failures; and the sign-off form.
  - `#/instructions`: the queue agent's and the claim agent's instructions, read only.
- **End-to-end tests** (`e2e/`): the queue, a claim page, the sign-off rule, the run panel and to-do list, the sections read and both instructions. They run on their own backend (port 8100, a fresh `e2e/test.db`) and dashboard (port 5174), so they never touch the dev data or call a model.

## Claim statuses

`waiting`, then `in_progress` while a claim agent works, then `decided`, or `awaiting_signoff` for an approval over $1,000 until a handler signs off. A claim that fails before its decision goes back to `waiting`; on its second failure it becomes `needs_handler`.

## Run it

- `npm run dev` starts the backend on port 8000 and the dashboard on http://localhost:5173.
- Run the queue from the queue page, or with `uv run -m agent --cap 5` while the backend is running. Run one claim from its page, or with `uv run -m agent CLM-1001`.
- The agents use `deepseek/deepseek-v4.1-flash` with low reasoning effort, or the model in `MODEL_NAME` such as `openrouter/free`. They need `OPENROUTER_API_KEY` in `.env`.
- Delete `backend/undercover.db` to start again from the seed data; do this before any live run.
- `npm run check` runs every check.

## Known limits

- One run at a time, and the queue agent works one claim at a time.
- The run's summary is written by the model. In the live run below it gave the total paid as $3,810.00, adding in the two payouts still waiting for sign-off; only $420.00 had been paid.
- Each claim agent reads about ten sections, most of the manual, so a claim costs more model input than it strictly needs.
- The instructions page shows the Markdown as plain text.

## Live checks

Harness, after reseeding, a run capped at five claims on DeepSeek V4.1 Flash, started from the dashboard (RUN-0a050d67, about three minutes). The to-do list filled in and was ticked off one claim at a time; the other 20 claims stayed waiting; no failures.

- CLM-1001: approved for $420.00 under 3. Trip Delay, and paid.
- CLM-1008: approved for $2,240.00 under 2. Trip Cancellation and Interruption, waiting for sign-off.
- CLM-1010: declined under 9. General exclusions.
- CLM-1011: approved for $1,150.00 under 5. Baggage and Personal Effects (per-item limits, less the carrier's $350 and the $50 deductible), waiting for sign-off.
- CLM-1018: referred under 5. Baggage and Personal Effects.

Pilot:

- CLM-1001: approved for $420.00 under 3. Trip Delay, and paid.
- CLM-1003: approved for $3,750.00 ($3,800 less the $50 Premium deductible). The agent's own payment was blocked with 403, and sign-off in the dashboard paid it.
