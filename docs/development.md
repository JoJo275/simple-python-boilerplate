# Development Guide

This guide covers developer tools and workflows for contributing to this project.

> **First time?** See [dev-setup.md](dev-setup.md) for environment setup instructions.

---

## Common Workflows

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit_test.py

# Run with coverage report
pytest --cov=simple_python_boilerplate --cov-report=term-missing
```

### Code Quality

```bash
# Lint code (check for issues)
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/

# Type checking
mypy src/
```

### Building the Package

```bash
# Install build tool
pip install build

# Build source and wheel distributions
python -m build

# Output goes to dist/
```

---

## Developer Tools

This project uses the following developer tools:

### GitHub CLI

GitHub CLI (`gh`) is required to run the label management scripts in `scripts/`.

Install GitHub CLI:

- **Windows (winget):**
  ```bash
  winget install --id GitHub.cli
  ```

- **Windows (Chocolatey):**
  ```bash
  choco install gh
  ```

- **macOS (Homebrew):**
  ```bash
  brew install gh
  ```

- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt install gh
  ```

After installation, authenticate with GitHub:

```bash
gh auth login
```

See the [GitHub CLI installation docs](https://cli.github.com/manual/installation) for other platforms.

### Commitizen

Commitizen is used to standardize commit messages during development.
It is not required to run the project.

Commit messages follow the Conventional Commits specification.

Install Commitizen using pipx:

```bash
pipx install commitizen
```

Create commits with:

```bash
cz commit
```

---

## Pre-commit Hooks (Optional)

Set up pre-commit hooks to automatically run checks before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Run against all files (first time)
pre-commit run --all-files
```

Create a `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: []
```

---

## Dependency Management

### Adding Dependencies

Edit `pyproject.toml`:

```toml
# Runtime dependencies (required to run the package)
dependencies = [
    "requests>=2.28",
]

# Dev dependencies (only needed for development)
[project.optional-dependencies]
dev = [
    "pytest",
    "new-dev-tool",  # Add here
]
```

Then reinstall:

```bash
pip install -e ".[dev]"
```

### Checking Installed Packages

```bash
# List all installed packages
pip list

# Show package details
pip show simple-python-boilerplate

# Check for outdated packages
pip list --outdated

# Generate requirements file (for reference)
pip freeze > requirements-freeze.txt
```

---

## Useful Resources

- [pyproject.toml Reference](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
