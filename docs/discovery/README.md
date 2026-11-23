# Discovery record

**A worked example.** UnderCover is a fictional client, and this record of its discovery is made up. The meetings, quotes and figures here were invented to show how a discovery produces the files in `data/`, `context/` and `docs/DISCOVERY.md`. Where a fact comes from UnderCover's data, the file is named; everything else is invented.

Discovery ran for four weeks, from 7 September to 2 October 2026. It ended with the sponsor agreeing the scope and the budget for the R&D phase.

## The steps

Each step has a file of its own. Each file says why the step matters, what was asked, what was found, and what it produced.

| Step | File | When | What it produced |
|---|---|---|---|
| 1. Kickoff | `01_kickoff.md` | Week 1 | The sponsor, the owner, the governance and the plan for discovery |
| 2. Interviews | `02_interviews.md` | Weeks 1 and 2 | The problem in the business's own words, and the unwritten rules |
| 3. Process map | `03_process_map.md` | Week 2 | How a claim is worked today, step by step |
| 4. Data requests | `04_data_requests.md` | Weeks 2 and 3 | Every file in `data/` and `context/`, with its source and owner |
| 5. Baseline | `05_baseline.md` | Week 3 | How the work performs today, in figures |
| 6. Use cases | `06_use_cases.md` | Week 3 | The ranked use cases, and why deciding claims came first |
| 7. Evals | `07_evals.md` | Weeks 3 and 4 | The handlers' decisions in `data/evals/claims/`, the cost of mistakes and the metrics |
| 8. Autonomy and risk | `08_autonomy_and_risk.md` | Week 4 | What the agent may do alone, with approval, and never |
| 9. Business case | `09_business_case.md` | Week 4 | The success criteria, the cost per claim, and the sign-off |

## What discovery must end with

From the agent development lifecycle, the discovery phase ends with:

- a sponsor and an accountable owner
- a business case
- evals, a baseline and success criteria
- an adoption plan
- the sponsor's sign-off on scope and budget

`docs/DISCOVERY.md` is the summary of this record, and `claims/docs/SPEC.md` is the spec agreed from it.
