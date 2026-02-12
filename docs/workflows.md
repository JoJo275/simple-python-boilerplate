# GitHub Actions Workflows

This template includes GitHub Actions workflows for CI/CD automation. Workflows are organized into core (always active), optional (disabled by default), and suggested additions.

---

## Included Workflows

### Core Workflows (Active)

These workflows run automatically on push/PR to `main`.

| Workflow | File | Triggers | Purpose |
|----------|------|----------|---------|
| **Test** | [test.yml](../.github/workflows/test.yml) | push, PR, manual | Run pytest across Python 3.11, 3.12, 3.13 |
| **Lint + Format** | [lint-format.yml](../.github/workflows/lint-format.yml) | push, PR, manual | Ruff linting and format checks |
| **Spellcheck** | [spellcheck.yml](../.github/workflows/spellcheck.yml) | push, PR, manual | Check for typos with codespell |
| **Release** | [release.yml](../.github/workflows/release.yml) | tag push (`v*.*.*`) | Build distribution artifacts + SBOMs |
| **SBOM** | [sbom.yml](../.github/workflows/sbom.yml) | push, PR, weekly, manual | Generate SPDX and CycloneDX SBOMs |

### Optional Workflows (Disabled)

Disabled workflows are prefixed with `_` and don't run until renamed.

| Workflow | File | Triggers | Purpose |
|----------|------|----------|---------|
| **Spellcheck Autofix** | [_spellcheck-autofix.yml](../.github/workflows/_spellcheck-autofix.yml) | weekly, manual | Auto-fix typos and create PR |

To enable: rename the file to remove the underscore prefix.

### Dependabot

Not a workflow, but automated dependency updates via [dependabot.yml](../.github/dependabot.yml):

- **GitHub Actions** — Weekly updates, grouped by minor/patch
- **Python (pip)** — Weekly updates for dependencies

---

## Suggested Workflows (Not Yet Added)

These are common workflows you may want to add to your project.

### Type Checking

```yaml
# .github/workflows/typecheck.yml
name: Type Check

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  mypy:
    name: Mypy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: mypy src/
```

### Security Audit

```yaml
# .github/workflows/security.yml
name: Security

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 9 * * 1"  # Weekly on Monday

permissions:
  contents: read

jobs:
  audit:
    name: Dependency audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pip-audit
      - run: pip-audit
```

### Code Coverage

```yaml
# .github/workflows/coverage.yml
name: Coverage

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  coverage:
    name: Test coverage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]" pytest-cov
      - run: pytest --cov=simple_python_boilerplate --cov-report=xml
      - uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
          fail_ci_if_error: true
```

### Documentation Build

```yaml
# .github/workflows/docs.yml
name: Docs

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  build:
    name: Build docs
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install mkdocs mkdocs-material
      - run: mkdocs build --strict
```

### Stale Issues/PRs

```yaml
# .github/workflows/stale.yml
name: Stale

on:
  schedule:
    - cron: "0 0 * * *"  # Daily

permissions:
  issues: write
  pull-requests: write

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v9
        with:
          stale-issue-message: "This issue has been automatically marked as stale due to inactivity."
          stale-pr-message: "This PR has been automatically marked as stale due to inactivity."
          stale-issue-label: "stale"
          stale-pr-label: "stale"
          days-before-stale: 60
          days-before-close: 14
```

### Auto-merge Dependabot

```yaml
# .github/workflows/dependabot-automerge.yml
name: Dependabot Auto-merge

on:
  pull_request:

permissions:
  contents: write
  pull-requests: write

jobs:
  automerge:
    if: github.actor == 'dependabot[bot]'
    runs-on: ubuntu-latest
    steps:
      - uses: dependabot/fetch-metadata@v2
        id: metadata
      - if: steps.metadata.outputs.update-type == 'version-update:semver-patch'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Label Sync

```yaml
# .github/workflows/labels.yml
name: Labels

on:
  push:
    branches: [main]
    paths:
      - "labels/*.json"
  workflow_dispatch:

permissions:
  issues: write

jobs:
  sync:
    name: Sync labels
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: EndBug/label-sync@v2
        with:
          config-file: labels/baseline.json
```

### Pre-commit CI

```yaml
# .github/workflows/pre-commit.yml
name: Pre-commit

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: pre-commit/action@v3.0.1
```

### CodeQL (Security Analysis)

```yaml
# .github/workflows/codeql.yml
name: CodeQL

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 0 * * 0"  # Weekly on Sunday

permissions:
  security-events: write
  contents: read

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/analyze@v3
```

### Bandit (Python Security)

```yaml
# .github/workflows/bandit.yml
name: Bandit

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  bandit:
    name: Security scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install bandit
      - run: bandit -r src/ -ll
```

---

## Workflow Conventions

### File Naming

| Pattern | Meaning |
|---------|---------|
| `workflow.yml` | Active workflow |
| `_workflow.yml` | Disabled workflow (underscore prefix) |

### Common Configuration

All workflows in this template use:

- **Concurrency control** — Cancels in-progress runs on new pushes
- **Timeout limits** — Prevents runaway jobs
- **Minimal permissions** — Principle of least privilege
- **SHA-pinned actions** — Security best practice (see [ADR-004](adr/004-pin-action-shas.md))

### Triggers

| Trigger | When |
|---------|------|
| `push` | Code pushed to specified branches |
| `pull_request` | PR opened/updated against specified branches |
| `workflow_dispatch` | Manual trigger from GitHub UI |
| `schedule` | Cron schedule (e.g., weekly) |
| `release` | GitHub release published |

---

## Adding New Workflows

1. Create a new `.yml` file in `.github/workflows/`
2. Follow the conventions above
3. Pin actions to full SHAs (not tags)
4. Add minimal required permissions
5. Include concurrency and timeout settings
6. Test manually with `workflow_dispatch` before relying on triggers

---

## See Also

- [Releasing](releasing.md) — Release workflow details
- [ADR-003](adr/003-separate-workflow-files.md) — Why separate workflow files
- [ADR-004](adr/004-pin-action-shas.md) — Why pin to SHAs
- [SBOM Strategy](sbom.md) — SBOM formats, channels, and authoritative source
- [ADR-013](adr/013-sbom-bill-of-materials.md) — Why SPDX + CycloneDX with four distribution channels
- [GitHub Actions Docs](https://docs.github.com/en/actions)
