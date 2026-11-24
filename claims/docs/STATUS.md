# Status

Plan 001, the pilot, is being built. Phases 1 to 4 are done: the database and queue, the rules for decisions, payments and sign-off, the agent, and the dashboard.

## Plans

| Plan | What it adds | Status |
|---|---|---|
| [001](plans/001-pilot.md) | The pilot: the agent works the queue, the dashboard, scoring | In progress |

## What's built

- `backend/`: a SQLite database of UnderCover's records, built by `npm run seed`, the queue, the agent's reads (policy, history, wording, instructions), and the rules: a decision is recorded once, a payment matches the approved payout and is made once, and a payout over $1,000 waits for a handler's sign-off. The agent's instructions are in `backend/instructions.md`
- `agent/`: the UnderCover Agent. Six tools, each a thin call to the API, with the claim id set by code; the claim it reads has the customer's date of birth, street, email and phone withheld. Every tool call and model call, with its cost, is recorded as a step. `npm run agent` works the queue until it is empty
- `dashboard/`: the queue with counts by status; each claim with its story, items, documents, decision and the agent's steps as they happen; a handler's sign-off for payouts over the limit; the agent's instructions, read only. Dark by default, with a light mode. The look is in `dashboard/src/theme.css`, from `docs/BRAND.md`
- `e2e/`: browser tests of the queue, a keyboard-only sign-off and an axe check of every screen in both modes, on their own backend, dashboard and database

## Run it

`uv sync` and `npm install` once, then `npm run seed` to build the database and `npm run dev`. With the backend running, `npm run agent` works the queue on the real model, which costs money. `npm run check` runs every check.

## Known limits

- There is no sign-in, so anyone who can reach the API can sign off a payout. The agent can't, because it has no tool for it.
- If the agent fails on a claim, the worker stops with the error, and the claim stays in progress for a person to look at.
- Personal details are withheld by matching the customer's own records: the date of birth in four common formats, the street, the email and the phone as stored. A detail written some other way, such as `Feb 3, 1965` or `(702) 555-0118`, would reach the agent.

## Live checks

<TBD>
