# GitHub Actions Workflows

<!-- This file is the canonical reference for the project's workflow inventory.
     Keep it in sync whenever workflows are added, removed, or renamed.
     copilot-instructions.md and docs/design/architecture.md reference this file. -->

This project has **26 workflow files** in `.github/workflows/`. All workflows
follow the conventions described at the bottom of this page. Configure these workflows in their respective `.yml` file.

---

## Workflow Inventory

### Quality

| Workflow | File | Triggers | Job name(s) | Purpose |
|----------|------|----------|-------------|---------|
| **Test** | [test.yml](../.github/workflows/test.yml) | push, PR, manual | `Test (Python 3.11)` / `3.12` / `3.13` | Runs pytest across Python 3.11–3.13 matrix |
| **Lint + Format** | [lint-format.yml](../.github/workflows/lint-format.yml) | push, PR, manual | `Ruff (lint & format)` | Ruff linting and format checks |
| **Type Check** | [type-check.yml](../.github/workflows/type-check.yml) | push, PR, manual | `mypy (strict)` | mypy strict mode against `src/` |
| **Coverage** | [coverage.yml](../.github/workflows/coverage.yml) | push, PR, manual | `Test + upload coverage` | pytest with coverage, uploads to Codecov |
| **Spellcheck** | [spellcheck.yml](../.github/workflows/spellcheck.yml) | push, PR, manual | `Spell check (codespell)` | Fails CI on spelling mistakes |
| **Spellcheck Autofix** | [spellcheck-autofix.yml](../.github/workflows/spellcheck-autofix.yml) | weekly, manual | `Auto-fix typos` | Creates a PR to auto-fix spelling mistakes |

### Security

| Workflow | File | Triggers | Job name(s) | Purpose |
|----------|------|----------|-------------|---------|
| **Security Audit** | [security-audit.yml](../.github/workflows/security-audit.yml) | push, PR, weekly, manual | `pip-audit` | Checks Python deps against OSV/PyPI vuln databases |
| **Bandit** | [bandit.yml](../.github/workflows/bandit.yml) | push (path-filtered), PR (path-filtered), daily, manual | `Bandit security scan` | Static security analysis for Python source |
| **Dependency Review** | [dependency-review.yml](../.github/workflows/dependency-review.yml) | PR | `Scan dependencies` | Scans PRs for vulnerable or risky new dependencies |
| **CodeQL** | [codeql.yml](../.github/workflows/codeql.yml) | push, PR, weekly | `CodeQL Analysis` | GitHub CodeQL static analysis |
| **Container Scan** | [container-scan.yml](../.github/workflows/container-scan.yml) | push, PR, weekly, manual | `Trivy vulnerability scan`, `Grype vulnerability scan`, `Dockerfile / IaC lint` | Multi-scanner container security pipeline |
| **Nightly Security** | [nightly-security.yml](../.github/workflows/nightly-security.yml) | daily, manual | Multiple (SBOM rescan, pip-audit, container scans) | Consolidated nightly sweep against latest vuln databases |
| **OpenSSF Scorecard** | [scorecard.yml](../.github/workflows/scorecard.yml) | push (main), weekly, manual | `Scorecard analysis` | Evaluates repo security practices via OpenSSF Scorecard |

### PR Hygiene

| Workflow | File | Triggers | Job name(s) | Purpose |
|----------|------|----------|-------------|---------|
| **PR Title** | [pr-title.yml](../.github/workflows/pr-title.yml) | PR | `Conventional commit check` | Enforces conventional commit format on PR titles |
| **Commit Lint** | [commit-lint.yml](../.github/workflows/commit-lint.yml) | PR | `Validate commit messages` | Validates all PR commits follow Conventional Commits |
| **Labeler** | [labeler.yml](../.github/workflows/labeler.yml) | PR | `Auto-label PR` | Auto-labels PRs based on changed file paths |

### Release

| Workflow | File | Triggers | Job name(s) | Purpose |
|----------|------|----------|-------------|---------|
| **Release Please** | [release-please.yml](../.github/workflows/release-please.yml) | push (main) | `Create or update Release PR` | Automates version bump, changelog, and git tags |
| **Release** | [release.yml](../.github/workflows/release.yml) | tag push (`v*`), manual | `Build distribution`, `Generate release SBOMs`, `Upload release assets` | Builds sdist + wheel, optionally publishes to PyPI |
| **SBOM** | [sbom.yml](../.github/workflows/sbom.yml) | push, PR, weekly, manual | `Generate SBOMs` | Generates SPDX + CycloneDX SBOMs |

### Documentation

| Workflow | File | Triggers | Job name(s) | Purpose |
|----------|------|----------|-------------|---------|
| **Docs Deploy** | [docs-deploy.yml](../.github/workflows/docs-deploy.yml) | push (main, path-filtered), PR (path-filtered), manual | `Build docs`, `Deploy to GitHub Pages` | Builds MkDocs site (strict) and deploys to GitHub Pages on push to main |

### Container

| Workflow | File | Triggers | Job name(s) | Purpose |
|----------|------|----------|-------------|---------|
| **Container Build** | [container-build.yml](../.github/workflows/container-build.yml) | push (main + tags), PR, manual | `Build container image` | Builds OCI container image, pushes to ghcr.io on main/tags |

### Maintenance

| Workflow | File | Triggers | Job name(s) | Purpose |
|----------|------|----------|-------------|---------|
| **Pre-commit Update** | [pre-commit-update.yml](../.github/workflows/pre-commit-update.yml) | weekly, manual | `Auto-update hooks` | Runs `pre-commit autoupdate` and opens a PR |
| **Stale** | [stale.yml](../.github/workflows/stale.yml) | daily, manual | `Close stale issues & PRs` | Marks and closes inactive issues/PRs |
| **Link Checker** | [link-checker.yml](../.github/workflows/link-checker.yml) | push (path-filtered), PR (path-filtered), weekly, manual | `Check links` | Checks Markdown/HTML for broken links using lychee |
| **Auto-merge Dependabot** | [auto-merge-dependabot.yml](../.github/workflows/auto-merge-dependabot.yml) | pull_request_target | `Auto-approve & merge` | Auto-approves and squash-merges minor/patch Dependabot PRs once CI passes |

### Gate

| Workflow | File | Triggers | Job name(s) | Purpose |
|----------|------|----------|-------------|---------|
| **CI Gate** | [ci-gate.yml](../.github/workflows/ci-gate.yml) | PR, push, manual | `gate` | Single fan-in "all-green" check for branch protection ([ADR 024](adr/024-ci-gate-pattern.md)) |

---

## CI Gate: Required Checks

The CI gate ([ADR 024](adr/024-ci-gate-pattern.md)) polls for these job
display names. Branch protection only requires `gate` — not individual checks.

Each required workflow's `name:` line is tagged with `# ci-gate: required`.
Grep for that marker to audit which workflows are coupled to the gate:

```bash
# Unix / Git Bash
grep -r 'ci-gate: required' .github/workflows/

# PowerShell
Select-String -Path ".github\workflows\*.yml" -Pattern "ci-gate: required"
```

| Check name | Workflow |
|-----------|----------|
| `Ruff (lint & format)` | lint-format.yml |
| `mypy (strict)` | type-check.yml |
| `Spell check (codespell)` | spellcheck.yml |
| `Test + upload coverage` | coverage.yml |
| `Test (Python 3.11)` | test.yml |
| `Test (Python 3.12)` | test.yml |
| `Test (Python 3.13)` | test.yml |
| `pip-audit` | security-audit.yml |
| `Scan dependencies` | dependency-review.yml |
| `Build container image` | container-build.yml |
| `Conventional commit check` | pr-title.yml |
| `Validate commit messages` | commit-lint.yml |

**Excluded from gate** (path-filtered — don't run on every PR):

- `bandit.yml` — only runs on `src/**`, `scripts/**`, `experiments/**`, `pyproject.toml` changes
- `docs-deploy.yml` — only runs on `docs/**`, `mkdocs.yml`, `src/**/*.py`, `pyproject.toml` changes
- `link-checker.yml` — only runs on `**/*.md`, `**/*.html`, `docs/**` changes

These still report status when they run and also run on push to main + schedules.

---

## Dependabot

Not a workflow, but automated dependency updates via
[dependabot.yml](../.github/dependabot.yml):

- **GitHub Actions** — Weekly updates, grouped by minor/patch
- **Python (pip)** — Weekly updates for dependencies

---

## Workflow Conventions

All workflows in this project follow these patterns:

| Convention | Detail |
|-----------|--------|
| **SHA-pinned actions** | Full commit SHAs with human-readable version comments ([ADR 004](adr/004-pin-action-shas.md)) |
| **Repository guard** | Workflows are disabled by default via `YOURNAME/YOURTEMPLATE` slug check; enable with repo slug or `vars.ENABLE_*` variable ([ADR 011](adr/011-repository-guard-pattern.md)) |
| **Concurrency control** | `cancel-in-progress: true` per workflow + ref |
| **Timeout limits** | `timeout-minutes` set on every job |
| **Minimal permissions** | `permissions: contents: read` (least privilege) |
| **Persist-credentials: false** | On all checkout steps |
| **Header comments** | Each file has a comment block explaining purpose, triggers, and TODO instructions for template users |

### File Naming

| Pattern | Meaning |
|---------|---------|
| `workflow.yml` | Active workflow |

### Adding New Workflows

1. Create a new `.yml` file in `.github/workflows/`
2. Follow the conventions above — copy an existing workflow as a starting point
3. Pin actions to full SHAs (not tags) — use `scripts/workflow_versions.py` to manage
4. Add the repository guard pattern
5. Add minimal required permissions
6. Include concurrency and timeout settings
7. If the workflow should block PRs, add its job `name:` to `REQUIRED_CHECKS` in `ci-gate.yml`
   and tag the `name:` line with `# ci-gate: required`
8. Update this file and `copilot-instructions.md`

---

## See Also

- [Architecture — CI/CD section](design/architecture.md) — CI/CD architecture diagram
- [Releasing](releasing.md) — Release workflow details
- [SBOM Strategy](sbom.md) — SBOM formats, channels, and authoritative source
- [ADR 003](adr/003-separate-workflow-files.md) — Why separate workflow files
- [ADR 004](adr/004-pin-action-shas.md) — Why pin to SHAs
- [ADR 011](adr/011-repository-guard-pattern.md) — Repository guard pattern
- [ADR 013](adr/013-sbom-bill-of-materials.md) — SBOM strategy (SPDX + CycloneDX)
- [ADR 024](adr/024-ci-gate-pattern.md) — CI gate pattern
