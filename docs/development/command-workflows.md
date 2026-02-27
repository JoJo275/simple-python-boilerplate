# Command Workflows

How commands flow through the tooling layers in this project.

---

## The Three Layers

This project has three ways to run developer commands, each building on the
one below:

```
┌─────────────────────────────────────────────┐
│  Layer 3: Task Runner (Taskfile.yml)        │  ← task test
│  Convenience shortcuts, no Hatch knowledge  │
├─────────────────────────────────────────────┤
│  Layer 2: Hatch (pyproject.toml envs)       │  ← hatch run test
│  Manages virtualenvs, installs deps         │
├─────────────────────────────────────────────┤
│  Layer 1: Python tools (pytest, ruff, mypy) │  ← pytest
│  The actual tools that do the work          │
└─────────────────────────────────────────────┘
```

Each layer is optional — you can work at whichever level you prefer.

---

## How a Command Flows

When you run `task test`, here's what happens:

```
task test
  → Taskfile.yml runs: hatch run test
    → Hatch activates the default env (creates it if needed)
    → Hatch runs the "test" script defined in pyproject.toml
      → Which executes: pytest {args}
```

The same pattern applies to every command:

| You type           | Taskfile runs          | Hatch script | Actual tool                         |
| ------------------ | ---------------------- | ------------ | ----------------------------------- |
| `task test`        | `hatch run test`       | `test`       | `pytest`                            |
| `task lint`        | `hatch run lint`       | `lint`       | `ruff check .`                      |
| `task lint:fix`    | `hatch run lint-fix`   | `lint-fix`   | `ruff check --fix .`                |
| `task fmt`         | `hatch run fmt`        | `fmt`        | `ruff format .`                     |
| `task typecheck`   | `hatch run typecheck`  | `typecheck`  | `mypy src/`                         |
| `task security`    | `hatch run security`   | `security`   | `bandit -r src/`                    |
| `task check`       | `hatch run check`      | `check`      | lint + fmt-check + typecheck + test |
| `task test:matrix` | `hatch run test:run`   | `test:run`   | pytest across Python 3.11–3.13      |
| `task docs:serve`  | `hatch run docs:serve` | `docs:serve` | `mkdocs serve`                      |
| `task docs:build`  | `hatch run docs:build` | `docs:build` | `mkdocs build --strict`             |

---

## Pick Your Layer

### Layer 1: Direct tools (no Hatch, no Task)

Use this if you manage your own virtualenv with `pip install -e ".[dev]"`.

```bash
pytest                          # run tests
ruff check .                    # lint
ruff format .                   # format
mypy src/                       # type check
bandit -r src/                  # security lint
mkdocs serve                    # serve docs
```

**Pros:** No extra tooling. Works in any venv.
**Cons:** You manage the venv, dependency installs, and Python versions yourself.

### Layer 2: Hatch

Use this if you want managed environments but don't want Task installed.

```bash
hatch shell                     # enter the dev environment
hatch run test                  # run tests (auto-creates env if needed)
hatch run lint                  # lint
hatch run fmt                   # format
hatch run typecheck             # type check
hatch run test:run              # test across Python 3.11–3.13
hatch run docs:serve            # serve docs (uses docs env)
hatch env show                  # show all environments
```

**Pros:** Automatic venv creation, dep syncing, multi-version matrix.
**Cons:** Requires Hatch installed (`pipx install hatch`).

### Layer 3: Task runner

Use this for the shortest commands. Requires both Hatch and [Task](https://taskfile.dev/).

```bash
task test                       # run tests
task lint                       # lint
task fmt                        # format
task typecheck                  # type check
task check                      # all quality gates
task test:matrix                # test across Python 3.11–3.13
task docs:serve                 # serve docs
task                            # list all available tasks
```

**Pros:** Shortest commands, discoverable via `task --list`.
**Cons:** Requires both Hatch and Task installed.

---

## Which Layer Should I Use?

| Situation                          | Recommended layer                             |
| ---------------------------------- | --------------------------------------------- |
| Quick contribution, minimal setup  | Layer 1 (pip + direct tools)                  |
| Regular development                | Layer 2 (Hatch) or Layer 3 (Task)             |
| CI/CD workflows                    | Layer 2 (Hatch) — Task is not installed in CI |
| Multi-version testing              | Layer 2 or 3 — Hatch manages the matrix       |
| First time, just want to run tests | Layer 3 if Task is installed, else Layer 2    |

---

## Where Commands Are Defined

| Layer             | Config file      | Section                             |
| ----------------- | ---------------- | ----------------------------------- |
| Hatch scripts     | `pyproject.toml` | `[tool.hatch.envs.default.scripts]` |
| Hatch test matrix | `pyproject.toml` | `[tool.hatch.envs.test]`            |
| Hatch docs env    | `pyproject.toml` | `[tool.hatch.envs.docs]`            |
| Task shortcuts    | `Taskfile.yml`   | `tasks:`                            |

To see all available commands:

```bash
task                            # list Task shortcuts
task --list-all                 # include internal tasks
hatch env show                  # show Hatch envs and their scripts
```

---

## See Also

- [developer-commands.md](developer-commands.md) — Complete command reference
- [dev-setup.md](dev-setup.md) — Environment setup instructions
- [ADR 016](../adr/016-hatchling-and-hatch.md) — Why Hatch
- [ADR 017](../adr/017-task-runner.md) — Why Taskfile
