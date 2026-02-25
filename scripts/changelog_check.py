#!/usr/bin/env python3
"""Verify CHANGELOG.md entries match git tags.

Compares version headings in CHANGELOG.md against git tags to detect
drift between what release-please generates and what's actually tagged.
Also checks for duplicate entries and correct ordering.

Usage::

    python scripts/changelog_check.py
    python scripts/changelog_check.py --verbose
    python scripts/changelog_check.py --quiet       # Exit code only (for CI)
    python scripts/changelog_check.py --changelog-path docs/CHANGES.md
"""

from __future__ import annotations

import argparse
import re
import subprocess  # nosec B404
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"

# Matches release-please style headings: ## [1.2.3](url) (date) or ## 1.2.3
VERSION_HEADING_RE = re.compile(
    r"^##\s+\[?(\d+\.\d+\.\d+(?:[a-zA-Z0-9.+-]*)?)\]?",
    re.MULTILINE,
)

# Git tag pattern (release-please convention)
TAG_RE = re.compile(r"^v(\d+\.\d+\.\d+(?:[a-zA-Z0-9.+-]*)?)$")


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def get_changelog_versions(changelog_path: Path) -> list[str]:
    """Extract version numbers from CHANGELOG.md headings.

    Args:
        changelog_path: Path to the CHANGELOG.md file.

    Returns:
        List of version strings found in headings, in file order.
    """
    if not changelog_path.exists():
        return []
    text = changelog_path.read_text(encoding="utf-8")
    return VERSION_HEADING_RE.findall(text)


def get_git_tag_versions() -> list[str]:
    """Extract version numbers from git tags matching ``v*.*.*``.

    Returns:
        Sorted list of version strings (without the ``v`` prefix).
    """
    try:
        result = subprocess.run(  # nosec B603 B607 — git only, no shell, no user input
            ["git", "tag", "--list", "v*"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=ROOT,
        )
        if result.returncode != 0:
            return []
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []

    versions = []
    for line in result.stdout.strip().splitlines():
        match = TAG_RE.match(line.strip())
        if match:
            versions.append(match.group(1))

    return sorted(versions, key=_version_key)


def _version_key(version: str) -> tuple[tuple[int, int | str], ...]:
    """Convert a version string to a sortable tuple.

    Handles semver with optional pre-release suffixes (e.g., ``1.2.3-rc.1``).
    Each segment becomes ``(0, int_value)`` for numeric parts or
    ``(1, str_value)`` for non-numeric parts, ensuring ints and strings
    never compare directly (which raises ``TypeError`` in Python 3).

    Args:
        version: Semver-like version string (e.g., "1.2.3", "1.2.3-rc.1").

    Returns:
        Tuple for sorting.
    """
    parts: list[tuple[int, int | str]] = []
    for segment in re.split(r"[.-]", version):
        if segment.isdigit():
            parts.append((0, int(segment)))
        else:
            parts.append((1, segment))
    return tuple(parts)


def check_duplicates(
    versions: list[str],
    *,
    quiet: bool = False,
) -> list[str]:
    """Find duplicate version entries.

    Args:
        versions: List of version strings (in file order).
        quiet: Suppress output.

    Returns:
        List of duplicated version strings.
    """
    seen: set[str] = set()
    duplicates: list[str] = []
    for v in versions:
        if v in seen and v not in duplicates:
            duplicates.append(v)
        seen.add(v)

    if duplicates and not quiet:
        print(f"\n  Duplicate CHANGELOG entries ({len(duplicates)}):")
        for v in duplicates:
            print(f"    - {v}")

    return duplicates


def check_ordering(
    versions: list[str],
    *,
    quiet: bool = False,
) -> bool:
    """Verify versions in CHANGELOG are in descending order (newest first).

    Args:
        versions: Version strings in file order.
        quiet: Suppress output.

    Returns:
        True if ordering is correct.
    """
    if len(versions) <= 1:
        return True

    # Deduplicate while preserving order for comparison
    seen: set[str] = set()
    unique: list[str] = []
    for v in versions:
        if v not in seen:
            unique.append(v)
            seen.add(v)

    misordered = [
        (unique[i], unique[i + 1])
        for i in range(len(unique) - 1)
        if _version_key(unique[i]) < _version_key(unique[i + 1])
    ]

    if misordered and not quiet:
        print(f"\n  Misordered versions ({len(misordered)}):")
        for before, after in misordered:
            print(f"    - {before} appears before {after} (should be after)")

    return len(misordered) == 0


def compare_versions(
    changelog_versions: list[str],
    tag_versions: list[str],
    *,
    verbose: bool = False,
    quiet: bool = False,
) -> int:
    """Compare changelog versions against git tags and report differences.

    Also checks for duplicate entries and correct ordering in the changelog.

    Args:
        changelog_versions: Versions found in CHANGELOG.md.
        tag_versions: Versions found in git tags.
        verbose: Print detailed output.
        quiet: Suppress all output (exit code only).

    Returns:
        Exit code: 0 if in sync, 1 if drift detected.
    """
    changelog_set = set(changelog_versions)
    tag_set = set(tag_versions)

    in_changelog_not_tagged = sorted(changelog_set - tag_set, key=_version_key)
    tagged_not_in_changelog = sorted(tag_set - changelog_set, key=_version_key)
    in_sync = sorted(changelog_set & tag_set, key=_version_key)

    # Print header first, before sub-checks that may also print
    if not quiet:
        print("CHANGELOG vs Git Tags")
        print("=" * 50)
        print(f"  CHANGELOG versions: {len(changelog_versions)}")
        print(f"  Git tag versions:   {len(tag_versions)}")
        print(f"  In sync:            {len(in_sync)}")

    # Additional checks (printed under the header)
    duplicates = check_duplicates(changelog_versions, quiet=quiet)
    ordering_ok = check_ordering(changelog_versions, quiet=quiet)

    has_drift = bool(
        in_changelog_not_tagged
        or tagged_not_in_changelog
        or duplicates
        or not ordering_ok
    )

    if not quiet:
        if in_changelog_not_tagged:
            print(f"\n  In CHANGELOG but not tagged ({len(in_changelog_not_tagged)}):")
            for v in in_changelog_not_tagged:
                print(f"    - {v}")

        if tagged_not_in_changelog:
            print(f"\n  Tagged but not in CHANGELOG ({len(tagged_not_in_changelog)}):")
            for v in tagged_not_in_changelog:
                print(f"    - {v}")

        if verbose and in_sync:
            print(f"\n  In sync ({len(in_sync)}):")
            for v in in_sync:
                print(f"    - {v}")

        if not has_drift:
            print("\nAll versions are in sync.")
        else:
            print("\nDrift detected between CHANGELOG.md and git tags.")

    return 1 if has_drift else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point for changelog_check.

    Returns:
        Exit code from compare_versions().
    """
    parser = argparse.ArgumentParser(
        description="Verify CHANGELOG.md entries match git tags.",
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show versions that are in sync",
    )
    verbosity.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output; exit code only (for CI)",
    )
    parser.add_argument(
        "--changelog-path",
        type=Path,
        default=CHANGELOG,
        help="Path to CHANGELOG.md (default: %(default)s)",
    )
    args = parser.parse_args()

    changelog_path: Path = args.changelog_path
    if not changelog_path.exists():
        if not args.quiet:
            print(f"CHANGELOG.md not found at {changelog_path}")
        return 1

    changelog_versions = get_changelog_versions(changelog_path)
    tag_versions = get_git_tag_versions()

    return compare_versions(
        changelog_versions,
        tag_versions,
        verbose=args.verbose,
        quiet=args.quiet,
    )


if __name__ == "__main__":
    sys.exit(main())
