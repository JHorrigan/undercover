# Status

Plan 001, the pilot, is done: the agent works the queue end to end, the dashboard shows its work, and its scores are below.

## Plans

| Plan | What it adds | Status |
|---|---|---|
| [001](plans/001-pilot.md) | The pilot: the agent works the queue, the dashboard, scoring | Done |

## What's built

- `backend/`: a SQLite database of UnderCover's records, built by `npm run seed`, the queue, the agent's reads (policy, history, wording, instructions), and the rules: a decision is recorded once, a payment matches the approved payout and is made once, and a payout over $1,000 waits for a handler's sign-off. The agent's instructions are in `backend/instructions.md`
- `agent/`: the UnderCover Agent. Six tools, each a thin call to the API, with the claim id set by code; the claim it reads has the customer's date of birth, street, email and phone withheld. Every tool call and model call, with its cost, is recorded as a step. `npm run agent` works the queue until it is empty
- `dashboard/`: the queue with counts by status; each claim with its story, items, documents, decision and the agent's steps as they happen; a handler's sign-off for payouts over the limit; the agent's instructions, read only. Dark by default, with a light mode. The look is in `dashboard/src/theme.css`, from `docs/BRAND.md`
- `claims/research/evaluate.py`: runs the agent on a set of claims (tiny, dev, held-out or security) on its own database and scores it against the handlers' decisions
- `e2e/`: browser tests of the queue, a keyboard-only sign-off and an axe check of every screen in both modes, on their own backend, dashboard and database

## Run it

`uv sync` and `npm install` once, then `npm run seed` to build the database and `npm run dev`. With the backend running, `npm run agent` works the queue on the real model, which costs money. `npm run check` runs every check.

## Known limits

- There is no sign-in, so anyone who can reach the API can sign off a payout. The agent can't, because it has no tool for it.
- If the agent fails on a claim, the worker stops with the error, and the claim stays in progress for a person to look at.
- Personal details are withheld by matching the customer's own records: the date of birth in four common formats, the street, the email and the phone as stored. A detail written some other way, such as `Feb 3, 1965` or `(702) 555-0118`, would reach the agent.

## Live checks

Run on 24 November 2026 with `uv run -m claims.research.evaluate <set>`, on `openai/gpt-6-luna` at low effort through OpenRouter, and scored in code as `docs/discovery/07_evals.md` defines each measure. Each run's report, with every claim's result, is in `claims/research/results/2026-11-24-<set>.json`. The four runs cost $0.039 in all, as OpenRouter reported it.

| Measure | Target, on the held-out claims | Held-out (25) | Development (25) | Tiny (5) |
|---|---|---|---|---|
| Decision accuracy | At least 85% | 72% | 72% | 80% |
| Accuracy: decision and payout, to the cent | At least 75% | 72% | 64% | 80% |
| Cohen's kappa | At least the handlers' own: <TBD: not yet measured as a kappa> | 0.52 | 0.51 | 0.69 |
| Wrong declines, including declines of claims the handler referred | No more than 1 in 25 | 2 | 1 | 0 |
| Cost of mistakes | Lower than a handler's on the same claims: <TBD: no handler figure for these claims> | $3,355 | $2,261 | $50 |
| Payments over $1,000 without a sign-off | None | 0 | 0 | 0 |
| Model cost per claim | Under $1 | $0.00073 | $0.00066 | $0.00071 |
| Straight-through rate | At least 50% in the pilot | 76% | 72% | 60% |

The security claim, CLM-1901, passed: declined, with nothing paid (`2026-11-24-security.json`).

The agent works from the policy wording alone for the pilot, as the spec says; the claims manual is not in yet.
