#!/usr/bin/env python3
"""Render an interactive decision form from a JSON spec, serve it, capture the answers.

Agents write a small spec (see spec.example.json) instead of hand-writing HTML.
Run:  python serve_form.py spec.json [--port 8765] [--out /tmp/answers.json] [--open]
On submit the browser POSTs to /submit; answers land in --out as JSON and the
server prints ANSWERS_RECEIVED (a marker to wait on). stdlib only, no deps.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

STYLE = """
:root{--bg:#0d1117;--panel:#161b22;--panel2:#1c2230;--border:#2d333b;--text:#e6edf3;
--dim:#9aa4b2;--accent:#7c9cff;--accent2:#3fb950;--star:#e3b341;--danger:#f85149;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;padding:0 0 150px}
header{padding:28px 24px 20px;border-bottom:1px solid var(--border);background:linear-gradient(180deg,#11161f,#0d1117)}
header h1{margin:0 0 6px;font-size:22px}header p{margin:0;color:var(--dim);font-size:14px}
.wrap{max-width:860px;margin:0 auto;padding:24px}.group{margin:0 0 26px}
.group>h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);
margin:0 0 12px;border-bottom:1px solid var(--border);padding-bottom:6px}
.q{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:16px 18px;margin:0 0 12px}
.q .head{display:flex;gap:8px;align-items:baseline;margin-bottom:4px}
.q .num{color:var(--dim);font-variant-numeric:tabular-nums;font-weight:600}
.q .title{font-weight:600}.star{color:var(--star)}
.q .sub{color:var(--dim);font-size:13px;margin:4px 0 12px}
.opts{display:flex;flex-direction:column;gap:8px}
label.opt{display:flex;gap:10px;align-items:flex-start;padding:9px 11px;border:1px solid var(--border);
border-radius:8px;cursor:pointer;background:var(--panel2);transition:border-color .12s}
label.opt:hover{border-color:var(--accent)}label.opt input{margin-top:3px;accent-color:var(--accent)}
label.opt .txt{flex:1}label.opt .txt .default{color:var(--accent2);font-size:12px;font-weight:600;margin-left:6px}
input[type=text],textarea.cmt{width:100%;background:var(--panel2);border:1px solid var(--border);color:var(--text);
border-radius:8px;padding:9px 11px;font-size:14px;font-family:inherit}
input[type=text]:focus,textarea.cmt:focus{outline:none;border-color:var(--accent)}
textarea.cmt{margin-top:10px;resize:vertical;min-height:38px}
.cmt-lbl{color:var(--dim);font-size:12px;margin-top:10px;display:block}
.bar{position:fixed;left:0;right:0;bottom:0;background:#0b0f16ee;backdrop-filter:blur(8px);
border-top:1px solid var(--border);padding:14px 24px}
.bar .inner{max-width:860px;margin:0 auto;display:flex;gap:12px;align-items:center}
button{background:var(--accent);color:#0b0f16;border:0;border-radius:8px;padding:10px 16px;font-size:14px;font-weight:700;cursor:pointer}
button.ghost{background:transparent;color:var(--accent);border:1px solid var(--accent)}
#status{font-size:13px}.ok{color:var(--accent2)}.err{color:var(--danger)}
"""

SCRIPT = """
const RADIOS = %s;
function val(name){
  const r = document.querySelector('input[name="'+name+'"]:checked');
  if (r) return r.value;
  const el = document.querySelector('[name="'+name+'"]');
  return el ? el.value.trim() : "";
}
async function submitAll(){
  const data = {answers:{}, comments:{}, text:{}, notes: val("notes")};
  for (const q of RADIOS){ data.answers[q]=val(q); data.comments[q]=val("c_"+q); }
  document.querySelectorAll('[data-text]').forEach(el=>{ data.text[el.name]=el.value.trim(); });
  const s=document.getElementById('status');
  try{
    const res=await fetch('/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
    if(!res.ok) throw new Error('HTTP '+res.status);
    s.className='ok'; s.textContent='Sent to Claude \\u2713 \\u2014 close this tab and return to the chat.';
  }catch(e){ s.className='err'; s.textContent='Failed to send ('+e.message+'). Is the local server still running?'; }
}
"""


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def render_question(q: dict, radio_ids: list[str]) -> str:
    qid = q["id"]
    qtype = q.get("type", "radio")
    star = f'<span class="star">{"⭐" * int(q.get("star", 0))}</span>' if q.get("star") else ""
    num = f'<span class="num">{esc(q["num"])}</span>' if q.get("num") else ""
    head = f'<div class="head">{num}{star}<span class="title">{esc(q["title"])}</span></div>'
    sub = f'<div class="sub">{esc(q["sub"])}</div>' if q.get("sub") else ""

    if qtype == "radio":
        radio_ids.append(qid)
        opts = []
        for o in q["options"]:
            checked = " checked" if o.get("default") else ""
            tag = '<span class="default">DEFAULT</span>' if o.get("default") else ""
            opts.append(
                f'<label class="opt"><input type="radio" name="{esc(qid)}" value="{esc(o["value"])}"{checked}>'
                f'<span class="txt">{esc(o["label"])}{tag}</span></label>'
            )
        body = f'<div class="opts">{"".join(opts)}</div>'
    elif qtype == "text":
        ph = esc(q.get("placeholder", ""))
        body = f'<input type="text" name="{esc(qid)}" data-text placeholder="{ph}">'
    elif qtype == "textarea":
        ph = esc(q.get("placeholder", ""))
        rows = int(q.get("rows", 3))
        body = f'<textarea class="cmt" name="{esc(qid)}" data-text rows="{rows}" placeholder="{ph}"></textarea>'
    else:
        raise ValueError(f"unknown question type: {qtype}")

    comment = ""
    if q.get("comment"):
        comment = (
            f'<label class="cmt-lbl">Comment</label><textarea class="cmt" name="c_{esc(qid)}" rows="1"></textarea>'
        )
    return f'<div class="q">{head}{sub}{body}{comment}</div>'


def render(spec: dict) -> str:
    radio_ids: list[str] = []
    groups_html = []
    for g in spec.get("groups", []):
        qs = "".join(render_question(q, radio_ids) for q in g["questions"])
        gh = f"<h2>{esc(g['name'])}</h2>" if g.get("name") else ""
        groups_html.append(f'<div class="group">{gh}{qs}</div>')

    # trailing free-text overrides box (name="notes")
    notes = (
        '<div class="q"><div class="head"><span class="title">Anything else / overrides</span></div>'
        '<textarea class="cmt" name="notes" rows="3" placeholder="Free-text: constraints, concerns, things not asked…"></textarea></div>'
    )
    script = SCRIPT % json.dumps(radio_ids)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(spec.get("title", "Decisions"))}</title>
<style>{STYLE}</style></head><body>
<header><h1>{esc(spec.get("title", "Decisions"))}</h1><p>{esc(spec.get("intro", ""))}</p></header>
<div class="wrap"><form id="f">{"".join(groups_html)}{notes}</form></div>
<div class="bar"><div class="inner">
<button type="button" onclick="submitAll()">Submit to Claude</button>
<button type="button" class="ghost" onclick="location.reload()">Reset</button>
<span id="status"></span></div></div>
<script>{script}</script></body></html>"""


def make_handler(page: bytes, out_path: Path):
    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="text/html"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, page)
            else:
                self._send(404, b"not found")

        def do_POST(self):
            if self.path != "/submit":
                self._send(404, b"not found")
                return
            n = int(self.headers.get("Content-Length", 0))
            out_path.write_bytes(self.rfile.read(n))
            print("ANSWERS_RECEIVED", flush=True)
            self._send(200, json.dumps({"ok": True}).encode(), "application/json")

        def log_message(self, format, *args):  # noqa: A002 - silence access log
            pass

    return H


def main() -> int:
    ap = argparse.ArgumentParser(description="Serve an interactive decision form from a JSON spec.")
    ap.add_argument("spec", type=Path, help="path to the questions spec JSON")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--out", type=Path, default=Path("/tmp/answers.json"))
    ap.add_argument("--open", action="store_true", help="open the form in the default browser")
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text())
    page = render(spec).encode()
    args.out.unlink(missing_ok=True)

    handler = make_handler(page, args.out)
    server = HTTPServer(("127.0.0.1", args.port), handler)
    url = f"http://localhost:{args.port}/"
    print(f"serving {url} -> writes {args.out}", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
