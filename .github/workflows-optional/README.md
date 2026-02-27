# Optional Workflows

This directory contains **optional workflow templates** that are not active by default.

## How to use

1. **Copy** a workflow from here into `.github/workflows/`.
2. **Follow the TODO** comments at the top of the file to configure it.
3. The workflow will become active on the next push.

## Why a separate directory?

GitHub Actions only executes workflows in `.github/workflows/`.
Files here are inert — they serve as a library of ready-to-use templates
you can adopt when your project needs them.

## Available templates

| File                    | Purpose                                              |
| ----------------------- | ---------------------------------------------------- |
| `docs.yml`              | Build and deploy documentation (e.g. MkDocs, Sphinx) |
| `dependency-review.yml` | Scan PRs for vulnerable or restricted dependencies   |
| `labeler.yml`           | Auto-label PRs based on file paths changed           |
