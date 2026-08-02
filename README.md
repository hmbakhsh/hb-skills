# haroon-skills

Personal Claude Code plugin marketplace — one source of truth for skills and slash commands shared across repos.

## Install (any machine / repo)

```
/plugin marketplace add hmbakhsh/haroon-skills
/plugin install haroon@haroon-skills
```

Skills are then available everywhere as `/haroon:<name>` (e.g. `/haroon:deslop`).

## Update

Commit + push here, then in any session:

```
/plugin update
```

No version field in `plugin.json` on purpose — every commit is treated as a new version.

## Contents

Skills: `36labs-report`, `deslop`, `make-pr-easy-to-review`, `notion-todo`, `qna-form`, `verify-this`, `what-did-i-get-done`

Commands: `aristotle`, `commit-and-push`, `grill-me`, `post-merge`, `session-retro`
