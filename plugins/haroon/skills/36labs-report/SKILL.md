---
name: 36labs-report
description: Generate a polished single-file HTML report OR slide deck in 36 Labs dark-mode brand style — embedded logo, system font, brand-blue accents, card/badge/pill/table components, low text density. Use whenever the user asks for a visual report, slide deck, slides, branded HTML summary, investigation writeup, or "make this look like 36 Labs".
---

# 36 Labs Report / Deck

Builds a **self-contained `.html` file** (no build step, no external assets, no network) styled in the 36 Labs internal-platform look. Two formats share one design system:

- **Report** — long-scroll document. Numbered sections, cards, comparison tables, callouts. For detailed writeups.
- **Deck** — fullscreen slides, one idea each, keyboard/click nav. For presenting. **Low text density — headlines + one visual + ≤3 short lines per slide.**

## Workflow: build → publish → share
When asked to make a report/deck — or when the user pastes the index page's **"Copy Claude prompt"** text:
1. **Ask first if unspecified:** what it's about, **report vs deck**, and any key points/data/sources. Don't build until you know the topic + format.
2. **Build** the single-file HTML from `templates/` (swap content only; keep the brand chrome).
3. **Publish** it:
   ```bash
   uv run python .claude/skills/36labs-report/deploy/publish.py <file.html> <slug> \
     --title "<Display Title>" --author <user's git email>
   ```
   Pick a short kebab-case `<slug>` from the title; author defaults to `git config user.email`.
4. **Always surface the URL** as the deliverable at the end: `https://internal.36labs.dev/reports/<slug>`.

If `R2_REPORTS_*` env is missing, the upload token isn't set up — point the user to `deploy/README.md`.

## How to use

1. **Pick format** from the request: "slides / deck / present" → deck; "report / writeup / doc" → report. If ambiguous, ask once.
2. **Copy the matching template** from `templates/deck.html` or `templates/report.html` into the target `.html`.
3. **The content region is a palette, not a script.** It holds one of every component (title, tiles, chart, split, callout, steps, ranked list, rows, checklist, list, table, reference) purely as a **styling reference**. Keep the components your material needs, delete the rest, reorder them, and repeat any. There is no required set or number of slides/sections — the content drives the shape, not the template. Don't add a slide just because the palette has one, and don't pad to "fill" it.
4. **Replace only the content**, never the chrome — don't touch the `<style>` block, the `.topbar`/`.toc`/`.nav` markup, or the scripts; that IS the brand. Slide count + Contents rail update themselves from the DOM. Give each deck slide a `data-title="…"` (its Contents-rail label).
5. Write the file, then `open <path>` (macOS) so the user sees it.

**Title bar (both templates).** The top bar shows the **document title** (left, beside the rail toggle) plus the **author email + publish date** (right). All three are tokens — `{{REPORT_TITLE}}` / `{{AUTHOR_EMAIL}}` / `{{PUBLISHED_DATE}}` — that `deploy/publish.py` fills at upload (from `--title`, `--author`, today's date). Leave them alone; opened pre-publish they're hidden.

**Contents rail.** An in-page left rail of just the entries, built automatically — deck = one per slide (jumps to it), report = the hero + every `h2.sec` (jumps + highlights the active section as you scroll). The title-bar toggle hides/shows it (content reflows to fill the space); auto-hidden below 1000px. Content stays fully interactive. No wiring needed.

The logo is inlined as SVG directly in the templates (`<svg class="mark">…`) so the file stays single-and-portable. `assets/36labs-mark.svg` is the source if you need it elsewhere.

## Structure & tone (advice — the user drives the actual shape)

These are defaults that make a report land, not a required template. Adapt freely to the material; the user decides the final structure and emphasis.

- **Open with context.** Before diving into findings, give the reader enough to follow the rest: what this is about (one line) and the situation around it — who/what's affected, what changed or triggered it, what "normal" looks like. A cold reader shouldn't have to ask "wait, what is this?". This matters most when the audience is outside the immediate team; skip or shrink it when everyone already shares the context.
- **Then the substance, each piece led by its conclusion** — evidence, comparisons, what was ruled out, the core insight. State the takeaway first, support it second.
- **Close with what it means** — the decision, next steps, or what's still open.
- **Self-contained copy.** Every slide/section should read on its own, without someone narrating alongside it. No reliance on a verbal "talk track".
- It's a guideline, not a checklist — use the pieces the story needs, in the order that fits.

## Content rules (the part that makes it good)

- **Plain language, low jargon.** Write for a smart reader *outside* the immediate team. Spell out or avoid acronyms and internal names; if a technical term is unavoidable, gloss it in a few words (e.g. "iGaming (online gambling)"). Prefer short everyday words over precise-but-opaque ones. Goal: instant comprehension, not sounding clever.
- **Make the Contents echo the slides.** Each slide's `data-title` (deck) / section heading (report) becomes its Contents-rail label — reuse the slide's *own* headline wording, not a separate abstract category. If the slide reads "A burst gets rate-limited", label it "Burst gets rate-limited", not "Hypothesis". Matching wording lets a reader scan the rail and map each entry to what's on screen.
- **One idea per slide / per card.** If a slide needs a paragraph, split it.
- **Convert prose → components:** comparison → table or split-panel; status → badge; list → lean list with mono index; key number → `.big` stat.
- **Lead with the insight, not the buildup.** Headline states the conclusion; supporting detail is secondary/muted.
- Max ~3 short lines of body per slide. Reports can be denser but still favor cards over walls of text.
- Use `code` for identifiers/paths, mono for hashes/IPs.

## Design tokens (already baked into the templates — reference only)

Dark theme, OKLch-derived. Background `#0a0a0a`, cards `#1b1b1b`, hairline borders `rgba(255,255,255,.10)`.

```
--bg:#0a0a0a   --card:#1b1b1b   --card-2:#202020
--fg:#fafafa   --muted:#b3b3b3  --faint:#7d7d7d
--border:rgba(255,255,255,.10)  --border-strong:rgba(255,255,255,.18)
--brand:#648ad9   --brand-2:#8fb0ee        (36 Labs blue + light tint)
--ok:#34d399   --warn:#f5b042   --bad:#ff5c5c   (+ matching translucent bg)
--sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif
--mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
radius: 12px cards · 6–8px badges/buttons · 999px pills
```

Signature treatments: brand-blue radial glow top-right of the page; uppercase tracked eyebrow labels in `--brand-2`; `.grad` text (white→blue clip) for hero words; `inset 0 0 0 1px var(--border)` instead of heavy shadows; emerald/amber/red badges for status.

## Components available in the templates

`.eyebrow` (uppercase brand label) · `h1`/`h2` headings · `.big`/`.grad` hero text · `.pill` (with `.dot` status colors) · `.badge` (`ok`/`warn`/`bad`/`neutral`) · `.card` · `.split` (two-pane A-vs-B) · `.rows`/`.row.diff` (comparison list) · `.flow`/`.fcard` (numbered steps) · `.steps` (rank rows: num + label/sublabel + value) · `.tiles`/`.tile` (stat grid) · `.chips` (checklist grid) · `.insight` (gradient callout) · `ul.lean` (indexed list) · `.kv` (key/value reference) · report-only: numbered `.sec` sections + `table`.

## Charts (Chart.js, ported from the whop-analysis deck)
Both templates load Chart.js and ship two helpers + matching dark styling. To add a chart:
1. Drop a card with a canvas where you want it: `<div class="chart-card"><div class="ch-h"><span style="background:var(--brand)"></span>Title</div><div class="chart-wrap"><canvas id="cFoo"></canvas></div></div>`.
2. Register it in the **CONTENT CHART DATA** script block at the bottom: `CHARTS.cFoo = cv => hbar(cv, [{label:'A', value:120}, …], {colors:[…]})`.

`hbar(canvas, rows, opts)` = horizontal bars (rows `{label, value}`; `opts.colors`, `opts.fmtv`, `opts.endfmt`). `doughnut(canvas, rows)` = donut (rows `{label, value, color}`). Deck charts build lazily when their slide first shows; report charts build when scrolled into view. Palette: `--brand` accent, `--chart-cream` default bars, `--src`/`--asm`/`--fin` for layered groups.

## Deck nav (built in)
← → / space / PageUp-Down, click right-half = next / left-half = back, dots jump, Home/End. Counter top-right. Don't reimplement.

## Publish behind the internal-ui Google session
Reports are **served by internal-ui** (`apps/internal-ui`) at `internal.36labs.dev/reports/<slug>`, behind its existing Better Auth (Google) session — same origin, so the login cookie just works, no separate gate. R2 still stores the HTML; `publish.py` uploads it via the S3 API (bucket-scoped token from Infisical), and internal-ui's `/reports` route reads it back. Publishing is a single upload — **no wrangler, no CF login**:
```bash
uv run python .claude/skills/36labs-report/deploy/publish.py <file.html> <slug> \
  --title "Display Title" --author you@36labs.ai
# → https://internal.36labs.dev/reports/<slug>   (only logged-in @36labs.ai users)
```
`--title`/`--author` are stored as R2 customMetadata. The `/reports` index renders each report's title, author, and last-updated time with a **search bar**. Bucket `36labs-internal-reports`, CF account trendlaborg@gmail.com. Publishers need only repo + Infisical access (`R2_REPORTS_*`). The old standalone `report.36labs.dev` Worker + Cloudflare Access app are decommissioned — see `deploy/README.md`.
