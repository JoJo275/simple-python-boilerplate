# Blueprint 001: Environment Inspection Web Dashboard

## Status

Accepted

## Summary

A local-only web dashboard that presents the same environment data as
`scripts/env_inspect.py` in a navigable, filterable, visually structured
interface. Built with FastAPI + Uvicorn (backend), Jinja2 templates +
htmx + Alpine.js + Chart.js (frontend), and Pico CSS (styling). Lives in
`tools/dev-tools/env-dashboard/` outside the distributed package.

## Origin

- [Exploration 001: Environment inspection web dashboard](../explorations/001-env-inspect-web-dashboard.md)

## Proposed Architecture

```
┌─────────────┐      ┌──────────────┐     ┌──────────────────┐
│  Browser    │─────▶│  Uvicorn     │────▶│  FastAPI app      │
│  (htmx +   │◀─────│  127.0.0.1   │◀────│  routes.py        │
│   Alpine)   │ HTML │  :8000       │     │  collector.py     │
└─────────────┘      └──────────────┘     └────────┬─────────┘
                                                   │
                                          ┌────────▼─────────┐
                                          │ env_inspect.py    │
                                          │ gather_env_info() │
                                          └──────────────────┘
```

**Request flow:**

1. Browser requests a page or htmx partial.
2. Uvicorn routes to the FastAPI app.
3. `routes.py` calls `collector.py` which wraps `gather_env_info()`.
4. Response is a rendered Jinja2 template (full page or HTML fragment).
5. htmx swaps the fragment into the DOM. Alpine.js manages local UI state.

**Data flow:**

- All data originates from `gather_env_info()` in `scripts/env_inspect.py`.
- `collector.py` is a thin adapter: calls `gather_env_info()`, caches
  results per-request, and reshapes data for template consumption.
- No database. No persistence. Read-only.

## Repo Layout

```
tools/
└── dev-tools/
    └── env-dashboard/
        ├── __init__.py
        ├── app.py                ← FastAPI app factory + Uvicorn entrypoint
        ├── collector.py          ← Wraps gather_env_info(), section-level helpers
        ├── routes.py             ← Route handlers: full pages + htmx partials
        ├── static/
        │   ├── css/
        │   │   ├── pico.min.css  ← Vendored Pico CSS (~10 KB)
        │   │   └── style.css     ← Custom properties, dashboard layout, status colours
        │   ├── js/
        │   │   ├── htmx.min.js   ← Vendored (~14 KB)
        │   │   ├── alpine.min.js ← Vendored (~15 KB)
        │   │   └── chart.min.js  ← Vendored (~65 KB), loaded only on chart pages
        │   └── img/
        │       └── favicon.svg   ← Simple Python-themed SVG
        ├── templates/
        │   ├── base.html         ← Layout shell: nav, footer, <script> tags
        │   ├── index.html        ← Dashboard home: section cards with htmx triggers
        │   └── partials/         ← One per section, htmx-swappable
        │       ├── python.html
        │       ├── python_installs.html
        │       ├── git.html
        │       ├── venv.html
        │       ├── hatch.html
        │       ├── packages.html
        │       ├── entrypoints.html
        │       ├── build_tools.html
        │       ├── python_support.html
        │       ├── path.html
        │       └── system.html
        └── README.md
```

**New top-level directory:** `tools/` — for multi-file developer tools
that don't belong in `scripts/` (single-file CLIs) or `src/` (distributed
package). See [ADR 041](../adr/041-env-inspect-web-dashboard.md).

## Components / Modules

| Component | Responsibility | Key interfaces |
| :-------- | :------------- | :------------- |
| `app.py` | Create FastAPI app, mount static files, configure Jinja2, start Uvicorn | `create_app() → FastAPI`, `main()` |
| `collector.py` | Call `gather_env_info()`, expose per-section data helpers | `get_all_data() → dict`, `get_section(name) → dict` |
| `routes.py` | Define routes for full pages and htmx partials | `GET /` (index), `GET /section/{name}` (partial) |
| `base.html` | Layout shell with nav sidebar, htmx/Alpine/Chart script loading | Jinja2 `{% block content %}` |
| `index.html` | Dashboard home — grid of section cards with `hx-get` triggers | Extends `base.html` |
| `partials/*.html` | One template per section — htmx-friendly HTML fragments | Standalone renderable fragments |
| `style.css` | Dashboard-specific styles, CSS custom properties for theming | `--color-ok`, `--color-warn`, `--color-error` tokens |

## Tooling Impact

### New dependencies

Add to `pyproject.toml` under `[project.optional-dependencies]`:

```toml
dashboard = [
    "fastapi[standard]",  # Includes uvicorn, jinja2, python-multipart
]
```

Jinja2 is already a transitive dep of MkDocs but should be declared
explicitly via `fastapi[standard]`.

### Config changes

| File | Change |
| :--- | :----- |
| `pyproject.toml` | Add `dashboard` optional-dependency group |
| `Taskfile.yml` | Add `dashboard:serve` task |
| `.gitignore` | No change needed (no build artifacts) |
| `.pre-commit-config.yaml` | Extend Prettier to cover `*.css` files (low-cost) |

### Hatch environment

```toml
[tool.hatch.envs.dashboard]
features = ["dashboard"]

[tool.hatch.envs.dashboard.scripts]
serve = "python -m tools.dev-tools.env-dashboard.app"
```

### Taskfile shortcut

```yaml
dashboard:serve:
  desc: Start the env-dashboard web UI
  cmds:
    - hatch run dashboard:serve
```

### CI/CD impact

None. This is a local-only tool. No CI workflow needed. No deployment.

## Workflow / UX

### Starting the dashboard

```bash
task dashboard:serve
# or
hatch run dashboard:serve
# or directly
python -m tools.dev-tools.env-dashboard.app
```

Opens `http://127.0.0.1:8000` in the default browser (or prints the URL).

### Using the dashboard

1. **Landing page** shows a grid of section cards (Python, Git, Packages,
   etc.) with summary info and status indicators (green/amber/red).
2. Each card has an **expand** action that loads the full section via htmx
   (`hx-get="/section/packages"` → swaps in `partials/packages.html`).
3. **Slow sections** (outdated packages) show a loading spinner and
   load asynchronously via `hx-trigger="load"`.
4. **Search/filter** (Alpine.js `x-model`) provides instant client-side
   filtering on package tables.
5. **Refresh** button per section re-fetches data without full page reload.
6. **Charts** (Chart.js) render on sections that benefit from visual
   representation (package count by location, PATH entry distribution).

### Stopping

`Ctrl+C` in the terminal. No cleanup needed — no state, no database.

## Open Design Questions

- [x] `tools/` vs `devtools/` directory name — **Decided: `tools/dev-tools/`**
- [x] FastAPI vs Starlette vs stdlib — **Decided: FastAPI + Uvicorn**
- [ ] Should `gather_env_info()` be extracted to a shared module, or
  should `collector.py` import directly from `scripts/env_inspect.py`?
  Recommendation: start with direct import, extract later if needed.
- [ ] Static HTML export mode — defer to a later iteration.
- [ ] Exact Chart.js usage — start with package distribution pie chart
  only, add more if they prove useful.

## Constraints

- **Local-only.** Bind to `127.0.0.1` only. No authentication, no TLS,
  no CORS. See security section in exploration.
- **Read-only.** No write endpoints. No state mutation. No forms that
  submit.
- **No npm / Node.js.** All JS vendored as single files. No build step.
- **Python 3.11+** — matches project minimum.
- **Jinja2 autoescape=True** — non-negotiable for safe rendering of
  arbitrary env-var values.

## References

- [Exploration 001: Environment inspection web dashboard](../explorations/001-env-inspect-web-dashboard.md)
- [ADR 041: Environment inspection web dashboard](../adr/041-env-inspect-web-dashboard.md)
- [Implementation Plan 001: Environment inspection web dashboard](../implementation-plans/001-env-inspect-web-dashboard.md)
- [scripts/env_inspect.py](../../scripts/env_inspect.py)
- [ADR 036: Diagnostic tooling strategy](../adr/036-diagnostic-tooling-strategy.md)
