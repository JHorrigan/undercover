# UnderCover Travel Insurance

An AI agent that decides travel insurance claims the way a claims handler does: it approves, declines or refers each claim, works out the payout, and explains the decision against the policy wording.

UnderCover is a fictional insurer. Its claims, policies, customers and handlers' decisions in `data/` are all invented.

## What's here

- `backend/`: the API, in FastAPI
- `agent/`: the claims agent, in LangChain
- `dashboard/`: the screens, in React and TypeScript
- `e2e/`: browser tests, in Playwright
- `data/`: the claims, policies, customers and the handlers' decisions used to score the agent
- `claims/research/`: notebooks comparing models on the claims
- `docs/`: how the work was scoped, the baseline and the success criteria

## Run it

You need `uv` and Node.js 24 or later, and an OpenRouter key as `OPENROUTER_API_KEY` in `.env`.

```
uv sync
npm install
npm run dev
```

`npm run check` runs every check and test.
