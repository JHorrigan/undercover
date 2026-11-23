# Code standards

1. Keep it simple, do not overcomplicate.
2. Comments only when necessary.
3. Be concise: a short README and no emojis. Nothing reads as AI-made: follow `docs/AI_SMELL.md`.
4. IMPORTANT: avoid overly defensive code. Handle exceptions only when necessary.
5. Use uv: ALWAYS `uv run`, NEVER `python3`.
6. TypeScript: strict mode, never `any`.
7. Short modules and short functions with clear names. Split a function once it does more than one job, and a module once it holds two concerns.
8. Every public function has a one-line docstring saying what it does.

## Structure

9. No hard-coded addresses. A URL, host, port or file path comes from an environment variable with a local default, set in one place, and the same name is used everywhere.
10. One way to reach each service.
11. Keep the layers apart, each in one place:
    - Business rules live in the backend.
    - Every agent tool is a thin call to the backend's API, kept in one tools module per agent.
    - The harness (the model, the middleware, building and running the agents) lives in one module.
    - One concern is not spread over several modules, and one module does not mix two.
12. Use the framework before writing your own. Before writing a loop, a closure, a parser or a wrapper around an agent, check what the installed version of LangChain already provides, and use that.
13. Agent state goes through the agent's context or state, never through closures or globals. A tool takes from the model only what the model has to decide.
14. Fix a type error by typing the code correctly, not by loosening the check. Say why in one line if a cast is the only way.

## Agent instructions

15. Instructions give the agent its goal, what a good result looks like, the rules it must keep and where to find what it needs. They are not step-by-step scripts of which tool to call when. Rules that must always hold are enforced in code, and the instructions only say what they are.
16. Write instructions from the client's own documents, never from `data/evals/`.
