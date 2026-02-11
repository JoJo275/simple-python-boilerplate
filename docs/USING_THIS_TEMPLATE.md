# Using This Template

This document guides you through customizing the boilerplate files for your own project.

Implement any of these changes at your discretion — this is just a guide to help you get started. You can skip or modify steps as needed for your specific project.

## Quick Start

1. **Clone or use as template** on GitHub
2. **Find and replace** all placeholders (see below)
3. **Delete what you don't need**
4. **Customize** the remaining files

---

## Placeholders to Replace

Search your project for these placeholders and replace them with your values:

| Placeholder | Replace With | Files |
|-------------|--------------|-------|
| `simple-python-boilerplate` | Your project name | `README.md`, `pyproject.toml`, `SECURITY.md` |
| `simple_python_boilerplate` | Your package name (underscore) | `src/`, `pyproject.toml` |
| `JoJo275` | Your GitHub username/org | `SECURITY.md`, issue templates |
| `security@example.com` | Your security contact email | `SECURITY.md` |
| `[INSERT EMAIL ADDRESS]` | Your contact email | Various files |
| `[Your Name]` | Your name | `LICENSE`, `pyproject.toml` |

---

## Files to Customize

### Required Customization

| File | What to Change |
|------|----------------|
| `README.md` | Project name, description, badges, installation instructions |
| `pyproject.toml` | Package name, author, dependencies, URLs |
| `LICENSE` | Year, author name (or choose a different license) |
| `SECURITY.md` | Repository URL, contact email, PGP key (optional) |

### Optional Customization

| File | When to Customize |
|------|-------------------|
| `.github/ISSUE_TEMPLATE/*.yml` | Adjust fields, labels, or remove templates you don't need |
| `CONTRIBUTING.md` | Add project-specific contribution guidelines |
| `CODE_OF_CONDUCT.md` | Usually fine as-is (Contributor Covenant) |
| `labels/*.json` | Add custom labels for your workflow |

---

## Issue Templates

This template includes 5 issue templates:

| Template | Purpose | When to Keep |
|----------|---------|--------------|
| `bug_report` | Report confirmed bugs | Always |
| `feature_request` | Suggest enhancements | Always |
| `documentation` | Docs issues/improvements | If you have docs |
| `question` | Technical questions | Optional — can use Discussions instead |
| `performance` | Performance issues | If performance matters to your project |

### Removing Templates

Simply delete the `.yml` and `.md` files you don't need from `.github/ISSUE_TEMPLATE/`.

### Customizing Labels

1. Edit `labels/baseline.json` or `labels/extended.json`
2. Run `./scripts/apply-labels.sh baseline` (or `extended`)
3. Update issue template `labels:` fields to match

---

## Security Policy

Choose your security policy approach:

| Scenario | Use |
|----------|-----|
| No bug bounty (most projects) | `SECURITY.md` (default) or see `docs/templates/SECURITY_no_bounty.md` |
| With bug bounty | See `docs/templates/SECURITY_with_bounty.md` |
| Standalone bounty policy | See `docs/templates/BUG_BOUNTY.md` |

### Enabling Private Vulnerability Reporting

1. Go to your repo → **Settings** → **Security** → **Code security and analysis**
2. Enable **Private vulnerability reporting**
3. Users can now report vulnerabilities privately via GitHub

---

## GitHub Features to Enable

After creating your repo, consider enabling:

- [ ] **Discussions** — For Q&A and community conversations
- [ ] **Private vulnerability reporting** — For security issues
- [ ] **Dependabot alerts** — For dependency vulnerabilities
- [ ] **Dependabot security updates** — Auto-create PRs for vulnerable deps
- [ ] **Branch protection** — Require PR reviews, status checks

---

## Files You Can Delete

If you don't need certain features, remove these files:

| Delete | If You Don't Need |
|--------|-------------------|
| `docs/templates/` | Template files (copy what you need first) |
| `.github/ISSUE_TEMPLATE/question.*` | Question template (use Discussions) |
| `.github/ISSUE_TEMPLATE/performance.*` | Performance issue tracking |
| `labels/extended.json` | Extended label set (baseline is enough) |

---

## Checklist

### Initial Setup

- [ ] Clone or use "Use this template" on GitHub
- [ ] Rename the repository to your project name
- [ ] Update remote URL if cloned directly

### Placeholder Replacements

- [ ] Replace `simple-python-boilerplate` with your project name
- [ ] Replace `simple_python_boilerplate` with your package name (snake_case)
- [ ] Replace `JoJo275` with your GitHub username/org
- [ ] Replace `[Your Name]` with your name in `LICENSE` and `pyproject.toml`
- [ ] Replace `security@example.com` with your security contact

### Core Files

- [ ] Update `README.md` with project description and badges
- [ ] Update `pyproject.toml` (name, author, dependencies, URLs)
- [ ] Update `LICENSE` (year, author — or choose different license)
- [ ] Update `SECURITY.md` with your contact info

### Source Code

- [ ] Rename `src/simple_python_boilerplate/` to your package name
- [ ] Update imports in test files to match new package name
- [ ] Update entry points in `pyproject.toml` if needed

### GitHub Configuration

- [ ] Enable **Discussions** (optional)
- [ ] Enable **Private vulnerability reporting**
- [ ] Enable **Dependabot alerts**
- [ ] Enable **Dependabot security updates**
- [ ] Set up **branch protection** rules
- [ ] Apply labels: `./scripts/apply-labels.sh baseline`

### Issue Templates

- [ ] Review and customize `.github/ISSUE_TEMPLATE/*.yml`
- [ ] Remove templates you don't need
- [ ] Update labels in templates to match your label set

### Cleanup

- [ ] Delete `docs/templates/` (after copying what you need)
- [ ] Delete unused issue templates
- [ ] Remove or update example code in `src/`
- [ ] Remove or update example tests in `tests/`
- [ ] Clear `CHANGELOG.md` for your project's history
- [ ] Remove template-specific notes from documentation

### Gitignore Configuration

After adopting the template, add these directories to your `.gitignore` to keep local experiments and data out of version control:

- [ ] Add `experiments/` to `.gitignore`
- [ ] Add `var/` to `.gitignore`

Add the following to your `.gitignore`:

```gitignore
# Local experiments (scratch code, prototypes)
/experiments/

# Local data and state
/var/
```

### Verification

- [ ] Run `python -m pip install -e .` successfully
- [ ] Run `pytest` — all tests pass
- [ ] Run `ruff check .` — no linting errors
- [ ] Run `mypy src/` — no type errors
- [ ] Verify imports work: `python -c "import your_package"`

### Optional Steps

- [ ] Add CI/CD workflows (`.github/workflows/`)
- [ ] Set up pre-commit hooks (`pre-commit install`)
- [ ] Configure code coverage reporting
- [ ] Add project-specific documentation
- [ ] Set up GitHub Pages for docs

---

## Optional Tools to Consider

These aren't included in the template but are worth evaluating for your project:

| Tool | Category | When to Use |
|------|----------|-------------|
| **[SQLAlchemy](https://www.sqlalchemy.org/)** | ORM / Database | Need a relational DB with Python models |
| **[Alembic](https://alembic.sqlalchemy.org/)** | DB Migrations | Managing schema changes over time (pairs with SQLAlchemy) |
| **[Sphinx](https://www.sphinx-doc.org/)** | Documentation | Generated API docs or a documentation site |
| **[MkDocs](https://www.mkdocs.org/)** | Documentation | Markdown-based docs site (simpler than Sphinx) |
| **[FastAPI](https://fastapi.tiangolo.com/)** | Web Framework | Building an API (async, OpenAPI docs built-in) |
| **[Flask](https://flask.palletsprojects.com/)** | Web Framework | Lightweight web apps and APIs |
| **[CircleCI](https://circleci.com/)** | CI/CD | Alternative to GitHub Actions |
| **[Celery](https://docs.celeryq.dev/)** | Task Queue | Background / async job processing |
| **[Docker](https://www.docker.com/)** | Containerization | Reproducible builds and deployments |
| **[Podman](https://podman.io/)** | Containerization | Daemonless alternative to Docker |
| **[Sentry](https://sentry.io/)** | Error Tracking | Production error monitoring |
| **[HTTPX](https://www.python-httpx.org/)** | HTTP Client | Modern async-capable HTTP client (alternative to requests) |
| **[Nox](https://nox.thea.codes/)** | Task Runner | Multi-environment testing and automation |
| **[Tox](https://tox.wiki/)** | Task Runner | Test across multiple Python versions |

---

## Need Help?

- Open an issue on the [template repository](https://github.com/JoJo275/simple-python-boilerplate)
- Check existing issues for common questions
