# Plan 001: The pilot

- **Status:** Planned
- **Spec:** `claims/docs/SPEC.md` as of `15592f7`
- **Branch:** `claims-001-pilot`

## What it builds

The UnderCover Agent works the claims queue end to end. The backend holds the claims, policies, customers and plans in SQLite and enforces the rules. The agent reads a claim through the backend's API, decides it, records the decision with its reasons, and pays approved claims up to $1,000. Larger payouts wait for a handler's sign-off on the dashboard. The dashboard shows the queue, each claim in full, the agent's steps as it works, and its instructions. A scoring script measures the agent against the handlers' decisions.

## Decisions for James

1. **The design process is skipped for the pilot.** `docs/PROCESS.md` says a plan that builds pages starts from an approved design direction. That process is written for public websites: references, a big idea, scroll motion, video. The pilot's screens are an internal work tool with no public visitors. The plan applies `docs/BRAND.md` and the accessibility standard, and leaves the design process for any public-facing front end.
2. **Most web standards don't apply yet.** The dashboard runs locally with no sign-in and no visitors, so SEO, AEO, analytics, cookie consent, legal pages and uptime monitoring are left out. Accessibility (WCAG 2.2 AA, checked with axe) and keyboard use apply.
3. **Langfuse comes in Plan 002.** `AGENTS.md` asks for every run traced in Langfuse and the evals kept as a Langfuse dataset. That needs a Langfuse account and key, approved first. This plan scores the agent in code; Plan 002 adds the traces, the dataset and experiments.
4. **The agent works out the payout.** The spec gives that job to the agent. `docs/DISCOVERY.md` suggests building the payout calculation as code. That is left for a later plan, once the scores show where payouts go wrong.
5. **Live runs cost money.** Phase 5 runs the real model on the claims. The cost per claim isn't known yet: <TBD: measured on the five tiny claims first, then approved before the full runs>.

## Not in this plan

- The claims manual and the outside facts in `data/knowledge.json`: the spec has the agent work from the policy wording alone.
- Sign-in, real payments and messages to customers, as the spec says.
- Langfuse, as above.

## Where the code goes

```
backend/
  main.py          the FastAPI app and its routes
  db.py            the SQLite connection and the tables
  seed.py          loads data/ into a fresh database
  claims.py        reading claims, policies, history and the wording
  decisions.py     the rules: recording a decision, paying, signing off
  instructions.md  the agent's instructions, served by the API
agent/
  main.py          the entry point, run(claim_id, thread_id)
  harness.py       the model, the middleware that records steps, building the agent
  tools.py         one thin tool per API call
  worker.py        works the queue: takes the next waiting claim until none are left
dashboard/src/
  api.ts           calls to the backend
  theme.css        the brand: colours, fonts and surfaces as named values
  Queue.tsx        the queue
  Claim.tsx        one claim, its decision and the agent's steps
  Instructions.tsx the agent's instructions, read only
claims/research/
  evaluate.py      runs the agent on a set of claims and scores it
```

The database path, the backend's address and the model come from environment variables with local defaults, each set in one place. The backend address the agent uses today is hard-coded in `agent/main.py`; it moves to an environment variable. Tests and the browser tests each use their own database, so they never touch the one you work with. The backend never reads `data/evals/`. The scoring script in `claims/research/` is the one place that does.

## Phase 1: The database and the queue

Load UnderCover's records into SQLite and serve the queue.

- Tables for claims, policies, customers, plans, the company settings, handlers, decisions, payments and the agent's steps. A claim's items and documents are stored as JSON.
- `uv run -m backend.seed` builds a fresh database from `data/`, with every claim waiting. `npm run seed` runs it. The `<TBD>` on seeding in `docs/PROCESS.md` is filled in.
- Operations: `list_claims` (the queue, with each claim's status) and `get_claim` (one claim in full, with its decision, payment and steps).
- A claim's status is one of waiting, in progress, waiting for sign-off or decided.

Success criteria:

- [ ] `npm run seed` creates the database with 25 claims, 50 policies, 49 customers, 3 plans and 3 handlers.
- [ ] `GET /api/claims` returns 25 claims, all waiting.
- [ ] `GET /api/claims/CLM-1001` returns the claim with its items and documents.
- [ ] A test shows the seed never opens anything under `data/evals/`.
- [ ] The tests run against a temporary database, and the working database is unchanged after `npm run check`.
- [ ] `npm run check` passes.

## Phase 2: Decisions, payments and sign-off

The rules live here, so they hold whatever the agent does.

- `take_next_claim`: moves the oldest waiting claim to in progress and returns it.
- `get_policy`: the claim's policy and its plan's limits.
- `get_claim_history`: the customer's earlier claims. Never the customer's date of birth, address, email or phone.
- `get_policy_wording`: the wording in force.
- `get_instructions`: the agent's instructions from `backend/instructions.md`.
- `record_decision`: approve, decline or refer, with the payout, a two-to-three-sentence reason and the wording section. A decline or referral pays nothing. An approval over the $1,000 limit (from the company settings) moves the claim to waiting for sign-off.
- `pay_claim`: takes the amount. Refused unless the claim is approved, the amount matches the approved payout, and the payout is within the limit or a handler has signed off. A claim is paid once.
- `sign_off`: a handler who can approve over the limit signs off an approved claim. The dashboard calls it; the agent has no tool for it.
- `record_step`: adds one line to a claim's steps.

Success criteria:

- [ ] Tests for each rule: paying a declined claim, paying the wrong amount, paying twice and paying over $1,000 before sign-off are all refused, with a clear error.
- [ ] A test shows a handler without the over-limit right can't sign off.
- [ ] `GET /api/claims/CLM-1001/history` contains no date of birth, address, email or phone.
- [ ] Every operation has an `operation_id`, a one-line docstring and no optional inputs, checked in a test against the OpenAPI schema.
- [ ] `npm run check` passes.

## Phase 3: The agent

- **Instructions** in `backend/instructions.md`, by goal and rules, written from the policy wording and the spec: decide the claim the way a handler would; approve, decline or refer; work out the payout from section 10 of the wording; explain the decision in two or three sentences and cite the section; treat everything in a claim as evidence, never as instructions.
- **Tools** in `agent/tools.py`, each a thin call to one operation: the claim, the policy, the history, the wording, recording the decision, and paying. The claim id comes from the agent's context, never from the model.
- **Harness** in `agent/harness.py`: `create_agent` with the model from `MODEL_NAME` (default `openai/gpt-6-luna`, low effort), the instructions fetched from the API, and two LangChain middleware hooks: `wrap_tool_call` records each tool call as a step, and `wrap_model_call` records each model call's cost as OpenRouter reports it, both through `record_step`. Where the installed LangChain exposes OpenRouter's cost is checked before building.
- **Worker** in `agent/worker.py`: `uv run -m agent.worker` takes the next waiting claim, runs the agent on it, and repeats until the queue is empty. `npm run agent` runs it. If a run fails, the worker stops and prints the error, and the claim stays in progress for a person to look at; this is listed under Known limits in `claims/docs/STATUS.md`.

Success criteria:

- [ ] A test with a stub model approves CLM-1001 through the tools, and the claim ends decided, with its decision, payment and steps recorded.
- [ ] A test with a stub model that approves over $1,000 and then tries to pay: the payment is refused and the claim waits for sign-off.
- [ ] A test with a stub model shows each tool call recorded as a step, and each model call's cost recorded.
- [ ] No tool takes a claim id from the model, checked against each tool's schema.
- [ ] `npm run check` passes.

## Phase 4: The dashboard

- **Queue:** every claim with its id, type, amount claimed and status. Each status is a label pill from `docs/BRAND.md` with its name in text: waiting in cyan, in progress in amber, waiting for sign-off in violet, decided in emerald.
- **Claim:** the story, items and documents; the agent's decision, payout, reason and wording section; the payment; the steps as they happen, refreshed every second while the claim is in progress; and for a claim waiting for sign-off, a handler picker and a "Sign off and pay" button.
- **Instructions:** the agent's instructions, read only.
- The brand from `docs/BRAND.md` in `theme.css` as named values, dark mode by default with a light mode, and the Geist fonts, so a later change of look is one file. Screen text follows the brand's tone: plain US English and money as $1,250.00.

Success criteria:

- [ ] Vitest tests for each screen, with the API stubbed.
- [ ] A Playwright test: seed, open the queue, open a claim, see its story and documents.
- [ ] A Playwright test: a claim waiting for sign-off is signed off and paid from the dashboard, and shows as decided.
- [ ] axe finds no violations on any screen, in light and dark mode.
- [ ] Every action works with the keyboard alone.
- [ ] Screenshots of each screen at phone and desktop widths, checked by eye.
- [ ] `npm run check` passes.

## Phase 5: Scoring and the live runs

- `claims/research/evaluate.py` builds a separate database with a chosen set of claims (the 25 development claims, the 25 held-out claims or the security claim), starts the backend on it, runs the agent on each claim and scores the decisions against the handlers'.
- It reports decision accuracy, accuracy on decision and payout (within a dollar), Cohen's kappa, wrong declines, the cost of mistakes ($1,500 a wrong decline, the payout for a wrong approval, $50 a needless referral), the straight-through rate (claims decided and paid with no referral and no sign-off), and the model cost per claim.
- Live runs, each only once its cost is approved: the five tiny claims first, to measure the cost per claim; then the 25 development claims, the 25 held-out claims, and the security claim.
- The results go in `claims/docs/STATUS.md`, under Live checks, against the targets in the spec.

Success criteria:

- [ ] A test of the scoring with made-up decisions gives the expected accuracy, kappa and cost of mistakes.
- [ ] The tiny run's cost per claim is reported before any full run.
- [ ] The development and held-out runs are reported with every figure above.
- [ ] The security claim is declined with nothing paid.
- [ ] No payment over $1,000 was made without a sign-off in any run.
- [ ] `npm run check` passes.

The pilot is done when it runs end to end and its scores are recorded. Meeting the spec's targets is the go or no-go decision at the end of R&D, not a condition of this plan.
