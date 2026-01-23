# Development Guide

## Developer Tools

This project uses the following developer tools:

### GitHub CLI

GitHub CLI (`gh`) is required to run the label management scripts in `scripts/`.

Install GitHub CLI:

- **Windows (winget):**
  ```bash
  winget install --id GitHub.cli
  ```

- **Windows (Chocolatey):**
  ```bash
  choco install gh
  ```

- **macOS (Homebrew):**
  ```bash
  brew install gh
  ```

- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt install gh
  ```

After installation, authenticate with GitHub:

```bash
gh auth login
```

See the [GitHub CLI installation docs](https://cli.github.com/manual/installation) for other platforms.

### Commitizen

Commitizen is used to standardize commit messages during development.
It is not required to run the project.

Commit messages follow the Conventional Commits specification.

Install Commitizen using pipx:

```bash
pipx install commitizen
```

Create commits with:

```bash
cz commit
```
