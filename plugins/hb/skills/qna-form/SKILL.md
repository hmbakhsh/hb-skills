---
name: qna-form
description: Ask the user a batch of design/decision questions in a browser form instead of a long chat wall. Answers post straight back to the agent (no copy-paste). Use when you have 4+ related decisions to confirm, want defaults pre-selected for rubber-stamping, and want a per-question comment box. Not for a single quick question.
---

# qna-form

Render a decision form from a small JSON spec, serve it locally, capture the answers to a file. The user picks radios (defaults pre-selected), types comments, hits **Submit to Claude** — no copy-paste back into the chat.

## When to use
- 4+ related decisions to confirm before writing a plan / doing work.
- You want defaults the user can rubber-stamp, ⭐ markers for the ones that branch the design, and a comment box per question.
- **Don't** use for a single question or a yes/no — just ask in chat.

## How to use (agent steps)
1. **Write a spec** JSON (see `spec.example.json`). Group the questions; mark each with `"default": true` on the recommended option and `"star": 1|2` on architecture-branching ones. Add `"comment": true` to any question that deserves a free-text note. Keep option labels short.
2. **Run the server** (background), pointing at your spec and an output path:
   ```bash
   python .claude/skills/qna-form/serve_form.py /tmp/my-spec.json --port 8765 --out /tmp/answers.json --open
   ```
   `--open` launches the browser. On a taken port, pick another.
3. **Wait for the answers file** (don't block the chat):
   ```bash
   until [ -f /tmp/answers.json ]; do sleep 1; done; echo READY
   ```
   Run this with `run_in_background: true`. The server also prints `ANSWERS_RECEIVED` on submit.
4. **Read `/tmp/answers.json`**, apply the answers, then stop the server (kill the background job).

## Spec format
```jsonc
{
  "title": "Feature X — Design Decisions",
  "intro": "One line shown under the title.",
  "groups": [
    {
      "name": "A · Scope",
      "questions": [
        {
          "id": "q1",              // unique; keys the answers
          "num": "1",              // optional label shown before the title
          "star": 1,               // optional ⭐ count (branching importance)
          "title": "Which approach?",
          "sub": "Context for the tradeoff.",
          "type": "radio",         // radio | text | textarea
          "comment": true,          // adds a per-question comment box
          "options": [
            { "value": "a", "label": "Option A", "default": true },
            { "value": "b", "label": "Option B" }
          ]
        },
        { "id": "scale", "title": "Rough scale", "type": "text", "placeholder": "e.g. ~8" }
      ]
    }
  ]
}
```
A free-text **overrides** box (`notes`) is appended automatically — don't add your own.

## Answers file shape
```json
{
  "answers":  { "q1": "a" },          // chosen radio values, keyed by question id
  "comments": { "q1": "..." },         // per-question comment text (empty string if blank)
  "text":     { "scale": "~8" },       // text / textarea question values
  "notes": "global overrides free-text"
}
```

## Notes
- stdlib only (`http.server`), no deps, binds `127.0.0.1` — local only.
- Server stays up after submit so the user can resubmit; kill it when done.
- The rendered HTML escapes all spec strings; safe to put prose in labels/subs.
