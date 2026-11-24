# Tech stack

- `backend/`: FastAPI and SQLite. Every API operation has an `operation_id`, a one-line docstring and no optional inputs. Paying a claim is a separate operation that takes the amount.
- `agent/`: LangChain's `create_agent` on OpenRouter, with one entry point that takes a claim id and a thread id. It reaches claims and its instructions only through the backend's API. It uses `openai/gpt-6-luna` with low reasoning effort by default, or the model in the environment variable `MODEL_NAME` if set, such as `openrouter/free`.
- `dashboard/`: React, Vite and TypeScript.
- `e2e/`: Playwright tests.
- `data/`: the business data the backend starts from. The agent never sees `data/evals/`, which holds the answer key.
- `claims/research/`: the R&D notebooks.

Python 3.14 with uv, all in the root `pyproject.toml`. Node 24 or later, with npm. The OpenRouter key is `OPENROUTER_API_KEY` in `.env`.

## Running it

- `uv sync` and `npm install` install everything, including the git pre-commit hook and Playwright's browser.
- `npm run dev` starts the backend and the dashboard.
- `npm run check` runs every check: Ruff, pyright and pytest for Python; Prettier, ESLint, `tsc` and Vitest for TypeScript; Playwright end to end. The checks need no paid service: tests use stub models.
- The pre-commit hook, from `lefthook.yml`, formats the staged files, runs the checks for the part that changed, and runs `scripts/smell.sh`.
