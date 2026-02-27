#!/usr/bin/env python3
"""Scan for TODO (template users) comments and report customization status.

After forking this template, many files contain ``TODO (template users):``
comments that need to be addressed. This script finds them all and reports
which ones remain, grouped by file.

Flags::

    --pattern TEXT      Text pattern to search for (default: "TODO (template users)")
    --count             Only print the count of TODOs found
    --json              Output results as JSON (for CI integration)
    --exclude PREFIX    Additional path prefixes to exclude (repeatable)
    -q, --quiet         Suppress output (exit code still indicates result)
    --version           Print version and exit

Usage::

    python scripts/check_todos.py
    python scripts/check_todos.py --count
    python scripts/check_todos.py --json
    python scripts/check_todos.py --pattern "TODO"
    python scripts/check_todos.py --exclude docs/notes
    python scripts/check_todos.py --quiet
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_VERSION = "1.1.0"
DEFAULT_PATTERN = "TODO (template users)"

# Directory names to skip (exact path-component match).
DEFAULT_EXCLUDE = {
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

# Directory name suffixes to skip.  A path component whose name *ends with*
# one of these is excluded (e.g. ".egg-info" matches
# "simple_python_boilerplate.egg-info").
DEFAULT_EXCLUDE_SUFFIXES = {
    ".egg-info",
}

# File extensions to scan (text files only)
SCAN_EXTENSIONS = {
    ".py",
    ".pyi",
    ".toml",
    ".yml",
    ".yaml",
    ".md",
    ".rst",
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
    ".sql",
    ".env",
    ".containerfile",
    ".dockerfile",
}

# Extensionless filenames that should always be scanned
SCAN_FILENAMES = {
    "Containerfile",
    "Dockerfile",
    "Makefile",
    "Taskfile",
    "Procfile",
}

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _is_excluded(
    path: Path,
    exclude_dirs: set[str],
    exclude_suffixes: set[str],
) -> bool:
    """Check whether *path* falls under an excluded directory.

    Supports two matching modes:

    * **Exact match** — the directory name equals an entry in *exclude_dirs*
      (e.g. ``".git"``, ``"__pycache__"``).
    * **Suffix match** — the directory name *ends with* an entry in
      *exclude_suffixes* (e.g. ``".egg-info"`` matches
      ``"simple_python_boilerplate.egg-info"``).

    Args:
        path: File path to test.
        exclude_dirs: Set of directory names to exclude (exact match).
        exclude_suffixes: Set of suffixes to exclude (endswith match).

    Returns:
        True if the path should be skipped.
    """
    for part in path.parts:
        if part in exclude_dirs:
            return True
        if any(part.endswith(sfx) for sfx in exclude_suffixes):
            return True
    return False


def find_todos(
    root: Path,
    pattern: str,
    exclude_dirs: set[str],
    extra_excludes: list[str] | None = None,
    exclude_suffixes: set[str] | None = None,
) -> dict[Path, list[tuple[int, str]]]:
    """Find all lines matching the pattern, grouped by file.

    Args:
        root: Project root directory.
        pattern: Text pattern to search for (case-insensitive).
        exclude_dirs: Directory names to skip entirely.
        extra_excludes: Additional path prefixes to exclude.
        exclude_suffixes: Directory name suffixes to skip.

    Returns:
        Dict mapping file paths to list of (line_number, line_text) tuples.
    """
    results: dict[Path, list[tuple[int, str]]] = {}
    pattern_lower = pattern.lower()
    extra = [Path(root / e) for e in (extra_excludes or [])]
    suffixes = exclude_suffixes or set()
    files_scanned = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in SCAN_EXTENSIONS and path.name not in SCAN_FILENAMES:
            continue
        if _is_excluded(path, exclude_dirs, suffixes):
            continue
        if any(path.is_relative_to(e) for e in extra):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError):
            continue

        files_scanned += 1
        matches = []
        for i, line in enumerate(text.splitlines(), start=1):
            if pattern_lower in line.lower():
                matches.append((i, line.rstrip()))

        if matches:
            results[path] = matches

    log.debug("Scanned %d file(s)", files_scanned)
    return results


def format_report(
    results: dict[Path, list[tuple[int, str]]],
    root: Path,
    *,
    count_only: bool = False,
    as_json: bool = False,
) -> str:
    """Build a report string for the found TODOs.

    Args:
        results: Output from find_todos().
        root: Project root (for relative path display).
        count_only: If True, only return summary counts.
        as_json: If True, return a JSON-encoded report.

    Returns:
        Formatted report string.
    """
    total = sum(len(matches) for matches in results.values())

    if as_json:
        data = {
            "total": total,
            "file_count": len(results),
            "files": {
                path.relative_to(root).as_posix(): [
                    {"line": num, "text": text.strip()} for num, text in matches
                ]
                for path, matches in results.items()
            },
        }
        return json.dumps(data, indent=2)

    if count_only:
        return f"{total} TODO(s) across {len(results)} file(s)"

    if not results:
        return "No TODOs found — template has been fully customized!"

    lines: list[str] = [f"Found {total} TODO(s) across {len(results)} file(s):\n"]

    for path, matches in results.items():
        rel = path.relative_to(root)
        lines.append(f"  {rel}")
        for line_num, line_text in matches:
            # Truncate long lines for readability
            display = line_text.strip()
            if len(display) > 100:
                display = display[:97] + "..."
            lines.append(f"    L{line_num}: {display}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_EPILOG = """\
exit codes:
  0  No TODOs found (template fully customized)
  1  TODOs remain (useful as a CI gate)
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Scan for TODO (template users) comments in the repository.",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help=f'Text pattern to search for (default: "{DEFAULT_PATTERN}")',
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--count",
        action="store_true",
        help="Only print the count of TODOs found",
    )
    output_group.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON (for CI integration)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output (exit code still indicates result)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional path prefixes to exclude (relative to project root)",
    )
    return parser.parse_args(argv)


def main() -> int:
    """Entry point for the check_todos script.

    Returns:
        Exit code: 0 if no TODOs found, 1 if TODOs remain.
    """
    args = parse_args()

    # Configure logging: --quiet suppresses INFO, errors always shown
    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)

    results = find_todos(
        root=ROOT,
        pattern=args.pattern,
        exclude_dirs=DEFAULT_EXCLUDE,
        extra_excludes=args.exclude,
        exclude_suffixes=DEFAULT_EXCLUDE_SUFFIXES,
    )

    if not args.quiet:
        report = format_report(
            results,
            ROOT,
            count_only=args.count,
            as_json=args.json_output,
        )
        # JSON goes to stdout for easy piping; human text uses logging
        if args.json_output:
            print(report)
        else:
            log.info("%s", report)

    # Non-zero exit if TODOs remain (useful in CI)
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
