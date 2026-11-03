#!/usr/bin/env python3
"""Generate index.html: one entry per artifact in atlas/*.html.

Entry text comes from each file's <title> and <meta name="description">.
Progress comes at runtime from localStorage["atlas-progress"], written by
atlas.js when a guide calls atlasProgress().
"""
import math
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


def entry(path):
    title, desc = read_meta(path)
    desc_html = f"<p>{escape(desc)}</p>" if desc else ""
    return (
        f'<li><a class="guide" href="atlas/{escape(path.name)}" data-guide="{escape(path.stem)}">'
        f'<div class="guide-text"><h2>{escape(title)}</h2>{desc_html}</div>'
        f'<div class="guide-progress"><div class="scale" aria-hidden="true"></div>'
        f'<p class="status">Sin empezar</p></div></a></li>'
    )


def contours(rings=12, w=640, h=480):
    """Topographic contour lines: wobbly concentric rings, every 5th one an index contour."""
    cx, cy = w * 0.58, h * 0.52
    out = []
    for i in range(1, rings + 1):
        r = 19 * i
        pts = []
        for k in range(97):
            a = k / 96 * math.tau
            rr = r * (1 + 0.17 * math.sin(3 * a + i * 0.33) + 0.07 * math.sin(5 * a - i * 0.5))
            pts.append(f"{cx + rr * math.cos(a) * 1.3:.1f},{cy + rr * math.sin(a):.1f}")
        cls = ' class="index"' if i % 5 == 0 else ""
        out.append(f'<path{cls} d="M{" L".join(pts)}Z"/>')
    return f'<svg class="topo" viewBox="0 0 {w} {h}" aria-hidden="true" focusable="false">{"".join(out)}</svg>'


PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Atlas</title>
<meta name="description" content="Guías de estudio interactivas en español.">
<script src="atlas.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
/* Cartographic landing: contour lines behind the wordmark, a map scale bar as each guide's progress. */
:root {
  color-scheme: light;
  --paper: #EDF1EE; --surface: #F8FAF8; --ink: #17232A; --muted: #56666C; --line: #CCD6D2;
  --accent: #1F5E8A; --accent-ink: #FFFFFF; --contour: #B89773;
  --f-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --f-body: "IBM Plex Sans", "Segoe UI", system-ui, -apple-system, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --paper: #10171A; --surface: #172024; --ink: #E2E9E6; --muted: #93A3A8; --line: #27343A;
    --accent: #82B8DD; --accent-ink: #0B1A24; --contour: #6E5C45;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --paper: #10171A; --surface: #172024; --ink: #E2E9E6; --muted: #93A3A8; --line: #27343A;
  --accent: #82B8DD; --accent-ink: #0B1A24; --contour: #6E5C45;
}
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink); font: 17px/1.6 var(--f-body); -webkit-font-smoothing: antialiased; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 4px; }
.wrap { max-width: 920px; margin: 0 auto; padding-left: max(20px, env(safe-area-inset-left)); padding-right: max(20px, env(safe-area-inset-right)); }

/* hero */
.hero { position: relative; isolation: isolate; overflow: hidden; padding-block: clamp(48px, 11vw, 112px) clamp(32px, 6vw, 56px); }
.theme-slot { position: absolute; z-index: 1; top: 16px; right: max(20px, env(safe-area-inset-right), calc((100% - 920px) / 2 + 20px)); }
.topo { position: absolute; top: 50%; right: -8%; width: min(720px, 110%); height: auto; transform: translateY(-50%); z-index: -1; }
.topo path { fill: none; stroke: var(--contour); stroke-width: .9; opacity: .55; }
.topo path.index { stroke-width: 1.8; opacity: .8; }
.hero h1 { font: 800 clamp(4.5rem, 17vw, 10rem)/.82 var(--f-display); letter-spacing: -.045em; margin: 0 0 20px; }
.hero p { margin: 0; max-width: 34ch; font-size: clamp(1.05rem, 2.4vw, 1.25rem); color: var(--muted); }

/* resume */
.resume { display: grid; gap: 2px; margin-bottom: 48px; padding: 20px 24px; border-radius: 14px; background: var(--accent); color: var(--accent-ink); text-decoration: none; }
.resume[hidden] { display: none; }
.resume span { font-size: .95rem; opacity: .85; }
.resume strong { font: 700 clamp(1.35rem, 3.6vw, 1.75rem)/1.15 var(--f-display); }
.resume small { font-size: .95rem; opacity: .85; }
.resume:hover strong { text-decoration: underline; text-underline-offset: 4px; text-decoration-thickness: 2px; }

/* guides */
.guides { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
.guide { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: 16px 40px; align-items: center; padding: 24px; border-radius: 14px; background: var(--surface); border: 1px solid var(--line); text-decoration: none; }
.guide:hover { border-color: var(--accent); }
.guide:hover h2 { color: var(--accent); }
.guide h2 { margin: 0 0 6px; font: 700 clamp(1.3rem, 3vw, 1.6rem)/1.15 var(--f-display); letter-spacing: -.01em; text-wrap: balance; }
.guide-text p { margin: 0; color: var(--muted); font-size: .95rem; max-width: 60ch; }
@media (max-width: 720px) { .guide { grid-template-columns: minmax(0, 1fr); padding: 20px; } }

/* map scale bar: ten segments, filled up to --p */
.scale { --p: 0%; height: 12px; border: 1.5px solid var(--ink); border-radius: 2px;
  background:
    repeating-linear-gradient(90deg, transparent 0 calc(10% - 1.5px), var(--ink) calc(10% - 1.5px) 10%),
    linear-gradient(90deg, var(--accent) var(--p), transparent var(--p)); }
.status { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin: 8px 0 0; font-size: .88rem; color: var(--muted); font-variant-numeric: tabular-nums; }
.status b { color: var(--ink); font-weight: 600; }

footer { padding-block: 56px max(80px, env(safe-area-inset-bottom)); color: var(--muted); font-size: .9rem; }
footer p { margin: 0; }
footer a { color: var(--accent); text-underline-offset: 3px; }
</style>
</head>
<body>
<header class="hero">
  <span class="theme-slot" data-atlas-theme></span>
  <!--TOPO-->
  <div class="wrap">
    <h1>Atlas</h1>
    <p>Guías de estudio interactivas, de cero a nivel de trabajo: explicación, animaciones, código y ejercicios.</p>
  </div>
</header>
<main class="wrap">
  <a class="resume" id="resume" hidden href="#"><span>Continuar con</span><strong></strong><small></small></a>
  <ul class="guides">
<!--GUIDES-->
  </ul>
</main>
<footer class="wrap">
  <p>Tu progreso se guarda solo en este navegador. <a href="https://github.com/jorgeroma/atlas">Código en GitHub</a></p>
</footer>
<script>
(() => {
  let all = {};
  try { all = JSON.parse(localStorage.getItem('atlas-progress')) || {}; } catch { /* no progress to show */ }
  const rtf = new Intl.RelativeTimeFormat('es', { numeric: 'auto' });
  const ago = (t) => rtf.format(Math.round((t - Date.now()) / 864e5), 'day');
  let last = null;
  for (const a of document.querySelectorAll('.guide')) {
    const p = all[a.dataset.guide];
    if (!p || !(p.total > 0)) continue;
    const pct = Math.min(100, Math.max(0, p.done / p.total * 100));
    a.querySelector('.scale').style.setProperty('--p', pct + '%');
    a.querySelector('.status').innerHTML = '';
    const count = document.createElement('span');
    count.innerHTML = '<b></b>';
    count.firstChild.textContent = `${p.done} de ${p.total}`;
    count.append(` ${p.unit}`);
    const seen = document.createElement('span');
    seen.textContent = `Visitada ${ago(p.at)}`;
    a.querySelector('.status').append(count, seen);
    if (!last || p.at > last.p.at) last = { a, p };
  }
  if (last) {
    const r = document.getElementById('resume');
    r.href = last.a.getAttribute('href');
    r.querySelector('strong').textContent = last.a.querySelector('h2').textContent;
    r.querySelector('small').textContent = last.p.done
      ? `Llevas ${last.p.done} de ${last.p.total} ${last.p.unit}`
      : `Visitada ${ago(last.p.at)}`;
    r.hidden = false;
  }
})();
</script>
</body>
</html>
"""


def main():
    files = sorted(SRC.glob("*.html"), key=lambda p: read_meta(p)[0].lower())
    out = PAGE.replace("<!--TOPO-->", contours()).replace("<!--GUIDES-->", "\n".join(entry(f) for f in files))
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html: {len(files)} artifacts")


if __name__ == "__main__":
    main()
