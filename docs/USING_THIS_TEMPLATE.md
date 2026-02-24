# Using This Template

This document guides you through customizing the boilerplate files for your own project.

Implement any of these changes at your discretion — this is just a guide to help you get started. You can skip or modify steps as needed for your specific project.

## Quick Start

1. **Clone or use as template** on GitHub
2. **Run the customization script** — it handles placeholders, package
   renaming, license selection, and optional directory stripping:

   ```bash
   python scripts/customize.py          # interactive
   python scripts/customize.py --dry-run # preview changes first
   ```

   Or do it manually: find-and-replace all placeholders (see below),
   delete what you don't need, and customize the remaining files.

---

## Placeholders to Replace

Search your project for these placeholders and replace them with your values:

| Placeholder | Replace With | Files |
|-------------|--------------|-------|
| `simple-python-boilerplate` | Your project name | `README.md`, `pyproject.toml`, `SECURITY.md` |
| `simple_python_boilerplate` | Your package name (underscore) | `src/`, `pyproject.toml` |
| `JoJo275` | Your GitHub username/org | `SECURITY.md`, issue templates |
| `security@example.com` | Your security contact email | `SECURITY.md` |
| `[INSERT EMAIL ADDRESS]` | Your contact email | Various files |
| `[Your Name]` | Your name | `LICENSE`, `pyproject.toml` |

---

## Files to Customize

### Required Customization

| File | What to Change |
|------|----------------|
| `README.md` | Project name, description, badges, installation instructions |
| `pyproject.toml` | Package name, author, dependencies, URLs |
| `LICENSE` | Year, author name (or choose a different license) |
| `SECURITY.md` | Repository URL, contact email, PGP key (optional) |

### Optional Customization

| File | When to Customize |
|------|-------------------|
| `.github/ISSUE_TEMPLATE/*.yml` | Adjust fields, labels, or remove templates you don't need |
| `CONTRIBUTING.md` | Add project-specific contribution guidelines |
| `CODE_OF_CONDUCT.md` | Usually fine as-is (Contributor Covenant) |
| `labels/*.json` | Add custom labels for your workflow |

---

## Issue Templates

This template includes 5 issue templates:

| Template | Purpose | When to Keep |
|----------|---------|--------------|
| `bug_report` | Report confirmed bugs | Always |
| `feature_request` | Suggest enhancements | Always |
| `documentation` | Docs issues/improvements | If you have docs |
| `question` | Technical questions | Optional — can use Discussions instead |
| `performance` | Performance issues | If performance matters to your project |

### Removing Templates

Simply delete the `.yml` and `.md` files you don't need from `.github/ISSUE_TEMPLATE/`.

### Customizing Labels

1. Edit `labels/baseline.json` or `labels/extended.json`
2. Run `./scripts/apply-labels.sh baseline` (or `extended`)
3. Update issue template `labels:` fields to match

---

## Security Policy

Choose your security policy approach:

| Scenario | Use |
|----------|-----|
| No bug bounty (most projects) | `SECURITY.md` (default) or see `docs/templates/SECURITY_no_bounty.md` |
| With bug bounty | See `docs/templates/SECURITY_with_bounty.md` |
| Standalone bounty policy | See `docs/templates/BUG_BOUNTY.md` |

### Enabling Private Vulnerability Reporting

1. Go to your repo → **Settings** → **Security** → **Code security and analysis**
2. Enable **Private vulnerability reporting**
3. Users can now report vulnerabilities privately via GitHub

---

## GitHub Features to Enable

After creating your repo, consider enabling:

- [ ] **Discussions** — For Q&A and community conversations
- [ ] **Private vulnerability reporting** — For security issues
- [ ] **Dependabot alerts** — For dependency vulnerabilities
- [ ] **Dependabot security updates** — Auto-create PRs for vulnerable deps
- [ ] **Branch protection** — Require PR reviews, status checks

---

## Files You Can Delete

If you don't need certain features, remove these files:

| Delete | If You Don't Need |
|--------|-------------------|
| `docs/templates/` | Template files (copy what you need first) |
| `.github/ISSUE_TEMPLATE/question.*` | Question template (use Discussions) |
| `.github/ISSUE_TEMPLATE/performance.*` | Performance issue tracking |
| `labels/extended.json` | Extended label set (baseline is enough) |

---

> The template is meant to be a starting point — feel free to strip out what you don't need and add what you do. **Be conscious** of certain files that depend on others (e.g., issue templates reference labels, so update or remove them together).

## Checklist

### Initial Setup

- [ ] Clone or use "Use this template" on GitHub
- [ ] Rename the repository to your project name
- [ ] Update remote URL if cloned directly

### Placeholder Replacements

- [ ] Replace `simple-python-boilerplate` with your project name
- [ ] Replace `simple_python_boilerplate` with your package name (snake_case)
- [ ] Replace `JoJo275` with your GitHub username/org
- [ ] Replace `[Your Name]` with your name in `LICENSE` and `pyproject.toml`
- [ ] Replace `security@example.com` with your security contact

### Core Files

- [ ] Update `README.md` with project description and badges
- [ ] Update `pyproject.toml` (name, author, dependencies, URLs)
- [ ] Update `LICENSE` (year, author — or choose different license)
- [ ] Update `SECURITY.md` with your contact info

### Source Code

- [ ] Rename `src/simple_python_boilerplate/` to your package name
- [ ] Update imports in test files to match new package name
- [ ] Update entry points in `pyproject.toml` if needed

### GitHub Configuration

- [ ] Enable **Discussions** (optional)
- [ ] Enable **Private vulnerability reporting**
- [ ] Enable **Dependabot alerts**
- [ ] Enable **Dependabot security updates**
- [ ] Set up **branch protection** rules
- [ ] Apply labels: `./scripts/apply-labels.sh baseline`

### Issue Templates

- [ ] Review and customize `.github/ISSUE_TEMPLATE/*.yml`
- [ ] Remove templates you don't need
- [ ] Update labels in templates to match your label set

### Cleanup

- [ ] Delete `docs/templates/` (after copying what you need)
- [ ] Delete unused issue templates
- [ ] Remove or update example code in `src/`
- [ ] Remove or update example tests in `tests/`
- [ ] Clear `CHANGELOG.md` for your project's history
- [ ] Remove template-specific notes from documentation

### Gitignore Configuration

After adopting the template, add these directories to your `.gitignore` to keep local experiments and data out of version control:

- [ ] Add `experiments/` to `.gitignore`
- [ ] Add `var/` to `.gitignore`

Add the following to your `.gitignore`:

```gitignore
# Local experiments (scratch code, prototypes)
/experiments/

# Local data and state
/var/
```

### Verification

- [ ] Run `python -m pip install -e .` successfully
- [ ] Run `pytest` — all tests pass
- [ ] Run `ruff check .` — no linting errors
- [ ] Run `mypy src/` — no type errors
- [ ] Verify imports work: `python -c "import your_package"`

### Optional Steps

- [ ] Set up pre-commit hooks (see [Pre-commit Hooks](#pre-commit-hooks) above)
- [ ] Configure code coverage reporting (Codecov, see [coverage.yml](../.github/workflows/coverage.yml))
- [ ] Add project-specific documentation
- [ ] Set up GitHub Pages for docs

---

## CI/CD Workflows Included

This template ships with **26 GitHub Actions workflows** in `.github/workflows/`
covering quality, security, PR hygiene, releases, docs, containers, and
maintenance. All are SHA-pinned to commit SHAs
([ADR 004](adr/004-pin-action-shas.md)) and disabled by default via repository
guards — enable them by setting a repository variable or updating the repo slug
([ADR 011](adr/011-repository-guard-pattern.md)).

A single **CI Gate** workflow aggregates all required checks into one
branch-protection status, so you never need to list individual workflows in
GitHub settings ([ADR 024](adr/024-ci-gate-pattern.md)).

For the full list of every workflow with triggers, job names, and descriptions,
see the [workflows README](../.github/workflows/README.md) or
[workflows.md](workflows.md).

## Pre-commit Hooks

[Pre-commit hooks](https://pre-commit.com/) are scripts that run automatically
at specific points in the Git workflow — before a commit is created, before a
push, etc. They catch problems (lint errors, type issues, security concerns,
bad commit messages) **before** code leaves your machine, so you don't discover
them later in CI.

This template includes **34+ hooks** across three Git stages:

| Stage | When it runs | Examples |
|-------|-------------|----------|
| **pre-commit** | Every `git commit` | Ruff lint/format, mypy, bandit, typos, deptry, YAML/TOML/JSON checks |
| **commit-msg** | Every `git commit` | Commitizen — validates Conventional Commits format |
| **pre-push** | Every `git push` | pytest, pip-audit, gitleaks |

All hooks are configured in [`.pre-commit-config.yaml`](../.pre-commit-config.yaml).
See [ADR 008](adr/008-pre-commit-hooks.md) for the full hook inventory and
reasoning behind each choice.

To install all three hook stages:

```bash
pre-commit install                              # pre-commit stage
pre-commit install --hook-type commit-msg        # commit-msg stage
pre-commit install --hook-type pre-push          # pre-push stage
```

> **New to pre-commit?** Think of hooks as automated code reviewers. Instead of
> remembering to run the linter, formatter, and tests manually before pushing,
> hooks run them for you. If a check fails, the commit or push is blocked with
> an explanation of what went wrong.

## File Templates

The [`docs/templates/`](templates/) directory contains **reusable file templates**
you can copy and adapt for your project:

| Template | Purpose |
|----------|---------|
| `SECURITY_no_bounty.md` | Standard security policy (most projects) |
| `SECURITY_with_bounty.md` | Security policy with bug bounty program |
| `BUG_BOUNTY.md` | Standalone bug bounty policy |
| `pull-request-draft.md` | PR description template |

Copy what you need, then delete the `docs/templates/` directory to keep your
repo clean.

## Command Workflows

This project has **three layers** for running developer commands:
raw Python tools (pytest, ruff, mypy), Hatch (managed environments),
and a Task runner (short aliases). Each layer is optional — use
whichever fits your preference.

See [command-workflows.md](development/command-workflows.md) for a
detailed breakdown of how `task test` → `hatch run test` → `pytest`
flows through each layer, and guidance on which layer to use.

## Containers

This template includes three container-related files, each serving a
different purpose ([ADR 025](adr/025-container-strategy.md)):

| File | Purpose | When to use |
|------|---------|-------------|
| [`Containerfile`](../Containerfile) | **Production image** — multi-stage build that produces a minimal runtime image (~150 MB) with only your installed package. No dev tools. | `docker build -f Containerfile .` or `podman build -f Containerfile .` |
| [`docker-compose.yml`](../docker-compose.yml) | **Orchestration** — convenience wrapper to build and run the production container locally. Also the place to add multi-service setups (app + database, etc.). | `docker compose up --build` |
| [`.devcontainer/`](../.devcontainer/) | **Development environment** — VS Code Dev Container / GitHub Codespaces config. Includes Python, Node.js, Task runner, all dev deps, and pre-commit hooks. | Open repo in VS Code → "Reopen in Container" |

> **Why is `docker-compose.yml` in the repo root, not `.devcontainer/`?**
> Compose orchestrates the *production* Containerfile — it’s for building and
> running your app, not for the dev environment. The `.devcontainer/` directory
> is specifically for VS Code Dev Container configuration. Keeping them
> separate avoids conflating production and development concerns.

If you don’t need containers, delete `Containerfile`, `docker-compose.yml`,
and `.devcontainer/`. If you only want production containers, delete
`.devcontainer/`. If you only want the dev container, delete the other two.

## Documentation Stack

This template includes a ready-to-use documentation site powered by
[MkDocs](https://www.mkdocs.org/) with the
[Material](https://squidfunk.github.io/mkdocs-material/) theme and
[mkdocstrings](https://mkdocstrings.github.io/) for auto-generated API docs
from Python docstrings ([ADR 020](adr/020-mkdocs-documentation-stack.md)).

**Key files:**

| File / Directory | Purpose |
|------------------|---------|
| `mkdocs.yml` | Site configuration (theme, nav, plugins) |
| `docs/mkdocs/` | Markdown source files for the built site |
| `docs/` (this directory) | Project docs that aren’t part of the MkDocs site |
| `site/` | Built HTML output (gitignored in production, committed here for reference) |

**Quick start:**

```bash
# Serve locally with live reload (http://localhost:8000)
hatch run docs:serve
# or
task docs:serve

# Build the site (strict mode — fails on warnings)
hatch run docs:build
# or
task docs:build
```

**Docstring format:** mkdocstrings is configured to parse **Google-style**
docstrings (`docstring_style: google` in `mkdocs.yml`). Ruff's pydocstyle
rules enforce the same convention (`convention = "google"` in
`pyproject.toml`). If you prefer NumPy or Sphinx style, update both settings
so the linter and the doc renderer stay in sync.

**To customize for your project:**

1. Update `mkdocs.yml` — change `site_name`, `site_url`, `repo_url`
2. Edit pages in `docs/mkdocs/` — add your own guides, tutorials, API docs
3. Update the `nav:` section in `mkdocs.yml` to reflect your page structure
4. (Optional) Enable GitHub Pages deployment via the `docs-deploy.yml` workflow

The CI workflow [`docs-deploy.yml`](../.github/workflows/docs-deploy.yml)
automatically builds the site on push to `main` and deploys to GitHub Pages
(path-filtered to docs/source changes only).

If you don’t need a documentation site, delete `mkdocs.yml`, `docs/mkdocs/`,
and `site/`.

---

## Repo Tooling Reference

Not sure what a tool does? See [tooling.md](tooling.md) for a one-line
explanation of every tool in this repo (Hatch, Ruff, mypy, pytest, pre-commit,
MkDocs, etc.) with links to their official docs.

For deeper reasoning on *why* each tool was chosen over alternatives, see
[tool-decisions.md](design/tool-decisions.md).

---

## Optional Tools to Consider

These aren't included in the template but are worth evaluating for your project:

| Tool | Category | When to Use |
|------|----------|-------------|
| **[SQLAlchemy](https://www.sqlalchemy.org/)** | ORM / Database | Need a relational DB with Python models |
| **[Alembic](https://alembic.sqlalchemy.org/)** | DB Migrations | Managing schema changes over time (pairs with SQLAlchemy) |
| **[Sphinx](https://www.sphinx-doc.org/)** | Documentation | Alternative to MkDocs — richer API doc generation from docstrings |
| **[MkDocs](https://www.mkdocs.org/)** | Documentation | Markdown-based docs site (simpler than Sphinx) |
| **[FastAPI](https://fastapi.tiangolo.com/)** | Web Framework | Building an API (async, OpenAPI docs built-in) |
| **[Flask](https://flask.palletsprojects.com/)** | Web Framework | Lightweight web apps and APIs |
| **[CircleCI](https://circleci.com/)** | CI/CD | Alternative to GitHub Actions |
| **[Celery](https://docs.celeryq.dev/)** | Task Queue | Background / async job processing |
| **[Docker](https://www.docker.com/)** | Containerization | Reproducible builds and deployments |
| **[Podman](https://podman.io/)** | Containerization | Daemonless alternative to Docker |
| **[Sentry](https://sentry.io/)** | Error Tracking | Production error monitoring |
| **[HTTPX](https://www.python-httpx.org/)** | HTTP Client | Modern async-capable HTTP client (alternative to requests) |
| **[Nox](https://nox.thea.codes/)** | Task Runner | Multi-environment testing and automation |
| **[Tox](https://tox.wiki/)** | Task Runner | Test across multiple Python versions |

---

## Need Help?

- Open an issue on the [template repository](https://github.com/JoJo275/simple-python-boilerplate)
- Check existing issues for common questions
