# ADR 003: Separate GitHub Actions workflow files

## Status

Accepted

## Context

GitHub Actions workflows can be organized in two ways:

1. **Single file** — All jobs in one `ci.yml` file
2. **Multiple files** — Separate files per concern (`test.yml`, `lint.yml`, `release.yml`)

## Decision

Use separate workflow files for distinct concerns:

```
.github/workflows/
├── test.yml          # Run tests on push/PR
├── lint.yml          # Code quality checks
├── release.yml       # Build and publish
└── _spellcheck.yml   # Disabled (underscore prefix)
```

## Consequences

### Positive

- **Easy to enable/disable** — Rename with underscore prefix to disable
- **Granular permissions** — Each workflow gets only required permissions
- **Independent triggers** — Different events for different workflows
- **Clearer debugging** — Failures are isolated to relevant workflow
- **Smaller diffs** — Changes scoped to relevant file

### Negative

- **More files** — More files to manage in `.github/workflows/`
- **Potential duplication** — Common steps may be repeated
- **Harder to share state** — Jobs in different workflows can't share artifacts directly

### Mitigations

- Use reusable workflows for shared logic (if needed)
- Keep workflows focused and simple
- Document workflow purposes in this ADR

## References

- [GitHub Actions: Reusing workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
