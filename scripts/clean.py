#!/usr/bin/env python3
"""Remove build artifacts and caches from the repository.

Cleans: dist/, build/, *.egg-info/, __pycache__/, .pytest_cache/,
.mypy_cache/, .ruff_cache/, site/, .coverage, htmlcov/, *.pyc

Usage::

    python scripts/clean.py
    python scripts/clean.py --dry-run
    python scripts/clean.py --quiet
    python scripts/clean.py --include-venv          # Also removes .venv directories
    python scripts/clean.py --include-venv --yes    # Skip confirmation prompt
    task clean:all
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_VERSION = "1.1.0"

# Top-level cache directories to remove
CACHE_DIRS = [
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    "site",
]

# Top-level cache files to remove
CACHE_FILES = [
    ".coverage",
]

# Directories to remove recursively (anywhere in tree)
RECURSIVE_DIRS = [
    "__pycache__",
    "*.egg-info",
]

# Top-level build directories
BUILD_DIRS = [
    "dist",
    "build",
]

# File patterns to remove (skips files inside already-removed __pycache__ dirs)
FILE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    ".coverage.*",
]

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def remove_path(path: Path, *, dry_run: bool = False) -> bool:
    """Remove a file or directory.

    Args:
        path: Path to remove.
        dry_run: If True, only log what would be removed.

    Returns:
        True if path existed and was (or would be) removed.
    """
    if not path.exists():
        return False

    kind = "directory" if path.is_dir() else "file"
    rel = path.relative_to(ROOT)

    if dry_run:
        log.info("  Would remove %s: %s", kind, rel)
        return True

    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    log.info("  Removed %s: %s", kind, rel)
    return True


def clean(*, dry_run: bool = False, include_venv: bool = False) -> int:
    """Remove all build artifacts and caches.

    Args:
        dry_run: If True, only log what would be removed.
        include_venv: If True, also remove .venv* directories.

    Returns:
        Number of items removed.
    """
    removed = 0

    # Track directories removed in previous phases so we don't double-count
    # files inside them (e.g. .pyc files inside already-removed __pycache__).
    removed_dirs: set[Path] = set()

    # Top-level cache directories
    log.info("Cleaning cache directories...")
    for name in CACHE_DIRS:
        path = ROOT / name
        if remove_path(path, dry_run=dry_run):
            removed_dirs.add(path)
            removed += 1

    # Top-level cache files
    for name in CACHE_FILES:
        if remove_path(ROOT / name, dry_run=dry_run):
            removed += 1

    # Top-level build directories
    log.info("Cleaning build directories...")
    for name in BUILD_DIRS:
        path = ROOT / name
        if remove_path(path, dry_run=dry_run):
            removed_dirs.add(path)
            removed += 1

    # Recursive directories (__pycache__, *.egg-info)
    log.info("Cleaning recursive directories...")
    for pattern in RECURSIVE_DIRS:
        for path in sorted(ROOT.rglob(pattern)):
            # Skip .venv directories unless explicitly requested
            if ".venv" in path.parts and not include_venv:
                continue
            if remove_path(path, dry_run=dry_run):
                removed_dirs.add(path)
                removed += 1

    # File patterns (skip files inside already-removed directories)
    log.info("Cleaning file patterns...")
    for pattern in FILE_PATTERNS:
        for path in sorted(ROOT.rglob(pattern)):
            if ".venv" in path.parts and not include_venv:
                continue
            # Skip files inside directories already removed (or marked for
            # removal in dry-run) to avoid double-counting.
            if any(path.is_relative_to(d) for d in removed_dirs):
                continue
            if remove_path(path, dry_run=dry_run):
                removed += 1

    # Virtual environments (only if requested)
    if include_venv:
        log.info("Cleaning virtual environments...")
        for venv_dir in sorted(ROOT.glob(".venv*")):
            if venv_dir.is_dir() and remove_path(venv_dir, dry_run=dry_run):
                removed += 1

    # Summary
    action = "Would remove" if dry_run else "Removed"
    log.info("\n%s %d item(s).", action, removed)
    return removed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_EPILOG = """\
exit codes:
  0  Clean completed successfully (or aborted by user)
  1  Error during cleanup
"""


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="clean",
        description="Remove build artifacts and caches from the repository.",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without deleting",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress informational output (errors still shown)",
    )
    parser.add_argument(
        "--include-venv",
        action="store_true",
        help="Also remove .venv* directories (requires confirmation)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt for --include-venv",
    )
    args = parser.parse_args()

    # Configure logging
    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)

    if args.include_venv and not args.dry_run and not args.yes:
        # Guard against non-TTY stdin (e.g. piped input in CI)
        if not sys.stdin.isatty():
            log.error(
                "Cannot confirm interactively (stdin is not a TTY). "
                "Use --yes to skip the prompt."
            )
            return 1
        try:
            confirm = input("This will delete .venv* directories. Continue? [y/N] ")
        except (EOFError, KeyboardInterrupt):
            log.info("\nAborted.")
            return 0
        if confirm.lower() != "y":
            log.info("Aborted.")
            return 0

    clean(dry_run=args.dry_run, include_venv=args.include_venv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
