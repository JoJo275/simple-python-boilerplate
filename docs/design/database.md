# Database Design

<!-- TODO: Document your database design decisions -->

## Overview

<!-- Brief description of the database and its purpose -->

## Database Engine

- **Engine:** SQLite (development) / PostgreSQL (production)
- **Location:** `var/app.sqlite3`

<!-- TODO: Update with your actual database choice -->

## Schema Diagram

<!-- TODO: Add ER diagram or link to diagram tool -->

```
┌─────────────┐       ┌─────────────┐
│   users     │       │   posts     │
├─────────────┤       ├─────────────┤
│ id (PK)     │──┐    │ id (PK)     │
│ name        │  │    │ user_id (FK)│──┐
│ email       │  └───>│ title       │  │
│ created_at  │       │ content     │  │
└─────────────┘       │ created_at  │  │
                      └─────────────┘  │
                                       │
                      ┌─────────────┐  │
                      │  comments   │  │
                      ├─────────────┤  │
                      │ id (PK)     │  │
                      │ post_id (FK)│<─┘
                      │ body        │
                      └─────────────┘
```

## Tables

### users

<!-- TODO: Document your actual tables -->

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Unique identifier |
| name | TEXT | NOT NULL | Display name |
| email | TEXT | UNIQUE, NOT NULL | Email address |
| created_at | TIMESTAMP | DEFAULT NOW | Creation timestamp |

## Indexes

<!-- TODO: Document indexes and their purpose -->

| Index | Table | Columns | Purpose |
|-------|-------|---------|---------|
| idx_users_email | users | email | Fast email lookups |

## Migrations Strategy

- Schema changes are tracked in `db/migrations/`
- Use sequential prefixes (`001_`, `002_`) for solo/small teams
- Use timestamps (`YYYYMMDDHHMMSS_`) for larger teams

## Related Files

- [db/schema.sql](../../db/schema.sql) — Canonical schema
- [db/migrations/](../../db/migrations/) — Migration files
- [db/seeds/](../../db/seeds/) — Seed data
- [db/queries/](../../db/queries/) — Reusable queries
