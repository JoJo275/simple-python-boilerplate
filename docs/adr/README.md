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

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [Michael Nygard's article on ADRs](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
