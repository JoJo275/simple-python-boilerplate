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

## Research: Other Template Repos

Notes and conventions gathered from popular Python boilerplate/template repositories on GitHub.

---

### Hypermodern Python (cjolowicz)

**Repo:** [cjolowicz/hypermodern-python](https://github.com/cjolowicz/hypermodern-python)

A reference for cutting-edge Python tooling. Accompanied by a detailed blog series.

| Convention | Details |
|------------|---------|
| **Build tool** | Poetry (now Hatch is also popular) |
| **Task runner** | Nox (multi-Python testing) |
| **Type checker** | Mypy with strict mode |
| **Docs** | Sphinx + Read the Docs |
| **Pre-commit** | Extensive hooks |
| **CLI** | Click |

**Key Takeaways:**
- Uses Nox for consistent test environments across Python versions
- Separates "sessions" (lint, tests, docs, safety) in `noxfile.py`
- Coverage enforced with pytest-cov
- Sphinx autodoc for API docs from docstrings
- GitHub Actions with matrix for Python 3.9–3.12

---

### Cookiecutter PyPackage (audreyfeldroy)

**Repo:** [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage)

One of the most popular Python package templates. Uses Cookiecutter for project generation.

| Convention | Details |
|------------|---------|
| **Layout** | `src/` layout (optional, flat by default) |
| **Testing** | pytest + tox |
| **Docs** | Sphinx |
| **CI** | Travis CI (older), GitHub Actions (forks) |
| **Versioning** | bumpversion |

**Key Takeaways:**
- Generates CONTRIBUTING.rst, HISTORY.rst, AUTHORS.rst
- Includes Makefile with common targets (`make test`, `make docs`)
- Supports multiple open source licenses via prompts
- tox.ini for multi-version testing
- Bump2version for version management

---

### Python Project Template (rochacbruno)

**Repo:** [rochacbruno/python-project-template](https://github.com/rochacbruno/python-project-template)

Modern template with Copier (alternative to Cookiecutter).

| Convention | Details |
|------------|---------|
| **Build tool** | Poetry or setuptools |
| **Linting** | Ruff (replaced flake8, isort, black) |
| **Type checker** | Mypy |
| **Task runner** | Make |
| **Docs** | MkDocs (Material theme) |

**Key Takeaways:**
- Uses Copier for template updates (can pull in template changes later)
- Containerfile for OCI/Docker builds
- GitHub Actions with reusable workflows
- Conventional commits enforced
- MkDocs Material for modern-looking docs

---

### FastAPI Project Structure (tiangolo)

**Repo:** [tiangolo/full-stack-fastapi-template](https://github.com/tiangolo/full-stack-fastapi-template)

While not a general template, FastAPI projects set conventions for modern Python.

| Convention | Details |
|------------|---------|
| **Layout** | `app/` package (not `src/`) |
| **Async** | Native async/await |
| **Config** | Pydantic Settings |
| **Database** | SQLAlchemy + Alembic |
| **Testing** | pytest + httpx |

**Key Takeaways:**
- Pydantic for settings/config management with `.env` files
- Alembic for database migrations (instead of raw SQL)
- Docker Compose for local development
- Separation: `app/core/`, `app/api/`, `app/models/`, `app/crud/`
- Pre-commit with Ruff

---

### Scikit-learn Contrib Template

**Repo:** [scikit-learn-contrib/project-template](https://github.com/scikit-learn-contrib/project-template)

Template for scikit-learn compatible packages.

| Convention | Details |
|------------|---------|
| **Layout** | Flat (package at root) |
| **Testing** | pytest-cov |
| **Docs** | Sphinx + sphinx-gallery |
| **CI** | GitHub Actions + CircleCI |

**Key Takeaways:**
- Strict scikit-learn API compatibility (estimator checks)
- Example gallery generated from scripts
- Extensive docstring format (NumPy style)
- Conda + pip dual support

---

### PyScaffold

**Repo:** [pyscaffold/pyscaffold](https://github.com/pyscaffold/pyscaffold)

CLI tool that generates Python projects. Very opinionated.

| Convention | Details |
|------------|---------|
| **Layout** | `src/` layout (enforced) |
| **Config** | `pyproject.toml` + `setup.cfg` hybrid |
| **Versioning** | setuptools-scm (git tags) |
| **Docs** | Sphinx |
| **Extensions** | Plugin system |

**Key Takeaways:**
- Version derived from git tags (no manual version bumping)
- setuptools-scm for automatic versioning
- Extensions for Django, pre-commit, CI templates
- Creates `CHANGELOG.rst` (reStructuredText)
- Authors file auto-generated from git log

---

### Packaging Conventions Comparison

| Aspect | This Template | Hypermodern | Cookiecutter | PyScaffold |
|--------|---------------|-------------|--------------|------------|
| **Layout** | `src/` | `src/` | flat (default) | `src/` |
| **Config** | pyproject.toml only | pyproject.toml | setup.py/cfg | hybrid |
| **Linting** | Ruff | flake8 + plugins | flake8 | flake8 |
| **Formatting** | Ruff | Black | Black | Black |
| **Types** | Mypy | Mypy strict | optional | optional |
| **Task runner** | Make/scripts | Nox | Make + tox | tox |
| **Docs** | Markdown | Sphinx | Sphinx | Sphinx |
| **Versioning** | manual | bump2version | bumpversion | setuptools-scm |

---

### Common Patterns Observed

**Project Structure:**
- `src/` layout gaining popularity (isolation benefits)
- `tests/` at root level (not inside `src/`)
- `docs/` for documentation source files
- Flat configs in root (pyproject.toml, tox.ini, etc.)

**Configuration:**
- pyproject.toml as single source (PEP 518/621)
- Tool configs in `[tool.X]` sections
- `.env` + `.env.example` for secrets

**CI/CD:**
- GitHub Actions dominant (Travis CI declining)
- Matrix testing (Python 3.10, 3.11, 3.12, etc.)
- Separate workflows per concern
- Dependabot or Renovate for dependency updates

**Documentation:**
- Sphinx still dominant for libraries
- MkDocs + Material gaining traction
- README.md as landing page
- CHANGELOG.md with Keep a Changelog format

**Testing:**
- pytest universal
- pytest-cov for coverage
- tox or nox for multi-version
- conftest.py for shared fixtures

**Developer Experience:**
- Pre-commit hooks standard
- Makefile or justfile for common tasks
- Editorconfig for cross-editor consistency
- .vscode/ or .idea/ for IDE settings

---

### Ideas Worth Considering

From researching these templates, potential additions:

| Idea | Benefit | Complexity |
|------|---------|------------|
| **setuptools-scm** | No manual version bumping | Low |
| **Nox** | Better than tox, Python-based | Medium |
| **MkDocs** | Simpler than Sphinx, Markdown-native | Low |
| **Copier** | Template updates after adoption | Medium |
| **justfile** | Modern Makefile alternative | Low |
| **CITATION.cff** | Academic citation support | Low |
| **.editorconfig** | Cross-editor consistency | Low |

---

## Source Code File Workflow

A clean separation of concerns for the `src/` package structure.

### The Pattern

```
main.py   → starts the program (entry points, thin wrappers)
cli.py    → defines CLI contract (argument parsing, commands)
engine.py → defines behavior (core logic, interface-agnostic)
api.py    → defines callable interface (HTTP/REST, optional)
```

### File Responsibilities

| File | Purpose | Contains |
|------|---------|----------|
| `main.py` | Entry points | Thin wrappers that call cli/engine |
| `cli.py` | CLI contract | Argument parser, command definitions |
| `engine.py` | Behavior | Pure logic, no I/O, easily testable |
| `api.py` | API interface | HTTP routes, request/response handling |

### Data Flow

```
User runs command
       ↓
main.py (entry point)
       ↓
cli.py (parse args, dispatch)
       ↓
engine.py (do the work)
       ↓
Return result to cli.py
       ↓
Format output (cli.py or main.py)
       ↓
User sees result
```

### Why This Pattern?

1. **Testability** — `engine.py` has no CLI/HTTP dependencies, easy to unit test
2. **Flexibility** — Same engine can power CLI, API, GUI, etc.
3. **Clarity** — Each file has one job
4. **Maintainability** — Changes to CLI don't affect core logic

### Example

```python
# engine.py — pure logic
def process_data(data: str) -> str:
    return f"Processed: {data}"

# cli.py — CLI contract  
def run(args):
    from engine import process_data
    result = process_data(args.input)
    print(result)
    return 0

# main.py — entry point
def main():
    from cli import parse_args, run
    sys.exit(run(parse_args()))
```

### Anti-patterns to Avoid

- ❌ Business logic in `main.py`
- ❌ Argument parsing in `engine.py`
- ❌ HTTP-specific code in `engine.py`
- ❌ `print()` statements in `engine.py` (return data instead)

---

| File | Primary role | What it contains | What it must **not** contain | Who calls it | When to use it | Common mistakes |
|---|---|---|---|---|---|---|
| **`engine.py`** | Source of truth (core logic) | Pure functions/classes that implement real behavior | CLI parsing, printing, shell commands, repo-specific assumptions | `api.py`, tests, other Python code | Always when behavior is non-trivial or reusable | Mixing I/O or argument parsing into core logic |
| **`api.py`** | Stable internal interface | Thin wrappers that expose intentional operations (e.g. `run_lint`, `build`) | Implementation details, argument parsing | `cli.py`, `main.py`, other tools | When you want a clean boundary and refactor safety | Making it a duplicate of `engine.py` with no added value |
| **`cli.py`** | Command-line interface | Argument parsing, subcommands, help text | Business logic, complex workflows | End users, developers, Just, CI | When providing an installable CLI | Putting real logic directly in CLI handlers |
| **`main.py`** | Entry point / bootstrap | Calls into `api.py` or `engine.py` to start execution | Logic, configuration rules | Python runtime (`python main.py`) | Optional; useful for quick execution or demos | Letting it grow into the main implementation file |

Decision rules (read top → bottom)

If someone outside this repo needs to run it → installable CLI
If only contributors need it → task runner (Just)
If it expresses real behavior → core logic
If it just wires things together → orchestration

Canonical decision table
| Question | Yes → Do this | No → Do this |
|---|---|---|
| Does this define real behavior (rules, algorithms, decisions)? | Put it in **core logic** (`engine.py` / `core/`) | Continue |
| Should this behavior be callable by other code or tools? | Expose via **installable CLI** (and/or API) | Continue |
| Is this meant to be run outside this repo? | **Installable CLI command** | Continue |
| Is this only for contributors working on this repo? | **Just task** | Continue |
| Is this repo-specific glue (order of steps, flags, paths)? | **Just task or script** | Continue |
| Is this a one-off or disposable automation? | **Script** | Re-evaluate |

What each bucket is responsible for
| Tool / Layer | Purpose | Source of truth? | Versioned? | Audience |
|---|---|---|---|---|
| Core logic | Implements behavior | ✅ Yes | With code | Everyone |
| Installable CLI | Defines public commands | ✅ Yes | Yes | Users / devs |
| Just (task runner) | Orchestrates commands | ❌ No | With repo | Contributors |
| Scripts | One-off helpers | ❌ No | Optional | Maintainers |
| CI workflows | Automation | ❌ No | With repo | CI only |

Concrete examples (grounding the rules)
| Action | Correct place | Why |
|---|---|---|
| Lint Python files | Installable CLI (`mytool lint`) | Reusable, meaningful behavior |
| Run lint + format + tests | Just (`just check`) | Repo workflow |
| Build and publish release | CLI (`mytool release`) | Stable, versioned behavior |
| Clean `.pytest_cache` | Just or script | Repo-specific cleanup |
| Bootstrap venv | Just | Developer convenience |
| Parse config file | Core logic | Behavior, not orchestration |
| Call multiple tools in order | Just | Pure glue |






## Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [Hynek's Testing & Packaging](https://hynek.me/articles/testing-packaging/)
- [Real Python: Python Packaging](https://realpython.com/pypi-publish-python-package/)
