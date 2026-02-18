# Copilot Code Review Instructions

Guidelines for GitHub Copilot when reviewing code in this repository.

## Project Overview

A Python boilerplate project using:
- **src/ layout** — All package code lives in `src/simple_python_boilerplate/`
- **pyproject.toml** — Single configuration file for all tools
- **pytest** — Testing framework
- **Ruff** — Linting and formatting
- **GitHub Actions** — CI/CD with pinned action SHAs

## Review Priorities

### High Priority
1. **Type hints** — Public functions should have type annotations (public = exported API and anything not prefixed with `_` in `src/`)
2. **Tests** — Changes should include or update relevant tests
3. **Security** — Flag:
   - Hardcoded credentials, secrets, API keys
   - SQL injection risks
   - `subprocess` with `shell=True` (prefer `shell=False` with argument list)
   - Unsafe `yaml.load()` (use `yaml.safe_load()`)
   - Logging secrets or tokens
4. **Import errors** — Ensure imports work with src/ layout (must be installed)

### Medium Priority
5. **Docstrings** — Public functions should have docstrings
6. **Error handling** — Appropriate exception handling
7. **Naming** — Clear, descriptive variable and function names

### Low Priority
8. **Comments** — Helpful but not excessive
9. **Code style** — Ruff handles most of this automatically

### General Guidance
- **Prefer minimal diffs** — Avoid stylistic rewrites; Ruff already enforces formatting
- **Don't churn** — Only suggest changes that add clear value
- **Never install packages globally** — Always install into the active virtual environment (`.venv`) or a Hatch-managed environment. Never run bare `pip install <package>` outside a venv. Use `pip install -e ".[dev]"` for project dependencies, `hatch env create` for Hatch environments, or `pipx` for standalone CLI tools. If no venv is active, create or activate one first.

## Conventions

### Python
- Use absolute imports: `from simple_python_boilerplate.module import func`
- Type hints for all public functions and methods
- Type checking uses **mypy** (strict mode) — prefer fixes compatible with mypy
- Docstrings in Google style format
- Constants in UPPER_SNAKE_CASE

### Project Structure
- Source code in `src/simple_python_boilerplate/`
- Tests in `tests/`
- Scripts in `scripts/`
- Documentation in `docs/`

### Git & PRs
- Conventional commit messages: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`
- Use `ci:` for workflow-only changes, `docs:` for docs-only changes, `chore:` for maintenance
- One logical change per commit
- PR titles follow conventional commit format

### Commit Message Format

When generating commit messages, follow the template in `.gitmessage.txt`:

```
<type>(<scope>): <description>

Why: <motivation for the change>

What changed: <summary of changes>

How tested: <how the change was verified>

Breaking change: <describe if applicable, otherwise omit>

Issues/Refs: #<issue number if applicable, otherwise omit>
```

- **type** — `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- **scope** — optional area affected (e.g., `cli`, `docs`, `ci`)
- **description** — imperative mood, lowercase, no period, max 50 chars
- Body sections (`Why`, `What changed`, `How tested`) should be included for non-trivial commits
- Omit `Breaking change` and `Issues/Refs` sections when not applicable

### CI/CD
- GitHub Actions pinned to full commit SHAs (not tags)
- Workflows separated by concern (e.g., test, lint, release)

## Ignore / Don't Flag

- **Line length (E501)** — Disabled in this project; don't request rewrapping docstrings or comments unless readability is impacted
- **Generated files** — `*.egg-info/`, `__pycache__/`, `.venv/`
- **Types in tests** — Be less strict; don't require full annotations for mocks, fixtures, or test helpers. Don't require annotations for pytest fixtures unless they clarify intent.

## Architecture Decisions

Key decisions are documented in `docs/adr/`:
- ADR 001: src/ layout for package structure
- ADR 002: pyproject.toml for all configuration
- ADR 003: Separate GitHub Actions workflow files
- ADR 004: Pin GitHub Actions to commit SHAs

## Common Issues to Catch

1. **Missing `pip install -e .`** — If running from source, use editable install so imports resolve with src/ layout
2. **Import from wrong location** — Should import from `simple_python_boilerplate`, not `src`
3. **Mutable default arguments** — `def func(items=[])` is a bug
4. **Bare except clauses** — Should catch specific exceptions
5. **Unused imports/variables** — Ruff catches these, but flag if missed
