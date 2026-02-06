# Repository Layout

Full annotated structure of this repository with details on what each component does and what breaks if removed.

For a quick overview, see the [Repository Layout](#repository-layout) section in the main [README](../README.md).

---

## Directory Tree

```
simple-python-boilerplate/
├── .github/                    # GitHub-specific configuration
│   ├── dependabot.yml          # Automated dependency updates
│   ├── ISSUE_TEMPLATE/         # Issue templates (bug, feature, etc.)
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/              # GitHub Actions CI/CD
│       ├── lint-format.yml     # Ruff linting and formatting
│       ├── release.yml         # Build artifacts on tag push
│       ├── spellcheck.yml      # Codespell typo checking
│       ├── test.yml            # Pytest across Python versions
│       └── _*.yml              # Disabled workflows (underscore prefix)
│
├── db/                         # Database assets (optional)
│   ├── migrations/             # Schema migration scripts
│   ├── queries/                # Reusable SQL queries
│   ├── seeds/                  # Sample/test data
│   └── schema.sql              # Database schema definition
│
├── docs/                       # Project documentation
│   ├── adr/                    # Architecture Decision Records
│   ├── design/                 # Architecture and database design
│   ├── development/            # Developer guides
│   ├── notes/                  # Personal learning notes
│   ├── templates/              # Reusable file templates
│   ├── release-policy.md       # Versioning and release policy
│   ├── releasing.md            # How to create releases
│   ├── repo-layout.md          # This file
│   └── workflows.md            # GitHub Actions reference
│
├── experiments/                # Scratch space for exploration
│
├── labels/                     # GitHub label definitions
│   ├── baseline.json           # Core labels
│   └── extended.json           # Additional labels
│
├── scripts/                    # Developer/maintenance scripts
│   ├── apply_labels.py         # Sync labels to GitHub
│   └── sql/                    # SQL utility scripts
│
├── src/                        # Source code (package root)
│   └── simple_python_boilerplate/
│       ├── __init__.py         # Package initialization, version
│       ├── api.py              # Programmatic interface
│       ├── cli.py              # Command-line interface
│       ├── engine.py           # Core business logic
│       ├── main.py             # Entry points
│       └── dev_tools/          # Development utilities
│
├── tests/                      # Test suite
│   ├── integration/            # Integration tests
│   ├── unit/                   # Unit tests
│   └── unit_test.py            # Legacy test file
│
├── var/                        # Runtime/generated files
│   └── app.example.sqlite3     # Example database file
│
├── .gitattributes              # Git file handling rules
├── .gitignore                  # Files excluded from git
├── .pre-commit-config.yaml     # Pre-commit hook configuration
├── CHANGELOG.md                # Version history
├── CODE_OF_CONDUCT.md          # Community guidelines
├── CONTRIBUTING.md             # Contribution guidelines
├── LICENSE                     # Project license (Apache-2.0)
├── pyproject.toml              # Project metadata and tool config
├── README.md                   # Project overview
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── SECURITY.md                 # Security policy
└── simple-python-boilerplate.code-workspace  # VS Code workspace
```

---

## Component Details

### Core (Required)

These are essential for the package to function.

| Path | Purpose | What Breaks If Removed |
|------|---------|------------------------|
| `src/simple_python_boilerplate/` | Package source code | Everything — no package to import |
| `src/simple_python_boilerplate/__init__.py` | Package marker, exports version | Package won't be recognized |
| `pyproject.toml` | Build config, metadata, tool settings | Can't install, build, or configure tools |
| `LICENSE` | Legal terms | License compliance issues |

### Testing

| Path | Purpose | What Breaks If Removed |
|------|---------|------------------------|
| `tests/` | Test suite | No tests to run, CI fails |
| `tests/unit/` | Unit tests | Reduced test coverage |
| `tests/integration/` | Integration tests | Can't verify component interactions |

### CI/CD

| Path | Purpose | What Breaks If Removed |
|------|---------|------------------------|
| `.github/workflows/test.yml` | Run tests on push/PR | No automated testing |
| `.github/workflows/lint-format.yml` | Code quality checks | Formatting issues slip through |
| `.github/workflows/release.yml` | Build on version tags | Manual build required |
| `.github/dependabot.yml` | Dependency updates | Manual dependency management |

See [workflows.md](workflows.md) for full workflow documentation.

### Documentation

| Path | Purpose | What Breaks If Removed |
|------|---------|------------------------|
| `README.md` | Project overview | No landing page |
| `CONTRIBUTING.md` | Contribution guide | Contributors lack guidance |
| `docs/` | Detailed documentation | Missing context for developers |
| `docs/adr/` | Decision records | Lost architectural context |
| `CHANGELOG.md` | Version history | No release notes |

### Development Experience

| Path | Purpose | What Breaks If Removed |
|------|---------|------------------------|
| `.pre-commit-config.yaml` | Pre-commit hooks | Local checks disabled |
| `requirements-dev.txt` | Dev dependencies list | Unclear what to install |
| `.gitignore` | Exclude generated files | Caches committed to git |
| `.gitattributes` | Line ending normalization | Cross-platform issues |

### Optional Components

These can be removed without breaking core functionality.

| Path | Purpose | Safe to Remove? |
|------|---------|-----------------|
| `db/` | Database assets | ✅ If not using a database |
| `experiments/` | Scratch space | ✅ Personal exploration |
| `labels/` | GitHub labels | ✅ Manual label management |
| `scripts/` | Utility scripts | ✅ Convenience only |
| `var/` | Runtime files | ✅ Example data |
| `docs/notes/` | Personal notes | ✅ Learning reference |
| `docs/templates/` | File templates | ✅ Copy as needed |

---

## Source Code Architecture

```
src/simple_python_boilerplate/
├── __init__.py     # Package exports, version
├── main.py         # Entry points (thin wrappers)
├── cli.py          # CLI argument parsing
├── engine.py       # Core business logic
├── api.py          # Programmatic interface
└── dev_tools/      # Development utilities
    ├── __init__.py
    └── clean.py    # Cache cleanup
```

### Data Flow

```
User → main.py → cli.py → engine.py → result
              ↘ api.py ↗
```

### Key Principle

> Logic lives in `engine.py`. Interfaces (`cli.py`, `api.py`) adapt it.

See [docs/notes/learning.md](notes/learning.md#source-code-file-workflow) for detailed architecture notes.

---

## Configuration Files

### pyproject.toml Sections

| Section | Purpose |
|---------|---------|
| `[build-system]` | How to build the package |
| `[project]` | Name, version, dependencies |
| `[project.optional-dependencies]` | Dev/test extras |
| `[project.scripts]` | CLI entry points |
| `[tool.ruff]` | Linter configuration |
| `[tool.mypy]` | Type checker configuration |
| `[tool.pytest]` | Test runner configuration |

### Other Config Files

| File | Tool | Purpose |
|------|------|---------|
| `.pre-commit-config.yaml` | pre-commit | Git hook definitions |
| `.github/dependabot.yml` | Dependabot | Dependency update rules |
| `requirements.txt` | pip | Production dependencies |
| `requirements-dev.txt` | pip | Development dependencies |

---

## Naming Conventions

| Pattern | Meaning | Example |
|---------|---------|---------|
| `_filename.yml` | Disabled workflow | `_spellcheck-autofix.yml` |
| `test_*.py` | Test file | `test_example.py` |
| `*.example.*` | Example/template file | `app.example.sqlite3` |
| `__init__.py` | Package marker | Required in all packages |
| `__pycache__/` | Python bytecode cache | Never commit |

---

## What to Remove When Adopting

If you're using this template, consider removing:

| Path | When to Remove |
|------|----------------|
| `docs/notes/` | After reading, personal learning |
| `experiments/` | After exploration |
| `var/app.example.sqlite3` | Replace with your data |
| `docs/templates/` | After copying what you need |
| `db/` | If not using a database |

---

## See Also

- [README.md](../README.md) — Quick overview
- [CONTRIBUTING.md](../CONTRIBUTING.md) — How to contribute
- [workflows.md](workflows.md) — CI/CD workflows
- [releasing.md](releasing.md) — Release process
- [ADR index](adr/README.md) — Architecture decisions
