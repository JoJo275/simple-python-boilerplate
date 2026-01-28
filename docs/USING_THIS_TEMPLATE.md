# Using This Template

This document guides you through customizing the boilerplate files for your own project.

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
| No bug bounty (most projects) | `SECURITY.md` (default) or see `docs/examples/SECURITY_no_bounty.md` |
| With bug bounty | See `docs/examples/SECURITY_with_bounty.md` |
| Standalone bounty policy | See `docs/examples/BUG_BOUNTY.md` |

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
| `docs/examples/` | Example files (reference only) |
| `.github/ISSUE_TEMPLATE/question.*` | Question template (use Discussions) |
| `.github/ISSUE_TEMPLATE/performance.*` | Performance issue tracking |
| `labels/extended.json` | Extended label set (baseline is enough) |

---

## Checklist

Before publishing your project:

- [ ] Replaced all placeholders
- [ ] Updated `README.md` with actual project info
- [ ] Set correct license and author
- [ ] Configured `SECURITY.md` with real contact info
- [ ] Removed unused issue templates
- [ ] Applied labels to your GitHub repo
- [ ] Enabled GitHub security features
- [ ] Deleted example/template documentation

---

## Need Help?

- Open an issue on the [template repository](https://github.com/JoJo275/simple-python-boilerplate)
- Check existing issues for common questions
