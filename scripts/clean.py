#!/usr/bin/env python3
"""Remove build artifacts and caches from the repository.

Cleans: dist/, build/, *.egg-info/, __pycache__/, .pytest_cache/,
.mypy_cache/, .ruff_cache/, site/, .coverage, htmlcov/, *.pyc

Usage::

    python scripts/clean.py
    python scripts/clean.py --dry-run
    python scripts/clean.py --include-venv   # Also removes .venv directories
    task clean:all
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories to remove (relative to ROOT)
CACHE_DIRS = [
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "htmlcov",
    "site",
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

# File patterns to remove
FILE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    ".coverage",
    ".coverage.*",
]


def remove_path(path: Path, *, dry_run: bool = False) -> bool:
    """Remove a file or directory.

    Args:
        path: Path to remove.
        dry_run: If True, only print what would be removed.

    Returns:
        True if path existed and was (or would be) removed.
    """
    if not path.exists():
        return False

    if dry_run:
        kind = "directory" if path.is_dir() else "file"
        print(f"  Would remove {kind}: {path.relative_to(ROOT)}")
        return True

    if path.is_dir():
        shutil.rmtree(path)
        print(f"  Removed directory: {path.relative_to(ROOT)}")
    else:
        path.unlink()
        print(f"  Removed file: {path.relative_to(ROOT)}")
    return True


def clean(*, dry_run: bool = False, include_venv: bool = False) -> int:
    """Remove all build artifacts and caches.

    Args:
        dry_run: If True, only print what would be removed.
        include_venv: If True, also remove .venv* directories.

    Returns:
        Number of items removed.
    """
    removed = 0

    # Top-level cache directories
    print("Cleaning cache directories...")
    for name in CACHE_DIRS:
        if remove_path(ROOT / name, dry_run=dry_run):
            removed += 1

    # Top-level build directories
    print("Cleaning build directories...")
    for name in BUILD_DIRS:
        if remove_path(ROOT / name, dry_run=dry_run):
            removed += 1

    # Recursive directories (__pycache__, *.egg-info)
    print("Cleaning recursive directories...")
    for pattern in RECURSIVE_DIRS:
        for path in ROOT.rglob(pattern):
            # Skip .venv directories unless explicitly requested
            if ".venv" in path.parts and not include_venv:
                continue
            if remove_path(path, dry_run=dry_run):
                removed += 1

    # File patterns
    print("Cleaning file patterns...")
    for pattern in FILE_PATTERNS:
        for path in ROOT.rglob(pattern):
            if ".venv" in path.parts and not include_venv:
                continue
            if remove_path(path, dry_run=dry_run):
                removed += 1

    # Virtual environments (only if requested)
    if include_venv:
        print("Cleaning virtual environments...")
        for venv_dir in ROOT.glob(".venv*"):
            if venv_dir.is_dir() and remove_path(venv_dir, dry_run=dry_run):
                removed += 1

    # Summary
    action = "Would remove" if dry_run else "Removed"
    print(f"\n{action} {removed} item(s).")
    return removed


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="clean",
        description="Remove build artifacts and caches from the repository.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without deleting",
    )
    parser.add_argument(
        "--include-venv",
        action="store_true",
        help="Also remove .venv* directories (requires confirmation)",
    )
    args = parser.parse_args()

    if args.include_venv and not args.dry_run:
        confirm = input("This will delete .venv* directories. Continue? [y/N] ")
        if confirm.lower() != "y":
            print("Aborted.")
            return 1

    clean(dry_run=args.dry_run, include_venv=args.include_venv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
