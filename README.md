# simple-python-boilerplate

A modern Python project template with `src/` layout, automated CI/CD, and batteries-included tooling.

<!-- TODO (template users): Replace 'JoJo275/simple-python-boilerplate' with your repo slug -->
[![CI](https://github.com/JoJo275/simple-python-boilerplate/actions/workflows/ci-gate.yml/badge.svg)](https://github.com/JoJo275/simple-python-boilerplate/actions/workflows/ci-gate.yml)
[![Coverage](https://codecov.io/gh/JoJo275/simple-python-boilerplate/branch/main/graph/badge.svg)](https://codecov.io/gh/JoJo275/simple-python-boilerplate)
[![License](https://img.shields.io/github/license/JoJo275/simple-python-boilerplate)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## What's Included

| Category | Tools |
|----------|-------|
| **Build** | Hatchling + hatch-vcs (version from git tags) |
| **Environments** | Hatch (virtualenv management, test matrix) |
| **Linting** | Ruff (lint + format), mypy (strict), bandit (security) |
| **Testing** | pytest, pytest-cov, Python 3.11-3.13 matrix |
| **Pre-commit** | 34+ hooks across 3 stages (commit, commit-msg, push) |
| **CI/CD** | 26 GitHub Actions workflows, SHA-pinned |
| **Docs** | MkDocs Material + mkdocstrings, auto-deploy to GitHub Pages |
| **Release** | release-please -> automated changelog + versioning |
| **Security** | CodeQL, pip-audit, Trivy, dependency-review, gitleaks |
| **Container** | Multi-stage Containerfile with scan |

## Quick Start

### Prerequisites

- Python **3.11+**
- [Hatch](https://hatch.pypa.io/) (`pipx install hatch`)
- [Task](https://taskfile.dev/) (optional, for convenience commands)

### Setup

```bash
# Clone and enter the project
git clone https://github.com/YOURNAME/YOURREPO.git
cd YOURREPO

# Enter the dev environment (installs everything automatically)
hatch shell

# Install all git hooks
task pre-commit:install
```

### Daily Workflow

```bash
task test              # Run tests
task test:cov          # Run tests with coverage
task test:matrix       # Run across Python 3.11-3.13
task lint              # Check linting issues
task lint:fix          # Auto-fix linting issues
task fmt               # Apply formatting
task typecheck         # Run mypy
task check             # All quality gates at once
task docs:serve        # Live-reload docs at localhost:8000
task docs:build        # Build docs (strict mode)
task security          # Run bandit security linter
```

> No Task installed? Use `hatch run <command>` directly (e.g., `hatch run test`).

### Alternative: pip

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -e ".[dev]"
pytest
```

## Project Structure

```
src/simple_python_boilerplate/   # Package source (src/ layout)
tests/unit/                      # Unit tests
tests/integration/               # Integration tests
docs/                            # MkDocs documentation
scripts/                         # Developer utility scripts
.github/workflows/               # 26 CI/CD workflows
db/                              # Database schema, migrations, seeds
```

See [docs/repo-layout.md](docs/repo-layout.md) for the full annotated tree.

## CLI Entry Points

```bash
spb              # Main CLI command
spb-version      # Print version info
spb-doctor       # Diagnose environment issues
```

## CI/CD Pipeline

Every push and PR triggers automated checks:

- **Quality:** Ruff lint/format, mypy strict, codespell, test matrix (3.11-3.13), coverage
- **Security:** bandit, pip-audit, CodeQL, dependency-review, Trivy, gitleaks
- **PR:** title validation, auto-labeler, spellcheck autofix
- **Release:** release-please changelog, SBOM generation
- **Gate:** Single `ci-gate` check for branch protection ([ADR 024](docs/adr/024-ci-gate-pattern.md))

All actions are SHA-pinned ([ADR 004](docs/adr/004-pin-action-shas.md)) with repository guards ([ADR 011](docs/adr/011-repository-guard-pattern.md)).

See [docs/workflows.md](docs/workflows.md) for the full workflow inventory.

## Utility Scripts

| Script | Purpose |
|--------|---------|
| `scripts/repo_doctor.py` | Health checker with `--fix` support |
| `scripts/dep_versions.py` | Show/update dependency versions |
| `scripts/workflow_versions.py` | Show/update SHA-pinned action versions |
| `scripts/apply_labels.py` | Apply GitHub labels (`--set baseline\|extended`) || `scripts/check_todos.py` | Scan for `TODO (template users)` comments |
| `scripts/customize.py` | Interactive project customization (placeholders, license, optional dirs) |
| `scripts/env_doctor.py` | Quick environment health check |
| `scripts/changelog_check.py` | Verify CHANGELOG.md matches git tags |
## Using This Template

See [docs/USING_THIS_TEMPLATE.md](docs/USING_THIS_TEMPLATE.md) for a step-by-step setup guide.

**Quick checklist:**

1. Click "Use this template" on GitHub
2. Replace `simple-python-boilerplate` / `simple_python_boilerplate` with your project name
3. Update `pyproject.toml` (name, description, URLs, author)
4. Update `mkdocs.yml` (`site_url`, `repo_url`, `site_name`)
5. Delete placeholder code in `src/` and `tests/`
6. Enable repository guards via repository variables (see [ADR 011](docs/adr/011-repository-guard-pattern.md))
7. Install labels: `python scripts/apply_labels.py --set baseline --repo OWNER/REPO`

## Documentation

- **Live docs:** `task docs:serve` at [localhost:8000](http://127.0.0.1:8000)
- **Architecture decisions:** [docs/adr/](docs/adr/)
- **Developer guides:** [docs/development/](docs/development/)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

## License

Apache License 2.0 - see [LICENSE](LICENSE).
