# The claims pilot

From the head of claims operations at UnderCover Travel Insurance.

## How claims work today

UnderCover sells travel insurance on three plans: Economy, Premium and First. Our three claims handlers work through a queue of claims by hand. For each claim, a handler reads the customer's story and documents and checks them against the policy and our policy wording. Then they approve the claim with a payout, decline it or refer it. A claim is referred when it needs someone's judgment or more information, as the claims manual explains.

## The pilot

We want an AI agent, the UnderCover Agent, to work the queue the way a handler does. Our goal is to handle claims straight through, as accurately as our handlers do.

## The success criteria we agreed

<TBD: the baseline of how the work performs today, and each criterion.>

The figures for each come from our records, worked out in code.

## Working claims

For each claim the agent should:

- read the claim, the customer's policy and claim history, and the policy wording
- approve, decline or refer the claim
- work out the payout when it approves
- explain the decision in two or three sentences, along with the relevant section of the policy

## Improving the agent

<TBD>

## Security

<TBD>

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

- Alone: approve, decline or refer a claim, and pay an approved claim of $1,000 or less.
- Needs approval: paying an approved claim over $1,000, which waits for a handler's sign-off.
- Never: see the handlers' decisions in `data/evals/claims/`, or pay a claim over $1,000 before a handler signs off.

## Our records

Everything is in `data/`, described in `data/README.md`: the claims queue, the policies, the customers, the plans, the handlers, the policy wording and the claims manual. The held-out claims in `data/evals/claims/` are for checking the agent later and stay out of the queue.

## Not for now

- The claims manual. For the pilot, the agent works from the policy wording alone.
- No sign-in.
- No real payments.
- No messages to customers.
