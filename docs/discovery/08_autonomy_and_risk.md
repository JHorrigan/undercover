# 8. Autonomy and risk

**A worked example.** The meetings and assessments below are invented. See `README.md`.

Tuesday 17 November 2026, the second half of the workshop that ranked the use cases, 90 minutes, with the owner, the head of IT, the data governance lead, the claims finance manager and UnderCover's information security officer.

## Why this step

How much an agent may do on its own is a risk decision, made with the business before anything is built. Each action is assessed on its own:

- **Risk appetite**: how much the business will tolerate here.
- **Consequence**: what a mistake costs.
- **Verifiability**: whether a mistake can be spotted.
- **Reversibility**: whether it can be undone.
- **Security, privacy and IP**: what could leak or be misused.

Too little autonomy and every claim still lands on a handler. Too much and one bad decision costs more than the project saves.

## What the agent may do

| Action | Consequence | Reversible? | Level |
|---|---|---|---|
| Read a claim, its policy, the customer's history, the wording and the manual | None | Yes | Alone |
| Work out the payout, with the calculator in code | None until paid | Yes | Alone |
| Approve, decline or refer a claim | A wrong decline costs $1,500 | Yes, until the customer is told | Alone, every decision recorded with its reason |
| Pay an approved claim of $1,000 or less | The payout | Rarely | Alone |
| Pay an approved claim over $1,000 | The payout | Rarely | **A handler signs off first** |
| Change its own instructions, rules or model | Every later decision | Yes | **A handler approves first** |
| Sign off its own payment | Bypasses the control | No | **Never** |
| Change the $1,000 limit | Bypasses the control | No | **Never** |
| See the handlers' decisions in the eval sets | The evals stop meaning anything | No | **Never** |
| Change the eval sets | As above | No | **Never** |
| Write to a customer | Reputation, and the risk below | No | **Not in the pilot** |

The three "never" rules from the kickoff are all here. The $1,000 limit is enforced by the system that pays, not by asking the agent to respect it.

## What the handler sees when asked

Over-asking leads to rubber-stamping, so the agent asks only above the limit, when it refers, or before changing itself. When it does:

- **The handler sees** the decision, the amount, the calculation and the reason, with the section of the wording.
- **The handler can** sign off, reject, or change the amount, with a note.
- **The record holds** who decided, when, and what they were shown (manual section 14).
- **If nobody answers**, the claim waits, the owner is told after two working days, and it is never paid twice.

## The lethal trifecta

An agent is open to attack when it has all three of:

1. **Private data**: yes. Customer records and medical details.
2. **Untrusted content**: yes. The customer writes the claim story and supplies the documents.
3. **A way to send data out**: not in the pilot. The agent writes only to the claims system.

With two of the three, the agent can be made to decide wrongly, but not to leak data. That is why `data/security/` holds CLM-1901, a claim whose story tells the AI the claim was pre-approved. The agent must decline it like any other unattended loss.

**The risk to watch:** use case 2, chasing documents, would let the agent write to customers. That completes the trifecta: a story could tell the agent to send another customer's details in a letter. It goes ahead only with a fresh review, and letters checked in code before they go.

## Guardrails

Three layers keep a payout within the rules:

1. **The agent**: its instructions, and a check on what goes in and what comes out.
2. **A gateway between the agent and the systems**: only the tools it needs, and a policy that refuses any payment over $1,000.
3. **The claims system**: an API key for the agent, and the same $1,000 limit checked again.

## Privacy

- **The model provider is a third party**, like any other supplier holding customer data. UnderCover's standard supplier review applies: a business API with no training on its data, security certification, and where the data is processed.
- **Send only what the decision needs.** The claim, the policy and the claim history, never the date of birth, address or contact details (manual section 11).
- **The data stays in UnderCover's account**, as agreed in `04_data_requests.md`.

The information security officer accepted this for R&D, with the supplier review to be finished before development.

## Responsible AI

| Pillar | How it is covered |
|---|---|
| Safety | Payments capped in code; refer when unsure |
| Fairness and bias | The agent sees no age, address or name; decisions checked across claim types in the evals |
| Security | The trifecta review, the security case and the three layers above |
| Privacy | As above |
| Transparency | Every decision has a reason and a section; every run is traced |
| Accountability | The Head of Claims Operations owns the agent's decisions; a person signs off above the limit |

## What it produced

- The autonomy levels in `claims/docs/SPEC.md`, under Rules.
- The security case in `data/security/`.
- Two conditions for later phases: a supplier review before development, and a fresh trifecta review before the agent writes to anyone.
