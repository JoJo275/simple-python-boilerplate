# Database Migrations

<!-- TODO: Update this README with your project's migration conventions -->

Schema migration files for version-controlled database changes.

## Naming Convention

**Sequential (default for solo/small teams):**
```
001_create_users_table.sql
002_add_email_to_users.sql
```

**Timestamp (recommended for teams/parallel branches):**
```
20260204143052_create_users_table.sql
20260204151030_add_email_to_users.sql
```

> **Tip:** Use timestamps (`YYYYMMDDHHMMSS_`) when multiple developers may create migrations on separate branches to avoid merge conflicts.

## Usage

```bash
# Apply migration (example)
sqlite3 var/app.sqlite3 < db/migrations/001_create_users_table.sql
```
