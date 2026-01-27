# Development Environment Setup

This guide walks you through setting up the development environment for this project.

## Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **VS Code** (recommended) - [Download VS Code](https://code.visualstudio.com/)

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/JoJo275/simple-python-boilerplate.git
cd simple-python-boilerplate

# 2. Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate

# 3. Install the package in editable mode with dev dependencies
python -m pip install -e ".[dev]"

# 4. Verify installation
spb  # Run the CLI entry point
python -m pytest  # Run tests
```

## Detailed Setup

### 1. Confirm Python Installation

```bash
# Ensure Python 3.11+ is installed
python --version
```

### 2. Ensure .venv/ is Ignored

Before creating a virtual environment, make sure `.venv/` is in your `.gitignore`:

```bash
# Check if .venv is ignored
git check-ignore .venv/

# If not ignored, add it
echo ".venv/" >> .gitignore
```

Your `.gitignore` should include:
```
.venv/
__pycache__/
*.egg-info/
dist/
build/
.mypy_cache/
.pytest_cache/
.ruff_cache/
```

### 3. Update pip

```bash
python -m pip install --upgrade pip
```

### 4. Virtual Environment

Always use a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate it (choose your platform)
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Windows CMD:
.venv\Scripts\activate.bat

# macOS/Linux/Git Bash:
source .venv/bin/activate
```

> **Tip:** Your terminal prompt should show `(.venv)` when activated.

### 5. Confirm You're in the venv

```bash
python -c "import sys; print(sys.executable); print(sys.prefix)"
python -m pip -V
```

### 6. Install Dependencies

```bash
# Install package + dev dependencies (pytest, ruff, mypy, etc.)
python -m pip install -e ".[dev]"

# Or install just the package (no dev tools)
python -m pip install -e .
```

The `-e` flag installs in "editable" mode - changes to source code take effect immediately without reinstalling.

### 7. Verify Installation

```bash
# Check the package is installed
python -m pip show simple-python-boilerplate

# Run the CLI
spb

# Run tests
python -m pytest

# Run linter
python -m ruff check src/

# Run type checker
python -m mypy src/
```

### 8. Helpful Commands

```bash
# Editable installs confirmation
python -m pip list --editable

# See all packages installed in the venv
python -m pip list

# Freeze list (good for reproducing exact versions)
python -m pip freeze

# See exactly what pip thinks your project requires
python -m pip show simple-python-boilerplate
```

**Dependency tree** (very useful for understanding what depends on what):

```bash
# Install pipdeptree
python -m pip install pipdeptree

# Show full dependency tree
python -m pipdeptree

# Show just your project's dependencies
python -m pipdeptree -p simple-python-boilerplate
```

## Project Structure

```
simple-python-boilerplate/
├── src/
│   └── simple_python_boilerplate/  # Main package code
│       ├── __init__.py
│       └── main.py
├── tests/                          # Test files
│   └── unit_test.py
├── docs/                           # Documentation
├── scripts/                        # Utility scripts
├── pyproject.toml                  # Project configuration
└── README.md
```

## Available Commands

| Command | Description |
|---------|-------------|
| `spb` | Run the CLI entry point |
| `python -m pytest` | Run all tests |
| `python -m pytest -v` | Run tests with verbose output |
| `python -m pytest --cov` | Run tests with coverage report |
| `python -m ruff check src/` | Lint source code |
| `python -m ruff format src/` | Format source code |
| `python -m mypy src/` | Type check source code |

## IDE Setup

### VS Code (Recommended)

1. Open the workspace file: `simple-python-boilerplate.code-workspace`
2. Install recommended extensions when prompted
3. Select the Python interpreter from `.venv`:
   - `Ctrl+Shift+P` → "Python: Select Interpreter" → Choose `.venv`

**Recommended Extensions:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)

### PyCharm

1. Open the project folder
2. Go to Settings → Project → Python Interpreter
3. Add interpreter → Existing environment → Select `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (macOS/Linux)

## Troubleshooting

### "spb" command not found

Make sure:
1. Virtual environment is activated (you see `(.venv)` in prompt)
2. Package is installed: `python -m pip install -e ".[dev]"`

### Import errors in IDE

1. Ensure VS Code is using the correct Python interpreter from `.venv`
2. Reload the window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Permission denied (Windows PowerShell)

If you can't activate the virtual environment:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### pip install fails

Ensure pip is up to date:
```bash
python -m pip install --upgrade pip
```

## Next Steps

- Read the [Development Guide](development.md) for developer tools and workflows
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Review [pyproject.toml](../pyproject.toml) for all configuration options
