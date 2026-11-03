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
    const style = document.createElement('style');
    // Each page names its tokens differently; the fallbacks cover all of them.
    style.textContent = `.theme-toggle{position:fixed;z-index:20;right:max(16px,env(safe-area-inset-right,0px));bottom:max(16px,env(safe-area-inset-bottom,0px));width:44px;height:44px;display:grid;place-items:center;border-radius:50%;border:1px solid var(--line);background:var(--surface,var(--card));color:var(--ink,var(--fg));font:20px/1 system-ui,sans-serif;cursor:pointer;box-shadow:0 2px 10px rgb(0 0 0/.15)}.theme-toggle:hover{border-color:var(--accent)}.theme-toggle:focus-visible{outline:2px solid var(--accent);outline-offset:2px}`;
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
    document.body.append(btn);
  });
})();
