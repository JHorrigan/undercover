# Status

The claims pilot, being built from `docs/PLAN.md`.

## Built

- **Phase 1, backend data:** SQLite at `backend/undercover.db` (or `UNDERCOVER_DB`), seeded on startup from the files in `data/` listed in `backend/seed.py`; never from `data/evals/` or `data/security/`. Read operations: `list_claims`, `get_claim`, `get_policy`, `get_customer`, `list_plans`, `list_handlers`, `get_policy_wording`, `get_instructions`.
- **Phase 2, decisions and payments:** `start_claim`, `record_decision`, `pay_claim`, `sign_off_claim`, `add_step` and `list_steps` in `backend/actions.py`. An approval over $1,000 waits at `awaiting_signoff`; `pay_claim` returns 403 until a handler signs off, and sign-off makes the payment.
- **Phase 3, the agent:** `agent/main.py` `run(claim_id, thread_id)` marks the claim in progress, loads its instructions from `GET /api/instructions` (the file `backend/instructions.md`), and logs each tool call and result as a step. Its tools in `agent/tools.py` only call the backend's API. `run_agent` starts it from the API in the background. Live check: CLM-1001 approved for $420.00 under 3. Trip Delay, and paid.
- **Phase 4, dashboard and queue:** the brand from `docs/BRAND.md` in `dashboard/src/styles.css` (light and dark), hash routes in `hooks.ts`, typed API calls in `api.ts`, and the queue page with a status bar and a badge for each claim. It refreshes every three seconds.

## Run it

- `npm run dev` starts the backend on port 8000 and the dashboard on port 5173.
- Delete `backend/undercover.db` to start again from the seed data.
- `uv run -m agent CLM-1001` runs the agent on one claim; the backend must be running on port 8000.
- `npm run check` runs every check.
