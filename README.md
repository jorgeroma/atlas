# Atlas

A collection of interactive, self-contained study guides, each one a single HTML file. A landing page links to all of them.

**Live site:** https://jorgeroma.github.io/atlas/

> **Note:** the guides are written in Spanish.

## Guides

| Guide | What it covers |
|-------|----------------|
| [Patrones LeetCode](https://jorgeroma.github.io/atlas/atlas/leetcode.html) | 24 algorithm patterns for coding interviews, ordered by frequency vs. effort. Each pattern has its core idea, recognition signals, complexity, a step-by-step visualization, Python and TypeScript code, common mistakes and 9 practice problems. Includes a mixed quiz, a timed mock interview and a "which pattern?" decision tree. |
| [Terraform desde cero](https://jorgeroma.github.io/atlas/atlas/terraform-desde-cero.html) | Terraform from zero to working level: infrastructure as code, HCL, the init/plan/apply lifecycle, providers and resources, variables, state, loops and functions, modules, remote backends, testing and security, CI/CD, and a final project deploying a website on AWS. Ends with a command cheat sheet and glossary. |

Progress (solved problems, quiz results, completed sections) is saved in your browser's `localStorage`. Nothing is sent to any server.

## How it works

```
atlas/                      one HTML file per guide
build.py                    generates index.html from atlas/*.html
atlas.js                    shared by every page: light/dark toggle and progress summary
.github/workflows/pages.yml builds and deploys to GitHub Pages on every push to main
```

`build.py` reads each guide's `<title>` and optional `<meta name="description">` and renders one card per file. It uses only the Python standard library. `index.html` is generated, so it is not committed.

## Adding a guide

1. Put the file in `atlas/`, e.g. `atlas/kubernetes.html`. The file name becomes its URL.
2. Give it a `<title>`, and optionally a `<meta name="description" content="...">` for the card subtitle.
3. If it stores data in `localStorage`, use a key unique to that guide. All guides share the same origin.
4. For the shared light/dark toggle, add `<script src="../atlas.js"></script>` inside `<head>` and style the dark theme under `:root[data-theme="dark"]` (plus `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { … } }` for the OS default). Place the toggle button with an element marked `data-atlas-theme` (e.g. `<span data-atlas-theme></span>` in the header); without it the saved theme still applies but no button is shown. The choice is saved in the `atlas-theme` cookie, shared by every page.
5. To show progress on the landing page, call `window.atlasProgress?.(done, total, 'unit')` on load and whenever progress changes (e.g. `'bloques'`, `'problemas'`).
6. If the guide picks its view in JavaScript (tabs, one section per view, restoring the last position), add `data-atlas-routing` to `<html>` and call `window.atlasRouted?.()` once the view is set, so the page is not painted before it jumps there.
7. Push to `main`. The landing page updates on its own.

## Run locally

```bash
git clone https://github.com/jorgeroma/atlas.git
cd atlas
python3 build.py
python3 -m http.server
```

Then open http://localhost:8000.

## Deploying a fork

In the repository go to **Settings → Pages → Build and deployment → Source** and select **GitHub Actions**. With "Deploy from a branch", Pages skips `build.py` and shows this README instead of the landing page.
