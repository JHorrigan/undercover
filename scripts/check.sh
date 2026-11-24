#!/usr/bin/env bash
# Runs every check and stops at the first failure.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== AI smell"
scripts/smell.sh

echo "== app"
npm run check

echo "All checks passed."
