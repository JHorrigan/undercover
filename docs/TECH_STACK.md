# Tech stack

Today's stack, the same in every repo, chosen for now and reviewed as the field moves.

## Front end

- Next.js with React and TypeScript.
- Tailwind CSS for styling.
- pnpm for packages.

## Back end

- Python, managed with `uv`.
- APIs run on AWS Lambda behind API Gateway, built with FastAPI.
- LangChain and LangGraph for agents and long-running, durable workflows.
- Langfuse for traces, datasets, experiments and scores, on Langfuse Cloud in the EU with one project per client. It moves to a self-hosted Langfuse, or into a client's own account, only if a client needs that.

## Sign-in

- Amazon Cognito, on the Essentials tier, for sign-in. API Gateway checks Cognito tokens before a request reaches the API.

## Data

- Postgres with the pgvector extension, for records, vectors, full-text search and key-value data alike. App code connects with a standard connection string, so it doesn't depend on where the database is hosted.
- Code reaches it through SQLAlchemy (async) with asyncpg, writing plain SQL rather than mapping tables to classes. Schema changes are numbered SQL files in each API's `migrations/`, such as `001_initial.sql`, applied in order by a small migrate script.
- Each project chooses where its database is hosted when it starts, checks current prices with the owner first, and records the choice here:
  - **Amazon RDS for PostgreSQL:** runs in the project's own AWS account, created by SST. A fixed hourly price, busy or idle. Lambdas reach it through the project's VPC, which may need a NAT gateway: price that too. Best when the data must stay in the client's account, or traffic is steady.
  - **Neon:** hosted by Neon. Pay for use with no monthly minimum; it scales to zero when idle and can branch the database for each pull request. Best for quiet apps and cheap starts.
  - **Supabase:** hosted by Supabase. A free plan that pauses after a week idle, then a fixed monthly plan, with a dashboard for browsing data. Best for cheap starts.
- For Neon and Supabase, the connection string is set with `sst secret`.
- This project's database: <TBD: RDS, Neon or Supabase.>

## AWS

- Everything is hosted on and deployed to AWS.
- The build runs in the region the client chooses: <TBD: region>. XPLORATECH's own default is eu-west-2 (London). Nothing hard-codes a region.
- Serverless first: Lambda, API Gateway, EventBridge, Step Functions and other serverless services as the work needs them.
- Amazon Bedrock AgentCore for hosting agents, the gateway, policy and memory.

## Deployment

- SST deploys everything: the Next.js apps, the Python Lambdas, the other AWS services and AgentCore. One tool, not SAM or CDK alongside it.
- Where SST can't reach, such as some agent resources, use the AWS CLI or boto3.
- Each app is its own SST app, in `<app>/sst.config.ts`, named `<project>-<app>`, with SST pinned in `<app>/package.json`. It names no account and no region: both come from the credentials the deploy runs with. A domain comes only from a setting, and only on production.
- The production stage is protected and keeps its resources on removal; every other stage is removed clean. Every stage but production is hidden from search, as `docs/WEB_STANDARDS.md` says.

## Local development

- `uv sync` and `pnpm install` set up the dependencies.
- `sst dev` runs the app: it deploys it to a personal stage in AWS, runs the Lambda functions on this machine, and starts the Next.js dev servers locally with the linked resources loaded.
- Each developer, and each worktree, has its own stage, such as `sst dev --stage james-site-header`, so parallel sessions don't overwrite each other. `sst dev` is never pointed at a shared stage.
- Settings come from `.env` and `.env.local`. A deployed stage reads `.env.<stage>` instead, such as `.env.dev`, which SST loads; these files are git-ignored and hold settings only. Secrets are set with `sst secret`, which keeps them in AWS.
- Tests need no AWS and no paid service: they use stub models and stand-ins.
- Postgres with pgvector runs locally in Docker, from the `pgvector/pgvector` image. Its Postgres version matches the hosted database, chosen with it.

## Testing

- Python: pytest for tests, Ruff for linting and formatting, mypy in strict mode for types.
- Next.js: Vitest with React Testing Library for unit and component tests, ESLint and Prettier for linting and formatting, `tsc --noEmit` for types.
- Playwright for end-to-end tests in the browser.
- Langfuse datasets and experiments for agent quality. Unit tests use stub models.
- One check command runs them all. The pre-commit hook runs the fast checks; CI runs everything.

## CI/CD

`.github/workflows/check.yml` runs `scripts/check.sh` on every pull request and every push to `main`, then deploys.

- GitHub Actions, on the plan's included allowance. With no payment method on file, Actions stops when the allowance runs out rather than charging.
- Every pull request runs every check, and is merged only when they all pass. GitHub Free can't enforce this on a private repo, so James checks the pull request is green before merging.
- A pull request deploys the dev stage once its checks pass, so James looks at dev before merging. Merging is the approval: a merge to `main` deploys production once its checks pass, with no step in between. Nothing is merged that can't go live.
- Each app deploys on its own: two jobs per app in `check.yml`, dev and production, both calling `deploy.yml`, which skips unless that app's folder changed, or a folder named with it such as the shared brand. A change only to the app's `docs/` doesn't deploy. The example at the end of `check.yml` is copied for each app.
- Actions signs in to AWS with a short-lived role (OIDC) per stage, made in the stage's account by `scripts/github-deploy-role.sh <stage>`. The dev role trusts only this repo's pull requests; the production role only its `main` branch. No AWS keys are stored in GitHub: the role and region are repository variables, set by the script, and each stage's settings are one more variable, `<APP>_SETTINGS_<STAGE>`, in `.env` form. A deploy job runs only once its role variable exists, so a stage goes live when James makes its role.

## Workflow automation

- n8n is available for simple workflow automation, but it is the last choice. Use the stack above first, and use n8n only when James agrees.

## Folders

Each app is its own folder with only the folders it needs: `research/` for R&D, `agent/`, `api/` and `web/`. <TBD: the apps and what each is built with.>
