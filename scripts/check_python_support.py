#!/usr/bin/env python3
"""Validate that Python version support is consistent across all config files.

Checks that the declared Python version support is aligned between:
  - pyproject.toml requires-python
  - pyproject.toml classifiers
  - Hatch test matrix (pyproject.toml)
  - CI test workflow matrix (.github/workflows/test.yml)
  - bootstrap.py MIN_PYTHON constant

Reports mismatches so you never accidentally test or ship a version
you don't officially support (or forget to add support you do).

Flags::

    --json          Output as JSON (for CI integration)
    -q, --quiet     Suppress output; exit code only
    --no-color      Disable colored output
    --version       Print version and exit

Usage::

    python scripts/check_python_support.py
    python scripts/check_python_support.py --json
    python scripts/check_python_support.py --quiet   # Exit code only (for CI)
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import tomllib

# -- Local script modules (not third-party; live in scripts/) ----------------
from _colors import Colors
from _imports import find_repo_root
from _ui import UI

log = logging.getLogger(__name__)

ROOT = find_repo_root()
SCRIPT_VERSION = "1.1.0"

# Theme color for this script's dashboard output.
THEME = "green"

# TODO (template users): Update these paths if your project structure
#   differs (e.g., monorepo with multiple pyproject.toml files).


def _read_pyproject() -> dict:
    """Read and parse pyproject.toml."""
    path = ROOT / "pyproject.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _parse_requires_python(spec: str) -> tuple[int, int] | None:
    """Extract minimum Python version from requires-python spec (e.g., '>=3.11')."""
    match = re.match(r">=\s*(\d+)\.(\d+)", spec)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None


def _extract_classifier_versions(classifiers: list[str]) -> list[tuple[int, int]]:
    """Extract Python X.Y versions from PyPI classifiers."""
    versions = []
    for c in classifiers:
        match = re.match(r"Programming Language :: Python :: (\d+)\.(\d+)$", c)
        if match:
            versions.append((int(match.group(1)), int(match.group(2))))
    return sorted(versions)


def _extract_hatch_matrix(data: dict) -> list[tuple[int, int]]:
    """Extract Python versions from Hatch test matrix."""
    versions = []
    matrices = (
        data.get("tool", {})
        .get("hatch", {})
        .get("envs", {})
        .get("test", {})
        .get("matrix", [])
    )
    for matrix in matrices:
        for v in matrix.get("python", []):
            parts = str(v).split(".")
            if len(parts) >= 2:
                versions.append((int(parts[0]), int(parts[1])))
    return sorted(versions)


def _extract_ci_matrix() -> list[tuple[int, int]]:
    """Extract Python versions from CI test workflow matrix."""
    test_yml = ROOT / ".github" / "workflows" / "test.yml"
    if not test_yml.is_file():
        return []
    content = test_yml.read_text(encoding="utf-8")
    # Match python-version: ["3.11", "3.12", "3.13"]
    match = re.search(r"python-version:\s*\[([^\]]+)\]", content)
    if not match:
        return []
    versions = []
    for v in re.findall(r'"(\d+\.\d+)"', match.group(1)):
        parts = v.split(".")
        versions.append((int(parts[0]), int(parts[1])))
    return sorted(versions)


def _extract_bootstrap_min() -> tuple[int, int] | None:
    """Extract MIN_PYTHON from bootstrap.py."""
    bootstrap = ROOT / "scripts" / "bootstrap.py"
    if not bootstrap.is_file():
        return None
    content = bootstrap.read_text(encoding="utf-8")
    match = re.search(r"MIN_PYTHON\s*=\s*\((\d+),\s*(\d+)\)", content)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None


def _fmt_version(v: tuple[int, int]) -> str:
    return f"{v[0]}.{v[1]}"


def _fmt_versions(versions: list[tuple[int, int]]) -> str:
    return ", ".join(_fmt_version(v) for v in versions)


def check_python_support(*, quiet: bool = False, no_color: bool = False) -> dict:
    """Check all sources of Python version info and report mismatches.

    Returns:
        Dictionary with results: sources, mismatches, and overall status.
    """
    data = _read_pyproject()

    # Gather all sources
    requires_python = data.get("project", {}).get("requires-python", "")
    min_version = _parse_requires_python(requires_python)
    classifiers = data.get("project", {}).get("classifiers", [])
    classifier_versions = _extract_classifier_versions(classifiers)
    hatch_versions = _extract_hatch_matrix(data)
    ci_versions = _extract_ci_matrix()
    bootstrap_min = _extract_bootstrap_min()

    sources = {
        "requires-python": requires_python,
        "min_version": _fmt_version(min_version) if min_version else None,
        "classifiers": _fmt_versions(classifier_versions),
        "hatch_matrix": _fmt_versions(hatch_versions),
        "ci_matrix": _fmt_versions(ci_versions),
        "bootstrap_min": _fmt_version(bootstrap_min) if bootstrap_min else None,
    }

    mismatches: list[str] = []

    # Check: classifier versions should match hatch and CI matrices
    if classifier_versions and hatch_versions and classifier_versions != hatch_versions:
        mismatches.append(
            f"Classifier versions ({_fmt_versions(classifier_versions)}) "
            f"!= Hatch matrix ({_fmt_versions(hatch_versions)})"
        )

    if classifier_versions and ci_versions and classifier_versions != ci_versions:
        mismatches.append(
            f"Classifier versions ({_fmt_versions(classifier_versions)}) "
            f"!= CI matrix ({_fmt_versions(ci_versions)})"
        )

    if hatch_versions and ci_versions and hatch_versions != ci_versions:
        mismatches.append(
            f"Hatch matrix ({_fmt_versions(hatch_versions)}) "
            f"!= CI matrix ({_fmt_versions(ci_versions)})"
        )

    # Check: min version should match the lowest classifier/matrix version
    if min_version and classifier_versions:
        lowest_classifier = classifier_versions[0]
        if min_version != lowest_classifier:
            mismatches.append(
                f"requires-python minimum ({_fmt_version(min_version)}) "
                f"!= lowest classifier ({_fmt_version(lowest_classifier)})"
            )

    if min_version and hatch_versions:
        lowest_hatch = hatch_versions[0]
        if min_version != lowest_hatch:
            mismatches.append(
                f"requires-python minimum ({_fmt_version(min_version)}) "
                f"!= lowest Hatch matrix ({_fmt_version(lowest_hatch)})"
            )

    # Check: bootstrap MIN_PYTHON should match requires-python
    if bootstrap_min and min_version and bootstrap_min != min_version:
        mismatches.append(
            f"bootstrap.py MIN_PYTHON ({_fmt_version(bootstrap_min)}) "
            f"!= requires-python ({_fmt_version(min_version)})"
        )

    # Check: current Python meets minimum
    current = sys.version_info[:2]
    current_ok = min_version is None or current >= min_version

    result = {
        "sources": sources,
        "mismatches": mismatches,
        "current_python": _fmt_version(current),
        "current_meets_minimum": current_ok,
        "ok": len(mismatches) == 0,
    }

    if not quiet:
        c = Colors(enabled=not no_color)
        ui = UI(
            title="Python Version Support",
            version=SCRIPT_VERSION,
            theme=THEME,
            no_color=no_color,
        )
        ui.header()

        ui.section("Version Sources")
        ui.kv("requires-python", requires_python or c.dim("(not set)"))
        ui.kv(
            "Classifiers",
            _fmt_versions(classifier_versions) or c.dim("(none)"),
        )
        ui.kv(
            "Hatch matrix",
            _fmt_versions(hatch_versions) or c.dim("(none)"),
        )
        ui.kv(
            "CI test matrix",
            _fmt_versions(ci_versions) or c.dim("(not found)"),
        )
        ui.kv(
            "bootstrap.py",
            _fmt_version(bootstrap_min) if bootstrap_min else c.dim("(not found)"),
        )
        ui.kv("Current Python", _fmt_version(current))

        ui.blank()
        if mismatches:
            ui.section("Mismatches")
            for m in mismatches:
                ui.status_line("cross", m, "red")
            ui.blank()
            ui.status_line(
                "cross",
                "Python version support is inconsistent across config files.",
                "red",
            )
        else:
            ui.status_line("check", "All version sources are consistent.", "green")

        if not current_ok:
            ui.status_line(
                "warn",
                f"Current Python {_fmt_version(current)} does not meet "
                f"minimum {_fmt_version(min_version) if min_version else '?'}",
                "yellow",
            )

        passed = (0 if mismatches else 1) + (1 if current_ok else 0)
        failed = (1 if mismatches else 0) + (0 if current_ok else 1)
        ui.footer(passed=passed, failed=failed)

    return result


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="check-python-support",
        description="Validate Python version support is consistent across config files.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output; exit code only",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    args = parser.parse_args()

    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)

    result = check_python_support(
        quiet=args.json_output or args.quiet,
        no_color=args.no_color,
    )

    if args.json_output:
        print(json.dumps(result, indent=2))

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
