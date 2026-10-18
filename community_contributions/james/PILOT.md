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

Next step: review the plan, then "Please implement the plan for the pilot".
