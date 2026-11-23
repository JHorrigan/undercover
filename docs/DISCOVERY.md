# Discovery

What we found, before anything is built. Written once for the client, before any app's `SPEC.md`. Each use case that is chosen becomes an app, and its spec is agreed from this.

## The problems

Claims are worked by hand. UnderCover's three claims handlers work through a queue of claims one at a time. For each claim, a handler reads the customer's story and documents and checks them against the policy and the policy wording, then approves the claim with a payout, declines it or refers it. A claim is referred when it needs someone's judgement or more information, as the claims manual explains.

How it can be measured: the time a handler spends on each claim, the number of claims waiting, and how often a decision agrees with the handlers' own decisions in `data/evals/claims/`. <TBD: which of these the client tracks today.>

## The baseline

<TBD: how long a claim takes today, how many claims come in, and the cost of handling them, from UnderCover's own records.>

## The use cases, ranked

Each use case is ranked with ICE and named as one of three kinds:

- **Automation**: do things cheaper.
- **Acceleration**: do things faster.
- **Differentiation**: do different things.

Each one is tested: does it solve a measurable problem, does it use the client's own data and systems, and can its benefit be measured? First ask whether it can be solved without an agent, or without an LLM at all.

| Rank | Use case | Kind | ICE | Measurable problem | Uses their data and systems | Benefit measurable | Without an agent or LLM? |
|---|---|---|---|---|---|---|---|
| 1 | Deciding claims: approve, decline or refer each claim, work out the payout and explain the decision | Automation | <TBD> | Yes: decisions are scored against the handlers' own | Yes: the claims, policies, customers, plans, policy wording and claims manual in `data/` | Accuracy yes; time and cost once the baseline is known | No: each claim is a customer's story and documents in free text, read against the policy wording |

## The success criteria

UnderCover's goal: to handle claims straight through, as accurately as its handlers do.

<TBD: the figures agreed with the client, such as the share of decisions and payouts that must match the handlers', before anything is built.>
