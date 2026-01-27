# Development Environment Setup

This guide walks you through setting up the development environment for this project.

## Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **VS Code** (recommended) - [Download VS Code](https://code.visualstudio.com/)

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/username/simple-python-boilerplate.git
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
pip install -e ".[dev]"

# 4. Verify installation
spb  # Run the CLI entry point
pytest  # Run tests
```

## Detailed Setup

### 1. Virtual Environment

Always use a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate it (choose your platform)
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Windows CMD:
.venv\Scripts\activate.bat

# macOS/Linux/Git Bash:
source .venv/bin/activate
```

> **Tip:** Your terminal prompt should show `(.venv)` when activated.

### 2. Install Dependencies

```bash
# Install package + dev dependencies (pytest, ruff, mypy, etc.)
pip install -e ".[dev]"

# Or install just the package (no dev tools)
pip install -e .
```

The `-e` flag installs in "editable" mode - changes to source code take effect immediately without reinstalling.

### 3. Verify Installation

```bash
# Check the package is installed
pip show simple-python-boilerplate

# Run the CLI
spb

# Run tests
pytest

# Run linter
ruff check src/

# Run type checker
mypy src/
```
### 4. Helpful Commands




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
| `pytest` | Run all tests |
| `pytest -v` | Run tests with verbose output |
| `pytest --cov` | Run tests with coverage report |
| `ruff check src/` | Lint source code |
| `ruff format src/` | Format source code |
| `mypy src/` | Type check source code |

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
2. Package is installed: `pip install -e ".[dev]"`

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
