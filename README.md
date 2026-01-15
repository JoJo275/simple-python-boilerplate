# simple-python-boilerplate

A minimal, modern Python boilerplate using a `src/` layout, `pyproject.toml`, and `pytest`.

> A living repository containing structure based on my learning path. Cut down, this is one template based on one mindset. May update as I learn more.

This repository is intended as:
- A learning reference
- A reusable starting point for small Python projects
- A correct baseline for Python packaging and testing

---

## Project Structure

```
simple-python-boilerplate/
├── src/
│   └── simple_python_boilerplate/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── unit_test.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

### Why `src/` layout?

The `src/` layout prevents accidental imports from the working directory and ensures your code is imported the same way users and CI will import it. This surfaces packaging issues early instead of hiding them.

---

## Requirements

- Python **3.11+**
- `pip`

---

## Setup (Development)

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 2. Install the project in editable mode

```bash
python -m pip install -e .
```

#### Why this is required

This project uses a `src/` layout. Python will not automatically find packages inside `src/` unless one of the following is true:
- The project is installed, or
- `src/` is manually added to `PYTHONPATH`

Editable install (`-e`) links your source directory into Python's environment so that:
- Imports work correctly
- `pytest` can find your package
- Code changes are reflected immediately without reinstalling

This is the recommended workflow for development.

---

## Running Tests

```bash
pytest
```

If tests fail with `ModuleNotFoundError`, ensure you ran:

```bash
python -m pip install -e .
```

---

## Versioning

The package exposes a version string in:

```python
simple_python_boilerplate.__version__
```

The version is defined in code and should match the version declared in `pyproject.toml`.

---

## License

MIT License. See the [LICENSE](LICENSE) file for details.

---

## Notes

- The distribution name (`simple-python-boilerplate`) may contain hyphens.
- The import package name (`simple_python_boilerplate`) must use underscores.
- `__init__.py` is intentionally included for clarity and tooling compatibility.

---

## Intended Use

This repo is intentionally small and explicit. It favors correctness and clarity over convenience or abstraction.

Use it as:
- A starting point
- A reference
- A reminder of how Python packaging actually works

Where Python should come from (common best choices)

For most developers on Windows, the most predictable options are:

python.org installer

Standard, widely documented, easy PATH behavior

Windows package manager (winget)

Also predictable, easy updates

Conda / Miniconda

Useful if you need heavy scientific/native dependencies, but adds its own environment system

If your priority is “stable and unsurprising for packaging + venv,” the python.org installer (or winget) is usually the simplest.

What you should do in practice (simple and safe)
In each repo

Create venv:

python -m venv .venv


Activate it:

.\.venv\Scripts\Activate.ps1


Install:

python -m pip install -e .

To confirm you’re using the repo’s venv
echo $env:VIRTUAL_ENV
python -c "import sys; print(sys.executable)"

To leave a venv
deactivate
