# Copilot Instructions

Guidelines for GitHub Copilot when working in this repository.

<!-- TODO (template users): This file is tailored to the boilerplate's
     conventions.  After forking, update it to match YOUR project:
     - Replace project-specific names, entry points, and paths
     - Add your own conventions, review priorities, and ignore rules
     - Remove sections that don't apply to your project
     - Add any domain-specific context that helps Copilot assist you
     Copilot reads this file on every interaction, so keep it accurate. -->

---

## How This Project Works

### Overview

A Python boilerplate/template project using src/ layout, Hatch for
environment/build management, and extensive CI/CD. The single source of truth
for almost all tool configuration is `pyproject.toml`.

### Domain / Business Context

This is a **template repository** — there is no application logic. The
"product" is the project structure, CI/CD pipelines, tooling conventions,
and documentation scaffolding. Everything under `src/` is placeholder code
that template users replace with their own implementation.

<!-- TODO (template users): Replace the paragraph above with 2-3 sentences
     describing what YOUR application does. Copilot is far more useful when
     it knows the domain.
     Examples:
       "A payment processing API that integrates with Stripe and handles
        subscription lifecycle management."
       "A CLI tool for analysing genomics data from FASTQ files."
     Delete this comment block after replacing. -->

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

| Stage | Key hooks | Count |
|-------|-----------|-------|
| **pre-commit** | ruff, mypy, bandit, typos, actionlint, deptry, + pre-commit-hooks suite | 35 |
| **commit-msg** | commitizen (Conventional Commits) | 1 |
| **pre-push** | pytest, pip-audit, gitleaks | 3 |
| **manual** | markdownlint-cli2, hadolint-docker, forbid-submodules | 3 |

Full hook inventory: [ADR 008](../docs/adr/008-pre-commit-hooks.md) |
Config: `.pre-commit-config.yaml` · Typos config: `_typos.toml`

### GitHub Actions Workflows

~29 workflow files in `.github/workflows/`, all SHA-pinned
([ADR 004](../docs/adr/004-pin-action-shas.md)) with repository guard pattern
([ADR 011](../docs/adr/011-repository-guard-pattern.md)).
**Canonical inventory:** `docs/workflows.md` — that file is authoritative;
the summary below is for quick orientation only.

**Categories at a glance:**

- **Quality:** test (3.11–3.13 matrix), lint-format (Ruff), type-check (mypy), coverage, spellcheck
- **Security:** bandit, pip-audit, CodeQL, dependency-review, Trivy container scan, nightly scan, OpenSSF Scorecard
- **PR hygiene:** commit-lint, pr-title, labeler, spellcheck-autofix
- **Documentation:** docs-build (MkDocs strict build, CI gate), docs-deploy (GitHub Pages deployment)
- **Release:** release-please → release → SBOM
- **Container:** container-build, container-scan
- **Maintenance:** pre-commit-update, stale, link-checker, auto-merge-dependabot, cache-cleanup, regenerate-files
- **Gate:** `ci-gate.yml` — single required check for branch protection ([ADR 024](../docs/adr/024-ci-gate-pattern.md))

Path-filtered workflows (bandit, docs-deploy, link-checker) are excluded from
required checks because they don't run on every PR. `docs-build` runs on all
PRs and IS in the CI gate.

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
- `task actions:check` — CI gate: exit non-zero if stale or upgradable actions

### Scripts

Utility scripts live in `scripts/`. They are standalone tools, not part of
the installed package. See [`scripts/README.md`](../scripts/README.md) for the
full inventory.

Key scripts:
- `bootstrap.py` — One-command setup for fresh clones
- `customize.py` — Interactive project customization (use `--enable-workflows OWNER/REPO` for quick workflow enablement)
- `clean.py` — Remove build artifacts/caches
- `doctor.py` — Diagnostics bundle for bug reports

Run scripts directly (`python scripts/bootstrap.py`) or via Taskfile
shortcuts where available.

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

### Leave TODOs for Template Users

This is a **template repository**. When adding new files or features that
template users will need to customise, include clear `TODO (template users):`
comments explaining what to change. Examples:

- Workflow files → TODO to enable the repository guard
- Config files → TODO to replace placeholder values
- Source files → TODO to replace example logic with real implementation
- Documentation → TODO to update project-specific details

TODOs should be actionable and specific — not just "fill this in" but
"Replace `YOURNAME/YOURREPO` with your actual repo slug".

### Check Templates Before Creating Files

Before creating a new file, check whether a relevant template or example
exists in the project. Key templates:

- **ADR** → `docs/adr/template.md` — follow this structure for new ADRs
- **Workflow** → review an existing `.github/workflows/*.yml` for the
  repository guard pattern, SHA-pinned actions, and naming conventions
- **Migration** → `db/migrations/001_example_migration.sql`
- **Seed** → `db/seeds/001_example_seed.sql`
- **Script** → review `scripts/` for naming and shebang conventions. **Important:** After creating a script with a shebang (`#!/usr/bin/env python3`), mark it executable: `git add --chmod=+x scripts/my_script.py`

### Keep Related Files in Sync

When updating a file, check whether other files reference or depend on what
changed and update them too. Examples:

- Adding a workflow → update `docs/workflows.md` and the categories list in this file
- Adding a pre-commit hook → update ADR 008's hook inventory and the hook table in this file
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

Don't just comply with every request. Push back when something is wrong,
overcomplicated, or conflicts with how this project works. Specifically:

- A request would introduce unnecessary complexity or tech debt
- There's a simpler, more idiomatic approach available
- A change conflicts with existing project conventions or ADRs
- A dependency is being added when a stdlib solution would suffice
- A proposed pattern doesn't scale or has known pitfalls
- Code or documentation is misleading, vague, or sugarcoated

Be direct: state the problem, explain why it matters, suggest an
alternative. Don't hedge with "you might consider" or "it could
potentially be beneficial" — say what the issue is and what to do
about it. Let the user make the final call, but don't soften the
assessment to be polite.

### Session Recap

At the end of a significant coding session (multiple changes, new features,
debugging sessions, or multi-step tasks), provide a brief recap that covers:

1. **What changed** — files created, modified, or deleted
2. **Why** — the motivation or problem being solved
3. **Impact** — how the changes benefit the project (e.g., reduced
   complexity, improved safety, better DX) *and* any downsides or
   trade-offs introduced (e.g., added maintenance burden, increased
   build time, new dependency). Be honest about both sides so the user
   can judge the net effect.
4. **What to watch for** — any follow-up steps, known issues, or things
   that need manual verification (e.g., "run pre-commit to verify",
   "update branch protection to add the new check")
5. **Decisions made** — any trade-offs or choices worth remembering
6. **Recommendations** — improvements, refactors, or follow-up work
   noticed during the session, even if unrelated to the current task.
   Include brief rationale and rough priority (do-soon vs. nice-to-have).
   Don't bury observations — if something is wrong, say so plainly.

Skip the recap for trivial single-file edits or quick Q&A.

### Surface Issues

During any session, proactively surface issues, risks, or anomalies
noticed — even when they're not directly related to the current task.
Examples: stale docs that contradict reality, a config that silently
does nothing, a pattern that will break at scale, a TODO that should
have been resolved long ago. Don't silently sweep things under the rug.
Raise them at end of session (in the recap's "What to watch for") or
inline if they're urgent. Keep each flag brief: what's wrong, why it
matters, and a suggested next step.

### Verify Before Finishing

Before concluding a task, verify the changes actually work:

- **Code changes** — run the relevant tests (`task test`) or at minimum
  check for syntax/type errors
- **Workflow changes** — run `actionlint` against modified files
- **Config changes** — run `validate-pyproject` or the relevant validator
- **Hook changes** — run `pre-commit run <hook-id> --all-files` for
  modified hooks
- **Documentation changes** — check that links resolve and markup renders
- **SHA-pinned actions** — when updating a SHA-pinned GitHub Action,
  verify the commit SHA actually exists on the upstream repo's releases
  page before committing. A wrong or truncated SHA will silently break
  every workflow that references it.

Don't declare something done based on "it looks right." If a
verification step is available, run it.

### Tone

Be direct and factual. Don't pad responses with filler praise ("Great
question!", "This is a really well-structured project!") or hedge
assessments to sound diplomatic. If something is broken, say it's broken.
If a design choice has downsides, name them. The user wants accurate
information, not reassurance.

This applies to documentation too — don't write marketing copy in docs,
READMEs, or comments. State what something does, what its limitations are,
and move on.

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
8. **Comments** — Explain *why*, not *what*. Skip comments that restate the code
   (`# Read the file` before `file.read_text()`). Add them when the reasoning
   isn't obvious — non-trivial regex patterns, workarounds, design trade-offs,
   or "this looks wrong but is intentional because…"
9. **Code style** — Ruff handles most of this automatically

### General Guidance
- **Prefer minimal diffs** — Avoid stylistic rewrites; Ruff already enforces formatting
- **Don't churn** — Only suggest changes that add clear value
- **Use Hatch for virtual environments** — Prefer `hatch shell` to enter the dev environment rather than creating manual `.venv` directories. Hatch manages environments automatically and keeps them in sync with `pyproject.toml`. Don't create `.venv` or `.venv-1` directories manually; use `hatch env create` if you need to explicitly create an environment.
- **Never install packages globally** — Always install into a Hatch-managed environment. Never run bare `pip install <package>` outside a venv. Use `hatch run <cmd>` or `hatch shell` for project work, or `pipx` for standalone CLI tools.

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

## Architecture & Design References

For deeper context beyond what's in this file, consult these docs:

- **`docs/design/architecture.md`** — System overview, module responsibilities,
  data flows, CI/CD architecture, and what's not yet implemented
- **`docs/design/tool-decisions.md`** — Detailed tool comparison notes: what
  was chosen, what was skipped, and why (pre-commit hooks, workflows, Python tooling)
- **`docs/adr/`** — Architecture Decision Records (template: `docs/adr/template.md`)

These are the canonical references for *why* things are the way they are.
This file summarises *what* to do; those files explain the reasoning.

**When numbers in this file conflict with those docs, those docs win.**
This file is a quick-reference summary that can go stale; the docs above
are maintained as the source of truth.

Key ADRs that most affect day-to-day work:

| ADR | Decision |
|-----|----------|
| 001 | src/ layout for package structure |
| 002 | pyproject.toml for all configuration |
| 005 | Ruff for linting and formatting |
| 008 | Pre-commit hooks (full inventory) |
| 009 | Conventional commits |
| 011 | Repository guard pattern |
| 016 | Hatchling and Hatch |
| 024 | CI gate pattern |
| 026 | No pip-tools for dependency management |

Full index: `docs/adr/README.md`

## Common Issues to Catch

1. **Missing `pip install -e .`** — If running from source, use editable install so imports resolve with src/ layout
2. **Import from wrong location** — Should import from `simple_python_boilerplate`, not `src`
3. **Mutable default arguments** — `def func(items=[])` is a bug
4. **Bare except clauses** — Should catch specific exceptions
5. **Unused imports/variables** — Ruff catches these, but flag if missed
6. **Hatch env stale after dependency removal** — After removing a dependency from `pyproject.toml`, run `hatch env remove default` then re-create. Hatch doesn't auto-uninstall removed packages; the old package silently remains.
7. **Installing packages outside a venv** — Never run bare `pip install <package>`. Always use a Hatch env, `.venv`, or `pipx`. This is easy to forget and causes global pollution.
8. **CI gate check name drift** — If you rename a workflow job's `name:` field, the CI gate will silently stop finding it and timeout. Always update `REQUIRED_CHECKS` in `ci-gate.yml` when renaming job display names.
9. **Scripts with shebangs must be executable** — If you add a shebang (`#!/usr/bin/env python3`) to a script, mark it executable in git: `git add --chmod=+x scripts/my_script.py`. The pre-commit hook `check-shebang-scripts-are-executable` will fail otherwise.

## Known Limitations / Tech Debt

Acknowledged gaps that don't need to be rediscovered each session:

| Area | Issue | Notes |
|------|-------|-------|
| **CI** | Container scan is advisory-only | `container-scan.yml` results don't block PRs (intentional — but worth knowing). |
| **CI** | Docs deploy is path-filtered | `docs-deploy.yml` only runs on docs/src changes on push to main. Docs *build* validation is handled by `docs-build.yml` which runs on every PR and IS in the CI gate. |
| **Docs** | `docs/workflows.md` can drift | It's manually maintained. When adding/removing workflows, update it or it becomes misleading fast. |
| **Template** | Placeholder source code | Everything under `src/simple_python_boilerplate/` is example code. Template users must replace it entirely. |

<!-- Add new entries here as they're discovered. Remove entries when resolved. -->
