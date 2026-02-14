# Scripts

Utility scripts for development and maintenance.

## Contents

| Script | Description |
|--------|-------------|
| [apply_labels.py](apply_labels.py) | Apply GitHub labels from JSON |
| [apply-labels.sh](apply-labels.sh) | Shell wrapper for label application |
| [dep_versions.py](dep_versions.py) | Show/update dependency versions in pyproject.toml and requirements files |
| [workflow_versions.py](workflow_versions.py) | Show/update version comments on SHA-pinned GitHub Actions |
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

# Run SQL against database
sqlite3 var/app.sqlite3 < scripts/sql/reset.sql
```

<!-- TODO: Update this README with your project's scripts -->
