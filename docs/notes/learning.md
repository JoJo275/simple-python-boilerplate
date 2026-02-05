# Learning Notes

Personal notes and learnings captured while building this project.

## Python Packaging

### The `src/` Layout Mystery (Solved)

**Problem:** Tests fail with `ModuleNotFoundError` even though code is right there.

**Why:** Python doesn't automatically look inside `src/`. The `src/` layout is *intentionally* strict — it forces you to install the package properly.

**Solution:** Always run `pip install -e .` after cloning. The `-e` (editable) flag links your source so changes reflect immediately.

### pyproject.toml vs setup.py

- `setup.py` = Old way (executable Python, security concerns)
- `pyproject.toml` = New way (declarative TOML, standard)

Most tools now read from `[tool.X]` sections in pyproject.toml. One file to rule them all.

---

## GitHub Actions

### Why Pin to SHAs?

Tags like `@v4` are mutable — someone could push malicious code and move the tag. SHAs are immutable. Always pin to full SHA with a version comment:

```yaml
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

### Workflow Organization

Separate files > one giant file:
- Easier to disable (just rename to `_workflow.yml`)
- Each gets its own permissions
- Failures are isolated

---

## Static Analysis Tools

| Tool | Purpose | Speed |
|------|---------|-------|
| **Ruff** | Linting + formatting | ⚡ Very fast (Rust) |
| **Mypy** | Type checking | 🐢 Slower |
| **Pyright** | Type checking (VS Code) | ⚡ Fast |
| **Bandit** | Security scanning | 🐢 Moderate |

**Ruff** replaces: flake8, isort, black, pyupgrade, and more. One tool, one config.

---

## Quality Gates

A **quality gate** is a checkpoint that code must pass before moving forward (e.g., merging to main, deploying to production).

### Common Quality Gates in CI

| Gate | What It Checks | Tool |
|------|----------------|------|
| **Tests pass** | Code works as expected | pytest |
| **Linting passes** | Code style, bugs | Ruff |
| **Type checking passes** | Type correctness | Mypy/Pyright |
| **Coverage threshold** | Enough tests exist | pytest-cov |
| **Security scan** | No vulnerabilities | Bandit, pip-audit |
| **Spell check** | No typos | codespell |

### Enforcing Quality Gates

1. **GitHub Branch Protection** — Require status checks to pass before merge
2. **CI Workflow** — Each job is a gate; if one fails, PR can't merge
3. **Pre-commit Hooks** — Catch issues before they even reach CI

### Soft vs Hard Gates

- **Hard gate** — Must pass (blocks merge/deploy)
- **Soft gate** — Informational only (warns but doesn't block)

Example: When adopting type checking, start with a soft gate (`continue-on-error: true`) while adding type hints gradually.

### Why Quality Gates Matter

- Catch bugs early (cheaper to fix)
- Maintain code consistency
- Build confidence in deployments
- Document quality expectations

---

## Virtual Environments

### Quick Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # macOS/Linux
pip install -e ".[dev]"
```

### Check Which Python

```bash
python -c "import sys; print(sys.executable)"
```

If it doesn't show `.venv`, you're using the wrong Python!

---

## Pre-commit Hooks

Pre-commit hooks run checks *before* code is committed, catching issues locally before they reach CI.

### Setup

```bash
pip install pre-commit
pre-commit install
```

### Configuration (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff          # Linting
        args: [--fix]
      - id: ruff-format   # Formatting

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.1
    hooks:
      - id: mypy
        additional_dependencies: []

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Key Commands

| Command | Purpose |
|---------|---------|
| `pre-commit install` | Enable hooks for this repo |
| `pre-commit run --all-files` | Run on all files (not just staged) |
| `pre-commit autoupdate` | Update hook versions |
| `git commit --no-verify` | Skip hooks (emergency only!) |

### Why Pre-commit > Manual Checks

- **Automatic** — Can't forget to run it
- **Fast feedback** — Fix before pushing
- **Consistent** — Same checks for everyone
- **CI friendly** — Run same hooks in CI as backup

---

## GitHub Actions Workflows

### Anatomy of a Workflow

```yaml
name: Tests                        # Display name

on:                                # Triggers
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:                       # Least-privilege access
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@...  # Pinned SHA
      - uses: actions/setup-python@...
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest
```

### Common Workflow Patterns

| Workflow | Triggers | Purpose |
|----------|----------|---------|
| `test.yml` | push, PR | Run tests |
| `lint.yml` | push, PR | Ruff, mypy |
| `release.yml` | tag push | Publish to PyPI |
| `security.yml` | schedule, PR | Dependency audits |

### Matrix Testing

Test across multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
    os: [ubuntu-latest, windows-latest]
```

### Caching Dependencies

Speed up workflows by caching pip:

```yaml
- uses: actions/setup-python@...
  with:
    python-version: "3.11"
    cache: "pip"
```

### Useful Actions

| Action | Purpose |
|--------|---------|
| `actions/checkout` | Clone repo |
| `actions/setup-python` | Install Python |
| `actions/cache` | Cache dependencies |
| `codecov/codecov-action` | Upload coverage |
| `pypa/gh-action-pypi-publish` | Publish to PyPI |

---

## Branch Protection

Branch protection prevents direct pushes to important branches and enforces quality gates.

### Setting Up (GitHub)

**Settings → Branches → Add rule**

### Recommended Settings for `main`

| Setting | Purpose |
|---------|---------|
| ✅ Require PR before merging | No direct pushes |
| ✅ Require status checks | CI must pass |
| ✅ Require branches up to date | Must merge main first |
| ✅ Require conversation resolution | All comments addressed |
| ⬜ Require approvals | Set to 1+ for teams |
| ⬜ Restrict who can push | Limit to admins |

### Required Status Checks

Add these as required checks:
- `test` — Tests pass
- `lint` — Linting passes
- `type-check` — Types are correct

### Bypassing (Emergency)

Admins can bypass, but it's logged. Use sparingly!

---

## Security Scanning

### Tools Overview

| Tool | What It Does | When to Run |
|------|--------------|-------------|
| **pip-audit** | Checks deps for CVEs | CI, pre-release |
| **Bandit** | Finds security bugs in code | CI, pre-commit |
| **Safety** | Dependency vulnerabilities | CI |
| **Trivy** | Container scanning | CI (Docker builds) |
| **Dependabot** | Auto-creates upgrade PRs | Scheduled |

### pip-audit in CI

```yaml
- name: Security audit
  run: |
    pip install pip-audit
    pip-audit
```

### Bandit in CI

```yaml
- name: Security scan
  run: |
    pip install bandit
    bandit -r src/ -ll
```

### Dependabot Configuration (`.github/dependabot.yml`)

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      dev-dependencies:
        patterns:
          - "pytest*"
          - "ruff"
          - "mypy"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Automation Strategy

### The Three Lines of Defense

1. **Pre-commit hooks** — Catch issues locally, instant feedback
2. **CI workflows** — Catch anything that slips through, authoritative
3. **Branch protection** — Enforce that CI passes before merge

### What to Run Where

| Check | Pre-commit | CI | Why |
|-------|------------|-----|-----|
| Formatting | ✅ | ✅ | Fast, catches everything |
| Linting | ✅ | ✅ | Fast, catches everything |
| Type checking | ⚠️ Optional | ✅ | Can be slow locally |
| Tests | ❌ | ✅ | Too slow for commit hook |
| Security scan | ❌ | ✅ | Needs network, slow |
| Coverage | ❌ | ✅ | Needs full test run |

### Progressive Adoption

1. **Start with CI** — Get workflows running first
2. **Add branch protection** — Enforce CI passes
3. **Add pre-commit** — Speed up feedback loop
4. **Tune thresholds** — Gradually increase strictness

---

## Things I Keep Forgetting

1. **Import name ≠ package name** — `simple-python-boilerplate` (hyphen) installs, but you `import simple_python_boilerplate` (underscore)

2. **`__init__.py` is still needed** — Even in Python 3, include it for tooling compatibility

3. **Editable install is required** — With `src/` layout, you must install to import

4. **pytest needs the package installed** — Or it won't find your modules

---

## Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [Hynek's Testing & Packaging](https://hynek.me/articles/testing-packaging/)
- [Real Python: Python Packaging](https://realpython.com/pypi-publish-python-package/)
