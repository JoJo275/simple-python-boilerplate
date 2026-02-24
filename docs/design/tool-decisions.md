# Tool Decisions

A living reference of tool evaluation notes — what was chosen, what was
skipped, and why.  This complements the formal [ADRs](../adr/) with the
lighter-weight reasoning that comes up when comparing specific tools.

> **When to write here vs. an ADR:**
> An ADR captures a *significant architectural decision* (e.g. "use pre-commit
> hooks" or "adopt a CI gate pattern").  This file captures the *tool-level
> trade-off notes* within those decisions (e.g. "typos over codespell because
> it's faster and broader").

---

## Pre-commit Hooks

See [ADR 008](../adr/008-pre-commit-hooks.md) for the architectural decision
to use pre-commit.  Notes below cover individual hook tool choices.

### Chosen

| Tool | Category | Why chosen |
|------|----------|-----------|
| **Ruff** | Lint + format | Single Rust binary that subsumes flake8, isort, pyupgrade, autopep8, and black. Orders of magnitude faster. Configured in one `[tool.ruff]` section. |
| **typos** | Spellcheck | Rust-based, faster and broader detection than codespell. Auto-fix support. Config in `_typos.toml`. |
| **pip-audit** | Vulnerability scan | PyPA-maintained, uses OSV + PyPI advisory DB. Successor to safety. |
| **gitleaks** | Secret detection | 150+ curated rules with entropy analysis. Single Go binary. Complements the fast regex `no-secrets-patterns` hook. |
| **deptry** | Dependency hygiene | No real alternative in Python. Compares `pyproject.toml` against actual imports to find unused, missing, and transitive deps. |
| **actionlint** | Workflow linting | Only mature GitHub Actions workflow linter. Catches expression errors, unknown runner labels, missing action inputs. |
| **commitizen** | Commit messages | Validates Conventional Commits format. Also provides `cz commit` for interactive authoring. |
| **validate-pyproject** | Config validation | Validates `pyproject.toml` against PEP 621 / packaging schemas. Catches schema errors before CI. |
| **check-jsonschema** | Config validation | SchemaStore-backed validation for GitHub workflows, actions, and Dependabot config. |
| **no-commit-to-branch** | Branch safety | Prevents accidental direct commits to `main`/`master`. Zero config, zero cost. |
| **check-docstring-first** | Code quality | Catches code placed before the module docstring — easy to miss in review. |

### Skipped

| Tool | Category | Why skipped |
|------|----------|------------|
| **prettier** | Formatter | Ruff handles Python formatting; `check-yaml`/`check-toml`/`check-json` cover config files. Adding a Node.js dependency for marginal benefit isn't worth it. |
| **pyupgrade** | Code moderniser | Ruff's `UP` rule set includes all pyupgrade checks. Running both is redundant. |
| **autopep8** | Formatter | Ruff's formatter and linter cover all autopep8 fixes. |
| **black** | Formatter | `ruff-format` is a drop-in replacement, faster, and configured alongside the linter in one tool. |
| **isort** | Import sorter | `ruff check` with isort rules (`I`) handles import sorting. Separate isort adds a dependency for duplicate functionality. |
| **codespell** (as a hook) | Spellcheck | typos is faster and has broader detection. codespell still runs in CI (`spellcheck.yml`) as a complementary safety net — the two overlap ~80% but each catches things the other misses. |
| **safety** | Vulnerability scan | pip-audit is the PyPA-maintained successor. safety's free tier scans an older, smaller database subset. |
| **trufflehog** | Secret detection | More complex setup, heavier runtime. gitleaks covers the same use case with a simpler single-binary approach. |
| **Husky** | Git hooks framework | Node.js-based. Adds a Node dependency to a Python project. pre-commit is Python-native and has a larger hook ecosystem. |
| **markdownlint-cli2** (as active) | Markdown linting | Available as manual hook. Not active because it requires Node.js — heavier dependency footprint for optional benefit. |
| **hadolint** (as active) | Dockerfile linting | Available as manual hook. Requires Docker runtime. Also covered in CI by Trivy misconfig scanning. |

### Notes

- **typos + codespell dual strategy:** typos runs locally (fast, Rust-based,
  pre-commit stage). codespell runs in CI (`spellcheck.yml`) with its own
  wordlist. They overlap ~80% but each catches things the other misses.
  Keeping both is intentional — not redundancy.

- **deptry requires project venv:** Unlike most hooks that run in pre-commit's
  isolated environment, deptry needs access to your installed packages to
  compare against imports.  That's why it runs as a `local`/`system` hook via
  `hatch run deptry .` rather than as a remote-repo hook.

- **pip-audit on pre-push, not pre-commit:** Vulnerability scans hit a network
  API and can take several seconds.  Running on every commit would be too slow.
  pre-push is the right trade-off — catches issues before code leaves your
  machine without slowing down every commit.

---

## GitHub Actions Workflows

See [ADR 003](../adr/003-separate-workflow-files.md) for why workflows are in
separate files, and [ADR 024](../adr/024-ci-gate-pattern.md) for the CI gate
pattern.

### Chosen

| Workflow | Purpose | Why chosen |
|----------|---------|-----------|
| **ci-gate.yml** | Fan-in required check | Single `gate` status in branch protection instead of listing every workflow individually. Adding/removing workflows only requires editing one array in code — no Settings changes. |
| **lint-format.yml** | Ruff lint + format | Core quality gate. Ruff is the single linter/formatter (ADR 005). |
| **test.yml** | pytest matrix | Runs across Python 3.11–3.13. Core quality gate. |
| **type-check.yml** | mypy | Strict type checking (ADR 007). |
| **coverage.yml** | pytest-cov | Tracks coverage trends. |
| **security-audit.yml** | pip-audit | Vulnerability scanning against OSV/PyPI DB. |
| **bandit.yml** | Bandit security lint | Path-filtered to `src/`/`scripts/` — only runs when Python source changes. |
| **codeql.yml** | GitHub CodeQL | Deep semantic analysis. Scheduled + PR-triggered. |
| **dependency-review.yml** | Dependency review | Flags new dependencies with known vulnerabilities on PRs. |
| **container-build.yml** | OCI image build | Builds the Containerfile on push/PR. |
| **container-scan.yml** | Trivy + Grype | Multi-scanner container vulnerability scanning (ADR 012). |
| **spellcheck.yml** | codespell in CI | Safety net for typos that the local `typos` hook might miss. |
| **link-checker.yml** | lychee | Validates URLs in docs. Path-filtered to `*.md`/`*.html`/`docs/`. |
| **commit-lint.yml** | Commit message validation | Ensures Conventional Commits on PRs (ADR 009). |
| **pr-title.yml** | PR title validation | Ensures PR titles follow conventional format. |
| **release-please.yml** | Automated releases | Changelog + version bumps (ADR 021). |
| **scorecard.yml** | OpenSSF Scorecard | Supply-chain security posture scoring. |
| **sbom.yml** | SBOM generation | Software Bill of Materials (ADR 013). |
| **nightly-security.yml** | Nightly full scan | Comprehensive security sweep on schedule. |
| **stale.yml** | Issue/PR cleanup | Auto-labels and closes stale issues/PRs. |
| **labeler.yml** | Auto-labeling | Labels PRs based on changed paths. |
| **pre-commit-update.yml** | Hook updates | Weekly PR to update pre-commit hook versions. |
| **spellcheck-autofix.yml** | Autofix typos | Weekly PR with codespell auto-corrections. |

### Skipped / Not adopted

| Workflow idea | Why skipped |
|--------------|------------|
| **Mega CI workflow** | Would consolidate all jobs into one file with `needs:`. Violates ADR 003 (separate files). Loses per-workflow triggers, permissions, path filters, and independent failure isolation. The ci-gate pattern solves the "single required check" problem without this trade-off. |
| **auto-merge Dependabot** | Considered but deferred. Would auto-approve + merge minor/patch Dependabot PRs. Useful for reducing toil, but need to set up first and ensure security-audit + dependency-review pass before auto-merge. Can add later. |
| **docs-deploy.yml** (MkDocs) | Have `mkdocs.yml` and `site/` but docs aren't deployed to GitHub Pages yet. Worth adding when ready to publish — even just `mkdocs build --strict` to catch broken cross-refs. |

### Notes

- **Path-filtered workflows and branch protection:** Workflows with `paths:`
  triggers (bandit, link-checker) can't be listed as required status checks in
  branch protection — they don't run on every PR, so GitHub would wait forever
  for a check that never appears.  The ci-gate pattern handles this by only
  requiring always-run workflows in the `REQUIRED_CHECKS` list.

- **Scheduled workflows as safety nets:** Most security and scanning workflows
  run on a weekly schedule in addition to PR triggers.  This ensures that even
  if a path filter skips a check on a particular PR, the check still runs
  regularly on `main`.

---

## Python Tooling

### Chosen

| Tool | Purpose | Why chosen |
|------|---------|-----------|
| **Hatch** | Project manager + env manager | Manages virtualenvs, runs scripts, builds packages. Single tool replaces tox + pip-tools + build (ADR 016). |
| **Hatchling** | Build backend | PEP 517 build backend. Pairs with Hatch, auto-discovers `src/` layout. |
| **hatch-vcs** | Version from git tags | Dynamic versioning from git tags. No manual version bumps. |
| **pytest** | Test framework | De facto standard. Rich plugin ecosystem (ADR 006). |
| **mypy** | Type checker | Strict mode. Best error messages for gradual typing (ADR 007). |
| **Ruff** | Linter + formatter | See pre-commit section above (ADR 005). |

### Skipped

| Tool | Why skipped |
|------|------------|
| **tox** | Hatch environments cover the same use case (matrix testing, isolated envs) with less configuration. |
| **Poetry** | Excellent tool but uses a non-standard `[tool.poetry]` config. Hatchling uses standard PEP 621 metadata. |
| **setuptools** | Works but requires more boilerplate. Hatchling auto-discovers `src/` layout with zero config. |
| **Pyright** | Valid alternative to mypy. mypy was chosen for broader community adoption and better error messages for gradual typing. Pyright is available via Pylance in VS Code for real-time feedback. |
| **pip-tools** | `pip-compile` is useful for pinning, but Hatch environments + `pyproject.toml` extras handle dependency management for this project's needs. See [ADR 026](../adr/026-no-pip-tools.md) for detailed rationale. |
