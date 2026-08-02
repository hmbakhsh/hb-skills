"""Publish a generated HTML report to the Google-gated host — frictionless.

No wrangler, no Cloudflare-account login. Uploads to the private R2 bucket via the
S3 API using a BUCKET-SCOPED token persisted in Infisical (R2_REPORTS_*). The
internal-ui app (apps/internal-ui) serves it at internal.36labs.dev/reports/<slug>
behind its existing Better Auth (Google) session — same origin, no separate gate —
and the /reports index renders the title, author, and last-updated time with search.

Usage (from repo root):
    uv run python .claude/skills/36labs-report/deploy/publish.py <file.html> <slug> [options]

    uv run python .claude/skills/36labs-report/deploy/publish.py \\
        scratchpad/retention_logout_deck.html retention-logout \\
        --title "Retention Logout Investigation" \\
        --author haroon@36labs.ai

Options:
    --title   Display title on the index (default: title-cased slug)
    --author  Author email (default: your `git config user.email`)

→ https://internal.36labs.dev/reports/<slug>

Required env (Infisical, pulse_new project):
    R2_REPORTS_ENDPOINT_URL · R2_REPORTS_ACCESS_KEY_ID · R2_REPORTS_SECRET_ACCESS_KEY
    R2_REPORTS_BUCKET (optional; default 36labs-internal-reports)
"""

from __future__ import annotations

import argparse
import datetime
import os
import subprocess

try:
    from lib.utils.env_loader import load_pulse_env

    load_pulse_env()
except Exception:  # noqa: BLE001 - env may already be exported
    pass

import boto3  # noqa: E402

HOST = "internal.36labs.dev"
REPORTS_PATH = "reports"
DEFAULT_BUCKET = "36labs-internal-reports"


def _git_email() -> str:
    try:
        return subprocess.check_output(["git", "config", "user.email"], text=True).strip()
    except Exception:  # noqa: BLE001
        return ""


# S3/R2 user-metadata must be ASCII. Titles routinely carry smart punctuation
# (em dash, middot, curly quotes, ellipsis) — fold those to ASCII rather than
# rejecting the upload, then drop anything still non-ASCII.
_ASCII_FOLD = str.maketrans(
    {
        "–": "-",
        "—": "-",
        "·": "-",
        "•": "-",
        "…": "...",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        " ": " ",
    }
)


def _ascii_meta(value: str) -> str:
    return value.translate(_ASCII_FOLD).encode("ascii", "ignore").decode("ascii").strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Publish an HTML report to internal.36labs.dev/reports")
    ap.add_argument("file", help="path to the .html report")
    ap.add_argument("slug", help="url slug, e.g. retention-logout")
    ap.add_argument("--title", default="", help="display title (default: title-cased slug)")
    ap.add_argument("--author", default="", help="author email (default: git user.email)")
    args = ap.parse_args()

    if not os.path.isfile(args.file):
        raise SystemExit(f"no such file: {args.file}")

    # Prefer a bucket-scoped token (R2_REPORTS_*); fall back to the repo's main
    # R2_* creds (same account, already in Infisical) so publishing works with no
    # extra setup. Swap in a scoped token later by just setting R2_REPORTS_*.
    try:
        endpoint = os.environ.get("R2_REPORTS_ENDPOINT_URL") or os.environ["R2_ENDPOINT_URL"]
        access_key = os.environ.get("R2_REPORTS_ACCESS_KEY_ID") or os.environ["R2_ACCESS_KEY_ID"]
        secret_key = os.environ.get("R2_REPORTS_SECRET_ACCESS_KEY") or os.environ["R2_SECRET_ACCESS_KEY"]
    except KeyError as missing:
        raise SystemExit(
            f"missing env {missing} — need R2_REPORTS_* or R2_* in Infisical (see deploy/README.md)"
        ) from missing
    bucket = os.environ.get("R2_REPORTS_BUCKET", DEFAULT_BUCKET)

    author = args.author or _git_email()
    # S3/R2 user-metadata is ASCII-only — fold smart punctuation to ASCII. The
    # title baked into the HTML keeps its original characters; only the metadata
    # copy (used by the /reports index) is folded.
    meta = {k: _ascii_meta(v) for k, v in {"title": args.title, "author": author}.items() if _ascii_meta(v)}

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )
    with open(args.file, "rb") as fh:
        body = fh.read()
    # Bake the author + publish date into the template's title bar by replacing
    # the {{AUTHOR_EMAIL}} / {{PUBLISHED_DATE}} tokens (the templates carry them;
    # a hand-written file without the tokens is uploaded unchanged). Single
    # source of truth: the same --author + today's date that drive the metadata.
    published = datetime.date.today().strftime("%-d %b %Y")
    # Title shown in the sidebar — keeps original (unicode) chars, unlike the
    # ASCII-folded metadata copy. Defaults to the title-cased slug. Minimal HTML
    # escaping since it lands in element text.
    display_title = args.title or args.slug.replace("-", " ").replace("_", " ").title()
    display_title = display_title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = body.decode("utf-8", errors="replace")
    html = (
        html.replace("{{AUTHOR_EMAIL}}", author)
        .replace("{{PUBLISHED_DATE}}", published)
        .replace("{{REPORT_TITLE}}", display_title)
    )
    body = html.encode("utf-8")
    s3.put_object(
        Bucket=bucket,
        Key=f"{args.slug}.html",
        Body=body,
        ContentType="text/html; charset=utf-8",
        Metadata=meta,
    )
    print(f"live → https://{HOST}/{REPORTS_PATH}/{args.slug}")
    if meta:
        print("       " + " · ".join(f"{k}={v}" for k, v in meta.items()))


if __name__ == "__main__":
    main()
