#!/usr/bin/env python3
"""Workflow action version manager for GitHub Actions workflow files.

Show all pinned GitHub Actions with their SHA hashes and version
comments, and update the ``# vX.Y.Z`` comments to match the actual
tag that each SHA points to (via the GitHub API).

Dependabot updates the SHA hashes in ``uses:`` lines but does **not**
touch the inline version comments. This script fills that gap.

The ``update-comments`` command also annotates each ``uses:`` line
with a succinct description of the action (fetched from the action's
``action.yml`` metadata via the GitHub API). Lines that already have
a description are left unchanged; lines with only a version tag
receive a new ``# <description> (vX.Y.Z)`` annotation.

Requirements:
    - Python 3.11+
    - Internet access (queries the GitHub API)
    - Optional: ``GITHUB_TOKEN`` env var for higher rate limits

Usage:
    python scripts/workflow_versions.py                # Show all actions
    python scripts/workflow_versions.py show           # Same as above
    python scripts/workflow_versions.py show --offline # Skip GitHub API
    python scripts/workflow_versions.py update-comments # Sync comments + add descriptions
    python scripts/workflow_versions.py upgrade        # Upgrade ALL actions to latest
    python scripts/workflow_versions.py upgrade actions/checkout          # Upgrade one action
    python scripts/workflow_versions.py upgrade actions/checkout v6.1.0   # Pin to a version
"""

from __future__ import annotations

import argparse
import base64
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
        with urllib.request.urlopen(req, timeout=15) as resp:  # nosec B310
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
    repo_slug: str,
    sha: str,
) -> str | None:
    """Scan recent tags (up to 500) to find one pointing at *sha*.

    Used as a fallback when no existing comment tag is available.
    """
    for page in range(1, 6):
        url = f"https://api.github.com/repos/{repo_slug}/tags?per_page=100&page={page}"
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
    owner_repo: str,
    sha: str,
    *,
    hint_tag: str | None = None,
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
    if hint_tag and _tag_points_at(repo_slug, hint_tag, sha):
        return hint_tag

    # Strategy 2: scan recent tags (slower, up to 5 pages)
    return _resolve_tag_from_tags_api(repo_slug, sha)


# ---------------------------------------------------------------------------
# Latest release / tag-to-SHA resolution
# ---------------------------------------------------------------------------


def _latest_tag(repo_slug: str) -> str | None:
    """Return the most recent semver-style release tag for *repo_slug*.

    Tries the Releases API first (returns the tag of the latest
    published release).  If the release tag doesn't look like a
    version (e.g. ``codeql-bundle-v2.24.1``), falls back to
    scanning the first page of tags for the newest ``vX.Y.Z``
    style tag.
    """
    _semver_re = re.compile(r"^v?\d+\.\d+")

    # Strategy 1: latest release (fast, 1 API call)
    url = f"https://api.github.com/repos/{repo_slug}/releases/latest"
    data = _gh_api(url)
    if isinstance(data, dict):
        tag = data.get("tag_name", "")
        if tag and _semver_re.match(tag):
            return tag

    # Strategy 2: first semver tag on page 1
    url = f"https://api.github.com/repos/{repo_slug}/tags?per_page=30"
    data = _gh_api(url)
    if isinstance(data, list):
        for tag_info in data:
            tag = tag_info.get("name", "")
            if tag and _semver_re.match(tag):
                return tag

    return None


def _resolve_sha_for_tag(
    repo_slug: str,
    tag_name: str,
) -> str | None:
    """Resolve *tag_name* to its commit SHA.

    Handles both lightweight and annotated tags.
    """
    url = f"https://api.github.com/repos/{repo_slug}/git/matching-refs/tags/{tag_name}"
    data = _gh_api(url)
    if not isinstance(data, list):
        return None

    for ref in data:
        ref_name = ref.get("ref", "").removeprefix("refs/tags/")
        if ref_name != tag_name:
            continue
        obj = ref.get("object", {})
        ref_sha = obj.get("sha", "")
        ref_type = obj.get("type", "")
        if ref_type == "commit":
            return ref_sha
        if ref_type == "tag":
            return _peel_to_commit(repo_slug, ref_sha)

    return None


# ---------------------------------------------------------------------------
# Action descriptions
# ---------------------------------------------------------------------------


def _shorten_description(desc: str) -> str:
    """Shorten an action description to a succinct phrase.

    Strips common boilerplate prefixes (e.g. "This action …"),
    takes the first sentence, and truncates to keep inline
    comments readable.
    """
    # Strip boilerplate prefixes
    desc = re.sub(
        r"^(This action\s+|"
        r"A GitHub Action (that |for |to )|"
        r"GitHub Action[,]?\s*(that |for |to )?)",
        "",
        desc,
        flags=re.IGNORECASE,
    )
    # Take first sentence (up to period, exclamation, or semicolon)
    sentence_match = re.match(r"^([^.!;]+)", desc)
    if sentence_match:
        desc = sentence_match.group(1).strip()
    # Strip trailing punctuation
    desc = desc.rstrip(".,;:!")
    # Capitalise first letter (preserve rest)
    if desc:
        desc = desc[0].upper() + desc[1:]
    # Truncate if too long
    if len(desc) > 50:
        truncated = desc[:47]
        last_space = truncated.rfind(" ")
        if last_space > 30:
            truncated = truncated[:last_space]
        desc = truncated + "…"
    return desc


def _action_description(action: str) -> str | None:
    """Fetch the one-line description from an action's ``action.yml``.

    Uses the GitHub Contents API to read the action metadata.
    Handles sub-path actions (e.g. ``github/codeql-action/init``
    looks up ``init/action.yml`` in ``github/codeql-action``).

    Returns a shortened description string, or ``None`` on failure.
    """
    parts = action.split("/")
    if len(parts) < 2:
        return None
    repo_slug = f"{parts[0]}/{parts[1]}"
    sub_path = "/".join(parts[2:]) if len(parts) > 2 else ""

    for filename in ("action.yml", "action.yaml"):
        path = f"{sub_path}/{filename}" if sub_path else filename
        url = f"https://api.github.com/repos/{repo_slug}/contents/{path}"
        data = _gh_api(url)
        if not isinstance(data, dict) or "content" not in data:
            continue

        try:
            raw = base64.b64decode(data["content"]).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            continue

        # Simple YAML parsing: find top-level ``description:`` key
        for yml_line in raw.splitlines():
            if not yml_line.startswith("description"):
                continue
            dm = re.match(r"^description:\s*(.+)$", yml_line)
            if not dm:
                continue
            value = dm.group(1).strip()
            # Skip block scalar indicators
            if value in (">", "|", ">-", "|-", ""):
                break
            # Remove surrounding quotes
            if len(value) >= 2 and value[0] in ("'", '"') and value[-1] == value[0]:
                value = value[1:-1]
            return _shorten_description(value)

    return None


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


def _repo_slug(action: str) -> str:
    """Strip sub-path from an action reference to get ``owner/repo``."""
    parts = action.split("/")
    return f"{parts[0]}/{parts[1]}"


def scan_workflows(
    *,
    resolve_tags: bool = True,
    check_latest: bool = False,
) -> list[dict[str, str | None]]:
    """Find all ``uses: owner/repo@SHA`` lines across workflow files.

    Returns a list of dicts with keys:
        - ``file``: workflow filename
        - ``line``: 1-based line number
        - ``action``: action reference (e.g. ``actions/checkout``)
        - ``sha``: the full 40-char SHA
        - ``comment_tag``: tag from the existing inline comment (or None)
        - ``resolved_tag``: tag resolved via GitHub API (or None)
        - ``latest_tag``: newest release tag (or None)
        - ``stale``: "yes" | "missing" | "no-desc" | ""
        - ``upgradable``: "yes" if latest_tag differs from current
        - ``has_description``: "yes" if comment has a description
    """
    if not WORKFLOWS_DIR.is_dir():
        return []

    rows: list[dict[str, str | None]] = []
    seen_shas: dict[str, str | None] = {}  # "action@SHA" -> resolved tag
    seen_latest: dict[str, str | None] = {}  # repo_slug -> latest tag

    for wf in sorted(WORKFLOWS_DIR.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            m = _USES_RE.match(line)
            if not m:
                continue

            action = m.group("action")
            sha = m.group("ref")
            trail = m.group("trail").strip()
            slug = _repo_slug(action)

            # Extract existing comment tag and detect description
            comment_tag: str | None = None
            has_desc = False
            if "#" in trail:
                # Try: description with version in parens "# Desc (v1.2.3)"
                paren_match = re.search(
                    r"\((v?\d+\.\d+[\.\d]*)\)",
                    trail,
                )
                if paren_match:
                    comment_tag = paren_match.group(1)
                    has_desc = True
                else:
                    # Fallback: bare version tag "# v1.2.3"
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
                        action,
                        sha,
                        hint_tag=comment_tag,
                    )
                    seen_shas[cache_key] = resolved_tag

            # Fetch latest tag (cached per repo)
            latest_tag: str | None = None
            if check_latest:
                if slug in seen_latest:
                    latest_tag = seen_latest[slug]
                else:
                    latest_tag = _latest_tag(slug)
                    seen_latest[slug] = latest_tag

            stale = ""
            if comment_tag and resolved_tag and comment_tag != resolved_tag:
                stale = "yes"
            elif not comment_tag and resolved_tag:
                stale = "missing"
            elif not has_desc and (comment_tag or resolved_tag):
                stale = "no-desc"

            current = resolved_tag or comment_tag
            upgradable = (
                "yes" if current and latest_tag and current != latest_tag else ""
            )

            rows.append(
                {
                    "file": wf.name,
                    "line": str(lineno),
                    "action": action,
                    "sha": sha,
                    "comment_tag": comment_tag,
                    "resolved_tag": resolved_tag,
                    "latest_tag": latest_tag,
                    "stale": stale,
                    "upgradable": upgradable,
                    "has_description": "yes" if has_desc else "",
                }
            )

    return rows


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def print_report(rows: list[dict[str, str | None]]) -> None:
    """Pretty-print the workflow action report."""
    if not rows:
        print("  No SHA-pinned actions found.")
        return

    has_latest = any(r.get("latest_tag") for r in rows)

    w_file = max(len(r["file"] or "") for r in rows)
    w_action = max(len(r["action"] or "") for r in rows)
    w_ctag = max((len(r["comment_tag"] or "-") for r in rows), default=7)
    w_rtag = max((len(r["resolved_tag"] or "-") for r in rows), default=8)

    if has_latest:
        w_ltag = max(
            (len(r["latest_tag"] or "-") for r in rows),
            default=6,
        )
        hdr = (
            f"  {'File':<{w_file}}  {'Action':<{w_action}}  "
            f"{'Comment':<{w_ctag}}  {'Resolved':<{w_rtag}}  "
            f"{'Latest':<{w_ltag}}  Upgrade?"
        )
    else:
        w_ltag = 0
        hdr = (
            f"  {'File':<{w_file}}  {'Action':<{w_action}}  "
            f"{'Comment':<{w_ctag}}  {'Resolved':<{w_rtag}}  Stale?"
        )
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    for r in rows:
        ctag = r["comment_tag"] or "-"
        rtag = r["resolved_tag"] or "-"

        if has_latest:
            ltag = r.get("latest_tag") or "-"
            uflag = "^" if r.get("upgradable") == "yes" else ""
            print(
                f"  {r['file']:<{w_file}}  {r['action']:<{w_action}}  "
                f"{ctag:<{w_ctag}}  {rtag:<{w_rtag}}  "
                f"{ltag:<{w_ltag}}  {uflag}"
            )
        else:
            flag_map = {"yes": "^", "missing": "+", "no-desc": "d"}
            flag = flag_map.get(r["stale"] or "", "")
            print(
                f"  {r['file']:<{w_file}}  {r['action']:<{w_action}}  "
                f"{ctag:<{w_ctag}}  {rtag:<{w_rtag}}  {flag}"
            )


# ---------------------------------------------------------------------------
# Comment updater
# ---------------------------------------------------------------------------


def update_comments(rows: list[dict[str, str | None]]) -> int:
    """Update or add inline ``# <description> (vX.Y.Z)`` comments.

    For every action line where the resolved tag differs from the
    comment, where no comment exists, or where a description is
    missing, the comment is rewritten with a succinct description
    (fetched from the action's ``action.yml``) and the resolved tag.

    Returns the total number of lines modified across all files.
    """
    # Group rows by file — include no-desc alongside yes/missing
    by_file: dict[str, list[dict[str, str | None]]] = {}
    for r in rows:
        fname = r["file"] or ""
        tag = r["resolved_tag"] or r["comment_tag"] or ""
        if tag and r["stale"] in ("yes", "missing", "no-desc"):
            by_file.setdefault(fname, []).append(r)

    if not by_file:
        return 0

    # Fetch descriptions for unique actions that need them
    desc_cache: dict[str, str | None] = {}
    actions_needing_desc = {
        r["action"] or ""
        for r in rows
        if r.get("has_description") != "yes"
        and r["stale"] in ("yes", "missing", "no-desc")
    }
    actions_needing_desc.discard("")
    if actions_needing_desc:
        print(f"\n  Fetching descriptions for {len(actions_needing_desc)} action(s) …")
    for action in sorted(actions_needing_desc):
        if action not in desc_cache:
            desc_cache[action] = _action_description(action)
            status = desc_cache[action] or "(not found)"
            print(f"    {action}: {status}")

    modified_total = 0

    for fname, file_rows in by_file.items():
        wf_path = WORKFLOWS_DIR / fname
        text = wf_path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        modified = 0

        # Build a lookup: line number -> (tag, action, has_desc)
        updates: dict[int, tuple[str, str, bool]] = {}
        for r in file_rows:
            lineno = int(r["line"] or "0")
            tag = r["resolved_tag"] or r["comment_tag"] or ""
            action = r["action"] or ""
            has_desc = r.get("has_description") == "yes"
            if lineno and tag:
                updates[lineno] = (tag, action, has_desc)

        for lineno, (new_tag, action, has_desc) in updates.items():
            idx = lineno - 1
            if idx >= len(lines):
                continue

            line = lines[idx].rstrip("\n")
            m = _USES_RE.match(line)
            if not m:
                continue

            trail = m.group("trail")
            desc = desc_cache.get(action) if not has_desc else None

            if "#" in trail:
                if has_desc:
                    # Already has description — just update version in parens
                    new_trail = re.sub(
                        r"\(v?\d+\.\d+[\.\d]*\)",
                        f"({new_tag})",
                        trail,
                        count=1,
                    )
                else:
                    # No description — rewrite entire comment
                    if desc:
                        new_trail = re.sub(
                            r"#\s*v?\S+.*",
                            f"# {desc} ({new_tag})",
                            trail,
                            count=1,
                        )
                    else:
                        new_trail = re.sub(
                            r"#\s*v?\S+",
                            f"# {new_tag}",
                            trail,
                            count=1,
                        )
            else:
                # No comment at all
                new_trail = f" # {desc} ({new_tag})" if desc else f" # {new_tag}"

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
# Upgrade
# ---------------------------------------------------------------------------


def upgrade_action(
    action: str,
    target_tag: str,
    rows: list[dict[str, str | None]],
) -> int:
    """Upgrade all occurrences of *action* to *target_tag*.

    Resolves the tag to a commit SHA via the GitHub API, then
    rewrites every matching ``uses:`` line (SHA + comment).

    Returns the number of lines modified.
    """
    slug = _repo_slug(action)
    new_sha = _resolve_sha_for_tag(slug, target_tag)
    if not new_sha:
        print(f"  [!] Could not resolve {target_tag} for {slug}")
        return 0

    # Group affected rows by file
    by_file: dict[str, list[dict[str, str | None]]] = {}
    for r in rows:
        if _repo_slug(r["action"] or "") == slug:
            fname = r["file"] or ""
            by_file.setdefault(fname, []).append(r)

    modified_total = 0

    for fname, file_rows in by_file.items():
        wf_path = WORKFLOWS_DIR / fname
        text = wf_path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        modified = 0

        for r in file_rows:
            idx = int(r["line"] or "0") - 1
            if idx < 0 or idx >= len(lines):
                continue

            line = lines[idx].rstrip("\n")
            m = _USES_RE.match(line)
            if not m:
                continue

            trail = m.group("trail")

            # Update the version in the comment
            if "#" in trail:
                # Replace version in parens: (v1.2.3) -> (v2.0.0)
                new_trail = re.sub(
                    r"\(v?\d+\.\d+[\.\d]*\)",
                    f"({target_tag})",
                    trail,
                )
                # Also handle bare "# v1.2.3" style
                if new_trail == trail:
                    new_trail = re.sub(
                        r"#\s*v?\d+\.\d+\S*",
                        f"# {target_tag}",
                        trail,
                        count=1,
                    )
            else:
                new_trail = f" # {target_tag}"

            new_line = (
                f"{m.group('indent')}"
                f"{'- ' if line.lstrip().startswith('-') else ''}"
                f"uses: {m.group('action')}@{new_sha}"
                f"{new_trail}\n"
            )

            if new_line != lines[idx]:
                lines[idx] = new_line
                modified += 1

        if modified:
            wf_path.write_text("".join(lines), encoding="utf-8")
            modified_total += modified

    return modified_total


def upgrade_all_actions(
    rows: list[dict[str, str | None]],
) -> int:
    """Upgrade all actions that have a newer version available.

    Returns the number of lines modified.
    """
    # Collect unique (slug, latest_tag) pairs
    seen: set[str] = set()
    upgrades: list[tuple[str, str]] = []
    for r in rows:
        if r.get("upgradable") != "yes":
            continue
        action = r["action"] or ""
        slug = _repo_slug(action)
        latest = r.get("latest_tag") or ""
        if slug not in seen and latest:
            seen.add(slug)
            upgrades.append((action, latest))

    modified_total = 0
    for action, target_tag in upgrades:
        slug = _repo_slug(action)
        print(f"  {slug}: upgrading to {target_tag} …")
        count = upgrade_action(action, target_tag, rows)
        if count:
            print(f"    updated {count} line(s)")
            modified_total += count
        else:
            print("    no changes")

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
            "Update inline version comments and add action descriptions. "
            "Comments are rewritten as '# <description> (vX.Y.Z)'. "
            "Requires GitHub API access."
        ),
    )

    upgrade_p = sub.add_parser(
        "upgrade",
        help="Upgrade actions to their latest release (or a specific version).",
    )
    upgrade_p.add_argument(
        "action",
        nargs="?",
        default=None,
        help=(
            "Action to upgrade (e.g. actions/checkout). "
            "Omit to upgrade all upgradable actions."
        ),
    )
    upgrade_p.add_argument(
        "version",
        nargs="?",
        default=None,
        help="Target version tag (e.g. v6.1.0). Omit for latest.",
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
        rows = scan_workflows(
            resolve_tags=not offline,
            check_latest=not offline,
        )
        if not rows:
            print("  No SHA-pinned actions found in workflow files.")
            return
        print_report(rows)

        # Summary
        stale = [r for r in rows if r["stale"] in ("yes", "missing")]
        no_desc = [r for r in rows if r["stale"] == "no-desc"]
        upgradable = [r for r in rows if r.get("upgradable") == "yes"]
        if stale or no_desc:
            parts: list[str] = []
            if stale:
                parts.append(
                    f"{len(stale)} version(s) (^ = stale, + = missing)",
                )
            if no_desc:
                parts.append(f"{len(no_desc)} description(s) (d = no desc)")
            print(f"\n  Needs updating: {', '.join(parts)}")
        else:
            print("\n  All comments are up to date.")

        # Dedupe upgradable by repo slug
        seen_slugs: set[str] = set()
        unique_upgradable: list[dict[str, str | None]] = []
        for r in upgradable:
            slug = _repo_slug(r["action"] or "")
            if slug not in seen_slugs:
                seen_slugs.add(slug)
                unique_upgradable.append(r)
        if unique_upgradable:
            print(
                f"  {len(unique_upgradable)} action(s) can be "
                f"upgraded (^ = upgrade available)",
            )

    elif command == "update-comments":
        rows = scan_workflows(resolve_tags=True)
        if not rows:
            print("  No SHA-pinned actions found.")
            return
        print_report(rows)

        needs_update = [r for r in rows if r["stale"] in ("yes", "missing", "no-desc")]
        if not needs_update:
            print("\n  All comments are already up to date.")
            return

        count = update_comments(rows)
        if count:
            print(f"\n  Updated {count} comment(s) across workflow files.")
        else:
            print("\n  No changes made.")

    elif command == "upgrade":
        action_arg = getattr(args, "action", None)
        version_arg = getattr(args, "version", None)

        if action_arg:
            # Upgrade a specific action
            rows = scan_workflows(resolve_tags=True, check_latest=True)
            if not rows:
                print("  No SHA-pinned actions found.")
                sys.exit(1)

            # Verify the action exists in workflows
            slug = _repo_slug(action_arg)
            matching = [r for r in rows if _repo_slug(r["action"] or "") == slug]
            if not matching:
                print(f"  '{action_arg}' not found in workflow files.")
                sys.exit(1)

            if version_arg:
                target = version_arg
            else:
                target = matching[0].get("latest_tag")
                if not target:
                    print(f"  Could not determine latest tag for {slug}.")
                    sys.exit(1)

            current = matching[0].get("resolved_tag") or matching[0].get("comment_tag")
            print(f"  {slug}: {current} -> {target}")
            count = upgrade_action(action_arg, target, rows)
            if count:
                print(f"\n  Upgraded {count} line(s) across workflow files.")
            else:
                print("\n  No changes made.")
        else:
            # Upgrade all
            rows = scan_workflows(resolve_tags=True, check_latest=True)
            if not rows:
                print("  No SHA-pinned actions found.")
                return
            print_report(rows)

            upgradable = [r for r in rows if r.get("upgradable") == "yes"]
            if not upgradable:
                print("\n  All actions are already at their latest version.")
                return

            # Dedupe by slug
            seen_slugs_u: set[str] = set()
            unique: list[dict[str, str | None]] = []
            for r in upgradable:
                s = _repo_slug(r["action"] or "")
                if s not in seen_slugs_u:
                    seen_slugs_u.add(s)
                    unique.append(r)

            print(f"\n  Upgrading {len(unique)} action(s) …\n")
            count = upgrade_all_actions(rows)
            if count:
                print(f"\n  Upgraded {count} line(s) across workflow files.")
            else:
                print("\n  No changes made.")

    print()


if __name__ == "__main__":
    main()
