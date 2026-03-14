#!/usr/bin/env python3
"""Git-focused health check and information dashboard.

Displays a comprehensive overview of the repository's git state:
branches, remotes, current working branch, recent commits,
release-please branches, and git-related health checks.

Flags::

    --no-color        Disable colored output
    --json            Output results as JSON (for CI integration)
    --export-config   Export full git config reference to Markdown file
    --apply-from PATH Apply desired values from an edited reference file
    --fix             Auto-apply recommended git config settings
    --dry-run         With --fix or --apply-from, preview without applying
    --new-branch      Interactive branch creation off origin/main
    --watch [N]       Re-run dashboard every N seconds (default: 10)
    --version         Print version and exit

Usage::

    python scripts/git_doctor.py
    python scripts/git_doctor.py --json
    python scripts/git_doctor.py --no-color
    python scripts/git_doctor.py --fix
    python scripts/git_doctor.py --fix --dry-run
    python scripts/git_doctor.py --new-branch
    python scripts/git_doctor.py --watch
    python scripts/git_doctor.py --watch 30
    python scripts/git_doctor.py --export-config
    python scripts/git_doctor.py --apply-from git-config-reference.md
    python scripts/git_doctor.py --apply-from git-config-reference.md --dry-run

Workflow for editing and applying config::

    1. Export:   python scripts/git_doctor.py --export-config
    2. Edit:     Open git-config-reference.md, change "Desired value" cells
    3. Preview:  python scripts/git_doctor.py --apply-from git-config-reference.md --dry-run
    4. Apply:    python scripts/git_doctor.py --apply-from git-config-reference.md

.. note::
   ``--export-config`` writes to ``git-config-reference.md`` by default
   (or a custom path if provided). The file is **replaced entirely** on
   each run — it is a generated artifact, not a hand-edited document.
   The exported reference covers commonly used git configurations (62 keys
   across 17 sections) — not every possible git config key.

Customisation notes:

- **Merge-base freshness threshold**: ``check_merge_base_freshness()``
  warns when the default branch is >10 commits ahead of the merge-base.
  Adjust the threshold (``default_ahead <= 10``) if your workflow merges
  main less frequently.
- **Branch commit counts**: ``get_recent_branches_with_stats()`` shows
  commits *unique* to each branch (since diverging from default), not
  total reachable commits.  ``get_branch_commit_count()`` still returns
  the total if needed.
- **Unmerged branches**: Branches whose remote tracking ref is ``[gone]``
  (deleted on the remote) are excluded by default — they were almost
  certainly merged via PR (rebase-merge or squash-merge).  See the TODO
  in ``get_unmerged_branches()`` if your team's workflow differs.
  The three merge strategies GitHub supports are:

  1. **Rebase-merge** — replays branch commits on top of the target;
     produces a linear history with the original commits preserved.
  2. **Squash-merge** — condenses all branch commits into a single
     commit on the target; original commit SHAs are lost.
  3. **Merge commit** — creates a merge commit; original commits are
     reachable via the merge parent and ``--no-merged`` works correctly.

  Because rebase-merge and squash-merge both create new commit objects,
  ``git branch --no-merged`` can't detect that the branch's *content*
  was already integrated.  Filtering out ``[gone]`` branches handles
  this correctly for normal post-PR-merge cleanup workflows.
- **Branch activity accuracy**: ``get_recent_branches_with_stats()`` uses
  ``origin/<default>`` (not the local ref) as the comparison base so
  that stats remain accurate even when the local default branch is stale.
- **Auto-fetch**: The script runs ``git fetch --all --prune`` at startup
  to ensure remote-tracking refs are current and deleted remote branches
  are cleaned up.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess  # nosec B404
import sys
import time
from collections.abc import Callable
from datetime import UTC

from _colors import Colors
from _colors import status_icon as _icon
from _colors import supports_color as _supports_color
from _colors import supports_unicode as _supports_unicode
from _colors import unicode_symbols as _unicode_symbols
from _doctor_common import extract_repo_slug, read_pyproject
from _imports import find_repo_root
from _progress import Spinner

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "2.1.0"

logger = logging.getLogger(__name__)

ROOT = find_repo_root()

_GIT: str | None = shutil.which("git")

# ---------------------------------------------------------------------------
# Recommended config values for --fix
# ---------------------------------------------------------------------------

# Safe, opinionated defaults that benefit most development workflows.
# Only keys with clear, non-destructive recommended values are included.
# Keys that depend on personal preference (e.g. core.editor) are omitted.
RECOMMENDED_CONFIGS: list[tuple[str, str, str]] = [
    # (key, value, scope)
    ("pull.rebase", "true", "global"),
    ("push.default", "current", "global"),
    ("push.autoSetupRemote", "true", "global"),
    ("fetch.prune", "true", "global"),
    ("fetch.prunetags", "true", "global"),
    ("merge.conflictstyle", "zdiff3", "global"),
    ("rebase.autostash", "true", "global"),
    ("rebase.autoSquash", "true", "global"),
    ("rerere.enabled", "true", "global"),
    ("branch.sort", "-committerdate", "global"),
    ("diff.algorithm", "histogram", "global"),
    ("init.defaultBranch", "main", "global"),
]

# Quick lookup: key -> recommended value (for terminal display hints)
_RECOMMENDED_LOOKUP: dict[str, str] = {k: v for k, v, _ in RECOMMENDED_CONFIGS}

# ---------------------------------------------------------------------------
# Git configuration catalog (used by --export-config)
# ---------------------------------------------------------------------------

# Curated catalog of commonly used git configurations.
# This is NOT exhaustive — git has 500+ keys; this covers the ones
# most relevant to day-to-day development workflows.
# Format: (key, recommended_scope, description, recommendation)
GIT_CONFIG_CATALOG: list[tuple[str, str, str, str]] = [
    # ── Core ──
    (
        "core.autocrlf",
        "global",
        "Line ending conversion: 'true'=CRLF<>LF (Windows), 'input'=LF on commit only, 'false'=off",
        "'input' on macOS/Linux, 'true' on Windows",
    ),
    (
        "core.editor",
        "global",
        "Default text editor for commit messages, interactive rebase, and other editing",
        "e.g. 'code --wait', 'vim', 'nano'",
    ),
    (
        "core.pager",
        "global",
        "Pager program for git output (log, diff). 'delta' gives syntax-highlighted diffs",
        "'delta' for better diffs, or 'less -FRX'",
    ),
    (
        "core.excludesfile",
        "global",
        "Path to a global gitignore file applied to ALL repositories (editor/OS ignores)",
        "'~/.gitignore_global'",
    ),
    (
        "core.filemode",
        "local",
        "Track file permission (executable bit) changes. Windows doesn't support Unix perms",
        "'false' on Windows if you see spurious permission diffs",
    ),
    (
        "core.longpaths",
        "global",
        "Enable paths longer than 260 chars on Windows. Required for deep node_modules",
        "'true' on Windows",
    ),
    (
        "core.quotepath",
        "global",
        "Quote non-ASCII characters in pathnames. Disable to see UTF-8 filenames correctly",
        "'false' to display non-ASCII filenames correctly",
    ),
    (
        "core.hooksPath",
        "local",
        "Custom directory for git hooks. Usually managed by pre-commit",
        "Leave unset when using pre-commit",
    ),
    (
        "core.eol",
        "local",
        "Line ending style in working directory: 'lf', 'crlf', or 'native'",
        "'lf' for cross-platform projects, or use .gitattributes",
    ),
    (
        "core.safecrlf",
        "global",
        "Abort/warn if line ending conversion would lose data",
        "'warn' for safety without blocking",
    ),
    (
        "core.symlinks",
        "local",
        "Whether working tree supports symbolic links (auto-detected on clone)",
        "Auto-detected; 'false' if symlinks cause issues on Windows",
    ),
    (
        "core.whitespace",
        "local",
        "Which whitespace problems git notices (trailing-space, space-before-tab, etc.)",
        "Default is fine for most projects",
    ),
    (
        "core.ignorecase",
        "local",
        "Whether filenames are case-insensitive (auto-detected on clone). Affects 'git mv'",
        "Auto-detected; usually 'true' on Windows/macOS, 'false' on Linux",
    ),
    # ── Fetch ──
    (
        "fetch.prune",
        "global",
        "Auto-remove stale remote-tracking branches on every fetch",
        "'true' -- avoids stale branch accumulation",
    ),
    ("fetch.prunetags", "global", "Auto-remove stale remote tags on fetch", "'true'"),
    (
        "fetch.fsckobjects",
        "global",
        "Verify integrity of objects received during fetch (catches corruption)",
        "'true' for security",
    ),
    # ── Pull ──
    (
        "pull.rebase",
        "global",
        "Rebase local commits on top of upstream when pulling. Gives linear history",
        "'true' for linear history",
    ),
    (
        "pull.ff",
        "global",
        "Fast-forward behavior on pull: 'only' refuses merge commits, 'true' allows any merge",
        "'only' to prevent accidental merge commits",
    ),
    # ── Push ──
    (
        "push.default",
        "global",
        "What to push when no refspec given: 'current'=same-named branch, 'simple'=default",
        "'current' or 'simple'",
    ),
    (
        "push.autoSetupRemote",
        "global",
        "Auto-set upstream tracking on first push (no more --set-upstream). Git 2.37+",
        "'true'",
    ),
    (
        "push.followTags",
        "global",
        "Push annotated tags along with commits automatically",
        "'true' if you use annotated tags for releases",
    ),
    # ── Merge ──
    (
        "merge.ff",
        "local",
        "Fast-forward on merge: 'only'=refuse merge commits, 'false'=always create them",
        "'only' for linear history, 'false' for explicit merge commits",
    ),
    (
        "merge.conflictstyle",
        "global",
        "Conflict marker format: 'diff3'/'zdiff3' shows the common ancestor (3-way diff)",
        "'zdiff3' (git 2.35+) or 'diff3'",
    ),
    (
        "merge.tool",
        "global",
        "Default tool for resolving merge conflicts interactively",
        "e.g. 'vscode', 'meld', 'vimdiff'",
    ),
    (
        "merge.log",
        "global",
        "Include one-line descriptions of merged commits in merge commit message",
        "'true' for informative merge commits",
    ),
    # ── Rebase ──
    (
        "rebase.autostash",
        "global",
        "Auto-stash uncommitted changes before rebase, unstash after",
        "'true' -- prevents 'dirty worktree' errors",
    ),
    (
        "rebase.autoSquash",
        "global",
        "Auto-apply fixup!/squash! prefixes in interactive rebase (with --fixup)",
        "'true'",
    ),
    (
        "rebase.updateRefs",
        "global",
        "Auto-update stacked branch refs during rebase. Git 2.38+",
        "'true' for stacked branch workflows",
    ),
    # ── Rerere ──
    (
        "rerere.enabled",
        "global",
        "REuse REcorded Resolution -- remember and replay merge conflict fixes",
        "'true' -- saves time on repeated rebases",
    ),
    # ── Stash ──
    (
        "stash.showPatch",
        "global",
        "Show the patch (diff) in 'git stash show' instead of just a file stat summary",
        "'true' for detailed stash inspection",
    ),
    # ── Branch & Init ──
    (
        "branch.autosetuprebase",
        "global",
        "Auto-set pull.rebase for new tracking branches: 'always', 'local', 'remote', 'never'",
        "'always' if you prefer rebasing consistently",
    ),
    (
        "branch.sort",
        "global",
        "Default sort for 'git branch': '-committerdate' shows most recent first",
        "'-committerdate'",
    ),
    ("init.defaultBranch", "global", "Default branch name for 'git init'", "'main'"),
    (
        "tag.sort",
        "global",
        "Sort for 'git tag': 'version:refname' gives natural version ordering (v1.9 < v1.10)",
        "'version:refname'",
    ),
    # ── Identity & Signing ──
    (
        "user.name",
        "global",
        "Author name recorded in every commit. Use local scope for work-specific identity",
        "Your full name (required)",
    ),
    (
        "user.email",
        "global",
        "Author email recorded in every commit. Use local scope for per-project email",
        "Your email (required; local for work repos)",
    ),
    (
        "commit.gpgsign",
        "global",
        "Auto-sign every commit with GPG/SSH key. GitHub shows 'Verified' badge",
        "'true' for verified commits",
    ),
    (
        "tag.gpgsign",
        "global",
        "Auto-sign every tag with GPG/SSH key",
        "'true' if signing commits",
    ),
    (
        "gpg.format",
        "global",
        "Signing format: 'openpgp' (GPG) or 'ssh' (SSH keys -- simpler setup)",
        "'ssh' for SSH-based signing",
    ),
    (
        "gpg.ssh.allowedSignersFile",
        "global",
        "Allowed SSH public keys file for signature verification",
        "Set if using SSH signing for local verification",
    ),
    # ── Commit ──
    (
        "commit.template",
        "local",
        "Path to default commit message template shown in editor on 'git commit'",
        "'.gitmessage.txt' for this project",
    ),
    (
        "commit.verbose",
        "global",
        "Show diff of staged changes in commit message editor for review",
        "'true'",
    ),
    # ── Diff ──
    (
        "diff.algorithm",
        "global",
        "Diff algorithm: 'histogram' gives better results than default 'myers'",
        "'histogram'",
    ),
    (
        "diff.colorMoved",
        "global",
        "Highlight moved lines in diffs (not just added/deleted). Makes refactoring clearer",
        "'default' or 'zebra'",
    ),
    (
        "diff.colorMovedWS",
        "global",
        "Whitespace handling for moved-line detection",
        "'allow-indentation-change' with colorMoved",
    ),
    (
        "diff.tool",
        "global",
        "Default tool for side-by-side diff comparison",
        "e.g. 'vscode', 'meld', 'delta'",
    ),
    (
        "diff.renameLimit",
        "global",
        "Max files for rename detection. Increase if git misses renames in large changesets",
        "Increase (e.g. 5000) for large repos",
    ),
    (
        "diff.submodule",
        "global",
        "Submodule diff format: 'log' shows commit summaries, 'short' shows only SHAs",
        "'log' if you use submodules",
    ),
    # ── Log & Display ──
    (
        "log.date",
        "global",
        "Default date format for 'git log': 'relative', 'short', 'iso', 'local'",
        "'relative' or 'short'",
    ),
    (
        "color.ui",
        "global",
        "Enable colored output: 'auto' enables when stdout is a terminal",
        "'auto' (default in modern git)",
    ),
    (
        "column.ui",
        "global",
        "Display branch/tag listings in columns when terminal is wide enough",
        "'auto'",
    ),
    # ── Credential & Transfer ──
    (
        "credential.helper",
        "global",
        "How git stores credentials (passwords/tokens). 'manager' uses OS credential store",
        "'manager' (Windows), 'osxkeychain' (macOS), 'store' (Linux)",
    ),
    (
        "http.sslVerify",
        "global",
        "Verify SSL certs for HTTPS. Disabling is a security risk",
        "Keep 'true' (default); only disable for self-signed certs",
    ),
    (
        "transfer.fsckobjects",
        "global",
        "Verify object integrity during push/pull transfers",
        "'true' for data integrity",
    ),
    # ── Performance ──
    (
        "gc.auto",
        "global",
        "Threshold for auto garbage collection (loose object count)",
        "Default (6700) is fine; increase for busy repos",
    ),
    (
        "feature.manyFiles",
        "local",
        "Enable optimizations for repos with many files (untracked cache, fsmonitor)",
        "'true' for large repos",
    ),
    (
        "index.version",
        "local",
        "Index format version. V4 is more compact and faster",
        "'4' for large repos",
    ),
    # ── Help & UX ──
    (
        "help.autocorrect",
        "global",
        "Auto-correct mistyped commands: 'prompt'=ask, N=wait N deciseconds, '0'=off",
        "'prompt' or '10' (1 second delay)",
    ),
    (
        "status.showUntrackedFiles",
        "global",
        "Untracked file display: 'all'=individual files, 'normal'=group by directory",
        "'all' for complete visibility",
    ),
    # ── Advice ──
    (
        "advice.detachedHead",
        "global",
        "Show the advice message when entering detached HEAD state",
        "'false' to suppress if you frequently check out tags or SHAs",
    ),
    (
        "advice.statusHints",
        "global",
        "Show hints in 'git status' about staging, unstaging, and conflict resolution",
        "'true' (default) for beginners, 'false' for cleaner output",
    ),
    # ── Protocol ──
    (
        "protocol.version",
        "global",
        "Git protocol version: v2 is faster (partial clone, faster negotiation). Git 2.26+",
        "'2' (default in modern git)",
    ),
]

# ---------------------------------------------------------------------------
# Config section descriptions (used by terminal display and --export-config)
# ---------------------------------------------------------------------------

# One-line description of each logical config section.
# TODO (template users): Add descriptions for any custom sections you define
#   in CONFIG_SECTION_MAP.
SECTION_DESCRIPTIONS: dict[str, str] = {
    "Core": "Fundamental git behavior: line endings, editor, pager, file handling.",
    "Fetch": "How git retrieves objects and refs from remotes.",
    "Pull": "Behavior when pulling changes from a remote branch.",
    "Push": "Defaults for pushing commits to remotes.",
    "Merge": "How git handles merges and conflict markers.",
    "Rebase": "Rebase workflow helpers: auto-stash, fixup squashing, stacked refs.",
    "Rerere": "Reuse recorded resolutions for recurring merge conflicts.",
    "Stash": "Temporary work storage: stash display and behavior.",
    "Branch & Init": "Branch/tag display, sorting, and defaults for new repositories.",
    "Identity & Signing": "Author identity and GPG/SSH commit/tag signing.",
    "Commit": "Commit message templates and editor behavior.",
    "Diff": "Diff algorithm, moved-line detection, and rename handling.",
    "Log & Display": "Date format, color output, and column display for listings.",
    "Credential & Transfer": "Credential storage, SSL, and object integrity verification.",
    "Performance": "Garbage collection, index format, and large-repo optimizations.",
    "Help & UX": "Autocorrect, advice messages, and other UX settings.",
    "Protocol": "Git wire protocol version for network communication.",
}

# Section display names for the exported config reference.  Key-specific
# overrides take priority, then prefix-based defaults.  Keys not listed
# here use the capitalised key prefix (e.g. "core.editor" -> "Core").
CONFIG_SECTION_MAP: dict[str, str] = {
    # Prefix-based
    "branch": "Branch & Init",
    "init": "Branch & Init",
    "user": "Identity & Signing",
    "gpg": "Identity & Signing",
    "log": "Log & Display",
    "color": "Log & Display",
    "column": "Log & Display",
    "credential": "Credential & Transfer",
    "http": "Credential & Transfer",
    "transfer": "Credential & Transfer",
    "gc": "Performance",
    "feature": "Performance",
    "index": "Performance",
    "help": "Help & UX",
    "status": "Help & UX",
    "advice": "Help & UX",
    "stash": "Stash",
    # Key-specific (when prefix alone is ambiguous)
    "commit.gpgsign": "Identity & Signing",
    "tag.gpgsign": "Identity & Signing",
    "tag.sort": "Branch & Init",
}


def _config_section(key: str) -> str:
    """Return the display section name for a git config key."""
    if key in CONFIG_SECTION_MAP:
        return CONFIG_SECTION_MAP[key]
    prefix = key.split(".")[0]
    return CONFIG_SECTION_MAP.get(prefix, prefix.capitalize())


# Keys shown in terminal output (top 18 most useful for daily workflow).
# TODO (template users): Add or remove keys to match your team's workflow.
TERMINAL_CONFIG_KEYS: list[str] = [
    # Core
    "core.autocrlf",
    "core.editor",
    # Fetch / Pull / Push
    "fetch.prune",
    "pull.rebase",
    "pull.ff",
    "push.default",
    "push.autoSetupRemote",
    # Merge / Rebase
    "merge.ff",
    "merge.conflictstyle",
    "rebase.autostash",
    "rebase.autoSquash",
    "rerere.enabled",
    # Branch & Init
    "branch.autosetuprebase",
    "init.defaultBranch",
    # Commit & Signing
    "commit.template",
    "commit.gpgsign",
    "tag.gpgsign",
    # Diff
    "diff.algorithm",
]

# TODO (template users): Update HEALTH_CHECKS at the bottom of this file
#   if you add/remove git-related conventions (e.g. signed commits,
#   different branch naming, or GPG verification).


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _run_git(args: list[str], *, timeout: int = 15) -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    if _GIT is None:
        return 1, "", "git not found on PATH"
    try:
        result = subprocess.run(  # nosec B603
            [_GIT, *args],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "git command timed out"
    except OSError as exc:
        return 1, "", str(exc)


# ---------------------------------------------------------------------------
# Fetch & prune (keep remote-tracking refs current)
# ---------------------------------------------------------------------------


def _fetch_and_prune(*, timeout: int = 30) -> tuple[bool, str]:
    """Run ``git fetch --all --prune`` to refresh remote-tracking refs.

    This ensures the branch activity section works with accurate data
    and that deleted remote branches are cleaned up before we enumerate
    them.  Errors are non-fatal — the rest of the script still runs.
    """
    # TODO (template users): Increase the timeout if your repository has
    #   many remotes or a slow network connection.  Set to 0 to disable
    #   the auto-fetch entirely (the script will use whatever refs are
    #   already cached locally).
    code, out, err = _run_git(["fetch", "--all", "--prune"], timeout=timeout)
    if code == 0:
        return True, out or "fetched successfully"
    return False, err or "fetch failed"


# ---------------------------------------------------------------------------
# Information collectors
# ---------------------------------------------------------------------------


def get_current_branch() -> str:
    """Return the current branch name, or HEAD state."""
    code, out, _ = _run_git(["branch", "--show-current"])
    if code == 0 and out:
        return out
    # Detached HEAD — get short SHA
    code, out, _ = _run_git(["rev-parse", "--short", "HEAD"])
    return f"(detached HEAD: {out})" if code == 0 else "(unknown)"


def get_default_branch() -> str:
    """Return the default branch from origin/HEAD."""
    code, out, _ = _run_git(["symbolic-ref", "refs/remotes/origin/HEAD"])
    if code == 0 and out:
        # refs/remotes/origin/main -> main
        return out.rsplit("/", 1)[-1]
    return "(unknown)"


def get_remote_url() -> str:
    """Return the origin remote URL."""
    code, out, _ = _run_git(["remote", "get-url", "origin"])
    return out if code == 0 and out else "(no remote)"


def get_all_remotes() -> list[dict[str, str]]:
    """Return list of all configured remotes."""
    code, out, _ = _run_git(["remote", "-v"])
    if code != 0 or not out:
        return []
    remotes: dict[str, dict[str, str]] = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0]
            url = parts[1]
            direction = parts[2].strip("()") if len(parts) > 2 else "fetch"
            if name not in remotes:
                remotes[name] = {"name": name, "url": url, "direction": direction}
    return list(remotes.values())


def get_local_branches() -> list[dict[str, str]]:
    """Return local branches with tracking info."""
    code, out, _ = _run_git(
        [
            "branch",
            "-vv",
            "--format=%(refname:short)\t%(upstream:short)\t%(upstream:track)\t%(objectname:short)\t%(committerdate:relative)",
        ]
    )
    if code != 0 or not out:
        return []
    branches: list[dict[str, str]] = []
    for line in out.splitlines():
        parts = line.split("\t", 4)
        if len(parts) >= 1:
            branch: dict[str, str] = {"name": parts[0]}
            if len(parts) >= 2 and parts[1]:
                branch["tracking"] = parts[1]
            if len(parts) >= 3 and parts[2]:
                branch["status"] = parts[2]
            if len(parts) >= 4:
                branch["sha"] = parts[3]
            if len(parts) >= 5:
                branch["last_commit"] = parts[4]
            branches.append(branch)
    return branches


def get_remote_branches() -> list[str]:
    """Return remote branch names (excluding HEAD)."""
    code, out, _ = _run_git(["branch", "-r", "--format=%(refname:short)"])
    if code != 0 or not out:
        return []
    return [b for b in out.splitlines() if b and "HEAD" not in b]


def get_recent_commits(count: int = 5) -> list[dict[str, str]]:
    """Return recent commits on the current branch."""
    code, out, _ = _run_git(["log", f"-{count}", "--format=%h\t%s\t%an\t%ar"])
    if code != 0 or not out:
        return []
    commits: list[dict[str, str]] = []
    for line in out.splitlines():
        parts = line.split("\t", 3)
        if len(parts) >= 2:
            commit: dict[str, str] = {"sha": parts[0], "message": parts[1]}
            if len(parts) >= 3:
                commit["author"] = parts[2]
            if len(parts) >= 4:
                commit["date"] = parts[3]
            commits.append(commit)
    return commits


def get_stash_count() -> int:
    """Return the number of stash entries."""
    code, out, _ = _run_git(["stash", "list"])
    if code != 0 or not out:
        return 0
    return len(out.splitlines())


def get_tags(count: int = 5) -> list[str]:
    """Return recent tags sorted by creation date."""
    code, out, _ = _run_git(["tag", "--sort=-creatordate", f"--count={count}"])
    if code != 0 or not out:
        return []
    return [t for t in out.splitlines() if t]


def get_commit_count() -> int:
    """Return total commit count on the current branch."""
    code, out, _ = _run_git(["rev-list", "--count", "HEAD"])
    if code != 0 or not out:
        return 0
    try:
        return int(out)
    except ValueError:
        return 0


def get_repo_age() -> str:
    """Return the date of the first commit (repo creation proxy).

    Uses ``git rev-list --max-parents=0`` to find the root commit(s),
    then reads the relative date of the earliest one.  The previous
    approach (``git log --reverse -1``) was buggy because ``-1`` limits
    *before* ``--reverse``, giving the most-recent commit instead.
    """
    # Find root commit(s) — commits with no parents
    code, out, _ = _run_git(["rev-list", "--max-parents=0", "HEAD"])
    if code != 0 or not out:
        return "unknown"
    root_sha = out.splitlines()[0]
    code, date_str, _ = _run_git(["log", "-1", "--format=%ar", root_sha])
    return date_str if code == 0 and date_str else "unknown"


def get_contributors_count() -> int:
    """Return unique author count."""
    code, out, _ = _run_git(["shortlog", "-sn", "--all", "--no-merges"])
    if code != 0 or not out:
        return 0
    return len([line for line in out.splitlines() if line.strip()])


def get_commit_frequency() -> dict[str, int]:
    """Return commit counts per day for the last 14 days."""
    code, out, _ = _run_git(
        ["log", "--format=%cd", "--date=short", "--since=14 days ago"]
    )
    if code != 0 or not out:
        return {}
    freq: dict[str, int] = {}
    for line in out.splitlines():
        date = line.strip()
        if date:
            freq[date] = freq.get(date, 0) + 1
    return freq


def _parse_shortstat(text: str) -> dict[str, int]:
    """Parse git ``--shortstat`` output into file/insertion/deletion counts."""
    counts: dict[str, int] = {"files_changed": 0, "insertions": 0, "deletions": 0}
    for line in text.splitlines():
        if "changed" not in line:
            continue
        for part in line.strip().split(","):
            part = part.strip()
            if "file" in part:
                counts["files_changed"] = int(re.sub(r"\D", "", part) or 0)
            elif "insertion" in part:
                counts["insertions"] = int(re.sub(r"\D", "", part) or 0)
            elif "deletion" in part:
                counts["deletions"] = int(re.sub(r"\D", "", part) or 0)
    return counts


def get_file_change_summary() -> dict[str, int]:
    """Return file change counts from recent commits."""
    code, out, _ = _run_git(["diff", "--stat", "--shortstat", "HEAD~5..HEAD"])
    if code != 0 or not out:
        return {}
    return _parse_shortstat(out)


def get_working_tree_status() -> dict[str, int]:
    """Return counts of working tree changes."""
    code, out, _ = _run_git(["status", "--porcelain"])
    if code != 0:
        return {}
    counts: dict[str, int] = {
        "staged": 0,
        "modified": 0,
        "untracked": 0,
        "conflicted": 0,
    }
    for line in out.splitlines():
        if len(line) < 2:
            continue
        index = line[0]
        worktree = line[1]
        if index == "U" or worktree == "U":
            counts["conflicted"] += 1
        elif index == "?":
            counts["untracked"] += 1
        elif worktree in ("M", "D"):
            counts["modified"] += 1
        elif index in ("A", "M", "D", "R", "C"):
            counts["staged"] += 1
    return counts


def find_release_please_branches() -> list[str]:
    """Check for release-please branches (local and remote)."""
    branches: list[str] = []
    # Check remote
    remote_branches = get_remote_branches()
    for b in remote_branches:
        name = b.split("/", 1)[-1] if "/" in b else b
        if name.startswith("release-please"):
            branches.append(b)
    # Check local
    code, out, _ = _run_git(
        ["branch", "--list", "release-please*", "--format=%(refname:short)"]
    )
    if code == 0 and out:
        for b in out.splitlines():
            if b and b not in branches:
                branches.append(b)
    return branches


def get_upstream_status() -> str:
    """Check if current branch is ahead/behind its upstream tracking ref.

    Returns a descriptive string including the tracking ref name.
    """
    # Get tracking ref name
    code_ref, tracking_ref, _ = _run_git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"]
    )
    tracking_name = tracking_ref if code_ref == 0 and tracking_ref else ""

    code, out, _ = _run_git(
        ["rev-list", "--left-right", "--count", "@{upstream}...HEAD"]
    )
    if code != 0:
        return "no upstream"
    parts = out.split()
    if len(parts) == 2:
        behind, ahead = int(parts[0]), int(parts[1])
        suffix = f" (tracking: {tracking_name})" if tracking_name else ""
        if ahead == 0 and behind == 0:
            return f"up to date{suffix}"
        msgs: list[str] = []
        if ahead > 0:
            msgs.append(f"{ahead} ahead")
        if behind > 0:
            msgs.append(f"{behind} behind")
        return ", ".join(msgs) + suffix
    return "unknown"


def get_branch_characteristics() -> dict[str, str]:
    """Compute helpful characteristics of the current working branch.

    Returns a dict with keys like 'on_default_head', 'stale',
    'behind_default', 'fast_forwardable', 'local_only'.
    """
    chars: dict[str, str] = {}
    current = get_current_branch()
    default = get_default_branch()

    if current.startswith("(") or default == "(unknown)":
        return chars

    # Check if branch is on the default branch HEAD
    code_cur, sha_cur, _ = _run_git(["rev-parse", "HEAD"])
    base = _resolve_comparison_base(default)
    code_def, sha_def, _ = _run_git(["rev-parse", base])
    if code_cur == 0 and code_def == 0:
        if sha_cur == sha_def:
            chars["on_default_head"] = f"at {default} HEAD"
        else:
            # Determine if we're ahead (normal feature branch) or behind+ahead
            # to give a more helpful description than just "diverged"
            code_behind, out_behind, _ = _run_git(
                ["rev-list", "--count", f"HEAD..{base}"]
            )
            behind_count = int(out_behind) if code_behind == 0 and out_behind else -1
            if behind_count == 0:
                # Branch has all of default's commits but also has its own
                chars["on_default_head"] = (
                    f"ahead of {default} (contains all {default} commits)"
                )
            else:
                chars["on_default_head"] = f"diverged from {default}"

    # Behind default branch count
    code, out, _ = _run_git(["rev-list", "--count", f"HEAD..{base}"])
    if code == 0 and out:
        behind_default = int(out)
        if behind_default > 0:
            chars["behind_default"] = f"{behind_default} commit(s) behind {default}"
        else:
            chars["behind_default"] = f"up to date with {default}"

    # Staleness — days since last commit on current branch
    code, out, _ = _run_git(["log", "-1", "--format=%ct", current])
    if code == 0 and out:
        last_commit_ts = int(out)
        days_since = (time.time() - last_commit_ts) / 86400
        if days_since > 30:
            chars["stale"] = f"stale ({int(days_since)} days since last commit)"
        elif days_since > 7:
            chars["stale"] = f"aging ({int(days_since)} days since last commit)"
        else:
            chars["stale"] = "active"

    # Fast-forwardable — can branch be fast-forwarded to default?
    code, out, _ = _run_git(["merge-base", "--is-ancestor", "HEAD", base])
    if code == 0:
        chars["fast_forwardable"] = f"already contained in {default}"
    else:
        code, out, _ = _run_git(["merge-base", "--is-ancestor", base, "HEAD"])
        if code == 0:
            chars["fast_forwardable"] = f"fast-forwardable into {default}"
        else:
            chars["fast_forwardable"] = "requires merge/rebase"

    # Local-only — no remote tracking branch
    code_ref, tracking_ref, _ = _run_git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"]
    )
    if code_ref != 0:
        chars["local_only"] = "local only (no remote tracking)"
    else:
        chars["local_only"] = "remote tracked"

    # Unpushed commits — ahead of tracking branch
    if code_ref == 0 and tracking_ref:
        code, out, _ = _run_git(["rev-list", "--count", f"{tracking_ref}..HEAD"])
        if code == 0 and out:
            unpushed = int(out)
            if unpushed > 0:
                chars["unpushed"] = f"{unpushed} unpushed commit(s)"
            else:
                chars["unpushed"] = "all commits pushed"

    # Branch age — time since first commit unique to this branch
    if base != "(unknown)":
        code, out, _ = _run_git(
            ["log", "--reverse", "--format=%cr", f"{base}..{current}", "--"]
        )
        if code == 0 and out:
            first_line = out.splitlines()[0]
            chars["branch_age"] = f"created {first_line}"

    # Ahead of default — commits unique to this branch
    if base != "(unknown)":
        code, out, _ = _run_git(["rev-list", "--count", f"{base}..{current}"])
        if code == 0 and out:
            ahead_count = int(out)
            chars["ahead_default"] = f"{ahead_count} commit(s) ahead of {default}"

    # Commit density — commits in last 7 days on this branch
    code, out, _ = _run_git(["rev-list", "--count", "--since=7.days", current])
    if code == 0 and out:
        recent = int(out)
        if recent == 0:
            chars["commit_density"] = "no commits in last 7 days"
        elif recent <= 3:
            chars["commit_density"] = f"{recent} commit(s) in last 7 days (light)"
        elif recent <= 10:
            chars["commit_density"] = f"{recent} commit(s) in last 7 days (moderate)"
        else:
            chars["commit_density"] = f"{recent} commit(s) in last 7 days (heavy)"

    # Has merge conflicts in progress
    if get_merge_conflicts():
        chars["conflicts"] = "unresolved merge conflicts"

    return chars


def get_merge_conflicts() -> bool:
    """Check if there are unresolved merge conflicts."""
    code, out, _ = _run_git(["diff", "--check"])
    return code != 0 and "conflict" in out.lower()


def get_git_config_value(key: str) -> str:
    """Get a git config value."""
    code, out, _ = _run_git(["config", "--get", key])
    return out if code == 0 else ""


def get_git_config_scope(key: str) -> str:
    """Return the scope where a git config key is set (local/global/system/unset)."""
    code, out, _ = _run_git(["config", "--show-scope", "--get", key])
    if code != 0 or not out:
        return "unset"
    return out.split()[0]


def get_branch_diff_stats(branch: str, base: str) -> dict[str, int]:
    """Get insertions/deletions/files changed for *branch* vs *base*."""
    code, out, _ = _run_git(["diff", "--shortstat", f"{base}...{branch}"])
    if code != 0 or not out:
        return {"files_changed": 0, "insertions": 0, "deletions": 0}
    return _parse_shortstat(out)


def get_branch_commit_count(ref: str) -> int:
    """Return total commit count reachable from *ref*.

    .. note:: This counts the **entire history** reachable from the ref,
       not just commits unique to a branch.  For branch-specific counts
       use ``get_branch_unique_commit_count()`` instead.
    """
    code, out, _ = _run_git(["rev-list", "--count", ref])
    if code != 0 or not out:
        return 0
    try:
        return int(out)
    except ValueError:
        return 0


def get_branch_unique_commit_count(branch: str, base: str) -> int:
    """Return commits on *branch* not reachable from *base*.

    This gives the number of commits unique to *branch* since it
    diverged from *base* (typically the default branch).
    """
    code, out, _ = _run_git(["rev-list", "--count", f"{base}..{branch}"])
    if code != 0 or not out:
        return 0
    try:
        return int(out)
    except ValueError:
        return 0


def _resolve_comparison_base(default: str) -> str:
    """Return the best ref to compare branches against.

    Prefers ``origin/<default>`` because the local default branch may be
    stale (behind origin).  Using the local ref inflates commit counts
    and diff stats for every remote branch.
    """
    if default == "(unknown)":
        return default
    origin_ref = f"origin/{default}"
    # Verify origin ref exists
    code, _, _ = _run_git(["rev-parse", "--verify", origin_ref])
    if code == 0:
        return origin_ref
    return default


def get_recent_branches_with_stats(
    count: int = 5,
) -> list[dict[str, object]]:
    """Return most recent branches (local + remote) with diff stats vs default.

    Uses ``origin/<default>`` as the comparison base so stats remain
    accurate even when the local default branch is behind the remote.
    Stale remote-tracking refs are avoided by running ``git fetch --prune``
    before this function is called.
    """
    default = get_default_branch()
    base = _resolve_comparison_base(default)

    code, out, _ = _run_git(
        [
            "for-each-ref",
            "--sort=-committerdate",
            "--format=%(refname:short)\t%(committerdate:relative)\t%(objectname:short)\t%(refname)",
            "refs/heads/",
            "refs/remotes/",
        ]
    )
    if code != 0 or not out:
        return []

    seen: set[str] = set()
    branches: list[dict[str, object]] = []

    for line in out.splitlines():
        parts = line.split("\t", 3)
        if len(parts) < 4:
            continue
        name, date, sha, ref = parts[0], parts[1], parts[2], parts[3]
        if "HEAD" in name:
            continue
        # Skip the default branch itself (both local and remote)
        base_name = name.split("/", 1)[-1] if name.startswith("origin/") else name
        if base_name == default:
            continue
        # Deduplicate local/remote pairs
        if base_name in seen:
            continue
        seen.add(base_name)

        # Verify ref is still reachable (deleted remote branches may linger)
        verify_code, _, _ = _run_git(["rev-parse", "--verify", name])
        if verify_code != 0:
            continue

        # Count only commits unique to this branch (not entire repo history)
        if base != "(unknown)":
            unique_commits = get_branch_unique_commit_count(name, base)
        else:
            unique_commits = get_branch_commit_count(name)

        entry: dict[str, object] = {
            "name": name,
            "base_name": base_name,
            "date": date,
            "sha": sha,
            "source": "remote" if ref.startswith("refs/remotes/") else "local",
            "commits": unique_commits,
            "files_changed": 0,
            "insertions": 0,
            "deletions": 0,
        }
        if base != "(unknown)":
            stats = get_branch_diff_stats(name, base)
            entry.update(stats)
        branches.append(entry)
        if len(branches) >= count:
            break

    return branches


def get_working_branch_stats() -> dict[str, dict[str, int]]:
    """Get current branch stats: staged, unstaged, and total diff vs default."""
    empty: dict[str, int] = {"files_changed": 0, "insertions": 0, "deletions": 0}
    result: dict[str, dict[str, int]] = {}

    # Unstaged changes
    code, out, _ = _run_git(["diff", "--shortstat"])
    result["unstaged"] = _parse_shortstat(out) if code == 0 and out else dict(empty)

    # Staged changes
    code, out, _ = _run_git(["diff", "--cached", "--shortstat"])
    result["staged"] = _parse_shortstat(out) if code == 0 and out else dict(empty)

    # Total branch diff vs default
    default = get_default_branch()
    if default != "(unknown)":
        current = get_current_branch()
        result["vs_default"] = get_branch_diff_stats(current, default)
    else:
        result["vs_default"] = dict(empty)

    return result


def get_modified_files(limit: int = 15) -> list[dict[str, str]]:
    """Return modified/untracked files in the working directory."""
    code, out, _ = _run_git(["status", "--porcelain"])
    if code != 0 or not out:
        return []
    _status_map = {
        "M": "modified",
        "A": "added",
        "D": "deleted",
        "R": "renamed",
        "C": "copied",
        "?": "untracked",
        "U": "conflicted",
    }
    files: list[dict[str, str]] = []
    for line in out.splitlines():
        if len(line) < 3:
            continue
        idx, wt = line[0], line[1]
        fname = line[3:]
        if idx == "?" or wt == "?":
            label = "untracked"
        elif idx == "U" or wt == "U":
            label = "conflicted"
        elif wt in ("M", "D"):
            label = _status_map.get(wt, wt)
        else:
            label = _status_map.get(idx, idx) + " (staged)"
        files.append({"file": fname, "status": label})
        if len(files) >= limit:
            break
    return files


def get_stale_branches(days: int = 30) -> list[dict[str, str]]:
    """Return local branches with no commits in the last *days* days."""
    code, out, _ = _run_git(
        [
            "for-each-ref",
            "--sort=committerdate",
            "--format=%(refname:short)\t%(committerdate:relative)\t%(committerdate:unix)",
            "refs/heads/",
        ]
    )
    if code != 0 or not out:
        return []
    cutoff = time.time() - (days * 86400)
    stale: list[dict[str, str]] = []
    for line in out.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 3:
            continue
        try:
            ts = float(parts[2])
        except ValueError:
            continue
        if ts < cutoff:
            stale.append({"name": parts[0], "last_commit": parts[1]})
    return stale


def get_git_config_summary() -> dict[str, str]:
    """Return key git configuration values (top 18 for terminal display).

    Returns the terminal-display subset of config keys with their values.
    Keys not set in any scope get ``"(unset)"``.  The full catalog is
    available via ``--export-config``.
    """
    return {k: get_git_config_value(k) or "(unset)" for k in TERMINAL_CONFIG_KEYS}


def get_unmerged_branches() -> list[dict[str, str]]:
    """Return local branches not yet merged into the default branch.

    Compares against ``origin/<default>`` (not the local ref) so
    branches that were merged via PR and deleted on the remote are
    correctly excluded — even if the local ``<default>`` hasn't been
    pulled recently.

    Branches whose upstream tracking reference is ``[gone]`` (remote
    deleted) are **excluded** by default — they were almost certainly
    merged via PR (rebase-merge or squash-merge) and deleting the
    remote branch is the normal post-merge workflow.  These are not
    "unmerged" in the meaningful sense; ``git branch --no-merged``
    reports them because rebase-merge and squash-merge create new
    commits rather than fast-forwarding.
    """
    # TODO (template users): If your team uses regular merges (not
    #   rebase-merge or squash-merge), you may want to re-include [gone]
    #   branches since they could genuinely be unmerged.  Change
    #   ``if "gone" in track: continue`` to the annotation approach
    #   from the previous version.
    default = get_default_branch()
    if default == "(unknown)":
        return []
    # Prefer origin/<default> for accuracy; fall back to local ref
    target = f"origin/{default}"
    code, out, _ = _run_git(
        ["branch", "--no-merged", target, "--format=%(refname:short)"]
    )
    if code != 0:
        # Fallback: local default branch ref
        code, out, _ = _run_git(
            ["branch", "--no-merged", default, "--format=%(refname:short)"]
        )
    if code != 0 or not out:
        return []

    # Cross-reference with tracking status to detect squash-merged branches
    tracking_info: dict[str, str] = {}
    tc, tout, _ = _run_git(
        ["branch", "-vv", "--format=%(refname:short)\t%(upstream:track)"]
    )
    if tc == 0 and tout:
        for line in tout.splitlines():
            parts = line.split("\t", 1)
            if len(parts) == 2:
                tracking_info[parts[0]] = parts[1]

    branches: list[dict[str, str]] = []
    for b in out.splitlines():
        b = b.strip()
        if not b:
            continue
        track = tracking_info.get(b, "")
        # Skip branches whose remote has been deleted — these are almost
        # certainly merged via squash/PR.  Listing them as "unmerged" is
        # misleading because the remote deletion is the normal post-merge
        # cleanup step.
        if "gone" in track:
            continue
        branches.append({"name": b, "note": ""})
    return branches


def get_last_merge_from_default() -> dict[str, str]:
    """Return info about the last merge from the default branch into current.

    Finds the most recent merge commit where the default branch (e.g. main)
    was merged into the current branch. Useful for knowing how fresh your
    branch is relative to the mainline.
    """
    default = get_default_branch()
    current = get_current_branch()
    if default == "(unknown)" or current == default:
        return {}

    # Find the merge-base (common ancestor)
    code, merge_base, _ = _run_git(["merge-base", current, default])
    if code != 0 or not merge_base:
        return {}

    # Get the date and message of the merge-base commit
    code, out, _ = _run_git(
        ["log", "-1", "--format=%H\t%h\t%s\t%an\t%ar\t%ai", merge_base]
    )
    if code != 0 or not out:
        return {}

    parts = out.split("\t", 5)
    result: dict[str, str] = {"merge_base_sha": parts[0], "sha_short": parts[1]}
    if len(parts) >= 3:
        result["message"] = parts[2]
    if len(parts) >= 4:
        result["author"] = parts[3]
    if len(parts) >= 5:
        result["relative_date"] = parts[4]
    if len(parts) >= 6:
        result["date"] = parts[5]

    # Count how many commits default branch is ahead of the merge-base
    code, out, _ = _run_git(["rev-list", "--count", f"{merge_base}..{default}"])
    if code == 0 and out:
        result["default_ahead"] = out

    # Count how many commits current branch is ahead of the merge-base
    code, out, _ = _run_git(["rev-list", "--count", f"{merge_base}..{current}"])
    if code == 0 and out:
        result["current_ahead"] = out

    return result


def get_first_commit_on_branch() -> dict[str, str]:
    """Return info about when the current branch diverged from default."""
    default = get_default_branch()
    current = get_current_branch()
    if default == "(unknown)" or current == default:
        return {}

    # Find the first commit after diverging from default
    code, merge_base, _ = _run_git(["merge-base", current, default])
    if code != 0 or not merge_base:
        return {}

    code, out, _ = _run_git(
        ["log", "--format=%h\t%s\t%ar", "--reverse", f"{merge_base}..HEAD", "-1"]
    )
    if code != 0 or not out:
        return {}

    parts = out.split("\t", 2)
    result: dict[str, str] = {"sha": parts[0]}
    if len(parts) >= 2:
        result["message"] = parts[1]
    if len(parts) >= 3:
        result["date"] = parts[2]
    return result


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------


def check_git_installed() -> tuple[bool, str]:
    """Verify git is available."""
    if _GIT is None:
        return False, "git not found in PATH"
    code, out, _ = _run_git(["--version"])
    return (True, out) if code == 0 else (False, "git found but failed to run")


def check_inside_repo() -> tuple[bool, str]:
    """Verify we're inside a git repo."""
    code, _, _ = _run_git(["rev-parse", "--is-inside-work-tree"])
    if code == 0:
        return True, "Inside a git repository"
    return False, "Not inside a git repository"


def check_clean_workdir() -> tuple[bool, str]:
    """Check for uncommitted changes."""
    status = get_working_tree_status()
    total = sum(status.values())
    if total == 0:
        return True, "Working directory clean"
    parts: list[str] = []
    for key, count in status.items():
        if count > 0:
            parts.append(f"{count} {key}")
    return False, f"Dirty working directory: {', '.join(parts)}"


def check_no_conflicts() -> tuple[bool, str]:
    """Check for merge conflicts."""
    code, out, _ = _run_git(["diff", "--name-only", "--diff-filter=U"])
    if code != 0 or not out:
        return True, "No merge conflicts"
    count = len(out.splitlines())
    return False, f"{count} file(s) with merge conflicts"


def check_upstream_configured() -> tuple[bool, str]:
    """Check if current branch tracks an upstream."""
    branch = get_current_branch()
    code, out, _ = _run_git(["config", f"branch.{branch}.remote"])
    if code == 0 and out:
        return True, f"Upstream configured: {out}/{branch}"
    return False, f"Branch '{branch}' has no upstream tracking"


def check_no_detached_head() -> tuple[bool, str]:
    """Check we're not in detached HEAD state."""
    code, _out, _ = _run_git(["symbolic-ref", "-q", "HEAD"])
    if code == 0:
        return True, "On a named branch"
    return False, "Detached HEAD state"


def check_fetch_recent() -> tuple[bool, str]:
    """Check if a fetch has happened recently (last hour)."""
    fetch_head = ROOT / ".git" / "FETCH_HEAD"
    if not fetch_head.exists():
        return False, "Never fetched - run: git fetch"

    age_seconds = time.time() - fetch_head.stat().st_mtime
    age_minutes = age_seconds / 60
    age_hours = age_seconds / 3600
    if age_hours < 1:
        return True, f"Last fetch: {age_minutes:.0f}m ago"
    if age_hours < 24:
        return True, f"Last fetch: {age_hours:.1f}h ago"
    days = age_hours / 24
    return False, f"Last fetch: {days:.0f}d ago - consider running: git fetch"


def check_gitignore_exists() -> tuple[bool, str]:
    """Check .gitignore exists."""
    if (ROOT / ".gitignore").is_file():
        return True, ".gitignore present"
    return False, ".gitignore missing"


def check_no_large_files_staged() -> tuple[bool, str]:
    """Warn about files > 5 MB staged for commit."""
    code, out, _ = _run_git(["diff", "--cached", "--name-only"])
    if code != 0 or not out:
        return True, "No large staged files"
    large: list[str] = []
    for fname in out.splitlines():
        fpath = ROOT / fname
        if fpath.is_file():
            size_mb = fpath.stat().st_size / (1024 * 1024)
            if size_mb > 5:
                large.append(f"{fname} ({size_mb:.1f} MB)")
    if large:
        return False, f"Large staged files: {', '.join(large[:3])}"
    return True, "No large staged files"


def check_branch_protection_alignment() -> tuple[bool, str]:
    """Check if default branch in git matches workflow expectations.

    .. note:: This check uses a simple regex to find ``branches:`` keys in
       workflow YAML.  It can false-positive on workflows that intentionally
       omit the default branch (e.g. release-only or tag-triggered workflows)
       or match commented-out lines.
    """
    # TODO (template users): If your workflows intentionally target branches
    #   other than the default, exclude those workflow files here or adjust
    #   the regex to skip commented-out lines.
    code, out, _ = _run_git(["symbolic-ref", "refs/remotes/origin/HEAD"])
    if code != 0:
        return (
            False,
            "Cannot determine default branch - run: git remote set-head origin --auto",
        )
    default_branch = out.rsplit("/", 1)[-1]

    # Check workflows reference the same branch
    workflows_dir = ROOT / ".github" / "workflows"
    mismatches: list[str] = []
    if workflows_dir.is_dir():
        for wf in workflows_dir.glob("*.yml"):
            try:
                content = wf.read_text(encoding="utf-8")
                for match in re.finditer(
                    r"branches:\s*\[([^\]]+)\]|branches:\s*\n\s*-\s*(\S+)",
                    content,
                ):
                    branch_refs = match.group(1) or match.group(2)
                    if branch_refs and default_branch not in branch_refs:
                        mismatches.append(wf.name)
                        break
            except OSError:
                continue

    if mismatches:
        return (
            False,
            f"Default branch '{default_branch}' not referenced in workflows: "
            f"{', '.join(mismatches[:5])}",
        )
    return True, f"Default branch '{default_branch}' aligns with workflows"


def check_git_hooks_integrity() -> tuple[bool, str]:
    """Verify pre-commit hook files are actual pre-commit scripts.

    Goes beyond existence checking — reads content to detect empty
    stubs, corrupted files, sample hooks, or non-pre-commit hooks.
    """
    hooks_dir = ROOT / ".git" / "hooks"
    if not hooks_dir.is_dir():
        return False, "No .git/hooks directory"

    expected = ["pre-commit", "commit-msg", "pre-push"]
    issues: list[str] = []
    ok_count = 0

    for hook_name in expected:
        hook_path = hooks_dir / hook_name
        if not hook_path.is_file():
            issues.append(f"{hook_name}: missing")
            continue

        try:
            content = hook_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            issues.append(f"{hook_name}: unreadable")
            continue

        content_stripped = content.strip()
        if not content_stripped:
            issues.append(f"{hook_name}: empty file")
        elif len(content_stripped) < 10:
            issues.append(
                f"{hook_name}: suspiciously small ({len(content_stripped)} bytes)"
            )
        elif "generated by pre-commit" not in content.lower():
            if ".sample" in hook_path.name or "this sample" in content.lower():
                issues.append(f"{hook_name}: git sample hook (not pre-commit)")
            else:
                issues.append(f"{hook_name}: custom script (not managed by pre-commit)")
        else:
            ok_count += 1

    if not issues:
        return True, f"All {ok_count} hook files are valid pre-commit hooks"
    return False, "; ".join(issues)


def check_git_remote_health() -> tuple[bool, str]:
    """Verify origin remote URL looks correct and matches pyproject.toml."""
    url = get_remote_url()
    if url == "(no remote)":
        return False, "No origin remote configured"

    issues: list[str] = []

    valid_prefixes = ("https://", "git@", "ssh://", "git://")
    if not any(url.startswith(p) for p in valid_prefixes):
        issues.append(f"Unusual URL scheme: {url}")

    pyproject = read_pyproject(ROOT)
    if pyproject is not None:
        project = pyproject.get("project", {})
        if isinstance(project, dict):
            urls = project.get("urls", {})
            if isinstance(urls, dict):
                repo_url = urls.get("Repository", "")
                if isinstance(repo_url, str) and repo_url:
                    remote_slug = extract_repo_slug(url)
                    declared_slug = extract_repo_slug(repo_url)
                    if remote_slug and declared_slug and remote_slug != declared_slug:
                        issues.append(
                            f"Remote ({remote_slug}) doesn't match "
                            f"pyproject.toml Repository URL ({declared_slug})"
                        )

    if issues:
        return False, "; ".join(issues)
    return True, f"Remote origin: {url}"


def check_conventional_commits() -> tuple[bool, str]:
    """Check if recent commits follow Conventional Commits format."""
    code, out, _ = _run_git(["log", "-10", "--format=%s"])
    if code != 0 or not out:
        return True, "No commits to check"
    conventional_re = re.compile(
        r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
        r"(\([^)]+\))?!?: .+"
    )
    non_conventional: list[str] = []
    subjects = out.splitlines()
    for subject in subjects:
        # Skip merge commits and release-please commits
        if subject.startswith(("Merge ", "chore(main):")):
            continue
        if not conventional_re.match(subject):
            non_conventional.append(subject[:50])
    if non_conventional:
        count = len(non_conventional)
        example = non_conventional[0]
        return (
            False,
            f"{count}/{len(subjects)} recent commits non-conventional "
            f'(e.g. "{example}")',
        )
    return True, "Recent commits follow Conventional Commits"


def check_gitmessage_template() -> tuple[bool, str]:
    """Check if .gitmessage commit template is configured."""
    template_path = ROOT / ".gitmessage.txt"
    if not template_path.is_file():
        return True, "No .gitmessage.txt (optional)"
    configured = get_git_config_value("commit.template")
    if configured:
        return True, f"Commit template configured: {configured}"
    return (
        False,
        "Found .gitmessage.txt but git commit.template not set "
        "- run: git config commit.template .gitmessage.txt",
    )


def check_user_identity() -> tuple[bool, str]:
    """Check that user.name and user.email are configured."""
    name = get_git_config_value("user.name")
    email = get_git_config_value("user.email")
    if name and email:
        return True, f"Identity: {name} <{email}>"
    missing: list[str] = []
    if not name:
        missing.append("user.name")
    if not email:
        missing.append("user.email")
    return False, f"Missing git config: {', '.join(missing)}"


def check_merge_base_freshness() -> tuple[bool, str]:
    """Warn if the current branch hasn't been rebased/merged from default recently.

    Checks how many commits the default branch is ahead of the merge-base.
    A high divergence means the branch may have merge conflicts waiting.
    """
    # TODO (template users): Adjust the threshold (default_ahead <= 10)
    #   to match your team's merge cadence.  Larger repos that merge main
    #   less frequently may want a higher value (e.g. 25 or 50).
    current = get_current_branch()
    default = get_default_branch()
    if default == "(unknown)" or current == default:
        return True, "On default branch (no merge-base to check)"

    merge_info = get_last_merge_from_default()
    if not merge_info:
        return False, f"Cannot determine merge-base with {default}"

    default_ahead = int(merge_info.get("default_ahead", "0"))
    rel_date = merge_info.get("relative_date", "unknown")

    if default_ahead == 0:
        return True, f"Branch is up to date with {default}"
    if default_ahead <= 10:
        return (
            True,
            f"{default} is {default_ahead} commits ahead (merge-base: {rel_date})",
        )
    return (
        False,
        f"{default} is {default_ahead} commits ahead "
        f"(merge-base: {rel_date}) "
        f"- consider: git fetch origin && git rebase origin/{default}",
    )


# ---------------------------------------------------------------------------
# Helpful commands reference
# ---------------------------------------------------------------------------

# TODO (template users): Add or remove helpful commands that match your
#   team's git workflow (e.g. signed commits, rebase preferences).
HELPFUL_COMMANDS: list[dict[str, str]] = [
    {
        "cmd": "git fetch --all --prune",
        "desc": "Fetch all remotes, remove stale tracking branches",
    },
    {"cmd": "git log --oneline -10", "desc": "Show last 10 commits"},
    {"cmd": "git status -sb", "desc": "Short status with branch info"},
    {"cmd": "git stash list", "desc": "List stash entries"},
    {"cmd": "git branch -vv", "desc": "List branches with tracking info"},
    {"cmd": "git remote -v", "desc": "Show all remotes"},
    {"cmd": "git diff --stat", "desc": "Summary of uncommitted changes"},
    {"cmd": "git log --all --graph --oneline -20", "desc": "Visual branch graph"},
    {"cmd": "git reflog -10", "desc": "Recent HEAD movements (undo helper)"},
    {"cmd": "git clean -fdn", "desc": "Preview untracked files that would be removed"},
    {
        "cmd": "git config --global --list",
        "desc": "View all global git configuration settings",
    },
    {
        "cmd": "git config --list --show-origin",
        "desc": "View all git config values with their source file",
    },
    {
        "cmd": "git pull --rebase",
        "desc": "Pull and rebase local commits on top of upstream (linear history)",
    },
    {
        "cmd": "git push --force-with-lease",
        "desc": "Force push safely (fails if remote has unexpected new commits)",
    },
]


# ---------------------------------------------------------------------------
# Check runner
# ---------------------------------------------------------------------------

CheckFn = Callable[[], tuple[bool, str]]

# TODO (template users): Add or remove health checks to match your
#   project's git conventions (e.g. require signed commits, enforce
#   branch naming patterns, check for .gitmessage).
HEALTH_CHECKS: list[tuple[str, CheckFn]] = [
    ("Git installed", check_git_installed),
    ("Inside git repo", check_inside_repo),
    ("Not detached HEAD", check_no_detached_head),
    ("Working directory", check_clean_workdir),
    ("Merge conflicts", check_no_conflicts),
    ("Upstream tracking", check_upstream_configured),
    ("Recent fetch", check_fetch_recent),
    (".gitignore", check_gitignore_exists),
    ("Large staged files", check_no_large_files_staged),
    ("Default branch", check_branch_protection_alignment),
    ("Hook integrity", check_git_hooks_integrity),
    ("Remote health", check_git_remote_health),
    ("Conventional commits", check_conventional_commits),
    ("Commit template", check_gitmessage_template),
    ("User identity", check_user_identity),
    ("Merge-base freshness", check_merge_base_freshness),
]


def _collect_info() -> dict[
    str,
    str | int | list[str] | list[dict[str, str]] | dict[str, int],
]:
    """Collect all git information into a dict."""
    collectors: list[tuple[str, Callable[[], object]]] = [
        ("current_branch", get_current_branch),
        ("default_branch", get_default_branch),
        ("remote_url", get_remote_url),
        ("remotes", get_all_remotes),
        ("upstream_status", get_upstream_status),
        ("local_branches", get_local_branches),
        ("remote_branches", get_remote_branches),
        ("recent_commits", lambda: get_recent_commits(5)),
        ("tags", lambda: get_tags(5)),
        ("stash_count", get_stash_count),
        ("commit_count", get_commit_count),
        ("repo_age", get_repo_age),
        ("contributors", get_contributors_count),
        ("working_tree", get_working_tree_status),
        ("release_please_branches", find_release_please_branches),
        ("user_name", lambda: get_git_config_value("user.name")),
        ("user_email", lambda: get_git_config_value("user.email")),
        ("branch_activity", lambda: get_recent_branches_with_stats(5)),
        ("working_branch_stats", get_working_branch_stats),
        ("modified_files", get_modified_files),
        ("stale_branches", get_stale_branches),
        ("git_config", get_git_config_summary),
        (
            "git_config_scopes",
            lambda: {k: get_git_config_scope(k) for k in TERMINAL_CONFIG_KEYS},
        ),
        ("unmerged_branches", get_unmerged_branches),
        ("last_merge_from_default", get_last_merge_from_default),
        ("branch_divergence", get_first_commit_on_branch),
        ("commit_frequency", get_commit_frequency),
        ("file_change_summary", get_file_change_summary),
        ("branch_characteristics", get_branch_characteristics),
    ]
    info: dict[str, object] = {}
    with Spinner("Collecting git info", log_interval=5) as spin:
        for key, fn in collectors:
            spin.update(key)
            info[key] = fn()
    return info  # type: ignore[return-value]


def _collect_health() -> tuple[list[dict[str, str]], int]:
    """Run all health checks and return (results, failure_count)."""
    results: list[dict[str, str]] = []
    failures = 0
    with Spinner("Running health checks", log_interval=5) as spin:
        for name, check_fn in HEALTH_CHECKS:
            spin.update(name)
            passed, msg = check_fn()
            status = "PASS" if passed else "FAIL"
            if not passed:
                failures += 1
            results.append({"name": name, "status": status, "message": msg})
    return results, failures


def run(
    *,
    color: bool | None = None,
    output_json: bool = False,
) -> int:
    """Run git doctor and print results.

    Args:
        color: Force color on/off. None = auto-detect.
        output_json: Output as JSON.

    Returns:
        Exit code: 0 = healthy, 1 = issues found.
    """
    elapsed_start = time.monotonic()

    # Fetch and prune stale remote-tracking refs before collecting data.
    # This ensures branch activity stats are accurate and deleted remote
    # branches don't pollute the output.
    with Spinner("Fetching remotes", log_interval=5):
        fetch_ok, fetch_msg = _fetch_and_prune()
        if not fetch_ok:
            logger.warning(
                "git fetch failed: %s (continuing with stale data)", fetch_msg
            )

    # Collect info once and reuse for both display and JSON
    info = _collect_info()
    current_branch: str = info["current_branch"]  # type: ignore[assignment]
    default_branch: str = info["default_branch"]  # type: ignore[assignment]
    remote_url: str = info["remote_url"]  # type: ignore[assignment]
    upstream_status: str = info["upstream_status"]  # type: ignore[assignment]
    local_branches: list[dict[str, str]] = info["local_branches"]  # type: ignore[assignment]
    recent_commits: list[dict[str, str]] = info["recent_commits"]  # type: ignore[assignment]
    tags: list[str] = info["tags"]  # type: ignore[assignment]
    stash_count: int = info["stash_count"]  # type: ignore[assignment]
    commit_count: int = info["commit_count"]  # type: ignore[assignment]
    repo_age: str = info["repo_age"]  # type: ignore[assignment]
    contributors: int = info["contributors"]  # type: ignore[assignment]
    working_tree: dict[str, int] = info["working_tree"]  # type: ignore[assignment]
    rp_branches: list[str] = info["release_please_branches"]  # type: ignore[assignment]
    user_name: str = info["user_name"]  # type: ignore[assignment]
    user_email: str = info["user_email"]  # type: ignore[assignment]
    branch_activity: list[dict[str, object]] = info["branch_activity"]  # type: ignore[assignment]
    wb_stats: dict[str, dict[str, int]] = info["working_branch_stats"]  # type: ignore[assignment]
    modified_files: list[dict[str, str]] = info["modified_files"]  # type: ignore[assignment]
    stale_branches: list[dict[str, str]] = info["stale_branches"]  # type: ignore[assignment]
    git_config: dict[str, str] = info["git_config"]  # type: ignore[assignment]
    git_config_scopes: dict[str, str] = info["git_config_scopes"]  # type: ignore[assignment]
    unmerged_branches: list[dict[str, str]] = info["unmerged_branches"]  # type: ignore[assignment]
    last_merge: dict[str, str] = info["last_merge_from_default"]  # type: ignore[assignment]
    branch_divergence: dict[str, str] = info["branch_divergence"]  # type: ignore[assignment]
    commit_freq: dict[str, int] = info["commit_frequency"]  # type: ignore[assignment]
    file_changes: dict[str, int] = info["file_change_summary"]  # type: ignore[assignment]
    branch_chars: dict[str, str] = info["branch_characteristics"]  # type: ignore[assignment]

    health_results, failures = _collect_health()

    if output_json:
        payload: dict[str, object] = {
            "version": SCRIPT_VERSION,
            "info": info,
            "health": health_results,
            "failures": failures,
            "helpful_commands": HELPFUL_COMMANDS,
        }
        print(json.dumps(payload, indent=2, default=str))
        return 1 if failures else 0

    use_color = color if color is not None else _supports_color(sys.stdout)
    use_unicode = _supports_unicode(sys.stdout)
    sym = _unicode_symbols(sys.stdout)
    bar_char = "\u2588" if use_unicode else "#"
    bar_left = "\u258c" if use_unicode else "["
    bar_right = "\u2590" if use_unicode else "]"
    dash = sym["dash"]
    c = Colors(enabled=use_color)

    # Box-drawing characters for section headers
    h_line = "\u2500" if use_unicode else "-"  # ─
    h_double = "\u2550" if use_unicode else "="  # ═
    tl = "\u250c" if use_unicode else "+"  # ┌
    tr = "\u2510" if use_unicode else "+"  # ┐
    bl = "\u2514" if use_unicode else "+"  # └
    br = "\u2518" if use_unicode else "+"  # ┘
    tl_d = "\u2554" if use_unicode else "+"  # ╔
    tr_d = "\u2557" if use_unicode else "+"  # ╗
    bl_d = "\u255a" if use_unicode else "+"  # ╚
    br_d = "\u255d" if use_unicode else "+"  # ╝
    vl = "\u2502" if use_unicode else "|"  # │
    vl_d = "\u2551" if use_unicode else "|"  # ║
    dot = "\u2022" if use_unicode else "*"  # •

    def _section(title: str) -> None:
        """Print a section header with colored box-drawing border."""
        border = h_line * 60
        print()
        print(c.cyan(f"  {tl}{border}{tr}"))
        print(f"  {c.cyan(vl)} {c.bold(title)}")
        print(c.cyan(f"  {bl}{border}{br}"))

    def _kv(label: str, value: str, width: int = 18, hint: str = "") -> None:
        """Print a key-value pair with consistent alignment.

        When *hint* is provided it is rendered on a separate indented
        line below the value in dim text, keeping the main line clean.
        """
        print(f"    {label + ':':{width}s} {value}")
        if hint:
            # Indent hint below, aligned past the label column
            print(f"    {'':{width}s} {c.dim(hint)}")

    # ── Header ──
    header_border = h_double * 60
    print()
    print(c.bold(c.cyan(f"  {tl_d}{header_border}{tr_d}")))
    print(
        f"  {c.bold(c.cyan(vl_d))} "
        f"{c.bold(c.cyan('Git Doctor'))}  {c.dim(f'v{SCRIPT_VERSION}')}"
    )
    print(c.bold(c.cyan(f"  {bl_d}{header_border}{br_d}")))

    # Quick status bar — three indicators with explicit labels
    check = sym.get("check", "+")
    cross = sym.get("cross", "x")
    warn_sym = sym.get("warn", "!")
    clean = not any(working_tree.values())
    sync_ok = "behind" not in upstream_status.lower()
    passed_count = len(health_results) - failures

    wt_icon = c.green(check) if clean else c.yellow(warn_sym)
    wt_label = c.green("clean") if clean else c.yellow("dirty")
    sync_icon = c.green(check) if sync_ok else c.yellow(warn_sym)
    sync_label = c.green("synced") if sync_ok else c.yellow("behind")
    hc_icon = c.green(check) if not failures else c.red(cross)
    hc_label = (
        c.green(f"{passed_count}/{len(health_results)} passed")
        if not failures
        else c.red(f"{failures} failed, {passed_count} passed")
    )

    # Extract branch age and unpushed count for the status bar
    _age_str = branch_chars.get("branch_age", "")
    _unpushed_str = branch_chars.get("unpushed", "")
    _unpushed_count = ""
    if _unpushed_str and "unpushed" in _unpushed_str:
        _unpushed_count = _unpushed_str.split()[0]  # e.g. "4"

    print()
    _status_w = 22  # pad labels to align values vertically
    print(f"  {wt_icon} {c.dim('Working tree:'.ljust(_status_w))} {wt_label}")
    print(
        f"  {sync_icon} {c.dim('Remote sync (origin):'.ljust(_status_w))} {sync_label}"
    )
    print(f"  {hc_icon} {c.dim('Health:'.ljust(_status_w))} {hc_label}")
    if _age_str:
        print(
            f"  {c.dim(dot)} {c.dim('Branch age:'.ljust(_status_w))} {c.dim(_age_str)}"
        )
    if _unpushed_count:
        print(
            f"  {c.yellow(warn_sym)} {c.dim('Unpushed commits:'.ljust(_status_w))} "
            f"{c.yellow(_unpushed_count)}"
        )

    # ── Repository Info ──
    _section("Repository")
    _kv("Remote URL", remote_url, hint="origin remote (fetch/push URL)")
    _kv("Current branch", c.green(current_branch), hint="your active branch (HEAD)")
    _kv(
        "Default branch",
        default_branch,
        hint=f"base branch for PRs (origin/{default_branch})",
    )
    _kv("Upstream", upstream_status, hint="remote tracking status (origin)")
    _kv("User", f"{user_name} <{user_email}>", hint="from git config")
    _kv("Commits", str(commit_count), hint="total repo history")
    _kv("Contributors", str(contributors), hint="unique commit authors")
    _kv("Repo age", repo_age, hint="first commit to now")

    # ── Git Configuration (top 18 — use --export-config for full reference) ──
    if git_config:
        set_count = sum(1 for v in git_config.values() if v != "(unset)")
        unset_count = len(git_config) - set_count
        _section(
            f"Git Configuration  {c.dim(f'({set_count} set, {unset_count} unset)')}"
        )
        print(
            f"    {c.dim('Showing commonly used keys — not every git config.')}"
            f"  {c.dim('Run --export-config for full reference.')}"
        )
        # Column layout — widened to accommodate longer config key names
        key_w = 30
        scope_w = 12
        val_w = 20
        total_w = key_w + scope_w + val_w + 2  # +2 for spaces between columns
        # Column headers
        hdr_key = c.dim("Key".ljust(key_w))
        hdr_scope = c.dim("Scope".ljust(scope_w))
        hdr_val = c.dim("Value")
        print(f"    {hdr_key} {hdr_scope} {hdr_val}")
        print(
            f"    {c.dim(h_line * key_w)} {c.dim(h_line * scope_w)} {c.dim(h_line * val_w)}"
        )
        # Group keys by their logical section for visual separation
        current_group = ""
        for key, val in git_config.items():
            group = _config_section(key)
            if group != current_group:
                if current_group:
                    print()  # blank line between groups
                current_group = group
                # Prominent section header with colored borders
                pad_len = max(total_w - len(group) - 3, 4)
                group_line = f"{h_line * 2} {group} {h_line * pad_len}"
                print(f"    {c.bold(c.cyan(group_line))}")
            scope = git_config_scopes.get(key, "unset")
            scope_str = f"[{scope}]".ljust(scope_w)
            key_padded = key.ljust(key_w)
            # Check if this key has a recommended value and it differs
            rec_value = _RECOMMENDED_LOOKUP.get(key)
            if val == "(unset)":
                hint_str = ""
                if rec_value:
                    hint_str = f"  {c.dim(f'(recommended: {rec_value})')}"
                print(
                    f"    {c.dim(key_padded)} {c.dim(scope_str)} {c.dim(val)}{hint_str}"
                )
            elif rec_value and val != rec_value:
                print(
                    f"    {key_padded} {c.dim(scope_str)} {c.yellow(val)}"
                    f"  {c.dim(f'(recommended: {rec_value})')}"
                )
            else:
                print(f"    {key_padded} {c.dim(scope_str)} {c.cyan(val)}")
        print()
        print(
            f"    {c.dim('Run with --export-config for full reference, --fix to apply recommended')}"
        )

    # ── Commit Activity — current branch (last 14 days) ──
    if commit_freq:
        _section(f"Commit Activity {dash} {c.green(current_branch)} (last 14 days)")
        print(f"    {c.dim('Daily commit frequency on this branch')}")
        max_count = max(commit_freq.values()) if commit_freq else 1
        sorted_dates = sorted(commit_freq)
        bar_data: list[tuple[str, int, int]] = []
        for date in sorted_dates:
            count = commit_freq[date]
            bar_len = int((count / max_count) * 30) if max_count > 0 else 0
            bar_data.append((date, count, bar_len))
        for idx, (date, count, bar_len) in enumerate(bar_data):
            inner = bar_char * bar_len if bar_len > 0 else ""
            bar = (
                c.green(f"{bar_left}{inner}{bar_right}")
                if bar_len > 0
                else c.dim(bar_left + bar_right)
            )
            print(f"    {date}  {bar} {count}")
            # Blank line between bars for visual separation (skip after last)
            if idx < len(bar_data) - 1:
                print()
        total_recent = sum(commit_freq.values())
        avg = total_recent / len(commit_freq) if commit_freq else 0
        print(f"    {c.dim(f'Total: {total_recent} commits, avg {avg:.1f}/day')}")

    # ── File Change Summary — current branch (last 5 commits) ──
    if file_changes and any(file_changes.values()):
        _section(
            f"Recent File Changes {dash} {c.green(current_branch)} (last 5 commits)"
        )
        print(
            f"    {c.dim('Diff of HEAD~5..HEAD — only the last 5 commits on this branch')}"
        )
        fc = file_changes
        ins = fc.get("insertions", 0)
        dels = fc.get("deletions", 0)
        files = fc.get("files_changed", 0)
        _kv("Files changed", str(files), hint="unique files touched")
        _kv("Insertions", c.green(f"+{ins}"), hint="lines added")
        _kv("Deletions", c.red(f"-{dels}"), hint="lines removed")

    # ── Repo Branch Activity (top 5 most recent) ──
    if branch_activity:
        _section("Repo Branch Activity (top 5 most recent)")
        print(
            f"    {c.dim('Total diff of each branch vs merge-base with default branch')}"
        )
        # Dynamic column width based on longest branch name (cap at 50)
        max_name = max((len(str(e["base_name"])) for e in branch_activity), default=20)
        name_w = min(max(max_name, 10), 50)
        # Header
        hdr_b = c.dim("Branch".ljust(name_w))
        hdr_s = c.dim("Source".ljust(8))
        hdr_d = c.dim("Last Commit".ljust(16))
        hdr_c = c.dim("Commits".rjust(8))
        hdr_f = c.dim("Files".rjust(6))
        hdr_i = c.dim("+Ins".rjust(7))
        hdr_dl = c.dim("-Del".rjust(7))
        print(f"    {hdr_b} {hdr_s} {hdr_d} {hdr_c} {hdr_f} {hdr_i} {hdr_dl}")
        for entry in branch_activity:
            bname = str(entry["base_name"])
            src = str(entry["source"])
            bdate = str(entry["date"])
            bcommits = int(entry.get("commits", 0))  # type: ignore[arg-type]
            bf = int(entry.get("files_changed", 0))  # type: ignore[arg-type]
            bi = int(entry.get("insertions", 0))  # type: ignore[arg-type]
            bd = int(entry.get("deletions", 0))  # type: ignore[arg-type]
            # Truncate long names with ellipsis
            display_name = (
                bname[: name_w - 1] + sym["ellip"] if len(bname) > name_w else bname
            )
            name_padded = display_name.ljust(name_w)
            name_display = (
                c.green(name_padded) if bname == current_branch else name_padded
            )
            ins_s = c.green(f"+{bi}".rjust(7)) if bi else str(bi).rjust(7)
            del_s = c.red(f"-{bd}".rjust(7)) if bd else str(bd).rjust(7)
            print(
                f"    {name_display} {src:8s} {bdate:16s}"
                f" {bcommits:>8d} {bf:>6d} {ins_s} {del_s}"
            )

    # ── Current Working Branch ──
    _section(f"Current Working Branch: {c.green(current_branch)}")
    # Show branch-specific commit count when on a feature branch
    if current_branch != default_branch and default_branch != "(unknown)":
        branch_commits = get_branch_unique_commit_count(current_branch, default_branch)
        _kv(
            "Branch commits",
            f"{branch_commits}  {c.dim(f'(repo total: {commit_count})')}",
            hint="commits unique to this branch",
        )
    else:
        _kv("Total commits", str(commit_count))
    vd = wb_stats.get("vs_default", {})
    st = wb_stats.get("staged", {})
    us = wb_stats.get("unstaged", {})
    vd_f, vd_i, vd_d = (
        vd.get("files_changed", 0),
        vd.get("insertions", 0),
        vd.get("deletions", 0),
    )
    st_f, st_i, st_d = (
        st.get("files_changed", 0),
        st.get("insertions", 0),
        st.get("deletions", 0),
    )
    us_f, us_i, us_d = (
        us.get("files_changed", 0),
        us.get("insertions", 0),
        us.get("deletions", 0),
    )
    if vd_f or vd_i or vd_d:
        _kv(
            f"vs {default_branch}",
            f"{vd_f} files changed, "
            f"{c.green(f'+{vd_i}')} insertions, {c.red(f'-{vd_d}')} deletions",
            hint="total diff from default branch",
        )
    else:
        _kv(
            f"vs {default_branch}",
            c.yellow("no divergence"),
            hint="total diff from default branch",
        )
    if st_f or st_i or st_d:
        _kv(
            "Staged",
            f"{st_f} files changed, "
            f"{c.green(f'+{st_i}')} insertions, {c.red(f'-{st_d}')} deletions",
            hint="changes in index (git add)",
        )
    else:
        _kv("Staged", c.yellow("nothing staged"), hint="changes in index (git add)")
    if us_f or us_i or us_d:
        _kv(
            "Unstaged",
            f"{us_f} files changed, "
            f"{c.green(f'+{us_i}')} insertions, {c.red(f'-{us_d}')} deletions",
            hint="modified but not yet staged",
        )
    else:
        _kv("Unstaged", c.yellow("clean"), hint="modified but not yet staged")

    # ── Branch Characteristics ──
    if branch_chars:
        _section(f"Branch Characteristics: {c.green(current_branch)}")
        # Ordered characteristics with semantic coloring and descriptor hints
        char_keys: list[tuple[str, str, str]] = [
            (
                "Default branch",
                "behind_default",
                "commits on default not on this branch",
            ),
            ("Ahead of default", "ahead_default", "commits unique to this branch"),
            (
                "Head position",
                "on_default_head",
                "branch tip vs default tip (can be ahead and up-to-date)",
            ),
            ("Activity", "stale", "time since last commit on this branch"),
            ("Commit density", "commit_density", "recent commit frequency"),
            ("Branch age", "branch_age", "when branch first diverged from default"),
            ("Merge status", "fast_forwardable", "can branch merge without conflicts"),
            ("Remote", "local_only", "whether branch is pushed to remote (origin)"),
            ("Unpushed", "unpushed", "local commits not yet on remote (origin)"),
        ]
        # Keywords that indicate good/warning/info states
        _good = (
            "up to date",
            "active",
            "tracked",
            "fast-forwardable",
            "all commits pushed",
            "contained",
            "ahead of",
        )
        _warn = (
            "stale",
            "behind",
            "requires",
            "aging",
            "unpushed",
            "no commits",
            "local only",
        )
        for label, key, hint_text in char_keys:
            val = branch_chars.get(key, "")
            if not val:
                continue
            if any(w in val for w in _warn):
                _kv(label, c.yellow(val), hint=hint_text)
            elif any(w in val for w in _good):
                _kv(label, c.green(val), hint=hint_text)
            else:
                _kv(label, c.cyan(val), hint=hint_text)
        if "conflicts" in branch_chars:
            _kv(
                "Conflicts",
                c.red(branch_chars["conflicts"]),
                hint="unresolved merge conflicts",
            )

    # ── Last Merge from Default Branch (table format) ──
    if last_merge and current_branch != default_branch:
        _section(f"Last Merge from {default_branch}")
        sha_short = last_merge.get("sha_short", "?")
        msg = last_merge.get("message", "")
        rel_date = last_merge.get("relative_date", "")
        author = last_merge.get("author", "")
        default_ahead = last_merge.get("default_ahead", "0")
        current_ahead = last_merge.get("current_ahead", "0")

        # Build table rows: (Label, Value, Time/Detail)
        lbl_w = 18
        val_w = 52
        time_w = 18
        hdr_lbl = c.dim("Property".ljust(lbl_w))
        hdr_val = c.dim("Value".ljust(val_w))
        hdr_time = c.dim("When")
        print(f"    {hdr_lbl} {hdr_val} {hdr_time}")
        print(
            f"    {c.dim(h_line * lbl_w)} {c.dim(h_line * val_w)}"
            f" {c.dim(h_line * time_w)}"
        )
        # Merge base row — wrap long commit messages
        merge_val = f"{c.yellow(sha_short)} {msg}"
        print(f"    {'Merge base'.ljust(lbl_w)} {merge_val:{val_w}s} {c.dim(rel_date)}")
        print(f"    {'':{lbl_w}s} {c.dim('last common ancestor with default')}")
        if author:
            print(f"    {'Author'.ljust(lbl_w)} {author}")
        if default_ahead != "0":
            ahead_val = f"{c.yellow(default_ahead)} commit(s) ahead of merge base"
            print(f"    {(default_branch + ' ahead').ljust(lbl_w)} {ahead_val}")
            print(
                f"    {'':{lbl_w}s} {c.dim('new work on default since you branched')}"
            )
        if current_ahead != "0":
            br_val = f"{c.cyan(current_ahead)} commit(s) ahead of merge base"
            print(f"    {'Branch ahead'.ljust(lbl_w)} {br_val}")
            print(f"    {'':{lbl_w}s} {c.dim('your unique work since branching')}")
        if branch_divergence:
            div_sha = branch_divergence.get("sha", "")
            div_msg = branch_divergence.get("message", "")
            div_date = branch_divergence.get("date", "")
            div_val = f"{c.yellow(div_sha)} {div_msg}"
            print(
                f"    {'Branch started'.ljust(lbl_w)} {div_val:{val_w}s} {c.dim(div_date)}"
            )
            print(f"    {'':{lbl_w}s} {c.dim('first commit on this branch')}")

    # ── Working Tree ──
    if any(working_tree.values()) or modified_files:
        _section("Working Tree")
        for key, count in working_tree.items():
            if count > 0:
                color_fn = c.yellow if key != "conflicted" else c.red
                _kv(key.capitalize(), color_fn(str(count)), width=14)
        if modified_files:
            print()
            status_colors = {
                "modified": c.yellow,
                "added": c.green,
                "added (staged)": c.green,
                "modified (staged)": c.green,
                "deleted": c.red,
                "deleted (staged)": c.red,
                "untracked": c.cyan,
                "conflicted": c.red,
                "renamed": c.cyan,
                "renamed (staged)": c.cyan,
            }
            for mf in modified_files:
                color_fn = status_colors.get(mf["status"], c.cyan)
                print(f"    {color_fn(mf['status'].ljust(18))} {mf['file']}")
            total_mf = len(modified_files)
            code_mf, out_mf, _ = _run_git(["status", "--porcelain"])
            real_total = (
                len(out_mf.splitlines()) if code_mf == 0 and out_mf else total_mf
            )
            if real_total > total_mf:
                print(f"    {c.dim(f'... and {real_total - total_mf} more')}")
    else:
        print(f"\n    {c.green('Working directory is clean')}")

    # ── Local Branches ──
    if local_branches:
        _section("Local Branches")
        # Compute column widths from data
        name_w = max(len(b["name"]) for b in local_branches)
        name_w = max(name_w, 6) + 2  # min "Branch" + padding
        track_w = max((len(b.get("tracking", "")) for b in local_branches), default=8)
        track_w = max(track_w, 8) + 2  # min "Tracking" + padding
        status_w = max((len(b.get("status", "")) for b in local_branches), default=6)
        status_w = max(status_w, 6) + 2  # min "Status" + padding
        last_w = 16  # "Last Commit" column

        # Column headers
        hdr_branch = c.dim("Branch".ljust(name_w))
        hdr_track = c.dim("Tracking".ljust(track_w))
        hdr_status = c.dim("Status".ljust(status_w))
        hdr_last = c.dim("Last Commit")
        print(f"    {hdr_branch} {hdr_track} {hdr_status} {hdr_last}")
        print(
            f"    {c.dim(h_line * name_w)} {c.dim(h_line * track_w)} "
            f"{c.dim(h_line * status_w)} {c.dim(h_line * last_w)}"
        )

        for b in local_branches:
            is_current = b["name"] == current_branch
            marker = "* " if is_current else "  "
            bname = b["name"]
            name_str = c.green(bname) if is_current else bname
            tracking = b.get("tracking", "")
            bstatus = b.get("status", "")
            last = b.get("last_commit", "")

            # Pad name with raw text width (before color codes)
            name_pad = " " * max(0, name_w - len(bname))
            track_str = (
                tracking.ljust(track_w) if tracking else c.dim("(none)".ljust(track_w))
            )
            status_str = (
                bstatus.ljust(status_w) if bstatus else c.dim(dash.ljust(status_w))
            )
            # Color-code age: green (<7d), yellow (7-30d), red (>30d)
            if last:
                last_lower = last.lower()
                if any(x in last_lower for x in ("month", "year", "weeks")):
                    last_str = c.red(last)
                elif "week" in last_lower or (
                    "day" in last_lower
                    and not any(last_lower.startswith(f"{n} day") for n in range(1, 8))
                ):
                    last_str = c.yellow(last)
                else:
                    last_str = c.green(last)
            else:
                last_str = ""

            print(f"  {marker}{name_str}{name_pad} {track_str} {status_str} {last_str}")

    # ── Stale Branches ──
    if stale_branches:
        _section("Stale Branches (no activity > 30 days)")
        sb_name_w = max(len(sb["name"]) for sb in stale_branches)
        sb_name_w = max(sb_name_w, 6) + 2
        print(f"    {c.dim('Branch'.ljust(sb_name_w))} {c.dim('Last Activity')}")
        print(f"    {c.dim(h_line * sb_name_w)} {c.dim(h_line * 20)}")
        for sb in stale_branches:
            print(
                f"    {c.yellow(sb['name'].ljust(sb_name_w))} "
                f"{c.red(sb['last_commit'])}"
            )

    # ── Unmerged Branches ──
    if unmerged_branches:
        _section(f"Unmerged Branches (not in {default_branch})")
        ub_name_w = max(len(ub["name"]) for ub in unmerged_branches)
        ub_name_w = max(ub_name_w, 6) + 2
        print(f"    {c.dim('Branch'.ljust(ub_name_w))} {c.dim('Note')}")
        print(f"    {c.dim(h_line * ub_name_w)} {c.dim(h_line * 20)}")
        for ub in unmerged_branches:
            name = ub["name"]
            note = ub.get("note", "")
            note_str = c.dim(note) if note else c.dim(dash)
            print(f"    {name.ljust(ub_name_w)} {note_str}")

    # ── Recent Tags ──
    if tags:
        _section("Recent Tags")
        for tag in tags:
            print(f"    {tag}")

    # ── Recent Commits ──
    if recent_commits:
        _section(f"Recent Commits {dash} {c.green(current_branch)}")
        sha_w = 8
        msg_w = max(
            (len(cm["message"]) for cm in recent_commits),
            default=40,
        )
        msg_w = min(msg_w, 50) + 2  # cap at 50 chars
        author_w = max(
            (len(cm.get("author", "")) for cm in recent_commits),
            default=10,
        )
        author_w = min(author_w, 20) + 2
        print(
            f"    {c.dim('SHA'.ljust(sha_w))} "
            f"{c.dim('Message'.ljust(msg_w))} "
            f"{c.dim('Author'.ljust(author_w))} "
            f"{c.dim('When')}"
        )
        print(
            f"    {c.dim(h_line * sha_w)} "
            f"{c.dim(h_line * msg_w)} "
            f"{c.dim(h_line * author_w)} "
            f"{c.dim(h_line * 16)}"
        )
        for commit in recent_commits:
            sha = c.yellow(commit["sha"])
            msg = commit["message"]
            if len(msg) > 50:
                msg = msg[:47] + "..."
            author = commit.get("author", "")
            if len(author) > 20:
                author = author[:17] + "..."
            cdate = commit.get("date", "")
            # Pad raw text before color codes
            msg_pad = msg.ljust(msg_w)
            author_pad = author.ljust(author_w)
            print(f"    {sha} {msg_pad} {c.dim(author_pad)} {c.dim(cdate)}")

    # ── Stashes ──
    if stash_count > 0:
        _section("Stashes")
        print(
            f"    {c.yellow(str(stash_count))} stash(es) saved  {c.dim('shelved changes via git stash')}"
        )

    # ── Release Please ──
    _section("Release Please")
    if rp_branches:
        for branch in rp_branches:
            print(f"    {c.cyan(branch)}")
    else:
        print(f"    {c.yellow('No release-please branches found')}")

    # ── Health Checks ──
    _section("Health Checks")
    check_sym = sym.get("check", "")
    cross_sym = sym.get("cross", "")
    hc_name_w = (
        max((len(r["name"]) for r in health_results), default=0) + 1
    )  # +1 for colon
    for r in health_results:
        if r["status"] == "PASS":
            icon = (
                c.green(check_sym)
                if use_unicode
                else _icon(r["status"], use_color=use_color)
            )
        else:
            icon = (
                c.red(cross_sym)
                if use_unicode
                else _icon(r["status"], use_color=use_color)
            )
        label = (r["name"] + ":").ljust(hc_name_w)
        print(f"    {icon} {c.dim(label)} {r['message']}")

    # ── Helpful Commands ──
    _section("Helpful Commands")
    for cmd_info in HELPFUL_COMMANDS:
        print(f"    {c.cyan(cmd_info['cmd'])}")
        print(f"      {c.dim(cmd_info['desc'])}")

    # ── Summary ──
    elapsed = time.monotonic() - elapsed_start
    total = len(health_results)
    passed = total - failures
    print()
    print(c.cyan(f"  {h_double * 60}"))
    if failures == 0:
        sym_str = c.green(check_sym) if use_unicode else c.green("OK")
        print(f"  {sym_str} {c.green(f'All {total} health checks passed')}")
    else:
        sym_str = c.red(cross_sym) if use_unicode else c.red("!!")
        print(
            f"  {sym_str} {c.red(f'{failures} issue(s) found')}  "
            f"{c.dim(f'({passed}/{total} passed)')}"
        )
    print(
        f"  {c.dim(f'Completed in {elapsed:.1f}s  {dot}  git-doctor v{SCRIPT_VERSION}')}"
    )
    print(c.cyan(f"  {h_double * 60}"))
    print()

    return 1 if failures else 0


# ---------------------------------------------------------------------------
# Config fix
# ---------------------------------------------------------------------------


def fix_git_config(*, dry_run: bool = False) -> int:
    """Apply recommended git config settings that are currently unset.

    Only sets values at global scope. Skips any key that already has a
    value at any scope (local/global/system) to avoid overwriting
    intentional per-project overrides.

    Args:
        dry_run: If True, print what would be changed without applying.

    Returns:
        Number of settings applied (or that would be applied in dry-run).
    """
    use_color = _supports_color(sys.stdout)
    c = Colors(enabled=use_color)
    applied = 0
    skipped = 0

    print()
    print(c.bold("Git Config Fix" + (" (dry run)" if dry_run else "")))
    print(c.dim("=" * 60))
    print()

    for key, value, scope in RECOMMENDED_CONFIGS:
        current = get_git_config_value(key)
        if current:
            if current == value:
                print(f"  {c.dim(key):40s} {c.green('already set')}  {c.dim(current)}")
            else:
                print(
                    f"  {c.dim(key):40s} {c.yellow('different')}    "
                    f"{c.dim(current)} (keeping)"
                )
            skipped += 1
            continue

        if dry_run:
            print(f"  {key:40s} {c.cyan('would set')}   --{scope} {value}")
        else:
            code, _, err = _run_git(["config", f"--{scope}", key, value])
            if code == 0:
                print(f"  {key:40s} {c.green('applied')}     --{scope} {value}")
            else:
                print(f"  {key:40s} {c.red('failed')}      {err}")
            applied += 1

    print()
    if dry_run:
        pending = len(RECOMMENDED_CONFIGS) - skipped
        print(c.cyan(f"{pending} setting(s) would be applied, {skipped} already set"))
    else:
        print(c.green(f"{applied} setting(s) applied, {skipped} already set"))
    print()
    return applied


# ---------------------------------------------------------------------------
# Config export
# ---------------------------------------------------------------------------


def export_git_config_reference(filepath: str) -> str:
    """Write a comprehensive git configuration reference to a Markdown file.

    Args:
        filepath: Output file path.

    Returns:
        The absolute path of the written file.
    """
    from datetime import datetime
    from pathlib import Path

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Build table of contents from catalog sections
    seen_sections: list[str] = []
    for key, _, _, _ in GIT_CONFIG_CATALOG:
        section = _config_section(key)
        if section not in seen_sections:
            seen_sections.append(section)

    # Count config keys per section for the summary table
    section_counts: dict[str, int] = {}
    for key, _, _, _ in GIT_CONFIG_CATALOG:
        section = _config_section(key)
        section_counts[section] = section_counts.get(section, 0) + 1

    toc_lines: list[str] = []
    for s in seen_sections:
        anchor = s.lower().replace(" & ", "--").replace(" ", "-")
        count = section_counts.get(s, 0)
        desc = SECTION_DESCRIPTIONS.get(s, "")
        toc_lines.append(f"| [{s}](#{anchor}) | {count} | {desc} |")

    total_keys = len(GIT_CONFIG_CATALOG)

    lines: list[str] = [
        "# Git Configuration Reference",
        "",
        "<!-- Auto-generated by git_doctor.py — do not edit by hand. -->",
        "",
        f"| **Generated by** | `git_doctor.py` v{SCRIPT_VERSION} |",
        "|:-----------------|:-----------------------|",
        f"| **Timestamp**     | {timestamp} |",
        "| **Command**       | `python scripts/git_doctor.py --export-config` |",
        "| **Regenerate**    | Run the command above to refresh with current settings |",
        f"| **Total keys**    | {total_keys} commonly used keys across {len(seen_sections)} sections |",
        "",
        "> **Note:** This reference covers commonly used git configuration",
        "> options — it is not an exhaustive list. Git has 500+ configuration",
        "> keys; this file curates the ones most relevant to day-to-day",
        "> development workflows.",
        "",
        "Each entry shows the config key, its current value in your",
        "environment, which scope it's set in (local/global/system),",
        "what it does, and a recommended value.",
        "",
        "---",
        "",
        "## Contents",
        "",
        "| Section | Keys | Description |",
        "|---------|-----:|-------------|",
        *toc_lines,
        "",
        "---",
        "",
        "## Scope Guide",
        "",
        "| Scope | File Location | Applies To |",
        "|-------|---------------|------------|",
        "| **local** | `.git/config` in the repository | This repository only |",
        "| **global** | `~/.gitconfig` or `~/.config/git/config` | All your repositories |",
        "| **system** | `/etc/gitconfig` (Linux/macOS) or `C:\\Program Files\\Git\\etc\\gitconfig` (Windows) | All users on machine |",
        "",
        "**Precedence:** local > global > system.",
        "",
        "Set most configs at **global** scope so they apply everywhere,",
        "then override at **local** scope for project-specific needs",
        "(e.g. different email for work repos, project-specific commit template).",
        "",
        '> **Scope caveat for `--apply-from`:** The "Recommended scope" column',
        "> below reflects the *catalog default*, not necessarily the scope where",
        "> you currently have the key set. If you already have a key set at",
        "> **local** scope but the reference says **global**, running",
        "> `--apply-from` will create a *separate* global entry — both values",
        "> will exist, with the local value winning due to git's precedence",
        '> rules (`local > global > system`). Edit the "Recommended scope"',
        "> column to match your desired target scope before applying.",
        "",
        "### Updating Config Values",
        "",
        "```bash",
        "# Read a value (shows effective value from highest-priority scope)",
        "git config <key>",
        "",
        "# Read with origin (shows which file defines the value)",
        "git config --show-origin <key>",
        "",
        "# Set at different scopes",
        "git config --global <key> <value>    # ~/.gitconfig",
        "git config --local <key> <value>     # .git/config (this repo only)",
        "git config --system <key> <value>    # system-wide (requires admin)",
        "",
        "# Remove a value",
        "git config --global --unset <key>",
        "",
        "# List all settings with their scopes",
        "git config --list --show-origin",
        "```",
        "",
        "### Further Reading",
        "",
        "| Resource | Link |",
        "|:---------|:-----|",
        "| **Official git-config docs** | <https://git-scm.com/docs/git-config> |",
        "| **All git config variables** | <https://git-scm.com/docs/git-config#_variables> |",
        "| **Pro Git book (customization)** | <https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration> |",
        "| **Git attributes** | <https://git-scm.com/docs/gitattributes> |",
        "| **Conditional includes** | <https://git-scm.com/docs/git-config#_conditional_includes> |",
        "",
    ]

    current_section = ""
    for key, rec_scope, description, recommendation in GIT_CONFIG_CATALOG:
        section = _config_section(key)
        if section != current_section:
            if current_section:
                lines.append("---")
                lines.append("")
            current_section = section
            lines.append(f"## {section}")
            lines.append("")
            sect_desc = SECTION_DESCRIPTIONS.get(section, "")
            if sect_desc:
                lines.append(f"*{sect_desc}*")
                lines.append("")

        value = get_git_config_value(key) or "(unset)"
        scope = get_git_config_scope(key)

        lines.append(f"### `{key}`")
        lines.append("")
        lines.append(
            "| Property | Value |",
        )
        lines.append("|:---------|:------|")
        lines.append(f"| **Current value** | `{value}` |")
        lines.append(f"| **Set in** | {scope} |")
        lines.append(f"| **Recommended scope** | {rec_scope} |")
        lines.append("| **Desired value** | _(no change)_ |")
        lines.append("")
        lines.append(f"**Description:** {description}")
        lines.append("")
        lines.append(f"**Recommendation:** {recommendation}")
        lines.append("")

    # ── .gitattributes Reference ──
    lines.extend(
        [
            "---",
            "",
            "## .gitattributes Reference",
            "",
            "`.gitattributes` controls per-path settings in your repository.",
            "Unlike `.gitconfig`, these settings are **committed and shared**",
            "with all collaborators. Place this file in the repository root.",
            "",
            "### Sample .gitattributes",
            "",
            "```text",
            "# ── Line Endings ─────────────────────────────────────────",
            "# Force LF in the repo, let git handle working-tree conversion",
            "* text=auto eol=lf",
            "",
            "# Explicitly mark text files (override auto-detection)",
            "*.py    text eol=lf",
            "*.md    text eol=lf",
            "*.yml   text eol=lf",
            "*.yaml  text eol=lf",
            "*.toml  text eol=lf",
            "*.json  text eol=lf",
            "*.html  text eol=lf",
            "*.css   text eol=lf",
            "*.js    text eol=lf",
            "*.sh    text eol=lf",
            "",
            "# Windows-specific files that need CRLF",
            "*.bat   text eol=crlf",
            "*.cmd   text eol=crlf",
            "*.ps1   text eol=crlf",
            "",
            "# ── Binary Files ─────────────────────────────────────────",
            "# Mark binary files so git doesn't try to diff/merge them",
            "*.png    binary",
            "*.jpg    binary",
            "*.jpeg   binary",
            "*.gif    binary",
            "*.ico    binary",
            "*.woff   binary",
            "*.woff2  binary",
            "*.ttf    binary",
            "*.zip    binary",
            "*.tar.gz binary",
            "*.sqlite3 binary",
            "*.db     binary",
            "*.pdf    binary",
            "",
            "# ── Diff Drivers ─────────────────────────────────────────",
            "# Better diffs for specific file types",
            "*.md diff=markdown",
            "*.py diff=python",
            "",
            "# ── Export Ignore ────────────────────────────────────────",
            "# Files excluded from 'git archive' exports",
            ".gitattributes   export-ignore",
            ".gitignore       export-ignore",
            ".github/         export-ignore",
            "tests/           export-ignore",
            "docs/            export-ignore",
            "Taskfile.yml     export-ignore",
            "*.code-workspace export-ignore",
            "",
            "# ── Linguist (GitHub) ────────────────────────────────────",
            "# Override GitHub's language statistics",
            "docs/*    linguist-documentation",
            "scripts/* linguist-vendored=false",
            "```",
            "",
            "### Pattern Syntax",
            "",
            "| Pattern | Meaning |",
            "|:--------|:--------|",
            "| `*` | Match all files |",
            "| `*.py` | Match files ending in .py |",
            "| `text` | Treat as text (enable line-ending conversion) |",
            "| `text=auto` | Let git detect text vs binary |",
            "| `binary` | Treat as binary (no newline conversion, no diff) |",
            "| `eol=lf` | Force LF line endings in the repository |",
            "| `eol=crlf` | Force CRLF in the working tree |",
            "| `diff=python` | Use Python-aware diff heuristics |",
            "| `export-ignore` | Exclude from `git archive` exports |",
            "| `linguist-documentation` | Mark as documentation for GitHub stats |",
            "",
            "---",
            "",
            "## Applying Changes from This File",
            "",
            "You can edit the **Desired value** column in any config entry above,",
            "then apply all changes at once:",
            "",
            "```bash",
            "python scripts/git_doctor.py --apply-from git-config-reference.md",
            "```",
            "",
            "This reads each entry's **Desired value** and applies it via",
            "`git config`. Only entries where you changed `_(no change)_` to",
            "an actual value are applied. The **Recommended scope** determines",
            "whether it's set at `--local` or `--global` scope.",
            "",
            "> **Important:** The **Recommended scope** column defaults to the",
            "> catalog's suggested scope, not the scope where you currently have",
            "> the key set. If you have `push.default` at **local** scope but the",
            "> reference says **global**, applying will create a separate global",
            "> entry — both will exist, with the local value winning",
            "> (`local > global > system`). Check and update the scope column to",
            "> match your intent before applying.",
            "",
            "To preview what would change without applying:",
            "",
            "```bash",
            "python scripts/git_doctor.py --apply-from git-config-reference.md --dry-run",
            "```",
            "",
        ]
    )

    out_path = Path(filepath).resolve()
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return str(out_path)


# ---------------------------------------------------------------------------
# Apply config from reference file
# ---------------------------------------------------------------------------


def apply_from_reference(filepath: str, *, dry_run: bool = False) -> int:
    """Apply git config changes from an edited git-config-reference.md file.

    Parses the Markdown file for entries where the **Desired value** column
    has been changed from ``_(no change)_`` to an actual value.  Applies
    each change via ``git config`` at the scope specified in the
    **Recommended scope** column.

    Args:
        filepath: Path to the edited reference Markdown file.
        dry_run: If True, print what would be changed without applying.

    Returns:
        Number of settings applied (or that would be applied in dry-run).
    """
    from pathlib import Path

    use_color = _supports_color(sys.stdout)
    c = Colors(enabled=use_color)

    ref_path = Path(filepath)
    if not ref_path.is_file():
        print(c.red(f"File not found: {filepath}"))
        return 0

    content = ref_path.read_text(encoding="utf-8")

    # Parse each config key block:
    #   ### `key.name`
    #   | Property | Value |
    #   |:---------|:------|
    #   | **Current value** | `...` |
    #   | **Set in** | ... |
    #   | **Recommended scope** | ... |
    #   | **Desired value** | ... |
    key_pattern = re.compile(r"^### `(.+?)`$", re.MULTILINE)

    applied = 0
    skipped = 0

    print()
    print(c.bold("Apply Config from Reference" + (" (dry run)" if dry_run else "")))
    print(c.dim("=" * 60))
    print()

    matches = list(key_pattern.finditer(content))
    for i, match in enumerate(matches):
        key = match.group(1)
        # Extract the block between this key and the next (or end of file)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        block = content[start:end]

        # Find Desired value in table row
        desired_match = re.search(
            r"\|\s*\*\*Desired value\*\*\s*\|\s*(.+?)\s*\|", block
        )
        if not desired_match:
            continue
        desired_raw = desired_match.group(1).strip()

        # Skip entries where user didn't change the value
        if desired_raw in ("_(no change)_", "", "-"):
            continue

        # Strip backticks and quotes if user wrapped the value
        desired = desired_raw.strip("`'\"")
        if not desired:
            continue

        # Find recommended scope from table
        scope_match = re.search(
            r"\|\s*\*\*Recommended scope\*\*\s*\|\s*(.+?)\s*\|", block
        )
        scope = scope_match.group(1).strip() if scope_match else "global"

        if dry_run:
            print(f"  {key:40s} {c.cyan('would set')}   --{scope} {desired}")
        else:
            code, _, err = _run_git(["config", f"--{scope}", key, desired])
            if code == 0:
                print(f"  {key:40s} {c.green('applied')}     --{scope} {desired}")
            else:
                print(f"  {key:40s} {c.red('failed')}      {err}")
        applied += 1

    if applied == 0:
        skipped = len(matches)
        print(
            c.dim(
                "  No changes found. Edit the 'Desired value' column in the\n"
                "  reference file, then re-run this command."
            )
        )

    print()
    if dry_run:
        print(c.cyan(f"{applied} setting(s) would be applied, {skipped} unchanged"))
    else:
        print(c.green(f"{applied} setting(s) applied, {skipped} unchanged"))
    print()
    return applied


# ---------------------------------------------------------------------------
# Branch creation workflow (--new-branch)
# ---------------------------------------------------------------------------

# Well-known branch prefixes for the interactive picker.
# TODO (template users): Add, remove, or reorder prefixes to match your
#   team's branch naming conventions. The first entry is the default when
#   the user presses Enter without choosing.
_BRANCH_PREFIXES: list[tuple[str, str]] = [
    ("feature/", "New functionality"),
    ("fix/", "Bug fixes"),
    ("chore/", "Maintenance, deps"),
    ("docs/", "Documentation"),
    ("spike/", "Experimental / exploratory"),
    ("wip/", "Work in progress / scratch"),
    ("hotfix/", "Urgent production fix"),
    ("refactor/", "Code refactor"),
    ("test/", "Test additions / changes"),
    ("ci/", "CI/CD changes"),
]


def _prompt(prompt_text: str, *, default: str = "") -> str:
    """Read a line from stdin with an optional default value."""
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"  {prompt_text}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(130)
    return value or default


def create_new_branch(*, color: bool | None = None) -> int:
    """Interactive branch creation workflow.

    Walks the user through creating a branch off ``origin/main``,
    pushing it with upstream tracking, and printing a summary of
    every command that ran.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    use_color = color if color is not None else _supports_color(sys.stdout)
    use_unicode = _supports_unicode(sys.stdout)
    sym = _unicode_symbols(sys.stdout)
    c = Colors(enabled=use_color)
    check = sym.get("check", "+")
    cross = sym.get("cross", "x")
    h_line = "\u2500" if use_unicode else "-"
    h_double = "\u2550" if use_unicode else "="
    tl_d = "\u2554" if use_unicode else "+"
    tr_d = "\u2557" if use_unicode else "+"
    bl_d = "\u255a" if use_unicode else "+"
    br_d = "\u255d" if use_unicode else "+"
    vl_d = "\u2551" if use_unicode else "|"
    tl = "\u250c" if use_unicode else "+"
    tr = "\u2510" if use_unicode else "+"
    bl = "\u2514" if use_unicode else "+"
    br = "\u2518" if use_unicode else "+"
    vl = "\u2502" if use_unicode else "|"
    dot = "\u2022" if use_unicode else "*"

    # ── Title ──
    border = h_double * 60
    print()
    print(c.bold(c.cyan(f"  {tl_d}{border}{tr_d}")))
    print(f"  {c.bold(c.cyan(vl_d))} {c.bold(c.cyan('New Branch Creation'))}")
    print(c.bold(c.cyan(f"  {bl_d}{border}{br_d}")))
    print()

    # ── Prefix selection ──
    print(f"  {c.bold('Select a branch prefix:')}")
    print()
    for i, (prefix, desc) in enumerate(_BRANCH_PREFIXES, 1):
        print(f"    {c.cyan(str(i).rjust(2))}. {prefix:{14}s} {c.dim(desc)}")
    print()
    choice = _prompt("Choose a prefix (number or type your own)", default="1")

    # Resolve prefix
    if choice.isdigit() and 1 <= int(choice) <= len(_BRANCH_PREFIXES):
        prefix = _BRANCH_PREFIXES[int(choice) - 1][0]
    else:
        # User typed a custom prefix — ensure it ends with /
        prefix = choice if choice.endswith("/") else f"{choice}/"

    # ── Branch name ──
    print()
    slug = _prompt(f"Branch name (after {c.cyan(prefix)})")
    if not slug:
        print(f"\n  {c.red(cross)} Branch name cannot be empty.")
        return 1

    # Sanitise: lowercase, replace spaces/underscores with hyphens
    # TODO (template users): Adjust sanitisation rules if your team uses
    #   uppercase, underscores, or other characters in branch names.
    slug = re.sub(r"[\s_]+", "-", slug.strip().lower())
    slug = re.sub(r"[^a-z0-9\-/.]", "", slug)
    branch_name = f"{prefix}{slug}"

    # Confirm
    print()
    print(f"  Branch to create: {c.bold(c.green(branch_name))}")
    confirm = _prompt("Proceed? (Y/n)", default="Y")
    if confirm.lower() not in ("y", "yes", ""):
        print(f"\n  {c.dim('Cancelled.')}")
        return 0

    # ── Execute commands ──
    steps: list[tuple[str, list[str], str]] = [
        (
            "Switch to main branch",
            ["switch", "main"],
            "git switch main",
        ),
        (
            "Update main (fast-forward only)",
            ["pull", "--ff-only"],
            "git pull --ff-only",
        ),
        (
            "Fetch latest commits from remote",
            ["fetch", "origin"],
            "git fetch origin",
        ),
        (
            f"Create and switch to {branch_name}",
            ["switch", "-c", branch_name, "origin/main"],
            f"git switch -c {branch_name} origin/main",
        ),
        (
            "Push branch and set upstream tracking",
            ["push", "-u", "origin", "HEAD"],
            "git push -u origin HEAD",
        ),
    ]

    results: list[tuple[str, str, bool, str, str]] = []
    print()
    section_border = h_line * 60
    print(c.cyan(f"  {tl}{section_border}{tr}"))
    print(f"  {c.cyan(vl)} {c.bold('Running commands')}")
    print(c.cyan(f"  {bl}{section_border}{br}"))
    print()

    failed = False
    for description, git_args, display_cmd in steps:
        if failed:
            results.append((description, display_cmd, False, "", "skipped"))
            print(f"    {c.dim('--')} {c.dim(display_cmd):40s} {c.dim('skipped')}")
            continue

        code, out, err = _run_git(git_args)
        ok = code == 0
        if not ok:
            failed = True
        icon = c.green(check) if ok else c.red(cross)
        status_text = c.green("ok") if ok else c.red("failed")
        results.append((description, display_cmd, ok, out, err))
        print(f"    {icon} {display_cmd:40s} {status_text}")
        if not ok and err:
            print(f"      {c.red(err)}")

    # ── Verify final branch ──
    print()
    code, final_branch, _ = _run_git(["branch", "--show-current"])
    _code2, status_out, _ = _run_git(["status", "-sb"])

    # ── Summary ──
    print(c.cyan(f"  {tl}{section_border}{tr}"))
    print(f"  {c.cyan(vl)} {c.bold('Summary')}")
    print(c.cyan(f"  {bl}{section_border}{br}"))
    print()

    if not failed:
        print(f"    {c.green(check)} {c.bold('New branch created successfully')}")
    else:
        print(f"    {c.red(cross)} {c.bold('Branch creation failed')}")

    print(f"    {dot} Branch:  {c.bold(c.green(final_branch or branch_name))}")
    if status_out:
        print(f"    {dot} Status:  {c.dim(status_out.splitlines()[0])}")
    print()

    # Command log with descriptions
    print(f"    {c.bold('Commands executed:')}")
    for desc, cmd, ok, _out, err_msg in results:
        icon = (
            c.green(check)
            if ok
            else (c.red(cross) if err_msg != "skipped" else c.dim("-"))
        )
        print(f"      {icon} {c.cyan(cmd)}")
        print(f"        {c.dim(desc)}")
        if not ok and err_msg and err_msg != "skipped":
            print(f"        {c.red(err_msg)}")

    # ── Recommendations ──
    print()
    print(f"    {c.bold('Next steps:')}")
    print(
        f"      {dot} Run {c.cyan('python scripts/git_doctor.py')} or "
        f"{c.cyan('task doctor:git')} to see full branch diagnostics"
    )
    print(
        f"      {dot} Start making {c.cyan('conventional commits')} "
        f"(e.g. feat:, fix:, docs:)"
    )
    print(
        f"      {dot} When ready, open a {c.cyan('Pull Request')} "
        f"targeting {c.cyan('main')}"
    )
    print()

    return 1 if failed else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point for git_doctor.

    Returns:
        Exit code from run().
    """
    parser = argparse.ArgumentParser(
        description="Git-focused health check and information dashboard.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (for CI integration)",
    )
    parser.add_argument(
        "--export-config",
        nargs="?",
        const="git-config-reference.md",
        default=None,
        metavar="PATH",
        help="Export comprehensive git config reference to a Markdown file "
        "(default: git-config-reference.md). NOTE: overwrites the file on each run.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply recommended git config settings (only sets unset values)",
    )
    parser.add_argument(
        "--apply-from",
        default=None,
        metavar="PATH",
        help="Apply desired values from an edited config reference file "
        "(exported with --export-config). Edit the 'Desired value' column, "
        "then run this to apply changes.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="With --fix or --apply-from, show what would be changed without applying",
    )
    parser.add_argument(
        "--new-branch",
        action="store_true",
        help="Interactive branch creation: prompts for a name, creates the "
        "branch off origin/main, pushes with upstream tracking, and "
        "prints a summary of all commands executed",
    )
    parser.add_argument(
        "--watch",
        nargs="?",
        const=10,
        default=None,
        type=int,
        metavar="SECONDS",
        help="Re-run the dashboard every N seconds (default: 10). "
        "Press Ctrl+C to stop.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # --new-branch mode: interactive branch creation and exit
    if args.new_branch:
        nb_color = False if args.no_color else None
        return create_new_branch(color=nb_color)

    # --apply-from mode: apply desired values from edited reference file
    if args.apply_from:
        apply_from_reference(args.apply_from, dry_run=args.dry_run)
        return 0

    # --fix mode: apply recommended configs and exit
    if args.fix:
        fix_git_config(dry_run=args.dry_run)
        return 0

    color = False if args.no_color else None

    # --watch mode: re-run dashboard on an interval until Ctrl+C
    if args.watch is not None:
        interval = max(args.watch, 2)  # minimum 2 seconds
        try:
            while True:
                # Clear terminal (cross-platform)
                subprocess.run(  # nosec B603
                    ["cmd", "/c", "cls"] if os.name == "nt" else ["clear"],
                    check=False,
                )
                run(color=color, output_json=args.json)
                print(f"\n  Watching every {interval}s — press Ctrl+C to stop")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n  Watch stopped.")
        return 0

    exit_code = run(color=color, output_json=args.json)

    if args.export_config:
        out_path = export_git_config_reference(args.export_config)
        print(f"\nGit config reference written to: {out_path}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
