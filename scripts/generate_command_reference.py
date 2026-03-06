#!/usr/bin/env python3
"""Generate the command reference page for MkDocs.

Collects usage information from three sources and writes a single
Markdown file (``docs/reference/commands.md``) that serves as a
comprehensive, auto-generated command dashboard.

Sources:
    1. **Taskfile.yml** — parsed for task names and descriptions
    2. **scripts/*.py** — each script is invoked with ``--help`` to
       capture its full usage text
    3. **Hatch environments** — ``hatch env show`` output is captured

The generated page is designed to be committed to the repo so that
MkDocs can serve it without running the generator at build time.
Re-run this script whenever scripts or tasks change.

.. note::

    The ``mkdocs-hooks/generate_commands.py`` MkDocs hook calls
    ``_generate()`` automatically during ``mkdocs build`` and
    ``mkdocs serve``, so the command reference is always fresh when
    building docs. This script is still useful for:

    - ``--check`` mode in CI (detect stale committed files)
    - ``--dry-run`` to preview output
    - Manual regeneration outside of mkdocs

Requirements:
    - Python 3.11+
    - ``task`` (go-task) CLI installed (for Taskfile parsing)
    - ``hatch`` CLI installed (for environment listing)
    - Scripts must be importable from the project root (for ``--help``)

Usage::

    python scripts/generate_command_reference.py          # Generate docs/reference/commands.md
    python scripts/generate_command_reference.py --check   # Exit 1 if the file is stale
    python scripts/generate_command_reference.py --dry-run  # Print to stdout instead of writing
    python scripts/generate_command_reference.py --version  # Print version

Flags::

    --check      Compare generated output with existing file; exit 1 if stale
    --dry-run    Print generated Markdown to stdout instead of writing to disk
    --version    Print script version and exit
"""

from __future__ import annotations

import argparse
import ast
import logging
import re
import subprocess  # nosec B404
import sys
from pathlib import Path

from _imports import find_repo_root

SCRIPT_VERSION = "1.2.0"

logger = logging.getLogger(__name__)

ROOT = find_repo_root()
SCRIPTS_DIR = ROOT / "scripts"
PRECOMMIT_DIR = SCRIPTS_DIR / "precommit"
TASKFILE = ROOT / "Taskfile.yml"
OUTPUT = ROOT / "docs" / "reference" / "commands.md"

# Scripts to skip (not user-facing CLIs).
# Note: scripts starting with '_' are already excluded by _collect_scripts().
# This set is for explicitly skipping scripts that don't start with '_'
# but still aren't user-facing CLIs.
# TODO (template users): Add any non-CLI scripts you create here.
_SKIP_SCRIPTS = {
    "__init__.py",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _escape_md_brackets(text: str) -> str:
    """Escape square brackets in text to prevent Markdown link interpretation."""
    return text.replace("[", "\\[").replace("]", "\\]")


def _extract_module_description(path: Path) -> str:
    """Extract the first line of a Python module's docstring.

    Uses ``ast.parse`` to reliably read the module-level docstring,
    falling back to a placeholder if the file can't be parsed or has
    no docstring.
    """
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return "*(no description)*"

    docstring = ast.get_docstring(tree)
    if docstring:
        first_line = docstring.strip().split("\n")[0].strip()
        if first_line:
            return first_line.rstrip(".")
    return "*(no description)*"


def _run(cmd: list[str], *, timeout: int = 30) -> str | None:
    """Run a command and return stdout, or None on failure."""
    try:
        result = subprocess.run(  # nosec B603
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ROOT),
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def _run_combined(cmd: list[str], *, timeout: int = 30) -> str | None:
    """Run a command and return stdout+stderr combined, or None on failure."""
    try:
        result = subprocess.run(  # nosec B603
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ROOT),
        )
        # Some tools (like argparse) print help to stderr on error,
        # and some print to stdout. Combine both.
        combined = (result.stdout + "\n" + result.stderr).strip()
        return combined if combined else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


# ---------------------------------------------------------------------------
# Taskfile tasks
# ---------------------------------------------------------------------------


def _parse_taskfile_tasks() -> list[tuple[str, str]]:
    """Parse Taskfile.yml for task names and descriptions.

    Returns a list of ``(task_name, description)`` tuples, sorted by name.
    Uses ``task --list`` for reliable output.
    """
    output = _run(["task", "--list"])
    if not output:
        logger.warning("Could not run 'task --list' — is go-task installed?")
        return []

    tasks: list[tuple[str, str]] = []
    for line in output.splitlines():
        # task --list outputs: "* task_name: description"
        m = re.match(r"\*\s+(\S+):\s+(.*)", line.strip())
        if m:
            tasks.append((m.group(1), m.group(2).strip()))
    return sorted(tasks)


# ---------------------------------------------------------------------------
# Script --help capture
# ---------------------------------------------------------------------------


def _script_help(script_path: Path) -> str | None:
    """Run ``python script --help`` and return the output."""
    return _run_combined(
        [sys.executable, str(script_path), "--help"],
        timeout=15,
    )


def _collect_scripts() -> list[Path]:
    """Return all user-facing .py scripts, sorted alphabetically.

    Scripts whose name starts with ``_`` or matches ``_SKIP_SCRIPTS``
    are excluded (they are shared modules, not CLIs).
    """
    scripts: list[Path] = [
        p
        for p in sorted(SCRIPTS_DIR.glob("*.py"))
        if p.name not in _SKIP_SCRIPTS and not p.name.startswith("_")
    ]

    # scripts/precommit/
    if PRECOMMIT_DIR.is_dir():
        scripts.extend(
            p for p in sorted(PRECOMMIT_DIR.glob("*.py")) if p.name not in _SKIP_SCRIPTS
        )

    return scripts


# ---------------------------------------------------------------------------
# Hatch environments
# ---------------------------------------------------------------------------


def _hatch_env_show() -> str | None:
    """Capture ``hatch env show`` output."""
    return _run(["hatch", "env", "show"], timeout=30)


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

_HEADER = """\
<!-- DO NOT EDIT — generated by scripts/generate_command_reference.py -->
<!-- Re-generate with: python scripts/generate_command_reference.py -->
<!-- This is a point-in-time snapshot. Run the generator before mkdocs build/deploy. -->

# Command Reference

Comprehensive reference of every command available in this project.
Auto-generated from Taskfile definitions, script `--help` output, and
Hatch environment configuration.

!!! tip "Quick start"
    Most developers only need `task check` (run all quality gates) and
    `task test` (run tests). See [Developer Commands](../development/developer-commands.md)
    for a guided walkthrough.

"""


def _generate() -> str:
    """Build the full Markdown content."""
    parts: list[str] = [_HEADER]

    # ── Taskfile tasks ────────────────────────────────────────
    parts.append("## Taskfile Commands\n\n")
    parts.append(
        "Run any task with `task <name>`. "
        "Pass extra arguments with `-- <args>` (e.g., `task test -- -v`).\n\n"
    )

    tasks = _parse_taskfile_tasks()
    if tasks:
        # Group tasks by prefix (before the colon)
        groups: dict[str, list[tuple[str, str]]] = {}
        for name, desc in tasks:
            prefix = name.split(":")[0] if ":" in name else "_top"
            groups.setdefault(prefix, []).append((name, desc))

        for group_key in sorted(groups):
            group_tasks = groups[group_key]
            label = group_key if group_key != "_top" else "General"
            parts.append(f"### {label.title()}\n\n")
            parts.append("| Command | Description |\n")
            parts.append("| ------- | ----------- |\n")
            for name, desc in group_tasks:
                parts.append(f"| `task {name}` | {_escape_md_brackets(desc)} |\n")
            parts.append("\n")
    else:
        parts.append("*Could not parse Taskfile. Is `task` installed?*\n\n")

    # ── Scripts ───────────────────────────────────────────────
    parts.append("## Scripts\n\n")
    parts.append(
        "Standalone utilities in `scripts/`. Run with "
        "`python scripts/<name>.py` or via the corresponding Taskfile shortcut.\n\n"
    )

    scripts = _collect_scripts()
    for script in scripts:
        rel = script.relative_to(ROOT).as_posix()
        parts.append(f"### `{script.name}`\n\n")
        parts.append(f"**File:** [`{rel}`](../../{rel})\n\n")

        help_text = _script_help(script)
        if help_text:
            # Wrap in a collapsible details block so the page stays scannable
            parts.append('??? note "Full `--help` output"\n\n')
            parts.append("    ```text\n")
            parts.extend(f"    {line}\n" for line in help_text.splitlines())
            parts.append("    ```\n\n")
        else:
            parts.append("*No `--help` output available.*\n\n")

    # ── Shared modules ────────────────────────────────────────
    parts.append("## Shared Modules\n\n")
    parts.append(
        "Internal modules in `scripts/` used by multiple scripts. "
        "Not intended to be run directly.\n\n"
    )
    # Auto-discover shared modules (scripts/_*.py)
    shared_modules = sorted(SCRIPTS_DIR.glob("_*.py"))
    if shared_modules:
        parts.append("| Module | Description |\n")
        parts.append("| ------ | ----------- |\n")
        for mod_path in shared_modules:
            # Extract the first line of the module docstring as description
            desc = _extract_module_description(mod_path)
            rel_path = mod_path.relative_to(ROOT).as_posix()
            parts.append(f"| [`{mod_path.name}`](../../{rel_path}) | {desc} |\n")
        parts.append("\n")
    else:
        parts.append("*No shared modules found.*\n\n")

    # ── Hatch environments ────────────────────────────────────
    parts.append("## Hatch Environments\n\n")
    parts.append(
        "Managed by [Hatch](https://hatch.pypa.io/). "
        "Enter with `hatch shell` or run commands with `hatch run <cmd>`.\n\n"
    )

    env_output = _hatch_env_show()
    if env_output:
        parts.append("```text\n")
        parts.extend(f"{line}\n" for line in env_output.splitlines())
        parts.append("```\n\n")
    else:
        parts.append(
            "*Could not capture Hatch environments. Is `hatch` installed?*\n\n"
        )

    # ── Quick-reference table ─────────────────────────────────
    # Auto-generated from all parsed Taskfile tasks — no manual
    # curation needed.  Adding a task to Taskfile.yml is enough.
    parts.append("## Quick Reference\n\n")
    parts.append("Flat summary of every available task.\n\n")

    if tasks:
        parts.append("| What | Command |\n")
        parts.append("| ---- | ------- |\n")
        for name, desc in tasks:
            parts.append(f"| {_escape_md_brackets(desc)} | `task {name}` |\n")
    parts.append("\n")

    return "".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(
        prog="generate_command_reference",
        description="Generate docs/reference/commands.md from project commands.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the generated file differs from the existing one (CI mode).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated Markdown to stdout instead of writing to disk.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    content = _generate()

    if args.dry_run:
        print(content)
        return 0

    if args.check:
        if OUTPUT.exists():
            existing = OUTPUT.read_text(encoding="utf-8")
            if existing == content:
                logger.info("%s is up to date.", OUTPUT.relative_to(ROOT))
                return 0
            logger.warning(
                "%s is stale. Re-run: python scripts/generate_command_reference.py",
                OUTPUT.relative_to(ROOT),
            )
            return 1
        logger.warning("%s does not exist.", OUTPUT.relative_to(ROOT))
        return 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    logger.info("Generated %s", OUTPUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
