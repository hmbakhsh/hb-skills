# hb-skills

Personal Claude Code plugin marketplace — one source of truth for skills and slash commands shared across repos.

## Install (any machine / repo)

```
/plugin marketplace add hmbakhsh/hb-skills
/plugin install hb@hb-skills
```

Skills are then available everywhere as `/hb:<name>` (e.g. `/hb:deslop`).

## Update

Commit + push here, then in any session:

```
/plugin update
```

No version field in `plugin.json` on purpose — every commit is treated as a new version.

## Contents

Skills: `deslop`, `make-pr-easy-to-review`, `qna-form`, `verify-this`, `what-did-i-get-done`

Commands: `aristotle`, `commit-and-push`, `new-worktree`, `post-merge`, `session-retro`
