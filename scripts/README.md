# Scripts

Utility scripts for development and maintenance.

## Contents

| Script | Description |
|--------|-------------|
| [apply_labels.py](apply_labels.py) | Apply GitHub labels from JSON |
| [apply-labels.sh](apply-labels.sh) | Shell wrapper for label application |
| [archive_todos.py](archive_todos.py) | Archive completed TODO items from todo.md |
| [bootstrap.py](bootstrap.py) | One-command setup for fresh clones |
| [check_nul_bytes.py](precommit/check_nul_bytes.py) | Detect NUL (0x00) bytes in staged files |
| [check_todos.py](check_todos.py) | Scan for `TODO (template users)` comments |
| [clean.py](clean.py) | Remove build artifacts and caches |
| [customize.py](customize.py) | Interactive project customization — replaces boilerplate placeholders |
| [dep_versions.py](dep_versions.py) | Show/update dependency versions in pyproject.toml and requirements files |
| [doctor.py](doctor.py) | Print diagnostics bundle for bug reports |
| [env_doctor.py](env_doctor.py) | Environment health check |
| [repo_doctor.py](repo_doctor.py) | Warn-only repo health checker driven by `.repo-doctor.toml` rules |
| [workflow_versions.py](workflow_versions.py) | Show/update version comments on SHA-pinned GitHub Actions |
| [precommit/](precommit/) | Custom pre-commit hook scripts |
| [sql/](sql/) | SQL scripts for database operations |

## SQL Scripts

| Script | Description |
|--------|-------------|
| [sql/reset.sql](sql/reset.sql) | Reset database (drop/recreate) |
| [sql/scratch.example.sql](sql/scratch.example.sql) | Template for ad-hoc queries |

## Usage

```bash
# One-command setup for fresh clones
python scripts/bootstrap.py

# Run a Python script
python scripts/apply_labels.py

# Customize the template for your project
python scripts/customize.py
python scripts/customize.py --dry-run

# Run repo health checks
python scripts/repo_doctor.py
python scripts/repo_doctor.py --category ci --level warn
python scripts/repo_doctor.py --fix

# Clean build artifacts and caches
python scripts/clean.py
python scripts/clean.py --dry-run

# Print diagnostics bundle for bug reports
python scripts/doctor.py
python scripts/doctor.py --markdown   # For GitHub issues

# Archive completed TODO items
python scripts/archive_todos.py

# Manage SHA-pinned GitHub Actions versions
python scripts/workflow_versions.py                    # Show all actions
python scripts/workflow_versions.py show --offline     # Skip GitHub API
python scripts/workflow_versions.py show --json        # JSON output
python scripts/workflow_versions.py update-comments    # Sync comments + add descriptions
python scripts/workflow_versions.py upgrade            # Upgrade all to latest
python scripts/workflow_versions.py upgrade --dry-run  # Preview upgrades
python scripts/workflow_versions.py upgrade actions/checkout v6.1.0  # Specific version

# Run SQL against database
sqlite3 var/app.sqlite3 < scripts/sql/reset.sql
```
