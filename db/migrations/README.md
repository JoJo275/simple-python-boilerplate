# Database Migrations

<!-- TODO: Update this README with your project's migration conventions -->

Schema migration files for version-controlled database changes.

## Naming Convention

```
001_create_users_table.sql
002_add_email_to_users.sql
```

## Usage

```bash
# Apply migration (example)
sqlite3 var/app.sqlite3 < db/migrations/001_create_users_table.sql
```
