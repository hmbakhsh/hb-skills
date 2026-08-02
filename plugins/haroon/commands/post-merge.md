Post-merge cleanup: stash local changes, switch to main, pull, restore stash, optionally start a new branch.

## When to run

Run this after merging a PR into main. Works in the same session where `/create-pr` ran or in a fresh session — it is fully stateless.

## Tone

This command is used by people who are not git experts. Write all user-facing messages in plain English. Avoid git jargon unless you also immediately explain what it means. Never surface a raw git error without translating it into what actually happened and what the user should do. Reassure at every step — "you're safe", "nothing is lost", "we're just moving to main".

## Input

Raw input: $ARGUMENTS

No required arguments. Optional:
- `--branch <name>` — new branch name to create after pulling main (skips the interactive prompt)
- `--no-branch` — skip the new branch prompt and stay on main

## Execution

### Step 1: Identify current state

```bash
git rev-parse --abbrev-ref HEAD
git status --porcelain
```

Tell the user in plain terms:
> "You're currently on branch `<name>`. Let's get you back to main with the latest changes from your merged PR."

If already on `main`, skip Steps 2–4 and go directly to Step 5. Tell the user there's no branch to switch from.

### Step 2: Check if the PR is merged (if not already on main)

```bash
gh pr view --json state,title,url --jq '{state: .state, title: .title, url: .url}'
```

Translate the result:
- `MERGED` → "Your PR was merged successfully. Let's continue." Proceed.
- `OPEN` → "Your PR (`<title>`) is still open on GitHub — it hasn't been merged yet. Are you sure you want to continue switching to main?" Wait for confirmation.
- `CLOSED` → "Your PR was closed without being merged. Do you still want to switch to main?" Wait for confirmation.
- No PR found → "I couldn't find a PR for this branch. Do you still want to switch to main?" Wait for confirmation.

### Step 3: Stash uncommitted changes

```bash
git status --porcelain
```

If the working tree is clean, tell the user: "No unsaved local changes — nothing to set aside." Skip to Step 4.

If there are uncommitted changes, explain before doing anything:
> "You have local changes that haven't been committed yet. Before switching branches, I'll temporarily set them aside (this is called a 'stash' — think of it like putting your work in a safe drawer). We'll bring them back once we're on main."

Show the list of affected files in plain language (not raw porcelain codes — translate `M` as "modified", `A` as "new file", `?` as "untracked/new"):

```
Files being set aside:
  modified:   lib/foo.py
  new file:   lib/bar.py
  untracked:  notes.txt
```

Then stash:

```bash
git stash push --include-untracked -m "post-merge stash from <branch-name> on <YYYY-MM-DD>"
```

Confirm: "Done — your changes are safely stored. We'll restore them in a moment."

Record that a stash was created.

### Step 4: Switch to main

```bash
git checkout main
```

Tell the user before running: "Switching to the main branch..."

If it succeeds: "You're now on main."

If it fails: stop, report in plain English what went wrong (e.g. "Git couldn't switch branches — this is unusual. Your stash is safe. Please let me know what the error says and we'll figure it out together."). Do not force anything.

### Step 5: Pull latest main

Tell the user: "Fetching the latest changes from GitHub..."

```bash
git pull
```

If new commits came in: "Got it — pulled in the latest changes from main." List the commits in one line each (from the pull output).

If already up to date: "Main is already up to date — nothing new to pull."

### Step 6: Restore stash

If no stash was created in Step 3, skip this step entirely.

Tell the user: "Now let's bring your local changes back..."

Before applying, show a plain-English preview of what's about to be restored:

```bash
git stash show stash@{0} --name-only
```

Show it as:
```
Changes being restored:
  lib/foo.py
  lib/bar.py
  notes.txt
```

Then apply (do NOT use `git stash pop` — `apply` keeps the stash entry intact no matter what happens next):

```bash
git stash apply stash@{0}
```

**If `git stash apply` exits 0 (success):**

Tell the user:
> "All your local changes have been restored. You're on main with everything you had before."
>
> "Your saved copy (stash) is still there as a backup. You can remove it by running `git stash drop`, or just leave it — it won't affect anything."

Do NOT auto-drop the stash.

**If `git stash apply` exits non-zero (conflict):**

This means some of the stashed files were also changed by the merge into main, and git needs human help deciding which version to keep.

First, run `git status --porcelain` to see exactly which files have conflicts.

Tell the user in plain English:

> "Almost there — but I hit a snag. Some of the files you were working on were also changed by the PR that was merged into main. Git isn't sure which version to keep, so it needs your help to decide."
>
> "**Nothing is lost.** Your saved changes are still intact in the stash. The files below have been partially updated and contain markers showing both versions — yours and the one from main."
>
> "**Do NOT run any command that 'cleans' or 'resets' your files** (like discarding changes in your editor, or running git reset). That would erase the work we're trying to restore."

Then list the conflicted files in plain language (translate status codes: `UU` = "both sides changed", `AA` = "both sides added", `DU` = "deleted on one side"):

```
Files needing your help:
  lib/foo.py   ← you changed it, and main changed it too
  lib/bar.py   ← both sides added something new
```

Then offer to walk through each conflict interactively:

> "Would you like me to go through each file with you and help you decide what to keep? Just say yes and I'll handle it one file at a time."

**If the user says yes (interactive resolution):**

For each conflicted file:
1. Read the file with the Read tool.
2. Find all conflict blocks (lines between `<<<<<<<`, `=======`, `>>>>>>>`).
3. Show each conflict block to the user in readable form:
   ```
   File: lib/foo.py  (conflict 1 of 2)

   YOUR version (what you had locally):
     result = process(data, mode="fast")

   MAIN's version (what came in from the merged PR):
     result = process(data, mode="fast", timeout=30)

   Which would you like to keep? (yours / main's / I'll show you both together)
   ```
4. Based on their answer, edit the file to resolve that block.
5. After all conflicts in a file are resolved, stage it:
   ```bash
   git add <file>
   ```
6. Confirm: "lib/foo.py resolved and saved."
7. Move to the next conflicted file.

After all files are resolved:
> "All conflicts resolved. Your changes are back and everything is consistent."
>
> "Run `git stash drop` to remove the now-unnecessary saved copy, or leave it as a backup."

**If the user says no (manual resolution):**

Give them the simplest possible instructions:

> "No problem. Here's what to do:"
>
> "1. Open each file listed above in your editor. Look for lines that start with `<<<<<<<` — those are the conflict spots."
>
> "2. Each conflict looks like this:"
> ```
> <<<<<<< Your changes
> result = process(data, mode="fast")
> =======
> result = process(data, mode="fast", timeout=30)
> >>>>>>> From main
> ```
> "Delete the markers and keep whichever version (or a combination) you want."
>
> "3. Once you've fixed all the conflicts in a file, come back here and let me know. I'll save it and move to the next one."
>
> "Your stash is safe the whole time — don't worry about losing anything."

Wait for the user to confirm each file is resolved, then stage it (`git add <file>`) and move to the next.

After all resolved: "All done. Run `git stash drop` to clean up the backup copy."

Stop here — do not proceed to Step 7 until the user confirms all conflicts are resolved.

### Step 7: Offer a new branch

If `--no-branch` was passed, skip this step entirely.

If `--branch <name>` was passed, create the branch immediately:

```bash
git checkout -b <name>
```

Confirm: "Created and switched to new branch `<name>`. You're ready to start working."

Otherwise, ask the user:

> "You're now on main with everything up to date. Would you like to start a new branch for your next piece of work?"

If they say yes but don't provide a name, suggest one. Look at `git log --oneline -5` for context on what they've been working on. Propose a branch name in the format `feat/short-description` or `fix/short-description` and ask if that works or if they'd like something different.

Once a name is confirmed:

```bash
git checkout -b <name>
```

Confirm: "Created and switched to `<name>`. You're good to go."

If they say no or leave it blank: "Staying on main. You're all set."

### Step 8: Summary

Print a clean, plain-English summary:

```
All done. Here's what happened:

  Branch:   Switched from <old-branch> → main, pulled latest changes
  Changes:  <Restored from stash | No local changes to restore | Conflicts resolved — stash backup still at stash@{0}>
  Next:     <Now on new branch <name> | Staying on main>
```

If there were conflicts, add one final reminder at the bottom:
> "Remember to run `git stash drop` once you've confirmed everything looks right."

## Important

- NEVER force-push, reset --hard, or delete branches.
- NEVER auto-resolve conflict markers — always involve the user in choosing which version to keep.
- NEVER auto-drop the stash at any point, success or failure.
- If `git checkout main` fails for any reason, stop and explain in plain English — do not attempt workarounds.
- Always translate raw git output into plain English before showing it to the user.
