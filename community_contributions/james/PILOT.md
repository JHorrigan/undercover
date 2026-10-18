# Pilot progress

## 1. Reviewing the docs before planning

Before planning the pilot, I read the documents in `docs/` and made small changes to make the build my own. I kept the changes minimal so the spec and the course still line up.

| File | Change | Why |
|---|---|---|
| `docs/BRAND.md` | New palette: Electric Blue, Cyan and Lavender as the three main colors, Mint for information and Coral Red for alerts, with new ink and surface colors. Headings use Archivo, body stays Instrument Sans. | To give the dashboard a distinct look from the reference build. |
| `docs/CODE_STANDARDS.md` | Added two rules: short modules and functions with clear names, and a one-line docstring on every public function. | To keep the code easy to read and review as it grows. |
| `docs/PROCESS.md` | Added a "Fixing bugs" section: reproduce, prove the cause, fix the root cause with a test, and stop after two failed attempts. | To stop the agent guessing or papering over bugs, and to make it say when it's stuck. |

`docs/SPEC.md`, `docs/TECH_STACK.md` and `docs/STATUS.md` are unchanged.

Next step: "Please plan the pilot", which writes `docs/PLAN.md`.
