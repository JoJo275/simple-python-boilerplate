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

| Stage          | Key hooks                                                               |  Count |
| :------------- | :---------------------------------------------------------------------- | -----: |
| **pre-commit** | ruff, mypy, bandit, typos, actionlint, deptry, + pre-commit-hooks suite |     38 |
| **commit-msg** | commitizen (Conventional Commits)                                       |      1 |
| **pre-push**   | pytest, pip-audit, gitleaks                                             |      3 |
| **manual**     | markdownlint-cli2, hadolint-docker, prettier, forbid-submodules         |      4 |
| **Total**      |                                                                         | **46** |

Full hook inventory: [ADR 008](../docs/adr/008-pre-commit-hooks.md)
Config: `.pre-commit-config.yaml` · Typos config: `_typos.toml`

### GitHub Actions Workflows

~36 workflow files in `.github/workflows/`, all SHA-pinned
([ADR 004](../docs/adr/004-pin-action-shas.md)) with repository guard pattern
([ADR 011](../docs/adr/011-repository-guard-pattern.md)).
**Canonical inventory:** `docs/workflows.md` — that file is authoritative.

See `.github/workflows/.instructions.md` for SHA pinning, repo guard, and
CI gate conventions.

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

Utility scripts live in `scripts/`. See [`scripts/README.md`](../scripts/README.md)
for the full inventory and `scripts/.instructions.md` for conventions.

### Documentation

MkDocs Material stack. See `docs/.instructions.md` for conventions and
`docs/adr/.instructions.md` for ADR procedures. Serve locally:
`hatch run docs:serve`.

### Key Configuration Files

| File                         | Controls                                                                                                                    |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `pyproject.toml`             | Project metadata, dependencies, Hatch envs, and all tool configs (ruff, mypy, pytest, coverage, bandit, deptry, commitizen) |
| `.pre-commit-config.yaml`    | All pre-commit hook definitions and stages                                                                                  |
| `_typos.toml`                | Typos spellchecker exceptions and config                                                                                    |
| `Taskfile.yml`               | Task runner shortcuts                                                                                                       |
| `mkdocs.yml`                 | Documentation site config                                                                                                   |
| `Containerfile`              | Multi-stage container build                                                                                                 |
| `release-please-config.json` | Release automation config                                                                                                   |
| `.github/dependabot.yml`     | Dependabot auto-update schedule                                                                                             |
| `.markdownlint-cli2.jsonc`   | markdownlint rule overrides (MD024 siblings_only, MD033 allowed elements, MD046 disabled)                                   |
| `mkdocs-hooks/repo_links.py` | MkDocs build hook: rewrites repo-relative links to GitHub URLs                                                              |
| `mkdocs-hooks/generate_commands.py` | MkDocs build hook: auto-regenerates `docs/reference/commands.md` before each build                                   |
| `mkdocs-hooks/include_templates.py` | MkDocs build hook: force-includes `docs/templates/` on MkDocs 1.6+ (which silently excludes `templates/` dirs)       |
| `*.code-workspace`           | VS Code workspace settings, recommended extensions, editor config. **Note:** `${workspaceFolder}` doesn't reliably expand in `.code-workspace` settings — use relative paths instead. |

### Targeted Instruction Files

File-type-specific rules live in `.instructions.md` files closer to the code
they govern. Copilot loads them automatically when the `applyTo` glob matches
the file being edited.

| File                                          | Scope                        |
| --------------------------------------------- | ---------------------------- |
| `.github/workflows/.instructions.md`          | Workflow YAML conventions    |
| `scripts/.instructions.md`                    | Script conventions           |
| `docs/.instructions.md`                       | Documentation conventions    |
| `docs/adr/.instructions.md`                   | ADR creation procedure       |
| `tests/.instructions.md`                      | Test conventions             |

This file covers **project-wide** rules. For file-type-specific details,
Copilot should prefer the targeted instruction file.

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

Before creating a new file, check the
[template inventory](../docs/reference/template-inventory.md) for existing
templates, examples, and conventions. Key ones: ADR template, workflow
pattern, script conventions, MkDocs hook pattern, SQL migrations.

The inventory also documents conventions for each file type (shebangs,
logging, argparse, registration steps, etc.).

### Use SKILL.md for Multi-step Operations

`.github/SKILL.md` contains step-by-step procedures for adding or modifying
project components (workflows, scripts, ADRs, hooks, dependencies,
instruction files). **Always read `SKILL.md` before performing multi-step
operations** — it lists not just the creation steps but also the required
sync steps (index updates, regeneration, instruction file updates) that are
easy to forget. If Copilot doesn't auto-load it, request it explicitly with
`#file:.github/SKILL.md`.

### Keep Related Files in Sync

When updating a file, check whether other files reference or depend on what
changed and update them too. Use the procedures in `.github/SKILL.md` as a
checklist to ensure all sync steps are completed.

Don't let documentation drift from reality.

### Keep Copilot Instructions Current

If a change to the project affects how Copilot should understand or work with
the codebase, update the relevant instruction file as part of the same change:

- **Targeted `.instructions.md` files first** — if a convention applies to a
  specific file type (workflows, scripts, tests, docs, ADRs), update the
  matching `.instructions.md` from the table above.
- **This file** (`copilot-instructions.md`) — for project-wide changes:
  new tool added/removed, new convention, new ADR, structural changes.
- When adding or renaming a `.instructions.md` file, update the
  "Targeted Instruction Files" table in this file.

The goal is to keep instruction files up-to-date so Copilot doesn't have
to rediscover project structure from scratch each session.

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

### Clean Up Dead Code When Encountered

Remove dead code (unused functions, orphaned imports, commented-out blocks,
stale helpers) as part of any task where you encounter it. Grep the codebase
first to confirm the symbol is truly unused (check direct calls and dynamic
references like `getattr`). Preserve symbols that are public API or documented
extension points. Flag removals in the session recap.

### Session Recap

At the end of a significant coding session (multiple changes, new features,
debugging sessions, or multi-step tasks), provide a brief recap that covers:

1. **What changed** — files created, modified, or deleted
2. **Why** — the motivation or problem being solved
3. **Impact** — how the changes benefit the project (e.g., reduced
   complexity, improved safety, better DX) _and_ any downsides or
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

8. **Comments** — Explain _why_, not _what_. Skip comments that restate the code
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
- `pathlib.Path` over `os.path`; `subprocess.run()` with arg lists (never `shell=True`)
- `tomllib` (stdlib 3.11+) for TOML; `importlib.metadata` for package introspection

Script-specific conventions (argparse, logging, shared modules) are in
`scripts/.instructions.md`.

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

See `.github/workflows/.instructions.md` for workflow conventions (SHA
pinning, repo guard, CI gate).

## Ignore / Don't Flag

- **Line length (E501)** — Disabled in this project; don't request rewrapping docstrings or comments unless readability is impacted
- **Generated files** — `*.egg-info/`, `__pycache__/`, `.venv/`
- **Types in tests** — See `tests/.instructions.md` for test-specific leniency

## Architecture & Design References

For deeper context beyond what's in this file, consult these docs:

- **`docs/design/architecture.md`** — System overview, module responsibilities,
  data flows, CI/CD architecture, and what's not yet implemented
- **`docs/design/tool-decisions.md`** — Detailed tool comparison notes: what
  was chosen, what was skipped, and why (pre-commit hooks, workflows, Python tooling)
- **`docs/adr/`** — Architecture Decision Records (template: `docs/adr/template.md`)

These are the canonical references for _why_ things are the way they are.
This file summarises _what_ to do; those files explain the reasoning.

**When numbers in this file conflict with those docs, those docs win.**
This file is a quick-reference summary that can go stale; the docs above
are maintained as the source of truth.

Key ADRs that most affect day-to-day work:

| ADR | Decision                                             |
| --- | ---------------------------------------------------- |
| 001 | src/ layout for package structure                    |
| 008 | Pre-commit hooks (full inventory, 46 hooks)          |
| 024 | CI gate pattern (single required check)              |
| 031 | Script conventions (argparse, logging, shebang, etc) |
| 040 | v1.0 release readiness checklist                     |

Full index (40 ADRs): [`docs/adr/README.md`](../docs/adr/README.md)

## Common Issues to Catch

1. **Missing `pip install -e .`** — If running from source, use editable install so imports resolve with src/ layout
2. **Import from wrong location** — Should import from `simple_python_boilerplate`, not `src`
3. **Mutable default arguments** — `def func(items=[])` is a bug
4. **Bare except clauses** — Should catch specific exceptions
5. **Unused imports/variables** — Ruff catches these, but flag if missed
6. **Hatch env stale after dependency removal** — After removing a dependency from `pyproject.toml`, run `hatch env remove default` then re-create. Hatch doesn't auto-uninstall removed packages; the old package silently remains.
7. **Installing packages outside a venv** — Never run bare `pip install <package>`. Always use a Hatch env, `.venv`, or `pipx`. This is easy to forget and causes global pollution.

## Known Limitations / Tech Debt

See [`docs/known-issues.md`](../docs/known-issues.md) for the current list.
That file is the canonical tracker — add new entries there, not here.
