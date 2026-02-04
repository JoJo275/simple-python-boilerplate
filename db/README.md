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
# Create database with schema
sqlite3 var/app.sqlite3 < db/schema.sql

# Apply seeds (development)
sqlite3 var/app.sqlite3 < db/seeds/001_example_seed.sql
```

## Related

- [var/](../var/) — Runtime database files (gitignored)
- [scripts/sql/](../scripts/sql/) — Ad-hoc SQL experimentation
- [tests/integration/sql/](../tests/integration/sql/) — Test fixtures
