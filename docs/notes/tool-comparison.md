# Tool Comparison Notes

Quick reference for choosing between similar tools.

## Formatters

| Tool | Language | Notes |
|------|----------|-------|
| **Black** | Python | Opinionated, zero-config, widely adopted |
| **Ruff** | Rust | Black-compatible, much faster, also lints |
| **autopep8** | Python | PEP 8 focused, less opinionated |
| **YAPF** | Python | Google's formatter, highly configurable |

**Winner:** Ruff — it's faster and combines formatting + linting.

---

## Linters

| Tool | Language | Notes |
|------|----------|-------|
| **Ruff** | Rust | Replaces flake8, isort, pyupgrade, etc. |
| **Flake8** | Python | Classic, plugin ecosystem |
| **Pylint** | Python | Very thorough, can be noisy |

**Winner:** Ruff — 10-100x faster, replaces multiple tools.

---

## Type Checkers

| Tool | Notes |
|------|-------|
| **Mypy** | Original, most widely used in CI |
| **Pyright** | Microsoft, powers Pylance in VS Code |
| **Pyre** | Facebook, incremental checking |

**Recommendation:** Use Pyright in editor (via Pylance), Mypy in CI.

---

## Test Frameworks

| Tool | Notes |
|------|-------|
| **pytest** | De facto standard, great plugins |
| **unittest** | Built-in, Java-style (verbose) |
| **nose2** | unittest successor, less active |

**Winner:** pytest — everyone uses it.

---

## Build Backends

| Tool | Notes |
|------|-------|
| **setuptools** | Standard, most compatible |
| **hatch** | Modern, good CLI, version management |
| **flit** | Simple, minimal config |
| **poetry** | All-in-one (deps + build + publish) |
| **PDM** | PEP 582 support, modern |

**Recommendation:** setuptools for compatibility, hatch for modern features.

---

## CI Platforms

| Platform | Notes |
|----------|-------|
| **GitHub Actions** | Best GitHub integration, free for public repos |
| **GitLab CI** | Built into GitLab, powerful |
| **CircleCI** | Fast, good caching |
| **Travis CI** | Pioneer, less popular now |

**For GitHub repos:** GitHub Actions, obviously.
