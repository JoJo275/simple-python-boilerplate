#!/usr/bin/env python3
"""Scan for TODO (template users) comments and report customization status.

After forking this template, many files contain ``TODO (template users):``
comments that need to be addressed. This script finds them all and reports
which ones remain, grouped by file.

Usage::

    python scripts/check_todos.py
    python scripts/check_todos.py --count
    python scripts/check_todos.py --pattern "TODO"
    python scripts/check_todos.py --exclude docs/notes
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATTERN = "TODO (template users)"
DEFAULT_EXCLUDE = {
    ".git",
    ".venv",
    ".venv-1",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "site",
    ".egg-info",
}
# File extensions to scan (text files only)
SCAN_EXTENSIONS = {
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
}


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def find_todos(
    root: Path,
    pattern: str,
    exclude_dirs: set[str],
    extra_excludes: list[str] | None = None,
) -> dict[Path, list[tuple[int, str]]]:
    """Find all lines matching the pattern, grouped by file.

    Args:
        root: Project root directory.
        pattern: Text pattern to search for (case-insensitive).
        exclude_dirs: Directory names to skip entirely.
        extra_excludes: Additional path prefixes to exclude.

    Returns:
        Dict mapping file paths to list of (line_number, line_text) tuples.
    """
    results: dict[Path, list[tuple[int, str]]] = {}
    pattern_lower = pattern.lower()
    extra = [Path(root / e) for e in (extra_excludes or [])]

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in SCAN_EXTENSIONS:
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue
        if any(path.is_relative_to(e) for e in extra):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError):
            continue

        matches = []
        for i, line in enumerate(text.splitlines(), start=1):
            if pattern_lower in line.lower():
                matches.append((i, line.rstrip()))

        if matches:
            results[path] = matches

    return results


def print_report(
    results: dict[Path, list[tuple[int, str]]], root: Path, count_only: bool
) -> None:
    """Print a human-readable report of found TODOs.

    Args:
        results: Output from find_todos().
        root: Project root (for relative path display).
        count_only: If True, only print summary counts.
    """
    total = sum(len(matches) for matches in results.values())

    if count_only:
        print(f"{total} TODO(s) across {len(results)} file(s)")
        return

    if not results:
        print("No TODOs found — template has been fully customized!")
        return

    print(f"Found {total} TODO(s) across {len(results)} file(s):\n")

    for path, matches in results.items():
        rel = path.relative_to(root)
        print(f"  {rel}")
        for line_num, line_text in matches:
            # Truncate long lines for readability
            display = line_text.strip()
            if len(display) > 100:
                display = display[:97] + "..."
            print(f"    L{line_num}: {display}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Scan for TODO (template users) comments in the repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help=f'Text pattern to search for (default: "{DEFAULT_PATTERN}")',
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Only print the count of TODOs found",
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
    results = find_todos(
        root=ROOT,
        pattern=args.pattern,
        exclude_dirs=DEFAULT_EXCLUDE,
        extra_excludes=args.exclude,
    )
    print_report(results, ROOT, args.count)

    # Non-zero exit if TODOs remain (useful in CI)
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
