# Learning Resources

Curated links to documentation, tutorials, and references for the tools and
patterns used in this project. Organized by topic for quick lookup.

---

## Python Packaging & Project Structure

| Resource | Description |
|----------|-------------|
| [Python Packaging User Guide](https://packaging.python.org/) | Official guide — covers pyproject.toml, src/ layout, builds, and publishing |
| [PEP 621 — Project metadata](https://peps.python.org/pep-0621/) | The standard for declaring metadata in pyproject.toml |
| [PEP 517 — Build system interface](https://peps.python.org/pep-0517/) | How build backends (Hatchling, setuptools) work under the hood |
| [src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) | Official comparison — why we chose src/ ([ADR 001](../adr/001-src-layout.md)) |
| [Hatch documentation](https://hatch.pypa.io/) | Project manager used for environments, builds, and scripts |
| [Hatchling documentation](https://hatch.pypa.io/latest/build/) | Build backend configuration |

## Testing

| Resource | Description |
|----------|-------------|
| [pytest documentation](https://docs.pytest.org/) | Test framework — fixtures, parametrize, markers, plugins |
| [pytest-cov](https://pytest-cov.readthedocs.io/) | Coverage plugin for pytest |
| [Effective Python Testing with pytest (Real Python)](https://realpython.com/pytest-python-testing/) | Practical tutorial covering fixtures, marks, and parametrize |
| [Testing Best Practices (The Hitchhiker's Guide)](https://docs.python-guide.org/writing/tests/) | General Python testing guidance |

## Linting, Formatting & Type Checking

| Resource | Description |
|----------|-------------|
| [Ruff documentation](https://docs.astral.sh/ruff/) | Linter + formatter — rules reference, configuration |
| [Ruff rule index](https://docs.astral.sh/ruff/rules/) | Searchable index of all lint rules by code |
| [mypy documentation](https://mypy.readthedocs.io/) | Static type checker — configuration, error codes, stubs |
| [mypy cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) | Quick reference for type annotations |
| [typing module docs](https://docs.python.org/3/library/typing.html) | Standard library typing reference |

## Pre-commit Hooks

| Resource | Description |
|----------|-------------|
| [pre-commit documentation](https://pre-commit.com/) | Hook framework — installation, configuration, creating hooks |
| [pre-commit hook directory](https://pre-commit.com/hooks.html) | Searchable directory of available hooks |
| [Supported hooks in this project](../adr/008-pre-commit-hooks.md) | Full inventory of hooks used here (ADR 008) |

## GitHub Actions & CI/CD

| Resource | Description |
|----------|-------------|
| [GitHub Actions documentation](https://docs.github.com/en/actions) | Official docs — workflows, syntax, runners, expressions |
| [Workflow syntax reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions) | Complete YAML syntax for workflow files |
| [GitHub Actions expressions](https://docs.github.com/en/actions/learn-github-actions/expressions) | `${{ }}` expression syntax, contexts, functions |
| [Security hardening for Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions) | Best practices — permissions, SHA pinning, secrets |
| [actionlint](https://github.com/rhysd/actionlint) | Workflow linter — catches errors before pushing |
| [act](https://github.com/nektos/act) | Run GitHub Actions locally for faster iteration |

## Security Tools

| Resource | Description |
|----------|-------------|
| [Bandit documentation](https://bandit.readthedocs.io/) | Python security linter — issue types, configuration |
| [pip-audit](https://github.com/pypa/pip-audit) | Vulnerability scanning for Python dependencies |
| [gitleaks](https://github.com/gitleaks/gitleaks) | Secret detection in git repositories |
| [Trivy](https://aquasecurity.github.io/trivy/) | Container and dependency vulnerability scanner |
| [OpenSSF Scorecard](https://securityscorecards.dev/) | Supply-chain security scoring |
| [OWASP Python Security](https://cheatsheetseries.owasp.org/cheatsheets/Python_Security_Cheat_Sheet.html) | Python-specific security cheat sheet |

## Documentation (MkDocs)

| Resource | Description |
|----------|-------------|
| [MkDocs documentation](https://www.mkdocs.org/) | Static site generator for project docs |
| [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) | Theme used in this project — features, customization |
| [mkdocstrings](https://mkdocstrings.github.io/) | Auto-generate API docs from Python docstrings |
| [Google Python Style Guide — Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) | Docstring convention used in this project |

## Containers

| Resource | Description |
|----------|-------------|
| [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) | Syntax reference for Containerfile / Dockerfile |
| [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/) | Pattern used in our Containerfile for minimal images |
| [Podman documentation](https://docs.podman.io/) | Daemonless container engine (alternative to Docker) |
| [Dev Containers specification](https://containers.dev/) | Standard for development containers (VS Code / Codespaces) |

## Git & Conventional Commits

| Resource | Description |
|----------|-------------|
| [Conventional Commits](https://www.conventionalcommits.org/) | Commit message convention used in this project |
| [commitizen](https://commitizen-tools.github.io/commitizen/) | CLI tool for authoring conventional commits |
| [release-please](https://github.com/googleapis/release-please) | Automated release management from conventional commits |

## Architecture Decision Records

| Resource | Description |
|----------|-------------|
| [ADR overview (adr.github.io)](https://adr.github.io/) | What ADRs are and why they matter |
| [Michael Nygard's ADR article](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | Original blog post that popularized ADRs |
| [MADR template](https://adr.github.io/madr/) | Markdown ADR template (similar to ours) |

## General Python

| Resource | Description |
|----------|-------------|
| [Python documentation](https://docs.python.org/3/) | Official language and stdlib reference |
| [Real Python](https://realpython.com/) | High-quality tutorials and guides |
| [The Hitchhiker's Guide to Python](https://docs.python-guide.org/) | Best practices for Python development |
| [PEP 8 — Style Guide](https://peps.python.org/pep-0008/) | The foundational Python style guide (Ruff enforces most of this) |
| [Python Type Hints cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) | Quick reference for common type patterns |

---

## How to Use This Page

- **New to the project?** Start with the Python Packaging and Testing sections
- **Setting up CI?** GitHub Actions and Security Tools sections
- **Writing docs?** MkDocs section and the Google docstring guide
- **Making an architectural decision?** ADR section for the template and process

This is a living document — add links as you discover useful resources and
remove ones that go stale.
