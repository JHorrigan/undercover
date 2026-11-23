# Discovery record

**A worked example.** UnderCover is a fictional client, and this record of its discovery is made up. The meetings, quotes and figures here were invented to show how a discovery produces the files in `data/`, `context/` and `docs/DISCOVERY.md`. Where a fact comes from UnderCover's data, the file is named; everything else is invented.

Discovery ran for two weeks, from Monday 9 November to Friday 20 November 2026. It ended with the sponsor agreeing the scope and the budget for the R&D phase.

## How it fitted in two weeks

The steps are numbered in the order they finish, but they overlap:

- **The data request went out at the kickoff**, so exports were being prepared while the interviews ran.
- **Interviews and sitting with the handlers took the first four days**, back to back.
- **A quick test on the sample claims ran on day 5**, as soon as the first data arrived. It showed within a day that a model could decide most routine claims, which made the use-case workshop sharper.
- **One half-day workshop on day 7 covered both the use cases and the autonomy and risk**, with the same people in the room.
- **The baseline used what UnderCover could produce quickly.** The rest is measured in R&D.

## The steps

Each step has a file of its own. Each file says why the step matters, what was asked, what was found, and what it produced.

| Step | File | When | What it produced |
|---|---|---|---|
| 1. Kickoff | `01_kickoff.md` | Day 1 | The sponsor, the owner, the governance, the first data request and the plan for discovery |
| 2. Interviews | `02_interviews.md` | Days 1 to 4 | The problem in the business's own words, and the unwritten rules |
| 3. Process map | `03_process_map.md` | Days 3 to 5 | How a claim is worked today, step by step |
| 4. Data requests | `04_data_requests.md` | Days 1 to 8 | Every file in `data/` and `context/`, with its source and owner |
| 5. Baseline | `05_baseline.md` | Days 3 to 7 | How the work performs today, in figures |
| 6. Use cases | `06_use_cases.md` | Days 5 to 7 | A quick test on the sample, the ranked use cases, and why deciding claims came first |
| 7. Evals | `07_evals.md` | Days 4 to 9 | The handlers' decisions in `data/evals/claims/`, the cost of mistakes and the metrics |
| 8. Autonomy and risk | `08_autonomy_and_risk.md` | Day 7 | What the agent may do alone, with approval, and never |
| 9. Business case | `09_business_case.md` | Days 9 and 10 | The success criteria, the cost per claim, and the sign-off |

## The two weeks

| Day | Date | What happened |
|---|---|---|
| 1 | Mon 9 Nov | Kickoff and first data request; the owner's interview |
| 2 | Tue 10 Nov | Interviews with the handlers and finance; the claims manual and the harder claims requested |
| 3 | Wed 11 Nov | Sitting with the handlers; the sample claims, policies and plans arrive |
| 4 | Thu 12 Nov | Sitting with the handlers; the customers, the recorded decisions and the data dictionary arrive |
| 5 | Fri 13 Nov | A quick test on the sample claims; playback to the owner; process map checked |
| 6 | Mon 16 Nov | Agreement test begins; the held-out, harder and security claims arrive |
| 7 | Tue 17 Nov | Half-day workshop: use cases, then autonomy and risk; the cost of mistakes agreed with finance |
| 8 | Wed 18 Nov | Reference data arrives; the senior handler reviews the recorded decisions |
| 9 | Thu 19 Nov | Evals finalised; business case written |
| 10 | Fri 20 Nov | Sign-off at the project committee |

## What discovery must end with

From the agent development lifecycle, the discovery phase ends with:

- a sponsor and an accountable owner
- a business case
- evals, a baseline and success criteria
- an adoption plan
- the sponsor's sign-off on scope and budget

`docs/DISCOVERY.md` is the summary of this record, and `claims/docs/SPEC.md` is the spec agreed from it.
