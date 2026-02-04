# ADR 008: Use pre-commit hooks for automated checks

## Status

Accepted

## Context

Code quality checks (linting, formatting, type checking) can run at several points:

1. **Manually** — Developer runs tools by hand
2. **Pre-commit hooks** — Automatically on `git commit`
3. **CI only** — Checks run in GitHub Actions after push
4. **Editor/IDE** — Real-time feedback while coding

Manual checks are error-prone (easy to forget). CI-only checks provide late feedback (errors found after push). Pre-commit hooks provide immediate, automatic feedback.

## Decision

Use the `pre-commit` framework to run checks automatically on commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
```

## Consequences

### Positive

- **Automatic** — No manual step to forget
- **Fast feedback** — Errors caught before commit, not after push
- **Consistent** — Same checks for all developers
- **Prevents bad commits** — Can't commit code that fails checks
- **CI backup** — CI still runs checks for contributors who skip hooks

### Negative

- **Setup required** — Developers must run `pre-commit install`
- **Can be bypassed** — `git commit --no-verify` skips hooks
- **Slower commits** — Adds time to commit process
- **Initial friction** — May block commits until code is fixed

### Mitigations

- Document setup in CONTRIBUTING.md
- Keep hooks fast (Ruff is very fast)
- CI runs same checks as safety net
- Allow `--no-verify` for WIP commits (CI will catch issues)

## Alternatives Considered

### CI-only checks

Run all checks in GitHub Actions, not locally.

**Rejected because:** Late feedback; developers don't see errors until after push; wastes CI resources on obvious issues.

### Husky (Node.js)

Git hooks via npm/Node.js.

**Rejected because:** Adds Node.js dependency to a Python project; pre-commit is Python-native and well-integrated.

### Manual checks

Document commands and trust developers to run them.

**Rejected because:** Easy to forget; inconsistent across team; bad commits reach CI.

## Implementation

- [.pre-commit-config.yaml](../../.pre-commit-config.yaml) — Pre-commit configuration with:
  - `pre-commit-hooks` — General file checks (trailing whitespace, YAML/TOML validation, etc.)
  - `ruff-pre-commit` — Linting and formatting
  - `mirrors-mypy` — Type checking
  - `bandit` — Security checks
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — Setup instructions for contributors
- [pyproject.toml](../../pyproject.toml) — `pre-commit` listed in `[project.optional-dependencies.dev]`

## References

- [pre-commit documentation](https://pre-commit.com/)
- [pre-commit hooks directory](https://pre-commit.com/hooks.html)
