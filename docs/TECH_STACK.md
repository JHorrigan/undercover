# Tech stack

- `backend/`: FastAPI and SQLite. Every API operation has an `operation_id`, a one-line docstring and no optional inputs. Paying a claim is a separate operation that takes the amount. The backend enforces a run's cap, retries and the missed-claims check.
- `agent/`: two LangChain `create_agent` agents on OpenRouter, with no other agent framework. The queue agent (`run_queue(cap)`) plans a run, keeps its to-do list and hands each claim to the claim agent (`run_one(claim_id)` for one named claim), which works it from a clean thread and reports back in a line. Both reach claims, documents and their instructions only through the backend's API. LangChain middleware retries model errors (`ModelRetryMiddleware`) and caps the queue agent's model calls (`ModelCallLimitMiddleware`). They use `deepseek/deepseek-v4.1-flash` with low reasoning effort by default, or the model in the environment variable `MODEL_NAME` if set, such as `openrouter/free`.
- `dashboard/`: React, Vite and TypeScript.
- `e2e/`: Playwright tests.
- `data/`: the business data the backend starts from. The agent never sees `data/evals/`, which holds the answer key.

Python 3.12 with uv, all in the root `pyproject.toml`. Node 26. The OpenRouter key is `OPENROUTER_API_KEY` in `.env`.
