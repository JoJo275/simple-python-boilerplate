# 🔴 Repository Sauron Report — simple-python-boilerplate

> *The all-seeing eye peers into every corner of your repository.*
>
> **Generated:** 2026-03-26 20:23:07 UTC
> **Version:** 2.0.0
> **Branch:** `wip/2026-03-26-scratch`

![files](https://img.shields.io/badge/files-320-blue)
![size](https://img.shields.io/badge/size-3.2%20MB-green)
![commits](https://img.shields.io/badge/commits-825-orange)
![contributors](https://img.shields.io/badge/contributors-5-purple)
![code files](https://img.shields.io/badge/code%20files-83-brightgreen)
![script files](https://img.shields.io/badge/script%20files-83-yellow)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Repository Structure](#-repository-structure)
- [File Types](#-file-types)
- [Languages](#-languages)
- [Code & Script Activity](#-code--script-activity)
- [Directory Sizes](#-directory-sizes)
- [Largest Files](#-largest-files)
- [File Access Statistics](#-file-access-statistics)
- [Git History](#-git-history)
- [Per-File Git Statistics](#-per-file-git-statistics)
- [Contributors](#-contributors)
- [Recommended Scripts](#-recommended-scripts)

---

## 📊 Overview

> [!NOTE]
> High-level repository metrics at a glance.

| Metric | Value |
|--------|-------|
| **Total files** | 320 |
| **Total directories** | 39 |
| **Total size** | 3.2 MB |
| **Avg file size** | 10.3 KB |
| **Code files** | 83 |
| **Script files** | 83 |
| **Avg directory size** | 79.8 KB (32 dirs) |
| **Total lines (text)** | 78,220 |
| **Total commits** | 825 |

---

## 🌳 Repository Structure

> [!TIP]
> Complete directory and file tree of the repository (excluding build artifacts and caches).

<details>
<summary><strong>Click to expand full repository tree</strong></summary>

```
simple-python-boilerplate/
├── db/
│   ├── migrations/
│   │   ├── 001_example_migration.sql
│   │   └── README.md
│   ├── queries/
│   │   ├── example_queries.sql
│   │   └── README.md
│   ├── seeds/
│   │   ├── 001_example_seed.sql
│   │   └── README.md
│   ├── README.md
│   └── schema.sql
├── docs/
│   ├── adr/
│   │   ├── archive/
│   │   │   └── README.md
│   │   ├── .instructions.md
│   │   ├── 001-src-layout.md
│   │   ├── 002-pyproject-toml.md
│   │   ├── 003-separate-workflow-files.md
│   │   ├── 004-pin-action-shas.md
│   │   ├── 005-ruff-for-linting-formatting.md
│   │   ├── 006-pytest-for-testing.md
│   │   ├── 007-mypy-for-type-checking.md
│   │   ├── 008-pre-commit-hooks.md
│   │   ├── 009-conventional-commits.md
│   │   ├── 010-dependabot-for-dependency-updates.md
│   │   ├── 011-repository-guard-pattern.md
│   │   ├── 012-multi-layer-security-scanning.md
│   │   ├── 013-sbom-bill-of-materials.md
│   │   ├── 014-no-template-engine.md
│   │   ├── 015-no-github-directory-readme.md
│   │   ├── 016-hatchling-and-hatch.md
│   │   ├── 017-task-runner.md
│   │   ├── 018-bandit-for-security-linting.md
│   │   ├── 019-containerfile.md
│   │   ├── 020-mkdocs-documentation-stack.md
│   │   ├── 021-automated-release-pipeline.md
│   │   ├── 022-rebase-merge-strategy.md
│   │   ├── 023-branch-protection-rules.md
│   │   ├── 024-ci-gate-pattern.md
│   │   ├── 025-container-strategy.md
│   │   ├── 026-no-pip-tools.md
│   │   ├── 027-database-strategy.md
│   │   ├── 028-git-branching-strategy.md
│   │   ├── 029-testing-strategy.md
│   │   ├── 030-label-management-as-code.md
│   │   ├── 031-script-conventions.md
│   │   ├── 032-dependency-grouping-strategy.md
│   │   ├── 033-prettier-for-markdown-formatting.md
│   │   ├── 034-documentation-organization-strategy.md
│   │   ├── 035-copilot-instructions-as-context.md
│   │   ├── 036-diagnostic-tooling-strategy.md
│   │   ├── 037-git-configuration-as-code.md
│   │   ├── 038-vscode-workspace-configuration-strategy.md
│   │   ├── 039-developer-onboarding-automation.md
│   │   ├── 040-v1-release-readiness.md
│   │   ├── README.md
│   │   └── template.md
│   ├── design/
│   │   ├── architecture.md
│   │   ├── ci-cd-design.md
│   │   ├── database.md
│   │   ├── README.md
│   │   └── tool-decisions.md
│   ├── development/
│   │   ├── branch-workflows.md
│   │   ├── command-workflows.md
│   │   ├── dev-setup.md
│   │   ├── developer-commands.md
│   │   ├── development.md
│   │   ├── pull-requests.md
│   │   └── README.md
│   ├── guide/
│   │   ├── getting-started.md
│   │   ├── README.md
│   │   └── troubleshooting.md
│   ├── notes/
│   │   ├── archive.md
│   │   ├── archive.md.bak
│   │   ├── learning.md
│   │   ├── README.md
│   │   ├── resources_links.md
│   │   ├── resources_written.md
│   │   ├── todo.md
│   │   ├── todo.md.bak
│   │   └── tool-comparison.md
│   ├── reference/
│   │   ├── api.md
│   │   ├── commands.md
│   │   ├── index.md
│   │   ├── README.md
│   │   ├── scripts.md
│   │   └── template-inventory.md
│   ├── templates/
│   │   ├── issue_templates/
│   │   │   ├── issue_forms/
│   │   │   │   ├── design_proposal.yml
│   │   │   │   ├── general.yml
│   │   │   │   ├── other.yml
│   │   │   │   ├── performance.yml
│   │   │   │   ├── question.yml
│   │   │   │   ├── refactor_request.yml
│   │   │   │   └── test_failure.yml
│   │   │   ├── legacy_markdown/
│   │   │   │   ├── bug_report.md
│   │   │   │   ├── design_proposal.md
│   │   │   │   ├── documentation.md
│   │   │   │   ├── feature_request.md
│   │   │   │   ├── general.md
│   │   │   │   ├── other.md
│   │   │   │   ├── performance.md
│   │   │   │   ├── question.md
│   │   │   │   ├── refactor_request.md
│   │   │   │   └── test_failure.md
│   │   │   └── README.md
│   │   ├── BUG_BOUNTY.md
│   │   ├── pull-request-draft.md
│   │   ├── README.md
│   │   ├── SECURITY_no_bounty.md
│   │   └── SECURITY_with_bounty.md
│   ├── .instructions.md
│   ├── index.md
│   ├── known-issues.md
│   ├── labels.md
│   ├── README.md
│   ├── release-policy.md
│   ├── releasing.md
│   ├── repo-layout.md
│   ├── sbom.md
│   ├── tooling.md
│   ├── USING_THIS_TEMPLATE.md
│   └── workflows.md
├── experiments/
│   ├── example_api_test.py
│   ├── example_data_exploration.py
│   └── README.md
├── labels/
│   ├── baseline.json
│   └── extended.json
├── mkdocs-hooks/
│   ├── generate_commands.py
│   ├── include_templates.py
│   ├── README.md
│   └── repo_links.py
├── repo_doctor.d/
│   ├── ci.toml
│   ├── container.toml
│   ├── db.toml
│   ├── docs.toml
│   ├── python.toml
│   ├── README.md
│   └── security.toml
├── scripts/
│   ├── precommit/
│   │   ├── auto_chmod_scripts.py
│   │   ├── check_local_imports.py
│   │   ├── check_nul_bytes.py
│   │   └── README.md
│   ├── sql/
│   │   ├── README.md
│   │   ├── reset.sql
│   │   └── scratch.example.sql
│   ├── .instructions.md
│   ├── _colors.py
│   ├── _container_common.py
│   ├── _doctor_common.py
│   ├── _imports.py
│   ├── _progress.py
│   ├── _ui.py
│   ├── apply-labels.sh
│   ├── apply_labels.py
│   ├── archive_todos.py
│   ├── bootstrap.py
│   ├── changelog_check.py
│   ├── check_known_issues.py
│   ├── check_python_support.py
│   ├── check_todos.py
│   ├── clean.py
│   ├── customize.py
│   ├── dep_versions.py
│   ├── doctor.py
│   ├── env_doctor.py
│   ├── env_inspect.py
│   ├── generate_command_reference.py
│   ├── git_doctor.py
│   ├── README.md
│   ├── repo_doctor.py
│   ├── repo_sauron.py
│   ├── test_containerfile.py
│   ├── test_containerfile.sh
│   ├── test_docker_compose.py
│   ├── test_docker_compose.sh
│   └── workflow_versions.py
├── src/
│   ├── simple_python_boilerplate/
│   │   ├── dev_tools/
│   │   │   └── __init__.py
│   │   ├── sql/
│   │   │   ├── __init__.py
│   │   │   ├── example_query.sql
│   │   │   └── README.md
│   │   ├── __init__.py
│   │   ├── _version.py
│   │   ├── api.py
│   │   ├── cli.py
│   │   ├── engine.py
│   │   ├── main.py
│   │   └── py.typed
│   └── README.md
├── tests/
│   ├── integration/
│   │   ├── sql/
│   │   │   ├── README.md
│   │   │   ├── setup_test_db.sql
│   │   │   └── teardown_test_db.sql
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_cli_smoke.py
│   │   └── test_db_example.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   ├── test_apply_labels.py
│   │   ├── test_archive_todos.py
│   │   ├── test_bootstrap.py
│   │   ├── test_changelog_check.py
│   │   ├── test_check_known_issues.py
│   │   ├── test_check_nul_bytes.py
│   │   ├── test_check_todos.py
│   │   ├── test_clean.py
│   │   ├── test_colors.py
│   │   ├── test_customize.py
│   │   ├── test_customize_interactive.py
│   │   ├── test_dep_versions.py
│   │   ├── test_doctor.py
│   │   ├── test_doctor_common.py
│   │   ├── test_env_doctor.py
│   │   ├── test_example.py
│   │   ├── test_generate_command_reference.py
│   │   ├── test_generate_commands.py
│   │   ├── test_git_doctor.py
│   │   ├── test_imports.py
│   │   ├── test_include_templates.py
│   │   ├── test_init_fallback.py
│   │   ├── test_main_entry.py
│   │   ├── test_progress.py
│   │   ├── test_repo_doctor.py
│   │   ├── test_repo_links.py
│   │   ├── test_test_containerfile.py
│   │   ├── test_test_docker_compose.py
│   │   ├── test_version.py
│   │   └── test_workflow_versions.py
│   ├── .instructions.md
│   ├── conftest.py
│   └── README.md
├── var/
│   ├── app.example.sqlite3
│   └── README.md
├── .containerignore
├── .coverage
├── .dockerignore
├── .editorconfig
├── .gitattributes
├── .gitconfig.recommended
├── .gitignore
├── .gitmessage.txt
├── .lycheeignore
├── .markdownlint-cli2.jsonc
├── .pre-commit-config.yaml
├── .prettierignore
├── .readthedocs.yaml
├── .release-please-manifest.json
├── .repo-doctor.toml
├── _typos.toml
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── codecov.yml
├── commit-report.md
├── container-structure-test.yml
├── Containerfile
├── CONTRIBUTING.md
├── docker-compose.yml
├── git-config-reference.md
├── LICENSE
├── mkdocs.yml
├── pgp-key.asc
├── pyproject.toml
├── README.md
├── release-please-config.json
├── requirements-dev.txt
├── requirements.txt
├── SECURITY.md
├── simple-python-boilerplate.code-workspace
├── Taskfile.yml
└── test-config-ref.md
```

</details>

---

## 📁 File Types

> Most common file extensions in the repository.

| Extension | Files | Lines |
|-----------|------:|------:|
| `.md` | 132 | 32,716 |
| `.py` | 80 | 32,825 |
| `.yml` | 56 | 8,489 |
| `(no ext)` | 11 | — |
| `.toml` | 9 | 2,143 |
| `.sql` | 9 | 333 |
| `.json` | 7 | 937 |
| `.txt` | 3 | 135 |
| `.sh` | 3 | 172 |
| `.yaml` | 2 | 470 |
| `.bak` | 2 | — |
| `.recommended` | 1 | — |
| `.jsonc` | 1 | — |
| `.asc` | 1 | — |
| `.code-workspace` | 1 | — |

---

## 🗣️ Languages

> Language breakdown by file count (percentage of recognized files).

| Language | Files | Lines | % |
|----------|------:|------:|---:|
| **Markdown** | 132 | 32,716 | 43.7% |
| **Python** | 80 | 32,825 | 26.5% |
| **YAML** | 58 | 8,959 | 19.2% |
| **TOML** | 9 | 2,143 | 3.0% |
| **SQL** | 9 | 333 | 3.0% |
| **JSON** | 7 | 937 | 2.3% |
| **Plain Text** | 3 | 135 | 1.0% |
| **Shell** | 3 | 172 | 1.0% |
| **Dockerfile** | 1 | — | 0.3% |

```diff
+ Markdown             █████████████████████ 43.7%
+ Python               █████████████ 26.5%
+ YAML                 █████████ 19.2%
+ TOML                 █ 3.0%
+ SQL                  █ 3.0%
+ JSON                 █ 2.3%
+ Plain Text           █ 1.0%
+ Shell                █ 1.0%
+ Dockerfile           █ 0.3%
```

---

## ⚡ Code & Script Activity

> [!NOTE]
> Commit frequency per file as a proxy for how actively code and scripts are used/developed.
> Files with more commits are being changed (and likely run) more frequently.

### Code Files (by commit activity)

| File | Commits | Last Commit |
|------|--------:|-------------|
| `scripts/git_doctor.py` | 38 | 2026-03-26 |
| `scripts/workflow_versions.py` | 25 | 2026-03-26 |
| `scripts/apply_labels.py` | 22 | 2026-03-26 |
| `scripts/bootstrap.py` | 19 | 2026-03-26 |
| `scripts/clean.py` | 18 | 2026-03-26 |
| `scripts/customize.py` | 18 | 2026-03-26 |
| `scripts/dep_versions.py` | 18 | 2026-03-26 |
| `scripts/env_doctor.py` | 17 | 2026-03-26 |
| `scripts/repo_doctor.py` | 16 | 2026-03-26 |
| `scripts/doctor.py` | 15 | 2026-03-26 |
| `scripts/generate_command_reference.py` | 15 | 2026-03-26 |
| `scripts/check_todos.py` | 13 | 2026-03-26 |
| `src/simple_python_boilerplate/__init__.py` | 12 | 2026-03-19 |
| `scripts/changelog_check.py` | 11 | 2026-03-26 |
| `scripts/check_known_issues.py` | 11 | 2026-03-26 |
| `scripts/archive_todos.py` | 10 | 2026-03-26 |
| `scripts/_progress.py` | 9 | 2026-03-09 |
| `scripts/test_containerfile.py` | 8 | 2026-03-26 |
| `scripts/test_docker_compose.py` | 8 | 2026-03-26 |
| `src/simple_python_boilerplate/main.py` | 8 | 2026-03-04 |

### Script Files (by commit activity)

| Script | Commits | Last Commit |
|--------|--------:|-------------|
| `scripts/git_doctor.py` | 38 | 2026-03-26 |
| `scripts/workflow_versions.py` | 25 | 2026-03-26 |
| `scripts/apply_labels.py` | 22 | 2026-03-26 |
| `scripts/bootstrap.py` | 19 | 2026-03-26 |
| `scripts/clean.py` | 18 | 2026-03-26 |
| `scripts/customize.py` | 18 | 2026-03-26 |
| `scripts/dep_versions.py` | 18 | 2026-03-26 |
| `scripts/env_doctor.py` | 17 | 2026-03-26 |
| `scripts/repo_doctor.py` | 16 | 2026-03-26 |
| `scripts/doctor.py` | 15 | 2026-03-26 |
| `scripts/generate_command_reference.py` | 15 | 2026-03-26 |
| `scripts/check_todos.py` | 13 | 2026-03-26 |
| `src/simple_python_boilerplate/__init__.py` | 12 | 2026-03-19 |
| `scripts/changelog_check.py` | 11 | 2026-03-26 |
| `scripts/check_known_issues.py` | 11 | 2026-03-26 |
| `scripts/archive_todos.py` | 10 | 2026-03-26 |
| `scripts/_progress.py` | 9 | 2026-03-09 |
| `scripts/test_containerfile.py` | 8 | 2026-03-26 |
| `scripts/test_docker_compose.py` | 8 | 2026-03-26 |
| `src/simple_python_boilerplate/main.py` | 8 | 2026-03-04 |

---

## 📦 Directory Sizes

> All 32 directories sorted by size (largest first).

<details>
<summary><strong>Click to expand directory sizes</strong></summary>

| Directory | Size | Files |
|-----------|-----:|------:|
| `scripts/` | 723.4 KB | 31 |
| `docs\notes/` | 433.0 KB | 9 |
| `tests\unit/` | 332.6 KB | 33 |
| `docs/` | 246.1 KB | 12 |
| `docs\adr/` | 205.4 KB | 43 |
| `docs\development/` | 99.7 KB | 7 |
| `docs\design/` | 78.0 KB | 5 |
| `docs\reference/` | 68.4 KB | 6 |
| `docs\templates\issue_templates\issue_forms/` | 67.8 KB | 7 |
| `docs\guide/` | 44.2 KB | 3 |
| `docs\templates/` | 43.1 KB | 5 |
| `repo_doctor.d/` | 35.5 KB | 7 |
| `docs\templates\issue_templates\legacy_markdown/` | 34.8 KB | 10 |
| `mkdocs-hooks/` | 28.4 KB | 4 |
| `var/` | 25.5 KB | 2 |
| `src\simple_python_boilerplate/` | 14.5 KB | 7 |
| `labels/` | 11.2 KB | 2 |
| `scripts\precommit/` | 11.0 KB | 4 |
| `tests\integration/` | 8.2 KB | 4 |
| `tests\integration\sql/` | 6.8 KB | 3 |
| `tests/` | 5.3 KB | 3 |
| `db/` | 5.2 KB | 2 |
| `db\queries/` | 5.2 KB | 2 |
| `src/` | 4.0 KB | 1 |
| `docs\templates\issue_templates/` | 3.7 KB | 1 |
| `db\migrations/` | 3.2 KB | 2 |
| `experiments/` | 3.1 KB | 3 |
| `db\seeds/` | 2.4 KB | 2 |
| `scripts\sql/` | 2.2 KB | 3 |
| `src\simple_python_boilerplate\sql/` | 1.9 KB | 3 |
| `docs\adr\archive/` | 1.2 KB | 1 |
| `src\simple_python_boilerplate\dev_tools/` | 52 B | 1 |

</details>

---

## 🐘 Largest Files

> Individual files sorted by size (top 15).

| File | Size |
|------|-----:|
| `docs\notes\learning.md` | 322.5 KB |
| `scripts\git_doctor.py` | 237.5 KB |
| `git-config-reference.md` | 87.1 KB |
| `docs\USING_THIS_TEMPLATE.md` | 85.4 KB |
| `scripts\customize.py` | 66.4 KB |
| `.coverage` | 52.0 KB |
| `CHANGELOG.md` | 51.7 KB |
| `scripts\workflow_versions.py` | 49.7 KB |
| `docs\development\branch-workflows.md` | 47.4 KB |
| `docs\releasing.md` | 46.0 KB |
| `scripts\env_doctor.py` | 43.8 KB |
| `tests\unit\test_workflow_versions.py` | 42.8 KB |
| `docs\reference\commands.md` | 41.5 KB |
| `docs\design\tool-decisions.md` | 37.9 KB |
| `test-config-ref.md` | 34.8 KB |

---

## 🕐 File Access Statistics

> [!WARNING]
> File access times (`atime`) depend on OS/filesystem configuration.
> Many systems use `relatime` or `noatime` mount options which may not reflect actual access.

<details>
<summary><strong>Click to expand file access stats</strong></summary>

| File | Last Accessed |
|------|---------------|
| `var\README.md` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_workflow_versions.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\__init__.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_test_docker_compose.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_version.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_repo_links.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_test_containerfile.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_progress.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_repo_doctor.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_include_templates.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_init_fallback.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_main_entry.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_git_doctor.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_imports.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_generate_commands.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_generate_command_reference.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_doctor_common.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_env_doctor.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_example.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_dep_versions.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_doctor.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_customize.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_customize_interactive.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_check_todos.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_clean.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_colors.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_bootstrap.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_changelog_check.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_check_known_issues.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_check_nul_bytes.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_apply_labels.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_archive_todos.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\conftest.py` | 2026-03-26 20:22:31 UTC |
| `tests\unit\test_api.py` | 2026-03-26 20:22:31 UTC |
| `tests\integration\sql\README.md` | 2026-03-26 20:22:31 UTC |
| `tests\integration\sql\setup_test_db.sql` | 2026-03-26 20:22:31 UTC |
| `tests\integration\sql\teardown_test_db.sql` | 2026-03-26 20:22:31 UTC |
| `tests\integration\test_db_example.py` | 2026-03-26 20:22:31 UTC |
| `tests\integration\__init__.py` | 2026-03-26 20:22:31 UTC |
| `tests\integration\conftest.py` | 2026-03-26 20:22:31 UTC |
| `tests\integration\test_cli_smoke.py` | 2026-03-26 20:22:31 UTC |
| `tests\conftest.py` | 2026-03-26 20:22:31 UTC |
| `tests\README.md` | 2026-03-26 20:22:31 UTC |
| `src\simple_python_boilerplate\sql\__init__.py` | 2026-03-26 20:22:31 UTC |
| `tests\.instructions.md` | 2026-03-26 20:22:31 UTC |
| `src\simple_python_boilerplate\sql\example_query.sql` | 2026-03-26 20:22:31 UTC |
| `src\simple_python_boilerplate\sql\README.md` | 2026-03-26 20:22:31 UTC |
| `src\simple_python_boilerplate\dev_tools\__init__.py` | 2026-03-26 20:22:31 UTC |
| `src\simple_python_boilerplate\_version.py` | 2026-03-26 20:22:31 UTC |
| `src\simple_python_boilerplate\__init__.py` | 2026-03-26 20:22:31 UTC |
| *... and 270 more files* | |

</details>

---

## 📜 Git History

| Metric | Value |
|--------|-------|
| **Total commits** | 825 |
| **Contributors** | 5 |
| **Branches** | 3 |
| **Tags** | 6 |
| **Current branch** | `wip/2026-03-26-scratch` |
| **Latest tag** | `v1.0.0` |
| **First commit** | 2026-03-26 |
| **Last commit** | 2026-03-26 |
| **Remote** | `https://github.com/JoJo275/simple-python-boilerplate.git` |

---

## 📝 Per-File Git Statistics

> Commit count and last commit date for every tracked file.

<details>
<summary><strong>Click to expand per-file git stats</strong></summary>

| File | Commits | Last Commit |
|------|--------:|-------------|
| `docs/notes/todo.md` | 121 | 2026-03-19 |
| `README.md` | 80 | 2026-03-26 |
| `docs/notes/learning.md` | 60 | 2026-03-26 |
| `.github/copilot-instructions.md` | 59 | 2026-03-26 |
| `pyproject.toml` | 57 | 2026-03-18 |
| `docs/USING_THIS_TEMPLATE.md` | 55 | 2026-03-26 |
| `.github/ISSUE_TEMPLATE/bug_report.yml` | 50 | 2026-03-03 |
| `scripts/git_doctor.py` | 38 | 2026-03-26 |
| `.pre-commit-config.yaml` | 36 | 2026-03-26 |
| `Taskfile.yml` | 31 | 2026-03-26 |
| `scripts/README.md` | 27 | 2026-03-26 |
| `docs/workflows.md` | 25 | 2026-03-18 |
| `scripts/workflow_versions.py` | 25 | 2026-03-26 |
| `.github/workflows/release.yml` | 24 | 2026-03-18 |
| `docs/releasing.md` | 23 | 2026-03-26 |
| `.gitignore` | 22 | 2026-03-11 |
| `SECURITY.md` | 22 | 2026-03-18 |
| `scripts/apply_labels.py` | 22 | 2026-03-26 |
| `docs/adr/README.md` | 21 | 2026-03-18 |
| `docs/design/architecture.md` | 20 | 2026-03-26 |
| `docs/templates/pull-request-draft.md` | 20 | 2026-03-18 |
| `mkdocs.yml` | 19 | 2026-03-13 |
| `scripts/bootstrap.py` | 19 | 2026-03-26 |
| `CONTRIBUTING.md` | 18 | 2026-03-02 |
| `docs/labels.md` | 18 | 2026-03-18 |
| `scripts/clean.py` | 18 | 2026-03-26 |
| `scripts/customize.py` | 18 | 2026-03-26 |
| `scripts/dep_versions.py` | 18 | 2026-03-26 |
| `.github/workflows/pre-commit-update.yml` | 17 | 2026-03-26 |
| `scripts/env_doctor.py` | 17 | 2026-03-26 |
| `.github/workflows/security-audit.yml` | 16 | 2026-03-02 |
| `.github/workflows/spellcheck.yml` | 16 | 2026-03-02 |
| `scripts/repo_doctor.py` | 16 | 2026-03-26 |
| `.github/ISSUE_TEMPLATE/feature_request.yml` | 15 | 2026-03-03 |
| `.github/workflows/spellcheck-autofix.yml` | 15 | 2026-03-02 |
| `docs/repo-layout.md` | 15 | 2026-03-18 |
| `scripts/doctor.py` | 15 | 2026-03-26 |
| `scripts/generate_command_reference.py` | 15 | 2026-03-26 |
| `.github/ISSUE_TEMPLATE/config.yml` | 14 | 2026-01-29 |
| `.github/workflows/coverage.yml` | 14 | 2026-03-02 |
| `.github/workflows/stale.yml` | 14 | 2026-03-18 |
| `.github/workflows/test.yml` | 14 | 2026-03-02 |
| `docs/development/developer-commands.md` | 14 | 2026-03-18 |
| `simple-python-boilerplate.code-workspace` | 14 | 2026-03-18 |
| `.github/workflows/container-build.yml` | 13 | 2026-03-18 |
| `.github/workflows/container-scan.yml` | 13 | 2026-03-18 |
| `.github/workflows/dependency-review.yml` | 13 | 2026-03-18 |
| `.github/workflows/lint-format.yml` | 13 | 2026-03-02 |
| `docs/development/development.md` | 13 | 2026-03-26 |
| `docs/index.md` | 13 | 2026-03-26 |
| `scripts/check_todos.py` | 13 | 2026-03-26 |
| `.github/workflows/bandit.yml` | 12 | 2026-02-24 |
| `.github/workflows/nightly-security.yml` | 12 | 2026-03-26 |
| `.github/workflows/sbom.yml` | 12 | 2026-03-18 |
| `docs/development/pull-requests.md` | 12 | 2026-03-18 |
| `docs/known-issues.md` | 12 | 2026-03-26 |
| `docs/notes/archive.md` | 12 | 2026-03-19 |
| `git-config-reference.md` | 12 | 2026-03-18 |
| `src/simple_python_boilerplate/__init__.py` | 12 | 2026-03-19 |
| `.github/dependabot.yml` | 11 | 2026-03-03 |
| `.github/workflows/type-check.yml` | 11 | 2026-03-02 |
| `CHANGELOG.md` | 11 | 2026-03-19 |
| `scripts/changelog_check.py` | 11 | 2026-03-26 |
| `scripts/check_known_issues.py` | 11 | 2026-03-26 |
| `.github/ISSUE_TEMPLATE/documentation.yml` | 10 | 2026-03-03 |
| `.github/workflows/labeler.yml` | 10 | 2026-02-24 |
| `.github/workflows/link-checker.yml` | 10 | 2026-03-19 |
| `.github/workflows/scorecard.yml` | 10 | 2026-03-18 |
| `.vscode/settings.json` | 10 | 2026-03-26 |
| `docs/design/ci-cd-design.md` | 10 | 2026-03-18 |
| `requirements-dev.txt` | 10 | 2026-03-18 |
| `scripts/archive_todos.py` | 10 | 2026-03-26 |
| `.github/workflows/ci-gate.yml` | 9 | 2026-03-02 |
| `Containerfile` | 9 | 2026-03-17 |
| `docs/design/tool-decisions.md` | 9 | 2026-02-28 |
| `docs/development/command-workflows.md` | 9 | 2026-03-18 |
| `scripts/_progress.py` | 9 | 2026-03-09 |
| `.repo-doctor.toml` | 8 | 2026-03-02 |
| `docs/development/dev-setup.md` | 8 | 2026-03-18 |
| `docs/guide/troubleshooting.md` | 8 | 2026-03-26 |
| `docs/notes/README.md` | 8 | 2026-03-18 |
| `docs/tooling.md` | 8 | 2026-03-18 |
| `scripts/test_containerfile.py` | 8 | 2026-03-26 |
| `scripts/test_docker_compose.py` | 8 | 2026-03-26 |
| `src/simple_python_boilerplate/main.py` | 8 | 2026-03-04 |
| `tests/unit/test_workflow_versions.py` | 8 | 2026-03-19 |
| `.containerignore` | 7 | 2026-03-02 |
| `.dockerignore` | 7 | 2026-03-02 |
| `.github/PULL_REQUEST_TEMPLATE.md` | 7 | 2026-02-27 |
| `.github/workflows/docs-deploy.yml` | 7 | 2026-03-18 |
| `.github/workflows/pr-title.yml` | 7 | 2026-03-19 |
| `.release-please-manifest.json` | 7 | 2026-03-19 |
| `codecov.yml` | 7 | 2026-03-18 |
| `docs/README.md` | 7 | 2026-03-03 |
| `docs/adr/008-pre-commit-hooks.md` | 7 | 2026-03-26 |
| `docs/reference/commands.md` | 7 | 2026-03-26 |
| `.devcontainer/README.md` | 6 | 2026-03-16 |
| `.github/labeler.yml` | 6 | 2026-03-03 |
| `.github/workflows/README.md` | 6 | 2026-03-03 |
| `CODE_OF_CONDUCT.md` | 6 | 2026-03-02 |
| `docs/adr/011-repository-guard-pattern.md` | 6 | 2026-03-18 |
| `docs/development/README.md` | 6 | 2026-03-18 |
| `docs/development/branch-workflows.md` | 6 | 2026-03-18 |
| `docs/guide/getting-started.md` | 6 | 2026-03-18 |
| `docs/reference/index.md` | 6 | 2026-03-18 |
| `docs/release-policy.md` | 6 | 2026-03-18 |
| `labels/baseline.json` | 6 | 2026-03-03 |
| `labels/extended.json` | 6 | 2026-03-03 |
| `mkdocs-hooks/README.md` | 6 | 2026-03-18 |
| `mkdocs-hooks/generate_commands.py` | 6 | 2026-03-18 |
| `requirements.txt` | 6 | 2026-02-26 |
| `scripts/apply-labels.sh` | 6 | 2026-03-03 |
| `src/simple_python_boilerplate/engine.py` | 6 | 2026-03-08 |
| `tests/unit/test_env_doctor.py` | 6 | 2026-03-12 |
| `.gitattributes` | 5 | 2026-03-03 |
| `.github/FUNDING.yml` | 5 | 2026-03-03 |
| `.github/workflows/auto-merge-dependabot.yml` | 5 | 2026-03-18 |
| `.github/workflows/commit-lint.yml` | 5 | 2026-03-18 |
| `.github/workflows/release-please.yml` | 5 | 2026-03-18 |
| `.lycheeignore` | 5 | 2026-03-06 |
| `.readthedocs.yaml` | 5 | 2026-03-02 |
| `LICENSE` | 5 | 2026-01-16 |
| `db/README.md` | 5 | 2026-03-03 |
| `db/migrations/README.md` | 5 | 2026-03-03 |
| `db/queries/example_queries.sql` | 5 | 2026-03-03 |
| `docker-compose.yml` | 5 | 2026-03-17 |
| `docs/adr/002-pyproject-toml.md` | 5 | 2026-03-18 |
| `docs/adr/003-separate-workflow-files.md` | 5 | 2026-02-27 |
| `docs/adr/020-mkdocs-documentation-stack.md` | 5 | 2026-03-18 |
| `docs/design/README.md` | 5 | 2026-03-03 |
| `docs/reference/api.md` | 5 | 2026-03-02 |
| `docs/sbom.md` | 5 | 2026-03-02 |
| `docs/templates/BUG_BOUNTY.md` | 5 | 2026-03-18 |
| `docs/templates/SECURITY_no_bounty.md` | 5 | 2026-03-18 |
| `docs/templates/SECURITY_with_bounty.md` | 5 | 2026-03-18 |
| `mkdocs-hooks/repo_links.py` | 5 | 2026-03-04 |
| `release-please-config.json` | 5 | 2026-03-18 |
| `scripts/.instructions.md` | 5 | 2026-03-26 |
| `scripts/_colors.py` | 5 | 2026-03-09 |
| `scripts/precommit/README.md` | 5 | 2026-03-18 |
| `scripts/sql/README.md` | 5 | 2026-03-18 |
| `src/README.md` | 5 | 2026-03-18 |
| `tests/README.md` | 5 | 2026-03-18 |
| `tests/integration/sql/setup_test_db.sql` | 5 | 2026-03-03 |
| `tests/integration/sql/teardown_test_db.sql` | 5 | 2026-03-03 |
| `tests/integration/test_db_example.py` | 5 | 2026-03-03 |
| `tests/unit/test_repo_doctor.py` | 5 | 2026-03-18 |
| `.devcontainer/devcontainer.json` | 4 | 2026-03-16 |
| `.github/CODEOWNERS` | 4 | 2026-03-03 |
| `.github/workflows-optional/README.md` | 4 | 2026-03-03 |
| `.github/workflows/license-check.yml` | 4 | 2026-03-05 |
| `.github/workflows/regenerate-files.yml` | 4 | 2026-03-18 |
| `_typos.toml` | 4 | 2026-03-03 |
| `commit-report.md` | 4 | 2026-03-18 |
| `db/migrations/001_example_migration.sql` | 4 | 2026-03-03 |
| `db/queries/README.md` | 4 | 2026-03-03 |
| `db/seeds/001_example_seed.sql` | 4 | 2026-03-03 |
| `db/seeds/README.md` | 4 | 2026-03-03 |
| `docs/adr/001-src-layout.md` | 4 | 2026-02-27 |
| `docs/adr/004-pin-action-shas.md` | 4 | 2026-02-27 |
| `docs/adr/006-pytest-for-testing.md` | 4 | 2026-02-27 |
| `docs/adr/013-sbom-bill-of-materials.md` | 4 | 2026-03-18 |
| `docs/templates/README.md` | 4 | 2026-03-03 |
| `docs/templates/issue_templates/README.md` | 4 | 2026-03-18 |
| `mkdocs-hooks/include_templates.py` | 4 | 2026-03-04 |
| `repo_doctor.d/README.md` | 4 | 2026-03-03 |
| `scripts/_doctor_common.py` | 4 | 2026-03-10 |
| `scripts/precommit/check_nul_bytes.py` | 4 | 2026-03-18 |
| `scripts/test_containerfile.sh` | 4 | 2026-03-19 |
| `scripts/test_docker_compose.sh` | 4 | 2026-03-19 |
| `src/simple_python_boilerplate/cli.py` | 4 | 2026-03-03 |
| `tests/integration/sql/README.md` | 4 | 2026-03-03 |
| `.github/workflows-optional/changelog.yml` | 3 | 2026-02-24 |
| `.github/workflows/cache-cleanup.yml` | 3 | 2026-03-05 |
| `.github/workflows/docs-build.yml` | 3 | 2026-03-18 |
| `.github/workflows/security-codeql.yml` | 3 | 2026-03-18 |
| `.gitmessage.txt` | 3 | 2026-03-03 |
| `.markdownlint-cli2.jsonc` | 3 | 2026-03-02 |
| `.prettierignore` | 3 | 2026-03-02 |
| `db/schema.sql` | 3 | 2026-03-03 |
| `docs/.instructions.md` | 3 | 2026-03-18 |
| `docs/adr/005-ruff-for-linting-formatting.md` | 3 | 2026-02-27 |
| `docs/adr/007-mypy-for-type-checking.md` | 3 | 2026-02-27 |
| `docs/adr/009-conventional-commits.md` | 3 | 2026-02-27 |
| `docs/adr/012-multi-layer-security-scanning.md` | 3 | 2026-02-27 |
| `docs/adr/015-no-github-directory-readme.md` | 3 | 2026-02-27 |
| `docs/adr/016-hatchling-and-hatch.md` | 3 | 2026-02-27 |
| `docs/adr/018-bandit-for-security-linting.md` | 3 | 2026-02-27 |
| `docs/adr/019-containerfile.md` | 3 | 2026-02-27 |
| `docs/adr/024-ci-gate-pattern.md` | 3 | 2026-02-27 |
| `docs/adr/031-script-conventions.md` | 3 | 2026-03-03 |
| `docs/adr/032-dependency-grouping-strategy.md` | 3 | 2026-03-18 |
| `docs/adr/archive/README.md` | 3 | 2026-03-03 |
| `docs/design/database.md` | 3 | 2026-02-27 |
| `docs/notes/resources_written.md` | 3 | 2026-03-18 |
| `docs/notes/tool-comparison.md` | 3 | 2026-02-28 |
| `docs/reference/scripts.md` | 3 | 2026-03-18 |
| `docs/templates/issue_templates/legacy_markdown/bug_report.md` | 3 | 2026-03-03 |
| `docs/templates/issue_templates/legacy_markdown/design_proposal.md` | 3 | 2026-03-03 |
| `docs/templates/issue_templates/legacy_markdown/documentation.md` | 3 | 2026-03-03 |
| `docs/templates/issue_templates/legacy_markdown/feature_request.md` | 3 | 2026-03-03 |
| `docs/templates/issue_templates/legacy_markdown/performance.md` | 3 | 2026-03-03 |
| `docs/templates/issue_templates/legacy_markdown/question.md` | 3 | 2026-03-03 |
| `docs/templates/issue_templates/legacy_markdown/refactor_request.md` | 3 | 2026-03-03 |
| `docs/templates/issue_templates/legacy_markdown/test_failure.md` | 3 | 2026-03-03 |
| `experiments/README.md` | 3 | 2026-03-03 |
| `repo_doctor.d/ci.toml` | 3 | 2026-03-18 |
| `repo_doctor.d/container.toml` | 3 | 2026-03-18 |
| `repo_doctor.d/docs.toml` | 3 | 2026-03-18 |
| `scripts/_imports.py` | 3 | 2026-03-06 |
| `scripts/check_python_support.py` | 3 | 2026-03-26 |
| `scripts/sql/reset.sql` | 3 | 2026-03-03 |
| `scripts/sql/scratch.example.sql` | 3 | 2026-03-03 |
| `src/simple_python_boilerplate/api.py` | 3 | 2026-03-08 |
| `src/simple_python_boilerplate/sql/README.md` | 3 | 2026-03-03 |
| `src/simple_python_boilerplate/sql/example_query.sql` | 3 | 2026-03-03 |
| `tests/integration/__init__.py` | 3 | 2026-03-03 |
| `tests/unit/__init__.py` | 3 | 2026-03-03 |
| `tests/unit/test_clean.py` | 3 | 2026-03-04 |
| `tests/unit/test_dep_versions.py` | 3 | 2026-02-26 |
| `tests/unit/test_doctor.py` | 3 | 2026-03-06 |
| `tests/unit/test_example.py` | 3 | 2026-03-03 |
| `var/README.md` | 3 | 2026-03-03 |
| `var/app.example.sqlite3` | 3 | 2026-03-03 |
| `.editorconfig` | 2 | 2026-03-03 |
| `.github/SKILL.md` | 2 | 2026-03-05 |
| `.github/workflows/devcontainer-build.yml` | 2 | 2026-03-18 |
| `.github/workflows/doctor-all.yml` | 2 | 2026-03-18 |
| `docs/adr/.instructions.md` | 2 | 2026-03-05 |
| `docs/adr/010-dependabot-for-dependency-updates.md` | 2 | 2026-02-27 |
| `docs/adr/014-no-template-engine.md` | 2 | 2026-02-27 |
| `docs/adr/017-task-runner.md` | 2 | 2026-02-27 |
| `docs/adr/021-automated-release-pipeline.md` | 2 | 2026-02-27 |
| `docs/adr/022-rebase-merge-strategy.md` | 2 | 2026-02-27 |
| `docs/adr/023-branch-protection-rules.md` | 2 | 2026-02-27 |
| `docs/adr/026-no-pip-tools.md` | 2 | 2026-02-27 |
| `docs/adr/027-database-strategy.md` | 2 | 2026-02-27 |
| `docs/adr/028-git-branching-strategy.md` | 2 | 2026-02-27 |
| `docs/adr/029-testing-strategy.md` | 2 | 2026-02-27 |
| `docs/adr/030-label-management-as-code.md` | 2 | 2026-03-18 |
| `docs/adr/037-git-configuration-as-code.md` | 2 | 2026-03-18 |
| `docs/adr/038-vscode-workspace-configuration-strategy.md` | 2 | 2026-03-18 |
| `docs/adr/039-developer-onboarding-automation.md` | 2 | 2026-03-18 |
| `docs/guide/README.md` | 2 | 2026-03-18 |
| `docs/reference/README.md` | 2 | 2026-03-18 |
| `docs/reference/template-inventory.md` | 2 | 2026-03-18 |
| `docs/templates/issue_templates/issue_forms/design_proposal.yml` | 2 | 2026-03-03 |
| `docs/templates/issue_templates/issue_forms/performance.yml` | 2 | 2026-03-03 |
| `docs/templates/issue_templates/issue_forms/question.yml` | 2 | 2026-03-03 |
| `docs/templates/issue_templates/issue_forms/refactor_request.yml` | 2 | 2026-03-03 |
| `docs/templates/issue_templates/issue_forms/test_failure.yml` | 2 | 2026-03-03 |
| `docs/templates/issue_templates/legacy_markdown/general.md` | 2 | 2026-02-27 |
| `docs/templates/issue_templates/legacy_markdown/other.md` | 2 | 2026-02-27 |
| `experiments/example_api_test.py` | 2 | 2026-02-17 |
| `experiments/example_data_exploration.py` | 2 | 2026-02-17 |
| `repo_doctor.d/db.toml` | 2 | 2026-03-03 |
| `repo_doctor.d/python.toml` | 2 | 2026-03-03 |
| `repo_doctor.d/security.toml` | 2 | 2026-03-03 |
| `scripts/_container_common.py` | 2 | 2026-03-19 |
| `scripts/env_inspect.py` | 2 | 2026-03-26 |
| `scripts/repo_sauron.py` | 2 | 2026-03-26 |
| `src/simple_python_boilerplate/dev_tools/__init__.py` | 2 | 2026-02-17 |
| `src/simple_python_boilerplate/sql/__init__.py` | 2 | 2026-03-03 |
| `test-config-ref.md` | 2 | 2026-03-18 |
| `tests/.instructions.md` | 2 | 2026-03-05 |
| `tests/conftest.py` | 2 | 2026-02-26 |
| `tests/integration/test_cli_smoke.py` | 2 | 2026-02-22 |
| `tests/unit/test_customize.py` | 2 | 2026-03-18 |
| `tests/unit/test_customize_interactive.py` | 2 | 2026-03-18 |
| `tests/unit/test_generate_commands.py` | 2 | 2026-03-18 |
| `tests/unit/test_git_doctor.py` | 2 | 2026-03-12 |
| `tests/unit/test_include_templates.py` | 2 | 2026-03-06 |
| `tests/unit/test_test_containerfile.py` | 2 | 2026-03-19 |
| `tests/unit/test_test_docker_compose.py` | 2 | 2026-03-19 |
| `.gitconfig.recommended` | 1 | 2026-03-12 |
| `.github/workflows/.instructions.md` | 1 | 2026-03-05 |
| `.github/workflows/known-issues-check.yml` | 1 | 2026-03-04 |
| `.github/workflows/repo-doctor.yml` | 1 | 2026-03-04 |
| `.github/workflows/todo-check.yml` | 1 | 2026-03-04 |
| `.github/workflows/welcome.yml` | 1 | 2026-03-04 |
| `.vscode/extensions.json` | 1 | 2026-03-11 |
| `container-structure-test.yml` | 1 | 2026-03-07 |
| `docs/adr/025-container-strategy.md` | 1 | 2026-02-23 |
| `docs/adr/033-prettier-for-markdown-formatting.md` | 1 | 2026-02-28 |
| `docs/adr/034-documentation-organization-strategy.md` | 1 | 2026-02-28 |
| `docs/adr/035-copilot-instructions-as-context.md` | 1 | 2026-02-28 |
| `docs/adr/036-diagnostic-tooling-strategy.md` | 1 | 2026-03-16 |
| `docs/adr/040-v1-release-readiness.md` | 1 | 2026-03-18 |
| `docs/adr/template.md` | 1 | 2026-02-20 |
| `docs/notes/resources_links.md` | 1 | 2026-03-13 |
| `docs/templates/issue_templates/issue_forms/general.yml` | 1 | 2026-02-22 |
| `docs/templates/issue_templates/issue_forms/other.yml` | 1 | 2026-02-22 |
| `pgp-key.asc` | 1 | 2026-03-07 |
| `scripts/_ui.py` | 1 | 2026-03-26 |
| `scripts/precommit/check_local_imports.py` | 1 | 2026-03-26 |
| `src/simple_python_boilerplate/py.typed` | 1 | 2026-02-22 |
| `tests/integration/conftest.py` | 1 | 2026-02-22 |
| `tests/unit/conftest.py` | 1 | 2026-02-22 |
| `tests/unit/test_api.py` | 1 | 2026-02-23 |
| `tests/unit/test_apply_labels.py` | 1 | 2026-03-07 |
| `tests/unit/test_archive_todos.py` | 1 | 2026-02-25 |
| `tests/unit/test_bootstrap.py` | 1 | 2026-03-07 |
| `tests/unit/test_changelog_check.py` | 1 | 2026-03-07 |
| `tests/unit/test_check_known_issues.py` | 1 | 2026-03-04 |
| `tests/unit/test_check_nul_bytes.py` | 1 | 2026-03-07 |
| `tests/unit/test_check_todos.py` | 1 | 2026-03-07 |
| `tests/unit/test_colors.py` | 1 | 2026-03-06 |
| `tests/unit/test_doctor_common.py` | 1 | 2026-03-06 |
| `tests/unit/test_generate_command_reference.py` | 1 | 2026-03-04 |
| `tests/unit/test_imports.py` | 1 | 2026-03-07 |
| `tests/unit/test_init_fallback.py` | 1 | 2026-03-06 |
| `tests/unit/test_main_entry.py` | 1 | 2026-03-06 |
| `tests/unit/test_progress.py` | 1 | 2026-03-04 |
| `tests/unit/test_repo_links.py` | 1 | 2026-02-28 |
| `tests/unit/test_version.py` | 1 | 2026-02-22 |

</details>

---

## 👥 Contributors

> Top 5 of 5 contributors, ranked by commits.

| Contributor | Commits |
|-------------|--------:|
| **Joseph** | 807 |
| **dependabot[bot]** | 11 |
| **github-actions[bot]** | 3 |
| **spb-release-bot[bot]** | 3 |
| **JoJo275** | 1 |

---

## 🔧 Recommended Scripts

> Scripts that expand on repository information and health checks.
>
> **Source:** [simple-python-boilerplate](https://github.com/JoJo275/simple-python-boilerplate) by [JoJo275](https://github.com/JoJo275) on GitHub
>
> Scripts are located in the `scripts/` directory.
>
> *These scripts may already exist in this repository if it was forked from or based on the source.*
> *If not, visit the [source repo](https://github.com/JoJo275/simple-python-boilerplate) by JoJo275 to obtain them.*

| Script | Description |
|--------|-------------|
| `python scripts/git_doctor.py` | Git health dashboard — config, branch ops, integrity |
| `python scripts/env_inspect.py` | Environment, packages, PATH inspection |
| `python scripts/check_python_support.py` | Python version consistency across configs |
| `python scripts/repo_doctor.py` | Repository structure health checks |
| `python scripts/dep_versions.py show` | Dependency versions and update status |
| `python scripts/env_doctor.py` | Development environment diagnostics |
| `python scripts/doctor.py` | Unified health check (runs all doctors) |
| `python scripts/workflow_versions.py` | GitHub Actions SHA-pinned version status |

---

<sub>Generated by <strong>repo_sauron.py</strong> v2.0.0 — the all-seeing eye &bull; 2026-03-26 20:23:07 UTC</sub>
