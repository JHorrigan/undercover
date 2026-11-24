# Discovery

What we found, before anything is built. Written once, before any app's `SPEC.md`. Each use case that is chosen becomes an app, and its spec is agreed from this.

Discovery ran from 9 to 20 November 2026. The full record, step by step, is in `docs/discovery/`. It is a worked example: UnderCover is fictional, and the meetings and most figures are invented.

- **Sponsor**: Chief Operating Officer
- **Owner**: Head of Claims Operations
- **Signed off**: 20 November 2026, scope and R&D plan agreed

## The problems

**Claims are worked by hand, and the queue overflows every summer.** Three claims handlers decide every claim. For each one, a handler reads the customer's story and documents and checks them against the policy, the policy wording and the claims manual, then approves with a payout, declines or refers. From June to August claims arrive faster than the team can decide them, and customers wait.

**Most of the time goes on routine claims.** About 60% of claims are routine, clearly covered or clearly excluded, and they take most of the handlers' time. The hard claims depend on the claims manual and on experience.

**Decision quality was never measured.** Nobody checked how often handlers agree with each other until discovery measured it.

How each is measured: the time and cost per claim, the wait from submitted to decided, and agreement with the handlers' recorded decisions. See `docs/discovery/02_interviews.md` and `03_process_map.md`.

## The baseline

From `docs/discovery/05_baseline.md`. Figures marked † are worked out from `data/`; the rest are invented.

| Measure | Today |
|---|---|
| Claims a year | About 6,600 |
| Claims a month, peak and off-peak | About 950 and 420, against 520 the team can decide |
| Handler time per claim, average | 54 minutes |
| Handling cost per claim | $36 |
| Median wait, peak and off-peak | 16 and 3 working days |
| Temporary staff at the 2026 peak | $48,000 |
| Claims decided without a handler | 0% |
| Handlers agreeing with each other, decision | 85% |
| Handlers agreeing with each other, decision and payout | 75% |
| Approving every claim would be right on | 56% † |

## The use cases, ranked

Each use case is ranked with ICE and named as one of three kinds:

- **Automation**: do things cheaper.
- **Acceleration**: do things faster.
- **Differentiation**: do different things.

Each one is tested: does it solve a measurable problem, does it use UnderCover's own data and systems, and can its benefit be measured? First ask whether it can be solved without an agent, or without an LLM at all.

From `docs/discovery/06_use_cases.md`.

| Rank | Use case | Kind | ICE | Measurable problem | Uses their data and systems | Benefit measurable | Without an agent or LLM? |
|---|---|---|---|---|---|---|---|
| 1 | Deciding claims: approve, decline or refer, with the payout and the reason | Automation | 378 | Yes | Yes | Yes, against the handlers' decisions | No |
| 2 | Asking customers for missing documents, and chasing them | Acceleration | 336 | Yes | Yes | Yes | Partly |
| 3 | A payout calculator | Automation | 324 | Yes | Yes | Yes | **Yes: built as code inside use case 1** |
| 4 | A copilot for handlers | Acceleration | 180 | Partly | Yes | Harder | No |
| 5 | Patterns across claims for Special Investigations | Differentiation | 63 | Not yet | Partly | Not yet | Unknown |
| 6 | A chatbot for customers | Differentiation | 48 | No | Partly | No | Not tested |

Use case 1 is chosen, as the `claims/` app.

## The success criteria

From `docs/discovery/09_business_case.md`. Measured on the held-out set in `data/evals/claims/`, worked out in code.

| Criterion | Target |
|---|---|
| Decision accuracy | At least 85% |
| Accuracy, decision and payout | At least 75% |
| Cohen's kappa | At least the handlers' own |
| Wrong declines | No more than 1 in 25 |
| Cost of mistakes | Lower than a handler's on the same claims |
| The security case in `data/security/` | Declined, nothing paid, every run |
| Payments over $1,000 without sign-off | None |
| Model cost per claim | Under $1 |
| Straight-through rate, in the pilot | At least 50% |
| Median wait at the 2027 peak | 5 working days or fewer |

The cost of a mistake, used for "cost of mistakes": a wrong decline $1,500, a wrong approval the payout, a needless referral $50. See `docs/discovery/07_evals.md`.
