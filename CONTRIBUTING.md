# Contributing

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Reporting Issues](#reporting-issues)
- [Code of Conduct](#code-of-conduct)

---

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a branch for your changes

---

## Development Setup

### Prerequisites

- Python **3.11+**
- `pip`
- `pipx` (recommended for developer tools)

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

### 3. Install developer tools (optional but recommended)

See [docs/development.md](docs/development.md) for developer tooling details.

---

## Making Changes

1. Create a new branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

   Use descriptive branch names such as `fix/login-timeout` or `feat/add-cli`.

2. Make your changes
3. Run tests to ensure nothing is broken:

   ```bash
   pytest
   ```

4. Commit your changes following the commit message guidelines below

---

## Commit Messages

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type        | Description                                                |
|-------------|------------------------------------------------------------|
| `feat`      | A new feature                                              |
| `fix`       | A bug fix                                                  |
| `docs`      | Documentation only changes                                 |
| `style`     | Changes that do not affect the meaning of code             |
| `refactor`  | A code change that neither fixes a bug nor adds a feature  |
| `test`      | Adding missing tests or correcting existing tests          |
| `chore`     | Changes to the build process or auxiliary tools            |

### Using Commitizen

We recommend using Commitizen to create properly formatted commits, but certainly not required:

```bash
pipx install commitizen
cz commit
```

---

## Pull Requests

1. Ensure your branch is up to date with `main`
2. Ensure all tests pass
3. Write a clear PR description explaining:
   - What changes you made
   - Why you made them
   - Any relevant issue numbers
4. Request a review

---

## Reporting Issues

When reporting issues, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Python version and operating system
- Any relevant error messages or logs

---

## Code of Conduct

Please be respectful and constructive in all interactions. See our [Code of Conduct](CODE_OF_CONDUCT.md) for details.

---

## License

By contributing to this project, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
