# Status

A hello-world skeleton is in place, with every check passing. The spec is ready for the first plan, the pilot.

## Plans

| Plan | What it adds | Status |
|---|---|---|
| None yet | | |

## What's built

- `backend/`: one route, `GET /api/health`
- `agent/`: the entry point `run(claim_id, thread_id)`, with one tool that calls the health route
- `dashboard/`: one page that shows whether the backend is up
- `e2e/`: one test of that page

## Run it

`uv sync` and `npm install` once, then `npm run dev`. `npm run check` runs every check.

## Known limits

<TBD>

## Live checks

<TBD>
