# src/

<!--
TODO: This README is NOT common practice.
      It exists only to explain the src-layout for template users.
      REMOVE this file when using this template for a real project.
-->

This directory uses the **src-layout** pattern for Python packaging.

## Why src/?

The `src/` directory is a container that:

- Prevents accidental imports of uninstalled code
- Forces you to install the package (`pip install -e .`)
- Ensures tests run against the installed package, not local files

## Structure

```
src/
└── simple_python_boilerplate/   # ← The actual package
    ├── __init__.py
    ├── main.py
    └── ...
```

## Usage

```bash
# Install in editable mode (required for development)
pip install -e .

# Then import normally
python -c "from simple_python_boilerplate import main"
```

## Learn More

- [ADR 001: src-layout](../docs/adr/001-src-layout.md)
- [PyPA: src-layout vs flat-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
