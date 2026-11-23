#!/usr/bin/env bash
# Flags what docs/AI_SMELL.md bans. Em dashes and emoji fail everywhere;
# banned words fail in website copy (any */web/ app) and only warn elsewhere.
set -euo pipefail
export LC_ALL=C.UTF-8
cd "$(dirname "$0")/.."

WORDS='\b(delve|leverage|unlock|seamless(ly)?|elevate|empower|harness|game-changer|cutting-edge|revolutionise|transformative|landscape|realm|tapestry|journey|navigate|streamline|supercharge|effortless(ly)?|robust|holistic|synergy)\b'
PHRASES="in today's fast-paced world|let's dive in|look no further|take it to the next level"
MARKS='\x{2014}|[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]'

mapfile -t files < <(git ls-files -co --exclude-standard \
  | grep -E '\.(md|ts|tsx|js|mjs|py|html|css|sh|json|ya?ml|toml|txt)$' \
  | grep -vE '(^|/)(pnpm-lock\.yaml|uv\.lock|package-lock\.json)$|^docs/AI_SMELL\.md$|^scripts/smell\.sh$|(^|/)node_modules/')
mapfile -t web < <(printf '%s\n' "${files[@]}" | grep -E '^[^/]+/web/' || true)
mapfile -t rest < <(printf '%s\n' "${files[@]}" | grep -vE '^[^/]+/web/' || true)

failed=0
if grep -nP "$MARKS" "${files[@]}"; then
  echo "AI smell: em dashes or emoji above. Rewrite without them." >&2
  failed=1
fi
if [ ${#web[@]} -gt 0 ] && grep -niP "$WORDS|$PHRASES" "${web[@]}"; then
  echo "AI smell: banned words in website copy above. See docs/AI_SMELL.md." >&2
  failed=1
fi
if [ ${#rest[@]} -gt 0 ]; then
  warnings=$(grep -ciP "$WORDS|$PHRASES" "${rest[@]}" | grep -v ':0$' || true)
  [ -n "$warnings" ] && echo "AI smell warnings (banned words outside website copy, per file):" && echo "$warnings"
fi
exit $failed
