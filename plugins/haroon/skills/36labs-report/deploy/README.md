# Serving — `internal.36labs.dev/reports/<slug>`

Reports are served by **internal-ui** (`apps/internal-ui`), behind its existing
Better Auth (Google) session — same origin, so the login cookie just works, no
separate gate. R2 stores the HTML; `publish.py` uploads it via the S3 API; the
app's `/reports` Hono routes read it back.

- **Viewer app:** internal-ui  ·  **Host:** internal.36labs.dev  ·  **Routes:** `/reports`, `/reports/<slug>`
- **Bucket:** `36labs-internal-reports` (private)  ·  **CF account:** trendlaborg@gmail.com
- **Who can view:** any logged-in internal-ui user (sign-up is domain-gated to `@36labs.ai` / `@outercircle.one`)

> **History:** this used to be a standalone Cloudflare Worker + Access app on its
> own subdomain (`report.36labs.dev`). The Worker (and its `report.36labs.dev`
> custom domain) was **deleted on 2026-06-26** (`wrangler delete 36labs-internal-reports`);
> the host no longer resolves. One manual cleanup step remains — removing the
> orphaned Cloudflare Access application — see "Decommissioning the old Worker".

---

## One-time setup

### 1. Create the bucket (if it doesn't exist)
```bash
wrangler r2 bucket create 36labs-internal-reports
```

### 2. Mint a bucket-scoped R2 (S3) token
`dash.cloudflare.com` → **R2** → **Manage R2 API Tokens** → **Create API Token**:
- **Permissions:** Object Read & Write (publishers write; internal-ui reads — one
  token covers both, or mint a second Read-only token for internal-ui).
- **Specify bucket(s):** `36labs-internal-reports` only (do NOT grant account-wide).
- Create → copy the **Access Key ID**, **Secret Access Key**, and the **S3 endpoint**
  (`https://<account-id>.r2.cloudflarestorage.com`).

### 3a. Publishers — add the token to the **pulse_new** Infisical project
So `publish.py`'s `load_pulse_env()` resolves it:
```
R2_REPORTS_ENDPOINT_URL       https://<account-id>.r2.cloudflarestorage.com
R2_REPORTS_ACCESS_KEY_ID      <token access key>
R2_REPORTS_SECRET_ACCESS_KEY  <token secret>
R2_REPORTS_BUCKET             36labs-internal-reports
```
(`publish.py` also falls back to the repo's existing `R2_*` creds — same account —
so publishing works even before `R2_REPORTS_*` is set.)

### 3b. Serving — add the token to **internal-ui**'s Infisical project (99831c9d) + Railway
internal-ui is a separate service with its own Infisical project and Railway
service. Add the same four vars there (a Read-only token is enough):
```
R2_REPORTS_ENDPOINT_URL       https://<account-id>.r2.cloudflarestorage.com
R2_REPORTS_ACCESS_KEY_ID      <token access key>
R2_REPORTS_SECRET_ACCESS_KEY  <token secret>
R2_REPORTS_BUCKET             36labs-internal-reports
```
When any of these is unset the `/reports` routes answer **503** (the app still
boots). Backed by `@aws-sdk/client-s3` in the backend.

---

## Publish a report (every time — no deploy, no wrangler)
```bash
# from repo root
uv run python .claude/skills/36labs-report/deploy/publish.py <file.html> <slug> [--title ..] [--author ..]
# e.g.
uv run python .claude/skills/36labs-report/deploy/publish.py \
  scratchpad/retention_logout_deck.html retention-logout \
  --title "Retention Logout Investigation" \
  --author haroon@36labs.ai
# → https://internal.36labs.dev/reports/retention-logout
```
- `--title` display name (default: title-cased slug) · `--author` email (default: your `git config user.email`).
- Stored as R2 customMetadata; re-publishing the same slug overwrites + updates metadata.

Index `https://internal.36labs.dev/reports` shows each report's title, author, and
last-updated time, with a **search bar**.

## Test
Open `https://internal.36labs.dev/reports/<slug>` → logged out bounces to the
internal-ui login → log in with Google → report renders. The `/reports` index
lists everything in the bucket.

## Decommissioning the old Worker
- ✅ **Worker + `report.36labs.dev` route/DNS** — DELETED 2026-06-26 via
  `wrangler delete 36labs-internal-reports` (Trendlaborg account
  `25cd0da3f65b28c4d17a1cf86379dc6e`). The host no longer resolves.
- ⬜ **Cloudflare Access application** (manual — needs Zero Trust dashboard or an
  Access:Edit API token, which wrangler doesn't carry): dash.cloudflare.com →
  **Zero Trust** → **Access** → **Applications** → delete the `36 Labs Reports`
  app (the one whose domain was `report.36labs.dev`). It's orphaned now that the
  host is gone, so this is tidy-up, not load-bearing.

The bucket `36labs-internal-reports` and its data are untouched — only the old
front door is removed. internal-ui serves the same objects at `/reports`.
