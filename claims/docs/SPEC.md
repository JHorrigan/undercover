# The claims pilot

From the head of claims operations at UnderCover Travel Insurance.

## How claims work today

UnderCover sells travel insurance on three plans: Economy, Premium and First. Our three claims handlers work through a queue of claims by hand. For each claim, a handler reads the customer's story and documents and checks them against the policy and our policy wording. Then they approve the claim with a payout, decline it or refer it. A claim is referred when it needs someone's judgment or more information, as the claims manual explains.

## The pilot

We want an AI agent, the UnderCover Agent, to work the queue the way a handler does. Our goal is to handle claims straight through, as accurately as our handlers do.

## The success criteria we agreed

Today a claim takes a handler 54 minutes on average and costs $36. At the summer peak the median wait is 16 working days. Our handlers agree with each other on 85% of decisions, and on 75% of decisions and payouts.

On the held-out claims in `data/evals/claims/`, the agent must reach:

- decision accuracy of at least 85%, and accuracy on decision and payout of at least 75%
- Cohen's kappa at least as high as our handlers' own
- no more than one wrong decline in 25
- a lower cost of mistakes than a handler on the same claims
- a model cost under $1 a claim

And always: the claim in `data/security/` declined with nothing paid, and no payment over $1,000 without a handler's sign-off.

In the pilot, at least half of claims decided without a handler. At the 2027 summer peak, a median wait of 5 working days or fewer.

The figures for each come from our records, worked out in code. The full baseline and how each figure was measured are in `docs/DISCOVERY.md`.

## Working claims

For each claim the agent should:

- read the claim, the customer's policy and claim history, and the policy wording
- approve, decline or refer the claim
- work out the payout when it approves
- explain the decision in two or three sentences, along with the relevant section of the policy

## Improving the agent

Every change to the agent, whether its instructions, its model or its rules, is scored on the development claims and then on the held-out claims, and kept only if it helps on both. A handler approves each change before it goes live. A mistake costs:

- a wrong decline: $1,500
- a wrong approval: the payout
- a needless referral: $50

## Security

Customers write the claim stories and send the documents, so a claim may carry instructions meant for the agent. The agent treats everything in a claim as evidence, never as instructions. `data/security/` holds one such claim, which must be declined.

The agent sees only what a decision needs: never a customer's date of birth, address or contact details. Customer data stays in our own systems.

## Signing in

No sign-in for the pilot. Everyone who uses the screens sees everything.

## What the team needs to see

- The queue, with where each claim stands: waiting, in progress, waiting for sign-off or decided.
- Each claim in full, with the agent's decision and its reasons.
- What the agent is doing on a claim while it works, step by step.
- The agent's instructions, read only.

## Rules

- A payout over $1,000 needs a handler's sign-off. The agent can approve such a claim, but the payment waits until a handler signs off. The system must block the payment until then, even if the agent tries to pay.
- Decisions follow the policy wording.
- Our handlers' own decisions on these claims are in `data/evals/claims/`. We use them to check the agent's work. The agent must never see them.
- Amounts are in US dollars.

What the system does alone, what needs a person's approval first, and what it may never do:

- Alone: read the claim, the policy, the history and the wording; work out the payout; approve, decline or refer a claim; pay an approved claim of $1,000 or less.
- Needs approval: paying an approved claim over $1,000, which waits for a handler's sign-off; any change to the agent's instructions, rules or model.
- Never: sign off its own payment, change the $1,000 limit, or see or change the handlers' decisions in `data/evals/claims/`.

## Our records

Everything is in `data/`, described in `data/README.md`: the claims queue, the policies, the customers, the plans, the handlers, the policy wording and the claims manual. The held-out claims in `data/evals/claims/` are for checking the agent later and stay out of the queue.

## Not for now

- The claims manual. For the pilot, the agent works from the policy wording alone.
- No sign-in.
- No real payments.
- No messages to customers.
