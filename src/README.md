# src/

<!--
TODO (template users): This README exists only to explain the src-layout
      pattern. REMOVE this file when using this template for a real project.
-->

This directory uses the **src-layout** pattern for Python packaging.

## Why src/?

The `src/` directory is a container that:

- Prevents accidental imports of uninstalled code
- Forces you to install the package (`pip install -e .` or `hatch shell`)
- Ensures tests run against the installed package, not local files

## Structure

```text
src/
└── simple_python_boilerplate/   # ← The actual package
    ├── __init__.py
    ├── main.py
    ├── sql/                     # Embedded SQL queries (shipped with package)
    └── ...
```

## Usage

```bash
# Preferred: Use Hatch for development
hatch shell

# Alternative: Install in editable mode
pip install -e .

# Then import normally
python -c "from simple_python_boilerplate import main"
```

## Learn More

- [ADR 001: src-layout](../docs/adr/001-src-layout.md)
- [ADR 016: Hatchling and Hatch](../docs/adr/016-hatchling-and-hatch.md)
- [PyPA: src-layout vs flat-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
