# Learning Notes

Personal notes and learnings captured while building this project.

## Python Packaging

### The `src/` Layout Mystery (Solved)

**Problem:** Tests fail with `ModuleNotFoundError` even though code is right there.

**Why:** Python doesn't automatically look inside `src/`. The `src/` layout is *intentionally* strict — it forces you to install the package properly.

**Solution:** Always run `pip install -e .` after cloning. The `-e` (editable) flag links your source so changes reflect immediately.

### pyproject.toml vs setup.py

- `setup.py` = Old way (executable Python, security concerns)
- `pyproject.toml` = New way (declarative TOML, standard)

Most tools now read from `[tool.X]` sections in pyproject.toml. One file to rule them all.

---

## GitHub Actions

### Why Pin to SHAs?

Tags like `@v4` are mutable — someone could push malicious code and move the tag. SHAs are immutable. Always pin to full SHA with a version comment:

```yaml
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

### Workflow Organization

Separate files > one giant file:
- Easier to disable (just rename to `_workflow.yml`)
- Each gets its own permissions
- Failures are isolated

---

## Static Analysis Tools

| Tool | Purpose | Speed |
|------|---------|-------|
| **Ruff** | Linting + formatting | ⚡ Very fast (Rust) |
| **Mypy** | Type checking | 🐢 Slower |
| **Pyright** | Type checking (VS Code) | ⚡ Fast |
| **Bandit** | Security scanning | 🐢 Moderate |

**Ruff** replaces: flake8, isort, black, pyupgrade, and more. One tool, one config.

---

## Virtual Environments

### Quick Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # macOS/Linux
pip install -e ".[dev]"
```

### Check Which Python

```bash
python -c "import sys; print(sys.executable)"
```

If it doesn't show `.venv`, you're using the wrong Python!

---

## Things I Keep Forgetting

1. **Import name ≠ package name** — `simple-python-boilerplate` (hyphen) installs, but you `import simple_python_boilerplate` (underscore)

2. **`__init__.py` is still needed** — Even in Python 3, include it for tooling compatibility

3. **Editable install is required** — With `src/` layout, you must install to import

4. **pytest needs the package installed** — Or it won't find your modules

---

## Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [Hynek's Testing & Packaging](https://hynek.me/articles/testing-packaging/)
- [Real Python: Python Packaging](https://realpython.com/pypi-publish-python-package/)
