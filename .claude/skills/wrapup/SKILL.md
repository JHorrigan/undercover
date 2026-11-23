---
name: wrapup
description: End a working session cleanly. Saves where things stand to memory, checks for uncommitted or unpushed work and open pull requests, lists anything still running or able to charge, and says the next step. Use when James says he is stopping or going, or asks to wrap up.
---

# Wrap up

Goal: James can leave now, and the next session picks up exactly where this one stopped.

Work through these in order, then report once at the end.

## 1. Git

For each repo touched this session:

- `git status -sb` for the branch, uncommitted changes and anything not pushed.
- `gh pr list --author "@me"` for open pull requests and whether their checks passed.

Don't commit or push just to wrap up. Commits follow the Git rule in `AGENTS.md`: say what is uncommitted and ask James what to do with it.

## 2. Anything still running

List what this session started and is still running: background shells, dev servers, watchers. Say how to restart each one. Stop only what James won't need, and ask if unsure.

## 3. Anything that can cost money

List anything started this session that can charge: cloud resources, trials, API keys, paid services. Nothing is left charging without James knowing.

## 4. Memory

Update memory with:

- where the work stands
- what James decided this session, and why
- what he rejected, so it isn't offered again
- open questions

Update an existing memory rather than add a duplicate, and fix any memory that is now wrong. Don't save what git or the docs already record.

## 5. Report

Short, plain words, these headings only:

- **Done:** what changed this session.
- **Where it lives:** paths, branches and pull requests.
- **Still running:** what, and how to stop or restart it. "Nothing" if so.
- **Next step:** one line, plus the command to resume if there is one.
