# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for this project.

ADRs are short documents that capture important architectural decisions made during development, along with their context and consequences.

## What is an ADR?

An ADR records a significant decision that affects the structure, non-functional characteristics, dependencies, interfaces, or construction techniques of a project.

## Format

Each ADR follows this structure:

1. **Title** — Short descriptive name
2. **Status** — Proposed, Accepted, Deprecated, Superseded
3. **Context** — What is the issue or situation?
4. **Decision** — What did we decide?
5. **Consequences** — What are the results?

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [001](001-src-layout.md) | Use src/ layout for package structure | Accepted |
| [002](002-pyproject-toml.md) | Use pyproject.toml for all configuration | Accepted |
| [003](003-separate-workflow-files.md) | Separate GitHub Actions workflow files | Accepted |
| [004](004-pin-action-shas.md) | Pin GitHub Actions to commit SHAs | Accepted |
| [005](005-ruff-for-linting-formatting.md) | Use Ruff for linting and formatting | Accepted |
| [006](006-pytest-for-testing.md) | Use pytest for testing | Accepted |
| [007](007-mypy-for-type-checking.md) | Use mypy for static type checking | Accepted |
| [008](008-pre-commit-hooks.md) | Use pre-commit hooks for automated checks | Accepted |
| [009](009-conventional-commits.md) | Use Conventional Commits for commit messages | Accepted |
| [010](010-dependabot-for-dependency-updates.md) | Use Dependabot for dependency updates | Accepted |
| [011](011-repository-guard-pattern.md) | Repository guard pattern for optional workflows | Accepted |
| [012](012-multi-layer-security-scanning.md) | Multi-layer security scanning in CI | Accepted |
| [013](013-sbom-bill-of-materials.md) | SBOM generation and distribution strategy | Accepted |
| [014](014-no-template-engine.md) | No template engine — manual customisation | Accepted |

## Archive

Deprecated, superseded, or suspended ADRs are moved to the [archive/](archive/) directory.

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [Michael Nygard's article on ADRs](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
