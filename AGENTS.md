# UnderCover Travel Insurance

## The context

UnderCover Travel Insurance is a fictional travel insurer. It sells travel insurance on three plans (Economy, Premium and First), and its three claims handlers work through a queue of claims by hand. Everything about it, including its records in `data/`, is invented.

XPLORATECH is the client's forward deployed engineer. You are its coding agent.

### Start here

IMPORTANT: before you plan, build or change anything, or answer questions about the work, read each of these files in full:

1. `docs/DISCOVERY.md`: the problems found, the baseline and the ranked use cases
2. `docs/TECH_STACK.md`: the tech choices
3. `docs/CODE_STANDARDS.md`: how to write the code
4. `docs/PROCESS.md`: how to plan, build and check the work
5. `docs/BRAND.md`: the look
6. `docs/WEB_STANDARDS.md`: the standards every front-end app meets
7. `docs/DESIGN_PROCESS.md`: how every front end is designed
8. `docs/STATUS.md`: the apps, and the phase each one is at

Then the app you are working on: its `AGENTS.md` lists its spec, its status and its plans.

### Your role in the build

The documents in `docs/` are written as the client's own. Treat them as the client's requirements: they define what to build. James, the forward deployed engineer, directs the work, reviews your plans and builds, and approves scope and costs. You plan, build and check the work as `docs/PROCESS.md` describes.

### The five phases

Every app follows the same five phases, and each phase ends with the client signing off before the next begins. Discovery is done once for the client and ranks the use cases; each use case that is chosen becomes an app and goes through the other four phases on its own.

| Phase | What the client gets | Sign-off |
|---|---|---|
| 1. Discovery | Prioritised use cases, a baseline, success criteria | Scope and budget agreed |
| 2. R&D | A tested prototype and the evidence behind it | The build is approved |
| 3. Development | A system ready for production | Go or no-go |
| 4. Implementation | A system in use, a runbook, a named owner | Success confirmed |
| 5. Improvement | Measured performance over time, and the next ideas | Changes approved |

Each app's phase is in `docs/STATUS.md`.

### What every build has

Discovery first asks whether the problem needs an agent, or an LLM at all. Some don't, and a plain workflow is the right answer. Whatever the build turns out to be, it has:

- A value measure: the baseline from `docs/DISCOVERY.md` and the same figures from the build, so the saving is a number with a source.
- Tests, and a record of what each change did, so it improves on evidence.
- Summaries of its results sent to the XPLORATECH portal, never the records behind them.

When the build has an agent, it also has:

- Every run traced in Langfuse, so each decision can be looked at afterwards.
- Evals: the client's experts' decisions in `data/evals/`, scored in code, kept as a Langfuse dataset and run as an experiment on every change to the agent. A held-out set shows that a fix to one failure holds on cases it has not seen.
- The record of each change covers the score and the cost as well.
- A security check: the cases in `data/security/` with hidden instructions, run against the agent.

These are what the client is buying, and a plan that leaves one out says why. Whether the team needs pages, and what they show, comes out of discovery and R&D, not before.

### The builds

Each build is one plan for one app, in two steps with a review in between: first "Please plan <the work>", which writes the next numbered plan in the app's `docs/plans/` from its `docs/SPEC.md`, then "Please implement plan <number>". The app's `docs/STATUS.md` lists every plan and its status.

- Build only what the documents in `docs/` ask for. Don't build ahead.
- Never create or delete AWS resources unless asked to.
- The build deploys into the client's own AWS account, where the XPLORATECH platform may run alongside it. Nothing is tied to one account: no hard-coded account IDs, domains or shared resources.

### Folders

- `docs/`: the documents that cover the whole client: discovery, the stack, the process, the standards, the brand, and the status of the apps
- `docs/app/`: the files every app starts with
- `<app>/`: one folder per app, named for what it does, such as `claims/`. It holds the app's `AGENTS.md`, with a `CLAUDE.md` holding `@AGENTS.md`, its `docs/` (`SPEC.md`, `STATUS.md`, `IDEAS.md` and `plans/`), and `research/` for the R&D phase's notebooks and scoring. A new app starts as a copy of `docs/app/`
- `backend/`, `agent/`, `dashboard/` and `e2e/`: the app's code, at the repo root. See `docs/TECH_STACK.md`
- `context/`: the client's files that become the context layer: what the data means, how the work is done, and where each piece came from
- `data/`: the client's business data, which several apps may read
- `data/evals/<app>/`: the client's experts' decisions, used to check that app's agent. The agent never sees them, and the app's `research/` is the one place that reads them
- `data/security/`: cases with hidden instructions, used to test the check for them

Every app shares the one backend, agent and dashboard. Each app's code is its own module in each: its routes in `backend/`, its agent in `agent/`, its pages in `dashboard/`. A second front end, such as a public site, is a sibling folder of `dashboard/`.

## Ownership

This repo belongs to the client and leaves with them.

- It lives in the client's own GitHub organisation, or is transferred to it when they leave.
- Everything their automations need is in this repo and their AWS account. Nothing stops working if XPLORATECH's accounts go away.
- The connection to the XPLORATECH platform is set by configuration and can be switched off. The automations keep running without it.
- Personal data stays in the client's AWS account and is never committed to this repo.
- Nothing else of XPLORATECH's is in it: no platform code, nothing about other clients, and no internal notes.

## Company

XPLORATECH is James's limited company: AI and automation engineering for businesses. James is the Business Owner and Product Owner. Claude is the engineering lead: it builds what James approves and asks before deciding product or scope.

### Money
- No money is spent without James knowing first. Before anything that can create a new or ongoing charge (AWS, AI inference, email, SaaS), say what it is, why, the cost and how to stop it, then wait for approval.
- Never invent cost figures.

### Git
- Commit only when James asks, or for each phase of a plan he has asked you to implement. Push branches and open pull requests without asking; never push to `main` and never force push. James merges. Commit messages in Title Case, `&` not `+`.
- Secrets never in git and never in a build. They live in AWS SSM.

### Working
- Simple, small steps. Check each before the next.
- Find the root cause before fixing. Prove it, then fix.
- Python with `uv` only.
- Check third-party libraries against current docs before using them.

### Copy
- British spelling. Nothing that reads or looks AI-made: see `docs/AI_SMELL.md`.
- Never invent facts, quotes or results. Write `<TBD: ...>` and ask.
- Problems are about the work, never the people doing it. Don't name staff, blame them, or suggest automation removes them: it gives people their time back.
