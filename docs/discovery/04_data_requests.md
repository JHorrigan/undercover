# 4. Data requests

**A worked example.** The requests and dates below are invented; the files they produced are real. See `README.md`.

9 to 18 November 2026.

## Why this step

The agent can only be as good as what it reads, and it can only be checked against what the experts decided. A data request asks for three kinds of data:

- **The work**: what a handler sees for each claim, exactly as they see it.
- **The rules and context**: what the data means, how the work is done, and what is allowed.
- **The answers**: what the experts decided on past claims, and why. These become the evals, and they are the most important request of all.

Each request names the system, the owner and the format, so the data can be traced back to where it came from. Ask for a sample first, not everything.

## Before anything was sent

On 10 November, before any data was sent, the Head of IT and the Data Governance Lead agreed how data would be handled during discovery and R&D:

- Customer names, contact details, dates of birth and addresses are replaced with realistic invented ones before export. Claim stories and medical details are kept, because the decisions depend on them.
- The data stays in UnderCover's own AWS account and the repo it owns. Nothing is copied anywhere else.
- Section 11 of the claims manual applies: a customer's data is used only to decide that customer's claims.

## The requests

| # | Asked for | Asked | From | Owner | Arrived | Became |
|---|---|---|---|---|---|---|
| 1 | 25 claims from the summer peak, June to September, exported as they first arrived, before any decision, with stories, items and documents as text | 9 Nov | Claims system | Head of Claims Operations | 11 Nov | `data/claims.json` |
| 2 | The policy behind each of those claims, and 25 more | 9 Nov | Policy administration | Product | 11 Nov | `data/policies.json` |
| 3 | Each customer on those policies, with their claim history | 9 Nov | Customer system | Head of Claims Operations | 12 Nov | `data/customers.json` |
| 4 | The plans and add-ons with their limits | 9 Nov | Policy administration | Product | 11 Nov | `data/plans.json`, `context/plans.yaml` |
| 5 | The company settings: the sign-off limit, the filing window and the other numbers | 9 Nov | Claims operations | Head of Claims Operations | 11 Nov | `data/company.json`, `context/claim_rules.yaml` |
| 6 | The handlers and who can sign off | 9 Nov | Claims operations | Head of Claims Operations | 11 Nov | `data/handlers.json` |
| 7 | The policy wording in force | 9 Nov | Published policy documents | Legal | 10 Nov | `data/policy_wording.md`, `context/policy_wording.md` |
| 8 | The customer-facing summary of the wording | 9 Nov | Published policy documents | Legal | 10 Nov | `data/policy_wording_short.md` |
| 9 | The claims manual | 10 Nov | Claims operations | Head of Claims Operations | 10 Nov | `data/claims_manual.md`, `context/claims_manual.md` |
| 10 | The data catalog entries for each field above | 10 Nov | The data catalog | Data Governance Lead | 12 Nov | `context/data_dictionary.yaml` |
| 11 | The wording's defined terms | 10 Nov | Published policy documents | Legal | 12 Nov | `context/glossary.yaml` |
| 12 | The outside facts handlers look up: storm warnings, strikes, where adventure sports happen, product prices | 10 Nov | Outside data providers | Head of Claims Operations | 18 Nov | `context/reference_data.yaml`, `data/knowledge.json` |
| 13 | The decisions the handlers recorded on those 25 claims, with the payout, the working and the reason | 10 Nov | Claims system | Head of Claims Operations | 12 Nov | `data/evals/claims/decisions.json` |
| 14 | 25 more claims from the same months and of the same mix, with their decisions, kept back for testing | 10 Nov | Claims system | Head of Claims Operations | 16 Nov | `data/evals/claims/held_out_*.json` |
| 15 | Harder claims: ones that took longest or were disputed | 10 Nov | Claims system and the handlers | Head of Claims Operations | 16 Nov | `data/evals/claims/harder/`, `even_harder/` |
| 16 | Any claim where someone tried to game the process | 10 Nov | Special Investigations Unit | Head of Claims Operations | 16 Nov | `data/security/` |

How the decisions in requests 13 to 16 were gathered is in `07_evals.md`.

## What came up

- **The manual was not on the first list.** It was added after the interviews (request 9). Ask the people doing the work what they read, not just what is official.
- **The policies came with 25 more than asked.** Product sent every policy for the customers in the sample. They are kept, because claim history and other policies matter.
- **The wording and the manual are versioned.** Wording 2026.1 and manual 2026.2 are recorded in `data/company.json`. A claim is decided under the wording in force when the policy was bought (manual section 13).
- **Outside facts were the slowest.** Handlers look them up on the web case by case. Claims operations keeps a list of the ones that come up most, last reviewed on 30 September, and added the facts the sample needed.
- **Each context file names its source, owner and review date**, so anyone can check where a fact came from and when it was last confirmed.

## Enterprise data questions

| Question | Answer for UnderCover |
|---|---|
| Where does each record live? | Claims in the claims system, policies and plans in policy administration, customers in the customer system, the wording and manual in published documents. |
| What may the agent change? | Only a decision on a claim, and a payment up to $1,000. Both are checked by the system that records them. |
| Where may the data go? | Inside UnderCover's own account only, under manual section 11. |
| Whose access does it use? | Its own, with a role and key of its own, never a handler's login. |

## What it produced

- Every file in `data/` and `context/`, each traced to a request, a system and an owner.
- The data handling agreement above.
- The first answers for the evals, which `07_evals.md` builds on.
