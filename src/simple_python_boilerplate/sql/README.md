# SQL Queries Module

<!-- TODO: Update with your project's query organization -->

Application SQL queries embedded in the package.

## When to Use

Use this directory for queries that are:
- Tightly coupled to application code
- Loaded at runtime via `importlib.resources`
- Shipped with the installed package

Use `db/queries/` for:
- Standalone queries run manually or by scripts
- Queries shared across multiple applications

## Usage

```python
from importlib.resources import files

# Load a query file
query = files("simple_python_boilerplate.sql").joinpath("get_user.sql").read_text()
```

## Structure

```
sql/
├── users/
│   ├── get_by_id.sql
│   └── search.sql
└── reports/
    └── daily_summary.sql
```
