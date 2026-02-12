# Development Guide

This guide covers developer tools and workflows for contributing to this project.

> **First time?** See [dev-setup.md](dev-setup.md) for environment setup instructions.
>
> **Ready to contribute?** See [pull-requests.md](pull-requests.md) for PR guidelines.

---

## Common Workflows

### Running Tests

```bash
# Run all tests
hatch run test

# Run with verbose output
hatch run test -v

# Run specific test file
hatch run test tests/unit_test.py

# Run with coverage report
hatch run test-cov
```

### Code Quality

```bash
# Lint code (check for issues)
hatch run lint

# Auto-fix linting issues
hatch run lint-fix

# Format code
hatch run fmt

# Type checking
hatch run typecheck

# Run ALL checks (lint + format + typecheck + test)
hatch run check
```

### Building the Package

```bash
# Build source and wheel distributions
hatch build

# Clean build artifacts
hatch clean

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

### Commit Messages (Conventional Commits)

Commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. You can write them manually — no tooling required.

#### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

- **type** — what kind of change (see table below)
- **scope** — what area is affected (optional, e.g. `cli`, `docs`, `ci`)
- **description** — short imperative summary, lowercase, no period

#### Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Whitespace, formatting (no logic changes) |
| `refactor` | Code restructuring (no feature/fix) |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `build` | Build system, dependencies |
| `ci` | CI/CD configuration |
| `chore` | Maintenance, tooling, config |
| `revert` | Reverting a previous commit |

#### Breaking Changes

Add `!` after the type/scope, and explain in the footer:

```
feat(api)!: change authentication to OAuth2

BREAKING CHANGE: removed basic auth support
```

#### Examples

```bash
git commit -m "feat: add user authentication"
git commit -m "fix(cli): handle missing config file gracefully"
git commit -m "docs: update installation guide"
git commit -m "refactor(engine): extract validation into separate module"
git commit -m "ci: add Python 3.13 to test matrix"
git commit -m "chore: bump ruff to 0.9.x"
```

#### Optional: Commitizen

If you prefer an interactive prompt, install [Commitizen](https://commitizen-tools.github.io/commitizen/):

```bash
pipx install commitizen
cz commit
```

---

## Helpful Tools (Optional)

These tools aren't required but can make development easier. Install them individually or all at once:

```bash
# Install all extras
pip install -e ".[extras]"

# Or install individually
pip install pipdeptree
```

### pipdeptree

Visualize your project's dependency tree - helpful for understanding what packages depend on what:

```bash
# Show full dependency tree
python -m pipdeptree

# Show dependencies for a specific package
python -m pipdeptree -p simple-python-boilerplate

# Reverse: show what depends on a package
python -m pipdeptree -r -p requests

# Output as JSON (for tooling)
python -m pipdeptree --json
```

### Other Helpful Tools

Tools I found helpful during development:

| Tool | Install | Description |
|------|---------|-------------|
| `pip-tools` | `pip install pip-tools` | Pin dependencies with `pip-compile` |
| `pip-audit` | `pip install pip-audit` | Check for security vulnerabilities |
| `rich` | `pip install rich` | Pretty console output and tables |
| `icecream` | `pip install icecream` | Better debug printing: `ic(variable)` |
| `ipython` | `pip install ipython` | Enhanced interactive Python shell |
| `devtools` | `pip install devtools` | Debug utilities: `debug(variable)` |

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

Edit `pyproject.toml` and Hatch picks them up automatically on the next command:

```toml
# Runtime dependencies (required to run the package)
[project]
dependencies = [
    "requests>=2.28",
]

# Dev dependencies (Hatch environment)
[tool.hatch.envs.default]
dependencies = [
    "pytest",
    "new-dev-tool",  # Add here
]
```

Then run any `hatch run` command — Hatch syncs and installs the new dependency automatically.

### Removing Dependencies

Remove the line from `pyproject.toml`. However, some setups/versions of Hatch may leave the old package installed in the environment. The reliable cleanup is to recreate the environment:

```bash
# Remove a specific environment
hatch env remove default

# Or remove ALL environments
hatch env prune
```

The next `hatch run` or `hatch shell` command will rebuild a clean environment.

### Checking Installed Packages

```bash
# List all installed packages in the Hatch default env
hatch run pip list

# Show package details
hatch run pip show simple-python-boilerplate

# Show Hatch environments
hatch env show
```

---

## Useful Resources

- [Hatch Documentation](https://hatch.pypa.io/latest/)
- [pyproject.toml Reference](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
