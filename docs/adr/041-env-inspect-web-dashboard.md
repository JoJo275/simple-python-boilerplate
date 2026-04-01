# ADR 041: Environment Inspection Web Dashboard

## Status

Accepted

## Context

`scripts/env_inspect.py` provides a comprehensive CLI dashboard covering
Python info, git status, venv detection, installed packages, entry points,
build tools, PATH inspection, Python installations, and system environment.
The output is rich but confined to the terminal — long tables scroll off
screen, cross-referencing sections requires scrolling, and data can't be
filtered, searched, or bookmarked interactively.

[Exploration 001](../explorations/001-env-inspect-web-dashboard.md)
evaluated five alternatives (web dashboard, full SPA, Textual TUI, static
HTML export, do nothing) and concluded that a local web dashboard adds
genuine value for onboarding and debugging while staying lightweight.

[Blueprint 001](../blueprints/001-env-inspect-web-dashboard.md) defined
the structural design: FastAPI + Uvicorn backend, Jinja2 + htmx + Alpine.js
+ Chart.js frontend, Pico CSS styling.

This ADR locks in three decisions:

1. **Build the web dashboard** — an alternative view of `env_inspect.py` data.
2. **Use `tools/dev-tools/` as the directory** for multi-file developer tools.
3. **Use the FastAPI + htmx stack** described in the blueprint.

## Decision

### 1. Build a local-only web dashboard for environment inspection

Serve a read-only web dashboard at `http://127.0.0.1:8000` that presents
the same data as `env_inspect.py` in a navigable, filterable interface.
The dashboard is a developer tool, not part of the distributed package.

### 2. Introduce `tools/dev-tools/` for multi-file developer tools

`scripts/` is for single-file CLI utilities. The dashboard is a multi-file
application with templates, static assets, and internal structure. A new
`tools/dev-tools/env-dashboard/` directory clearly separates it. The path
is explicit — important for a template repo where clarity beats brevity.

This also establishes a convention: future multi-file developer tools
go under `tools/dev-tools/` in their own subdirectory.

### 3. Technology stack

| Layer | Tool | Rationale |
| :---- | :--- | :-------- |
| Backend — framework | FastAPI | Async routing, Jinja2 integration, auto OpenAPI docs |
| Backend — server | Uvicorn | Standard FastAPI server; `--reload` for dev; lightweight |
| Backend — templating | Jinja2 | Already a transitive dep; partials map to htmx endpoints |
| Frontend — interactivity | htmx (vendored) | SPA-like UX, zero JS framework, ~14 KB |
| Frontend — client state | Alpine.js (vendored) | Search/filter, toggles, tabs; ~15 KB; declarative HTML |
| Frontend — charts | Chart.js (vendored) | Data visualisation where tables aren't enough; ~65 KB |
| Frontend — styling | Pico CSS + custom CSS | Classless base + project-specific overrides |

All JS vendored as single files in `static/js/`. No npm, no build step,
no CDN dependency.

### 4. Dependencies

Add a `dashboard` optional-dependency group in `pyproject.toml`:

```toml
[project.optional-dependencies]
dashboard = [
    "fastapi[standard]",
]
```

Create a dedicated Hatch environment:

```toml
[tool.hatch.envs.dashboard]
features = ["dashboard"]
```

### 5. Security constraints

- Bind to `127.0.0.1` only — never `0.0.0.0`.
- `Jinja2 autoescape=True` — non-negotiable.
- Read-only — no write endpoints, no forms, no state mutation.
- Redact sensitive environment variables before rendering.

## Alternatives Considered

### Full SPA (React/Vue/Svelte + FastAPI)

Maximum flexibility and rich interactivity.

**Rejected because:** Disproportionate complexity — adds Node.js, npm,
bundler, and a JS build step to a Python-focused project. Template users
who don't want the dashboard still inherit the JS toolchain.

### Textual TUI

Terminal-based interactive dashboard using the Textual framework.

**Rejected because:** Terminal-only — can't bookmark, can't share a URL,
limited layout flexibility vs. HTML+CSS. Textual is a ~5 MB dependency.
Worth considering as a complementary option but doesn't replace the web
dashboard.

### Static HTML export only

Generate a standalone `.html` file with all data inlined.

**Rejected because:** No interactivity (filtering, lazy-loading, refresh).
Useful as a secondary export feature but not as the primary interface.

### Do nothing

Keep the CLI as-is.

**Rejected because:** The CLI works but misses UX improvements for
onboarding and debugging. The web version adds meaningful value for
small incremental effort.

### Keep it in `scripts/`

Put the dashboard files in `scripts/env_dashboard/`.

**Rejected because:** `scripts/` convention is single-file CLIs. A
multi-file application with templates and static assets doesn't fit.
Mixing the two creates confusion about what the `scripts/` directory is for.

## Consequences

### Positive

- Developers get a navigable, filterable view of their environment —
  faster debugging and easier onboarding.
- Template users can delete `tools/dev-tools/env-dashboard/` cleanly
  without affecting the core package or scripts.
- Establishes a reusable `tools/dev-tools/` convention for future
  multi-file developer tools.
- No npm/Node.js dependency — all JS vendored, no build step.

### Negative

- New optional dependency group (`fastapi[standard]`) in `pyproject.toml`.
- Another thing to maintain — templates, routes, and styles need updating
  when `gather_env_info()` output changes.
- Vendored JS files (~95 KB total) add to repo size.

### Neutral

- The CLI (`env_inspect.py`) is unchanged. The dashboard is additive.
- CI is unaffected — no new workflows, no new gate checks.

### Mitigations

- Maintenance burden: `collector.py` depends only on `gather_env_info()`
  (the public interface), not internal `_*` functions. Changes to the
  data shape are localised to `collector.py` and the affected template.
- Scope creep: keep the dashboard read-only and diagnostic. No write
  operations, no config editing, no package management.

## Implementation

- [tools/dev-tools/env-dashboard/app.py](../../tools/dev-tools/env-dashboard/app.py) — FastAPI app factory
- [tools/dev-tools/env-dashboard/collector.py](../../tools/dev-tools/env-dashboard/collector.py) — Data collection adapter
- [tools/dev-tools/env-dashboard/routes.py](../../tools/dev-tools/env-dashboard/routes.py) — Route handlers
- [tools/dev-tools/env-dashboard/templates/](../../tools/dev-tools/env-dashboard/templates/) — Jinja2 templates
- [tools/dev-tools/env-dashboard/static/](../../tools/dev-tools/env-dashboard/static/) — CSS, JS, images
- [pyproject.toml](../../pyproject.toml) — `dashboard` dependency group and Hatch env
- [Taskfile.yml](../../Taskfile.yml) — `dashboard:serve` task

## References

- [Exploration 001: Environment inspection web dashboard](../explorations/001-env-inspect-web-dashboard.md)
- [Blueprint 001: Environment inspection web dashboard](../blueprints/001-env-inspect-web-dashboard.md)
- [Implementation Plan 001: Environment inspection web dashboard](../implementation-plans/001-env-inspect-web-dashboard.md)
- [ADR 036: Diagnostic tooling strategy](../adr/036-diagnostic-tooling-strategy.md)
- [ADR 031: Script conventions](../adr/031-script-conventions.md)
- [scripts/env_inspect.py](../../scripts/env_inspect.py)
