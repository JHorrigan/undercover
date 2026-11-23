#!/usr/bin/env bash
# PreToolUse guard for Bash commands. Blocks commits that skip the checks, force
# pushes and pushes to main; asks before git and GitHub changes that lose work,
# deploys, AWS changes and destructive database commands. Command checks ignore
# quoted text and look at each command in a chain on its own line, so quoting a
# rule or grepping for SQL is safe. A push's arguments keep their quoted text.
# A push with no branch named counts as a push to main when the session's
# folder is on main; a cd or git -C earlier in the command is not followed.

input=$(cat)
cmd=$(jq -r '.tool_input.command // empty' <<<"$input")
cwd=$(jq -r '.cwd // empty' <<<"$input")
bare=$(sed -E "s/\"[^\"]*\"//g; s/'[^']*'//g" <<<"$cmd" | tr ';&|' '\n\n\n')
flat=$(tr '\n' ' ' <<<"$cmd")

decide() {
  jq -n --arg d "$1" --arg r "$2" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: $d, permissionDecisionReason: $r}}'
  exit 0
}

has() { grep -qE "$1" <<<"$bare"; }

aws_read='\baws\s+(--version|((--\S+\s+\S+)\s+)*(sts|sso|configure|help|\S+\s+(describe-\S*|get-\S*|list-\S*|ls|tail|filter-\S*|wait|help)))(\s|$)'
sql='\bdrop\s+(table|database|schema|index|view|function|role|owned|extension)\b|\btruncate\b|\bdelete\s+from\b|\balter\s+table\b.*\bdrop\b|\bupdate\s+\S+\s+set\b'

if has '\bgit\b.*\bcommit\b.*(--no-verify|\s-[a-zA-Z]*n[a-zA-Z]*(\s|$))|core\.hooksPath|\bHUSKY=0\b'; then
  decide deny "Commits must run the checks. Never skip them."
fi
check_push() {
  if grep -qE '(^|\s)(--force\S*|-[a-zA-Z]*f[a-zA-Z]*|\+\S+|--all|--mirror)(\s|$)' <<<"$1"; then
    decide deny "Never force push. Push a new commit instead."
  fi
  if grep -qE '(\s|:|refs/heads/)main(\s|$)' <<<"$1"; then
    decide deny "Never push to main. Push a branch and open a pull request."
  fi
  refs=$(grep -oE '\s[^-[:space:]]\S*' <<<"$1" | wc -l)
  if { [ "$refs" -le 1 ] || grep -qE '\sHEAD(\s|$)' <<<"$1"; } &&
    [ "$(git -C "$cwd" branch --show-current 2>/dev/null)" = main ]; then
    decide deny "This is the main branch. Push a branch and open a pull request."
  fi
}
unquoted=$(tr -d "\"'" <<<"$cmd" | tr ';&|' '\n\n\n')
for n in $(grep -nE '\bgit(\s+-\S+(\s+[^-[:space:]]\S*)?)*\s+push\b' <<<"$bare" | cut -d: -f1); do
  line=$(sed -n "${n}p" <<<"$unquoted")
  check_push "push ${line#*[[:space:]]push}"
done
if has '\bgit\b.*\b(reset\s+--hard\b|clean\s+-[a-zA-Z]*f|branch\s+-D\b|stash\s+(drop|clear)\b)'; then
  decide ask "This can lose work or history."
fi
if has '\bgh\b.*\b(delete|merge|archive)\b|\bgh\s+api\b.*(-X|--method)\s*(DELETE|PUT|PATCH|POST)'; then
  decide ask "This changes GitHub."
fi
if has '\b(sst|cdk|sam|serverless|sls|agentcore)\b.*\b(deploy|launch|destroy|remove|delete)\b|\b(pnpm|npm|yarn)\b.*\bdeploy'; then
  decide ask "This deploys or removes live resources."
fi
if grep -E '^\s*((\S+=\S*|sudo|npx|uv run)\s+)*aws\s' <<<"$bare" | grep -vqE "$aws_read"; then
  decide ask "This changes AWS resources."
fi
if grep -qE '\bpython[0-9.]*\b.*\bboto3\b' <<<"$flat"; then
  decide ask "This calls AWS from Python."
fi
if has '\b(dropdb|dropuser)\b|\balembic\s+downgrade\b|\bmigrate\s+reset\b|\bdb\s+(reset|push)\b|\bbranches\s+delete\b|\bdrizzle-kit\s+(drop|push)\b|\b(psql|sqlite3|mysql)\b.*\s-f\b'; then
  decide ask "This can change or delete data in a database."
fi
if has '\b(psql|sqlite3|mysql|duckdb)\b' && grep -qiE "$sql" <<<"$flat"; then
  decide ask "This can change or delete data in a database."
fi
exit 0
