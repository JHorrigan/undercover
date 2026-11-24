# Process

## Install

Once per machine: install `uv` and Node.js 24 or later.

Once per clone: `uv sync` and `npm install` at the repo root install everything, including the pre-commit hook and Playwright's browser. `npm run dev` starts the backend and the dashboard. <TBD: how to seed the product, chosen with the database.>

## Checks

`scripts/check.sh` runs every check: the AI smell check, then `npm run check`, which runs Ruff, pyright and pytest for Python, Prettier, ESLint, `tsc` and Vitest for TypeScript, and Playwright end to end. It stops at the first failure. The checks need no paid service: tests use stub models and stand-ins.

The pre-commit hook, from `lefthook.yml`, formats the staged files, runs the Python or TypeScript checks for the part that changed, and runs the AI smell check.

CI runs `scripts/check.sh` on every pull request and every push to `main` (`.github/workflows/check.yml`). Report a pull request as passing only once its checks are green on GitHub.

## Specs & ideas

Each app keeps its own `SPEC.md`, `IDEAS.md`, `STATUS.md` and `plans/` in its `docs/` folder, such as `site/docs/`.

- `SPEC.md` says what the product must do and why, never how. There is one living spec: when something changes, edit it in place, and git keeps the history.
- A new idea goes in `IDEAS.md` as a few lines on what it is and why. Writing it down commits to nothing, and it never interrupts the build in progress.
- When an idea is chosen, ask questions until it is clear, then add it to `SPEC.md` and remove it from `IDEAS.md`. Write `<TBD: ...>` for anything not known and never invent it. The change is approved before it is committed.
- A spec change may take several plans. Each plan is one slice that can be built and shipped on its own.

## Planning

When asked to plan, as in "Please plan lead search", write each slice's plan to its own numbered file in `plans/`, such as `site/docs/plans/002-lead-search.md`, and write no code.

- Start each plan with its status (Planned, In progress or Done), the commit that added its work to `SPEC.md`, and its branch.
- A plan that builds pages starts from the app's approved `docs/design/DIRECTION.md`. If there is none, the design process in `docs/DESIGN_PROCESS.md` comes first.
- Add each plan to the Plans table in `STATUS.md` as Planned.

- Split the work into phases, usually 5 or 6, each building on the last.
- Say where the new code goes: which modules, and what each is for. Check that layout against `docs/CODE_STANDARDS.md`, and check what the framework already provides before planning code of your own.
- Describe agent instructions by their goal and rules, never as a script of steps.
- Give each phase detailed success criteria that you can verify yourself: tests that pass, commands and their output, API calls and their responses, and pages you check in the browser. Write each one as a checkbox.
- Then stop and wait until you are asked to implement the plan.

## Implementing

When asked to implement a plan, set its status to In progress, then build every phase in order without stopping. For each phase:

1. Build it, with tests.
2. Check every success criterion and fix whatever fails.
3. Review the phase's code before you commit it, as a reviewer who did not write it would: run the `reviewer` agent in `.claude/agents/` on the diff. It checks the whole diff, not just the tests' results, against every point in `docs/CODE_STANDARDS.md` and `docs/AI_SMELL.md`. Fix what fails.
4. Tick off its criteria in the plan, and update `STATUS.md`, including the plan's row in the Plans table.
5. Commit, naming the plan and phase, such as `Add Lead Search Filters (Plan 002, Phase 3)`. The pre-commit hook runs the checks; if it fails, fix the problem and commit again.

When the last phase is done, review the whole build the same way, then run every check and report the results, including what the review found and fixed. Then set the plan's status to Done, in the plan and in `STATUS.md`.

When a build extends earlier code, the earlier code meets the standards too. Fix a shortcut you find rather than building on it.

## Fixing bugs

When something fails, find the root cause before you change any code:

1. Reproduce it with a failing test or a command, and note the exact error.
2. Prove the cause with evidence, such as a log line, a value or a stack trace. Don't guess.
3. Fix the cause, not the symptom. No workarounds, retries or broad exception handlers to hide it.
4. Check the failing test now passes, run every check, and commit the test with the fix.
5. If you can't prove the cause after two attempts, stop and report what you tried.

## Working in parallel

- One job, one worktree. Start each session from the repo root with `claude --worktree <app>-<plan>`, such as `claude --worktree site-002-lead-search`.
- Each worktree starts from `main` on GitHub, on its own branch, and gets a copy of the `.env` files listed in `.worktreeinclude`.
- Keep the main checkout clean. Code changes happen only in a worktree.
- When the work is done, push the worktree's branch and open a pull request into `main`. James merges it without squashing, so each phase's commit stays in the history. A session inside a worktree doesn't merge.

## Rules

- Add tests with each change. Tests never call a model; use a stub model.
- Run every check before you hand work over.
- A green check is necessary but not enough: work is done only once it has passed the review against `docs/CODE_STANDARDS.md`.
- Live runs with the real model only as the plan names them. Report what each live run spent.
- Never use `git commit --no-verify`.
- Never lower a threshold, turn off a rule or exclude a file to get a green run. If a rule looks wrong, stop and ask.
- Keep `docs/STATUS.md` up to date.
- Push branches and open pull requests; never push to `main`, and never force push. The guard in `.claude/hooks/guard.sh` blocks both.
- Don't open `data/evals/` unless you're asked to.
