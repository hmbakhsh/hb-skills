Reflect on this session and surface concrete changes that make the model more efficient and the codebase more AI-agentic-native for future sessions without your current context.

## Goal

Identify friction the model hit in this session — failed tool calls, wrong defaults, missing context, redundant work, suboptimal paths — and propose specific fixes to the repo, CLAUDE.md, slash commands, hooks, or settings. Two framings that both matter:

- **Model efficiency** — fewer wasted tool calls, less backtracking, less context burned on stale refs or garbage output, fewer wrong-default corrections.
- **Agentic-native codebase** — structure, docs, hooks, and tooling that let an agent succeed the first time without human hand-holding. Clear contracts, explicit defaults, discoverable commands, self-describing conventions.

The output is for compounding: every retro should leave the repo more legible to the next agent.

## How to answer

Walk back through the session. For each friction point, report:

1. **What happened** — the actual command, file, or moment. Quote output if relevant.
2. **Why it was friction** — wrong assumption, stale ref, hook misfire, missing allowlist, ambiguous docs, etc.
3. **Concrete fix** — a specific file/line to edit, a new slash command, a hook change, a CLAUDE.md addition, a settings.json permission. Not "be more careful" — an artifact change.

Group findings by priority:

- **High** — happens often, easy fix, clear win. E.g. a hook that misfires on every push, a default that's wrong 90% of the time.
- **Medium** — happens sometimes, fix is small. E.g. one line in CLAUDE.md that would prevent a common footgun.
- **Low** — rare or cosmetic. Note but don't belabor.

## Rules

- Be specific. "The `/create-pr` skill should diff against `origin/main` not local `main`, line 33 of `.claude/commands/create-pr.md`" beats "PR creation has issues with stale main".
- Don't sugarcoat. If the model wasted 3 tool calls on a wrong guess, say so — that's the signal.
- Skip generic advice ("use more subagents", "add more tests"). Only cite things you actually hit in *this* session.
- If nothing went wrong, say so in one line and stop. Don't invent friction.
- Distinguish model-side issues (wrong default, bad prompt) from tooling issues (hook bug, stale ref, missing permission). Tooling fixes compound better — they make the codebase agentic-native, not just the model better-behaved.

## Output shape

```
## Friction this session

**High**
- {one-line title} — {what, why, concrete fix with file:line}
- …

**Medium**
- …

**Low**
- …

## Suggested artifact changes

1. {file path or new file} — {what to add/change, why}
2. …
```

Keep it tight. The reader is the same developer who just ran the session — they don't need context, they need the list of edits.
