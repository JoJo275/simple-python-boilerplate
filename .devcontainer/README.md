# Dev Container

This folder configures a VS Code [Dev Container](https://code.visualstudio.com/docs/devcontainers/containers)
for consistent development environments.

## Quick Start

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Podman)
2. Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VS Code
3. Open this repo in VS Code
4. Click "Reopen in Container" when prompted (or run `Dev Containers: Reopen in Container` from the command palette)

VS Code will build the container and set up your environment automatically.

## What's Included

- Python 3.12 with pip
- Node.js LTS (for pre-commit hooks like markdownlint)
- Task runner (go-task)
- All Python dev dependencies installed
- Pre-commit hooks configured
- VS Code extensions for Python, TOML, YAML, Git

## GitHub Codespaces

This configuration also works with [GitHub Codespaces](https://github.com/features/codespaces).
Click the green "Code" button on GitHub and select "Open with Codespaces" to get a
browser-based development environment with zero local setup.

## Dev Container vs Containerfile

| Aspect | Dev Container (`.devcontainer/`) | Containerfile (repo root) |
|--------|----------------------------------|---------------------------|
| **Purpose** | Development environment | Production runtime |
| **Contains** | All dev tools, editors, linters | Minimal app only |
| **Image size** | Large (~1GB+) | Small (~150MB) |
| **User** | Interactive development | Run the application |
| **When to use** | `code .` → "Reopen in Container" | `docker build` → `docker run` |

They serve completely different purposes and don't share configuration.
