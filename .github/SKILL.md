---
description: >-
  Add new components to this project: ADRs, workflows, scripts, MkDocs hooks,
  pre-commit hooks. Each procedure includes the file creation step AND all
  required sync steps (index updates, regeneration, instruction file updates).
  Use this skill when asked to "add a new ADR", "add a new workflow", etc.
---

# Project Component Procedures

Multi-step recipes for adding new components to this repository. Each
procedure lists creation steps AND the sync/registration steps that keep
documentation and tooling up-to-date.

---

## Add a New ADR

1. Find the next sequential number by listing `docs/adr/`.
2. Copy `docs/adr/template.md` to `docs/adr/NNN-short-title.md`.
3. Fill in all sections: Status, Context, Decision, Alternatives, Consequences, Implementation, References.
4. Update `docs/adr/README.md` — add the new ADR to the index table.
5. If the ADR affects day-to-day work, add it to the "Key ADRs" table in `.github/copilot-instructions.md`.
6. If the decision touches architecture or tooling, update `docs/design/architecture.md` and/or `docs/design/tool-decisions.md`.

## Add a New Workflow

1. Create `.github/workflows/<name>.yml`.
2. Pin all third-party actions to full 40-character commit SHAs with a version comment: `uses: actions/checkout@<sha> # v4.2.0`.
3. Add repository guard pattern (`if: github.repository == ...`) unless the workflow is essential.
4. Update `docs/workflows.md` — add the workflow to the appropriate category table.
5. If the workflow is required for PRs, add its job display name to `REQUIRED_CHECKS` in `ci-gate.yml`.
6. Update `.github/workflows/.instructions.md` if this introduces a new convention.

## Add a New Script

1. Create `scripts/<name>.py` with shebang (`#!/usr/bin/env python3`), argparse CLI (`--help`, `--version`, optionally `--dry-run`), and `logging` for status messages.
2. Mark executable: `git add --chmod=+x scripts/<name>.py`.
3. Update `scripts/README.md` — add to the inventory table.
4. Re-run: `python scripts/generate_command_reference.py` to refresh `docs/reference/commands.md`.
5. If the script is useful as a Taskfile shortcut, add a task to `Taskfile.yml`.
6. For shared utilities (not CLIs), name as `scripts/_<name>.py` (underscore prefix).

## Add a New MkDocs Hook

1. Create `mkdocs-hooks/<name>.py` with the hook function (e.g., `on_files`, `on_page_markdown`).
2. Register in `mkdocs.yml` under `hooks:`.
3. Update `mkdocs-hooks/README.md` — add to the inventory.
4. Add tests in `tests/unit/test_<name>.py` if the hook has non-trivial logic.

## Add a New Pre-commit Hook

1. Add the hook definition to `.pre-commit-config.yaml` under the appropriate stage.
2. Update `docs/adr/008-pre-commit-hooks.md` — add to the hook inventory table and update the count.
3. Update the hook count in `.github/copilot-instructions.md` (Pre-commit Hooks table).

## Add a New Dependency

1. Add to the appropriate group in `pyproject.toml` `[project.optional-dependencies]`: `test`, `dev`, `docs`, or `extras`.
2. If the tool is a significant choice, update `docs/design/tool-decisions.md`.
3. Run `hatch env remove default` then re-enter with `hatch shell` to pick up changes.
