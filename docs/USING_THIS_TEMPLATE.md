# Using This Template

This is the source of truth for getting started with this template. It walks
you through customization, explains what every section of the repo does, and
links to deeper docs where they exist.

Implement any of these changes at your discretion — skip or reorder steps to
fit your project.

> **Something not working?**
> See **[Troubleshooting & FAQ](guide/troubleshooting.md)** for solutions
> to common errors with installation, CI/CD, pre-commit hooks, testing, Git,
> and more.

---

## Quick Start

1. **Clone or use as template** on GitHub
2. **Run the customization script** — handles placeholders, package
   renaming, license selection, and optional directory stripping:

   ```bash
   python scripts/customize.py          # interactive
   python scripts/customize.py --dry-run # preview changes first
   ```

   Or do it manually: find-and-replace all placeholders (see
   [Placeholders to Replace](#placeholders-to-replace)), delete what you
   don't need, and customize the remaining files.

3. **Bootstrap your environment** — installs Hatch envs, pre-commit hooks,
   and verifies the setup:

   ```bash
   python scripts/bootstrap.py          # full setup
   python scripts/bootstrap.py --dry-run # preview
   ```

> **What's the difference?** [`scripts/customize.py`](../scripts/customize.py)
> rewrites files (renames packages, swaps placeholders, changes the license).
> [`scripts/bootstrap.py`](../scripts/bootstrap.py) sets up your local dev
> environment (creates Hatch envs, installs hooks, verifies the install).
> Run `customize.py` first, then `bootstrap.py`.
>
> Both scripts support `--dry-run` to preview changes and `--help` for the
> full list of flags. See the docstring at the top of each script for details.

---

## Placeholders to Replace

<!-- TODO (template users): After replacing these, delete this table or mark
     items done. The customize.py script handles most of them automatically. -->

Search your project for these placeholders and replace them with your values:

| Placeholder                     | Replace with                          | Key files                                                          |
| :------------------------------ | :------------------------------------ | :----------------------------------------------------------------- |
| `simple-python-boilerplate`     | Your project name (kebab-case)        | [README.md](../README.md), [pyproject.toml](../pyproject.toml), [SECURITY.md](../SECURITY.md) |
| `simple_python_boilerplate`     | Your package name (snake_case)        | [src/](../src/), [pyproject.toml](../pyproject.toml)               |
| `JoJo275`                       | Your GitHub username/org              | [SECURITY.md](../SECURITY.md), issue templates                     |
| `YOURNAME/YOURREPO`             | Your `owner/repo` slug                | [.github/workflows/](../.github/workflows/), [README.md](../README.md) |
| `security@example.com`          | Your security contact email           | [SECURITY.md](../SECURITY.md)                                     |
| `[INSERT EMAIL ADDRESS]`        | Your contact email                    | Various files                                                      |
| `[Your Name]`                   | Your name                             | [LICENSE](../LICENSE), [pyproject.toml](../pyproject.toml)         |
| `YOUR_TOKEN`                    | Your Codecov token (or remove badge)  | [README.md](../README.md)                                         |

---

## Files to Customize

### Required

| File                                          | What to change                                              |
| :-------------------------------------------- | :---------------------------------------------------------- |
| [README.md](../README.md)                     | Project name, description, badges, installation instructions |
| [pyproject.toml](../pyproject.toml)           | Package name, author, dependencies, URLs, entry points      |
| [LICENSE](../LICENSE)                          | Year, author name (or choose a different license)           |
| [SECURITY.md](../SECURITY.md)                 | Repository URL, contact email, PGP key (optional)           |
| [mkdocs.yml](../mkdocs.yml)                   | `site_name`, `site_url`, `repo_url`                         |

### Optional

| File                                                              | When to customize                                       |
| :---------------------------------------------------------------- | :------------------------------------------------------ |
| [.github/ISSUE_TEMPLATE/*.yml](../.github/ISSUE_TEMPLATE/)       | Adjust fields, labels, or remove templates you don't need |
| [CONTRIBUTING.md](../CONTRIBUTING.md)                             | Add project-specific contribution guidelines            |
| [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)                      | Usually fine as-is (Contributor Covenant)                |
| [labels/*.json](../labels/)                                       | Add custom labels for your workflow — see [labels.md](labels.md) |
| [codecov.yml](../codecov.yml)                                     | Coverage thresholds, flags, path exclusions              |

---

## Issue Templates

This template includes 3 issue templates plus a config file:

| Template                                                               | Purpose                    | Keep?                                     |
| :--------------------------------------------------------------------- | :------------------------- | :---------------------------------------- |
| [bug_report.yml](../.github/ISSUE_TEMPLATE/bug_report.yml)            | Report confirmed bugs      | Always                                    |
| [feature_request.yml](../.github/ISSUE_TEMPLATE/feature_request.yml)  | Suggest enhancements       | Always                                    |
| [documentation.yml](../.github/ISSUE_TEMPLATE/documentation.yml)      | Docs issues/improvements   | If you maintain docs                      |
| [config.yml](../.github/ISSUE_TEMPLATE/config.yml)                    | External links & Discussions | Customize link targets                   |

Additional templates are available in [docs/templates/issue_templates/](templates/issue_templates/)
if you need them (e.g., question, performance).

### Removing templates

Delete the `.yml` files you don't need from [.github/ISSUE_TEMPLATE/](../.github/ISSUE_TEMPLATE/).

### Customizing labels

1. Edit [labels/baseline.json](../labels/baseline.json) or [labels/extended.json](../labels/extended.json)
2. Run `python scripts/apply_labels.py --set baseline --repo OWNER/REPO`
3. Update issue template `labels:` fields to match

For the full label taxonomy, see [labels.md](labels.md).

---

## Security Policy

| Scenario                        | Use                                                                         |
| :------------------------------ | :-------------------------------------------------------------------------- |
| No bug bounty (most projects)   | [SECURITY.md](../SECURITY.md) (default) or [SECURITY_no_bounty.md](templates/SECURITY_no_bounty.md) |
| With bug bounty                 | [SECURITY_with_bounty.md](templates/SECURITY_with_bounty.md)                |
| Standalone bounty policy        | [BUG_BOUNTY.md](templates/BUG_BOUNTY.md)                                   |

### Enabling Private Vulnerability Reporting

1. Go to your repo → **Settings** → **Security** → **Code security and analysis**
2. Enable **Private vulnerability reporting**

For the security scanning CI setup, see [ADR 012](adr/012-multi-layer-security-scanning.md).

---

## GitHub Features to Enable

After creating your repo, consider enabling:

- [ ] **Discussions** — For Q&A and community conversations
- [ ] **Private vulnerability reporting** — For security issues
- [ ] **Dependabot alerts** — For dependency vulnerabilities
- [ ] **Dependabot security updates** — Auto-create PRs for vulnerable deps
- [ ] **Branch protection** — Require PR reviews, status checks (see [ADR 023](adr/023-branch-protection-rules.md))

---

## Files You Can Delete

This template ships with ~225 files. After customizing, delete anything that
doesn't apply:

| Delete                                                | If you don't need…                                                        |
| :---------------------------------------------------- | :------------------------------------------------------------------------ |
| [docs/templates/](templates/)                         | File templates (copy what you need first)                                 |
| [docs/adr/template.md](adr/template.md)              | ADR template (keep if you write ADRs)                                     |
| [experiments/](../experiments/)                        | Example experiment scripts                                                |
| [labels/extended.json](../labels/extended.json)       | Extended label set (baseline is enough)                                   |
| [Containerfile](../Containerfile), [docker-compose.yml](../docker-compose.yml) | Container support                                    |
| [.devcontainer/](../.devcontainer/)                   | VS Code Dev Container / Codespaces                                        |
| [db/](../db/), `scripts/sql/`, [var/](../var/)        | Database scaffolding                                                      |
| [requirements.txt](../requirements.txt), [requirements-dev.txt](../requirements-dev.txt) | If you only use Hatch (optional mirrors of `pyproject.toml`) |
| `site/`                                               | Built docs output (regenerated by `mkdocs build`)                         |
| [mkdocs.yml](../mkdocs.yml), `docs/` (selectively)   | If you don't need a documentation site                                    |
| [codecov.yml](../codecov.yml)                         | If you don't use Codecov for coverage reporting                           |

> **Don't forget dependent files**
> Some files depend on others. If you remove container files, also remove
> `container-build.yml` and `container-scan.yml` workflows. If you remove
> issue templates, update the label references. When in doubt, run
> `task check` after deleting.

---

## Checklist

A consolidated checklist for the full setup. Copy this into an issue or
check items off as you go.

### Initial Setup

- [ ] Clone or use "Use this template" on GitHub
- [ ] Run `python scripts/customize.py` (or replace placeholders manually)
- [ ] Run `python scripts/bootstrap.py` to set up the local environment
- [ ] Update remote URL if cloned directly

### Core Files

- [ ] Update [README.md](../README.md) with project description and badges
- [ ] Update [pyproject.toml](../pyproject.toml) — name, author, dependencies, URLs
- [ ] Update [LICENSE](../LICENSE) — year, author (or choose a different license)
- [ ] Update [SECURITY.md](../SECURITY.md) with your contact info
- [ ] Update [mkdocs.yml](../mkdocs.yml) — `site_name`, `site_url`, `repo_url`

### Source Code

- [ ] Rename `src/simple_python_boilerplate/` to your package name
- [ ] Update imports in test files to match new package name
- [ ] Update `[project.scripts]` entry points in [pyproject.toml](../pyproject.toml)
- [ ] Replace placeholder code in [src/](../src/) and [tests/](../tests/)

### GitHub Configuration

- [ ] Enable Discussions (optional)
- [ ] Enable Private vulnerability reporting
- [ ] Enable Dependabot alerts and security updates
- [ ] Set up branch protection rules — see [ADR 023](adr/023-branch-protection-rules.md)
- [ ] Apply labels: `python scripts/apply_labels.py --set baseline --repo OWNER/REPO`
- [ ] Enable workflows — see [Enabling Workflows](#enabling-workflows)

### Cleanup

- [ ] Delete [docs/templates/](templates/) (after copying what you need)
- [ ] Delete unused issue templates from [.github/ISSUE_TEMPLATE/](../.github/ISSUE_TEMPLATE/)
- [ ] Clear [CHANGELOG.md](../CHANGELOG.md) for your project's history
- [ ] Remove template-specific notes from documentation
- [ ] Add `experiments/` and `var/` to `.gitignore` if keeping those directories

### Verification

- [ ] Run `hatch shell` then `pytest` — all tests pass
- [ ] Run `task check` — all quality gates pass
- [ ] Run `task docs:build` — docs build without warnings
- [ ] Verify imports: `python -c "import your_package"`

---

## CI/CD Workflows Included

This template ships with **29 GitHub Actions workflows** in
[.github/workflows/](../.github/workflows/) covering quality, security, PR
hygiene, releases, docs, containers, and maintenance.

All are SHA-pinned ([ADR 004](adr/004-pin-action-shas.md)) and disabled by
default via repository guards ([ADR 011](adr/011-repository-guard-pattern.md)).
A single **CI Gate** workflow aggregates all required checks into one
branch-protection status ([ADR 024](adr/024-ci-gate-pattern.md)).

For the full inventory, see [workflows.md](workflows.md) or the
[workflows README](../.github/workflows/README.md).

### Enabling Workflows

All optional workflows are disabled by default via a **repository guard** — an
`if:` condition at the top of each job. Until you opt in, workflows silently
skip on forks and clones.

**Three ways to enable:**

| Method                             | How                                                                                                          | Best for                                    |
| :--------------------------------- | :----------------------------------------------------------------------------------------------------------- | :------------------------------------------ |
| **Option A — Edit the YAML**       | Replace `YOURNAME/YOURREPO` with your repo slug in each workflow file                                         | Permanent, no external config               |
| **Option B — Global variable**     | Set `vars.ENABLE_WORKFLOWS = 'true'` as a repository variable                                                 | Enable all workflows at once                |
| **Option C — Per-workflow variable** | Set `vars.ENABLE_<WORKFLOW> = 'true'` (e.g., `ENABLE_TEST`, `ENABLE_STALE`)                                  | Granular control                            |

> **Fastest approach**
> Run the customization script with the `--enable-workflows` flag:
>
> ```bash
> python scripts/customize.py --enable-workflows myorg/myproject
> python scripts/customize.py --enable-workflows myorg/myproject --dry-run  # preview
> ```

**Setting a repository variable (Options B/C):**

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions** → **Variables** tab
3. Click **New repository variable**
4. Name: `ENABLE_WORKFLOWS` (or `ENABLE_<WORKFLOW>` for individual control)
5. Value: `true`

### Disabling Workflows You Don't Need

Not every project needs all 29 workflows:

| If you don't need…         | Remove these workflows                                                    | Notes                                                                  |
| :------------------------- | :------------------------------------------------------------------------ | :--------------------------------------------------------------------- |
| Container support          | `container-build.yml`, `container-scan.yml`                               | Also delete [Containerfile](../Containerfile) and [docker-compose.yml](../docker-compose.yml) |
| Documentation site         | `docs-deploy.yml`                                                         | Keep `docs-build.yml` for CI validation of docs                        |
| Automated releases         | `release-please.yml`, `release.yml`, `sbom.yml`                          | Manual releases still work via git tags                                |
| Security scanning          | `nightly-security.yml`, `container-scan.yml`, `scorecard.yml`            | Keep `security-audit.yml` and `dependency-review.yml` at minimum       |
| Spell checking             | `spellcheck.yml`, `spellcheck-autofix.yml`                               | Also remove the typos/codespell pre-commit hooks                       |
| Auto-merge Dependabot      | `auto-merge-dependabot.yml`                                              | Review Dependabot PRs manually instead                                 |
| Stale issue cleanup        | `stale.yml`                                                              | Manage stale issues manually                                           |

> **Don't remove core quality workflows.**
> These are in the CI gate and should stay unless you're replacing them:
> `test.yml`, `lint-format.yml`, `type-check.yml`, `coverage.yml`,
> `ci-gate.yml`.

**After removing workflows:**

1. Update `REQUIRED_CHECKS` in [ci-gate.yml](../.github/workflows/ci-gate.yml)
2. Update [workflows.md](workflows.md)
3. Update branch protection if affected

### Workflow Categories

| Category          | Workflows                                                                                     | Always run?                    |
| :---------------- | :-------------------------------------------------------------------------------------------- | :----------------------------- |
| **Quality**       | test, lint-format, type-check, coverage, spellcheck                                           | Yes — in CI gate               |
| **Security**      | security-audit, bandit, dependency-review, CodeQL, container-scan, nightly, scorecard          | Mixed — some path-filtered     |
| **PR Hygiene**    | pr-title, commit-lint, labeler                                                                | Yes — in CI gate               |
| **Release**       | release-please, release, sbom                                                                 | Push to main / tags only       |
| **Documentation** | docs-build, docs-deploy                                                                       | docs-build in gate; deploy is path-filtered |
| **Container**     | container-build, container-scan                                                               | container-build in gate        |
| **Maintenance**   | pre-commit-update, stale, link-checker, auto-merge-dependabot, cache-cleanup, regenerate-files | Scheduled / event-triggered    |
| **Gate**          | ci-gate                                                                                       | Yes — the single required check |

---

## Pre-commit Hooks

[Pre-commit hooks](https://pre-commit.com/) catch problems before code leaves
your machine. This template includes **42 hooks** across four Git stages:

| Stage            | When it runs          | Examples                                                                | Count |
| :--------------- | :-------------------- | :---------------------------------------------------------------------- | ----: |
| **pre-commit**   | Every `git commit`    | Ruff lint/format, mypy, bandit, typos, deptry, YAML/TOML/JSON checks   |    35 |
| **commit-msg**   | Every `git commit`    | Commitizen — validates Conventional Commits format                      |     1 |
| **pre-push**     | Every `git push`      | pytest, pip-audit, gitleaks                                             |     3 |
| **manual**       | On demand             | markdownlint-cli2, hadolint-docker, forbid-submodules                   |     3 |

All hooks are configured in [.pre-commit-config.yaml](../.pre-commit-config.yaml).
See [ADR 008](adr/008-pre-commit-hooks.md) for the full inventory and rationale.

To install all hook stages:

```bash
task pre-commit:install
# or manually:
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit install --hook-type pre-push
```

> **New to pre-commit?** Think of hooks as automated code reviewers. Instead of
> remembering to run the linter, formatter, and tests manually before pushing,
> hooks run them for you. If a check fails, the commit or push is blocked with
> an explanation of what went wrong.

---

## File Templates

[docs/templates/](templates/) contains reusable file templates you can copy
and adapt:

| Template                                                             | Purpose                                    |
| :------------------------------------------------------------------- | :----------------------------------------- |
| [SECURITY_no_bounty.md](templates/SECURITY_no_bounty.md)            | Standard security policy (most projects)   |
| [SECURITY_with_bounty.md](templates/SECURITY_with_bounty.md)        | Security policy with bug bounty program    |
| [BUG_BOUNTY.md](templates/BUG_BOUNTY.md)                            | Standalone bug bounty policy               |
| [pull-request-draft.md](templates/pull-request-draft.md)            | PR description template                    |

Copy what you need, then delete the `docs/templates/` directory.

---

## Command Workflows

This project has **three layers** for running developer commands:
raw Python tools (pytest, ruff, mypy), Hatch (managed environments),
and a Task runner (short aliases). Each layer is optional.

See [command-workflows.md](development/command-workflows.md) for a
detailed breakdown of how `task test` → `hatch run test` → `pytest`
flows through each layer, and guidance on which to use.

---

## Containers

This template includes three container-related files
([ADR 025](adr/025-container-strategy.md)):

| File                                           | Purpose                                                                                                      | Usage                                                          |
| :--------------------------------------------- | :----------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------- |
| [Containerfile](../Containerfile)              | **Production image** — multi-stage build, minimal runtime (~150 MB)                                           | `docker build -f Containerfile .`                              |
| [docker-compose.yml](../docker-compose.yml)    | **Orchestration** — build + run locally, or multi-service setups                                              | `docker compose up --build`                                    |
| [.devcontainer/](../.devcontainer/)            | **Dev environment** — VS Code Dev Container / Codespaces                                                      | Open in VS Code → "Reopen in Container"                        |

If you don't need containers, delete `Containerfile`, `docker-compose.yml`,
and `.devcontainer/`. If you only want production containers, delete
`.devcontainer/`. If you only want the dev container, delete the other two.

---

## Documentation Stack

Ready-to-use documentation site powered by MkDocs + Material theme +
mkdocstrings ([ADR 020](adr/020-mkdocs-documentation-stack.md)).

| File / Directory                   | Purpose                                              |
| :--------------------------------- | :--------------------------------------------------- |
| [mkdocs.yml](../mkdocs.yml)       | Site configuration (theme, nav, plugins)             |
| `docs/`                           | Markdown source files                                |
| `site/`                           | Built HTML output (regenerated by `mkdocs build`)    |

```bash
task docs:serve    # Live-reload at http://localhost:8000
task docs:build    # Build (strict mode — fails on warnings)
```

**Docstring format:** mkdocstrings parses **Google-style** docstrings
(`docstring_style: google` in [mkdocs.yml](../mkdocs.yml)). Ruff enforces the
same convention (`convention = "google"` in [pyproject.toml](../pyproject.toml)).
Update both if you prefer a different style.

**To customize:**

1. Update [mkdocs.yml](../mkdocs.yml) — `site_name`, `site_url`, `repo_url`
2. Edit pages in `docs/` — add your own guides, tutorials, API docs
3. Update the `nav:` section in [mkdocs.yml](../mkdocs.yml)
4. (Optional) Enable GitHub Pages via the `docs-deploy.yml` workflow

Docs have two CI workflows:

- `docs-build.yml` — runs `mkdocs build --strict` on every PR (CI gate check)
- `docs-deploy.yml` — deploys to GitHub Pages on push to `main` (path-filtered)

If you don't need a documentation site, delete [mkdocs.yml](../mkdocs.yml)
and the docs you don't need.

---

## Further Reading

| Topic                     | Document                                                                            |
| :------------------------ | :---------------------------------------------------------------------------------- |
| Repo layout explained     | [repo-layout.md](repo-layout.md)                                                   |
| All tools at a glance     | [tooling.md](tooling.md)                                                            |
| Why each tool was chosen  | [tool-decisions.md](design/tool-decisions.md)                                       |
| Architecture overview     | [architecture.md](design/architecture.md)                                           |
| Learning resources        | [resources.md](notes/resources.md)                                                  |
| Release policy            | [releasing.md](releasing.md)                                                        |
| Contributing guide        | [CONTRIBUTING.md](../CONTRIBUTING.md)                                               |
| ADR index                 | [docs/adr/](adr/)                                                                  |

---

## Optional Tools to Consider

Not included in the template, but worth evaluating:

| Tool                                                      | Category          | When to use                                         |
| :-------------------------------------------------------- | :---------------- | :-------------------------------------------------- |
| [SQLAlchemy](https://www.sqlalchemy.org/)                 | ORM / Database    | Need a relational DB with Python models             |
| [Alembic](https://alembic.sqlalchemy.org/)                | DB Migrations     | Managing schema changes (pairs with SQLAlchemy)     |
| [FastAPI](https://fastapi.tiangolo.com/)                  | Web Framework     | Building an API (async, OpenAPI docs built-in)      |
| [Flask](https://flask.palletsprojects.com/)               | Web Framework     | Lightweight web apps and APIs                       |
| [Celery](https://docs.celeryq.dev/)                       | Task Queue        | Background / async job processing                   |
| [Sentry](https://sentry.io/)                              | Error Tracking    | Production error monitoring                         |
| [HTTPX](https://www.python-httpx.org/)                    | HTTP Client       | Modern async-capable HTTP client                    |

---

## Need Help?

- **[Troubleshooting & FAQ](guide/troubleshooting.md)** — covers common errors
  for installation, pre-commit, CI/CD, testing, linting, Git, containers, and more
- **[Learning resources](notes/resources.md)** — curated links by topic
- Open an issue on the [template repository](https://github.com/JoJo275/simple-python-boilerplate)
