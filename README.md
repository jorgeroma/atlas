# Atlas

Hub for self-contained HTML study guides, published with GitHub Pages.

## Add a guide

1. Drop the file in `atlas/` (e.g. `atlas/kubernetes.html`).
2. Push to `main`. The workflow runs `build.py`, which regenerates `index.html` with one card per file, and deploys.

Card title comes from the file's `<title>`; the optional subtitle from `<meta name="description" content="...">`.

## Local preview

```bash
python3 build.py && python3 -m http.server
```

`index.html` is generated, so it is git-ignored.

## One-time setup

Repo **Settings → Pages → Source: GitHub Actions**.
