#!/usr/bin/env bash
# Status line: shows which worktree and branch this session is working in,
# so parallel sessions are easy to tell apart.

input=$(cat)
dir=$(jq -r '.workspace.current_dir' <<<"$input")
tree=$(jq -r '.worktree.name // .workspace.git_worktree // "main checkout"' <<<"$input")
branch=$(git -C "$dir" branch --show-current 2>/dev/null)

echo "worktree: $tree | branch: ${branch:-none}"
