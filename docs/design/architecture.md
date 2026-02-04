# Architecture

<!-- TODO: Document your application architecture -->

## Overview

<!-- Brief description of the system and its purpose -->

## High-Level Architecture

<!-- TODO: Update with your actual architecture -->

```
┌─────────────────────────────────────────────────────────┐
│                      Application                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   CLI/API   │  │   Services  │  │    Models   │      │
│  │  (main.py)  │──│  (business  │──│   (data)    │      │
│  │             │  │   logic)    │  │             │      │
│  └─────────────┘  └─────────────┘  └──────┬──────┘      │
│                                           │             │
│                                    ┌──────▼──────┐      │
│                                    │  Database   │      │
│                                    │  (SQLite)   │      │
│                                    └─────────────┘      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

<!-- TODO: Update to reflect your actual structure -->

```
src/simple_python_boilerplate/
├── __init__.py          # Package root
├── main.py              # CLI entry points
├── sql/                 # Embedded SQL queries
└── dev_tools/           # Development utilities
```

## Key Components

### Entry Points

<!-- TODO: Document your entry points -->

| Command | Module | Description |
|---------|--------|-------------|
| `spb` | `main:main` | Main CLI entry point |
| `spb-version` | `main:print_version` | Print version |
| `spb-doctor` | `main:doctor` | System diagnostics |

### Layers

<!-- TODO: Describe your architectural layers -->

1. **Presentation Layer** — CLI commands, API endpoints
2. **Service Layer** — Business logic, orchestration
3. **Data Layer** — Database access, models

## Data Flow

<!-- TODO: Document typical data flows -->

```
User Input → CLI Parser → Service → Repository → Database
                                         ↓
User Output ← Formatter ← Service ← Domain Model
```

## Design Decisions

Key architectural decisions are documented in [ADRs](../adr/):

| ADR | Decision |
|-----|----------|
| [001](../adr/001-src-layout.md) | src/ layout for packages |
| [002](../adr/002-pyproject-toml.md) | pyproject.toml for config |

## External Dependencies

<!-- TODO: List key external dependencies -->

| Dependency | Purpose |
|------------|---------|
| sqlite3 | Database (stdlib) |

## Related Documentation

- [Database Design](database.md) — Schema and data model
- [ADRs](../adr/) — Architecture Decision Records
- [Development Guide](../development/) — Developer setup
