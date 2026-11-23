# 5. Baseline

**A worked example.** Figures marked *invented* are made up. Figures marked *from the data* are worked out from the files in `data/`. See `README.md`.

21 to 25 September 2026.

## Why this step

The baseline is how the work performs today, from the client's own records. Without it there is no way to show what the build saved, and no way to agree success criteria that mean anything.

Each figure needs a source and a method, so it can be measured again the same way once the build is live. When the client doesn't measure something today, measuring it becomes part of discovery, as the agreement test below shows.

Cover all three: how much work there is, how long and how much it costs, and how good the decisions are.

## Volume

| Measure | Figure | Source |
|---|---|---|
| Claims in 2025 | About 6,600 | Claims system, claims by month submitted. *Invented* |
| Claims a month, September to May | About 420 | As above. *Invented* |
| Claims a month, June to August | About 950 | As above. *Invented* |
| Claims a handler decides in a day | About 8 | Sitting with the handlers: 50 claims in two days by three handlers. *Invented* |
| What the team can decide in a month | About 520 | 3 handlers, about 8.3 claims a day each, 21 working days. *Invented* |

From June to August the queue grows by over 400 claims a month. That backlog is the sponsor's problem from the kickoff.

## Time and cost

| Measure | Figure | Source |
|---|---|---|
| Share of claims that are routine | 60% (15 of 25) | The difficulty tag on `data/evals/claims/decisions.json`. *From the data* |
| Handler time, routine claim | 40 minutes, median | `03_process_map.md`. *Invented* |
| Handler time, hard claim | 75 minutes, median | As above. *Invented* |
| Handler time, average claim | 54 minutes | 60% at 40 minutes and 40% at 75. *Invented* |
| Days from submitted to decided, September to May | 3 working days, median | Claims system, submitted and decided dates. *Invented* |
| Days from submitted to decided, June to August | 16 working days, median | As above. *Invented* |
| Cost of a handler hour, fully loaded | $40 | Finance. *Invented* |
| Handling cost per claim | $36 | 54 minutes at $40 an hour. *Invented* |
| Temporary staff for the 2025 peak | $48,000 | Finance. *Invented* |
| Share of claims decided without a handler | 0% | Every claim is worked by hand today |

## Quality

Nobody checked decisions before discovery, so we measured it. From 22 to 24 September each handler re-decided recent claims from the claims system that someone else had decided, without seeing the first decision.

| Measure | Figure | Source |
|---|---|---|
| Same decision as the first handler | 85% (17 of 20) | The agreement test. *Invented* |
| Same decision and same payout | 75% (15 of 20) | As above. *Invented* |
| Complaints about a decline in 2025 | 38 | Complaints log. *Invented* |
| Declines overturned on complaint | 9 of 38 | As above. *Invented* |

Cohen's kappa for the agreement test, which allows for agreement by chance, will be worked out in code in R&D, from the same 20 claims.

## The decision mix

From `data/evals/claims/decisions.json`, the handlers' decisions on the 25 sample claims. *From the data.*

| Decision | Claims | Share |
|---|---|---|
| Approve | 14 | 56% |
| Refer | 6 | 24% |
| Decline | 5 | 20% |

Three of the 14 approvals pay over $1,000 and need a handler's sign-off. The median amount claimed is $830.

A system that approved every claim would get 56% of decisions right, so 56% is the floor any agent must clear. The handlers' 85% agreement with each other is the ceiling it can be measured against: an agent that agrees with the handlers as often as they agree with each other is doing the job as well as they do.

## What it produced

- The baseline in `docs/DISCOVERY.md`.
- The floor (56%) and the ceiling (85%) for the success criteria in `09_business_case.md`.
- The cost per claim today ($36), to set against the agent's cost per claim.
- A method for each figure, so it can be measured again after go-live.
