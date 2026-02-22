# Scripts

Utility scripts for development and maintenance.

## Contents

| Script | Description |
|--------|-------------|
| [apply_labels.py](apply_labels.py) | Apply GitHub labels from JSON |
| [apply-labels.sh](apply-labels.sh) | Shell wrapper for label application |
| [check_nul_bytes.py](check_nul_bytes.py) | Detect NUL (0x00) bytes in staged files |
| [dep_versions.py](dep_versions.py) | Show/update dependency versions in pyproject.toml and requirements files |
| [repo_doctor.py](repo_doctor.py) | Warn-only repo health checker driven by `.repo-doctor.toml` rules |
| [workflow_versions.py](workflow_versions.py) | Show/update version comments on SHA-pinned GitHub Actions |
| [customize.py](customize.py) | Interactive project customization — replaces boilerplate placeholders |
| [precommit/](precommit/) | Custom pre-commit hook scripts |
| [sql/](sql/) | SQL scripts for database operations |

## SQL Scripts

| Script | Description |
|--------|-------------|
| [sql/reset.sql](sql/reset.sql) | Reset database (drop/recreate) |
| [sql/scratch.example.sql](sql/scratch.example.sql) | Template for ad-hoc queries |

## Usage

```bash
# Run a Python script
python scripts/apply_labels.py

# Customize the template for your project
python scripts/customize.py
python scripts/customize.py --dry-run

# Run repo health checks
python scripts/repo_doctor.py
python scripts/repo_doctor.py --category ci --level warn
python scripts/repo_doctor.py --fix

# Run SQL against database
sqlite3 var/app.sqlite3 < scripts/sql/reset.sql
```
