# Pilot progress

## 1. Reviewing the docs before planning

Before planning the pilot, I read the documents in `docs/` and made small changes to make the build my own. I kept the changes minimal so the spec and the course still line up.

| File | Change | Why |
|---|---|---|
| `docs/BRAND.md` | New palette: Electric Blue, Cyan and Lavender as the three main colors, Mint for information and Coral Red for alerts, with new ink and surface colors. Headings use Archivo, body stays Instrument Sans. | To give the dashboard a distinct look from the reference build. |
| `docs/CODE_STANDARDS.md` | Added two rules: short modules and functions with clear names, and a one-line docstring on every public function. | To keep the code easy to read and review as it grows. |
| `docs/PROCESS.md` | Added a "Fixing bugs" section: reproduce, prove the cause, fix the root cause with a test, and stop after two failed attempts. | To stop the agent guessing or papering over bugs, and to make it say when it's stuck. |

`docs/SPEC.md`, `docs/TECH_STACK.md` and `docs/STATUS.md` are unchanged.

## 2. Planning the pilot

Asked the agent to "plan the pilot". It wrote `docs/PLAN.md`: six phases covering backend data, decisions and the $1,000 sign-off rule, the agent, then the dashboard and end-to-end tests. Key choices: the backend enforces the payment limit rather than trusting the agent, the agent reaches data only through the API so it can't see `data/evals/`, and the runner logs the agent's steps for the dashboard.

## 3. Building the pilot

Asked the agent to "implement the plan for the pilot". It built the six phases in order, checked each one's success criteria, and committed after each phase.

- **Backend:** SQLite seeded from `data/`, with a test proving it never reads `data/evals/`. The $1,000 rule lives in the payment operation, so the agent can't pay a big claim without a handler.
- **Agent:** tools that only call the API, and a runner that logs every step for the dashboard.
- **Dashboard:** the queue, the claim page with live steps and sign-off, and the instructions, all in my brand colors.
- **Tests:** 27 Python, 10 dashboard and 4 end-to-end, with no model calls. `npm run check` passes.

Live runs with a real model:

- CLM-1001: approved for $420.00 and paid.
- CLM-1003: approved for $3,750.00. The agent tried to pay and was blocked, and paying it took a handler's sign-off in the dashboard.

Lessons from the build:

- The first live run showed the model guessing ids, so the instructions now tell it to read the claim first.
- Raw tool results made the steps hard to read, so they're cut to two lines.
