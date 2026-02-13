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
| [API Reference](reference/api.md) | Auto-generated from source docstrings |

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
