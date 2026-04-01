# Implementation Plan 001: Environment Inspection Web Dashboard

## Status

Draft

## Summary

Build the local environment inspection web dashboard described in
[Blueprint 001](../blueprints/001-env-inspect-web-dashboard.md) and
approved in [ADR 041](../adr/041-env-inspect-web-dashboard.md). The
work creates the `tools/dev-tools/env-dashboard/` directory, wires up
FastAPI + Uvicorn, builds Jinja2 templates for all 11 sections, and
adds the Hatch env / Taskfile integration.

## Origin

- [Blueprint 001: Environment inspection web dashboard](../blueprints/001-env-inspect-web-dashboard.md)
- [ADR 041: Environment inspection web dashboard](../adr/041-env-inspect-web-dashboard.md)

## Prerequisites

- [x] Exploration concluded — Proceed
- [x] Blueprint accepted
- [x] ADR accepted
- [ ] `fastapi[standard]` available on PyPI (it is — just needs adding)

## Task Order

### Phase 1: Scaffolding and backend

Set up the directory, dependencies, and a minimal working server that
renders one page.

| # | Task | Files changed | Notes |
|---|------|---------------|-------|
| 1 | Create `tools/dev-tools/env-dashboard/` directory structure | `tools/dev-tools/env-dashboard/__init__.py` | Empty `__init__.py` |
| 2 | Add `dashboard` optional-dependency group | `pyproject.toml` | `fastapi[standard]` under `[project.optional-dependencies]` |
| 3 | Add Hatch `dashboard` environment | `pyproject.toml` | `[tool.hatch.envs.dashboard]` with `features = ["dashboard"]` and `serve` script |
| 4 | Add Taskfile shortcut | `Taskfile.yml` | `dashboard:serve` task |
| 5 | Create `app.py` — FastAPI app factory | `tools/dev-tools/env-dashboard/app.py` | Mount static files, configure Jinja2 (autoescape=True), `if __name__` starts Uvicorn on `127.0.0.1:8000` |
| 6 | Create `collector.py` — data adapter | `tools/dev-tools/env-dashboard/collector.py` | Import `gather_env_info()` from `scripts/env_inspect.py`, expose `get_all_data()` and `get_section(name)` |
| 7 | Create `routes.py` — route handlers | `tools/dev-tools/env-dashboard/routes.py` | `GET /` (index), `GET /section/{name}` (htmx partial) |
| 8 | Verify: `hatch run dashboard:serve` starts and returns HTTP 200 | — | Manual smoke test |

### Phase 2: Templates and static assets

Build the HTML shell, vendor JS/CSS, and create the index page.

| # | Task | Files changed | Notes |
|---|------|---------------|-------|
| 9 | Vendor Pico CSS into `static/css/pico.min.css` | `tools/dev-tools/env-dashboard/static/css/pico.min.css` | Download from picocss.com (MIT licence) |
| 10 | Create `style.css` — custom properties and layout | `tools/dev-tools/env-dashboard/static/css/style.css` | `--color-ok/warn/error` tokens, dashboard grid, section card styles |
| 11 | Vendor htmx into `static/js/htmx.min.js` | `tools/dev-tools/env-dashboard/static/js/htmx.min.js` | Download from htmx.org (BSD licence) |
| 12 | Vendor Alpine.js into `static/js/alpine.min.js` | `tools/dev-tools/env-dashboard/static/js/alpine.min.js` | Download from alpinejs.dev (MIT licence) |
| 13 | Create `base.html` — layout shell | `tools/dev-tools/env-dashboard/templates/base.html` | Nav sidebar, footer, `<script>` tags for htmx + Alpine, Pico CSS link, `{% block content %}` |
| 14 | Create `index.html` — dashboard home | `tools/dev-tools/env-dashboard/templates/index.html` | Grid of section cards with `hx-get` triggers, summary stats, status indicators |
| 15 | Create `favicon.svg` | `tools/dev-tools/env-dashboard/static/img/favicon.svg` | Simple Python-themed SVG |
| 16 | Verify: dashboard loads in browser with styled layout | — | Manual check — nav, cards, Pico styles render correctly |

### Phase 3: Section partials (core sections)

Build templates for the highest-value sections first.

| # | Task | Files changed | Notes |
|---|------|---------------|-------|
| 17 | `partials/python.html` — Python info section | `tools/dev-tools/env-dashboard/templates/partials/python.html` | Version, executable, implementation, venv status |
| 18 | `partials/git.html` — Git info section | `tools/dev-tools/env-dashboard/templates/partials/git.html` | Version, path |
| 19 | `partials/venv.html` — Virtual environment | `tools/dev-tools/env-dashboard/templates/partials/venv.html` | Active venv details |
| 20 | `partials/packages.html` — Installed packages | `tools/dev-tools/env-dashboard/templates/partials/packages.html` | Grouped by location, Alpine.js search/filter, expandable groups |
| 21 | `partials/build_tools.html` — Build tools | `tools/dev-tools/env-dashboard/templates/partials/build_tools.html` | Tools found on PATH with versions |
| 22 | Verify: five core sections load via htmx and display data | — | Manual smoke test |

### Phase 4: Remaining sections

| # | Task | Files changed | Notes |
|---|------|---------------|-------|
| 23 | `partials/python_installs.html` | `tools/dev-tools/env-dashboard/templates/partials/python_installs.html` | All Python installations found on system |
| 24 | `partials/hatch.html` | `tools/dev-tools/env-dashboard/templates/partials/hatch.html` | Hatch env list, version |
| 25 | `partials/entrypoints.html` | `tools/dev-tools/env-dashboard/templates/partials/entrypoints.html` | Console/GUI scripts |
| 26 | `partials/python_support.html` | `tools/dev-tools/env-dashboard/templates/partials/python_support.html` | Version consistency check |
| 27 | `partials/path.html` | `tools/dev-tools/env-dashboard/templates/partials/path.html` | PATH dirs, duplicates, counts |
| 28 | `partials/system.html` | `tools/dev-tools/env-dashboard/templates/partials/system.html` | OS, hostname, encoding |
| 29 | Verify: all 11 sections render correctly | — | Full manual walkthrough |

### Phase 5: Charts and polish

| # | Task | Files changed | Notes |
|---|------|---------------|-------|
| 30 | Vendor Chart.js into `static/js/chart.min.js` | `tools/dev-tools/env-dashboard/static/js/chart.min.js` | Download from chartjs.org (MIT licence), load only where needed |
| 31 | Add package distribution chart to packages section | `templates/partials/packages.html` | Pie/doughnut chart: package count by location |
| 32 | Add PATH entry count chart to path section | `templates/partials/path.html` | Bar chart: executable counts per PATH entry |
| 33 | Lazy-load slow sections (outdated packages) | `routes.py`, `templates/partials/packages.html` | `hx-trigger="load"` for outdated check, spinner while loading |
| 34 | Add per-section refresh buttons | `templates/partials/*.html` | `hx-get` + `hx-target` on a refresh icon per section |
| 35 | Dark/light mode toggle | `style.css`, `base.html` | CSS `prefers-color-scheme` + Alpine.js toggle switch |
| 36 | Verify: charts render, lazy-load works, refresh works | — | Manual smoke test |

### Phase 6: Documentation and cleanup

| # | Task | Files changed | Notes |
|---|------|---------------|-------|
| 37 | Create `tools/dev-tools/env-dashboard/README.md` | `tools/dev-tools/env-dashboard/README.md` | Usage, development, architecture overview |
| 38 | Extend Prettier to cover `*.css` files | `.pre-commit-config.yaml` | Add CSS to Prettier file patterns |
| 39 | Update `docs/design/tool-decisions.md` | `docs/design/tool-decisions.md` | Note FastAPI, htmx, Alpine.js, Chart.js choices |
| 40 | Update `docs/repo-layout.md` | `docs/repo-layout.md` | Add `tools/dev-tools/` directory |
| 41 | Update `.github/copilot-instructions.md` | `.github/copilot-instructions.md` | Add ADR 041 to key ADRs if warranted |
| 42 | Final verification: full walkthrough | — | All sections, charts, search, refresh, dark mode |

## Migrations / Refactors

No migrations needed. This is purely additive — new files in a new
directory with a new optional dependency group. Nothing existing changes
in a breaking way.

- **Before:** `env_inspect.py` CLI only.
- **After:** CLI unchanged + new web dashboard as alternative view.

## Testing Checklist

- [ ] `hatch run dashboard:serve` starts without errors
- [ ] `http://127.0.0.1:8000` returns HTTP 200
- [ ] Index page renders with all 11 section cards
- [ ] Each section loads correctly via htmx
- [ ] Package search/filter works (Alpine.js)
- [ ] Charts render on packages and path sections
- [ ] Lazy-load spinner shows for slow sections
- [ ] Per-section refresh updates data
- [ ] Dark/light mode toggle works
- [ ] Jinja2 autoescape active (test with env var containing `<script>`)
- [ ] Server binds to `127.0.0.1` only (verify with `netstat`/`ss`)
- [ ] `task dashboard:serve` works as Taskfile shortcut
- [ ] No console errors in browser DevTools
- [ ] Templates validate (no unclosed tags)

## Rollout Notes

- **Feature flags:** None — the dashboard is opt-in via
  `hatch run dashboard:serve`. It doesn't affect any existing workflow.
- **Breaking changes:** None. Purely additive.
- **Rollback plan:** Delete `tools/dev-tools/env-dashboard/`, remove the
  `dashboard` dependency group and Hatch env from `pyproject.toml`,
  remove the Taskfile task.
- **Documentation updates:** README in the dashboard directory, plus
  updates to `repo-layout.md` and `tool-decisions.md`.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep — dashboard grows into a feature-rich app | Med | Keep read-only. No write endpoints. Defer features to later iterations. |
| `gather_env_info()` API changes break collector | Low | Depend only on the public interface. Localise changes to `collector.py`. |
| Vendored JS becomes outdated | Low | Pin versions in README. Update periodically. No security risk for local-only tool. |
| Template users don't want the dashboard | Low | Self-contained in `tools/dev-tools/env-dashboard/`. Delete the directory — no impact on core package. |

## References

- [Exploration 001: Environment inspection web dashboard](../explorations/001-env-inspect-web-dashboard.md)
- [Blueprint 001: Environment inspection web dashboard](../blueprints/001-env-inspect-web-dashboard.md)
- [ADR 041: Environment inspection web dashboard](../adr/041-env-inspect-web-dashboard.md)
- [scripts/env_inspect.py](../../scripts/env_inspect.py)
