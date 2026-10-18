# Status

The claims pilot, being built from `docs/PLAN.md`.

## Built

- **Phase 1, backend data:** SQLite at `backend/undercover.db` (or `UNDERCOVER_DB`), seeded on startup from the files in `data/` listed in `backend/seed.py`; never from `data/evals/` or `data/security/`. Read operations: `list_claims`, `get_claim`, `get_policy`, `get_customer`, `list_plans`, `list_handlers`, `get_policy_wording`, `get_instructions`.
- `agent/`: still the hello-world skeleton.
- `dashboard/`: still the page that shows whether the backend is up.

## Run it

- `npm run dev` starts the backend on port 8000 and the dashboard on port 5173.
- Delete `backend/undercover.db` to start again from the seed data.
- `npm run check` runs every check.
