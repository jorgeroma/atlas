#!/usr/bin/env python3
"""Generate index.html: one card per artifact in atlas/*.html.

Card text comes from each file's <title> and <meta name="description">.
"""
from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "atlas"


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.desc, self._in_title = "", "", False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title" and not self.title:
            self._in_title = True
        elif tag == "meta" and (a.get("name") or "").lower() == "description" and not self.desc:
            self.desc = a.get("content") or ""

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def read_meta(path):
    p = Head()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    title = " ".join(p.title.split()) or path.stem.replace("-", " ").replace("_", " ").title()
    return title, " ".join(p.desc.split())


def card(path):
    title, desc = read_meta(path)
    desc_html = f"<p>{escape(desc)}</p>" if desc else ""
    return (
        f'<a class="card" href="atlas/{escape(path.name)}">'
        f"<h2>{escape(title)}</h2>{desc_html}<span>{escape(path.stem)} →</span></a>"
    )


PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atlas</title>
<style>
:root {{ --bg:#f7f7f5; --fg:#1b1b1b; --muted:#666; --card:#fff; --line:#e3e3df; --accent:#3b5bdb; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#141414; --fg:#ececec; --muted:#9a9a9a; --card:#1e1e1e; --line:#2e2e2e; --accent:#8ea2ff; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, sans-serif; }}
main {{ max-width:960px; margin:0 auto; padding:48px 16px; }}
h1 {{ margin:0 0 4px; font-size:2rem; }}
header p {{ margin:0 0 32px; color:var(--muted); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(min(100%, 260px), 1fr)); gap:16px; }}
.card {{ display:flex; flex-direction:column; gap:8px; padding:20px; background:var(--card);
  border:1px solid var(--line); border-radius:12px; color:inherit; text-decoration:none; }}
.card:hover, .card:focus-visible {{ border-color:var(--accent); }}
.card h2 {{ margin:0; font-size:1.15rem; }}
.card p {{ margin:0; color:var(--muted); font-size:.95rem; }}
.card span {{ margin-top:auto; color:var(--accent); font-size:.9rem; }}
</style>
</head>
<body>
<main>
<header><h1>Atlas</h1><p>{count} guías</p></header>
<nav class="grid">
{cards}
</nav>
</main>
</body>
</html>
"""


def main():
    files = sorted(SRC.glob("*.html"), key=lambda p: read_meta(p)[0].lower())
    out = PAGE.format(count=len(files), cards="\n".join(card(f) for f in files))
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html: {len(files)} artifacts")


if __name__ == "__main__":
    main()
