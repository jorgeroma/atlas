// Shared helpers for index.html and every guide. Load synchronously in <head>.

// Progress summary for the landing page. Guides call
// atlasProgress(done, total, unit) on load and whenever progress changes;
// index.html reads localStorage["atlas-progress"][<file stem>].
window.atlasProgress = (done, total, unit) => {
  const id = location.pathname.split('/').pop().replace(/\.html$/, '');
  try {
    const all = JSON.parse(localStorage.getItem('atlas-progress')) || {};
    all[id] = { done, total, unit, at: Date.now() };
    localStorage.setItem('atlas-progress', JSON.stringify(all));
  } catch { /* storage unavailable: the landing page just shows no progress */ }
};

// Guides that choose their view in JS mark <html data-atlas-routing> and call
// atlasRouted() once the view is set. Until then the page stays hidden, so it never
// paints the default view and then jumps. Window load reveals it as a safety net.
if (document.documentElement.hasAttribute('data-atlas-routing')) {
  const hide = document.createElement('style');
  hide.textContent = 'body{visibility:hidden}';
  document.head.append(hide);
  window.atlasRouted = () => hide.remove();
  addEventListener('load', window.atlasRouted);
}

// Light/dark toggle. Loaded in <head> so the saved theme applies before first paint.
// Pages style themes with :root[data-theme="light|dark"]; no attribute = follow the OS.
// The choice lives in a cookie scoped to this file's directory (the site root),
// so the landing page and all guides share it.
(() => {
  const root = document.documentElement;
  const path = new URL('.', document.currentScript.src).pathname;
  const saved = document.cookie.match(/(?:^|;\s*)atlas-theme=(light|dark)/)?.[1];
  if (saved) root.dataset.theme = saved;

  const osDark = matchMedia('(prefers-color-scheme: dark)');
  const isDark = () => (root.dataset.theme || (osDark.matches ? 'dark' : 'light')) === 'dark';

  addEventListener('DOMContentLoaded', () => {
    // Each page places the button by providing an element with [data-atlas-theme];
    // without one there is no button, but the saved theme still applies.
    const slot = document.querySelector('[data-atlas-theme]');
    if (!slot) return;
    const style = document.createElement('style');
    // Each page names its tokens differently; the fallbacks cover all of them.
    style.textContent = `.theme-toggle{flex:none;width:40px;height:40px;padding:0;display:grid;place-items:center;border-radius:50%;border:1px solid var(--line);background:var(--surface,var(--card));color:var(--ink,var(--fg));font:18px/1 system-ui,sans-serif;cursor:pointer}.theme-toggle:hover{border-color:var(--accent)}.theme-toggle:focus-visible{outline:2px solid var(--accent);outline-offset:2px}`;
    document.head.append(style);

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'theme-toggle';
    const paint = () => {
      const dark = isDark();
      btn.textContent = dark ? '☀' : '☾';
      btn.title = dark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro';
      btn.setAttribute('aria-label', btn.title);
    };
    btn.addEventListener('click', () => {
      const next = isDark() ? 'light' : 'dark';
      root.dataset.theme = next;
      document.cookie = `atlas-theme=${next}; path=${path}; max-age=31536000; SameSite=Lax`;
      paint();
    });
    osDark.addEventListener('change', paint);
    paint();
    slot.append(btn);
  });
})();

// Reading progress: a thin bar pinned to the bottom edge, guides only. Colour is
// --accent; a page whose accent is neutral can set --atlas-scroll on :root instead.
// (the landing page sits next to this file; guides live one folder down).
(() => {
  if (new URL('.', document.currentScript.src).pathname === new URL('.', location.href).pathname) return;
  addEventListener('DOMContentLoaded', () => {
    const bar = document.createElement('div');
    bar.setAttribute('aria-hidden', 'true');
    bar.style.cssText = 'position:fixed;left:0;right:0;bottom:0;height:4px;z-index:2147483647;pointer-events:none;background:var(--atlas-scroll,var(--accent,currentColor));transform-origin:left;transform:scaleX(0)';
    document.body.append(bar);
    let queued = false;
    const update = () => {
      queued = false;
      const max = document.documentElement.scrollHeight - innerHeight;
      bar.style.transform = `scaleX(${max > 0 ? Math.min(scrollY / max, 1) : 0})`;
    };
    const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
    addEventListener('scroll', queue, { passive: true });
    new ResizeObserver(queue).observe(document.body); // tabs/accordions change height without scrolling
    update();
  });
})();
