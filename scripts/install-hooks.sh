#!/usr/bin/env bash
# Installs the pre-commit hook for this clone. Every worktree of the clone shares it.
set -euo pipefail
cd "$(dirname "$0")/.."
hooks="$(git rev-parse --git-common-dir)/hooks"
cp scripts/pre-commit "$hooks/pre-commit"
echo "Installed $hooks/pre-commit"
