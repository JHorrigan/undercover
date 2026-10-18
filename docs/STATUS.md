# Status

The claims pilot, being built from `docs/PLAN.md`.

## Built

- **Phase 1, backend data:** SQLite at `backend/undercover.db` (or `UNDERCOVER_DB`), seeded on startup from the files in `data/` listed in `backend/seed.py`; never from `data/evals/` or `data/security/`. Read operations: `list_claims`, `get_claim`, `get_policy`, `get_customer`, `list_plans`, `list_handlers`, `get_policy_wording`, `get_instructions`.
- **Phase 2, decisions and payments:** `start_claim`, `record_decision`, `pay_claim`, `sign_off_claim`, `add_step` and `list_steps` in `backend/actions.py`. An approval over $1,000 waits at `awaiting_signoff`; `pay_claim` returns 403 until a handler signs off, and sign-off makes the payment.
- `agent/`: still the hello-world skeleton.
- `dashboard/`: still the page that shows whether the backend is up.

## Run it

- `npm run dev` starts the backend on port 8000 and the dashboard on port 5173.
- Delete `backend/undercover.db` to start again from the seed data.
- `npm run check` runs every check.
