# Developer Commands

Quick reference for common development commands in this project.

## Environment Setup

### Using Hatch (recommended)

```bash
# Enter the dev environment (creates venv + installs deps automatically)
hatch shell

# Or run commands directly without entering the shell
hatch run <command>
```

### Using pip + venv (manual)

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Testing

```bash
# Run all tests
hatch run test

# Run with verbose output
hatch run test -v

# Run specific test file
hatch run test tests/unit_test.py

# Run with coverage
hatch run test-cov
```

<details>
<summary>Without Hatch (direct commands)</summary>

```bash
pytest
pytest -v
pytest tests/unit_test.py
pytest --cov=simple_python_boilerplate --cov-report=term-missing
```
</details>

## Linting & Formatting

```bash
# Check for linting issues
hatch run lint

# Auto-fix linting issues
hatch run lint-fix

# Check formatting
hatch run fmt-check

# Apply formatting
hatch run fmt
```

<details>
<summary>Without Hatch (direct commands)</summary>

```bash
ruff check .
ruff check --fix .
ruff format --check .
ruff format .
```
</details>

## Type Checking

```bash
# Run mypy
hatch run typecheck
```

<details>
<summary>Without Hatch (direct commands)</summary>

```bash
mypy src/
mypy --strict src/
```
</details>

## Building

```bash
# Build source and wheel distributions
hatch build

# Clean build artifacts
hatch clean
```

<details>
<summary>Without Hatch (direct commands)</summary>

```bash
pip install build
python -m build
```
</details>

## Utility Scripts

```bash
# Archive completed TODO items
python scripts/clean.py --todo

# Show clean script help
python scripts/clean.py --help
```

## Git Shortcuts

```bash
# Check status
git status

# Stage all changes
git add .

# Commit with conventional message
git commit -m "feat: add new feature"

# Push to remote
git push origin <branch-name>
```

## Pre-commit (if installed)

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

## Quick Checks Before PR

```bash
# Run all quality checks (lint, format check, typecheck, test)
hatch run check
```

<details>
<summary>Without Hatch (direct commands)</summary>

```bash
pytest && ruff check . && ruff format --check . && mypy src/
```
</details>

## See Also

- [dev-setup.md](dev-setup.md) — Detailed environment setup
- [development.md](development.md) — Full development workflows
- [pull-requests.md](pull-requests.md) — PR guidelines
