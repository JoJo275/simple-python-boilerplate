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

### Hatchling vs Hatch — The Mental Model

These two names kept confusing me. The key distinction:

- **Hatchling** = "how to build the package" (build backend, like setuptools)
- **Hatch** = "how to work on the project" (project manager, like tox/nox + venv)

| Tool | What it does | Config section |
|------|-------------|----------------|
| **Hatchling** | Builds sdist/wheel when you `pip install .` or `python -m build` | `[build-system]`, `[tool.hatch.build.*]` |
| **Hatch** | Manages envs, runs scripts, bumps versions, triggers builds | `[tool.hatch.envs.*]`, `[tool.hatch.version]` |

**Why use both?** A single `pyproject.toml` defines everything:
- Build backend (Hatchling)
- What goes into distributions (include/exclude rules)
- Version source/bumping rules
- Dev/test/lint environments and scripts (Hatch)

**Important:** Hatchling works *without* Hatch installed. Anyone can `pip install .` and Hatchling handles the build. Hatch is optional — it's a convenience CLI for developers.

See: [ADR 016](../adr/016-hatchling-and-hatch.md)

### Python Tool Landscape

There are a lot of overlapping tools in the Python ecosystem. This table groups them by purpose.

#### Build Backends (what `pip install .` uses)

| Tool | Description | Capabilities | Pros | Cons |
|------|-------------|-------------|------|------|
| **Hatchling** | Modern build backend by the Hatch project | Build sdist/wheel, auto-discover packages, include/exclude rules, plugins | Fast, minimal config, auto-discovers src/ layout | Newer, smaller ecosystem than setuptools |
| **setuptools** | The original build backend | Build sdist/wheel, C extensions, entry points, data files, find_packages | Ubiquitous, massive community, battle-tested | Verbose config, legacy baggage (`setup.py`, `setup.cfg`) |
| **Flit-core** | Minimalist build backend | Build sdist/wheel for pure-Python packages | Dead simple for pure-Python packages | No compiled extensions, fewer features |
| **PDM-backend** | Build backend from the PDM project | Build sdist/wheel, PEP 621 metadata, editable installs | PEP 621 native, supports lock files | Tied to PDM ecosystem |
| **Maturin** | Build backend for Rust+Python (PyO3) | Build wheels with compiled Rust extensions, cross-compile | First-class Rust FFI support | Only for Rust extensions |

#### Project/Environment Managers (create envs, run tasks)

| Tool | Description | Capabilities | Pros | Cons |
|------|-------------|-------------|------|------|
| **Hatch** | Project manager + env manager | Create/manage envs, run scripts, test matrices, version bumping, build, publish | Env management, test matrices, scripts, version bumping — all in `pyproject.toml` | Less established than tox in older codebases |
| **tox** | Test automation / environment manager | Multi-env test runs, dependency isolation, CI integration, plugin system | Very mature, widely adopted in CI, plugin ecosystem | Separate `tox.ini` config, can be verbose |
| **nox** | Like tox but config is Python code | Session-based test runs, parametrize, reuse venvs, conda support | Full Python flexibility, easy to debug sessions | Requires writing Python (pro or con), no declarative config |
| **PDM** | Package + project manager | Dependency resolution, lock files, scripts, env management, publish | PEP 582 support, lock files, scripts | Different philosophy (centralised tool), smaller community |
| **uv** | Fast package installer + env manager (Rust) | Install packages, create venvs, resolve dependencies, run scripts | Extremely fast, drop-in pip/venv replacement | Newer tool, still evolving rapidly |
| **Poetry** | Dependency manager + build tool | Dependency resolution, lock files, env management, build, publish | Lock files, dependency resolution, publish built in | Own config format (`[tool.poetry]`), doesn't follow PEP 621 fully |
| **Pipenv** | pip + virtualenv wrapper | Pipfile/Pipfile.lock, auto-create venvs, `.env` loading | Lock files, `.env` support | Slow dependency resolution, less active development |

#### Task Runners (run commands/scripts)

| Tool | Description | Capabilities | Pros | Cons |
|------|-------------|-------------|------|------|
| **Hatch scripts** | Scripts defined in `pyproject.toml` | Run commands, chain scripts, pass args, env-aware | Zero extra tools, integrated with Hatch envs | Only available through Hatch |
| **Make** | Classic build automation (Makefile) | Targets, dependencies, variables, shell commands, parallel builds | Universal, available everywhere, well understood | Not Python-native, Windows requires extra setup, tab-sensitive syntax |
| **just** | Modern command runner (Justfile) | Recipes, arguments, variables, dotenv loading, cross-platform | Simple syntax, cross-platform, no tab issues | Extra binary to install, not Python-specific |
| **Task (go-task)** | Task runner using `Taskfile.yml` | Tasks, dependencies, variables, watch mode, cross-platform | YAML-based, cross-platform, dependency graphs | Extra binary, Go ecosystem tool |
| **invoke** | Python-based task runner | Tasks as Python functions, namespaces, auto-parsing args | Pure Python, good for complex logic | Another dependency, less popular now |
| **nox** | Also works as a task runner | Session-based commands, parametrize, venv per session | Python-based, session isolation | Heavier than a simple task runner |
| **tox** | Also works as a task runner | Env-isolated command runs, dependency pinning | Mature, env isolation | Verbose for simple tasks |

#### CLI Frameworks (building user-facing CLIs)

| Tool | Description | Capabilities | Pros | Cons |
|------|-------------|-------------|------|------|
| **argparse** | Standard library CLI parser | Positional/optional args, subcommands, type conversion, help generation | No dependencies, always available | Verbose, manual help formatting |
| **click** | Decorator-based CLI framework | Commands, groups, options, prompts, file handling, colour output, plugins | Clean API, composable commands, excellent docs | Extra dependency |
| **typer** | Click-based, uses type hints for CLI args | Auto CLI from type hints, auto-completion, rich help | Minimal boilerplate, auto-generates help | Depends on click, newer |
| **rich-click** | Click + Rich for beautiful help output | Rich-formatted help, panels, syntax highlighting, tables | Pretty terminal output, drop-in for click | Extra dependency on top of click |
| **fire** | Auto-generates CLI from any Python object | Auto CLI from functions/classes/objects, no decorators needed | Zero boilerplate | Less control over help text and validation |

#### Linting & Formatting

| Tool | Description | Capabilities | Pros | Cons |
|------|-------------|-------------|------|------|
| **Ruff** | Linter + formatter (Rust) | 800+ lint rules, auto-fix, import sorting, formatting, pyupgrade | Blazing fast, replaces flake8+isort+black+pyupgrade+more | Newer, not 100% rule parity with all tools |
| **flake8** | Linter | Style checks, error detection, plugin system (200+ plugins) | Mature, huge plugin ecosystem | Slower, Python-based, being superseded by Ruff |
| **Black** | Opinionated formatter | Deterministic formatting, magic trailing comma, string normalisation | Zero config, consistent | No flexibility, being superseded by Ruff |
| **isort** | Import sorter | Sort imports, configurable sections, profiles (black-compatible) | Focused, configurable | Separate tool, Ruff handles this now |
| **autopep8** | PEP 8 formatter | Fix PEP 8 violations, conservative by default | Conservative formatting | Less opinionated than Black, less popular |

#### Type Checkers

| Tool | Description | Capabilities | Pros | Cons |
|------|-------------|-------------|------|------|
| **mypy** | The original Python type checker | Strict mode, incremental checks, stubs, plugins, daemon mode | Most mature, wide adoption, plugin ecosystem | Slower, can be strict to configure |
| **Pyright** | Type checker (powers VS Code Pylance) | Full type inference, watch mode, multi-root workspaces, strict mode | Fast, excellent IDE integration | Node.js dependency, different strictness defaults |
| **pytype** | Google's type checker | Type inference without annotations, cross-function analysis | Infers types even without annotations | Less widely used outside Google |

#### Dependency & Security Tools

| Tool | Install | Capabilities | Pros | Cons |
|------|---------|-------------|------|------|
| **pip-tools** | `pip install pip-tools` | `pip-compile` pins deps to a lock file, `pip-sync` installs exactly those pins | Reproducible builds, minimal lock file, works with pip | Extra step in workflow, no auto-update |
| **pip-audit** | `pip install pip-audit` | Scan installed packages against known vulnerability databases (OSV, PyPI) | Fast, integrates with CI, supports requirements.txt and pyproject.toml | Only checks known CVEs, not code-level issues |
| **pipdeptree** | `pip install pipdeptree` | Visualise dependency tree, detect conflicts, show reverse deps | Great for debugging dependency issues, simple output | Read-only — doesn't fix problems |

#### Debugging & Developer Experience Tools

| Tool | Install | Capabilities | Pros | Cons |
|------|---------|-------------|------|------|
| **rich** | `pip install rich` | Pretty tables, tracebacks, progress bars, syntax highlighting, logging, markdown rendering | Beautiful console output, drop-in traceback handler | Extra dependency, large package |
| **icecream** | `pip install icecream` | `ic(variable)` — prints variable name + value + file/line, auto-formats | Much better than `print()` debugging, zero-config | Debug-only — must remove before committing |
| **ipython** | `pip install ipython` | Enhanced REPL with tab completion, syntax highlighting, magic commands, `%timeit`, `%debug` | Far better than default Python shell, auto-reload modules | Heavier dependency, not for production |
| **devtools** | `pip install devtools` | `debug(variable)` — pretty-prints with type info, file/line, colour output | Clean debug output, type-aware formatting | Less known than icecream, similar purpose |

#### Commit Convention & Versioning Tools

| Tool | Install | Capabilities | Pros | Cons |
|------|---------|-------------|------|------|
| **commitizen** | `pip install commitizen` | Interactive commit prompts enforcing Conventional Commits, auto-bump version, auto-generate changelog, pre-commit hook, CI validation | All-in-one: commit format + version bump + changelog, configurable via `pyproject.toml`, supports custom commit schemas | Python dependency, learning curve for custom rules |
| **commitlint** | `npm install @commitlint/cli` | Lint commit messages against Conventional Commits (or custom) rules, integrates with husky | Huge ecosystem, very configurable rules | Node.js dependency, doesn't bump versions or generate changelogs |
| **semantic-release** | `pip install python-semantic-release` | Auto-determine next version from commits, generate changelog, create Git tags, publish to PyPI | Fully automated release pipeline, CI-friendly | Opinionated workflow, less control over individual steps |
| **towncrier** | `pip install towncrier` | Fragment-based changelog generation — each PR adds a news fragment file, assembled at release | Avoids merge conflicts in CHANGELOG, per-PR granularity | Extra workflow step (create fragment file per change), not commit-based |
| **standard-version** | `npm install standard-version` | Bump version, generate changelog from Conventional Commits, create Git tag | Simple, focused on versioning + changelog | Node.js dependency, archived/maintenance-only |
| **bump2version** | `pip install bump2version` | Find-and-replace version strings across files, create Git tag | Simple, language-agnostic, config file driven | No commit message parsing, no changelog generation, maintenance mode |

#### Commit Message Prefixes (Conventional Commits)

| Prefix | Meaning | When to use | Version bump | Example |
|--------|---------|-------------|--------------|---------|
| `feat:` | New feature | Adding new user-facing functionality | Minor | `feat: add user login endpoint` |
| `fix:` | Bug fix | Fixing a defect or incorrect behavior | Patch | `fix: correct null check in parser` |
| `docs:` | Documentation | Changes to documentation only | None | `docs: update API usage guide` |
| `style:` | Code style | Formatting, whitespace — no logic change | None | `style: fix indentation in models` |
| `refactor:` | Refactoring | Restructuring code without changing behavior | None | `refactor: extract validation into helper` |
| `perf:` | Performance | Improving performance without changing behavior | Patch | `perf: cache database query results` |
| `test:` | Tests | Adding or updating tests only | None | `test: add unit tests for auth module` |
| `build:` | Build system | Changes to build config or dependencies | None | `build: upgrade hatchling to 1.25` |
| `ci:` | CI/CD | Changes to CI/CD configuration or scripts | None | `ci: add mypy check to PR workflow` |
| `chore:` | Maintenance | Routine tasks, tooling, no production code change | None | `chore: update .gitignore` |
| `revert:` | Revert | Reverting a previous commit | Varies | `revert: undo feat: add login endpoint` |
| `feat!:` / `fix!:` | Breaking change | Append `!` after any type for incompatible API changes | Major | `feat!: remove deprecated login endpoint` |

> **Tip:** Use a `BREAKING CHANGE:` footer in the commit body for longer breaking change explanations.

#### Branch Prefixes

| Branch prefix | Meaning | When to use | Typical merge expectation | Example |
|---------------|---------|-------------|---------------------------|---------|
| `wip/` | Work in progress | Incomplete work, not ready for review | Draft PR or no PR yet | `wip/user-auth-flow` |
| `spike/` | Technical spike | Time-boxed research or proof of concept | May not merge — results documented | `spike/graphql-feasibility` |
| `explore/` | Exploration | Experimenting with an idea or library | May not merge — learning exercise | `explore/htmx-integration` |
| `chore/` | Maintenance | Routine tasks, config, tooling changes | Merge after review | `chore/update-gitignore` |
| `feat/` | Feature | New user-facing functionality | Merge after review + tests pass | `feat/user-login` |
| `fix/` | Bug fix | Fixing a defect or incorrect behavior | Merge after review + tests pass | `fix/null-pointer-in-parser` |
| `docs/` | Documentation | Changes to documentation only | Merge after review | `docs/update-readme` |
| `refactor/` | Refactoring | Restructuring code without changing behavior | Merge after review + tests pass | `refactor/extract-auth-service` |
| `test/` | Tests | Adding or updating tests only | Merge after review | `test/add-auth-unit-tests` |
| `ci/` | CI/CD | Changes to CI/CD configuration | Merge after review | `ci/add-mypy-workflow` |
| `build/` | Build system | Build config, packaging, dependencies | Merge after review | `build/upgrade-hatchling` |
| `perf/` | Performance | Performance improvements | Merge after review + benchmarks | `perf/cache-db-queries` |
| `style/` | Code style | Formatting, whitespace — no logic change | Merge after review | `style/fix-indentation` |
| `release/` | Release | Preparing a release (version bump, changelog) | Merge to main, tag, deploy | `release/v1.2.0` |
| `hotfix/` | Hotfix | Urgent production fix | Fast-track merge + deploy | `hotfix/fix-login-crash` |
| `deps/` | Dependencies | Dependency updates (manual or grouped) | Merge after CI passes | `deps/bump-requests-2.32` |
| `sec/` | Security | Security-related fix or hardening | Merge after review (may be private) | `sec/patch-ssrf-vulnerability` |

#### What this project uses

| Category | Tool | Why |
|----------|------|-----|
| Build backend | Hatchling | Auto-discovers src/ layout, minimal config |
| Project manager | Hatch | Envs, scripts, test matrices — one `pyproject.toml` |
| Task runner | Hatch scripts | No extra tools needed |
| CLI framework | argparse | No dependencies for a simple boilerplate |
| Linter + formatter | Ruff | Fast, replaces multiple tools |
| Type checker | mypy | Most mature, strict mode |
| Testing | pytest | De facto standard |

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

## Quality Gates

A **quality gate** is a checkpoint that code must pass before moving forward (e.g., merging to main, deploying to production).

### Common Quality Gates in CI

| Gate | What It Checks | Tool |
|------|----------------|------|
| **Tests pass** | Code works as expected | pytest |
| **Linting passes** | Code style, bugs | Ruff |
| **Type checking passes** | Type correctness | Mypy/Pyright |
| **Coverage threshold** | Enough tests exist | pytest-cov |
| **Security scan** | No vulnerabilities | Bandit, pip-audit |
| **Spell check** | No typos | codespell |

> **codespell: report-only by default.** codespell does *not* auto-fix typos unless you pass `--write-changes` (or `-w`). Without that flag it reports the misspelling and a suggested fix, then exits non-zero — which blocks your commit. You have two options:
>
> 1. **Auto-fix:** Add `-w` to the hook args in `.pre-commit-config.yaml`:
>    ```yaml
>    - id: codespell
>      args: [-w, --skip, ".git,.venv,dist,build,..."]
>    ```
>    codespell will rewrite the file in-place. The commit still fails (the file changed), but re-running `git add` + `git commit` picks up the fix.
>
> 2. **Manual fix:** Read the output, fix the typo yourself, then re-commit. This is safer when codespell's suggestion is wrong (it happens with domain-specific terms).
>
> **Tip:** If codespell flags a word that's correct (e.g., a variable name or technical term), add it to an ignore list: `args: [-L, "word1,word2", --skip, "..."]` or set `[tool.codespell]` in `pyproject.toml` with `ignore-words-list = "word1,word2"`.

### Enforcing Quality Gates

1. **GitHub Branch Protection** — Require status checks to pass before merge
2. **CI Workflow** — Each job is a gate; if one fails, PR can't merge
3. **Pre-commit Hooks** — Catch issues before they even reach CI

### Soft vs Hard Gates

- **Hard gate** — Must pass (blocks merge/deploy)
- **Soft gate** — Informational only (warns but doesn't block)

Example: When adopting type checking, start with a soft gate (`continue-on-error: true`) while adding type hints gradually.

### Why Quality Gates Matter

- Catch bugs early (cheaper to fix)
- Maintain code consistency
- Build confidence in deployments
- Document quality expectations

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

## Pre-commit Hooks

Pre-commit hooks run checks *before* code is committed, catching issues locally before they reach CI.

### Setup

```bash
pip install pre-commit
pre-commit install
```

### Configuration (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff          # Linting
        args: [--fix]
      - id: ruff-format   # Formatting

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.1
    hooks:
      - id: mypy
        additional_dependencies: []

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Key Commands

| Command | Purpose |
|---------|---------|
| `pre-commit install` | Enable hooks for this repo |
| `pre-commit run --all-files` | Run on all files (not just staged) |
| `pre-commit autoupdate` | Update hook versions |
| `git commit --no-verify` | Skip hooks (emergency only!) |

### Why Pre-commit > Manual Checks

- **Automatic** — Can't forget to run it
- **Fast feedback** — Fix before pushing
- **Consistent** — Same checks for everyone
- **CI friendly** — Run same hooks in CI as backup

### Authoring Custom Git Hooks

Beyond using existing hooks, you can author your own and publish them for others to use. Custom hooks live in a Git repository with a `.pre-commit-hooks.yaml` file at the root that declares the available hooks.

#### How It Works

1. Create a new Git repository for your hook(s).
2. Write the script or tool that performs the check.
3. Add a `.pre-commit-hooks.yaml` file describing the hook(s).
4. Tag a release — consumers pin to this tag via `rev` in their `.pre-commit-config.yaml`.

#### `.pre-commit-hooks.yaml` Fields

The `.pre-commit-hooks.yaml` file is a list of hook definitions. Each entry supports these fields:

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier for the hook (used in consumers' `hooks:` list) |
| `name` | Yes | Human-readable name shown during execution |
| `entry` | Yes | The executable to run (script path, command, or console_script) |
| `language` | Yes | How to install/run the hook (`python`, `node`, `system`, `script`, `docker`, etc.) |
| `files` | No | Regex pattern for filenames to pass to the hook (default: `''` — all files) |
| `exclude` | No | Regex pattern for filenames to exclude |
| `types` | No | File types to filter on (e.g., `[python]`, `[yaml]`) — uses `identify` library types |
| `types_or` | No | Like `types` but matches if *any* type matches (OR logic instead of AND) |
| `exclude_types` | No | File types to exclude |
| `always_run` | No | If `true`, run even when no matching files are staged (default: `false`) |
| `pass_filenames` | No | If `true`, staged filenames are passed as arguments (default: `true`) |
| `require_serial` | No | If `true`, disable parallel execution for this hook (default: `false`) |
| `args` | No | Default arguments passed to `entry` (consumers can override via `args` in their config) |
| `description` | No | Short description of what the hook does |
| `minimum_pre_commit_version` | No | Minimum pre-commit version required (e.g., `'3.0.0'`) |
| `stages` | No | Which git hook stages to run in (e.g., `[pre-commit]`, `[pre-push]`, `[commit-msg]`) |
| `verbose` | No | If `true`, force hook output to be printed even on success (default: `false`) |
| `additional_dependencies` | No | Extra packages to install alongside the hook |
| `language_version` | No | Version of the language runtime to use (e.g., `python3.11`) |

#### Minimal Example

A simple hook that checks for `TODO` comments:

```yaml
# .pre-commit-hooks.yaml
- id: no-todos
  name: Check for TODO comments
  entry: grep -rn TODO
  language: system
  types: [python]
  pass_filenames: true
```

#### Python Script Hook Example

For hooks written in Python, structure the repo as an installable package:

```
my-hooks/
├── .pre-commit-hooks.yaml
├── pyproject.toml
└── my_hooks/
    └── check_something.py
```

```yaml
# .pre-commit-hooks.yaml
- id: check-something
  name: Check something custom
  entry: check-something       # console_scripts entry point
  language: python
  types: [python]
```

The `language: python` setting tells pre-commit to create an isolated virtualenv and `pip install` the hook repository, so any `console_scripts` defined in `pyproject.toml` become available as the `entry`.

#### Hook Stages

Git supports multiple hook points. Pre-commit can target different stages:

| Stage | Git Hook | When It Runs |
|-------|----------|--------------|
| `pre-commit` | `pre-commit` | Before commit is created (default) |
| `pre-merge-commit` | `pre-merge-commit` | Before merge commit is created |
| `pre-push` | `pre-push` | Before push to remote |
| `commit-msg` | `commit-msg` | After commit message is entered (can validate or modify it) |
| `post-checkout` | `post-checkout` | After `git checkout` or `git switch` |
| `post-commit` | `post-commit` | After commit is created |
| `post-merge` | `post-merge` | After a merge completes |
| `post-rewrite` | `post-rewrite` | After `git rebase` or `git commit --amend` |
| `prepare-commit-msg` | `prepare-commit-msg` | Before the commit message editor opens |
| `manual` | — | Only runs via `pre-commit run --hook-stage manual` |

To install hooks for non-default stages: `pre-commit install --hook-type commit-msg`

#### Common Hooks by Stage

> **Note:** The repos listed below are popular, widely-used choices — not an exhaustive list. Many alternative hooks exist for each stage. Browse [pre-commit.com/hooks](https://pre-commit.com/hooks.html) for a searchable directory.

**`pre-commit`** — Fast checks that run on every commit (the default stage):

| Hook | Repo | What It Does |
|------|------|--------------|
| `trailing-whitespace` | pre-commit/pre-commit-hooks | Strip trailing whitespace |
| `end-of-file-fixer` | pre-commit/pre-commit-hooks | Ensure files end with a newline |
| `check-yaml` | pre-commit/pre-commit-hooks | Validate YAML syntax |
| `check-toml` | pre-commit/pre-commit-hooks | Validate TOML syntax |
| `check-json` | pre-commit/pre-commit-hooks | Validate JSON syntax |
| `check-ast` | pre-commit/pre-commit-hooks | Validate Python syntax |
| `check-added-large-files` | pre-commit/pre-commit-hooks | Block oversized files |
| `check-merge-conflict` | pre-commit/pre-commit-hooks | Detect conflict markers (`<<<<<<<`) |
| `debug-statements` | pre-commit/pre-commit-hooks | Catch leftover `breakpoint()` / debugger imports |
| `detect-private-key` | pre-commit/pre-commit-hooks | Block private key files |
| `mixed-line-ending` | pre-commit/pre-commit-hooks | Normalize line endings |
| `ruff` | astral-sh/ruff-pre-commit | Lint Python (replaces flake8, isort, pyupgrade) |
| `ruff-format` | astral-sh/ruff-pre-commit | Format Python (replaces black) |
| `mypy` | pre-commit/mirrors-mypy | Type check Python |
| `bandit` | PyCQA/bandit | Security linting for Python |
| `codespell` | codespell-project/codespell | Catch common typos in code and docs |
| `validate-pyproject` | abravalheri/validate-pyproject | Validate pyproject.toml schema |
| `actionlint` | rhysd/actionlint | Lint GitHub Actions workflows |
| `check-github-workflows` | python-jsonschema/check-jsonschema | Validate workflow YAML against schema |

**`commit-msg`** — Validate or modify the commit message after the user writes it:

| Hook | Repo | What It Does |
|------|------|--------------|
| `conventional-pre-commit` | compilerla/conventional-pre-commit | Enforce Conventional Commits format |
| `commitizen` | commitizen-tools/commitizen | Validate commit message against commitizen rules |
| `commitlint` | alessandrojcm/commitlint-pre-commit-hook | Lint commit messages (Node-based) |
| `gitlint` | jorisroovers/gitlint | Configurable commit message linter |

**`pre-push`** — Slower checks that run before pushing to remote:

| Hook | Repo | What It Does |
|------|------|--------------|
| `pytest` (local) | local | Run full test suite |
| `gitleaks` | gitleaks/gitleaks | Secret detection across git history |
| `trufflehog` | trufflesecurity/trufflehog | Deep secret scanning |
| `mypy` | pre-commit/mirrors-mypy | Type check (if too slow for pre-commit) |
| `bandit` | PyCQA/bandit | Security scan (if too slow for pre-commit) |

**`prepare-commit-msg`** — Modify the commit message before the editor opens:

| Hook | Repo | What It Does |
|------|------|--------------|
| `commitizen` (cz) | commitizen-tools/commitizen | Interactive commit message prompts |
| Custom template hook | local | Pre-fill commit message from a template |

**`post-checkout` / `post-merge`** — Run setup tasks after branch changes:

| Hook | Repo | What It Does |
|------|------|--------------|
| Auto `pip install` | local | Re-install deps after switching branches |
| Auto `npm install` | local | Re-install Node deps |
| DB migration check | local | Warn if unapplied migrations exist |

**`manual`** — Opt-in only, run explicitly with `pre-commit run <id> --hook-stage manual`:

| Hook | Repo | What It Does |
|------|------|--------------|
| `typos` | crate-ci/typos | Rust-based spellchecker (stricter than codespell) |
| `markdownlint-cli2` | DavidAnson/markdownlint-cli2 | Markdown linting (Node-based) |
| `hadolint-docker` | hadolint/hadolint | Dockerfile/Containerfile linter |
| `gitleaks` | gitleaks/gitleaks | Secret detection (when not on pre-push) |

#### References

- [Creating new hooks — pre-commit docs](https://pre-commit.com/#creating-new-hooks) — Official guide to authoring hooks
- [`.pre-commit-hooks.yaml` specification](https://pre-commit.com/#pre-commit-hooks-yaml) — Full field reference for hook definitions
- [Supported languages](https://pre-commit.com/#supported-languages) — All `language` values and how each is installed/executed
- [Supported hook stages](https://pre-commit.com/#confining-hooks-to-run-at-certain-stages) — Details on `stages` field and hook stage configuration
- [Git documentation: githooks](https://git-scm.com/docs/githooks) — Underlying Git hooks that pre-commit wraps
- [identify library — file type tags](https://github.com/pre-commit/identify) — Reference for `types` / `types_or` values

---

## GitHub Actions Workflows

### Anatomy of a Workflow

```yaml
name: Tests                        # Display name

on:                                # Triggers
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:                       # Least-privilege access
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@...  # Pinned SHA
      - uses: actions/setup-python@...
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest
```

### Common Workflow Patterns

| Workflow | Triggers | Purpose |
|----------|----------|---------|
| `test.yml` | push, PR | Run tests |
| `lint.yml` | push, PR | Ruff, mypy |
| `release.yml` | tag push | Publish to PyPI |
| `security.yml` | schedule, PR | Dependency audits |

### Matrix Testing

Test across multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
    os: [ubuntu-latest, windows-latest]
```

### Caching Dependencies

Speed up workflows by caching pip:

```yaml
- uses: actions/setup-python@...
  with:
    python-version: "3.11"
    cache: "pip"
```

### Useful Actions

| Action | Purpose |
|--------|---------|
| `actions/checkout` | Clone repo |
| `actions/setup-python` | Install Python |
| `actions/cache` | Cache dependencies |
| `codecov/codecov-action` | Upload coverage |
| `pypa/gh-action-pypi-publish` | Publish to PyPI |

---

## Branch Protection

Branch protection prevents direct pushes to important branches and enforces quality gates.

### Setting Up (GitHub)

**Settings → Branches → Add rule**

### Recommended Settings for `main`

| Setting | Purpose |
|---------|---------|
| ✅ Require PR before merging | No direct pushes |
| ✅ Require status checks | CI must pass |
| ✅ Require branches up to date | Must merge main first |
| ✅ Require conversation resolution | All comments addressed |
| ⬜ Require approvals | Set to 1+ for teams |
| ⬜ Restrict who can push | Limit to admins |

### Required Status Checks

Add these as required checks:
- `test` — Tests pass
- `lint` — Linting passes
- `type-check` — Types are correct

### Bypassing (Emergency)

Admins can bypass, but it's logged. Use sparingly!

---

## Security Scanning

### Tools Overview

| Tool | What It Does | When to Run |
|------|--------------|-------------|
| **pip-audit** | Checks deps for CVEs | CI, pre-release |
| **Bandit** | Finds security bugs in code | CI, pre-commit |
| **Safety** | Dependency vulnerabilities | CI |
| **Trivy** | Container scanning | CI (Docker builds) |
| **Dependabot** | Auto-creates upgrade PRs | Scheduled |

### What Is SARIF?

**SARIF** (Static Analysis Results Interchange Format) is a standardized JSON format for the output of static analysis tools. It's an [OASIS standard](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) designed so that different tools (linters, security scanners, type checkers) can all produce results in the same shape.

**Why it matters:**
- **GitHub Security tab** — When a CI workflow uploads a `.sarif` file via `github/codeql-action/upload-sarif`, the findings appear as **Code scanning alerts** in the repository's Security tab. This gives a unified view of vulnerabilities across tools.
- **Tool-agnostic** — Whether results come from Trivy, Grype, Bandit, CodeQL, or Scorecard, SARIF normalises them into one format.
- **IDE integration** — VS Code extensions (e.g., SARIF Viewer) can display SARIF results inline, showing issues right where the code is.

**Structure:** A SARIF file contains `runs`, each with a `tool` descriptor and an array of `results`. Each result has a `ruleId`, `message`, `level` (error/warning/note), and `locations` pointing to specific files and line numbers.

**In this project:** The `scorecard.yml`, `container-scan.yml`, and `nightly-security.yml` workflows all produce SARIF output and upload it to GitHub's Security tab.

### pip-audit in CI

```yaml
- name: Security audit
  run: |
    pip install pip-audit
    pip-audit
```

### Bandit in CI

```yaml
- name: Security scan
  run: |
    pip install bandit
    bandit -r src/ -ll
```

### Dependabot Configuration (`.github/dependabot.yml`)

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      dev-dependencies:
        patterns:
          - "pytest*"
          - "ruff"
          - "mypy"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Automation Strategy

### The Three Lines of Defense

1. **Pre-commit hooks** — Catch issues locally, instant feedback
2. **CI workflows** — Catch anything that slips through, authoritative
3. **Branch protection** — Enforce that CI passes before merge

### What to Run Where

| Check | Pre-commit | CI | Why |
|-------|------------|-----|-----|
| Formatting | ✅ | ✅ | Fast, catches everything |
| Linting | ✅ | ✅ | Fast, catches everything |
| Type checking | ⚠️ Optional | ✅ | Can be slow locally |
| Tests | ❌ | ✅ | Too slow for commit hook |
| Security scan | ❌ | ✅ | Needs network, slow |
| Coverage | ❌ | ✅ | Needs full test run |

### Progressive Adoption

1. **Start with CI** — Get workflows running first
2. **Add branch protection** — Enforce CI passes
3. **Add pre-commit** — Speed up feedback loop
4. **Tune thresholds** — Gradually increase strictness

---

## GitHub README Priority Order

GitHub has a hidden priority order for which README displays on the repo landing page:

1. **`.github/README.md`** — Highest priority (surprising!)
2. **`README.md`** — Root (what you'd expect)
3. **`docs/README.md`** — Lowest priority

**The gotcha:** If you put a `README.md` in `.github/` to document your workflows and templates, it **silently replaces** your root `README.md` on the repository page. Visitors see your internal `.github/` docs instead of your project README — with no warning.

This is unique to `.github/`. Every other directory's `README.md` only renders when browsing *that* directory. But `.github/README.md` is treated as a profile-level README, similar to how `<username>/<username>/README.md` shows on your GitHub profile.

**Fix:** Don't put a `README.md` in `.github/`. Document that directory's contents elsewhere (e.g., `docs/repo-layout.md`).

See: [ADR 015](../adr/015-no-github-directory-readme.md)

---

## Things I Keep Forgetting

1. **Import name ≠ package name** — `simple-python-boilerplate` (hyphen) installs, but you `import simple_python_boilerplate` (underscore)

2. **`__init__.py` is still needed** — Even in Python 3, include it for tooling compatibility

3. **Editable install is required** — With `src/` layout, you must install to import

4. **pytest needs the package installed** — Or it won't find your modules

---

## Research: Other Template Repos

Notes and conventions gathered from popular Python boilerplate/template repositories on GitHub.

---

### Hypermodern Python (cjolowicz)

**Repo:** [cjolowicz/hypermodern-python](https://github.com/cjolowicz/hypermodern-python)

A reference for cutting-edge Python tooling. Accompanied by a detailed blog series.

| Convention | Details |
|------------|---------|
| **Build tool** | Poetry (now Hatch is also popular) |
| **Task runner** | Nox (multi-Python testing) |
| **Type checker** | Mypy with strict mode |
| **Docs** | Sphinx + Read the Docs |
| **Pre-commit** | Extensive hooks |
| **CLI** | Click |

**Key Takeaways:**
- Uses Nox for consistent test environments across Python versions
- Separates "sessions" (lint, tests, docs, safety) in `noxfile.py`
- Coverage enforced with pytest-cov
- Sphinx autodoc for API docs from docstrings
- GitHub Actions with matrix for Python 3.9–3.12

---

### Cookiecutter PyPackage (audreyfeldroy)

**Repo:** [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage)

One of the most popular Python package templates. Uses Cookiecutter for project generation.

| Convention | Details |
|------------|---------|
| **Layout** | `src/` layout (optional, flat by default) |
| **Testing** | pytest + tox |
| **Docs** | Sphinx |
| **CI** | Travis CI (older), GitHub Actions (forks) |
| **Versioning** | bumpversion |

**Key Takeaways:**
- Generates CONTRIBUTING.rst, HISTORY.rst, AUTHORS.rst
- Includes Makefile with common targets (`make test`, `make docs`)
- Supports multiple open source licenses via prompts
- tox.ini for multi-version testing
- Bump2version for version management

---

### Python Project Template (rochacbruno)

**Repo:** [rochacbruno/python-project-template](https://github.com/rochacbruno/python-project-template)

Modern template with Copier (alternative to Cookiecutter).

| Convention | Details |
|------------|---------|
| **Build tool** | Poetry or setuptools |
| **Linting** | Ruff (replaced flake8, isort, black) |
| **Type checker** | Mypy |
| **Task runner** | Make |
| **Docs** | MkDocs (Material theme) |

**Key Takeaways:**
- Uses Copier for template updates (can pull in template changes later)
- Containerfile for OCI/Docker builds
- GitHub Actions with reusable workflows
- Conventional commits enforced
- MkDocs Material for modern-looking docs

---

### FastAPI Project Structure (tiangolo)

**Repo:** [tiangolo/full-stack-fastapi-template](https://github.com/tiangolo/full-stack-fastapi-template)

While not a general template, FastAPI projects set conventions for modern Python.

| Convention | Details |
|------------|---------|
| **Layout** | `app/` package (not `src/`) |
| **Async** | Native async/await |
| **Config** | Pydantic Settings |
| **Database** | SQLAlchemy + Alembic |
| **Testing** | pytest + httpx |

**Key Takeaways:**
- Pydantic for settings/config management with `.env` files
- Alembic for database migrations (instead of raw SQL)
- Docker Compose for local development
- Separation: `app/core/`, `app/api/`, `app/models/`, `app/crud/`
- Pre-commit with Ruff

---

### Scikit-learn Contrib Template

**Repo:** [scikit-learn-contrib/project-template](https://github.com/scikit-learn-contrib/project-template)

Template for scikit-learn compatible packages.

| Convention | Details |
|------------|---------|
| **Layout** | Flat (package at root) |
| **Testing** | pytest-cov |
| **Docs** | Sphinx + sphinx-gallery |
| **CI** | GitHub Actions + CircleCI |

**Key Takeaways:**
- Strict scikit-learn API compatibility (estimator checks)
- Example gallery generated from scripts
- Extensive docstring format (NumPy style)
- Conda + pip dual support

---

### PyScaffold

**Repo:** [pyscaffold/pyscaffold](https://github.com/pyscaffold/pyscaffold)

CLI tool that generates Python projects. Very opinionated.

| Convention | Details |
|------------|---------|
| **Layout** | `src/` layout (enforced) |
| **Config** | `pyproject.toml` + `setup.cfg` hybrid |
| **Versioning** | setuptools-scm (git tags) |
| **Docs** | Sphinx |
| **Extensions** | Plugin system |

**Key Takeaways:**
- Version derived from git tags (no manual version bumping)
- setuptools-scm for automatic versioning
- Extensions for Django, pre-commit, CI templates
- Creates `CHANGELOG.rst` (reStructuredText)
- Authors file auto-generated from git log

---

### Packaging Conventions Comparison

| Aspect | This Template | Hypermodern | Cookiecutter | PyScaffold |
|--------|---------------|-------------|--------------|------------|
| **Layout** | `src/` | `src/` | flat (default) | `src/` |
| **Config** | pyproject.toml only | pyproject.toml | setup.py/cfg | hybrid |
| **Linting** | Ruff | flake8 + plugins | flake8 | flake8 |
| **Formatting** | Ruff | Black | Black | Black |
| **Types** | Mypy | Mypy strict | optional | optional |
| **Task runner** | Make/scripts | Nox | Make + tox | tox |
| **Docs** | Markdown | Sphinx | Sphinx | Sphinx |
| **Versioning** | manual | bump2version | bumpversion | setuptools-scm |

---

### Common Patterns Observed

**Project Structure:**
- `src/` layout gaining popularity (isolation benefits)
- `tests/` at root level (not inside `src/`)
- `docs/` for documentation source files
- Flat configs in root (pyproject.toml, tox.ini, etc.)

**Configuration:**
- pyproject.toml as single source (PEP 518/621)
- Tool configs in `[tool.X]` sections
- `.env` + `.env.example` for secrets

**CI/CD:**
- GitHub Actions dominant (Travis CI declining)
- Matrix testing (Python 3.10, 3.11, 3.12, etc.)
- Separate workflows per concern
- Dependabot or Renovate for dependency updates

**Documentation:**
- Sphinx still dominant for libraries
- MkDocs + Material gaining traction
- README.md as landing page
- CHANGELOG.md with Keep a Changelog format

**Testing:**
- pytest universal
- pytest-cov for coverage
- tox or nox for multi-version
- conftest.py for shared fixtures

**Developer Experience:**
- Pre-commit hooks standard
- Makefile or justfile for common tasks
- Editorconfig for cross-editor consistency
- .vscode/ or .idea/ for IDE settings

---

### Ideas Worth Considering

From researching these templates, potential additions:

| Idea | Benefit | Complexity |
|------|---------|------------|
| **setuptools-scm** | No manual version bumping | Low |
| **Nox** | Better than tox, Python-based | Medium |
| **MkDocs** | Simpler than Sphinx, Markdown-native | Low |
| **Copier** | Template updates after adoption | Medium |
| **justfile** | Modern Makefile alternative | Low |
| **CITATION.cff** | Academic citation support | Low |
| **.editorconfig** | Cross-editor consistency | Low |

---

### Other Template Repos (To Review)

Additional template and boilerplate repositories worth studying:

---

### PyPA Sample Project

**Repo:** [pypa/sampleproject](https://github.com/pypa/sampleproject)

The official sample project from the Python Packaging Authority (PyPA). Exists as a companion to the [PyPUG Tutorial on Packaging and Distributing Projects](https://packaging.python.org/tutorials/packaging-projects/). Intentionally minimal — focuses purely on packaging, not project development practices.

| Convention | Details |
|------------|---------|
| **Layout** | `src/` layout (`src/sample/`) |
| **Config** | `pyproject.toml` only |
| **Testing** | Nox |
| **CI** | GitHub Actions |
| **Docs** | None (README only) |
| **Versioning** | Manual in `pyproject.toml` |

**Key Takeaways:**
- The most authoritative reference for pyproject.toml packaging metadata
- Deliberately does not cover linting, formatting, type checking, or CI beyond testing
- `src/` layout used as the recommended default
- 5.3k stars — extremely well-known as the canonical packaging example
- Good reference for pyproject.toml fields (classifiers, URLs, optional-dependencies, entry-points)
- No template engine — just a plain project to clone and adapt

---

### Kotlin Android Template (cortinico)

**Repo:** [cortinico/kotlin-android-template](https://github.com/cortinico/kotlin-android-template)

A 100% Kotlin template for Android projects with static analysis and CI baked in. Useful as a cross-language comparison for how non-Python ecosystems approach project templates.

| Convention | Details |
|------------|---------|
| **Language** | Kotlin (100%) |
| **Build tool** | Gradle (Kotlin DSL) |
| **Static analysis** | Detekt + ktlint |
| **CI** | GitHub Actions (pre-merge, publish-snapshot, publish-release) |
| **Dependency management** | Gradle Version Catalog (`libs.versions.toml`) + Renovate |
| **Publishing** | Maven Central via Nexus |

**Key Takeaways:**
- Multi-module structure: `app/`, `library-android/`, `library-kotlin/`, `library-compose/`
- Shared build logic lives in `buildSrc/` as precompiled script plugins
- Renovate (not Dependabot) for automated dependency updates with auto-merge
- Static analysis runs as part of CI, not just pre-commit
- Jetpack Compose module included as a ready-to-use example
- No template engine — uses GitHub "Use this template" with manual find-and-replace
- `.idea/` directory committed for consistent IDE settings (Android Studio / IntelliJ)
- 1.9k stars; maintained by a Meta/React Native engineer

---

### Electron Boilerplate (sindresorhus)

**Repo:** [sindresorhus/electron-boilerplate](https://github.com/sindresorhus/electron-boilerplate) (**Archived** May 2024)

A minimal, opinionated Electron starter from sindresorhus. Now archived but still a good reference for how a "less is more" boilerplate can work.

| Convention | Details |
|------------|---------|
| **Language** | JavaScript (84%), CSS, HTML |
| **Build tool** | electron-builder |
| **CI** | GitHub Actions (cross-platform builds) |
| **Config** | electron-store |
| **Error handling** | electron-unhandled |
| **Editor** | `.editorconfig` |

**Key Takeaways:**
- Extremely minimal — only the files you actually need (no over-engineering)
- electron-builder configured for cross-platform builds (macOS, Linux, Windows)
- Silent auto-updates built in
- System-native app menu out of the box
- Context menu via `electron-context-menu`
- README acts as a template itself — "remove everything above here" pattern
- Example of a successful boilerplate that is a working app, not a meta-template
- 1.6k stars; archived because the author moved on from Electron

---

### Josee9988's Project Template

**Repo:** [Josee9988/project-template](https://github.com/Josee9988/project-template)

A language-agnostic GitHub template focused on community health files, issue templates, labels, and repository automation. Not about code structure — about the GitHub repo wrapper around a project.

| Convention | Details |
|------------|---------|
| **Language** | Language-agnostic (Shell for setup script) |
| **Setup** | `SETUP_TEMPLATE.sh` script auto-detects and replaces placeholders |
| **Issue templates** | 8 templates (bug, failing test, docs, feature, enhancement, security, question, blank) |
| **Labels** | 20+ labels auto-created via `settings.yml` bot |
| **Community files** | CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, CODEOWNERS |
| **Bots** | issue-label-bot, probot-settings, welcome-bot, todo-bot |

**Key Takeaways:**
- Strongest emphasis on community health files of any template reviewed
- Shell script for initial personalisation (replaces placeholders in all files)
- Uses GitHub Probot ecosystem heavily for automation
- CHANGELOG follows Keep a Changelog format
- Pull request template auto-closes linked issues via keywords
- No CI workflows for code — purely a "repo wrapper" template
- 934 stars; last updated 4 years ago (not actively maintained)

---

### inovintell Python Template

**Repo:** [inovintell/py-template](https://github.com/inovintell/py-template)

A Python template that uses **Cookiecutter** for project generation. Focused on CI/CD automation with semantic release and comprehensive GitHub Actions pipelines.

| Convention | Details |
|------------|---------|
| **Layout** | `src/{{cookiecutter.repository}}/` (Cookiecutter-templated) |
| **Build tool** | Poetry |
| **Linting** | Ruff |
| **Pre-commit** | Yes (with commitlint for conventional commits) |
| **CI** | GitHub Actions (extensive pipeline) |
| **Docs** | MkDocs |
| **Dependency updates** | Renovate |
| **Versioning** | Semantic release (automated) |

**Key Takeaways:**
- Uses Cookiecutter — source files have `{{cookiecutter.repository}}` placeholders throughout
- This means the template repo itself is not directly runnable or testable
- Heavy Renovate usage — bot commits dominate the commit history
- Conventional commits enforced via commitlint
- `.editorconfig` and `.yamllint.yml` included for cross-editor and YAML consistency
- Poetry for dependency management (not pip/setuptools)
- Example of the trade-off ADR-014 discusses: powerful automation but harder to read/contribute to
- 92 stars; actively maintained (Renovate keeps dependencies current)

---

### Awesome Repo Template (MarketingPipeline)

**Repo:** [MarketingPipeline/Awesome-Repo-Template](https://github.com/MarketingPipeline/Awesome-Repo-Template)

A feature-rich, language-agnostic GitHub template with heavy automation via GitHub Actions workflows that run at template setup time.

| Convention | Details |
|------------|---------|
| **Language** | Language-agnostic (HTML landing page) |
| **Setup** | GitHub Actions workflow auto-replaces links, emails, and metadata |
| **Community files** | CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, CODEOWNERS, CHANGE_LOG, TO_DO |
| **Issue templates** | Bug report and feature request (YAML-based forms) |
| **Automation** | Image compression, TOC generation, stargazer metrics SVG, SEO index.html |
| **Bots** | issue-label-bot, probot-settings, welcome-bot |

**Key Takeaways:**
- Unique approach: uses a GitHub Actions workflow to auto-configure the repo after creation
- Generates a markdown-styled `index.html` with SEO metadata
- Auto-generates a table of contents in the README
- Stargazer metrics SVG generated automatically
- Image optimisation workflow compresses all repo images
- More "GitHub infrastructure" than "code template" — no language-specific tooling
- Similar to Josee9988's template but with more workflow-based automation
- 201 stars; last updated 4 years ago

---

## Source Code File Workflow

A clean separation of concerns for the `src/` package structure.

### The Pattern

```
main.py   → starts the program (entry points, thin wrappers)
cli.py    → defines CLI contract (argument parsing, commands)
engine.py → defines behavior (core logic, interface-agnostic)
api.py    → defines callable interface (HTTP/REST, optional)
```

### File Responsibilities

| File | Purpose | Contains |
|------|---------|----------|
| `main.py` | Entry points | Thin wrappers that call cli/engine |
| `cli.py` | CLI contract | Argument parser, command definitions |
| `engine.py` | Behavior | Pure logic, no I/O, easily testable |
| `api.py` | API interface | HTTP routes, request/response handling |

### Data Flow

```
User runs command
       ↓
main.py (entry point)
       ↓
cli.py (parse args, dispatch)
       ↓
engine.py (do the work)
       ↓
Return result to cli.py
       ↓
Format output (cli.py or main.py)
       ↓
User sees result
```

### Why This Pattern?

1. **Testability** — `engine.py` has no CLI/HTTP dependencies, easy to unit test
2. **Flexibility** — Same engine can power CLI, API, GUI, etc.
3. **Clarity** — Each file has one job
4. **Maintainability** — Changes to CLI don't affect core logic

### Example

```python
# engine.py — pure logic
def process_data(data: str) -> str:
    return f"Processed: {data}"

# cli.py — CLI contract
def run(args):
    from engine import process_data
    result = process_data(args.input)
    print(result)
    return 0

# main.py — entry point
def main():
    from cli import parse_args, run
    sys.exit(run(parse_args()))
```

### Anti-patterns to Avoid

- ❌ Business logic in `main.py`
- ❌ Argument parsing in `engine.py`
- ❌ HTTP-specific code in `engine.py`
- ❌ `print()` statements in `engine.py` (return data instead)

---

| File             | Primary role                  | What it contains                                                            | What it must **not** contain                                     | Who calls it                        | When to use it                                     | Common mistakes                                          |
|------------------|-------------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------|-------------------------------------|----------------------------------------------------|----------------------------------------------------------|
| **`engine.py`**  | Source of truth (core logic)  | Pure functions/classes that implement real behavior                         | CLI parsing, printing, shell commands, repo-specific assumptions | `api.py`, tests, other Python code  | Always when behavior is non-trivial or reusable    | Mixing I/O or argument parsing into core logic           |
| **`api.py`**     | Stable internal interface     | Thin wrappers that expose intentional operations (e.g. `run_lint`, `build`) | Implementation details, argument parsing                         | `cli.py`, `main.py`, other tools    | When you want a clean boundary and refactor safety | Making it a duplicate of `engine.py` with no added value |
| **`cli.py`**     | Command-line interface        | Argument parsing, subcommands, help text                                    | Business logic, complex workflows                                | End users, developers, Just, CI     | When providing an installable CLI                  | Putting real logic directly in CLI handlers              |
| **`main.py`**    | Entry point / bootstrap       | Calls into `api.py` or `engine.py` to start execution                       | Logic, configuration rules                                       | Python runtime (`python main.py`)   | Optional; useful for quick execution or demos      | Letting it grow into the main implementation file        |

### Key Rule

> Logic flows downward; control flows upward.

- Logic lives in `engine.py`
- Interfaces adapt it (`api.py`, `cli.py`)
- Entrypoints trigger it (`main.py`)

### Decision Rules (read top → bottom)

- If someone outside this repo needs to run it → installable CLI
- If only contributors need it → task runner (Just)
- If it expresses real behavior → core logic
- If it just wires things together → orchestration

### Canonical Decision Table

| Question                                                        | Yes → Do this                                       | No → Do this |
|-----------------------------------------------------------------|-----------------------------------------------------|--------------|
| Does this define real behavior (rules, algorithms, decisions)?  | Put it in **core logic** (`engine.py` / `core/`)    | Continue     |
| Should this behavior be callable by other code or tools?        | Expose via **installable CLI** (and/or API)         | Continue     |
| Is this meant to be run outside this repo?                      | **Installable CLI command**                         | Continue     |
| Is this only for contributors working on this repo?             | **Just task**                                       | Continue     |
| Is this repo-specific glue (order of steps, flags, paths)?      | **Just task or script**                             | Continue     |
| Is this a one-off or disposable automation?                     | **Script**                                          | Re-evaluate  |

### What Each Bucket Is Responsible For

| Tool / Layer       | Purpose                  | Source of truth? | Versioned? | Audience     |
|--------------------|--------------------------|------------------|------------|-------------|
| Core logic         | Implements behavior      | ✅ Yes            | With code  | Everyone     |
| Installable CLI    | Defines public commands  | ✅ Yes            | Yes        | Users / devs |
| Just (task runner) | Orchestrates commands    | ❌ No             | With repo  | Contributors |
| Scripts            | One-off helpers          | ❌ No             | Optional   | Maintainers  |
| CI workflows       | Automation               | ❌ No             | With repo  | CI only      |

### Concrete Examples (grounding the rules)

| Action                       | Correct place                    | Why                          |
|------------------------------|----------------------------------|------------------------------|
| Lint Python files            | Installable CLI (`mytool lint`)  | Reusable, meaningful behavior |
| Run lint + format + tests    | Just (`just check`)              | Repo workflow                |
| Build and publish release    | CLI (`mytool release`)           | Stable, versioned behavior   |
| Clean `.pytest_cache`        | Just or script                   | Repo-specific cleanup        |
| Bootstrap venv               | Just                             | Developer convenience        |
| Parse config file            | Core logic                       | Behavior, not orchestration  |
| Call multiple tools in order | Just                             | Pure glue                    |

### Anti-patterns (what not to do)

| Smell                                  | Why it's wrong                   |
|----------------------------------------|----------------------------------|
| Logic lives in `justfile`              | Not testable or reusable         |
| CI runs `just something`               | CI now depends on dev tooling    |
| CLI calls shell pipelines              | Logic trapped in strings         |
| Scripts are the only interface         | No stable API                    |
| Just command documented as "the way"   | Just became the API              |

### One-sentence Rule (worth memorizing)

> Installable CLIs define behavior.
> Just coordinates behavior.
> Scripts are temporary.

### Why This Matters for Your Template

You are not just writing code—you are teaching architecture.

**If you teach:**

- "put logic in core"
- "keep runners dumb"

**Then users:**

- Can refactor safely
- Can add new interfaces later
- Avoid brittle repos

---

## Common Python Cache & Artifact Directories

| Path               | Created by          | Purpose                                            | Safe to delete? | Commit to git? |
|--------------------|---------------------|----------------------------------------------------|-----------------|----------------|
| `__pycache__/`     | Python interpreter  | Stores compiled `.pyc` bytecode for faster imports | ✅ Yes           | ❌ Never        |
| `.pytest_cache/`   | pytest              | Remembers test state (last failed, node IDs)       | ✅ Yes           | ❌ Never        |
| `.mypy_cache/`     | mypy                | Type-checking cache                                | ✅ Yes           | ❌ Never        |
| `.ruff_cache/`     | ruff                | Linting cache                                      | ✅ Yes           | ❌ Never        |
| `.coverage`        | coverage.py         | Coverage data file                                 | ✅ Yes           | ❌ Never        |
| `htmlcov/`         | coverage.py         | HTML coverage report                               | ✅ Yes           | ❌ Never        |
| `.tox/`            | tox                 | Virtualenvs + test environments                    | ✅ Yes           | ❌ Never        |
| `.nox/`            | nox                 | Virtualenvs + sessions                             | ✅ Yes           | ❌ Never        |
| `.venv/`           | venv / uv / poetry  | Local virtual environment                          | ✅ Yes           | ❌ Never        |
| `dist/`            | build tools         | Built distributions (wheel/sdist)                  | ✅ Yes           | ❌ Never        |
| `build/`           | build tools         | Temporary build artifacts                          | ✅ Yes           | ❌ Never        |

### Why Python Creates So Many Caches

Python tooling is modular:

- Each tool optimizes independently
- Each tool owns its own cache
- No central "build system" cleans everything automatically

This is normal and healthy.

### Do Other Programming Languages Have the Same Thing?

Yes — absolutely. Every serious ecosystem does.

**Comparison across ecosystems:**

| Language    | Examples of cache / artifact dirs                              |
|-------------|----------------------------------------------------------------|
| Python      | `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.venv/`     |
| JavaScript  | `node_modules/`, `.next/`, `.turbo/`, `.parcel-cache/`         |
| Rust        | `target/`                                                      |
| Java        | `target/`, `.gradle/`                                          |
| Go          | `pkg/`, `bin/`, module cache                                   |
| C/C++       | `build/`, `*.o`, `*.a`, `*.out`                                |
| .NET        | `bin/`, `obj/`                                                 |

The names differ; the idea is identical.

### Why These Should Never Be Committed

Cache directories are:

- Machine-specific
- Non-deterministic
- Frequently invalidated
- Huge source of merge conflicts

A repo that commits caches is a broken repo.

### Where Cleanup Belongs (Architecture Tie-In)

Cleaning caches:

- Is not real behavior
- Is not business logic
- Is repo hygiene

**Correct places:**

- `just clean`
- `scripts/clean.py`
- CI steps

**Incorrect places:**

- Core logic
- Installable CLI
- Application code

### Example `.gitignore` Entries

```gitignore
# Python
__pycache__/
*.py[cod]

# Virtual environments
.venv/
env/

# Test / lint / type-check caches
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Build artifacts
build/
dist/
*.egg-info/
```

### One Rule to Remember

> If deleting it breaks nothing permanently, it's not source code.

---

## What is `*.egg-info`?

`*.egg-info/` is Python packaging metadata generated by setuptools (often via pip) when a project is installed, especially in editable (`pip install -e .`) mode.

It is not source code. It is installation metadata.

### What Lives Inside `*.egg-info/`

Typical contents:

```
my_package.egg-info/
├── PKG-INFO        # Name, version, license, metadata
├── SOURCES.txt     # Files included in the package
├── requires.txt    # Dependencies
├── entry_points.txt# Console scripts / CLI entry points
├── top_level.txt   # Top-level import names
└── dependency_links.txt
```

This data answers questions like:

- "What version is installed?"
- "What console scripts should exist?"
- "What are the dependencies?"

### Why It Appears in Your Repo

Common causes:

- You ran `pip install -e .`
- A tool installed your package locally
- A test or dev workflow installed the project

Editable installs must write metadata somewhere, and `*.egg-info` is how setuptools does it.

### Should `*.egg-info` Be Committed?

**No. Never.**

Reasons:

- Machine-specific paths
- Installation-state dependent
- Regenerated at will
- Causes merge noise and confusion

Add to `.gitignore`:

```gitignore
*.egg-info/
```

### Related Packaging Artifacts (same category)

These are not caches, but build/install artifacts.

| Artifact              | Created by  | Purpose                     | Commit? |
|-----------------------|-------------|-----------------------------|:-------:|
| `*.egg-info/`         | setuptools  | Installed package metadata  | ❌       |
| `*.dist-info/`        | pip         | Wheel installation metadata | ❌       |
| `dist/`               | build tools | Built wheels / sdists       | ❌       |
| `build/`              | build tools | Temporary build output      | ❌       |
| `pip-wheel-metadata/` | pip         | Intermediate wheel metadata | ❌       |

**Rule:** If it only exists after install or build, it does not belong in git.

### `egg-info` vs `dist-info` (important distinction)

**`*.egg-info`**

- Legacy / setuptools-era format
- Common in editable installs

**`*.dist-info`**

- Modern standard (PEP 376)
- Created when installing wheels

Both serve the same role: describe what’s installed, not what you wrote.

### Beyond Python: Other Non-Cache Artifacts You May See

These exist in many ecosystems and are not caches, but tooling state.

| Ecosystem   | Examples                              |
|-------------|---------------------------------------|
| Python      | `*.egg-info/`, `*.dist-info/`         |
| JavaScript  | `package-lock.json`, `pnpm-lock.yaml` |
| Rust        | `Cargo.lock`                          |
| Java        | `pom.xml`, `.classpath`               |
| .NET        | `.csproj`, `.deps.json`               |

**Key difference:**

- Lockfiles → usually committed
- Install/build metadata → never committed

### Mental Model (use this)

> Caches speed things up.
> Metadata describes installed artifacts.
> Neither is source code.

If deleting it only requires reinstalling or rebuilding → it does not belong in git.

### Where This Fits in Your Architecture Rules

`*.egg-info` is not:

- Logic
- CLI
- Just
- Scripts

It is a tool byproduct, managed by the packaging system.

### Bottom-Line Rules

- Source code → commit
- Configuration → commit
- Lockfiles → usually commit
- Caches → never commit
- Build artifacts → never commit
- Install metadata (`*.egg-info`, `*.dist-info`) → never commit

### Quick Reference: When to Use What

| Scenario              | Installable CLI | Just | Script |
|-----------------------|-----------------|------|--------|
| Reusable logic        | ✅               | ❌    | ❌      |
| Distributed tool      | ✅               | ❌    | ❌      |
| Repo glue             | ❌               | ✅    | ⚠️     |
| One-off automation    | ❌               | ⚠️   | ✅      |
| User-facing command   | ✅               | ❌    | ❌      |
| Developer convenience | ⚠️              | ✅    | ⚠️     |

---

## What is `pyproject.toml`?

`pyproject.toml` is a single configuration file (written in [TOML](https://toml.io/)) that defines everything about a Python project: metadata, dependencies, build instructions, and tool settings.

Before `pyproject.toml`, Python projects needed multiple config files (`setup.py`, `setup.cfg`, `tox.ini`, `.flake8`, `mypy.ini`, etc.). Now most of that lives in one place.

### The Standards Behind It

| PEP | What It Defines | Year |
|-----|----------------|------|
| [PEP 518](https://peps.python.org/pep-0518/) | `[build-system]` table — how to build the project | 2016 |
| [PEP 621](https://peps.python.org/pep-0621/) | `[project]` table — project metadata (name, version, deps, etc.) | 2020 |
| [PEP 517](https://peps.python.org/pep-0517/) | Build backend interface (how pip talks to build tools) | 2017 |
| [PEP 660](https://peps.python.org/pep-0660/) | Editable installs via build backends | 2021 |

These PEPs made `pyproject.toml` the **standard** way to configure Python projects. Any PEP 621-compliant tool (pip, Hatch, setuptools, Flit, PDM, Dependabot, etc.) can read the `[project]` table.

### Structure Overview

A `pyproject.toml` has three major sections:

```
┌─────────────────────────────────────────────────┐
│  [build-system]            ← PEP 518            │
│  How to build this project                      │
├─────────────────────────────────────────────────┤
│  [project]                 ← PEP 621            │
│  What this project IS (metadata, deps, etc.)    │
│  ├─ [project.scripts]                           │
│  ├─ [project.urls]                              │
│  └─ [project.optional-dependencies]             │
├─────────────────────────────────────────────────┤
│  [tool.*]                  ← Tool-specific      │
│  Configuration for individual tools             │
│  ├─ [tool.hatch.*]                              │
│  ├─ [tool.pytest.*]                             │
│  ├─ [tool.ruff.*]                               │
│  ├─ [tool.mypy]                                 │
│  └─ [tool.coverage.*]                           │
└─────────────────────────────────────────────────┘
```

### Section 1: `[build-system]` (PEP 518)

Tells pip and other installers **how** to build your project.

```toml
[build-system]
requires = ["hatchling"]           # What to download to build
build-backend = "hatchling.build"  # The Python object that does the build
```

| Field | Purpose | Example Values |
|-------|---------|----------------|
| `requires` | Build-time dependencies (downloaded by pip) | `["hatchling"]`, `["setuptools>=68"]`, `["flit_core>=3.9"]` |
| `build-backend` | Python callable that builds sdist/wheel | `"hatchling.build"`, `"setuptools.build_meta"`, `"flit_core.api"` |

**Key insight:** You don't need Hatch installed to `pip install .` your project. pip downloads `hatchling` automatically based on `requires`. Hatch (the CLI) is a separate, optional developer tool.

### Section 2: `[project]` (PEP 621)

Describes **what** your project is. This is standardized metadata — every tool reads the same fields.

```toml
[project]
name = "my-project"                  # Package name (PyPI / pip install)
version = "0.1.0"                    # Current version
description = "One-line summary"     # Short description
readme = "README.md"                 # Long description file
requires-python = ">=3.11"           # Minimum Python version
license = {text = "Apache-2.0"}      # SPDX license identifier
authors = [{name = "You"}]           # Author(s)
```

#### Subfields of `[project]`

| Field | Type | Purpose |
|-------|------|---------|
| `name` | string | Package name on PyPI, used with `pip install <name>` |
| `version` | string | SemVer version (or `dynamic = ["version"]` for auto) |
| `description` | string | One-line summary shown on PyPI |
| `readme` | string/table | Path to long description (usually README.md) |
| `requires-python` | string | Minimum Python version specifier |
| `license` | table | SPDX license identifier or file path |
| `authors` | array of tables | Name and/or email of author(s) |
| `keywords` | array of strings | PyPI search keywords |
| `classifiers` | array of strings | [PyPI classifiers](https://pypi.org/classifiers/) (maturity, license, Python versions) |
| `dependencies` | array of strings | **Runtime** dependencies (installed by `pip install .`) |

#### `[project.scripts]` — CLI Entry Points

Maps command names to Python functions. pip creates executables for these automatically.

```toml
[project.scripts]
my-tool = "my_package.main:main"     # Runs main() from my_package/main.py
my-tool-doctor = "my_package.main:doctor"
```

After `pip install .`, typing `my-tool` in a terminal calls `my_package.main:main()`.

#### `[project.urls]` — Project Links

Shown on the PyPI sidebar.

```toml
[project.urls]
Homepage = "https://github.com/user/project"
Repository = "https://github.com/user/project"
Documentation = "https://project.readthedocs.io"
Changelog = "https://github.com/user/project/blob/main/CHANGELOG.md"
"Bug Tracker" = "https://github.com/user/project/issues"
```

#### `[project.optional-dependencies]` — Extra Dependency Groups

Dependencies that are only installed when explicitly requested. This is PEP 621, so **any tool** (pip, Hatch, Dependabot, tox, nox) understands it.

```toml
[project.optional-dependencies]
test = ["pytest", "pytest-cov"]
dev = ["my-project[test]", "ruff", "mypy"]   # Can reference other groups!
docs = ["mkdocs>=1.6", "mkdocs-material>=9.4"]
```

Install with: `pip install -e ".[dev]"` or `pip install -e ".[test,docs]"`.

**Why this matters for Hatch:** Hatch environments reference these groups via `features = ["dev"]` instead of duplicating the dependency list. One source of truth, two consumers.

**Why this matters for Dependabot:** Dependabot reads `[project.optional-dependencies]` and auto-creates PRs to update version specifiers (e.g., `"ruff"` → `"ruff>=0.9.1"`).

### Section 3: `[tool.*]` — Tool-Specific Config

Each tool gets its own namespace under `[tool]`. This is not standardized — each tool defines its own schema.

```toml
[tool.hatch.envs.default]           # Hatch environment config
[tool.pytest.ini_options]           # pytest settings
[tool.ruff]                         # Ruff linter/formatter
[tool.mypy]                         # mypy type checker
[tool.coverage.run]                 # coverage.py
[tool.bandit]                       # Bandit security linter
```

**Key point:** `[tool.*]` sections are ignored by tools that don't own them. Ruff doesn't care about `[tool.mypy]`, and mypy doesn't care about `[tool.ruff]`. They coexist peacefully.

#### Hatch-Specific Tool Config

Hatch uses `[tool.hatch.*]` for environments, scripts, build config, and versioning:

```toml
# Environments — isolated virtualenvs with specific dependency groups
[tool.hatch.envs.default]
features = ["dev"]                     # Install [project.optional-dependencies].dev

[tool.hatch.envs.default.scripts]
test = "pytest {args}"                 # `hatch run test`
lint = "ruff check {args: src/}"       # `hatch run lint`

# Test matrix — test across Python versions
[tool.hatch.envs.test]
features = ["test"]

[[tool.hatch.envs.test.matrix]]        # Note: double brackets = array of tables
python = ["3.11", "3.12", "3.13"]

# Build config
[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
```

### TOML Syntax Quick Reference

TOML has a few syntax patterns that can trip you up:

| Syntax | Meaning | Example |
|--------|---------|---------|
| `[section]` | Table (like a dict) | `[project]` |
| `[section.subsection]` | Nested table | `[tool.ruff.lint]` |
| `[[section]]` | Array of tables (list of dicts) | `[[tool.hatch.envs.test.matrix]]` |
| `key = "value"` | String | `name = "my-project"` |
| `key = ["a", "b"]` | Array | `dependencies = ["click"]` |
| `key = {a = "b"}` | Inline table | `license = {text = "MIT"}` |
| `key = [{a = "b"}]` | Array of inline tables | `authors = [{name = "You"}]` |

### How Tools Discover `pyproject.toml`

Most tools (pytest, ruff, mypy, etc.) walk up the directory tree from the current working directory until they find a `pyproject.toml` with their `[tool.X]` section. No need to pass `--config` flags.

### Putting It All Together

```toml
# ── How to build ──
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# ── What this project is ──
[project]
name = "my-project"
version = "0.1.0"
dependencies = ["requests"]

[project.optional-dependencies]
dev = ["ruff", "pytest"]

[project.scripts]
my-cli = "my_project.main:main"

# ── How tools behave ──
[tool.hatch.envs.default]
features = ["dev"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 88
```

One file. Everything in one place. Every tool knows where to look.

### Dependabot and `pyproject.toml`

Dependabot understands PEP 621 fully. It scans:

- `[project].dependencies` — runtime deps
- `[project.optional-dependencies].*` — all extras (dev, test, docs, etc.)

It creates PRs to update version specifiers when new releases are published.

**What Dependabot does NOT do:**

- It does **not** update version numbers inside TOML comments (e.g., `# v0.6.9` in a comment)
- It does **not** update versions in non-standard locations (Taskfile.yml, scripts, README examples)
- It only touches the actual dependency specifier strings

If you have comments documenting current versions (like `"ruff",  # v0.9.1`), those comments will become stale as Dependabot bumps the specifier. You need a separate script or manual process to keep comments current.

---

## Shells: sh, bash, zsh, and Others

Shells are command-line interpreters — programs that read your commands and execute them. They matter for git hooks, scripts, CI pipelines, and daily terminal use. Each shell is a superset or variant of the one before it.

### The Shell Family Tree

```
sh (Bourne Shell, 1979)
 └── bash (Bourne Again Shell, 1989)
      └── zsh (Z Shell, 1990)

csh (C Shell, 1978)         ← separate lineage
 └── tcsh
      └── fish (2005)       ← inspired by csh, but independent
```

### Shell Comparison

| Shell | Full Name | Default On | Best For | Key Trait |
|-------|-----------|-----------|----------|-----------|
| **sh** | Bourne Shell | POSIX systems, Docker `alpine` | Portable scripts, git hooks, CI | Minimal — works everywhere |
| **bash** | Bourne Again Shell | Most Linux distros, older macOS | General scripting, interactive use | Arrays, `[[ ]]`, `$()`, rich scripting |
| **zsh** | Z Shell | macOS (since Catalina), many devs | Interactive daily use | Plugins (Oh My Zsh), autocomplete, glob |
| **dash** | Debian Almquist Shell | Debian/Ubuntu (`/bin/sh` → dash) | System scripts | Extremely fast, strict POSIX |
| **fish** | Friendly Interactive Shell | — (opt-in) | Interactive use, beginners | Syntax highlighting, autosuggestions |
| **PowerShell** | PowerShell | Windows | Windows automation, .NET | Object pipeline (not text), cmdlets |

### sh — The Portable Baseline

`sh` (POSIX shell) is the lowest common denominator. If you write a script in `sh`, it will run on virtually any Unix-like system — Linux, macOS, BSD, Docker containers, CI runners.

```bash
#!/bin/sh
# This runs everywhere. No bashisms allowed.
echo "Hello from sh"
```

**Key limitations** (things sh does NOT have):
- No arrays (`arr=(a b c)` is bash)
- No `[[ ]]` (use `[ ]` instead)
- No `$(( ))` for arithmetic in all implementations
- No `{1..10}` brace expansion
- No `function` keyword (just `myfunc() { ... }`)

**Why this matters:** On Debian/Ubuntu, `/bin/sh` is actually `dash` (not bash), so scripts with `#!/bin/sh` that use bash features will silently break.

### bash — The Workhorse

Bash is the most widely used shell for scripting. It extends sh with arrays, better string manipulation, `[[ ]]` tests, process substitution, and more.

```bash
#!/bin/bash
# Bash-specific features
names=("alice" "bob" "charlie")      # arrays
for name in "${names[@]}"; do
    if [[ "$name" == a* ]]; then     # [[ ]] pattern matching
        echo "Found: $name"
    fi
done
```

**Bash vs sh — common "bashisms" that break in sh:**

| Feature | bash | sh (POSIX) |
|---------|------|-----------|
| Test syntax | `[[ -f file ]]` | `[ -f file ]` |
| Arrays | `arr=(a b c)` | Not available |
| String substitution | `${var//old/new}` | Not available |
| Process substitution | `<(command)` | Not available |
| Brace expansion | `{1..5}` | Not available |
| `source` command | `source file` | `. file` |
| Function keyword | `function foo()` | `foo()` |

### zsh — The Interactive Powerhouse

zsh is bash-compatible for most scripting but shines as an interactive shell with better tab completion, theming, spelling correction, and plugin ecosystems like **Oh My Zsh**.

```zsh
#!/bin/zsh
# zsh-specific features
typeset -A config                   # associative arrays (bash 4+ also has these)
config[host]=localhost
config[port]=8080
echo "Server: $config[host]:$config[port]"

# Glob qualifiers — zsh-only
print -l *.py(om)                   # list .py files sorted by modification time
```

**Why macOS switched to zsh:** Apple shipped bash 3.2 (2007) because bash 4+ is GPLv3, which conflicts with Apple's licensing. Rather than ship ancient bash, they switched the default to zsh (MIT-licensed) in macOS Catalina (2019).

### Which Shell for What?

| Use Case | Recommended Shell | Why |
|----------|------------------|-----|
| **Git hooks** | `#!/bin/sh` | Portability — hooks must work on every contributor's machine |
| **CI/CD scripts** | `#!/bin/sh` or `#!/bin/bash` | CI runners have bash, but sh is safer for Docker alpine |
| **Complex automation scripts** | `#!/bin/bash` | Need arrays, string ops, or conditionals |
| **Daily terminal use** | zsh or fish | Better autocomplete, history, plugins |
| **Makefiles / Taskfiles** | sh (implicit) | Make uses `/bin/sh` by default |
| **Docker `RUN` commands** | sh | Alpine images only have sh, not bash |
| **Windows scripts** | PowerShell | Native, object-based pipeline |

### Shells and Git Hooks

Git hooks are executable scripts in `.git/hooks/`. The shebang line (`#!/bin/sh`) determines which shell interprets them.

```bash
#!/bin/sh
# .git/hooks/pre-commit — runs before every commit
# Using sh for maximum portability

echo "Running pre-commit checks..."
python -m ruff check src/ || exit 1
```

**Why pre-commit (the framework) helps:** Instead of writing raw shell hook scripts, `pre-commit` manages hooks via `.pre-commit-config.yaml`. It handles shebang lines, virtual environments, and cross-platform compatibility — you never need to think about which shell the hook uses.

**Without pre-commit** (raw hooks):
- You write shell scripts directly in `.git/hooks/`
- You choose the shell (`#!/bin/sh`, `#!/bin/bash`, etc.)
- You handle portability yourself
- Hooks aren't versioned (`.git/hooks/` is not committed)

**With pre-commit** (framework):
- Hooks are defined in `.pre-commit-config.yaml` (versioned)
- The framework generates the actual hook scripts
- Each hook tool runs in its own isolated environment
- Shell portability is handled for you

### Common Gotcha: Shebang Lines

The shebang (`#!`) must be the **first line** of the script, with no leading whitespace or BOM:

```bash
#!/bin/sh          ← correct
#!/bin/bash        ← correct, but limits portability
#!/usr/bin/env bash  ← most portable way to invoke bash (finds it in $PATH)
```

`#!/usr/bin/env bash` is preferred over `#!/bin/bash` because bash isn't always at `/bin/bash` (e.g., on NixOS or some BSD systems). `env` searches `$PATH` to find it.

### Hook Scripts in Other Programming Languages

Git hooks don't have to be shell scripts. Any executable file with a valid shebang line works. This opens the door to Python, Node.js, Ruby, Perl, Rust, Go — whatever you have installed.

#### Language Examples for Hooks

**Python:**
```python
#!/usr/bin/env python3
"""pre-commit hook: check for TODO comments with no issue reference."""
import subprocess
import sys

result = subprocess.run(
    ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
    capture_output=True, text=True
)
staged_files = result.stdout.strip().splitlines()

for filepath in staged_files:
    with open(filepath) as f:
        for i, line in enumerate(f, 1):
            if "TODO" in line and "#" not in line.split("TODO")[1][:10]:
                print(f"{filepath}:{i}: TODO without issue reference")
                sys.exit(1)
```

**Node.js:**
```javascript
#!/usr/bin/env node
// pre-commit hook: validate JSON files
const fs = require('fs');
const { execSync } = require('child_process');

const staged = execSync('git diff --cached --name-only --diff-filter=ACM')
  .toString().trim().split('\n')
  .filter(f => f.endsWith('.json'));

let failed = false;
for (const file of staged) {
  try {
    JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    console.error(`Invalid JSON: ${file} — ${e.message}`);
    failed = true;
  }
}
process.exit(failed ? 1 : 0);
```

**Ruby:**
```ruby
#!/usr/bin/env ruby
# pre-commit hook: check for binding.pry left in code
staged = `git diff --cached --name-only --diff-filter=ACM`.split("\n")
staged.select { |f| f.end_with?('.rb') }.each do |file|
  File.readlines(file).each_with_index do |line, i|
    if line.include?('binding.pry')
      puts "#{file}:#{i + 1}: Remove binding.pry before committing"
      exit 1
    end
  end
end
```

**Perl:**
```perl
#!/usr/bin/env perl
# pre-commit hook: check for trailing whitespace
use strict;
my @files = `git diff --cached --name-only --diff-filter=ACM`;
chomp @files;
for my $file (@files) {
    open my $fh, '<', $file or next;
    while (<$fh>) {
        if (/\s+$/) {
            print "$file:$.: trailing whitespace\n";
            exit 1;
        }
    }
}
```

#### Compiled Languages as Hooks

Compiled languages (Rust, Go, C) can also be used — you compile the binary first, then point the hook at it. This is less common for one-off hooks but used by dedicated hook tools:

```bash
#!/bin/sh
# Hook that delegates to a compiled Go binary
exec .git/hooks/bin/my-hook "$@"
```

Notable tools written in compiled languages that serve as hook systems:
- **lefthook** (Go) — fast, parallel hook runner with YAML config
- **rusty-hook** (Rust) — lightweight hook runner for Node projects
- **overcommit** (Ruby) — full-featured hook manager

#### Shells vs Programming Languages for Hooks

| Factor | Shell (sh/bash) | Python | Node.js | Compiled (Go/Rust) |
|--------|----------------|--------|---------|-------------------|
| **Startup speed** | Instant (~5ms) | Slow (~50-100ms) | Slow (~100ms) | Instant (~5ms) |
| **Portability** | sh is everywhere | Needs Python installed | Needs Node installed | Binary runs anywhere |
| **String/text processing** | Awkward (sed, awk, grep) | Excellent | Good | Good |
| **Error handling** | Fragile (`set -e`, exit codes) | try/except, robust | try/catch, robust | Strong type system |
| **File system operations** | Basic (test, find, ls) | `pathlib`, `os` — powerful | `fs` module — decent | Full stdlib |
| **JSON/YAML parsing** | Needs `jq` or similar | Built-in `json` module | Built-in `JSON` | Serde (Rust), encoding/json |
| **Git integration** | Native (`git` commands) | Subprocess calls | Subprocess or libraries | Subprocess or `git2` |
| **Complexity ceiling** | Low (~50 lines max) | Unlimited | Unlimited | Unlimited |
| **Dependencies** | None | pip/venv | npm/node_modules | Compile step |
| **Debugging** | Painful (`set -x`) | Proper debugger (pdb) | Proper debugger | Proper debugger |
| **Windows support** | Needs Git Bash/WSL | Native | Native | Native |

#### When to Use What

| Scenario | Best Choice | Why |
|----------|------------|-----|
| Simple file checks (whitespace, merge markers) | **Shell (sh)** | 2-5 lines, no dependencies, instant |
| Check staged file contents or patterns | **Python** | Easy file I/O, regex, readable |
| Validate JSON/YAML/config files | **Python or Node** | Built-in parsers |
| Complex multi-step validation | **Python** | Best balance of power and readability |
| Enforce commit message format | **Shell or Python** | Shell for simple regex, Python for complex rules |
| Performance-critical (huge repos) | **Compiled (Go/Rust)** | Sub-millisecond execution |
| Team with mixed OS (Windows + Mac + Linux) | **Python or Node** | Cross-platform without shell quirks |
| You already use pre-commit framework | **Doesn't matter** | pre-commit abstracts the language away |

#### The Reality: pre-commit Framework Handles This

In practice, choosing a language for hooks is mostly academic if you use the `pre-commit` framework (which this project does). Each hook in `.pre-commit-config.yaml` runs its own tool in an isolated environment:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit  # Rust binary
    hooks:
      - id: ruff           # ← you don't care that Ruff is written in Rust
  - repo: https://github.com/pre-commit/mirrors-mypy     # Python tool
    hooks:
      - id: mypy           # ← you don't care that mypy is Python
  - repo: https://github.com/pre-commit/pre-commit-hooks # Python scripts
    hooks:
      - id: check-yaml     # ← you don't care about the implementation
```

The framework:
- Downloads and installs each hook's dependencies automatically
- Creates isolated environments (virtualenvs for Python, node_modules for Node, etc.)
- Handles shebang lines and shell compatibility
- Works identically on macOS, Linux, and Windows

**Bottom line:** The pre-commit framework lets you use the *best tool for the job* regardless of what language it's written in. You pick hooks by *what they check*, not *what language they use*.

### Quick Reference: Shell Config Files

| Shell | Login Shell | Interactive (non-login) | Notes |
|-------|------------|------------------------|-------|
| **bash** | `~/.bash_profile` or `~/.profile` | `~/.bashrc` | `.bash_profile` often sources `.bashrc` |
| **zsh** | `~/.zprofile` then `~/.zshrc` | `~/.zshrc` | Oh My Zsh configures this |
| **sh** | `~/.profile` | — | Minimal config |
| **fish** | `~/.config/fish/config.fish` | Same file | No login/non-login split |

---

## Resources

### Python Packaging

- [Python Packaging User Guide](https://packaging.python.org/)
- [Hynek's Testing & Packaging](https://hynek.me/articles/testing-packaging/)
- [Real Python: Python Packaging](https://realpython.com/pypi-publish-python-package/)
- [PyPA Sample Project](https://github.com/pypa/sampleproject)
- [PEP 621 – Project metadata in pyproject.toml](https://peps.python.org/pep-0621/)

### Testing & Quality

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Hypothesis (property-based testing)](https://hypothesis.readthedocs.io/)

### Linting & Formatting

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [pre-commit](https://pre-commit.com/)

### CI/CD & GitHub Actions

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)

### Project Templates & Best Practices

- [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
- [Scientific Python Library Development Guide](https://learn.scientific-python.org/development/)
- [The Hitchhiker's Guide to Python](https://docs.python-guide.org/)

### Security

- [pip-audit](https://github.com/pypa/pip-audit)
- [Bandit](https://bandit.readthedocs.io/)
- [OpenSSF Scorecard](https://securityscorecards.dev/)
