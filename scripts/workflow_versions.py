#!/usr/bin/env python3
"""Workflow action version manager for GitHub Actions workflow files.

Show all pinned GitHub Actions with their SHA hashes and version
comments, and update the ``# vX.Y.Z`` comments to match the actual
tag that each SHA points to (via the GitHub API).

Dependabot updates the SHA hashes in ``uses:`` lines but does **not**
touch the inline version comments. This script fills that gap.

Requirements:
    - Python 3.11+
    - Internet access (queries the GitHub API)
    - Optional: ``GITHUB_TOKEN`` env var for higher rate limits

Usage:
    python scripts/workflow_versions.py                # Show all actions
    python scripts/workflow_versions.py show           # Same as above
    python scripts/workflow_versions.py show --offline # Skip GitHub API
    python scripts/workflow_versions.py update-comments # Sync comments with resolved tags
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = ROOT / ".github" / "workflows"

# Matches:  uses: owner/repo@SHA # vX.Y.Z
#      or:  uses: owner/repo/sub@SHA # vX.Y.Z
#      or:  uses: owner/repo@SHA   (no comment)
_USES_RE = re.compile(
    r"""
    ^
    (?P<indent>\s*)                  # leading whitespace
    -?\s*uses:\s*                    # "uses:" key (with optional list marker)
    (?P<action>[A-Za-z0-9._-]+      # owner
        /[A-Za-z0-9._-]+            # repo
        (?:/[A-Za-z0-9._-]+)*)      # optional sub-path (e.g. /init, /analyze)
    @
    (?P<ref>[0-9a-fA-F]{40})        # full 40-char SHA
    (?P<trail>.*)                    # trailing content (comment or nothing)
    $
    """,
    re.VERBOSE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _gh_api(url: str) -> object:
    """Make a GET request to the GitHub API and return parsed JSON.

    Uses ``GITHUB_TOKEN`` / ``GH_TOKEN`` env var if available.
    Returns ``None`` on any failure.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            print(
                "  [!] GitHub API rate limit reached."
                " Set GITHUB_TOKEN env var for 5,000 req/hr"
                " (current: 60/hr unauthenticated).",
                file=sys.stderr,
            )
        elif exc.code == 404:
            pass  # repo or ref not found — expected for some lookups
        else:
            print(
                f"  [!] GitHub API error: HTTP {exc.code} for {url}",
                file=sys.stderr,
            )
        return None
    except urllib.error.URLError as exc:
        print(
            f"  [!] Network error: {exc.reason}",
            file=sys.stderr,
        )
        return None
    except TimeoutError:
        print(
            "  [!] GitHub API request timed out.",
            file=sys.stderr,
        )
        return None
    except json.JSONDecodeError:
        return None


def _peel_to_commit(repo_slug: str, tag_obj_sha: str) -> str | None:
    """Peel an annotated tag object to its underlying commit SHA."""
    url = f"https://api.github.com/repos/{repo_slug}/git/tags/{tag_obj_sha}"
    data = _gh_api(url)
    if isinstance(data, dict):
        return data.get("object", {}).get("sha")
    return None


def _tag_points_at(repo_slug: str, tag_name: str, sha: str) -> bool:
    """Check whether *tag_name* in *repo_slug* resolves to commit *sha*.

    Handles both lightweight and annotated tags.
    """
    url = f"https://api.github.com/repos/{repo_slug}/git/matching-refs/tags/{tag_name}"
    data = _gh_api(url)
    if not isinstance(data, list):
        return False

    for ref in data:
        ref_name = ref.get("ref", "").removeprefix("refs/tags/")
        if ref_name != tag_name:
            continue
        obj = ref.get("object", {})
        ref_sha = obj.get("sha", "")
        ref_type = obj.get("type", "")
        if ref_sha == sha:
            return True
        if ref_type == "tag":
            commit_sha = _peel_to_commit(repo_slug, ref_sha)
            return commit_sha == sha

    return False


def _resolve_tag_from_tags_api(
    repo_slug: str, sha: str,
) -> str | None:
    """Scan recent tags (up to 500) to find one pointing at *sha*.

    Used as a fallback when no existing comment tag is available.
    """
    for page in range(1, 6):
        url = (
            f"https://api.github.com/repos/{repo_slug}/tags"
            f"?per_page=100&page={page}"
        )
        data = _gh_api(url)
        if not data or not isinstance(data, list):
            break

        matching: list[str] = []
        for tag_info in data:
            tag_name = tag_info.get("name", "")
            commit_sha = tag_info.get("commit", {}).get("sha", "")
            if commit_sha == sha:
                matching.append(tag_name)

        if matching:
            matching.sort(key=lambda t: t.count("."), reverse=True)
            return matching[0]

        if len(data) < 100:
            break

    return None


def _resolve_tag(
    owner_repo: str, sha: str, *, hint_tag: str | None = None,
) -> str | None:
    """Resolve a commit SHA to a version tag via the GitHub API.

    When *hint_tag* is provided (from an existing inline comment),
    the function first verifies that the tag still points at *sha*.
    This avoids expensive iteration through hundreds of tags for
    repos like ``github/codeql-action`` that have thousands of tags.

    Falls back to scanning recent tags (up to 500) when no hint
    is available.

    Returns the tag name (e.g. ``v6.0.1``) or ``None``.
    """
    # Strip sub-path (e.g. github/codeql-action/init -> github/codeql-action)
    parts = owner_repo.split("/")
    repo_slug = f"{parts[0]}/{parts[1]}"

    # Strategy 1: verify the existing comment tag (fast, 1-2 API calls)
    if hint_tag:
        if _tag_points_at(repo_slug, hint_tag, sha):
            return hint_tag

    # Strategy 2: scan recent tags (slower, up to 5 pages)
    return _resolve_tag_from_tags_api(repo_slug, sha)


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


def scan_workflows(
    *, resolve_tags: bool = True,
) -> list[dict[str, str | None]]:
    """Find all ``uses: owner/repo@SHA`` lines across workflow files.

    Returns a list of dicts with keys:
        - ``file``: workflow filename
        - ``line``: 1-based line number
        - ``action``: action reference (e.g. ``actions/checkout``)
        - ``sha``: the full 40-char SHA
        - ``comment_tag``: tag from the existing inline comment (or None)
        - ``resolved_tag``: tag resolved via GitHub API (or None)
        - ``stale``: "yes" if comment_tag != resolved_tag
    """
    if not WORKFLOWS_DIR.is_dir():
        return []

    rows: list[dict[str, str | None]] = []
    seen_shas: dict[str, str | None] = {}  # "action@SHA" -> resolved tag

    for wf in sorted(WORKFLOWS_DIR.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            m = _USES_RE.match(line)
            if not m:
                continue

            action = m.group("action")
            sha = m.group("ref")
            trail = m.group("trail").strip()

            # Extract existing comment tag
            comment_tag: str | None = None
            if "#" in trail:
                comment_match = re.search(r"#\s*(v?\S+)", trail)
                if comment_match:
                    comment_tag = comment_match.group(1)

            # Resolve tag from SHA (cached per SHA)
            resolved_tag: str | None = None
            if resolve_tags:
                cache_key = f"{action}@{sha}"
                if cache_key in seen_shas:
                    resolved_tag = seen_shas[cache_key]
                else:
                    resolved_tag = _resolve_tag(
                        action, sha, hint_tag=comment_tag,
                    )
                    seen_shas[cache_key] = resolved_tag

            stale = ""
            if comment_tag and resolved_tag and comment_tag != resolved_tag:
                stale = "yes"
            elif not comment_tag and resolved_tag:
                stale = "missing"

            rows.append({
                "file": wf.name,
                "line": str(lineno),
                "action": action,
                "sha": sha,
                "comment_tag": comment_tag,
                "resolved_tag": resolved_tag,
                "stale": stale,
            })

    return rows


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def print_report(rows: list[dict[str, str | None]]) -> None:
    """Pretty-print the workflow action report."""
    if not rows:
        print("  No SHA-pinned actions found.")
        return

    w_file = max(len(r["file"] or "") for r in rows)
    w_action = max(len(r["action"] or "") for r in rows)
    w_ctag = max((len(r["comment_tag"] or "-") for r in rows), default=7)
    w_rtag = max((len(r["resolved_tag"] or "-") for r in rows), default=8)

    hdr = (
        f"  {'File':<{w_file}}  {'Action':<{w_action}}  "
        f"{'Comment':<{w_ctag}}  {'Resolved':<{w_rtag}}  Stale?"
    )
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    for r in rows:
        ctag = r["comment_tag"] or "-"
        rtag = r["resolved_tag"] or "-"
        flag = "^" if r["stale"] == "yes" else ("+" if r["stale"] == "missing" else "")
        print(
            f"  {r['file']:<{w_file}}  {r['action']:<{w_action}}  "
            f"{ctag:<{w_ctag}}  {rtag:<{w_rtag}}  {flag}"
        )


# ---------------------------------------------------------------------------
# Comment updater
# ---------------------------------------------------------------------------


def update_comments(rows: list[dict[str, str | None]]) -> int:
    """Update or add inline ``# vX.Y.Z`` comments on ``uses:`` lines.

    For every action line where the resolved tag differs from the
    comment (or where no comment exists), the comment is rewritten.

    Returns the total number of lines modified across all files.
    """
    # Group rows by file
    by_file: dict[str, list[dict[str, str | None]]] = {}
    for r in rows:
        fname = r["file"] or ""
        if r["resolved_tag"] and r["stale"] in ("yes", "missing"):
            by_file.setdefault(fname, []).append(r)

    modified_total = 0

    for fname, file_rows in by_file.items():
        wf_path = WORKFLOWS_DIR / fname
        text = wf_path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        modified = 0

        # Build a lookup: line number -> resolved tag
        updates: dict[int, str] = {}
        for r in file_rows:
            lineno = int(r["line"] or "0")
            tag = r["resolved_tag"] or ""
            if lineno and tag:
                updates[lineno] = tag

        for lineno, new_tag in updates.items():
            idx = lineno - 1
            if idx >= len(lines):
                continue

            line = lines[idx].rstrip("\n")
            m = _USES_RE.match(line)
            if not m:
                continue

            trail = m.group("trail")

            if "#" in trail:
                # Replace existing comment tag
                new_trail = re.sub(r"#\s*v?\S+", f"# {new_tag}", trail, count=1)
            else:
                # Append new comment
                new_trail = f" # {new_tag}"

            new_line = (
                f"{m.group('indent')}"
                f"{'- ' if line.lstrip().startswith('-') else ''}"
                f"uses: {m.group('action')}@{m.group('ref')}"
                f"{new_trail}\n"
            )

            if new_line != lines[idx]:
                lines[idx] = new_line
                modified += 1

        if modified:
            wf_path.write_text("".join(lines), encoding="utf-8")
            modified_total += modified

    return modified_total


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="workflow_versions",
        description=(
            "Show and update version comments on SHA-pinned "
            "GitHub Actions in .github/workflows/."
        ),
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    show_p = sub.add_parser(
        "show",
        help="Show all SHA-pinned actions with comment and resolved tags (default).",
    )
    show_p.add_argument(
        "--offline",
        action="store_true",
        help="Skip resolving tags via GitHub API (just show comment tags).",
    )

    sub.add_parser(
        "update-comments",
        help=(
            "Update inline version comments to match the tag each SHA "
            "resolves to. Requires GitHub API access."
        ),
    )

    return parser


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()
    command = args.command or "show"

    print(f"\nWorkflow action versions for {ROOT.name}\n")

    if not WORKFLOWS_DIR.is_dir():
        print(f"  No workflows directory found at {WORKFLOWS_DIR}")
        sys.exit(1)

    if command == "show":
        offline = getattr(args, "offline", False)
        rows = scan_workflows(resolve_tags=not offline)
        if not rows:
            print("  No SHA-pinned actions found in workflow files.")
            return
        print_report(rows)

        # Summary
        stale = [r for r in rows if r["stale"] in ("yes", "missing")]
        if stale:
            print(f"\n  {len(stale)} comment(s) need updating (^ = stale, + = missing)")
        else:
            print("\n  All comments are up to date.")

    elif command == "update-comments":
        rows = scan_workflows(resolve_tags=True)
        if not rows:
            print("  No SHA-pinned actions found.")
            return
        print_report(rows)

        stale = [r for r in rows if r["stale"] in ("yes", "missing")]
        if not stale:
            print("\n  All comments are already up to date.")
            return

        count = update_comments(rows)
        if count:
            print(f"\n  Updated {count} comment(s) across workflow files.")
        else:
            print("\n  No changes made.")

    print()


if __name__ == "__main__":
    main()
