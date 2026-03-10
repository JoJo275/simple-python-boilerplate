#!/usr/bin/env python3
"""Git-focused health check and information dashboard.

Displays a comprehensive overview of the repository's git state:
branches, remotes, current working branch, recent commits, open
PRs/issues status, release-please branches, and git-related health
checks.

Flags::

    --no-color   Disable colored output
    --json       Output results as JSON (for CI integration)
    --version    Print version and exit

Usage::

    python scripts/git_doctor.py
    python scripts/git_doctor.py --json
    python scripts/git_doctor.py --no-color
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import subprocess  # nosec B404
import sys
import time
from collections.abc import Callable

from _colors import Colors
from _colors import status_icon as _icon
from _colors import supports_color as _supports_color
from _colors import supports_unicode as _supports_unicode
from _doctor_common import extract_repo_slug, read_pyproject
from _imports import find_repo_root

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.3.0"

logger = logging.getLogger(__name__)

ROOT = find_repo_root()

_GIT: str | None = shutil.which("git")

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
    """Return the date of the first commit (repo creation proxy)."""
    code, out, _ = _run_git(["log", "--reverse", "--format=%ar", "-1"])
    return out if code == 0 and out else "unknown"


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


def get_file_change_summary() -> dict[str, int]:
    """Return file change counts from recent commits."""
    code, out, _ = _run_git(["diff", "--stat", "--shortstat", "HEAD~5..HEAD"])
    if code != 0 or not out:
        return {}
    counts: dict[str, int] = {
        "files_changed": 0,
        "insertions": 0,
        "deletions": 0,
    }
    for line in out.splitlines():
        if "changed" in line:
            parts = line.strip().split(",")
            for part in parts:
                part = part.strip()
                if "file" in part:
                    counts["files_changed"] = int(re.sub(r"\D", "", part) or 0)
                elif "insertion" in part:
                    counts["insertions"] = int(re.sub(r"\D", "", part) or 0)
                elif "deletion" in part:
                    counts["deletions"] = int(re.sub(r"\D", "", part) or 0)
    return counts


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
    """Check if current branch is ahead/behind its upstream."""
    code, out, _ = _run_git(
        ["rev-list", "--left-right", "--count", "@{upstream}...HEAD"]
    )
    if code != 0:
        return "no upstream"
    parts = out.split()
    if len(parts) == 2:
        behind, ahead = int(parts[0]), int(parts[1])
        if ahead == 0 and behind == 0:
            return "up to date"
        msgs: list[str] = []
        if ahead > 0:
            msgs.append(f"{ahead} ahead")
        if behind > 0:
            msgs.append(f"{behind} behind")
        return ", ".join(msgs)
    return "unknown"


def get_merge_conflicts() -> bool:
    """Check if there are unresolved merge conflicts."""
    code, out, _ = _run_git(["diff", "--check"])
    return code != 0 and "conflict" in out.lower()


def get_git_config_value(key: str) -> str:
    """Get a git config value."""
    code, out, _ = _run_git(["config", "--get", key])
    return out if code == 0 else ""


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
    """Check if default branch in git matches workflow expectations."""
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
]


def _collect_info() -> dict[
    str,
    str | int | list[str] | list[dict[str, str]] | dict[str, int],
]:
    """Collect all git information into a dict."""
    return {
        "current_branch": get_current_branch(),
        "default_branch": get_default_branch(),
        "remote_url": get_remote_url(),
        "remotes": get_all_remotes(),
        "upstream_status": get_upstream_status(),
        "local_branches": get_local_branches(),
        "remote_branches": get_remote_branches(),
        "recent_commits": get_recent_commits(5),
        "tags": get_tags(5),
        "stash_count": get_stash_count(),
        "commit_count": get_commit_count(),
        "repo_age": get_repo_age(),
        "contributors": get_contributors_count(),
        "working_tree": get_working_tree_status(),
        "release_please_branches": find_release_please_branches(),
        "user_name": get_git_config_value("user.name"),
        "user_email": get_git_config_value("user.email"),
    }


def _collect_health() -> tuple[list[dict[str, str]], int]:
    """Run all health checks and return (results, failure_count)."""
    results: list[dict[str, str]] = []
    failures = 0
    for name, check_fn in HEALTH_CHECKS:
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
    commit_freq = get_commit_frequency()
    file_changes = get_file_change_summary()

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
    bar_char = "\u2588" if use_unicode else "#"
    c = Colors(enabled=use_color)

    # ── Header ──
    print()
    print(c.bold("Git Doctor"))
    print(c.dim("=" * 60))

    # ── Repository Info ──
    print()
    print(c.bold("Repository"))
    print(c.dim("-" * 60))
    print(f"  Remote URL:     {remote_url}")
    print(f"  Current branch: {c.green(current_branch)}")
    print(f"  Default branch: {default_branch}")
    print(f"  Upstream:       {upstream_status}")
    print(f"  User:           {user_name} <{user_email}>")
    print(f"  Commits:        {commit_count}")
    print(f"  Contributors:   {contributors}")
    print(f"  Repo age:       {repo_age}")

    # ── Commit Activity (last 14 days) ──
    if commit_freq:
        print()
        print(c.bold("Commit Activity (last 14 days)"))
        print(c.dim("-" * 60))
        max_count = max(commit_freq.values()) if commit_freq else 1
        for date in sorted(commit_freq):
            count = commit_freq[date]
            bar_len = int((count / max_count) * 30) if max_count > 0 else 0
            bar = c.green(bar_char * bar_len)
            print(f"  {date}  {bar} {count}")
        total_recent = sum(commit_freq.values())
        avg = total_recent / len(commit_freq) if commit_freq else 0
        print(f"  {c.dim(f'Total: {total_recent} commits, avg {avg:.1f}/day')}")

    # ── File Change Summary (last 5 commits) ──
    if file_changes and any(file_changes.values()):
        print()
        print(c.bold("Recent File Changes (last 5 commits)"))
        print(c.dim("-" * 60))
        fc = file_changes
        ins = fc.get("insertions", 0)
        dels = fc.get("deletions", 0)
        files = fc.get("files_changed", 0)
        print(f"  Files changed:  {files}")
        print(f"  Insertions:     {c.green(f'+{ins}')}")
        print(f"  Deletions:      {c.red(f'-{dels}')}")

    # ── Working Tree ──
    if any(working_tree.values()):
        print()
        print(c.bold("Working Tree"))
        print(c.dim("-" * 60))
        for key, count in working_tree.items():
            if count > 0:
                color_fn = c.yellow if key != "conflicted" else c.red
                print(f"  {key.capitalize():12s} {color_fn(str(count))}")
    else:
        print(f"\n  {c.green('Working directory is clean')}")

    # ── Local Branches ──
    if local_branches:
        print()
        print(c.bold("Local Branches"))
        print(c.dim("-" * 60))
        for b in local_branches:
            marker = "* " if b["name"] == current_branch else "  "
            bname = b["name"]
            name_str = c.green(bname) if bname == current_branch else bname
            tracking = b.get("tracking", "")
            bstatus = b.get("status", "")
            last = b.get("last_commit", "")
            extra = ""
            if tracking:
                extra += f" -> {tracking}"
            if bstatus:
                extra += f" {bstatus}"
            if last:
                extra += f"  ({last})"
            print(f"  {marker}{name_str}{c.dim(extra)}")

    # ── Recent Tags ──
    if tags:
        print()
        print(c.bold("Recent Tags"))
        print(c.dim("-" * 60))
        for tag in tags:
            print(f"  {tag}")

    # ── Recent Commits ──
    if recent_commits:
        print()
        print(c.bold("Recent Commits"))
        print(c.dim("-" * 60))
        for commit in recent_commits:
            sha = c.yellow(commit["sha"])
            msg = commit["message"]
            cdate = commit.get("date", "")
            print(f"  {sha} {msg}  {c.dim(cdate)}")

    # ── Stashes ──
    if stash_count > 0:
        print()
        print(f"  Stashes: {c.yellow(str(stash_count))}")

    # ── Release Please ──
    print()
    print(c.bold("Release Please"))
    print(c.dim("-" * 60))
    if rp_branches:
        for branch in rp_branches:
            print(f"  {c.cyan(branch)}")
    else:
        print(f"  {c.dim('No release-please branches found')}")

    # ── Health Checks ──
    print()
    print(c.bold("Health Checks"))
    print(c.dim("-" * 60))
    for r in health_results:
        print(
            f"  [{_icon(r['status'], use_color=use_color)}]"
            f" {c.dim(r['name'] + ':')} {r['message']}"
        )

    # ── Helpful Commands ──
    print()
    print(c.bold("Helpful Commands"))
    print(c.dim("-" * 60))
    for cmd_info in HELPFUL_COMMANDS:
        print(f"  {c.cyan(cmd_info['cmd'])}")
        print(f"    {c.dim(cmd_info['desc'])}")

    # ── Summary ──
    elapsed = time.monotonic() - elapsed_start
    print()
    total = len(health_results)
    passed = total - failures
    if failures == 0:
        print(c.green(f"All {total} health checks passed!"))
    else:
        print(c.red(f"{passed}/{total} checks passed, {failures} issues found"))
    print(c.dim(f"Completed in {elapsed:.1f}s"))
    print()

    return 1 if failures else 0


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
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    color = False if args.no_color else None
    return run(color=color, output_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
