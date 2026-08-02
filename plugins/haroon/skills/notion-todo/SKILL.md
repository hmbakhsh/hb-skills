---
name: notion-todo
description: File a structured engineering todo into the team's centralised Notion Kanban Board. Use when the user asks to add/file/note/log a todo, task, ticket, or reminder to Notion (e.g. "add this to my Notion todos", "file a todo for X", "make a note of this in Notion"). Produces a short title + one-line description on the database page, plus a full context breakdown in the page body that a cold reader (no prior conversation context) can understand.
---

# Notion Todo

File a structured engineering todo into the team's centralised Notion **Kanban Board** so a future agent or teammate — with zero context from this conversation — can pick it up and act on it.

## When to use

Triggered when the user asks to capture a task/todo/reminder/ticket in Notion. Common phrasings:

- "add this to my todos"
- "file a todo for …"
- "make a note of this in Notion"
- "log this as a task"
- "ticket this"

There is **one centralised Kanban Board** for the team — do not search for personal lists, do not ask which list. The board, schema, and assignment rules below are the entire interface.

## The board

- **Database URL:** https://www.notion.so/21451f38beba80ae887ae37bba3021a9
- **Data source ID:** `collection://21451f38-beba-81ad-9ec4-000bdc4ff8fe`

### Schema — fetch it, don't assume it

The board's properties and select options change over time, so **never rely on a hardcoded schema**. At the start of every run, fetch the live schema:

```
mcp__notion__notion-fetch id="collection://21451f38-beba-81ad-9ec4-000bdc4ff8fe"
```

Use the returned property names, types, and option lists as the source of truth for the `create-pages` call. The guidance below tells you *how to fill* the properties you'll find there; if a property mentioned below doesn't exist in the fetched schema, skip that guidance, and if the schema has properties not covered below, set them only when the user gave you a value.

How to fill the core properties (by name, as of last update — trust the fetched schema over this list):

- **`Task name`** (title) — short, action-oriented, scannable in a table view.
- **`Description`** (text) — one or two sentences. Hover/preview field — not the place for context.
- **`Assignee`** (person) — **required**; defaults to the requester (see Assignment below).
- **`Created By`** (person) — set to the requester's person ID (same lookup as Assignee) so the board shows who filed it regardless of which account the MCP connection uses. Verify the connection identity with `mcp__notion__notion-get-users user_id="self"` if in doubt.
- **`Status`** (status) — default to the schema's "new/to-do" option (currently `New Task`).
- **`Priority`** (select) — **leave unset by default**; only set when the user signalled urgency or named a priority.
- **`Task type`** (multi_select) — pick from the fetched options; recruiting/candidate tasks are `Hiring`, not `Engineering: Feature Request`, even if the deliverable is a tool or report.
- **Date / effort properties** — only set if the user gave a value. Don't invent one.
- **`Helpful links`** (url) — PR, issue, doc — set if there's an obvious one.

## Instructions

### 1. Resolve the requester (always)

The "requester" is the local user driving this conversation. Resolve their first name from git:

```bash
git config user.name
```

Take the first token (e.g. `Haroon Bakhsh` → `Haroon`). Never hardcode a name — always read it fresh so the skill works for any user.

If the fetched schema has a `Source list` select, set it to the requester's first name — its options are the team's first names. If the resolved first name is not among the options, ask the user which value to use.

### 2. Resolve the Assignee

**Default: assignee = requester.** The task belongs to whoever asked for it, unless they say otherwise.

Look up the requester's Notion person ID:

```
mcp__notion__notion-get-users query="{FirstName}"
```

Take the `id` from the first matching `type: person` result. If multiple people match the first name, prefer one whose `name` starts with the full git name; if still ambiguous, ask the user once.

**Override: when the user says the task is for someone else** — phrasings like "this is for Alex", "assign to Karta", "Gil should pick this up", "for Gil", "@Gil" — look up that person instead with `mcp__notion__notion-get-users query="{TheirFirstName}"` and use their ID as the Assignee. Leave `Source list` as the requester's first name (the requester filed it; the assignee owns it).

If the user names someone you can't find in the workspace, ask before falling back to assigning the requester.

### 3. Decide the property values

Keep `Task name` short and action-oriented — something scannable in a table view. Not a sentence, not a paragraph.

Keep `Description` to **one or two sentences**. It's a hover/preview field.

Set `Status = "New Task"` by default. **Do not set `Priority` by default** — leave it unset and let the requester triage it on the board. Only set `Priority` when the user explicitly names one ("high priority", "low pri") or signals urgency ("urgent", "blocker", "asap" → `High`). Pick `Task type` from the wording against the fetched options — e.g. bug report → `Engineering: Bug Report`, "would be nice if…" / "we should add…" → `Engineering: Feature Request`, recruiting → `Hiring`. Multiple are allowed; none is also fine.

### 4. Put the real context in the page body

The page body is where a cold reader learns enough to act. Use this structure (skip sections that don't apply, but keep the order):

```markdown
## What's happening today

{Current behavior, in plain language. Assume the reader has never touched this code or feature. Name the relevant command/flag/file so they can find it.}

## Why that's a problem

{Numbered list. Each item is a distinct failure mode or cost. Be concrete — "silent failure", "brittle", "compounds with X" — not vague ("suboptimal").}

## Example

> {A walkthrough with real values. Show the input, show what happens today, show why it's surprising or wrong. Use a blockquote so it reads as a scenario, not as prose.}

## Proposed behavior

{Bullet list of the desired behavior. One bullet per observable change. Include any new logging/warnings so the behavior is debuggable.}

## Where to look

{File paths, module names, config files, and the branch where this came up (if relevant). Enough for the implementer to orient without re-deriving context.}
```

Rules for the body:

- **Write for a cold reader.** Don't reference "the conversation" or "what we just discussed". Don't use pronouns without antecedents. If the todo came out of a specific branch/PR/incident, name it.
- **At least one concrete example.** Abstract descriptions are not enough. Show real inputs and real outputs (or expected outputs).
- **Name files and flags explicitly.** `lib/generation/`, `generation_models.yaml`, `--video-duration`, `feat/branch-name`. Grep-able beats descriptive.
- **No meta-commentary.** Don't write "this todo captures…" or "the goal of this page is…". Just describe the work.
- **No emojis** in the body (the `Task type` property already carries them).

### 5. Create the page

Call `mcp__notion__notion-create-pages` with:

- `parent.type = "data_source_id"`
- `parent.data_source_id = "21451f38-beba-81ad-9ec4-000bdc4ff8fe"`
- Properties from steps 1–3, using the property names and option values from the fetched schema (person properties like `Assignee` / `Created By` are person ID arrays).
- Page body from step 4 as the `content`.

### 6. Report back

Give the user:

- The Notion page URL.
- Who it was assigned to (and the `Source list` value if different from the assignee).
- Priority (if set) + task type.
- A one-sentence summary of what was captured, so they can sanity-check the framing without opening the page.

Keep the reply short. The page is the deliverable, not the chat reply.

## Anti-patterns to avoid

- Searching for or creating a "personal todo list" — there is one board, use it.
- Asking the user which list to file under — there is only one.
- Stuffing the `Description` property with paragraphs of context. It belongs in the page body.
- Forgetting to set `Assignee` — the board is unusable without it.
- Setting `Source list` to the assignee's name when the requester is someone different. `Source list` = who asked, `Assignee` = who does it.
- Writing a page that only makes sense if you've seen the conversation that produced it.
- Skipping the Example section because "it's obvious". It's not obvious to a cold reader.
- Inventing property values not in the fetched schema (e.g. a `Critical` priority).
- Inventing a due date or effort value the user didn't give.
- Trusting a property/option list written down in this file (or a past run) instead of fetching the live schema.
