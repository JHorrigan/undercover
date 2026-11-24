# Status

Plan 001, the pilot, is being built. Phases 1 to 3 are done: the database and queue, the rules for decisions, payments and sign-off, and the agent.

## Plans

| Plan | What it adds | Status |
|---|---|---|
| [001](plans/001-pilot.md) | The pilot: the agent works the queue, the dashboard, scoring | In progress |

## What's built

- `backend/`: a SQLite database of UnderCover's records, built by `npm run seed`, the queue, the agent's reads (policy, history, wording, instructions), and the rules: a decision is recorded once, a payment matches the approved payout and is made once, and a payout over $1,000 waits for a handler's sign-off. The agent's instructions are in `backend/instructions.md`
- `agent/`: the UnderCover Agent. Six tools, each a thin call to the API, with the claim id set by code; the claim it reads has the customer's date of birth, street, email and phone withheld. Every tool call and model call, with its cost, is recorded as a step. `npm run agent` works the queue until it is empty
- `dashboard/`: one page that shows whether the backend is up
- `e2e/`: one test of that page

## Run it

`uv sync` and `npm install` once, then `npm run seed` to build the database and `npm run dev`. With the backend running, `npm run agent` works the queue on the real model, which costs money. `npm run check` runs every check.

## Known limits

- There is no sign-in, so anyone who can reach the API can sign off a payout. The agent can't, because it has no tool for it.
- If the agent fails on a claim, the worker stops with the error, and the claim stays in progress for a person to look at.
- Personal details are withheld by matching the customer's own records: the date of birth in four common formats, the street, the email and the phone as stored. A detail written some other way, such as `Feb 3, 1965` or `(702) 555-0118`, would reach the agent.

## Live checks

<TBD>
