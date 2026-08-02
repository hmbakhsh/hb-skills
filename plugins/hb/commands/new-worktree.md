---
argument-hint: <feature description or branch name>
description: Start new work in an isolated git worktree (guided)
---

Start new work in an isolated workspace: create a git worktree under `.worktrees/<branch>` on a fresh branch, then continue straight into the task.

## Input

Raw input: $ARGUMENTS

`$ARGUMENTS` is a description of the work the user is about to start — NOT a branch name. The user will not hand you a slug or a `feat/...` string; it's your job to infer a good branch name from their stated intent, or probe them if intent is unclear. Also mine the recent conversation: the user may have already described the feature/bug above without restating it here.

## Step 1 — infer the branch name

Derive a short, descriptive branch name from the user's intent — don't ask them to name it:
- Read `$ARGUMENTS` (and recent conversation) for what they're building or fixing, then slugify: lowercase, non-alphanumeric → `-`, ~3-5 words, prefixed `feat/` (or `fix/` for a clear bugfix). E.g. "I'm adding retry backoff to the publish worker" → `feat/publish-retry-backoff`; "the karaoke timing is off on shorts" → `fix/karaoke-timing-shorts`.
- If they happen to give an explicit branch (`feat/...`, contains `/`), respect it as-is.
- Only probe when intent is genuinely unclear or absent: ask "What are you about to work on?" (one line) and infer from their answer — still don't ask them for a slug.

State the branch name you inferred in one line and proceed. Only pause for confirmation if you had to guess hard or the work could map to several very different names; otherwise keep moving.

## Step 2 — create the worktree

From the repo root:

```bash
git worktree add .worktrees/<branch> -b <branch> <base>
```

- `<base>` defaults to the repo's default branch (`main` unless the repo says otherwise). Use another base only if the user asks.
- Ensure `.worktrees/` is ignored: if it isn't in `.gitignore`, add it (or confirm `git check-ignore .worktrees` passes some other way) before creating the worktree.
- If the repo has an env file the worktree needs (e.g. `.env.local`, gitignored so not carried over), copy it into the worktree and say so.

## Step 3 — report and continue

- Print the worktree path (`.worktrees/<branch>`) and the `cd` command. Don't `cd` for the user mid-session unless they ask.
- Teardown when done: `git worktree remove .worktrees/<branch> && git branch -d <branch>`.
- Then continue straight into the task the user described — don't stop and wait after creating the worktree; pause only for real questions.
