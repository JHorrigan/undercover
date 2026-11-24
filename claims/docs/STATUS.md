# Status

Plan 001, the pilot, is being built. Phase 1 is done: the database and the queue.

## Plans

| Plan | What it adds | Status |
|---|---|---|
| [001](plans/001-pilot.md) | The pilot: the agent works the queue, the dashboard, scoring | In progress |

## What's built

- `backend/`: a SQLite database of UnderCover's records, built by `npm run seed`, and the queue: `GET /api/claims` and `GET /api/claims/{claim_id}`
- `agent/`: the entry point `run(claim_id, thread_id)`, with one tool that calls the health route
- `dashboard/`: one page that shows whether the backend is up
- `e2e/`: one test of that page

## Run it

`uv sync` and `npm install` once, then `npm run seed` to build the database and `npm run dev`. `npm run check` runs every check.

## Known limits

<TBD>

## Live checks

<TBD>
