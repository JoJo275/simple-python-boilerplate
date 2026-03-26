#!/usr/bin/env python3
"""Interactive project customization — replace boilerplate placeholders.

Replaces template placeholders with your project's values, renames the
package directory, strips optional directories, cleans up template-specific
files, and optionally swaps the license.  A lightweight alternative to
template engines like Copier or Cookiecutter — runs once after cloning
with no external dependencies.

See ADR 014 for the design rationale behind manual customization.

Flags::

    --dry-run               Show what would change without modifying any files
    --non-interactive       Skip interactive prompts; use CLI flags for all values
    --project-name NAME     Project name (lowercase-hyphenated, e.g. my-project)
    --package-name NAME     Python package name (underscored); auto-derived from
                            --project-name if omitted
    --author NAME           Author name
    --github-user NAME      GitHub username or organization
    --description TEXT       One-line project description
    --cli-prefix PREFIX     CLI command prefix (default: initials of project name)
    --license ID            License to use (default: apache-2.0; choices:
                            apache-2.0, mit, bsd-3-clause, …)
    --strip DIR [DIR ...]   Optional directories to remove: db, experiments, var,
                            container, optional-workflows, labels, repo-doctor, …
    --template-cleanup ITEM [ITEM ...]
                            Template-specific items to clean up: adr-files,
                            docs-notes, docs-design, docs-reference,
                            docs-development, docs-guide, placeholder-code,
                            utility-scripts, advanced-workflows
    --private-repo          Strip open-source community files not needed for
                            private repos (CODE_OF_CONDUCT, CONTRIBUTING,
                            SECURITY, scorecard workflow, etc.)
    --force                 Skip the already-customized safety check
    --enable-workflows SLUG Replace YOURNAME/YOURREPO in all workflow files with
                            your repo slug (runs only this operation)
    -q, --quiet             Suppress informational output (errors still shown)
    --version               Print version and exit

Usage::

    # Interactive (default)
    python scripts/customize.py

    # Preview changes
    python scripts/customize.py --dry-run

    # Fully non-interactive
    python scripts/customize.py --non-interactive \\
        --project-name my-project --author "Jane Doe" \\
        --github-user janedoe --strip db experiments

    # Non-interactive with template cleanup
    python scripts/customize.py --non-interactive \\
        --project-name my-project --author "Jane Doe" \\
        --github-user janedoe \\
        --template-cleanup adr-files docs-notes placeholder-code

    # Just enable workflows
    python scripts/customize.py --enable-workflows janedoe/my-project
"""

from __future__ import annotations

import argparse
import datetime
import keyword
import logging
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

# -- Local script modules (not third-party; live in scripts/) ----------------
from _colors import Colors, unicode_symbols
from _imports import find_repo_root, import_sibling
from _ui import UI

_progress = import_sibling("_progress")
ProgressBar = _progress.ProgressBar

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = find_repo_root()
SCRIPT_VERSION = "1.5.0"

# Theme color for this script's dashboard output.
THEME = "cyan"

# Original placeholders baked into the template.
# customize.py searches files for these literal strings and replaces them
# with the user's values.  plan_replacements() builds the substitution list.
# NOTE: If you forked this template and changed these values throughout your
# template clone before running customize.py, update them here so the script can
# find them.
TEMPLATE_PROJECT_NAME = "simple-python-boilerplate"  # -> cfg.project_name  (kebab-case repo slug / PyPI name)
TEMPLATE_PACKAGE_NAME = "simple_python_boilerplate"  # -> cfg.package_name  (Python import name, underscored)
TEMPLATE_GITHUB_USER = "JoJo275"  # -> cfg.github_user   (GitHub username or org)
TEMPLATE_GITHUB_URL_PLACEHOLDER = (
    "YOURNAME/YOURREPO"  # -> <github_user>/<project_name>  (full repo slug)
)
TEMPLATE_AUTHOR = "Joseph"  # -> cfg.author        (pyproject.toml authors.name)
TEMPLATE_DESCRIPTION = (
    "Simple Python boilerplate using src/ layout"  # -> cfg.description
)
TEMPLATE_CLI_PREFIX = "spb"  # -> cfg.cli_prefix    (entry-point command prefix)

# Directory names to skip when scanning files (exact match)
SKIP_DIRS: set[str] = {
    ".git",
    ".venv",
    ".venv-1",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "node_modules",
    "site",
}

# Directory name suffixes to skip (endswith match)
SKIP_DIR_SUFFIXES: set[str] = {
    ".egg-info",
}

# File extensions to process (text-based files only)
TEXT_EXTENSIONS: set[str] = {
    ".py",
    ".toml",
    ".yml",
    ".yaml",
    ".md",
    ".txt",
    ".cfg",
    ".ini",
    ".json",
    ".sh",
    ".ps1",
    ".bat",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".rst",
    ".in",
    ".sql",
    ".env",
    ".containerfile",
    ".dockerfile",
}

# Extensionless filenames that should always be scanned
SCAN_FILENAMES: set[str] = {
    "Containerfile",
    "Dockerfile",
    "Makefile",
    "Taskfile",
    "Procfile",
}

# Files to never modify (relative to ROOT)
SKIP_FILES: set[Path] = {
    Path("scripts") / "customize.py",
}

# Optional directories / files that can be stripped
# TODO (template users): Add your own optional directory groups here if
#   your project has components that downstream users might not need
#   (e.g., "mobile-app", "admin-panel", "legacy-api").
STRIPPABLE: dict[str, dict[str, object]] = {
    "db": {
        "label": "Database directory (schema, migrations, seeds, queries)",
        "paths": [
            "db/",
            "scripts/sql/",
            f"src/{TEMPLATE_PACKAGE_NAME}/sql/",
        ],
    },
    "experiments": {
        "label": "Experiments / scratch code directory",
        "paths": ["experiments/"],
    },
    "var": {
        "label": "Local data / state directory (var/)",
        "paths": ["var/"],
    },
    "docs-templates": {
        "label": "Security-policy & issue templates (docs/templates/)",
        "paths": ["docs/templates/"],
    },
    "container": {
        "label": "Container files (Containerfile, docker-compose, build & scan workflows)",
        "paths": [
            "Containerfile",
            "docker-compose.yml",
            "container-structure-test.yml",
            ".github/workflows/container-build.yml",
            ".github/workflows/container-scan.yml",
            "scripts/_container_common.py",
            "scripts/test_containerfile.py",
            "scripts/test_containerfile.sh",
            "scripts/test_docker_compose.py",
            "scripts/test_docker_compose.sh",
        ],
    },
    "optional-workflows": {
        "label": "Optional workflow templates (.github/workflows-optional/)",
        "paths": [".github/workflows-optional/"],
    },
    "labels": {
        "label": "Label management files (labels/, apply scripts)",
        "paths": [
            "labels/",
            "scripts/apply_labels.py",
            "scripts/apply-labels.sh",
        ],
    },
    "repo-doctor": {
        "label": "Repo doctor checks (repo_doctor.d/, doctor scripts)",
        "paths": [
            "repo_doctor.d/",
            "scripts/repo_doctor.py",
            "scripts/doctor.py",
            "scripts/env_doctor.py",
            "scripts/git_doctor.py",
            "scripts/_doctor_common.py",
        ],
        # NOTE: _ui.py and _colors.py are intentionally NOT listed here.
        # They are shared modules used by many scripts (bootstrap.py,
        # customize.py, dep_versions.py, etc.), not just the doctor
        # scripts.  Stripping repo-doctor leaves them in place, which
        # is correct.
    },
}

# Files that are private-repo-specific and should be removed when
# --private-repo is passed (these are only useful for public/open-source
# repos).
PRIVATE_REPO_STRIP: dict[str, dict[str, object]] = {
    "community-files": {
        "label": "Open-source community files (not needed for private repos)",
        "paths": [
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "pgp-key.asc",
        ],
    },
    "public-workflows": {
        "label": "Public-repo workflows (Scorecard, welcome bot, stale issues)",
        "paths": [
            ".github/workflows/scorecard.yml",
            ".github/workflows/welcome.yml",
            ".github/workflows/stale.yml",
            ".github/workflows/sbom.yml",
        ],
    },
    "label-management": {
        "label": "GitHub label management (labels/, apply scripts)",
        "paths": [
            "labels/",
            "scripts/apply_labels.py",
            "scripts/apply-labels.sh",
        ],
    },
}

# ---------------------------------------------------------------------------
# Template cleanup — items specific to the template repo's own development
# ---------------------------------------------------------------------------
# These are files and directories that exist to support the template repo
# itself and are not useful to template users building their own project.
# Each entry includes a disclaimer about potential negative effects.

# Workflows to KEEP when the user selects "advanced-workflows" cleanup.
# These are the essential CI workflows most projects need.
ESSENTIAL_WORKFLOWS: set[str] = {
    "ci-gate.yml",
    "test.yml",
    "lint-format.yml",
    "type-check.yml",
    "coverage.yml",
    "security-audit.yml",
    "dependency-review.yml",
    "docs-build.yml",
}


def _discover_adr_paths() -> list[str]:
    """Dynamically discover ADR files and subdirectories in docs/adr/.

    Returns all numbered ADR markdown files (NNN-*.md) plus subdirectories
    like archive/. Excludes README.md and template.md so users keep those.
    """
    adr_dir = ROOT / "docs" / "adr"
    paths: list[str] = []
    if not adr_dir.is_dir():
        return paths
    for entry in sorted(adr_dir.iterdir()):
        rel = f"docs/adr/{entry.name}"
        if entry.is_dir():
            # Include subdirectories like archive/
            if entry.name not in {"__pycache__"}:
                paths.append(f"{rel}/")
        elif (
            entry.is_file()
            and entry.suffix == ".md"
            and re.match(r"^\d{3}-", entry.name)
        ):
            # Include numbered ADRs (NNN-*.md), skip README and template
            paths.append(rel)
    return paths


TEMPLATE_CLEANUP: dict[str, dict[str, object]] = {
    "adr-files": {
        "label": "ADR files (docs/adr/ — template design decisions)",
        "paths": _discover_adr_paths(),
        "disclaimer": (
            "⚠ Removes all numbered ADR files and subdirectories (e.g. archive/) "
            "from docs/adr/. Keeps README.md and template.md. These ADRs document "
            "decisions made for the TEMPLATE repository — why Ruff over Black, "
            "why src/ layout, why Hatch, etc. They do NOT describe decisions in "
            "YOUR project. Removing them deletes the rationale behind the tooling "
            "and patterns you inherited, which can make it harder for future "
            "contributors to understand why things are set up this way. Consider "
            "keeping them as reference until you've written your own ADRs."
        ),
    },
    "docs-notes": {
        "label": "Developer notes (docs/notes/ — learning, resources, TODOs, etc.)",
        "paths": ["docs/notes/"],
        "disclaimer": (
            "⚠ Removes the entire docs/notes/ directory, including: "
            "learning.md (Python packaging lessons, mental models for "
            "Hatch vs Hatchling, lockfile strategies), resources.md "
            "(curated links to official docs for every tool in the stack), "
            "tool-comparison.md (side-by-side evaluations of formatters, "
            "linters, type checkers, task runners, etc.), todo.md (roadmap "
            "and checklist of remaining template work), archive.md "
            "(completed items for historical context), and README.md. "
            "No project functionality depends on these files, but they "
            "contain valuable context — especially learning.md and "
            "resources.md — that can accelerate onboarding for developers "
            "unfamiliar with the tooling stack. Consider keeping them as "
            "reference material, or extracting useful content into your "
            "own docs before removing."
        ),
    },
    "docs-design": {
        "label": "Design docs (docs/design/ — architecture, tool decisions, CI/CD design, database, etc.)",
        "paths": ["docs/design/"],
        "disclaimer": (
            "⚠ Removes the entire docs/design/ directory, including: "
            "architecture.md, ci-cd-design.md, database.md, tool-decisions.md, "
            "and any future files added there. These document the 'why' behind "
            "CI/CD pipeline design, dependency choices, database schema rationale, "
            "and overall system architecture. The copilot-instructions.md file "
            "references these docs — Copilot will lose context for architectural "
            "questions. Contributors will have no written rationale for the "
            "project's structural decisions."
        ),
    },
    "docs-reference": {
        "label": "Reference docs (docs/reference/ — API, commands, inventory, etc.)",
        "paths": ["docs/reference/"],
        "disclaimer": (
            "⚠ Removes the entire docs/reference/ directory, including: "
            "api.md, commands.md, index.md, template-inventory.md, and "
            "README.md. The command reference is auto-generated by "
            "generate_command_reference.py and will need to be regenerated "
            "if you add new scripts. The template inventory is only useful "
            "during initial setup. The mkdocs-hooks/generate_commands.py "
            "hook will fail if docs/reference/ is missing — update "
            "mkdocs.yml nav and remove the hook if you strip this."
        ),
    },
    "docs-development": {
        "label": "Development guides (docs/development/ — dev setup, PR guide, command workflows, etc.)",
        "paths": ["docs/development/"],
        "disclaimer": (
            "⚠ Removes the entire docs/development/ directory, including: "
            "dev-setup.md, pull-requests.md, developer-commands.md, "
            "command-workflows.md, development.md, and README.md. These are "
            "developer onboarding docs covering environment setup, PR "
            "workflow, and available commands. Removing these makes it "
            "harder for new contributors to get started. mkdocs.yml nav "
            "links to these pages — update it to avoid broken links. "
            "Consider replacing with your own project-specific guides."
        ),
    },
    "docs-guide": {
        "label": "User guides (docs/guide/ — getting started, troubleshooting, etc.)",
        "paths": ["docs/guide/"],
        "disclaimer": (
            "⚠ Removes the entire docs/guide/ directory, including: "
            "getting-started.md, troubleshooting.md, and README.md. "
            "These provide end-user onboarding and common issue "
            "resolution. mkdocs.yml nav references these pages — update "
            "it to avoid broken links. Consider replacing with "
            "project-specific guides rather than deleting outright."
        ),
    },
    "placeholder-code": {
        "label": "Placeholder source & test files (clear src/ and tests/ content)",
        "paths": [],  # Handled specially — clears file content, not deletion
        "disclaimer": (
            "⚠ Replaces placeholder code in src/ modules (api.py, cli.py, "
            "engine.py, main.py) and test files (test_example.py) with "
            "minimal stubs. Also removes non-__init__.py files from the "
            "dev_tools/ subdirectory if present. Keeps the file structure "
            "so you can fill in your own code. __init__.py, _version.py, "
            "conftest.py, and py.typed are preserved as-is. Entry points "
            "in pyproject.toml still reference these files — update them "
            "if you rename or restructure."
        ),
    },
    "utility-scripts": {
        "label": "Template utility scripts (scripts/ — most helper scripts)",
        "paths": [
            "scripts/archive_todos.py",
            "scripts/changelog_check.py",
            "scripts/check_known_issues.py",
            "scripts/check_todos.py",
            "scripts/dep_versions.py",
            "scripts/generate_command_reference.py",
            "scripts/workflow_versions.py",
            "scripts/precommit/",
        ],
        "disclaimer": (
            "⚠ Removes 7 scripts and the precommit/ directory: "
            "archive_todos.py, changelog_check.py, check_known_issues.py, "
            "check_todos.py, dep_versions.py, generate_command_reference.py, "
            "workflow_versions.py, and scripts/precommit/. bootstrap.py, "
            "clean.py, and customize.py are kept. Removing these also "
            "means Taskfile tasks and pre-commit hooks that call them will "
            "break — update Taskfile.yml and .pre-commit-config.yaml "
            "accordingly. Some GitHub Actions workflows may also reference "
            "these scripts."
        ),
    },
    "advanced-workflows": {
        "label": "Advanced workflows (keep only essential CI subset)",
        "paths": [],  # Handled specially — deletes all except ESSENTIAL_WORKFLOWS
        # TODO (template users): Update the "~28" count in the disclaimer
        #   below if you add or remove workflow files in .github/workflows/.
        "disclaimer": (
            "⚠ Deletes ALL .yml files in .github/workflows/ EXCEPT the "
            "essential set: ci-gate, test, lint-format, type-check, coverage, "
            "security-audit, dependency-review, docs-build. This removes ~28 "
            "workflows including: release automation (release-please), "
            "container builds & scans, nightly security scans, Scorecard, "
            "SBOM generation, spellcheck, label management, welcome bot, "
            "stale issues, and more. You will lose significant CI/CD "
            "automation — including automated releases and container "
            "publishing. Non-.yml files (e.g. .instructions.md) are kept. "
            "You can re-add individual workflows from git history or the "
            ".github/workflows-optional/ directory."
        ),
    },
}

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# License templates
# ---------------------------------------------------------------------------

# TODO (template users): If your organization uses a different license
#   (e.g., GPL-3.0, MPL-2.0, proprietary), add it to LICENSE_CHOICES below
#   and provide a template string. The script will write it to LICENSE and
#   update the classifier in pyproject.toml.

MIT_LICENSE = """\
MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

BSD_3_LICENSE = """\
BSD 3-Clause License

Copyright (c) {year}, {author}

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

LICENSE_CHOICES: dict[str, dict[str, str | None]] = {
    "apache-2.0": {
        "name": "Apache License 2.0",
        "classifier": "License :: OSI Approved :: Apache Software License",
        "template": None,  # keep the existing LICENSE file
    },
    "mit": {
        "name": "MIT License",
        "classifier": "License :: OSI Approved :: MIT License",
        "template": MIT_LICENSE,
    },
    "bsd-3-clause": {
        "name": "BSD 3-Clause License",
        "classifier": "License :: OSI Approved :: BSD License",
        "template": BSD_3_LICENSE,
    },
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Config:
    """User-provided customization values collected via prompts or CLI."""

    project_name: str = ""
    package_name: str = ""
    author: str = ""
    github_user: str = ""
    description: str = ""
    cli_prefix: str = ""
    license_id: str = "apache-2.0"
    strip_dirs: list[str] = field(default_factory=list)
    template_cleanup: list[str] = field(default_factory=list)
    private_repo: bool = False
    dry_run: bool = False


@dataclass(frozen=True)
class Replacement:
    """A single text substitution to apply across the project."""

    old: str
    new: str
    description: str


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------


def _prompt(label: str, default: str = "") -> str:
    """Prompt the user for a text value, showing an optional default.

    Args:
        label: Prompt text.
        default: Value used when the user presses Enter.

    Returns:
        The user's input, or *default* if they pressed Enter.
    """
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            value = input(f"  {label}{suffix}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raise SystemExit(1) from None
        if value:
            return value
        if default:
            return default
        print("    (required — please enter a value)")


def _prompt_yn(label: str, *, default: bool = True) -> bool:
    """Prompt for yes/no.

    Args:
        label: Prompt text.
        default: Value used when the user presses Enter.

    Returns:
        ``True`` for yes, ``False`` for no.
    """
    hint = "Y/n" if default else "y/N"
    try:
        value = input(f"  {label} [{hint}]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(1) from None
    if not value:
        return default
    return value in ("y", "yes")


def _prompt_choice(label: str, choices: dict[str, str], default: str) -> str:
    """Prompt the user to pick one item from a numbered list.

    Args:
        label: Header text.
        choices: Mapping of key → display string.
        default: Key returned when the user presses Enter.

    Returns:
        The chosen key.
    """
    print(f"  {label}")
    keys = list(choices.keys())
    for i, key in enumerate(keys, 1):
        marker = " (default)" if key == default else ""
        print(f"    {i}. {choices[key]}{marker}")
    while True:
        try:
            raw = input(f"  Choice [1-{len(keys)}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raise SystemExit(1) from None
        if not raw:
            return default
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        except ValueError:
            if raw in keys:
                return raw
        print(f"    (enter a number 1-{len(keys)})")


def _prompt_multi(label: str, choices: dict[str, str]) -> list[str]:
    """Prompt the user to select zero or more items from a numbered list.

    Args:
        label: Header text.
        choices: Mapping of key → display string.

    Returns:
        List of selected keys (may be empty).
    """
    print(f"  {label}")
    keys = list(choices.keys())
    for i, key in enumerate(keys, 1):
        print(f"    {i}. {choices[key]}")
    all_idx = len(keys) + 1
    print(f"    {all_idx}. All of the above")
    print("    0. None of the above")
    try:
        raw = input("  Selection (comma-separated, e.g. 1,3): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(1) from None
    if not raw or raw == "0":
        return []
    # "All of the above" shortcut
    if raw.strip() == str(all_idx):
        return list(keys)
    selected: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if part == str(all_idx):
            return list(keys)
        try:
            idx = int(part) - 1
            if 0 <= idx < len(keys) and keys[idx] not in selected:
                selected.append(keys[idx])
        except ValueError:
            if part in keys and part not in selected:
                selected.append(part)
    return selected


# ---------------------------------------------------------------------------
# Interactive configuration
# ---------------------------------------------------------------------------


def _validate_project_name(name: str) -> str | None:
    """Return an error message if *name* is not a valid project slug."""
    if not re.match(r"^[a-z][a-z0-9]+(-[a-z0-9]+)*$", name):
        return (
            "Use lowercase letters, digits, and hyphens "
            "(e.g. my-cool-project). Must start with a letter "
            "and be at least 2 characters."
        )
    return None


# Common builtins that would cause subtle bugs if used as package names
_SHADOWED_BUILTINS: set[str] = {
    "list",
    "dict",
    "set",
    "type",
    "map",
    "filter",
    "input",
    "hash",
    "id",
    "open",
    "print",
    "format",
    "object",
    "property",
    "range",
    "slice",
    "super",
    "tuple",
    "bytes",
    "str",
    "int",
    "float",
    "bool",
    "complex",
}


def _validate_package_name(name: str) -> str | None:
    """Return an error message if *name* is not a valid Python package name.

    Checks for PEP 8 naming, minimum length, Python keywords, and
    names that shadow common builtins.
    """
    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        return (
            "Use lowercase letters, digits, and underscores "
            "(e.g. my_project). Must start with a letter."
        )
    if len(name) < 2:
        return "Package name must be at least 2 characters."
    if name.endswith("_"):
        return "Should not end with an underscore."
    if "__" in name:
        return "Avoid double underscores (reserved for Python internals)."
    if keyword.iskeyword(name) or keyword.issoftkeyword(name):
        return f"'{name}' is a Python keyword and cannot be used as a package name."
    if name in _SHADOWED_BUILTINS:
        return (
            f"'{name}' shadows a Python builtin. This will cause subtle "
            f"bugs when importing. Choose a more specific name."
        )
    return None


def gather_config_interactive() -> Config:
    """Run an interactive Q&A session and return a populated Config."""
    cfg = Config()
    c = Colors()
    sym = unicode_symbols()
    ui = UI(title="Customize", version=SCRIPT_VERSION, theme=THEME)

    ui.header()
    ui.blank()
    print(f"  {c.bold('Project Customization Wizard')}")
    print(f"  {c.dim('Replace boilerplate placeholders with your project values.')}")
    print(
        f"  {c.dim('Press Enter to accept [defaults]. Re-run with --dry-run to preview.')}"
    )

    # --- Project identity ---------------------------------------------------
    ui.section("Step 1/6 — Project Identity")
    while True:
        cfg.project_name = _prompt(
            "Project name (lowercase, hyphens OK, e.g. my-cool-app)"
        )
        err = _validate_project_name(cfg.project_name)
        if err is None:
            break
        print(f"    {c.red(sym['cross'])} Invalid: '{cfg.project_name}' — {err}")

    default_pkg = cfg.project_name.replace("-", "_")
    while True:
        cfg.package_name = _prompt(
            "Package name (Python import name, underscored)",
            default_pkg,
        )
        err = _validate_package_name(cfg.package_name)
        if err is None:
            break
        print(f"    {c.red(sym['cross'])} Invalid: '{cfg.package_name}' — {err}")

    cfg.author = _prompt("Author / maintainer name")
    cfg.github_user = _prompt("GitHub username or organization")
    cfg.description = _prompt(
        "One-line project description",
        f"{cfg.project_name} — a Python project",
    )

    # Derive CLI prefix from initials of hyphenated name
    parts = cfg.project_name.split("-")
    default_cli = (
        "".join(p[0] for p in parts if p) if len(parts) > 1 else cfg.project_name
    )
    cfg.cli_prefix = _prompt(
        "CLI command prefix (used for entry points like <prefix>-version)",
        default_cli,
    )

    # --- Private repo -------------------------------------------------------
    ui.section("Step 2/6 — Repository Visibility")
    ui.blank()
    print(f"  {c.dim('Private repos do not need open-source community files')}")
    print(f"  {c.dim('(CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, scorecard, etc.).')}")
    print(f"  {c.dim('Selecting this removes them automatically.')}")
    ui.blank()
    cfg.private_repo = _prompt_yn("Is this a private repository?", default=False)

    # --- License ------------------------------------------------------------
    ui.section("Step 3/6 — License")
    print()
    license_options = {k: str(v["name"]) for k, v in LICENSE_CHOICES.items()}
    cfg.license_id = _prompt_choice("Choose a license:", license_options, "apache-2.0")

    # --- Strip optional directories -----------------------------------------
    ui.section("Step 4/6 — Optional Directories")
    print()
    print(f"  {c.dim('These directories ship with the template but are optional.')}")
    print(
        f"  {c.dim('Select any you do not need — the files inside will be deleted.')}"
    )
    print(
        f"  {c.dim('You will be asked about removing now-empty parent directories.')}"
    )
    print()
    strip_options = {k: str(v["label"]) for k, v in STRIPPABLE.items()}
    cfg.strip_dirs = _prompt_multi("Remove any of these?", strip_options)

    # --- Template cleanup ---------------------------------------------------
    ui.section("Step 5/6 — Template Cleanup")
    print()
    print(f"  {c.dim('The items below exist to support the template repository.')}")
    print(f"  {c.dim('Most template users will not need them.')}")
    print()
    print(
        f"  {c.yellow(sym['warn'])} {c.yellow('Each item has trade-offs')} — after you make your selection,"
    )
    print("     a disclaimer will be shown and you will be asked to confirm.")
    print(f"     {c.dim('You can always recover files from git history.')}")
    print()
    cleanup_options: dict[str, str] = {}
    for key, entry in TEMPLATE_CLEANUP.items():
        cleanup_options[key] = str(entry["label"])
    selected_cleanup = _prompt_multi(
        "Clean up any template-specific items?", cleanup_options
    )

    # Show disclaimers for selected items and confirm
    if selected_cleanup:
        print()
        print(f"  {c.bold('Disclaimers for selected items:')}")
        for key in selected_cleanup:
            entry = TEMPLATE_CLEANUP[key]
            print(f"\n    {c.cyan(f'[{key}]')}")
            disclaimer = str(entry.get("disclaimer", ""))
            # Word-wrap disclaimer to ~60 chars with indent
            words = disclaimer.split()
            line = "      "
            for word in words:
                if len(line) + len(word) + 1 > 72:
                    print(c.dim(line))
                    line = "      " + word
                else:
                    line += (" " if line.strip() else "") + word
            if line.strip():
                print(c.dim(line))
        print()
        if not _prompt_yn("Proceed with these cleanup selections?"):
            print("  (skipping template cleanup)")
            selected_cleanup = []

    cfg.template_cleanup = selected_cleanup

    # --- Summary / confirm --------------------------------------------------
    ui.section("Step 6/6 — Review")

    return cfg


# ---------------------------------------------------------------------------
# Replacement planning
# ---------------------------------------------------------------------------


def plan_replacements(cfg: Config) -> list[Replacement]:
    """Build an ordered list of text substitutions from the config.

    Ordering matters: more-specific patterns (e.g. ``YOURNAME/YOURREPO``)
    are applied before their substrings to avoid partial replacements.

    Args:
        cfg: Populated customization config.

    Returns:
        Ordered list of :class:`Replacement` instances.
    """
    reps: list[Replacement] = []
    github_slug = f"{cfg.github_user}/{cfg.project_name}"

    # 1. GitHub URL placeholder (most specific — contains '/')
    reps.append(
        Replacement(
            old=TEMPLATE_GITHUB_URL_PLACEHOLDER,
            new=github_slug,
            description=f"GitHub URL placeholder -> {github_slug}",
        )
    )

    # 2. Project name (hyphenated)
    if cfg.project_name != TEMPLATE_PROJECT_NAME:
        reps.append(
            Replacement(
                old=TEMPLATE_PROJECT_NAME,
                new=cfg.project_name,
                description=f"Project name -> {cfg.project_name}",
            )
        )

    # 3. Package name (underscored)
    if cfg.package_name != TEMPLATE_PACKAGE_NAME:
        reps.append(
            Replacement(
                old=TEMPLATE_PACKAGE_NAME,
                new=cfg.package_name,
                description=f"Package name -> {cfg.package_name}",
            )
        )

    # 4. GitHub username (standalone occurrences in SECURITY.md, issue templates)
    reps.append(
        Replacement(
            old=TEMPLATE_GITHUB_USER,
            new=cfg.github_user,
            description=f"GitHub user -> {cfg.github_user}",
        )
    )

    # 5. Author (scoped to pyproject.toml authors field to avoid false positives)
    if cfg.author != TEMPLATE_AUTHOR:
        reps.append(
            Replacement(
                old=f'name = "{TEMPLATE_AUTHOR}"',
                new=f'name = "{cfg.author}"',
                description=f"Author -> {cfg.author}",
            )
        )

    # 6. Description
    if cfg.description != TEMPLATE_DESCRIPTION:
        reps.append(
            Replacement(
                old=TEMPLATE_DESCRIPTION,
                new=cfg.description,
                description=f"Description -> {cfg.description}",
            )
        )

    # 7. CLI entry-point prefix (compound names first to avoid partial match)
    if cfg.cli_prefix != TEMPLATE_CLI_PREFIX:
        reps.extend(
            Replacement(
                old=f"{TEMPLATE_CLI_PREFIX}{suffix}",
                new=f"{cfg.cli_prefix}{suffix}",
                description=f"CLI command -> {cfg.cli_prefix}{suffix}",
            )
            for suffix in ("-version", "-doctor")
        )
        reps.append(
            Replacement(
                old=f'{TEMPLATE_CLI_PREFIX} = "',
                new=f'{cfg.cli_prefix} = "',
                description=f"CLI base command -> {cfg.cli_prefix}",
            )
        )

    return reps


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------


def _should_process(path: Path) -> bool:
    """Return True if *path* is a text file we should scan for replacements."""
    if not path.is_file():
        return False
    if path.suffix not in TEXT_EXTENSIONS and path.name not in SCAN_FILENAMES:
        return False
    rel = path.relative_to(ROOT)
    # Exact directory name match
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    # Suffix-based directory match (e.g. .egg-info)
    if any(part.endswith(sfx) for part in rel.parts for sfx in SKIP_DIR_SUFFIXES):
        return False
    return rel not in SKIP_FILES


def _collect_eligible_files() -> list[Path]:
    """Gather all text files eligible for replacement scanning.

    Returns:
        Sorted list of file paths that pass the processing filter.
    """
    return sorted(p for p in ROOT.rglob("*") if _should_process(p))


def apply_replacements(
    replacements: list[Replacement],
    *,
    dry_run: bool = False,
    show_progress: bool = True,
) -> dict[Path, int]:
    """Apply text replacements across all eligible files in the project.

    Args:
        replacements: Ordered substitutions (applied in sequence per file).
        dry_run: If ``True``, report changes without writing files.
        show_progress: If ``True``, display a progress bar during processing.

    Returns:
        Mapping of modified file paths to number of individual substitutions.
    """
    eligible = _collect_eligible_files()
    modified: dict[Path, int] = {}

    bar: ProgressBar | None = None
    if show_progress and eligible:
        bar = ProgressBar(
            total=len(eligible),
            label="Scanning files",
            log_interval=20,
            color="cyan",
        )

    for path in eligible:
        rel = path.relative_to(ROOT)
        if bar is not None:
            bar.update(str(rel))

        try:
            original = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError):
            continue

        text = original
        count = 0
        for r in replacements:
            hits = text.count(r.old)
            if hits > 0:
                text = text.replace(r.old, r.new)
                count += hits

        if count > 0:
            modified[path] = count
            if not dry_run:
                path.write_text(text, encoding="utf-8")

    if bar is not None:
        total_subs = sum(modified.values())
        bar.finish(
            f"  Scanned {len(eligible)} files — "
            f"{total_subs} replacement{'s' if total_subs != 1 else ''} "
            f"in {len(modified)} file{'s' if len(modified) != 1 else ''}"
        )

    return modified


def rename_package_dir(cfg: Config, *, dry_run: bool = False) -> bool:
    """Rename ``src/simple_python_boilerplate/`` to the new package name.

    Also cleans up stale ``.egg-info`` if present.

    Args:
        cfg: Customization config.
        dry_run: If ``True``, report without renaming.

    Returns:
        ``True`` if a rename was performed (or would be in dry-run mode).
    """
    if cfg.package_name == TEMPLATE_PACKAGE_NAME:
        return False

    old_dir = ROOT / "src" / TEMPLATE_PACKAGE_NAME
    new_dir = ROOT / "src" / cfg.package_name

    if not old_dir.is_dir():
        log.warning("src/%s/ not found — skipping rename", TEMPLATE_PACKAGE_NAME)
        return False
    if new_dir.exists():
        log.warning("src/%s/ already exists — skipping rename", cfg.package_name)
        return False

    if dry_run:
        print(
            f"  Would rename: src/{TEMPLATE_PACKAGE_NAME}/ -> src/{cfg.package_name}/"
        )
    else:
        old_dir.rename(new_dir)
        print(f"  Renamed: src/{TEMPLATE_PACKAGE_NAME}/ -> src/{cfg.package_name}/")

    # Remove stale .egg-info (will be regenerated by pip install -e .)
    old_egg = ROOT / "src" / f"{TEMPLATE_PACKAGE_NAME}.egg-info"
    if old_egg.is_dir():
        if dry_run:
            print(f"  Would remove: src/{TEMPLATE_PACKAGE_NAME}.egg-info/")
        else:
            shutil.rmtree(old_egg)
            print(f"  Removed stale: src/{TEMPLATE_PACKAGE_NAME}.egg-info/")

    return True


def strip_directories(
    keys: list[str],
    *,
    dry_run: bool = False,
    strippable: dict[str, dict[str, object]] | None = None,
) -> list[str]:
    """Remove optional directories and files from the project.

    Separates files and directories, showing what will be removed
    with color-coded output and per-group labels.  After all removals,
    checks for newly-empty parent directories and offers to remove them.

    Args:
        keys: Keys from *strippable* identifying what to remove.
        dry_run: If ``True``, report without deleting.
        strippable: Registry to look up keys.  Defaults to :data:`STRIPPABLE`.

    Returns:
        Relative paths that were removed (or would be removed).
    """
    if strippable is None:
        strippable = STRIPPABLE

    c = Colors()
    sym = unicode_symbols()
    removed: list[str] = []
    # Track parent directories whose children were deleted so we can
    # offer to remove them if they become empty.
    affected_parents: set[Path] = set()

    for key in keys:
        entry = strippable.get(key)
        if entry is None:
            continue
        label = str(entry.get("label", key))
        paths: list[str] = entry["paths"]  # type: ignore[assignment]

        # Partition into existing dirs and files
        dirs: list[tuple[str, Path]] = []
        files: list[tuple[str, Path]] = []
        for rel_path in paths:
            target = ROOT / rel_path
            if not target.exists():
                continue
            if target.is_dir():
                dirs.append((rel_path, target))
            else:
                files.append((rel_path, target))

        if not dirs and not files:
            continue

        print(f"\n  {c.bold(c.cyan(f'[{key}]'))} {c.dim(label)}")

        for rel_path, target in dirs:
            removed.append(rel_path)
            if dry_run:
                print(
                    f"    {c.yellow(sym['arrow'])} Would remove directory: {c.yellow(rel_path)}"
                )
            else:
                try:
                    shutil.rmtree(target)
                    print(f"    {c.green(sym['check'])} Removed directory: {rel_path}")
                    affected_parents.add(target.parent)
                except (OSError, PermissionError) as exc:
                    log.warning(
                        "    %s Failed to remove %s: %s", sym["cross"], rel_path, exc
                    )

        for rel_path, target in files:
            removed.append(rel_path)
            if dry_run:
                print(
                    f"    {c.yellow(sym['arrow'])} Would remove file: {c.dim(rel_path)}"
                )
            else:
                try:
                    target.unlink()
                    print(f"    {c.green(sym['check'])} Removed file: {rel_path}")
                    affected_parents.add(target.parent)
                except (OSError, PermissionError) as exc:
                    log.warning(
                        "    %s Failed to remove %s: %s", sym["cross"], rel_path, exc
                    )

    # Offer to clean up empty parent directories
    _cleanup_empty_parents(affected_parents, dry_run=dry_run)

    return removed


def _cleanup_empty_parents(
    parents: set[Path],
    *,
    dry_run: bool = False,
) -> None:
    """Check affected parent directories and remove them if empty.

    Walks up toward ROOT (but never beyond it), removing directories
    that are now empty after file/subdirectory stripping.

    Args:
        parents: Set of parent directory paths to check.
        dry_run: If ``True``, report without deleting.
    """
    c = Colors()
    sym = unicode_symbols()
    cleaned: set[Path] = set()

    for parent in sorted(parents):
        current = parent
        while current != ROOT and current not in cleaned:
            if not current.is_dir():
                break
            # A directory is "empty" if it has no children at all
            children = list(current.iterdir())
            if children:
                break
            rel = current.relative_to(ROOT)
            if dry_run:
                print(
                    f"    {c.yellow(sym['arrow'])} Would remove empty directory: {c.dim(str(rel) + '/')}"
                )
            else:
                try:
                    current.rmdir()
                    print(
                        f"    {c.green(sym['check'])} Removed empty directory: {rel!s}/"
                    )
                except OSError:
                    break
            cleaned.add(current)
            current = current.parent


# ---------------------------------------------------------------------------
# Placeholder file stubs
# ---------------------------------------------------------------------------

# Minimal stub content for src/ placeholder files. These replace the full
# boilerplate examples so template users start with a clean slate but keep
# the file structure as a guide.

_STUB_API = '''\
"""HTTP/REST API interface.

TODO (template users): Implement your API endpoints here.
"""

from typing import Any


def create_app() -> Any:
    """Create and configure the API application.

    Returns:
        Configured application instance.
    """
    raise NotImplementedError("Implement your API framework setup here")
'''

_STUB_CLI = '''\
"""Command-line interface definitions and argument parsing.

TODO (template users): Define your CLI commands and arguments here.
"""

import argparse
from collections.abc import Sequence


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="TODO: describe your project",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    return create_parser().parse_args(argv)


def run(args: argparse.Namespace) -> int:
    """Execute the CLI command.

    Args:
        args: Parsed arguments.

    Returns:
        Exit code (0 for success).
    """
    return 0
'''

_STUB_ENGINE = '''\
"""Core business logic and processing engine.

TODO (template users): Implement your domain logic here.
"""


def process() -> None:
    """Main processing function.

    TODO: Replace with your core logic.
    """
    raise NotImplementedError("Implement your business logic here")
'''

_STUB_MAIN = '''\
"""Application entry points (thin wrappers).

Entry points configured in pyproject.toml. These should be thin
wrappers that delegate to cli.py for argument parsing and engine.py
for logic.

TODO (template users): Update entry points to match your project.
"""

import sys


def main() -> None:
    """Main CLI entry point."""
    from {package_name} import cli

    sys.exit(cli.run(cli.parse_args()))
'''

_STUB_TEST = '''\
"""Unit tests.

TODO (template users): Replace with tests for your code.
"""


def test_placeholder() -> None:
    """Placeholder test — replace with real tests."""
    assert True
'''

# Map of src/ files to their stub content (relative to the package dir)
_SRC_STUBS: dict[str, str] = {
    "api.py": _STUB_API,
    "cli.py": _STUB_CLI,
    "engine.py": _STUB_ENGINE,
    "main.py": _STUB_MAIN,
}

# Files in src/ to never touch during placeholder cleanup
_SRC_PRESERVE: set[str] = {
    "__init__.py",
    "_version.py",
    "py.typed",
}

# Test files to stub out (relative to tests/)
_TEST_STUB_PATTERNS: set[str] = {
    "test_example.py",
}


def apply_template_cleanup(
    keys: list[str],
    cfg: Config,
    *,
    dry_run: bool = False,
) -> list[str]:
    """Execute template cleanup operations.

    Handles both file/directory deletion and special operations like
    clearing placeholder code and trimming workflows.

    Args:
        keys: Keys from :data:`TEMPLATE_CLEANUP` identifying what to clean.
        cfg: Config with package_name for stub generation.
        dry_run: If ``True``, report without modifying.

    Returns:
        List of descriptions of actions taken.
    """
    actions: list[str] = []
    c = Colors()
    sym = unicode_symbols()

    for key in keys:
        entry = TEMPLATE_CLEANUP.get(key)
        if entry is None:
            continue

        # Special handling: placeholder code
        if key == "placeholder-code":
            actions.extend(_cleanup_placeholder_code(cfg.package_name, dry_run=dry_run))
            continue

        # Special handling: advanced workflows
        if key == "advanced-workflows":
            actions.extend(_cleanup_advanced_workflows(dry_run=dry_run))
            continue

        # Standard path-based deletion
        label = str(entry.get("label", key))
        paths: list[str] = entry["paths"]  # type: ignore[assignment]

        existing = [(p, ROOT / p) for p in paths if (ROOT / p).exists()]
        if existing:
            print(f"\n  {c.bold(c.cyan(f'[{key}]'))} {c.dim(label)}")

        for rel_path, target in existing:
            if dry_run:
                kind = "directory" if target.is_dir() else "file"
                print(
                    f"    {c.yellow(sym['arrow'])} Would remove {kind}: {c.yellow(rel_path)}"
                )
            else:
                try:
                    if target.is_dir():
                        shutil.rmtree(target)
                        print(
                            f"    {c.green(sym['check'])} Removed directory: {rel_path}"
                        )
                    else:
                        target.unlink()
                        print(f"    {c.green(sym['check'])} Removed file: {rel_path}")
                except (OSError, PermissionError) as exc:
                    log.warning(
                        "    %s Failed to remove %s: %s", sym["cross"], rel_path, exc
                    )
            actions.append(f"Removed: {rel_path}")

    return actions


def _cleanup_placeholder_code(
    package_name: str,
    *,
    dry_run: bool = False,
) -> list[str]:
    """Replace placeholder source and test files with minimal stubs.

    Preserves file structure, __init__.py, _version.py, and conftest.py.

    Args:
        package_name: The (possibly renamed) package name.
        dry_run: If ``True``, report without modifying.

    Returns:
        List of action descriptions.
    """
    actions: list[str] = []

    # Determine the actual package directory (may have been renamed already)
    pkg_dir = ROOT / "src" / package_name
    if not pkg_dir.is_dir():
        # Fall back to template name if not renamed yet
        pkg_dir = ROOT / "src" / TEMPLATE_PACKAGE_NAME

    if pkg_dir.is_dir():
        for filename, stub in _SRC_STUBS.items():
            target = pkg_dir / filename
            if not target.is_file():
                continue
            content = stub.format(package_name=package_name)
            if dry_run:
                print(f"  Would replace with stub: src/{pkg_dir.name}/{filename}")
            else:
                target.write_text(content, encoding="utf-8")
                print(f"  Replaced with stub: src/{pkg_dir.name}/{filename}")
            actions.append(f"Stubbed: src/{pkg_dir.name}/{filename}")

        # Clear dev_tools/ contents but keep __init__.py
        dev_tools = pkg_dir / "dev_tools"
        if dev_tools.is_dir():
            for child in dev_tools.iterdir():
                if child.name == "__init__.py":
                    continue
                if dry_run:
                    print(f"  Would remove: src/{pkg_dir.name}/dev_tools/{child.name}")
                else:
                    if child.is_dir():
                        shutil.rmtree(child)
                    else:
                        child.unlink()
                    print(f"  Removed: src/{pkg_dir.name}/dev_tools/{child.name}")
                actions.append(f"Removed: src/{pkg_dir.name}/dev_tools/{child.name}")

    # Stub out test files
    tests_dir = ROOT / "tests"
    if tests_dir.is_dir():
        for test_file in tests_dir.rglob("test_*.py"):
            rel = test_file.relative_to(ROOT)
            # Only stub the example/placeholder test files;
            # keep script-specific tests since those test real functionality
            if test_file.name in _TEST_STUB_PATTERNS:
                if dry_run:
                    print(f"  Would replace with stub: {rel}")
                else:
                    test_file.write_text(_STUB_TEST, encoding="utf-8")
                    print(f"  Replaced with stub: {rel}")
                actions.append(f"Stubbed: {rel}")

    return actions


def _cleanup_advanced_workflows(*, dry_run: bool = False) -> list[str]:
    """Remove non-essential workflows, keeping only the core CI set.

    Keeps workflows listed in :data:`ESSENTIAL_WORKFLOWS`.

    Args:
        dry_run: If ``True``, report without deleting.

    Returns:
        List of action descriptions.
    """
    actions: list[str] = []
    workflows_dir = ROOT / ".github" / "workflows"

    if not workflows_dir.is_dir():
        return actions

    for wf in sorted(workflows_dir.iterdir()):
        if not wf.is_file() or wf.suffix != ".yml":
            continue
        if wf.name in ESSENTIAL_WORKFLOWS:
            continue
        rel = f".github/workflows/{wf.name}"
        if dry_run:
            print(f"  Would remove workflow: {rel}")
        else:
            try:
                wf.unlink()
                print(f"  Removed workflow: {rel}")
            except (OSError, PermissionError) as exc:
                log.warning("  Failed to remove %s: %s", rel, exc)
        actions.append(f"Removed: {rel}")

    return actions


def apply_license(cfg: Config, *, dry_run: bool = False) -> bool:
    """Write the chosen license file and update the pyproject.toml classifier.

    Args:
        cfg: Config with ``license_id`` and ``author`` set.
        dry_run: If ``True``, report without writing.

    Returns:
        ``True`` if the license was changed (or would be).
    """
    choice = LICENSE_CHOICES.get(cfg.license_id)
    if choice is None:
        return False

    template_text: str | None = choice["template"]
    new_classifier: str = choice["classifier"]  # type: ignore[assignment]
    old_classifier: str = LICENSE_CHOICES["apache-2.0"]["classifier"]  # type: ignore[assignment]
    changed = False

    # Replace the LICENSE file if a new template was selected
    license_path = ROOT / "LICENSE"
    if template_text is not None:
        year = datetime.datetime.now(tz=datetime.UTC).year
        content = template_text.format(year=year, author=cfg.author)
        if dry_run:
            print(f"  Would replace LICENSE with {choice['name']}")
        else:
            license_path.write_text(content, encoding="utf-8")
            print(f"  Replaced LICENSE with {choice['name']}")
        changed = True

    # Update the license classifier in pyproject.toml
    if new_classifier != old_classifier:
        pyproject = ROOT / "pyproject.toml"
        if pyproject.is_file():
            text = pyproject.read_text(encoding="utf-8")
            if old_classifier in text:
                if dry_run:
                    print("  Would update license classifier in pyproject.toml")
                else:
                    text = text.replace(old_classifier, new_classifier)
                    pyproject.write_text(text, encoding="utf-8")
                    print("  Updated license classifier in pyproject.toml")
                changed = True

    return changed


# ---------------------------------------------------------------------------
# Safety check
# ---------------------------------------------------------------------------


def _already_customized() -> bool:
    """Heuristic: return ``True`` if the template appears already customized."""
    pkg_dir = ROOT / "src" / TEMPLATE_PACKAGE_NAME
    if not pkg_dir.is_dir():
        return True

    pyproject = ROOT / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8", errors="ignore")
        if f'name = "{TEMPLATE_PROJECT_NAME}"' not in text:
            return True

    return False


# ---------------------------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------------------------


def print_plan(cfg: Config, replacements: list[Replacement]) -> None:
    """Print a human-readable summary of planned changes for confirmation.

    Args:
        cfg: Customization config.
        replacements: Planned text substitutions.
    """
    c = Colors()
    sym = unicode_symbols()
    ui = UI(title="Customize", version=SCRIPT_VERSION, theme=THEME)

    ui.section("Customization Plan")

    # Count eligible files upfront for context
    eligible_count = len(_collect_eligible_files())

    print(
        f"\n  {c.bold('Text replacements')} "
        f"{c.dim(f'({len(replacements)} rules, ~{eligible_count} files to scan)')}"
    )
    for r in replacements:
        print(f"    {c.cyan(sym['bullet'])} {r.description}")

    if cfg.package_name != TEMPLATE_PACKAGE_NAME:
        print(f"\n  {c.bold('Directory rename:')}")
        print(
            f"    {c.cyan(sym['arrow'])} src/{TEMPLATE_PACKAGE_NAME}/ {sym['arrow']} src/{cfg.package_name}/"
        )

    if cfg.license_id != "apache-2.0":
        name = LICENSE_CHOICES[cfg.license_id]["name"]
        print(f"\n  {c.bold('License:')} switch to {c.cyan(str(name))}")
    else:
        print(f"\n  {c.bold('License:')} {c.dim('keeping Apache-2.0 (no change)')}")

    if cfg.strip_dirs:
        print(f"\n  {c.bold('Directories to remove:')}")
        for key in cfg.strip_dirs:
            entry = STRIPPABLE[key]
            print(f"    {c.cyan(sym['bullet'])} {entry['label']}")
            paths: list[str] = entry["paths"]  # type: ignore[assignment]
            for p in paths:
                exists = (ROOT / p).exists()
                marker = "" if exists else c.dim(" (not found — skipped)")
                print(f"        {p}{marker}")
        print(
            f"    {c.dim('Empty parent directories will be cleaned up automatically.')}"
        )
    else:
        print(f"\n  {c.bold('Directories to remove:')} {c.dim('none')}")

    if cfg.private_repo:
        print(f"\n  {c.bold('Private repo cleanup:')}")
        for entry in PRIVATE_REPO_STRIP.values():
            print(f"    {c.cyan(sym['bullet'])} {entry['label']}")
            priv_paths: list[str] = entry["paths"]  # type: ignore[assignment]
            for p in priv_paths:
                exists = (ROOT / p).exists()
                marker = "" if exists else c.dim(" (not found — skipped)")
                print(f"        {p}{marker}")
    else:
        print(f"\n  {c.bold('Private repo cleanup:')} {c.dim('no (public repo)')}")

    if cfg.template_cleanup:
        print(f"\n  {c.bold('Template cleanup:')}")
        for key in cfg.template_cleanup:
            entry = TEMPLATE_CLEANUP[key]
            print(f"    {c.cyan(sym['bullet'])} {entry['label']}")
            if key == "placeholder-code":
                print(
                    f"        {c.dim('(Replace src/ and test placeholders with stubs)')}"
                )
            elif key == "advanced-workflows":
                kept = ", ".join(sorted(ESSENTIAL_WORKFLOWS))
                print(f"        {c.dim(f'(Keep only: {kept})')}")
            else:
                cleanup_paths: list[str] = entry["paths"]  # type: ignore[assignment]
                for p in cleanup_paths:
                    exists = (ROOT / p).exists()
                    marker = "" if exists else c.dim(" (not found — skipped)")
                    print(f"        {p}{marker}")
    else:
        print(f"\n  {c.bold('Template cleanup:')} {c.dim('none')}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Interactive project customization — replaces boilerplate "
            "placeholders with your project's values."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  python scripts/customize.py
  python scripts/customize.py --dry-run
  python scripts/customize.py --non-interactive \\
      --project-name my-project --author "Jane Doe" \\
      --github-user janedoe
""",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without modifying any files",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress informational output (errors still shown)",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Skip interactive prompts; use CLI arguments for all values",
    )
    parser.add_argument("--project-name", help="Project name (lowercase-hyphenated)")
    parser.add_argument(
        "--package-name",
        help="Python package name (underscored; auto-derived from --project-name if omitted)",
    )
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--github-user", help="GitHub username or organization")
    parser.add_argument("--description", help="One-line project description")
    parser.add_argument(
        "--cli-prefix",
        help="CLI command prefix (default: initials of project name)",
    )
    parser.add_argument(
        "--license",
        choices=list(LICENSE_CHOICES.keys()),
        default="apache-2.0",
        dest="license_id",
        help="License to use (default: apache-2.0)",
    )
    parser.add_argument(
        "--strip",
        nargs="*",
        choices=list(STRIPPABLE.keys()),
        default=[],
        metavar="DIR",
        help=(
            f"Optional directories to remove. Choices: {', '.join(STRIPPABLE.keys())}"
        ),
    )
    parser.add_argument(
        "--template-cleanup",
        nargs="*",
        choices=list(TEMPLATE_CLEANUP.keys()),
        default=[],
        metavar="ITEM",
        help=(
            "Template-specific items to clean up. "
            f"Choices: {', '.join(TEMPLATE_CLEANUP.keys())}"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip the already-customized safety check",
    )
    parser.add_argument(
        "--private-repo",
        action="store_true",
        help=(
            "Strip open-source community files not needed for private repos "
            "(CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, scorecard workflow, etc.)"
        ),
    )
    parser.add_argument(
        "--enable-workflows",
        metavar="OWNER/REPO",
        help=(
            "Enable all GitHub workflows by replacing 'YOURNAME/YOURREPO' placeholder. "
            "Pass your repo slug (e.g. 'myorg/myproject'). Runs only this operation."
        ),
    )
    return parser.parse_args(argv)


def config_from_args(args: argparse.Namespace) -> Config:
    """Build a :class:`Config` from parsed CLI arguments (non-interactive).

    Args:
        args: Parsed CLI arguments.

    Returns:
        Populated Config instance.

    Raises:
        SystemExit: If required arguments are missing.
    """
    missing: list[str] = []
    if not args.project_name:
        missing.append("--project-name")
    if not args.author:
        missing.append("--author")
    if not args.github_user:
        missing.append("--github-user")

    if missing:
        log.error("--non-interactive requires: %s", ", ".join(missing))
        raise SystemExit(2)

    # Validate project name
    name_err = _validate_project_name(args.project_name)
    if name_err:
        log.error("Invalid --project-name '%s': %s", args.project_name, name_err)
        raise SystemExit(2)

    package_name = args.package_name or args.project_name.replace("-", "_")

    # Validate package name
    pkg_err = _validate_package_name(package_name)
    if pkg_err:
        log.error("Invalid package name '%s': %s", package_name, pkg_err)
        raise SystemExit(2)

    parts = args.project_name.split("-")
    cli_prefix = args.cli_prefix or (
        "".join(p[0] for p in parts if p) if len(parts) > 1 else args.project_name
    )
    description = args.description or f"{args.project_name} — a Python project"

    return Config(
        project_name=args.project_name,
        package_name=package_name,
        author=args.author,
        github_user=args.github_user,
        description=description,
        cli_prefix=cli_prefix,
        license_id=args.license_id,
        strip_dirs=args.strip or [],
        template_cleanup=args.template_cleanup or [],
        private_repo=args.private_repo,
        dry_run=args.dry_run,
    )


# ---------------------------------------------------------------------------
# Enable Workflows Only
# ---------------------------------------------------------------------------


def enable_workflows_only(repo_slug: str, *, dry_run: bool = False) -> int:
    """Enable all workflows by replacing the YOURNAME/YOURREPO placeholder.

    This is a quick operation that only touches workflow files and related docs.

    Args:
        repo_slug: The GitHub repository slug (e.g., 'myorg/myproject').
        dry_run: If True, show what would change without modifying files.

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    # Validate slug format
    if "/" not in repo_slug or repo_slug.count("/") != 1:
        log.error("Invalid repo slug '%s'. Expected 'owner/repo' format.", repo_slug)
        return 1

    owner, repo = repo_slug.split("/")
    if not owner or not repo:
        log.error(
            "Invalid repo slug '%s'. Both owner and repo are required.", repo_slug
        )
        return 1

    replacements = [
        Replacement(
            old=TEMPLATE_GITHUB_URL_PLACEHOLDER,
            new=repo_slug,
            description=f"GitHub URL placeholder -> {repo_slug}",
        ),
    ]

    tag = "DRY RUN — " if dry_run else ""
    print(f"{tag}Enabling workflows with repo slug: {repo_slug}")
    print()

    modified = apply_replacements(replacements, dry_run=dry_run, show_progress=True)

    c = Colors()
    sym = unicode_symbols()

    if not modified:
        print(
            f"{c.green(sym['check'])} No files needed updating (placeholder may already be replaced)."
        )
        return 0

    # Show individual file results
    for path, count in modified.items():
        rel = path.relative_to(ROOT)
        print(f"  {rel} ({count} replacement{'s' if count != 1 else ''})")

    total = sum(modified.values())
    n_files = len(modified)
    print(
        f"\nTotal: {total} replacement{'s' if total != 1 else ''}"
        f" in {n_files} file{'s' if n_files != 1 else ''}"
    )

    if dry_run:
        print(f"\n{c.yellow('Dry run complete')} — no files were modified.")
        print(f"{c.dim('Re-run without --dry-run to apply.')}")
    else:
        print(
            f"\n{c.green(sym['check'])} {c.bold('Workflows enabled!')} They will now run on your repository."
        )
        print(f"\nNext step: push to GitHub and check the {c.cyan('Actions')} tab.")

    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point for the customize script.

    Returns:
        Exit code: 0 on success, 1 on abort or error.
    """
    args = parse_args()

    # Configure logging: --quiet suppresses INFO, errors always shown
    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)

    # Handle --enable-workflows as a standalone operation
    if args.enable_workflows:
        return enable_workflows_only(args.enable_workflows, dry_run=args.dry_run)

    # Safety check: warn if the template appears already customized
    if not args.force and _already_customized():
        log.warning(
            "This project appears to have already been customized "
            "(src/%s/ is missing or pyproject.toml has been modified).",
            TEMPLATE_PACKAGE_NAME,
        )
        if args.non_interactive:
            log.error("Use --force to run anyway.")
            return 1
        if not _prompt_yn("Run anyway?", default=False):
            print("Aborted.")
            return 0

    # Gather configuration
    if args.non_interactive:
        cfg = config_from_args(args)
    else:
        cfg = gather_config_interactive()

    cfg.dry_run = args.dry_run

    # Plan and show
    replacements = plan_replacements(cfg)
    print_plan(cfg, replacements)

    # Confirm (interactive only, skip for dry-run since it's non-destructive)
    if not args.non_interactive and not cfg.dry_run:
        c = Colors()
        sym = unicode_symbols()
        print(
            f"  {c.yellow(sym['warn'])} {c.yellow('This will modify files in-place.')} Make sure you have a"
        )
        print("     clean git state or a backup before proceeding.")
        print()
        if not _prompt_yn("Proceed with these changes?"):
            print("Aborted.")
            return 0

    c = Colors()
    sym = unicode_symbols()
    tag = f"{c.yellow('DRY RUN')} — " if cfg.dry_run else ""

    # Step 1: Strip optional directories (before rename so paths still match)
    if cfg.strip_dirs:
        print(f"\n{tag}Stripping optional directories...")
        strip_directories(cfg.strip_dirs, dry_run=cfg.dry_run)

    # Step 1b: Private repo cleanup
    if cfg.private_repo:
        print(f"\n{tag}Stripping open-source community files (private repo)...")
        strip_directories(
            list(PRIVATE_REPO_STRIP.keys()),
            dry_run=cfg.dry_run,
            strippable=PRIVATE_REPO_STRIP,
        )

    # Step 2: Text replacements across all files
    print(f"\n{tag}Applying text replacements...")
    modified = apply_replacements(
        replacements,
        dry_run=cfg.dry_run,
        show_progress=not args.quiet,
    )
    if cfg.dry_run:
        # In dry-run mode, list every affected file for review
        for path, count in modified.items():
            rel = path.relative_to(ROOT)
            print(f"  {rel} ({count} replacement{'s' if count != 1 else ''})")
    total = sum(modified.values())
    n_files = len(modified)
    print(
        f"  Total: {total} replacement{'s' if total != 1 else ''}"
        f" in {n_files} file{'s' if n_files != 1 else ''}"
    )

    # Step 3: Rename package directory
    print(f"\n{tag}Package directory...")
    if not rename_package_dir(cfg, dry_run=cfg.dry_run):
        print("  (no rename needed)")

    # Step 4: License
    print(f"\n{tag}License...")
    if not apply_license(cfg, dry_run=cfg.dry_run):
        print("  (keeping Apache-2.0)")

    # Step 5: Template cleanup
    if cfg.template_cleanup:
        print(f"\n{tag}Template cleanup...")
        apply_template_cleanup(cfg.template_cleanup, cfg, dry_run=cfg.dry_run)
    else:
        print(f"\n{tag}Template cleanup: none")

    # Done
    if cfg.dry_run:
        print()
        print(f"  {c.dim('─' * 50)}")
        print(f"  {c.yellow('Dry run complete')} — no files were modified.")
        print(f"  {c.dim('Re-run without --dry-run to apply changes.')}")
    else:
        print()
        print(f"  {c.dim('─' * 50)}")
        print(f"  {c.green(sym['check'])} {c.bold(c.green('Customization complete!'))}")
        ws_file = ROOT / f"{TEMPLATE_PROJECT_NAME}.code-workspace"
        print(f"\n  {c.bold('Next steps:')}")
        print(f"  1. Review the changes:  {c.cyan('git diff')}")
        reinstall_cmd = "pip install -e '.[dev]'"
        print(f"  2. Reinstall:           {c.cyan(reinstall_cmd)}")
        print(f"  3. Run tests:           {c.cyan('task test')}  (or pytest)")
        verify_cmd = f'python -c "import {cfg.package_name}"'
        print(f"  4. Verify import:       {c.cyan(verify_cmd)}")
        if ws_file.exists():
            print(
                f"  5. Rename workspace:    {TEMPLATE_PROJECT_NAME}.code-workspace"
                f" {sym['arrow']} {c.cyan(f'{cfg.project_name}.code-workspace')}"
            )
        # TODO (template users): Add any project-specific post-customization
        #   steps here (e.g., "6. Configure your database connection",
        #   "7. Set up your .env file").

    # Recommended scripts
    if not args.quiet:
        ui = UI(title="Customize", version=SCRIPT_VERSION, theme=THEME)
        ui.recommended_scripts(
            ["bootstrap", "doctor", "repo_sauron", "clean"],
            preamble="Scripts that help after customization.",
        )
        ui.blank()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
