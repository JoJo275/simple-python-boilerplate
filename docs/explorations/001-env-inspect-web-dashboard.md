# Exploration 001: Environment Inspection Web Dashboard

## Status

Draft

## Problem Statement

`scripts/env_inspect.py` provides a comprehensive CLI dashboard covering
Python info, git status, venv detection, installed packages, entry points,
build tools, PATH inspection, Python installations, and system environment.
The output is rich but confined to the terminal — long tables scroll off
screen, cross-referencing sections requires scrolling, and the data can't
be filtered, searched, or bookmarked interactively.

A local web dashboard would present the same data in a navigable,
filterable, visually structured interface — useful for onboarding,
debugging environment issues, and getting a quick "health check" view
without memorising CLI flags.

## Why This Might Matter

- **Onboarding:** New contributors get a single URL that shows everything
  about their local setup, with guidance on what's wrong and how to fix it.
- **Debugging:** When something breaks, a filterable, colour-coded dashboard
  is faster than scrolling terminal output. Tables can be sorted by status,
  outdated packages highlighted, duplicate entries grouped.
- **Diagnostics:** Complements the existing `doctor.py` / `env_doctor.py`
  family — those check rules, this _shows state_. Together they answer
  "what do I have?" and "is it correct?".
- **Cost of inaction:** Low — the CLI works fine. But the web version adds
  meaningful UX for a small incremental effort.

## Alternatives

### Option 1: Jinja + htmx + CSS + minimal JS (recommended)

Serve a Python HTTP server locally, render templates with Jinja2, use htmx
for interactive behaviour (lazy-load slow sections, refresh data, expand/
collapse), and plain CSS for layout.

**Pros:**

- Pure Python backend — no Node.js toolchain, no npm, no bundler
- htmx gives SPA-like interactivity with zero JS framework overhead
- Jinja2 is already a transitive dependency of MkDocs (already in the env)
- Lightweight: the entire frontend is HTML templates + one CSS file + a
  few htmx attributes
- Aligns with the project's "minimal tooling" philosophy
- Easy to extend: add a new section = add a Jinja partial + a route

**Cons:**

- htmx is a CDN/vendored JS dependency (≈14 KB min+gzip) — though it can
  be vendored as a single file in the repo
- CSS-only styling limits chart/graph visualisations (but we don't need
  charts for this use case — tables and key-value grids suffice)
- Less familiar to developers who expect React/Vue patterns

### Option 2: Flask / FastAPI + full frontend framework (React, Vue, Svelte)

Use a proper ASGI/WSGI framework with a JS SPA for the frontend.

**Pros:**

- Maximum flexibility for rich interactivity
- Large ecosystem and community support

**Cons:**

- Massive tooling overhead: Node.js, npm, bundler, framework boilerplate
- Adds a JS build step to a Python-focused project
- overkill for a local diagnostic tool
- Template users who don't want the app still inherit the JS toolchain

**Rejected as primary approach.** Disproportionate complexity for a local
inspection tool.

### Option 3: Rich Live / Textual TUI

Use Rich's Live display or the Textual framework for a terminal-based
interactive dashboard.

**Pros:**

- Stays entirely in the terminal — no browser needed
- Pure Python, no web stack at all
- Textual supports tables, tabs, scrolling, search

**Cons:**

- Terminal-only; can't bookmark, can't share a link
- Textual is a heavyweight dependency (~5 MB) with its own API surface
- Limited layout flexibility vs. HTML+CSS
- Doesn't solve the "show someone your environment state" use case

**Worth considering as a complementary option**, but doesn't replace the
web dashboard.

### Option 4: Static HTML export (no server)

Generate a standalone `.html` file with all data inlined. Open in browser.

**Pros:**

- No server process needed
- File can be shared, attached to issues

**Cons:**

- No interactivity (filtering, lazy-loading, refresh)
- Every inspection generates a new file — workspace clutter
- Stale the moment it's generated

**Could be a useful secondary feature** (export mode), not the primary
interface.

### Option 5: Do nothing

Keep `env_inspect.py --json` and `env_inspect.py --section <name>` as-is.

**Pros:**

- Zero effort
- CLI already works well

**Cons:**

- Misses UX improvements for onboarding and debugging
- Long terminal output remains hard to navigate

## Proposed Repo Layout

The app should live **outside `src/`** since it's a developer tool, not
part of the distributed package. Template users who don't want it can
delete the directory without affecting the core package.

```
tools/
└── dev-tools/
    └── env-dashboard/
        ├── __init__.py
        ├── app.py              ← Entry point: starts Uvicorn server
        ├── collector.py        ← Gathers env data (extracted from env_inspect.py)
        ├── routes.py           ← Route handlers, returns rendered templates
        ├── static/
        │   ├── css/
        │   │   ├── pico.min.css  ← Vendored Pico CSS base
        │   │   └── style.css     ← Dashboard overrides and custom properties
        │   ├── js/
        │   │   ├── htmx.min.js   ← Vendored htmx (~14 KB)
        │   │   ├── alpine.min.js ← Vendored Alpine.js (~15 KB)
        │   │   └── chart.min.js  ← Vendored Chart.js (~65 KB, load only where needed)
        │   └── img/              ← Optional: icons, favicon
        ├── templates/
        │   ├── base.html       ← Layout shell (nav, footer, script tags)
        │   ├── index.html      ← Main dashboard page
        │   └── partials/       ← htmx-swappable fragments
        │       ├── python.html
        │       ├── git.html
        │       ├── venv.html
        │       ├── packages.html
        │       ├── entrypoints.html
        │       ├── build_tools.html
        │       ├── python_support.html
        │       ├── path.html
        │       ├── python_installs.html
        │       └── system.html
        └── README.md           ← Usage, development instructions
```

**Why `tools/dev-tools/` and not `scripts/`?** `scripts/` is for
single-file CLI utilities. The env-dashboard is a multi-file application
with its own templates, static assets, and internal structure. The
`tools/dev-tools/` path makes the purpose explicit — this is a template
repo, so clarity matters more than brevity. Template users scanning the
repo tree immediately understand what lives here. The extra nesting also
leaves room for sibling directories under `tools/` (e.g., `tools/ci/`,
`tools/release/`) without overloading one flat folder.

**Data sharing with `env_inspect.py`:** The `collector.py` module can
import and reuse the gathering functions from `env_inspect.py` (which
already returns structured dicts via `gather_env_info()`), or the data
collection logic can be extracted into a shared module. The CLI stays
as-is — the web app is an alternative view of the same data.

## Technology Details

### Backend

- **FastAPI** or **Starlette** as the backend framework. FastAPI is the
  natural choice: it's already in the Python ecosystem, gives you async
  route handlers, automatic OpenAPI docs, and clean dependency injection.
  Yes, FastAPI _is_ the backend — it handles HTTP routing, serves the
  Jinja2 templates, and exposes the data-collection endpoints. No
  separate "backend" is needed beyond it.
- **Uvicorn** as the ASGI server. Uvicorn is the standard way to run
  FastAPI/Starlette apps — lightweight, fast, pure-Python, and supports
  `--reload` for development. It's the default recommendation in the
  FastAPI docs and adds no conceptual overhead. Install it alongside
  FastAPI (often via `fastapi[standard]` which bundles Uvicorn). For a
  local dev tool the built-in Uvicorn invocation (`uvicorn app:app
  --reload --host 127.0.0.1 --port 8000`) is all you need — no process
  manager, no Gunicorn, no reverse proxy.
- Alternatively, Python stdlib `http.server` works for a zero-dependency
  start, but if routing gets beyond ~5 routes or you want async data
  collection (fetching slow package info without blocking), FastAPI +
  Uvicorn earns its keep quickly.
- **Jinja2** for templating — already available via MkDocs dependency.
  Add as an explicit optional dependency in `pyproject.toml` under a
  `[project.optional-dependencies] dashboard` group.
- Data collection reuses `gather_env_info()` from `env_inspect.py`.

### Frontend

### Frontend

- **htmx** (vendored, ~14 KB): handles lazy-loading of slow sections
  (e.g., outdated package checks), refresh-in-place, and expand/collapse
  without writing JS handlers.
- **Alpine.js** (vendored, ~15 KB min+gzip): tiny reactive JS framework
  for client-side state that htmx doesn't cover — search/filter input
  binding, toggle/accordion state, tab switching, dropdown menus. Uses
  declarative HTML attributes (`x-data`, `x-show`, `x-on`) so it reads
  like htmx and requires no build step. Alpine and htmx complement each
  other cleanly: htmx owns server communication, Alpine owns local UI
  state. Only reach for Alpine when the interaction is purely client-side
  and doesn't need a server round-trip.
- **Chart.js** (vendored or CDN, ~65 KB min+gzip): canvas-based charting
  library for data visualisations where tables aren't enough — e.g.,
  package distribution by location (pie/doughnut), dependency freshness
  over time (bar), Python version coverage matrix (horizontal bar), or
  PATH entry counts. Simple API, sensible defaults, responsive out of the
  box. Only include Chart.js on pages/sections that actually render a
  chart — don't load it globally if most sections are pure tables.
- **CSS**: Custom stylesheet. Start with a clean, minimal design. CSS
  custom properties for theming.  Consider classless CSS frameworks
  (Pico CSS, Simple.css, MVP.css) as a starting base — they style
  semantic HTML with zero class annotations and weigh <10 KB.
- **Minimal additional JS**: Only for behaviour that htmx + Alpine can't
  handle (e.g., clipboard API for copy-to-clipboard). No framework, no
  build step, no npm. **Use minimal JavaScript unless it adds a feature
  or idea worth having** — one of the reasons a web app makes sense here
  is the amount of information to display is too heavy for a terminal
  view, but the interactivity budget should stay small. If a feature can
  be done with htmx attributes, Alpine directives, or CSS, do it that
  way.

### Sections (mirroring env_inspect.py)

| Section             | Data source              | Notes                                  |
| :------------------ | :----------------------- | :------------------------------------- |
| Python              | `_python_info()`         | Version, executable, venv status       |
| Python Installations| `_find_python_installations()` | All Pythons on system           |
| Git                 | `_git_info()`            | Version, path                          |
| Virtual Environment | Python info subset       | Active venv details                    |
| Hatch               | `_hatch_info()`          | Env list, version                      |
| Packages            | `_all_installed_packages()` | Grouped by location, outdated flag  |
| Entry Points        | `_collect_entry_points()` | Console/GUI scripts                   |
| Build Tools         | `_detect_build_tools()`  | Tools on PATH                          |
| Python Support      | `_check_python_support_summary()` | Version consistency       |
| PATH                | `_inspect_path()`        | Dirs, duplicates, executable counts    |
| System              | `_system_env_summary()`  | OS, hostname, encoding                 |

### Interactive features via htmx

- **Lazy-load slow sections:** Package outdated check (runs `pip list
  --outdated`) is slow. Load the page immediately, then htmx-trigger the
  outdated check in the background and swap in results.
- **Refresh button per section:** `hx-get="/section/packages"
  hx-target="#packages"` — re-collect and re-render just that section.
- **Expand/collapse details:** Package list grouped by location, each
  group collapsible. Alpine.js `x-show` / `x-data` handles the toggle
  state client-side — no server round-trip needed.
- **Search/filter:** Alpine.js `x-model` on an input bound to a filtered
  list — instant client-side filtering across package tables (~10 lines
  of Alpine directives, zero custom JS).
- **Chart rendering:** Chart.js canvases for visual sections (package
  distribution, PATH entry counts). Alpine.js `x-init` can trigger chart
  initialisation when the section loads via htmx.

### Technology Stack Summary

All tools for the web dashboard in one table. "Vendored" means checked
into the repo as a single file — no CDN dependency, no npm, no build
step.

| Tool | Category | What It Does | Why Use It Here |
| :--- | :------- | :----------- | :-------------- |
| **FastAPI** | Backend — framework | ASGI web framework: routing, dependency injection, async endpoints | Clean route declarations, native async (critical for slow subprocess calls), auto OpenAPI docs for the REST-like section endpoints, Jinja2 integration built-in |
| **Uvicorn** | Backend — server | ASGI server that runs the FastAPI app | The standard FastAPI server; lightweight, fast, pure-Python; `--reload` for dev; hardcode `--host 127.0.0.1` for local-only binding |
| **Jinja2** | Backend — templating | Server-side HTML template rendering with inheritance and partials | Already a transitive dep (MkDocs); proven and well-documented; partials map 1:1 to htmx fragment endpoints; `autoescape=True` for safe rendering of arbitrary env-var values |
| **htmx** | Frontend — interactivity | HTML-over-the-wire: AJAX, lazy-loading, partial page updates via HTML attributes | SPA-like UX with zero JS framework overhead; lazy-load slow sections, refresh-in-place, swap HTML fragments; ~14 KB vendored; no build step |
| **Alpine.js** | Frontend — client-side state | Minimal reactive JS framework for local UI interactions | Client-side search/filter binding, toggle/accordion state, tab switching, dropdown menus; ~15 KB vendored; declarative HTML attributes (`x-data`, `x-show`, `x-model`) — reads like htmx; no build step |
| **Chart.js** | Frontend — data visualisation | Canvas-based charting library (bar, pie, doughnut, line, etc.) | Visual graphs for package distribution by location, dependency freshness, Python version coverage, PATH entry counts; ~65 KB min+gzip; simple API, responsive, good defaults; only load on pages that render charts |
| **Pico CSS** | Frontend — styling | Classless CSS framework for semantic HTML | Clean typography, tables, cards, dark/light mode with zero class annotations; <10 KB; styles `<table>`, `<article>`, `<nav>` directly; rapid prototyping without writing CSS from scratch |
| **Custom CSS** | Frontend — styling | Project-specific dashboard styles and theming | CSS custom properties for colour theming, dashboard grid layouts, status-colour tokens (green/amber/red for health indicators), overrides on top of Pico CSS base |
| **djLint** | Tooling — linting | Jinja/HTML template linter and formatter | Catches unclosed tags, malformed Jinja blocks, attribute ordering issues; single Python package (`pip install djlint`), no Node.js; add as pre-commit hook when templates exceed ~20 files |
| **Prettier** | Tooling — formatting | Code formatter for CSS (already in project) | Already available via pre-commit; extend existing file patterns to cover `.css` files — trivial config change |
| **Biome** | Tooling — linting | Fast JS linter and formatter (Rust binary) | Single binary, zero npm dep; add when JS exceeds ~200 lines or spans multiple files; handles JS + JSON + CSS in one tool |

### Additional Recommendations

Tools not in the core stack but worth considering as the dashboard
evolves:

| Tool | Category | What It Does | When to Add |
| :--- | :------- | :----------- | :---------- |
| **htmx SSE extension** | Frontend — real-time | Server-Sent Events via htmx attributes | If you want live-updating sections (e.g., auto-refresh on file changes); FastAPI/Starlette support SSE natively; htmx has a built-in SSE extension |
| **orjson** | Backend — performance | Fast JSON serialisation (Rust-backed) | Only if the `/api/` JSON endpoints become a bottleneck; the stdlib `json` module is fine for a local tool |
| **python-multipart** | Backend — forms | Multipart form data parsing for FastAPI | Only if you ever add a form (e.g., a search box that POSTs); currently not needed since the dashboard is read-only |
| **Heroicons / Lucide** | Frontend — icons | SVG icon sets | Small inline SVGs for status indicators (check, warning, error), nav icons, section headers; copy individual SVGs into templates — no icon font, no sprite sheet |
| **favicon** | Frontend — branding | `.ico` or `.svg` favicon | Minor polish; a simple Python-themed SVG favicon avoids the browser's default blank tab icon |

## Linting and Formatting for Additional Languages

The web app introduces HTML (Jinja templates), CSS, and a small amount of
JS. The question: do these need dedicated linters/formatters?

**Recommendation: not yet, but plan for it.**

### HTML (Jinja) — djLint vs manual review

- **djLint** is the leading linter/formatter for Jinja/Nunjucks/Django
  templates. It checks tag balance, attribute ordering, indentation, and
  Jinja syntax errors. It runs as a single Python package (`pip install
  djlint`) with no Node.js dependency — fits this project perfectly.
- **curlylint** is an alternative but is unmaintained.
- With only ~12 template files initially, manual review is sufficient.
  If templates grow past ~20 files, add djLint as a pre-commit hook —
  it's cheap and catches real bugs (unclosed tags, malformed blocks).

### CSS — Prettier (already available)

- **Stylelint** is the standard CSS linter, but for a single stylesheet
  it's overkill and adds a Node.js dependency.
- **Prettier** (already in the project for Markdown) can format CSS.
  Add `css` to the Prettier file patterns in `.pre-commit-config.yaml`
  as a low-cost first step.

### JS — ESLint vs Biome vs nothing

- **ESLint** is the standard JS linter but requires Node.js, npm, and a
  config file. For ~50 lines of vanilla JS in a Python project, the
  dependency weight is disproportionate.
- **Biome** (https://biomejs.dev/) is a single Rust binary that handles
  linting + formatting for JS/TS/JSON/CSS with zero npm dependency. It
  can be installed via `curl`, Homebrew, or as a pre-commit hook. If JS
  grows beyond a single file, Biome is the right choice — fast, zero
  config by default, and doesn't drag in the Node.js ecosystem.
- **For now:** Skip dedicated JS linting. The JS surface is tiny (vanilla
  snippets, no modules, no build step). Revisit when JS exceeds ~200
  lines or spans multiple files.

**TL;DR:** Extend Prettier to cover CSS (trivial). Skip dedicated
HTML/JS linters until the codebase warrants it. When it does, use djLint
for Jinja templates and Biome for JS — both avoid Node.js/npm overhead.
Revisit if the template count exceeds ~20 files or JS exceeds ~200 lines.

## Risks

- **Scope creep:** A "simple dashboard" easily grows into a feature-rich
  app. Keep it read-only and diagnostic. No write operations, no config
  editing, no package management.
- **Dependency on env_inspect.py internals:** If `gather_env_info()` or
  the private `_*` functions change, the web app breaks. Mitigate by
  depending only on `gather_env_info()` (the public interface).
- **Security:** See the dedicated section below.
- **Maintenance burden:** Another thing to keep working. Mitigate by
  keeping the frontend simple (no build step, no npm, no framework) and
  the data layer shared with the CLI.

## Security — Local-Only Scope

This is a **local developer tool**, not a public web app. The security
requirements are fundamentally different from a production service.

### What you need for local-only use

- **Bind to localhost only.** Hardcode `--bind 127.0.0.1` — never
  `0.0.0.0`. This means only processes on your machine can reach it.
  No network exposure, no remote access.
- **Jinja2 autoescaping.** Environment variables can contain arbitrary
  strings. Jinja2's `autoescape=True` (default in select mode) prevents
  accidental XSS from those values being rendered as HTML. This is a
  one-line setting and non-negotiable even for local use.
- **No secrets in the UI.** The dashboard displays environment state, not
  credentials. If `gather_env_info()` returns sensitive env vars, filter
  or redact them before rendering.
- **Read-only.** The dashboard only _reads_ state — it never modifies
  packages, config files, or environment. No write endpoints.

### What you do NOT need for local-only use

- **Authentication / authorization** — only you can reach 127.0.0.1.
- **HTTPS / TLS** — traffic never leaves your machine.
- **CSRF tokens** — no state-changing operations, no forms that submit.
- **Rate limiting** — only one user (you).
- **Session management** — no login, no cookies, no state.
- **Input validation on URLs** — the routes are fixed, not user-supplied.
- **Database hardening** — there is no database.
- **CORS headers** — no cross-origin requests to handle.

### When security gets serious

If this were ever exposed to the network or multiple users, you'd need
all of the above plus: authentication (OAuth/API keys), TLS, CORS policy,
CSRF protection, rate limiting, input sanitization, and audit logging.
That's a significant jump in complexity — and a strong reason to keep
this local. The local-only constraint is itself a security strategy.

## Complexity Scaling — What If You Want a Lot of Features?

A natural question: what if the dashboard grows to show a _lot_ of
information — not just env state but also doctor results, CI status,
dependency graphs, security audit results, and more?

### It stays manageable if you follow these rules

1. **Each section is a Jinja partial + a route.** Adding a new section
   means one template file and one route handler. The architecture is
   additive, not exponential — 20 sections isn't 20× harder than 5.
2. **htmx lazy-loading keeps the page fast.** Slow sections (package
   outdated checks, security audits) load asynchronously. The initial
   page render stays snappy regardless of how many sections exist.
3. **Data collection is the bottleneck, not the frontend.** The hard
   part is gathering data (subprocess calls, file parsing, network
   requests). The dashboard just renders what `gather_env_info()` and
   similar functions return. If a new data source is slow, give it an
   htmx lazy-load endpoint.
4. **No client-side state management.** With htmx, the server owns all
   state. Each section is an independent HTML fragment. No Redux, no
   Vuex, no component lifecycle — just templates.

### Where it gets harder

- **Cross-section relationships.** If sections need to reference each
  other ("this package is outdated AND breaks this entry point"), you
  need a data layer that correlates information before rendering. This
  is still backend Python logic, not frontend complexity.
- **Real-time updates.** If you want live-updating data (watch for file
  changes, auto-refresh on git operations), you'd need SSE (Server-Sent
  Events) or WebSocket support. FastAPI/Starlette handle both natively,
  and htmx has SSE support built in — but it adds moving parts.
- **User preferences.** If you want saved filters, layout customization,
  or bookmarkable views, you need persistence (even just a JSON file).
  This is where local tools start creeping toward app territory.
- **Multiple data sources with different refresh rates.** Some data is
  instant (Python version), some is slow (outdated packages), some is
  very slow (security audit). Managing per-section refresh intervals
  adds coordination overhead.

### Honest assessment

For a local diagnostic dashboard with 10–20 read-only sections, the
Jinja + htmx + FastAPI stack handles it comfortably. The complexity
growth is linear, not exponential. It gets genuinely harder only if you
add write operations, real-time features, or cross-section data
correlations — and even then, it's backend complexity (Python code you
control), not frontend framework wrestling.

The danger isn't technical complexity — it's scope creep. Define what the
dashboard shows, resist the urge to add config editing or package
management, and it stays a simple read-only tool.

## Worth Doing?

**Yes, with a narrow scope.**

The CLI already works well and covers the data. The web dashboard adds
genuine value for onboarding and debugging through better navigation,
filtering, and visual hierarchy — but only if it stays simple. The
Jinja + htmx + CSS stack keeps it lightweight with no JS toolchain
overhead and minimal new dependencies.

**Recommendation:** Proceed. Start with a minimal viable dashboard
(Python info + packages + build tools), then expand sections
incrementally.

## Open Questions

- ~~**`tools/` vs `devtools/` vs another directory name?**~~ —
  **Decided: `tools/dev-tools/`.** Explicit naming for a template repo
  where clarity beats brevity. Each dev tool gets its own subdirectory
  (e.g., `tools/dev-tools/env-dashboard/`).
- ~~**FastAPI vs Starlette vs stdlib?**~~ — **Decided: FastAPI + Uvicorn.**
  FastAPI for async routing, Jinja2 integration, and auto OpenAPI docs.
  Uvicorn as the ASGI server (`uvicorn app:app --reload --host
  127.0.0.1`). No process manager needed for a local dev tool.
- **Should `gather_env_info()` be extracted into a shared library
  module?** — Currently it's in `scripts/env_inspect.py`. Could move
  the data-collection logic to `src/simple_python_boilerplate/env/` or
  keep it in scripts and import from there. The latter is simpler but
  couples the web app to the scripts directory.
- **Should the dashboard be a Hatch env or a Taskfile shortcut?** —
  Probably both: `hatch run dashboard:serve` and `task dashboard`.
- **Static HTML export as a secondary feature?** — Render the same
  templates to a standalone HTML file for sharing. Low effort if
  the template design is clean.
- **Vendor vs CDN for Alpine.js and Chart.js?** — Vendoring (checking
  the minified files into `static/js/`) is consistent with the htmx
  approach and avoids CDN dependency. Trade-off: slightly larger repo,
  but the combined size is ~95 KB — negligible.
- **Chart.js scope** — Which sections actually benefit from charts vs.
  tables? Candidates: package distribution by location (pie), PATH
  entry counts (bar), Python version matrix (horizontal bar). Avoid
  charts-for-the-sake-of-charts.

## Next Steps

- [ ] Create a blueprint in `docs/blueprints/` with detailed component
      design and template wireframes
- [ ] Draft an ADR for the `tools/dev-tools/` directory convention
- [ ] Prototype: standalone `app.py` that calls `gather_env_info()` and
      renders a single-page Jinja template

## References

- [scripts/env_inspect.py](../../scripts/env_inspect.py) — Existing CLI
  tool with all data-gathering logic
- [scripts/env_doctor.py](../../scripts/env_doctor.py) — Complementary
  diagnostic tool (checks rules, not state)
- [htmx documentation](https://htmx.org/docs/)
- [Alpine.js documentation](https://alpinejs.dev/)
- [Chart.js documentation](https://www.chartjs.org/docs/)
- [Uvicorn documentation](https://www.uvicorn.org/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Jinja2 documentation](https://jinja.palletsprojects.com/)
- [Pico CSS documentation](https://picocss.com/docs)
- [ADR 036: Diagnostic tooling strategy](../adr/036-diagnostic-tooling-strategy.md)
- [ADR 031: Script conventions](../adr/031-script-conventions.md)
