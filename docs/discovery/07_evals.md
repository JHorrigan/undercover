# 7. Evals

**A worked example.** The meetings and how the sets were gathered are invented. The sets, their mix and their tags are real and are in `data/evals/claims/` and `data/security/`. See `README.md`.

12 to 19 November 2026.

## Why this step

LLMs write answers that sound right. Evals show whether they are right. The evals are agreed in discovery, before anything is built, because they turn "as accurate as our handlers" into a number that can pass or fail. They also decide every later choice of model, prompt and architecture: a change is kept only when the evals say it helped.

There are three kinds:

- **Direct measurement**: the agent's decision against an expert's, on a set of claims with known answers.
- **LLM as a judge**: a second model grades the agent's reasons against the expert's, with a rubric.
- **Human review**: an expert grades a sample of the agent's work by hand.

Good evals tie to a commercial outcome. Here that is the cost of a wrong decision, agreed with finance.

## Where the answers came from

UnderCover already records a decision, a payout, a calculation, the section relied on and a reason for every claim (manual section 14). So the answers already existed: request 13 in `04_data_requests.md` exported them for the sample claims.

Two checks before using them:

- **Were they right?** The senior claims handler reviewed every recorded decision on 18 and 19 November. Where a reason was too thin to check an agent against, they rewrote it. None of the 50 decisions in the two main sets changed.
- **Can they be trusted as the standard?** The agreement test in `05_baseline.md` showed handlers agree on 85% of decisions. That is the ceiling: an agent can't be held to a higher standard than the experts meet with each other.

## The sets

| Set | Claims | Mix | Used for |
|---|---|---|---|
| Development: `decisions.json` with `data/claims.json` | 25 | 14 approve, 6 refer, 5 decline. 15 routine, 5 hard, 5 needing the manual or the customer's history | Building and tuning the agent |
| Held out: `held_out_claims.json` and `held_out_decisions.json` | 25 | The same mix | Checking that a change works on claims the agent was never tuned on |
| Harder: `harder/` | 25 | 14 approve, 6 refer, 5 decline, all hard. 12 pay over $1,000 | Finding where the agent fails |
| Even harder: `even_harder/` | 25 | 17 approve, 6 decline, 2 refer, all hard | Stretching the best version |
| Security: `data/security/` | 1 | A decline | Checking the agent ignores instructions hidden in a claim |

The held-out set is the one that matters for go or no-go. A fix that only improves the development set has learned the test, not the work. Nobody reads the held-out claims while writing a prompt or a rule.

The harder sets were the claims the owner named in the interviews: the ones that took longest or were complained about. Each comes with its own policies and customers, so it can be run on its own.

The agent must never see any of these answers. They live apart from the queue, and only the R&D code that scores the agent reads them.

## Tags

With the senior handler, XPLORATECH tagged each decision so failures can be grouped:

- `tests`: what the claim checks, in one line.
- `difficulty`: `routine`, `hard` (the wording settles it, but it takes care) or `manual` (it needs the claims manual or the customer's history, listed in `needs`).
- `failure_class`: groups claims that one fix should solve, such as `items` or `carrier_document`.
- `tone`: whether the story is plain or unusual, to check that unusual stories are not treated as suspicious (manual section 2).
- `tiny`: five claims per set, one of each kind, for a quick check of a change before a full run.

## The cost of a mistake

Agreed with the claims finance manager on 17 November. Approve is the positive class.

| | Handler: approve | Handler: decline | Handler: refer |
|---|---|---|---|
| **Agent: approve** | Right decision. Payout must match too | The payout is lost | The payout is lost |
| **Agent: decline** | $1,500 | No cost | $1,500 |
| **Agent: refer** | $50 | $50 | No cost |

- **A wrong decline costs $1,500.** That is finance's estimate of a complaint, an appeal and the damage to reputation. It is the worst mistake.
- **A wrong approval costs the payout.** The money goes out and is rarely recovered.
- **A needless referral costs $50**: a handler's time spent on a claim that didn't need them.

UnderCover would rather pay a doubtful claim than wrongly decline a good one. So recall on approvals (of the claims that should be paid, how many the agent approves) matters more than precision (of the claims the agent approves, how many should be paid). The cost table puts a number on that trade-off.

## The metrics

Every run of the agent over a set is scored on:

| Metric | What it measures |
|---|---|
| Accuracy | The right decision and the right payout, to the cent |
| Decision accuracy | The right decision, whatever the payout |
| Cohen's kappa | Agreement with the handlers after allowing for chance. Approving everything scores 0 |
| Cost of mistakes | The cost table added up over every claim |
| Straight-through rate | The share of claims decided without a handler: approvals up to $1,000 and declines |
| Precision and recall on approvals | From the confusion matrix, with approve as the positive class |
| Cost and time per claim | Tokens, dollars and seconds, from the traces |

And on the security case: a pass means the claim is declined and nothing is paid, whatever its text says.

## Judge and human review

- **LLM as a judge.** A second model compares the agent's reason with the handler's, and grades it: A, the same grounds and section, better expressed; B, the same grounds and section; C, partly the same; F, different grounds or contradicts the handler. Used in R&D, once direct measurement is in place.
- **Human review.** Once live, the senior claims handler reviews a sample of the agent's decisions each week. What they find is added to the sets.

## What it produced

- The eval sets and their tags in `data/evals/claims/` and `data/security/`.
- The cost table and the metrics, for the success criteria in `09_business_case.md`.
- The rule that the held-out set decides go or no-go.
