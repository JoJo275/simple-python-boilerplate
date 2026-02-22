# Database

<!-- TODO: Update this README with your project's database conventions -->

This directory contains all database-related files.

## Structure

```
db/
├── schema.sql        # Complete current schema
├── migrations/       # Incremental schema changes
├── seeds/            # Initial/test data
└── queries/          # Reusable SQL queries
```

## Quick Links

| Directory | Purpose |
|-----------|---------|
| [schema.sql](schema.sql) | Canonical database schema |
| [migrations/](migrations/) | Version-controlled schema changes |
| [seeds/](seeds/) | Seed data for dev/test environments |
| [queries/](queries/) | Reusable application queries |

## Getting Started

```bash
# Copy example database for local development
cp var/app.example.sqlite3 var/app.sqlite3

# Or create fresh database with schema
sqlite3 var/app.sqlite3 < db/schema.sql

# Apply seeds (development)
sqlite3 var/app.sqlite3 < db/seeds/001_example_seed.sql
```

## CI & Quality Checks for SQL

<!-- TODO (template users): Enable these when you add real SQL to your project -->

Once you add real SQL to your project, consider adding automated checks:

| Check | Tool | How |
|-------|------|-----|
| **Schema validation** | `sqlite3` | `sqlite3 :memory: < db/schema.sql` in CI |
| **SQL lint + format** | [SQLFluff](https://sqlfluff.com/) | Pre-commit hook + CI workflow |
| **Migration apply test** | sqlite3 or your DB | Apply all migrations sequentially in CI |
| **Seed data test** | sqlite3 or your DB | Apply seeds after schema to check constraints |

If using an ORM instead of raw SQL files, lint Python code (Ruff, mypy) and
test migrations with pytest. See [learning notes on SQL CI](../docs/notes/learning.md#setting-up-sql-ci-and-hooks)
for detailed examples.

## Related

- [var/](../var/) — Runtime database files (gitignored)
- [scripts/sql/](../scripts/sql/) — Ad-hoc SQL experimentation
- [tests/integration/sql/](../tests/integration/sql/) — Test fixtures
