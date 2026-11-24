# Status

Plan 001, the pilot, is being built. Phases 1 and 2 are done: the database, the queue, and the rules for decisions, payments and sign-off.

## Plans

| Plan | What it adds | Status |
|---|---|---|
| [001](plans/001-pilot.md) | The pilot: the agent works the queue, the dashboard, scoring | In progress |

## What's built

- `backend/`: a SQLite database of UnderCover's records, built by `npm run seed`, the queue, the agent's reads (policy, history, wording, instructions), and the rules: a decision is recorded once, a payment matches the approved payout and is made once, and a payout over $1,000 waits for a handler's sign-off. The agent's instructions are in `backend/instructions.md`
- `agent/`: the entry point `run(claim_id, thread_id)`, with one tool that calls the health route
- `dashboard/`: one page that shows whether the backend is up
- `e2e/`: one test of that page

## Run it

`uv sync` and `npm install` once, then `npm run seed` to build the database and `npm run dev`. `npm run check` runs every check.

## Known limits

- There is no sign-in, so anyone who can reach the API can sign off a payout. The agent can't, because it has no tool for it.

## Live checks

<TBD>
