# Copilot Instructions

Guidelines for GitHub Copilot when working in this repository.

---

## How This Project Works

### Overview

A Python boilerplate/template project using src/ layout, Hatch for
environment/build management, and extensive CI/CD. The single source of truth
for almost all tool configuration is `pyproject.toml`.

### Build & Environment — Hatch

- **Build backend:** Hatchling (`hatchling.build`) with `hatch-vcs` for git-tag versioning.
- **Environments:** Hatch manages virtualenvs. Run commands with `hatch run <cmd>` or enter a shell with `hatch shell`.
- **Dependency strategy:** `[project.optional-dependencies]` groups (`test`, `dev`, `extras`, `docs`) are the single source of truth. Hatch envs consume them via `features = [...]`.
- **Key environments:**
  - `default` — dev tools: ruff, mypy, pre-commit, bandit, commitizen, deptry (`hatch shell`)
  - `docs` — mkdocs + material + mkdocstrings (`hatch run docs:serve`)
  - `test` — pytest matrix across Python 3.11–3.13 (`hatch run test:run`)
- **Removing a dependency** requires `hatch env remove default` then re-running; Hatch doesn't auto-uninstall.
- **Version** comes from git tags via `hatch-vcs`. `release-please` creates the tags. Fallback: `0.0.0+unknown`.

### Pre-commit Hooks

Three installed hook stages plus a manual stage:

```
pre-commit install                              # pre-commit stage
pre-commit install --hook-type commit-msg        # commit-msg stage
pre-commit install --hook-type pre-push          # pre-push stage
```

| Stage | Hooks |
|-------|-------|
| **pre-commit** | trailing-whitespace, end-of-file-fixer, check-yaml/toml/json/ast, check-added-large-files, check-merge-conflict, check-case-conflict, debug-statements, detect-private-key, fix-byte-order-marker, name-tests-test, check-executables-have-shebangs, check-shebang-scripts-are-executable, check-symlinks, check-docstring-first, no-commit-to-branch (main/master), mixed-line-ending (LF), ruff (lint+fix), ruff-format, mypy, bandit, validate-pyproject, typos, actionlint, check-github-workflows, check-github-actions, check-dependabot, no-do-not-commit-marker, no-secrets-patterns, no-nul-bytes, deptry |
| **commit-msg** | commitizen (Conventional Commits validation) |
| **pre-push** | pytest test suite, pip-audit, gitleaks |
| **manual** | markdownlint-cli2, hadolint-docker |

- Config: `.pre-commit-config.yaml` (354 lines, heavily commented)
- Typos config: `_typos.toml`
- Minimum version: `3.6.0`

### GitHub Actions Workflows (24 files)

All workflows live in `.github/workflows/`, use SHA-pinned actions, and follow
the repository guard pattern (`vars.ENABLE_*`).

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test.yml` | PR / push | Pytest matrix (3.11–3.13) |
| `lint-format.yml` | PR / push | Ruff lint + format check |
| `type-check.yml` | PR / push | mypy strict mode |
| `coverage.yml` | PR / push | Coverage report |
| `commit-lint.yml` | PR | Conventional commit message validation |
| `pr-title.yml` | PR | PR title follows conventional format |
| `ci-gate.yml` | PR / push | Fan-in gate — single required check for branch protection |
| `bandit.yml` | PR (path-filtered) | Security linting on Python files |
| `link-checker.yml` | PR (path-filtered) | Broken link detection in Markdown |
| `spellcheck.yml` | PR / push | Codespell spell checking |
| `spellcheck-autofix.yml` | PR | Auto-fix spelling mistakes |
| `dependency-review.yml` | PR | License + vulnerability check on new deps |
| `security-audit.yml` | PR / push | pip-audit vulnerability scan |
| `nightly-security.yml` | schedule | Nightly security scan |
| `codeql.yml` | PR / schedule | GitHub CodeQL analysis |
| `scorecard.yml` | schedule | OpenSSF Scorecard |
| `container-build.yml` | PR / push | Build container image from Containerfile |
| `container-scan.yml` | PR / push | Trivy scan of container image |
| `release-please.yml` | push to main | Creates release PRs + changelogs |
| `release.yml` | release published | Build + publish artifacts |
| `sbom.yml` | release | Generate SBOM |
| `pre-commit-update.yml` | schedule | Auto-update pre-commit hooks |
| `labeler.yml` | PR | Auto-label PRs based on paths |
| `stale.yml` | schedule | Close stale issues/PRs |

**Branch protection** only requires the `gate` check from `ci-gate.yml`. Path-filtered
workflows (bandit, link-checker) are excluded from required checks because they
don't run on every PR — see ADR 024.

### Task Runner — Taskfile

`Taskfile.yml` wraps common `hatch run` commands for convenience. Run `task` to
list available tasks. Key ones:

- `task test` / `task test:cov` / `task test:matrix` — run tests
- `task lint` / `task lint:fix` / `task fmt` — linting and formatting
- `task typecheck` — mypy
- `task check` — all quality gates in one command
- `task pre-commit:install` / `task pre-commit:run` — pre-commit management
- `task commit` — interactive conventional commit via commitizen
- `task deps:versions` / `task deps:upgrade` — dependency management
- `task actions:versions` — show SHA-pinned action versions

### Documentation

- **MkDocs Material** stack: `mkdocs.yml` + `docs/` directory
- **ADRs** in `docs/adr/` — template at `docs/adr/template.md`
- **Tool decisions** (lightweight notes) in `docs/design/tool-decisions.md`
- **Architecture docs** in `docs/design/`
- Serve locally: `hatch run docs:serve`

### Key Configuration Files

| File | Controls |
|------|----------|
| `pyproject.toml` | Project metadata, dependencies, Hatch envs, and all tool configs (ruff, mypy, pytest, coverage, bandit, deptry, commitizen) |
| `.pre-commit-config.yaml` | All pre-commit hook definitions and stages |
| `_typos.toml` | Typos spellchecker exceptions and config |
| `Taskfile.yml` | Task runner shortcuts |
| `mkdocs.yml` | Documentation site config |
| `Containerfile` | Multi-stage container build |
| `release-please-config.json` | Release automation config |
| `.github/dependabot.yml` | Dependabot auto-update schedule |

---

## Working Style

### Check Templates Before Creating Files

Before creating a new file, check whether a relevant template or example
exists in the project. Key templates:

- **ADR** → `docs/adr/template.md` — follow this structure for new ADRs
- **Workflow** → review an existing `.github/workflows/*.yml` for the
  repository guard pattern, SHA-pinned actions, and naming conventions
- **Migration** → `db/migrations/001_example_migration.sql`
- **Seed** → `db/seeds/001_example_seed.sql`
- **Script** → review `scripts/` for naming and shebang conventions

### Keep Related Files in Sync

When updating a file, check whether other files reference or depend on what
changed and update them too. Examples:

- Adding a workflow → update the workflow table in this file and `docs/workflows.md`
- Adding a pre-commit hook → update ADR 008's hook inventory and this file's hook table
- Adding an ADR → update `docs/adr/README.md` index and the ADR table in this file
- Changing a dependency → update `docs/design/tool-decisions.md` if the tool is listed there
- Renaming a script or entry point → update `Taskfile.yml`, README, and any docs that reference it
- Making an architectural or tooling choice → update `docs/design/architecture.md`
  and/or `docs/design/tool-decisions.md` to reflect the current state
- Making a *significant* decision (new pattern, new tool category, new
  convention) → propose creating an ADR in `docs/adr/`. Use the template at
  `docs/adr/template.md`. Not every change needs an ADR — reserve them for
  decisions that are hard to reverse, affect multiple parts of the project, or
  would be useful context for future contributors. When an ADR is created,
  update `docs/adr/README.md` index and the ADR table in this file.

Don't let documentation drift from reality.

### Keep Copilot Instructions Current

If a change to the project affects how Copilot should understand or work with
the codebase, update this file (`copilot-instructions.md`) as part of the same
change. Examples worth capturing:

- New tool added or removed (update "How This Project Works" section)
- New workflow or hook (update the relevant table)
- New convention or pattern adopted (add to "Conventions")
- New ADR created (add to the ADR table)
- New template or example file (add to "Check Templates" list)

The goal is to keep this file as a reliable, up-to-date briefing so Copilot
doesn't have to rediscover project structure from scratch each session.

### Provide Feedback and Pushback

Don't just comply with every request. Push back or offer alternatives when:

- A request would introduce unnecessary complexity or tech debt
- There's a simpler, more idiomatic approach available
- A change conflicts with existing project conventions or ADRs
- A dependency is being added when a stdlib solution would suffice
- A proposed pattern doesn't scale or has known pitfalls

Frame pushback constructively: explain *why*, suggest an alternative, and let
the user decide. Being a yes-machine is less useful than being a thoughtful
collaborator.

### Session Recap

At the end of a significant coding session (multiple changes, new features,
debugging sessions, or multi-step tasks), provide a brief recap that covers:

1. **What changed** — files created, modified, or deleted
2. **Why** — the motivation or problem being solved
3. **What to watch for** — any follow-up steps, known issues, or things
   that need manual verification (e.g., "run pre-commit to verify",
   "update branch protection to add the new check")
4. **Decisions made** — any trade-offs or choices worth remembering

Skip the recap for trivial single-file edits or quick Q&A.

## Review Priorities

### High Priority
1. **Type hints** — Public functions should have type annotations (public = exported API and anything not prefixed with `_` in `src/`)
2. **Tests** — Changes should include or update relevant tests
3. **Security** — Flag:
   - Hardcoded credentials, secrets, API keys
   - SQL injection risks
   - `subprocess` with `shell=True` (prefer `shell=False` with argument list)
   - Unsafe `yaml.load()` (use `yaml.safe_load()`)
   - Logging secrets or tokens
4. **Import errors** — Ensure imports work with src/ layout (must be installed)

### Medium Priority
5. **Docstrings** — Public functions should have docstrings
6. **Error handling** — Appropriate exception handling
7. **Naming** — Clear, descriptive variable and function names

### Low Priority
8. **Comments** — Helpful but not excessive
9. **Code style** — Ruff handles most of this automatically

### General Guidance
- **Prefer minimal diffs** — Avoid stylistic rewrites; Ruff already enforces formatting
- **Don't churn** — Only suggest changes that add clear value
- **Never install packages globally** — Always install into the active virtual environment (`.venv`) or a Hatch-managed environment. Never run bare `pip install <package>` outside a venv. Use `pip install -e ".[dev]"` for project dependencies, `hatch env create` for Hatch environments, or `pipx` for standalone CLI tools. If no venv is active, create or activate one first.

## Conventions

### Python
- Use absolute imports: `from simple_python_boilerplate.module import func`
- Type hints for all public functions and methods
- Type checking uses **mypy** (strict mode) — prefer fixes compatible with mypy
- Docstrings in Google style format
- Constants in UPPER_SNAKE_CASE

### Project Structure
- Source code in `src/simple_python_boilerplate/`
- Tests in `tests/`
- Scripts in `scripts/`
- Documentation in `docs/`

### Git & PRs
- Conventional commit messages: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`
- Use `ci:` for workflow-only changes, `docs:` for docs-only changes, `chore:` for maintenance
- One logical change per commit
- PR titles follow conventional commit format

### Commit Message Format

When generating commit messages, follow the template in `.gitmessage.txt`:

```
<type>(<scope>): <description>

Why: <motivation for the change>

What changed: <summary of changes>

How tested: <how the change was verified>

Breaking change: <describe if applicable, otherwise omit>

Issues/Refs: #<issue number if applicable, otherwise omit>
```

- **type** — `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- **scope** — optional area affected (e.g., `cli`, `docs`, `ci`)
- **description** — imperative mood, lowercase, no period, max 50 chars
- Body sections (`Why`, `What changed`, `How tested`) should be included for non-trivial commits
- Omit `Breaking change` and `Issues/Refs` sections when not applicable

### CI/CD
- GitHub Actions pinned to full commit SHAs (not tags)
- Workflows separated by concern (e.g., test, lint, release)

## Ignore / Don't Flag

- **Line length (E501)** — Disabled in this project; don't request rewrapping docstrings or comments unless readability is impacted
- **Generated files** — `*.egg-info/`, `__pycache__/`, `.venv/`
- **Types in tests** — Be less strict; don't require full annotations for mocks, fixtures, or test helpers. Don't require annotations for pytest fixtures unless they clarify intent.

## Architecture Decisions

Key decisions are documented in `docs/adr/` (template: `docs/adr/template.md`).
Tool-level trade-off notes live in `docs/design/tool-decisions.md`.

| ADR | Decision |
|-----|----------|
| 001 | src/ layout for package structure |
| 002 | pyproject.toml for all configuration |
| 003 | Separate GitHub Actions workflow files |
| 004 | Pin GitHub Actions to commit SHAs |
| 005 | Ruff for linting and formatting |
| 006 | pytest for testing |
| 007 | mypy for type checking |
| 008 | Pre-commit hooks (full inventory) |
| 009 | Conventional commits |
| 010 | Dependabot for dependency updates |
| 011 | Repository guard pattern |
| 012 | Multi-layer security scanning |
| 013 | SBOM / bill of materials |
| 014 | No template engine |
| 015 | No .github directory README |
| 016 | Hatchling and Hatch |
| 017 | Task runner (Taskfile) |
| 018 | Bandit for security linting |
| 019 | Containerfile |
| 020 | MkDocs documentation stack |
| 021 | Automated release pipeline |
| 022 | Rebase merge strategy |
| 023 | Branch protection rules |
| 024 | CI gate pattern |

## Common Issues to Catch

1. **Missing `pip install -e .`** — If running from source, use editable install so imports resolve with src/ layout
2. **Import from wrong location** — Should import from `simple_python_boilerplate`, not `src`
3. **Mutable default arguments** — `def func(items=[])` is a bug
4. **Bare except clauses** — Should catch specific exceptions
5. **Unused imports/variables** — Ruff catches these, but flag if missed
