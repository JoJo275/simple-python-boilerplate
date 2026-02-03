# Developer Commands

Quick reference for common development commands in this project.

## Environment Setup

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
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit_test.py

# Run with coverage
pytest --cov=simple_python_boilerplate --cov-report=term-missing
```

## Linting & Formatting

```bash
# Check for linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Check formatting
ruff format --check .

# Apply formatting
ruff format .
```

## Type Checking

```bash
# Run mypy
mypy src/

# Run with strict mode (default in this project)
mypy --strict src/
```

## Building

```bash
# Install build tool
pip install build

# Build source and wheel distributions
python -m build

# Check built package
twine check dist/*
```

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
# Run all quality checks
pytest && ruff check . && ruff format --check .

# Or individually:
pytest              # Tests pass?
ruff check .        # Linting clean?
ruff format --check # Formatting correct?
mypy src/           # Types okay?
```

## See Also

- [dev-setup.md](dev-setup.md) — Detailed environment setup
- [development.md](development.md) — Full development workflows
- [pull-requests.md](pull-requests.md) — PR guidelines
