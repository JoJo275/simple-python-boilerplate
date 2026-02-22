#!/usr/bin/env python3
"""Verify CHANGELOG.md entries match git tags.

Compares version headings in CHANGELOG.md against git tags to detect
drift between what release-please generates and what's actually tagged.

Usage::

    python scripts/changelog_check.py
    python scripts/changelog_check.py --verbose
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
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    versions = []
    for line in result.stdout.strip().splitlines():
        match = TAG_RE.match(line.strip())
        if match:
            versions.append(match.group(1))

    return sorted(versions, key=_version_key)


def _version_key(version: str) -> tuple[int, ...]:
    """Convert a version string to a sortable tuple.

    Args:
        version: Semver-like version string (e.g., "1.2.3").

    Returns:
        Tuple of integers for sorting.
    """
    parts = []
    for part in version.split("."):
        # Strip any pre-release suffix for sorting
        numeric = re.match(r"(\d+)", part)
        parts.append(int(numeric.group(1)) if numeric else 0)
    return tuple(parts)


def compare_versions(
    changelog_versions: list[str],
    tag_versions: list[str],
    verbose: bool = False,
) -> int:
    """Compare changelog versions against git tags and report differences.

    Args:
        changelog_versions: Versions found in CHANGELOG.md.
        tag_versions: Versions found in git tags.
        verbose: Print detailed output.

    Returns:
        Exit code: 0 if in sync, 1 if drift detected.
    """
    changelog_set = set(changelog_versions)
    tag_set = set(tag_versions)

    in_changelog_not_tagged = sorted(changelog_set - tag_set, key=_version_key)
    tagged_not_in_changelog = sorted(tag_set - changelog_set, key=_version_key)
    in_sync = sorted(changelog_set & tag_set, key=_version_key)

    has_drift = bool(in_changelog_not_tagged or tagged_not_in_changelog)

    print("CHANGELOG vs Git Tags")
    print("=" * 50)
    print(f"  CHANGELOG versions: {len(changelog_versions)}")
    print(f"  Git tag versions:   {len(tag_versions)}")
    print(f"  In sync:            {len(in_sync)}")

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
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show versions that are in sync",
    )
    args = parser.parse_args()

    if not CHANGELOG.exists():
        print(f"CHANGELOG.md not found at {CHANGELOG}")
        return 1

    changelog_versions = get_changelog_versions(CHANGELOG)
    tag_versions = get_git_tag_versions()

    return compare_versions(changelog_versions, tag_versions, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
