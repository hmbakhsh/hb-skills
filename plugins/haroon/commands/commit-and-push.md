Create conventional commits for all staged and unstaged changes in the working tree, then push to remote.

## Input

Raw input: $ARGUMENTS

If `$ARGUMENTS` is provided, use it as guidance for how to group or describe the commits. Otherwise, auto-detect.

## Execution

### Step 1: Assess changes

```bash
git status
git diff
git diff --cached
git log --oneline -5
```

If there are no changes (no untracked, no modified, no staged), tell the user: "Nothing to commit."

### Step 2: Group changes by concern

Analyze all changed and untracked files. Group them into logical commits — each commit should represent ONE concern:

- **One feature** = one commit
- **One bug fix** = one commit
- **One refactor** = one commit
- **Docs changes** = one commit
- **Config/tooling changes** = one commit

If ALL changes serve a single purpose, make a single commit. Don't split artificially.

### Step 3: Write conventional commit messages

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]
```

**Types:**
- `feat` — new feature
- `fix` — bug fix
- `refactor` — code restructuring without behavior change
- `docs` — documentation only
- `chore` — tooling, config, CI, dependencies
- `test` — adding or fixing tests
- `style` — formatting, whitespace (no logic change)
- `perf` — performance improvement

**Rules:**
- Description is imperative mood, lowercase, no period: "add retry logic" not "Added retry logic."
- Keep the first line under 72 characters
- Use the body for context on WHY, not WHAT (the diff shows what)
- Scope is optional but useful: `feat(karaoke):`, `fix(scheduler):`, `chore(hooks):`

### Step 4: Stage and commit each group

For each logical group:
1. `git add` only the files for that group
2. `git commit` with a HEREDOC message

```bash
git add file1 file2
git commit -m "$(cat <<'EOF'
type(scope): description

Optional body explaining why.
EOF
)"
```

### Step 5: Push to remote

```bash
git push -u origin HEAD
```

If the push fails (e.g. no upstream, rejected), inform the user with the error.

### Step 6: Show summary

After all commits and push, show:
```
✓ N commits created and pushed:
  - <hash> <message>
  - <hash> <message>
```

## Important

- NEVER use `git add -A` or `git add .` — always add specific files
- NEVER amend existing commits unless the user explicitly asks
- Skip files that look like secrets (`.env`, credentials, tokens)
- If unsure how to group changes, ask the user
