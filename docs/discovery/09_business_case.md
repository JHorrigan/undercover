# 9. Business case and sign-off

**A worked example.** The figures, meetings and sign-off below are invented. See `README.md`.

Presented to the project committee on Friday 20 November 2026.

## Why this step

Discovery ends with a decision: the sponsor agrees the scope and the budget for R&D, or stops. The business case gives them what they need to decide: what it is worth, what it costs, how success is measured, and how it will be taken into use.

## The problem

UnderCover decides about 6,600 claims a year by hand, at about $36 a claim. From June to August claims arrive faster than the team can decide them: the median wait goes from 3 to 16 working days, and the 2026 peak needed $48,000 of temporary staff. About 60% of claims are routine, and they take most of the handlers' time. See `05_baseline.md`.

## What it is worth

If the agent decides half of all claims without a handler (routine approvals up to $1,000, and declines):

| | Per year |
|---|---|
| Claims decided without a handler | About 3,300 |
| Handler time given back, at 40 minutes a routine claim | About 2,200 hours, a little over one handler's year |
| Value of that time, at $40 an hour | About $88,000 |
| Temporary staff no longer needed at peak | About $48,000 |
| **Total** | **About $136,000** |

The time goes back to the handlers for the hard claims, the referrals and customers whose claims are stuck. Nobody's role is removed.

## What it costs to run

- **The model**: an estimated few cents a claim, from the claim, the wording and the reasoning in each call. Measured in R&D on the real claims, by model, as a cost per correct decision. *Estimate, to be measured.*
- **AWS hosting**: <TBD: priced in R&D, once the architecture is chosen.>
- **The engineer's fees**: <TBD: agreed separately with the sponsor.>

## Success criteria

All measured on the held-out set unless stated, and all worked out in code.

| Criterion | Target | Why |
|---|---|---|
| Decision accuracy | At least 85% | As good as handlers agree with each other |
| Accuracy, decision and payout | At least 75% | As good as handlers agree on both |
| Cohen's kappa | At least the handlers' own, from the agreement test | Agreement beyond chance |
| Wrong declines | No more than 1 in 25 | The most costly mistake |
| Cost of mistakes | Lower than a handler's on the same claims | The commercial measure |
| The security case | Declined, nothing paid, every run | No hidden instruction is followed |
| Payments over $1,000 without sign-off | None, in any test | The control holds |
| Model cost per claim | Under $1 | Against $36 by hand |
| Straight-through rate, in the pilot | At least 50% | The source of the value above |
| Median wait at the 2027 peak | 5 working days or fewer | The sponsor's problem, measured after go-live |

The first eight are checked at the end of R&D. The last two are checked in the implementation phase, on live claims.

## R&D scope

Six weeks, from 23 November 2026:

1. Load the data and score a first agent on the development set.
2. Compare models and prompts on the evals, with cost per claim.
3. Run the best version once on the held-out set.
4. Report the results against the criteria above.

R&D ends with the sponsor deciding whether to build. Nothing goes live in R&D, and no customer is affected.

## Adoption plan

- **A champion**: the senior claims handler, who helped build the evals, leads the handlers' side.
- **Shadow first**: in the pilot, the agent decides alongside the handlers and pays nothing. Its decisions are compared with theirs before it acts on its own.
- **Training**: a half day for the handlers on reading the agent's decisions and signing off.
- **Open results**: the evals and live accuracy are visible to the team every week.
- **Rollout by claim type**: Trip Delay first, the most routine; then Baggage; Emergency Medical last.

## The decision

On 20 November 2026 the sponsor agreed the scope and the R&D plan above, with the budget <TBD: the agreed figure>. Conditions:

- The supplier review of the model provider is finished before development.
- The success criteria above are the bar for the build decision.

Discovery is closed. The `claims/` app moves to R&D.
