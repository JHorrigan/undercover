#!/usr/bin/env bash
# Runs every check for every app and stops at the first failure.
# Usage: scripts/check.sh [--fast]   (--fast skips the end-to-end tests)
set -euo pipefail
shopt -s nullglob
cd "$(dirname "$0")/.."

echo "== AI smell"
scripts/smell.sh

for project in */*/pyproject.toml; do
  dir=$(dirname "$project")
  echo "== $dir"
  (cd "$dir" && uv run ruff format --check . && uv run ruff check . && uv run mypy . && uv run pytest -q)
done

for project in */*/package.json; do
  dir=$(dirname "$project")
  echo "== $dir"
  (cd "$dir" && pnpm format:check && pnpm lint && pnpm typecheck && pnpm test)
  if [ "${1:-}" != --fast ]; then
    (cd "$dir" && pnpm e2e)
  fi
done

echo "All checks passed."
