# simple-python-boilerplate

A minimal, modern Python boilerplate using a `src/` layout, `pyproject.toml`, and `pytest`.

> A living repository containing structure based on my learning path. Cut down, this is one template based on one mindset. May update as I learn more.

**This repository is intended as:**

- A learning reference
- A reusable starting point for small Python projects
- A correct baseline for Python packaging and testing

---

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup (Development)](#setup-development)
- [Running Tests](#running-tests)
- [Versioning](#versioning)
- [Quick Reference](#quick-reference)
- [Where Should Python Come From?](#where-should-python-come-from)
- [Notes](#notes)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [License](#license)

---

## Project Structure

```
simple-python-boilerplate/
├── docs/
│   └── development.md
├── src/
│   └── simple_python_boilerplate/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── unit_test.py
├── .gitattributes
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
└── README.md
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

### Why is editable install required?

This project uses a `src/` layout. Python will not automatically find packages inside `src/` unless:

- The project is installed, **or**
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

## Quick Reference

### Per-Repository Workflow

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 3. Install project in editable mode
python -m pip install -e .
```

### Verify Your Environment

```powershell
# Check which venv is active
echo $env:VIRTUAL_ENV

# Check Python executable path
python -c "import sys; print(sys.executable)"
```

### Deactivate Environment

```bash
deactivate
```

---

## Where Should Python Come From?

For most developers on Windows, the most predictable options are:

| Source | Notes |
|--------|-------|
| [python.org](https://www.python.org/downloads/) | Standard, widely documented, easy PATH behavior |
| `winget install Python.Python.3.12` | Easy updates via Windows package manager |
| Conda / Miniconda | Useful for heavy scientific/native dependencies, but adds its own environment system |

> **Recommendation:** If your priority is "stable and unsurprising for packaging + venv," the python.org installer (or winget) is usually the simplest.

---

## Notes

- The distribution name (`simple-python-boilerplate`) may contain hyphens.
- The import package name (`simple_python_boilerplate`) must use underscores.
- `__init__.py` is intentionally included for clarity and tooling compatibility.
- This repo is intentionally small and explicit—it favors correctness and clarity over convenience or abstraction.

---

## Documentation

For developer tooling details, see [docs/development.md](docs/development.md).

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Code of Conduct

We are committed to a welcoming and inclusive community. Please see our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## License

This project is licensed under the Apache License 2.0 to allow unrestricted use, modification, and commercial distribution while providing explicit patent protection and legal clarity for users and contributors.

Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---

Questions, ideas, and open-ended discussion may be handled via GitHub Discussions if enabled in the future. For now, please use Issues for bugs or concrete proposals.

or

...

How to use this repository

1. Click "Use this template" on GitHub
2. Rename the package directory
3. Update pyproject.toml name and description

Scope: Many parts if not all can be adapted and changed as needed for a myriad of very valid reasons. This is simply one way to do it that I have found useful and educational.

If you do not want any templates, dependabot configs, or other files, please delete them as needed.

If you have any questions on how to do something or why something is done a certain way, please post in the disucssion.

stuff I may add in the future

- docker config
- more github actions/workflows/configs
- more testing examples (integration, e2e, etc)
- more ci/cd examples
- deployment configuration
- style/linting configuration

## Future Improvements

This repository is intentionally minimal while I learn and solidify concepts.

Potential additions in the future:

- Continuous Integration (GitHub Actions)
- Docker support for reproducible environments
- Automated release and deployment workflows
- docker config
- more github actions/workflows/configs
- more testing examples (integration, e2e, etc)
- more ci/cd examples
- deployment configuration
- style/linting configuration
- SLSA workflows for supply chain security

These may be added once I have covered the relevant concepts.

[Developer note]  
*Developer notes are formatted like this.*
