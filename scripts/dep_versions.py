#!/usr/bin/env python3
"""Show and optionally update dependency version comments in pyproject.toml.

This script reads all dependency groups from pyproject.toml, checks currently
installed versions, reports available upgrades, and can update inline comments
to reflect the currently installed version.

Dependabot updates the actual version *specifiers* (e.g., ``>=1.6`` → ``>=1.7``)
but does NOT touch comments. This script fills that gap.

Requirements:
    - Python 3.11+
    - pip (for ``pip index versions``)
    - The project installed in the current environment (``pip install -e .[dev]``)

Usage:
    python scripts/dep_versions.py              # Print version report
    python scripts/dep_versions.py --update     # Also update comments in pyproject.toml
    python scripts/dep_versions.py --no-latest  # Skip PyPI check (faster, offline)

Examples:
    # Quick overview of all dep versions
    python scripts/dep_versions.py

    # Update comments after a Dependabot merge
    python scripts/dep_versions.py --update

    # Offline mode — only show installed, skip latest check
    python scripts/dep_versions.py --no-latest
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"


def _installed_version(pkg: str) -> str | None:
    """Return the installed version of *pkg*, or ``None``."""
    try:
        return version(pkg)
    except PackageNotFoundError:
        return None


def _latest_version(pkg: str) -> str | None:
    """Query PyPI for the latest version of *pkg* via ``pip index versions``.

    Returns ``None`` on any failure (network, pip too old, etc.).
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", pkg],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return None
        # Output like: "my-package (1.2.3)"
        match = re.search(r"\(([^)]+)\)", result.stdout)
        return match.group(1) if match else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _normalise_name(raw: str) -> str:
    """Normalise a PEP 503 package name for comparison.

    ``mkdocs-material`` and ``mkdocs_material`` both become ``mkdocs-material``.
    Extras are stripped: ``mkdocstrings[python]`` → ``mkdocstrings``.
    """
    name = re.split(r"[><=!~;\[]", raw)[0].strip()
    return re.sub(r"[-_.]+", "-", name).lower()


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

_DEP_RE = re.compile(
    r"""
    ^                     # start of line
    (?P<indent>\s*)       # leading whitespace
    "                     # opening quote
    (?P<spec>[^"]+)       # dependency specifier
    "                     # closing quote
    (?P<sep>\s*,)         # comma (possibly with space before)
    (?P<trail>.*)         # trailing content (comment or nothing)
    $
    """,
    re.VERBOSE,
)


def _parse_deps_from_toml(text: str) -> dict[str, list[str]]:
    """Return ``{group_name: [raw_dep_line, ...]}`` from pyproject.toml text.

    Reads ``[project].dependencies`` and every key under
    ``[project.optional-dependencies]``.
    """
    groups: dict[str, list[str]] = {}
    current_section: str | None = None  # tracks the active TOML table header
    current_list: list[str] | None = None  # tracks the active array we're inside
    in_opt_deps = False  # whether we're inside [project.optional-dependencies]

    for line in text.splitlines():
        stripped = line.strip()

        # Detect TOML table headers: [something] or [[something]]
        table_match = re.match(r"^\[+([^\]]+)\]+$", stripped)
        if table_match:
            table_name = table_match.group(1).strip()
            current_section = table_name
            current_list = None  # close any open array
            in_opt_deps = table_name == "project.optional-dependencies"
            continue

        # Inside [project]: look for ``dependencies = [``
        if current_section == "project" and stripped == "dependencies = [":
            current_list = []
            groups["dependencies"] = current_list
            continue

        # Inside [project.optional-dependencies]: look for ``name = [``
        if in_opt_deps:
            group_match = re.match(r"^(\w[\w-]*)\s*=\s*\[$", stripped)
            if group_match:
                group_name = group_match.group(1)
                current_list = []
                groups[group_name] = current_list
                continue

        # Closing bracket ends the current array
        if stripped == "]":
            current_list = None
            continue

        # Collect quoted strings inside an active dependency array
        if current_list is not None and stripped.startswith('"'):
            # Extract the quoted specifier, stripping trailing comma
            spec_match = re.match(r'^"([^"]+)"', stripped)
            if spec_match:
                current_list.append(spec_match.group(1))

    return groups


def collect_report(
    *, check_latest: bool = True,
) -> list[dict[str, str | None]]:
    """Build a report of all dependencies with installed/latest versions."""
    text = PYPROJECT.read_text(encoding="utf-8")
    groups = _parse_deps_from_toml(text)

    rows: list[dict[str, str | None]] = []
    seen: set[str] = set()

    for group, deps in groups.items():
        for raw in deps:
            name = _normalise_name(raw)
            if name in seen:
                continue
            seen.add(name)

            # Skip self-references like ``my-project[test]``
            if name == _normalise_name(
                PYPROJECT.parent.name
            ) or "simple-python-boilerplate" in name:
                continue

            installed = _installed_version(name)
            latest = _latest_version(name) if check_latest else None
            upgradable = (
                installed != latest
                if installed and latest
                else None
            )

            rows.append({
                "group": group,
                "name": name,
                "specifier": raw,
                "installed": installed,
                "latest": latest,
                "upgradable": "yes" if upgradable else ("" if upgradable is None else ""),
            })

    return rows


def print_report(rows: list[dict[str, str | None]]) -> None:
    """Pretty-print the dependency report."""
    # Column widths
    w_name = max((len(r["name"] or "") for r in rows), default=10)
    w_group = max((len(r["group"] or "") for r in rows), default=10)
    w_spec = max((len(r["specifier"] or "") for r in rows), default=10)
    w_inst = max((len(r["installed"] or "") for r in rows), default=9)
    w_lat = max((len(r["latest"] or "-") for r in rows), default=6)

    hdr = (
        f"  {'Package':<{w_name}}  {'Group':<{w_group}}  "
        f"{'Specifier':<{w_spec}}  {'Installed':<{w_inst}}  "
        f"{'Latest':<{w_lat}}  Upgradable"
    )
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    for r in rows:
        flag = ""
        if r["upgradable"] == "yes":
            flag = "^"
        print(
            f"  {r['name']:<{w_name}}  {r['group']:<{w_group}}  "
            f"{r['specifier']:<{w_spec}}  {r['installed'] or '–':<{w_inst}}  "
            f"{r['latest'] or '-':<{w_lat}}  {flag}"
        )


# ---------------------------------------------------------------------------
# Comment updater
# ---------------------------------------------------------------------------


def update_comments(rows: list[dict[str, str | None]]) -> int:
    """Rewrite inline ``# vX.Y.Z`` comments in pyproject.toml.

    For every dependency line that has a trailing comment, replace the
    version portion with the currently installed version. Lines without
    a comment are left untouched.

    Returns the number of lines modified.
    """
    text = PYPROJECT.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # Build a lookup: normalised name → installed version
    versions: dict[str, str] = {}
    for r in rows:
        name = r.get("name", "")
        inst = r.get("installed")
        if name and inst:
            versions[name] = inst

    modified = 0

    for i, line in enumerate(lines):
        m = _DEP_RE.match(line.rstrip("\n"))
        if not m:
            continue

        spec = m.group("spec")
        name = _normalise_name(spec)
        trail = m.group("trail")

        if name not in versions:
            continue

        installed = versions[name]

        # Only touch lines that already have a comment
        if "#" not in trail:
            continue

        # Replace version in comment (e.g., ``# v1.2.3`` or ``# Testing framework``)
        # We look for an existing version pattern in the comment and replace it.
        # If no version pattern exists, append after the comment text.
        comment_match = re.search(r"#\s*(.*)", trail)
        if not comment_match:
            continue

        comment_text = comment_match.group(1).strip()

        # Check if comment already contains a version string
        ver_in_comment = re.search(r"v?\d+\.\d+[\.\d]*", comment_text)
        if ver_in_comment:
            new_comment = comment_text[:ver_in_comment.start()] + f"v{installed}" + comment_text[ver_in_comment.end():]
        else:
            # No version in comment — append it
            new_comment = f"{comment_text} (v{installed})"

        new_trail = f"  # {new_comment}"
        new_line = f'{m.group("indent")}"{spec}"{m.group("sep")}{new_trail}\n'

        if new_line != lines[i]:
            lines[i] = new_line
            modified += 1

    if modified:
        PYPROJECT.write_text("".join(lines), encoding="utf-8")

    return modified


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Show dependency versions and optionally update pyproject.toml comments.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update version comments in pyproject.toml to match installed versions.",
    )
    parser.add_argument(
        "--no-latest",
        action="store_true",
        help="Skip querying PyPI for latest versions (faster, works offline).",
    )
    args = parser.parse_args()

    print(f"\nDependency versions for {PYPROJECT.parent.name}\n")

    rows = collect_report(check_latest=not args.no_latest)

    if not rows:
        print("  No dependencies found in pyproject.toml.")
        return

    print_report(rows)

    if args.update:
        count = update_comments(rows)
        if count:
            print(f"\nUpdated {count} comment(s) in pyproject.toml")
        else:
            print("\n  No comments to update (add inline # comments to dep lines to use this feature).")

    print()


if __name__ == "__main__":
    main()
