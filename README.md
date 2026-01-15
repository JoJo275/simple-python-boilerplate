# simple-python-boilerplate
A living repository containing structure that is based on my learning path. Cut down, this is one template based on one mindset. May update as I learn more.

# simple-python-boilerplate

A minimal, modern Python boilerplate using a `src/` layout, `pyproject.toml`, and `pytest`.

This repository is intended as:
- a learning reference
- a reusable starting point for small Python projects
- a correct baseline for Python packaging and testing

---

## Project Structure

simple-python-boilerplate/
├─ src/
│ └─ simple_python_boilerplate/
│ ├─ init.py
│ └─ main.py
├─ tests/
│ └─ test_version.py
├─ pyproject.toml
├─ README.md
├─ LICENSE
└─ .gitignore


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

Activate it:

Windows (PowerShell):

.\.venv\Scripts\Activate.ps1


macOS / Linux:

source .venv/bin/activate

Install the project in editable mode
python -m pip install -e .


Why this is required:

This project uses a src/ layout. Python will not automatically find packages inside src/ unless one of the following is true:

the project is installed, or

src/ is manually added to PYTHONPATH

Editable install (-e) links your source directory into Python’s environment so that:

imports work correctly

pytest can find your package

code changes are reflected immediately without reinstalling

This is the recommended workflow for development.

Running Tests
pytest


If tests fail with ModuleNotFoundError, ensure you ran:

python -m pip install -e .

Versioning

The package exposes a version string in:

simple_python_boilerplate.__version__


The version is defined in code and should match the version declared in pyproject.toml.

License

MIT License.
See the LICENSE file for details.

Notes

The distribution name (simple-python-boilerplate) may contain hyphens.

The import package name (simple_python_boilerplate) must use underscores.

__init__.py is intentionally included for clarity and tooling compatibility.

Intended Use

This repo is intentionally small and explicit.
It favors correctness and clarity over convenience or abstraction.

Use it as:

a starting point

a reference

a reminder of how Python packaging actually works


---

### Final confirmation
- ✅ Including `python -m pip install -e .` in the README is **correct**
- ✅ It is **expected** for `src/` layout projects
- ✅ This README matches your current repo and avoids misleading shortcuts

If you want, next steps could be:
- adding a version-sync test (`pyproject.toml` ↔ `__version__`)
- adding a minimal GitHub Actions CI
- stripping this down to a CS50-specific variant
