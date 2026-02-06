# Release Policy

This document describes when and how releases are made.

---

## Versioning Scheme

This project follows [Semantic Versioning](https://semver.org/) (SemVer):

| Version | When to Increment | Example |
|---------|-------------------|---------|
| **MAJOR** (X.0.0) | Breaking changes to public API | `1.0.0` → `2.0.0` |
| **MINOR** (0.X.0) | New features, backward compatible | `1.0.0` → `1.1.0` |
| **PATCH** (0.0.X) | Bug fixes, backward compatible | `1.0.0` → `1.0.1` |

### Pre-release Versions

| Suffix | Meaning | Stability |
|--------|---------|-----------|
| `1.0.0a1` | Alpha | Incomplete, may change significantly |
| `1.0.0b1` | Beta | Feature complete, may have bugs |
| `1.0.0rc1` | Release candidate | Ready for release unless issues found |

---

## Release Cadence

This project does **not** follow a fixed release schedule. Releases are made when:

- Significant features are complete
- Security vulnerabilities need patching
- Critical bugs are fixed

---

## What Triggers a Release

| Trigger | Version Bump | Notes |
|---------|--------------|-------|
| Security fix | PATCH or higher | Released ASAP |
| Bug fix | PATCH | Batched unless critical |
| New feature | MINOR | After testing and documentation |
| Breaking change | MAJOR | Planned, documented, migration guide provided |

---

## Backward Compatibility

### What We Consider "Public API"

- Exported functions/classes from `simple_python_boilerplate`
- CLI commands and their arguments
- Configuration file formats

### What Is NOT Public API

- Internal modules (prefixed with `_`)
- Test utilities
- Development scripts
- File/directory structure

Changes to non-public API do not require a major version bump.

---

## Deprecation Policy

Before removing features:

1. Mark as deprecated in documentation and code (warnings)
2. Keep deprecated feature for at least one minor release
3. Document migration path
4. Remove in next major version

Example deprecation warning:

```python
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function()
```

---

## Support Policy

| Version | Support Level |
|---------|---------------|
| Latest major | Full support (bugs + features) |
| Previous major | Security fixes only (6 months) |
| Older versions | No support |

---

## Release Process

See [releasing.md](releasing.md) for the step-by-step release process.

### Summary

1. Update CHANGELOG.md
2. Bump version in pyproject.toml
3. Commit with `chore: release vX.Y.Z`
4. Tag with `vX.Y.Z`
5. Push tag (triggers release workflow)

---

## See Also

- [Releasing](releasing.md) — Step-by-step release instructions
- [CHANGELOG.md](../CHANGELOG.md) — Version history
- [Semantic Versioning](https://semver.org/)
