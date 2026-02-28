# Developer Commands

<!-- TODO (template users): Update command examples, script names, and paths
     throughout this file after renaming the project and adding your own
     Hatch scripts. Remove sections for features you don't use. -->

Quick reference for common development commands in this project.

## Environment Setup

### Using Hatch (recommended)

```bash
# Enter the dev environment (creates venv + installs deps automatically)
hatch shell

# Or run commands directly without entering the shell
hatch run <command>
```

#### Targeting Specific Environments

Hatch manages multiple environments (default, docs, test matrix). To run commands in a specific environment, prefix with the environment name:

```bash
hatch run <cmd>              # → default environment
hatch run docs:<cmd>         # → docs environment
hatch run test.py3.12:<cmd>  # → test.py3.12 environment
```

#### Temporary Package Installs

You can install packages temporarily into a Hatch environment for quick experimentation:

```bash
hatch run pip install some-package
```

> **Warning:** This install is **temporary** — it disappears when the environment is recreated (`hatch env remove default`). For permanent dependencies, add them to `pyproject.toml` under `[project.optional-dependencies]` instead.
>
> Useful for: quick debugging, one-off tools, testing compatibility before committing to a dependency.

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
hatch run test tests/unit/test_example.py

# Run with coverage
hatch run test-cov
```

### Multi-Version Testing

Hatch can run tests across multiple Python versions (3.11–3.13) using a test matrix defined in `pyproject.toml`.

```bash
# Run tests on ALL Python versions in the matrix
hatch run test:run

# Run tests with coverage on all versions
hatch run test:cov

# Run on a specific version only
hatch run +py=3.12 test:run

# Show all environments and their matrices
hatch env show
```

> **Note:** Each Python version in the matrix must be installed on your system. Hatch will skip versions that aren't available locally. CI workflows handle this automatically via `actions/setup-python`.

<details>
<summary>Without Hatch (direct commands)</summary>

```bash
pytest
pytest -v
pytest tests/unit/test_example.py
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

<!-- TODO (template users): Update this list after adding or removing scripts.
     The full script inventory is in scripts/README.md. -->

```bash
# Archive completed TODO items
python scripts/archive_todos.py
# or via task runner
task clean:todo

# Clean build artifacts and caches
python scripts/clean.py
python scripts/clean.py --dry-run
task clean:all

# Print diagnostics bundle for bug reports
python scripts/doctor.py
python scripts/doctor.py --markdown   # For GitHub issues
python scripts/doctor.py --output var/doctor.txt
task doctor

# Environment health check
python scripts/env_doctor.py
task doctor:env

# One-command setup for fresh clones
python scripts/bootstrap.py
task bootstrap
```

## GitHub Actions Version Management

Manage SHA-pinned GitHub Actions across workflow files.

```bash
# Show all pinned actions with version info
python scripts/workflow_versions.py show
task actions:versions

# Show offline (skip GitHub API)
task actions:versions -- --offline

# JSON output (useful for scripting)
task actions:versions -- --json

# Filter results (stale, upgradable, no-desc, or all)
task actions:versions -- --filter stale
task actions:versions -- --filter upgradable

# Quiet / CI mode (exit 1 if stale or upgradable actions found)
task actions:versions -- --quiet

# CI gate shortcut (same as --quiet, for pre-push hooks or CI)
task actions:check

# Update version comments and add descriptions
python scripts/workflow_versions.py update-comments
task actions:update-comments

# Upgrade all actions to their latest release
python scripts/workflow_versions.py upgrade
task actions:upgrade

# Preview upgrades without modifying files
task actions:upgrade:dry-run

# Upgrade a specific action
task actions:upgrade -- actions/checkout

# Upgrade to a specific version
task actions:upgrade -- actions/checkout v6.1.0

# Force colored output
task actions:versions -- --color
```

> **Tip:** Set `GITHUB_TOKEN` for higher API rate limits (5,000/hr vs. 60/hr).
> The remaining rate limit is shown at the end of each run.
>
> API responses are cached on disk (`.cache/workflow-versions/`, 1-hour TTL).
> Set `WV_CACHE_TTL=0` to disable caching.

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

<!-- TODO (template users): If you add or remove pre-commit hooks, update
     the hook examples and the hooks table below. The authoritative hook
     list is in .pre-commit-config.yaml and ADR 008. -->

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

### See Enabled Hooks

```bash
# List all configured hooks from .pre-commit-config.yaml
pre-commit run --all-files --list-hooks

# Or inspect the config directly
cat .pre-commit-config.yaml

# List raw Git hook scripts
ls .git/hooks/
```

### Disable / Skip Hooks

```bash
# Uninstall pre-commit hooks from this repo
pre-commit uninstall

# Skip ALL hooks for a single commit
SKIP=all git commit -m "feat: commit without hooks"
# Windows (PowerShell)
$env:SKIP="all"; git commit -m "feat: commit without hooks"; Remove-Item Env:SKIP

# Skip specific hooks only (comma-separated IDs)
SKIP=mypy,bandit git commit -m "fix: skip slow hooks"
# Windows (PowerShell)
$env:SKIP="mypy,bandit"; git commit -m "fix: skip slow hooks"; Remove-Item Env:SKIP

# Re-enable hooks
pre-commit install
```

### Without pre-commit (raw Git)

```bash
# Skip all Git hooks for a single commit
git commit --no-verify -m "feat: bypass all hooks"
# Short form
git commit -n -m "feat: bypass all hooks"

# Disable hooks globally via hooksPath
mkdir -p /tmp/no-hooks
git config core.hooksPath /tmp/no-hooks

# Restore default hooks path
git config --unset core.hooksPath

# Or delete the hook script directly
rm .git/hooks/pre-commit
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

## Hatch Reference

Common hatch commands beyond the project scripts defined above.

```bash
# Enter the dev shell (activates the default env)
hatch shell

# Leave the hatch shell
exit

# Show all configured environments and their scripts
hatch env show

# Remove a specific environment (e.g. to reset it)
hatch env remove default

# Remove all environments
hatch env prune

# Build sdist and wheel into dist/
hatch build

# Clean build artifacts
hatch clean

# Show project metadata (name, version, dependencies)
hatch project metadata

# Show resolved version
hatch version

# Show dependency tree
hatch dep show requirements

# Run an arbitrary command inside the default env
hatch run python -c "import sys; print(sys.executable)"

# Run a command in a specific env (if configured)
hatch run <env>:<command>
```

> Full docs: [hatch.pypa.io](https://hatch.pypa.io/latest/)

## See Also

- [dev-setup.md](dev-setup.md) — Detailed environment setup
- [development.md](development.md) — Full development workflows
- [pull-requests.md](pull-requests.md) — PR guidelines
