# var/

<!-- TODO: Update this list to match your project's runtime artifacts -->

Runtime data directory for:
- SQLite databases
- Log files
- Cache files
- Other generated artifacts

## Setup

```bash
# Copy the example database for local development
cp var/app.example.sqlite3 var/app.sqlite3
```

**Note:** `app.sqlite3` is gitignored. Only `app.example.sqlite3` is tracked.
