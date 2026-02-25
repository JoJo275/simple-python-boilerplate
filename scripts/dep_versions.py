#!/usr/bin/env python3
"""Dependency version manager for pyproject.toml and requirements files.

Show installed/latest versions, update inline comments, and upgrade
individual or all dependencies.

Dependabot updates the actual version *specifiers* (e.g., ``>=1.6`` to
``>=1.7``) but does NOT touch comments. This script fills that gap and
adds the ability to upgrade dependencies via pip.

The ``update-comments`` command annotates **every** dependency line with
a succinct description (from PyPI metadata) and the installed version.
Lines that already have a comment get their version refreshed; lines
without a comment receive a new ``# <summary> (vX.Y.Z)`` annotation.
This works across pyproject.toml **and** any requirements*.txt files
found in the project root.

Requirements:
    - Python 3.11+
    - pip
    - The project installed in the current environment

Usage:
    python scripts/dep_versions.py --version             # Show script version
    python scripts/dep_versions.py                       # Show all dep versions
    python scripts/dep_versions.py show --offline        # Skip PyPI check
    python scripts/dep_versions.py update-comments       # Sync comments with installed
    python scripts/dep_versions.py upgrade               # Upgrade ALL deps to latest
    python scripts/dep_versions.py upgrade --dry-run     # Preview upgrades without installing
    python scripts/dep_versions.py upgrade ruff           # Upgrade ruff to latest
    python scripts/dep_versions.py upgrade ruff 0.9.0    # Upgrade ruff to specific version
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess  # nosec B404
import sys
import warnings
from importlib.metadata import PackageNotFoundError
from importlib.metadata import metadata as pkg_metadata
from importlib.metadata import version as pkg_version
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.1.0"

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
REQ_FILES = sorted(ROOT.glob("requirements*.txt"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _warn_if_no_venv() -> None:
    """Emit a warning if running outside a virtual environment.

    Installing or upgrading packages outside a venv risks polluting
    the global Python installation.  This project convention is to
    always use a Hatch-managed environment.
    """
    if sys.prefix == sys.base_prefix:
        warnings.warn(
            "You are running outside a virtual environment. "
            "Upgrading packages here will modify the global Python "
            "installation. Consider using 'hatch shell' first.",
            stacklevel=2,
        )


def _installed_version(pkg: str) -> str | None:
    """Return the installed version of *pkg*, or ``None``."""
    try:
        return pkg_version(pkg)
    except PackageNotFoundError:
        return None


def _package_summary(pkg: str) -> str | None:
    """Return the one-line PyPI summary for *pkg*, or ``None``.

    Uses locally installed metadata — no network call required.
    If the summary starts with the package name (e.g. ``"pytest:
    simple powerful testing…"``), the redundant prefix is stripped.
    """
    try:
        meta = pkg_metadata(pkg)
        summary: str | None = meta["Summary"]
        if not summary:
            return None
        # Strip trailing periods for consistency
        summary = summary.rstrip(".")
        # Remove leading "pkgname: " or "pkgname - " prefix (redundant)
        prefix_re = re.compile(
            r"^" + re.escape(pkg) + r"\s*[:—–-]\s*",  # noqa: RUF001
            re.IGNORECASE,
        )
        summary = prefix_re.sub("", summary)
        return summary
    except PackageNotFoundError:
        return None


def _latest_version(pkg: str) -> str | None:
    """Query PyPI for the latest version of *pkg*.

    Tries ``pip index versions --format=json`` first (stable, machine-
    readable output added in pip 24.2).  Falls back to parsing the
    human-readable output for older pip versions.

    Returns ``None`` on any failure (network, pip too old, etc.).
    """
    try:
        # Attempt JSON format first (pip >= 24.2)
        result = subprocess.run(  # nosec B603
            [
                sys.executable,
                "-m",
                "pip",
                "index",
                "versions",
                pkg,
                "--format=json",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                # JSON output: {"name": ..., "version": "1.2.3", ...}
                ver = data.get("version")
                if ver:
                    return str(ver)
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        # Fallback: parse human-readable output (older pip)
        result = subprocess.run(  # nosec B603
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
    Extras are stripped: ``mkdocstrings[python]`` -> ``mkdocstrings``.
    """
    name = re.split(r"[><=!~;\[]", raw)[0].strip()
    return re.sub(r"[-_.]+", "-", name).lower()


def _capitalise(text: str) -> str:
    """Upper-case the first letter, leave the rest unchanged.

    Unlike ``str.capitalize()``, this does **not** lower-case the tail,
    so ``"PyPI metadata"`` stays ``"PyPI metadata"`` instead of becoming
    ``"Pypi metadata"``.
    """
    if not text:
        return text
    return text[0].upper() + text[1:]


# ---------------------------------------------------------------------------
# TOML parser (dependency lines only)
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
    """Return ``{group_name: [specifier_string, ...]}`` from pyproject.toml.

    Reads ``[project].dependencies`` and every key under
    ``[project.optional-dependencies]``.
    """
    groups: dict[str, list[str]] = {}
    current_section: str | None = None
    current_list: list[str] | None = None
    in_opt_deps = False

    for line in text.splitlines():
        stripped = line.strip()

        # Detect TOML table headers: [something] or [[something]]
        table_match = re.match(r"^\[+([^\]]+)\]+$", stripped)
        if table_match:
            table_name = table_match.group(1).strip()
            current_section = table_name
            current_list = None
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
                current_list = []
                groups[group_match.group(1)] = current_list
                continue

        # Closing bracket ends the current array
        if stripped == "]":
            current_list = None
            continue

        # Collect quoted strings inside an active dependency array
        if current_list is not None and stripped.startswith('"'):
            spec_match = re.match(r'^"([^"]+)"', stripped)
            if spec_match:
                current_list.append(spec_match.group(1))

    return groups


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def collect_report(*, check_latest: bool = True) -> list[dict[str, str | None]]:
    """Build a report of all dependencies with installed and latest versions."""
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

            # Skip self-references
            if "simple-python-boilerplate" in name:
                continue

            installed = _installed_version(name)
            latest = _latest_version(name) if check_latest else None
            upgradable = installed != latest if installed and latest else None

            rows.append(
                {
                    "group": group,
                    "name": name,
                    "specifier": raw,
                    "installed": installed,
                    "latest": latest,
                    "upgradable": "yes" if upgradable else "",
                }
            )

    return rows


def print_report(rows: list[dict[str, str | None]]) -> None:
    """Pretty-print the dependency report."""
    w_name = max((len(r["name"] or "") for r in rows), default=10)
    w_group = max((len(r["group"] or "") for r in rows), default=10)
    w_spec = max((len(r["specifier"] or "") for r in rows), default=10)
    w_inst = max((len(r["installed"] or "-") for r in rows), default=9)
    w_lat = max((len(r["latest"] or "-") for r in rows), default=6)

    hdr = (
        f"  {'Package':<{w_name}}  {'Group':<{w_group}}  "
        f"{'Specifier':<{w_spec}}  {'Installed':<{w_inst}}  "
        f"{'Latest':<{w_lat}}  Upgrade?"
    )
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    for r in rows:
        flag = "^" if r["upgradable"] == "yes" else ""
        inst = r["installed"] or "-"
        lat = r["latest"] or "-"
        print(
            f"  {r['name']:<{w_name}}  {r['group']:<{w_group}}  "
            f"{r['specifier']:<{w_spec}}  {inst:<{w_inst}}  "
            f"{lat:<{w_lat}}  {flag}"
        )


# ---------------------------------------------------------------------------
# Comment updater
# ---------------------------------------------------------------------------


def update_comments(rows: list[dict[str, str | None]]) -> int:
    """Rewrite inline comments on dependency lines in pyproject.toml.

    Behaviour per line:

    * **Has a comment with a version** — version is replaced with the
      installed version, description text is preserved.
    * **Has a comment without a version** — installed version is appended
      in parentheses.
    * **No comment at all** — a new comment is generated from the
      package's PyPI summary and the installed version, e.g.
      ``# Simple powerful testing with Python (v8.4.2)``.

    Returns the number of lines modified.
    """
    text = PYPROJECT.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

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

        if "#" in trail:
            # ---- existing comment: update version in place ----
            comment_match = re.search(r"#\s*(.*)", trail)
            if not comment_match:
                continue

            comment_text = comment_match.group(1).strip()

            ver_in_comment = re.search(r"v?\d+\.\d+[\.\d]*", comment_text)
            if ver_in_comment:
                new_comment = (
                    comment_text[: ver_in_comment.start()]
                    + f"v{installed}"
                    + comment_text[ver_in_comment.end() :]
                )
            else:
                new_comment = f"{comment_text} (v{installed})"
        else:
            # ---- no comment: generate description + version ----
            summary = _package_summary(name)
            desc = _capitalise(summary) if summary else name
            new_comment = f"{desc} (v{installed})"

        new_trail = f"  # {new_comment}"
        new_line = f'{m.group("indent")}"{spec}"{m.group("sep")}{new_trail}\n'

        if new_line != lines[i]:
            lines[i] = new_line
            modified += 1

    if modified:
        PYPROJECT.write_text("".join(lines), encoding="utf-8")

    return modified


# ---------------------------------------------------------------------------
# Requirements-file comment updater
# ---------------------------------------------------------------------------

# Matches an uncommented dependency line in a requirements file.
# Examples:  pytest, pytest>=8.0, pytest==8.4.2, ruff  # some comment
_REQ_DEP_RE = re.compile(
    r"""
    ^                        # start of line
    (?P<spec>[A-Za-z0-9]     # package name starts with alphanumeric
        [A-Za-z0-9._-]*      # rest of package name
        (?:\[[^\]]+\])?      # optional extras  e.g. [python]
        (?:[><=!~]\S*)?)     # optional version constraint
    (?P<trail>\s*(?:[#].*)?) # optional trailing comment
    $
    """,
    re.VERBOSE,
)


def update_requirements_comments() -> dict[str, int]:
    """Update inline comments in every ``requirements*.txt`` file.

    The same logic as ``update_comments`` for pyproject.toml is applied:

    * Lines with a comment get their version refreshed.
    * Lines without a comment receive a generated
      ``# <summary> (vX.Y.Z)`` annotation.

    Returns a mapping ``{filename: lines_modified}``.
    """
    results: dict[str, int] = {}

    for req_path in REQ_FILES:
        text = req_path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        modified = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip blanks, pure comments, options, and -r includes
            if not stripped or stripped.startswith("#") or stripped.startswith("-"):
                continue

            m = _REQ_DEP_RE.match(stripped)
            if not m:
                continue

            raw_spec = m.group("spec")
            name = _normalise_name(raw_spec)
            trail = m.group("trail").strip()
            installed = _installed_version(name)

            if not installed:
                continue

            if trail and "#" in trail:
                # Update existing comment
                comment_match = re.search(r"#\s*(.*)", trail)
                if not comment_match:
                    continue
                comment_text = comment_match.group(1).strip()
                ver_in = re.search(r"v?\d+\.\d+[\.\d]*", comment_text)
                if ver_in:
                    new_comment = (
                        comment_text[: ver_in.start()]
                        + f"v{installed}"
                        + comment_text[ver_in.end() :]
                    )
                else:
                    new_comment = f"{comment_text} (v{installed})"
            else:
                # Generate new comment
                summary = _package_summary(name)
                desc = _capitalise(summary) if summary else name
                new_comment = f"{desc} (v{installed})"

            new_line = f"{raw_spec}  # {new_comment}\n"
            if new_line != lines[i]:
                lines[i] = new_line
                modified += 1

        if modified:
            req_path.write_text("".join(lines), encoding="utf-8")
        results[req_path.name] = modified

    return results


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------


def upgrade_package(name: str, target_version: str | None = None) -> bool:
    """Upgrade a single package via pip.

    Args:
        name: Package name (e.g., ``ruff``).
        target_version: Specific version to install. If ``None``, installs
            the latest version.

    Returns:
        ``True`` if pip returned success.
    """
    spec = f"{name}=={target_version}" if target_version else name
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", spec]
    print(f"  pip install --upgrade {spec}")
    result = subprocess.run(  # nosec B603
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        print(f"  FAILED: {result.stderr.strip()}")
        return False
    # Show what was installed
    new_ver = _installed_version(name)
    print(f"  -> {name} {new_ver}")
    return True


def upgrade_all(rows: list[dict[str, str | None]]) -> int:
    """Upgrade all packages that have a newer version available.

    Returns the number of packages upgraded.
    """
    upgraded = 0
    for r in rows:
        if (
            r["upgradable"] == "yes"
            and r["name"]
            and r["installed"]
            and upgrade_package(r["name"])
        ):
            upgraded += 1
    return upgraded


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="dep_versions",
        description="Dependency version manager for pyproject.toml and requirements files.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # -- show (default) --
    show_p = sub.add_parser(
        "show",
        help="Show installed and latest versions of all dependencies (default).",
    )
    show_p.add_argument(
        "--offline",
        action="store_true",
        help="Skip querying PyPI for latest versions (faster).",
    )

    # -- update-comments --
    sub.add_parser(
        "update-comments",
        help=(
            "Update inline version comments in pyproject.toml and "
            "requirements*.txt files.  Adds descriptions and versions "
            "to lines that have no comment."
        ),
    )

    # -- upgrade --
    upgrade_p = sub.add_parser(
        "upgrade",
        help="Upgrade dependencies via pip.",
    )
    upgrade_p.add_argument(
        "package",
        nargs="?",
        default=None,
        help="Package to upgrade (omit to upgrade all upgradable).",
    )
    upgrade_p.add_argument(
        "version",
        nargs="?",
        default=None,
        help="Target version (omit to upgrade to latest).",
    )
    upgrade_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be upgraded without installing anything.",
    )

    return parser


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # Default to "show" when no subcommand given
    command = args.command or "show"

    print(f"\nDependency versions for {PYPROJECT.parent.name}\n")

    if command == "show":
        offline = getattr(args, "offline", False)
        rows = collect_report(check_latest=not offline)
        if not rows:
            print("  No dependencies found in pyproject.toml.")
            return
        print_report(rows)

    elif command == "update-comments":
        rows = collect_report(check_latest=False)
        if not rows:
            print("  No dependencies found in pyproject.toml.")
            return
        print_report(rows)

        # ---- pyproject.toml ----
        count = update_comments(rows)
        if count:
            print(f"\n  Updated {count} comment(s) in pyproject.toml")
        else:
            print("\n  pyproject.toml: no changes needed.")

        # ---- requirements*.txt ----
        req_results = update_requirements_comments()
        for fname, n in req_results.items():
            if n:
                print(f"  Updated {n} comment(s) in {fname}")
            else:
                print(f"  {fname}: no changes needed.")

    elif command == "upgrade":
        pkg = getattr(args, "package", None)
        ver = getattr(args, "version", None)
        dry_run = getattr(args, "dry_run", False)

        # Warn if running outside a virtual environment
        _warn_if_no_venv()

        if pkg:
            # Upgrade a single package
            normalised = _normalise_name(pkg)
            # Verify it's one of our declared deps
            text = PYPROJECT.read_text(encoding="utf-8")
            groups = _parse_deps_from_toml(text)
            all_deps = {_normalise_name(s) for specs in groups.values() for s in specs}
            if normalised not in all_deps:
                print(
                    f"  '{pkg}' is not declared in pyproject.toml."
                    " Only deps listed in [project.optional-dependencies]"
                    " or [project].dependencies can be upgraded."
                )
                sys.exit(1)
            if dry_run:
                latest = _latest_version(normalised)
                installed = _installed_version(normalised)
                print(f"  [dry-run] {normalised}: {installed} -> {latest or '?'}")
            else:
                success = upgrade_package(normalised, ver)
                sys.exit(0 if success else 1)
        else:
            # Upgrade all
            rows = collect_report(check_latest=True)
            if not rows:
                print("  No dependencies found.")
                return
            print_report(rows)

            upgradable = [r for r in rows if r["upgradable"] == "yes"]
            if not upgradable:
                print("\n  All dependencies are up to date.")
                return

            if dry_run:
                print(
                    f"\n  [dry-run] {len(upgradable)} package(s) would be upgraded:\n"
                )
                for r in upgradable:
                    print(f"    {r['name']}: {r['installed']} -> {r['latest']}")
                print("\n  Run without --dry-run to install.")
            else:
                print(f"\nUpgrading {len(upgradable)} package(s)...\n")
                count = upgrade_all(rows)
                print(f"\nUpgraded {count} package(s).")

        # After successful upgrade, refresh comments to keep files in sync
        if not dry_run:
            print("  Refreshing version comments...")
            fresh_rows = collect_report(check_latest=False)
            toml_count = update_comments(fresh_rows)
            req_results = update_requirements_comments()
            if toml_count:
                print(f"  Updated {toml_count} comment(s) in pyproject.toml")
            for fname, n in req_results.items():
                if n:
                    print(f"  Updated {n} comment(s) in {fname}")

    print()


if __name__ == "__main__":
    main()
