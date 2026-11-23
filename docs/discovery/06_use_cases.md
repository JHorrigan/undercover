# 6. Use cases

**A worked example.** The ideas, scores and reasoning below are invented. See `README.md`.

Workshop on Tuesday 22 September 2026, two hours, with the owner, the senior claims handler, the claims finance manager and the head of IT.

## Why this step

There are always more ideas than budget. Ranking them in the open, with the people who will use the result, shows which one to build first and why. Each idea is tested against the three traps:

1. **The agent for X.** Does it solve a business problem you can measure? Can it be solved without an agent, or without an LLM at all?
2. **Human-like agents.** Is the design one agent per job title, or one agent with a controlled workflow that grows only when the evals say so?
3. **Plausible, not accurate.** Can its output be checked against a right answer?

Each idea is also named as one of three kinds: **automation** (do things cheaper), **acceleration** (do things faster) or **differentiation** (do different things).

## How we scored

ICE, each out of 10, multiplied for the score:

- **Impact**: how much of the measured problem it removes.
- **Confidence**: how sure we are it works, given the data we have.
- **Ease**: how quickly it can be built and taken into use.

## The ideas, ranked

| Rank | Use case | Kind | I | C | E | ICE | Measurable problem | Uses their data and systems | Benefit measurable | Without an agent or LLM? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Deciding claims: approve, decline or refer, with the payout and the reason | Automation | 9 | 7 | 6 | 378 | Yes: 54 minutes and $36 a claim, and the summer backlog | Yes: claims, policies, customers, wording, manual | Yes: against the handlers' decisions | No: each claim is a story and documents in free text, read against the wording |
| 2 | Asking customers for missing documents, and chasing them | Acceleration | 6 | 7 | 8 | 336 | Yes: referred claims wait for documents | Yes: claims and the document list in manual section 5 | Yes: days waiting for a document | Partly: the list of what is missing needs reading; the chasing is a plain workflow |
| 3 | A payout calculator | Automation | 4 | 9 | 9 | 324 | Yes: 5 minutes a claim on a spreadsheet | Yes: plans and company settings | Yes: payouts against the handlers' | **Yes: plain code, no LLM** |
| 4 | A copilot for handlers: ask questions about a claim, the wording or the manual | Acceleration | 6 | 6 | 5 | 180 | Partly: time spent finding things | Yes | Harder: time saved per question | No |
| 5 | Spotting patterns across claims for Special Investigations | Differentiation | 7 | 3 | 3 | 63 | Not yet: fraud losses aren't measured today | Partly: needs years of history | Not yet | Unknown |
| 6 | A chatbot for customers to ask about their cover | Differentiation | 3 | 4 | 4 | 48 | No: nobody could name a problem it solves | Partly | No | Not tested |

## What we decided

- **Deciding claims comes first.** It goes straight at the baseline: the time and cost per claim and the summer backlog. And it can be checked against the handlers' decisions.
- **The payout calculator is not a use case of its own.** It needs no LLM, so it is built as code inside use case 1, as a tool the agent calls. Its score shows it is worth doing, just not as an AI project.
- **Document requests come next**, once claims are being decided and referrals are flowing.
- **The copilot** goes in `claims/docs/IDEAS.md`, to revisit once the agent is live and handlers can say what they would ask it.
- **Special Investigations patterns** wait until fraud losses are measured. Without a baseline there is no way to show it worked.
- **The customer chatbot is dropped.** It was the one idea that started from the technology instead of a problem.

## One agent, not a team

The sponsor's first sketch had a "claims manager agent", a "fraud checker agent" and a "payout agent". That is the human-like agents trap: it copies the org chart, not the work.

We start with one agent and a controlled workflow:

- **The model** makes the judgement calls: is the claim covered, which benefit, which lines count, and the reason.
- **Code** does the rules: looking things up, the filing window, the repeat-claim count, the limits, the deductible and the payout, given to the model as tools.
- **The system that pays** holds the $1,000 sign-off, where no agent can get round it.

A second agent is added only when the evals show it helps: for focus on one kind of claim, an independent check, a cheaper model for routine steps, or speed.

## What it produced

- The ranked table and the first use case in `docs/DISCOVERY.md`.
- The `claims/` app, with its spec in `claims/docs/SPEC.md`.
- The split between model and code, carried into `08_autonomy_and_risk.md`.
- The ideas kept for later, for `claims/docs/IDEAS.md`.
