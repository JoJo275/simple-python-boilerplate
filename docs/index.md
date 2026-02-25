# simple-python-boilerplate

A minimal Python boilerplate using the **src/ layout**, configured with
[Hatch](https://hatch.pypa.io/) as the build system.

## Features

- **src/ layout** — clean separation between source code and project root.
- **Hatch** — modern build backend and environment manager.
- **pytest** — testing framework with coverage support.
- **Ruff** — fast linting and formatting.
- **mypy** — strict static type checking.
- **MkDocs + Material** — documentation with auto-generated API reference.

## Quick links

| Resource | Description |
|----------|-------------|
| [Getting Started](guide/getting-started.md) | Installation and local development |
| [Using This Template](USING_THIS_TEMPLATE.md) | Customizing the boilerplate for your project |
| [Development Guide](development/development.md) | Developer tools and workflows |
| [API Reference](reference/api.md) | Auto-generated from source docstrings |
| [Architecture](design/architecture.md) | System overview and module responsibilities |
| [ADRs](adr/README.md) | Architecture Decision Records |
| [Workflows](workflows.md) | GitHub Actions inventory |
| [Tooling](tooling.md) | All repo tools at a glance |

## Project layout

```
src/
  simple_python_boilerplate/
    __init__.py       # Package root
    api.py            # HTTP/REST interface
    cli.py            # CLI argument parsing
    engine.py         # Core business logic
    main.py           # Entry points
tests/                # Test suite
docs/                 # Documentation source
pyproject.toml        # Project configuration (single source of truth)
```
