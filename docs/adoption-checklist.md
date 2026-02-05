# Adoption Checklist

A step-by-step checklist for setting up a new project from this template.

For detailed guidance, see [USING_THIS_TEMPLATE.md](USING_THIS_TEMPLATE.md).

---

## Initial Setup

- [ ] Clone or use "Use this template" on GitHub
- [ ] Rename the repository to your project name
- [ ] Update remote URL if cloned directly

## Placeholder Replacements

- [ ] Replace `simple-python-boilerplate` with your project name
- [ ] Replace `simple_python_boilerplate` with your package name (snake_case)
- [ ] Replace `JoJo275` with your GitHub username/org
- [ ] Replace `[Your Name]` with your name in `LICENSE` and `pyproject.toml`
- [ ] Replace `security@example.com` with your security contact

## Core Files

- [ ] Update `README.md` with project description and badges
- [ ] Update `pyproject.toml` (name, author, dependencies, URLs)
- [ ] Update `LICENSE` (year, author — or choose different license)
- [ ] Update `SECURITY.md` with your contact info

## Source Code

- [ ] Rename `src/simple_python_boilerplate/` to your package name
- [ ] Update imports in test files to match new package name
- [ ] Update entry points in `pyproject.toml` if needed

## GitHub Configuration

- [ ] Enable **Discussions** (optional)
- [ ] Enable **Private vulnerability reporting**
- [ ] Enable **Dependabot alerts**
- [ ] Enable **Dependabot security updates**
- [ ] Set up **branch protection** rules
- [ ] Apply labels: `./scripts/apply-labels.sh baseline`

## Issue Templates

- [ ] Review and customize `.github/ISSUE_TEMPLATE/*.yml`
- [ ] Remove templates you don't need
- [ ] Update labels in templates to match your label set

## Cleanup

- [ ] Delete `docs/examples/` (reference only)
- [ ] Delete unused issue templates
- [ ] Remove or update example code in `src/`
- [ ] Remove or update example tests in `tests/`
- [ ] Clear `CHANGELOG.md` for your project's history
- [ ] Remove template-specific notes from documentation

## Verification

- [ ] Run `python -m pip install -e .` successfully
- [ ] Run `pytest` — all tests pass
- [ ] Run `ruff check .` — no linting errors
- [ ] Run `mypy src/` — no type errors
- [ ] Verify imports work: `python -c "import your_package"`

---

## Optional Steps

- [ ] Add CI/CD workflows (`.github/workflows/`)
- [ ] Set up pre-commit hooks (`pre-commit install`)
- [ ] Configure code coverage reporting
- [ ] Add project-specific documentation
- [ ] Set up GitHub Pages for docs
