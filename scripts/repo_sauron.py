#!/usr/bin/env python3
"""Repository statistics dashboard — the all-seeing eye for any git repo.

Generates a comprehensive Markdown report about the current repository:
file counts by type, lines of code, language breakdown, full directory tree,
file access statistics, per-file git commit history, contributor list,
code/script activity tracking, and more. Works on any git repository,
not just this template.

Named after Sauron's all-seeing eye from The Lord of the Rings.

Flags::

    --output PATH       Output file path (default: repo-sauron-report.md)
    --json              Output as JSON (for CI integration)
    -q, --quiet         Suppress output; exit code only
    --version           Print version and exit

Usage::

    python scripts/repo_sauron.py
    python scripts/repo_sauron.py --output docs/report.md
    python scripts/repo_sauron.py --json

Output:
    Generates a Markdown file with colored sections, table of contents,
    repo structure tree, file access stats, and per-file git history.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess  # nosec B404
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

# -- Local script modules (not third-party; live in scripts/) ----------------
from _colors import Colors
from _imports import find_repo_root
from _progress import Spinner

log = logging.getLogger(__name__)

SCRIPT_VERSION = "2.0.0"

ROOT = find_repo_root()

# Directories to skip when scanning (common build/cache artifacts)
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    ".tox",
    ".nox",
    "site",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
    ".cache",
    "htmlcov",
}

_GIT_CMD: str | None = shutil.which("git")

# Map file extensions to language names
_EXT_TO_LANGUAGE: dict[str, str] = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript (JSX)",
    ".tsx": "TypeScript (TSX)",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".less": "Less",
    ".java": "Java",
    ".kt": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cs": "C#",
    ".swift": "Swift",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".r": "R",
    ".lua": "Lua",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".json": "JSON",
    ".xml": "XML",
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Plain Text",
    ".cfg": "Config",
    ".ini": "Config",
    ".dockerfile": "Dockerfile",
}

# Extensions considered "code" files
_CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".rs",
    ".rb",
    ".java",
    ".c",
    ".cpp",
    ".cs",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
}

# Extensions considered "script" files specifically
_SCRIPT_EXTENSIONS = {".py", ".sh", ".bash", ".zsh", ".ps1", ".rb", ".pl"}


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _run_git(args: list[str], *, timeout: int = 30) -> tuple[int, str]:
    """Run a git command and return (returncode, stdout)."""
    if _GIT_CMD is None:
        return 1, ""
    try:
        result = subprocess.run(  # nosec B603
            [_GIT_CMD, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return 1, ""


# ---------------------------------------------------------------------------
# Stats collectors
# ---------------------------------------------------------------------------


def _collect_file_stats() -> dict:
    """Walk the repo and collect file statistics."""
    total_files = 0
    total_dirs = 0
    total_size = 0
    extension_counts: Counter[str] = Counter()
    extension_lines: Counter[str] = Counter()
    language_lines: Counter[str] = Counter()
    language_files: Counter[str] = Counter()
    largest_files: list[tuple[str, int]] = []
    code_file_count = 0
    script_file_count = 0

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [
            d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".egg-info")
        ]
        total_dirs += 1

        for fname in filenames:
            filepath = Path(dirpath) / fname
            try:
                size = filepath.stat().st_size
            except OSError:
                continue

            total_files += 1
            total_size += size
            ext = filepath.suffix.lower() or "(no ext)"
            extension_counts[ext] += 1

            lang = _EXT_TO_LANGUAGE.get(ext)
            if lang is None and fname.lower() in ("containerfile", "dockerfile"):
                lang = "Dockerfile"
            if lang:
                language_files[lang] += 1

            if ext in _CODE_EXTENSIONS:
                code_file_count += 1
            if ext in _SCRIPT_EXTENSIONS:
                script_file_count += 1

            if ext in (
                ".py",
                ".yml",
                ".yaml",
                ".md",
                ".toml",
                ".json",
                ".txt",
                ".sh",
                ".sql",
                ".html",
                ".css",
                ".js",
                ".ts",
            ):
                try:
                    line_count = len(filepath.read_bytes().split(b"\n"))
                    extension_lines[ext] += line_count
                    if lang:
                        language_lines[lang] += line_count
                except OSError:
                    pass

            rel = str(filepath.relative_to(ROOT))
            largest_files.append((rel, size))

    largest_files.sort(key=lambda x: x[1], reverse=True)

    total_lang_files = sum(language_files.values())
    languages: list[dict] = []
    for lang, count in language_files.most_common(20):
        pct = (count / total_lang_files * 100) if total_lang_files else 0
        languages.append(
            {
                "language": lang,
                "files": count,
                "lines": language_lines.get(lang, 0),
                "percentage": round(pct, 1),
            }
        )

    return {
        "total_files": total_files,
        "total_dirs": total_dirs,
        "total_size_bytes": total_size,
        "avg_file_size_bytes": total_size // total_files if total_files else 0,
        "extension_counts": dict(extension_counts.most_common(20)),
        "extension_lines": dict(extension_lines.most_common(20)),
        "languages": languages,
        "largest_files": [(f, s) for f, s in largest_files[:15]],
        "code_file_count": code_file_count,
        "script_file_count": script_file_count,
    }


def _collect_git_stats() -> dict:
    """Collect git repository statistics."""
    stats: dict = {"available": False}

    code, out = _run_git(["rev-parse", "--is-inside-work-tree"])
    if code != 0 or out != "true":
        return stats

    stats["available"] = True

    code, out = _run_git(["rev-list", "--count", "HEAD"])
    stats["total_commits"] = int(out) if code == 0 and out.isdigit() else 0

    code, out = _run_git(["shortlog", "-sn", "--no-merges", "HEAD"])
    if code == 0 and out:
        authors = []
        for line in out.splitlines():
            parts = line.strip().split("\t", 1)
            if len(parts) == 2:
                authors.append(
                    {
                        "commits": int(parts[0].strip()),
                        "name": parts[1].strip(),
                    }
                )
        stats["authors"] = authors[:10]
        stats["author_count"] = len(authors)
    else:
        stats["authors"] = []
        stats["author_count"] = 0

    code, out = _run_git(["branch", "--list"])
    if code == 0:
        branches = [b.strip().lstrip("* ") for b in out.splitlines() if b.strip()]
        stats["branch_count"] = len(branches)
    else:
        stats["branch_count"] = 0

    code, out = _run_git(["tag", "--list"])
    if code == 0:
        tags = [t.strip() for t in out.splitlines() if t.strip()]
        stats["tag_count"] = len(tags)
        stats["latest_tag"] = tags[-1] if tags else None
    else:
        stats["tag_count"] = 0
        stats["latest_tag"] = None

    code, out = _run_git(["branch", "--show-current"])
    stats["current_branch"] = out if code == 0 else None

    code, out = _run_git(["log", "--reverse", "--format=%aI", "-1"])
    stats["first_commit_date"] = out if code == 0 and out else None

    code, out = _run_git(["log", "--format=%aI", "-1"])
    stats["last_commit_date"] = out if code == 0 and out else None

    code, out = _run_git(["remote", "get-url", "origin"])
    stats["remote_url"] = out if code == 0 and out else None

    return stats


def _collect_file_git_stats() -> dict[str, dict]:
    """Collect per-file git commit counts and last commit dates."""
    file_stats: dict[str, dict] = {}

    if _GIT_CMD is None:
        return file_stats

    code, out = _run_git(["ls-files"], timeout=30)
    if code != 0 or not out:
        return file_stats

    tracked_files = [f for f in out.splitlines() if f.strip()]

    for filepath in tracked_files:
        code, count_out = _run_git(["rev-list", "--count", "HEAD", "--", filepath])
        commit_count = int(count_out) if code == 0 and count_out.isdigit() else 0

        code, date_out = _run_git(["log", "-1", "--format=%aI", "--", filepath])
        last_commit = date_out if code == 0 and date_out else None

        file_stats[filepath] = {
            "commits": commit_count,
            "last_commit": last_commit,
        }

    return file_stats


def _collect_file_access_stats() -> dict[str, dict]:
    """Collect file access timestamps from the filesystem."""
    access_stats: dict[str, dict] = {}

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [
            d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".egg-info")
        ]

        for fname in filenames:
            filepath = Path(dirpath) / fname
            try:
                stat = filepath.stat()
                rel = str(filepath.relative_to(ROOT))
                atime = datetime.fromtimestamp(stat.st_atime, tz=UTC)
                access_stats[rel] = {
                    "last_accessed": atime.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "last_accessed_iso": atime.isoformat(),
                }
            except OSError:
                continue

    return access_stats


def _collect_directory_sizes() -> list[tuple[str, int, int]]:
    """Get all directory sizes sorted largest-first."""
    dirs: list[tuple[str, int, int]] = []

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [
            d
            for d in dirnames
            if d not in SKIP_DIRS
            and not d.startswith(".")
            and not d.endswith(".egg-info")
        ]

        rel_path = Path(dirpath).relative_to(ROOT)
        if str(rel_path) == ".":
            continue

        total_size = 0
        file_count = 0
        for fname in filenames:
            try:
                total_size += (Path(dirpath) / fname).stat().st_size
            except OSError:
                continue
            file_count += 1

        dirs.append((str(rel_path), total_size, file_count))

    dirs.sort(key=lambda x: x[1], reverse=True)
    return dirs


def _build_repo_tree() -> str:
    """Build a full directory/file tree of the repository."""
    lines: list[str] = []
    repo_name = ROOT.name

    def _walk(directory: Path, prefix: str = "") -> None:
        entries = sorted(
            directory.iterdir(),
            key=lambda e: (not e.is_dir(), e.name.lower()),
        )
        entries = [
            e
            for e in entries
            if not (
                e.is_dir()
                and (
                    e.name in SKIP_DIRS
                    or e.name.startswith(".")
                    or e.name.endswith(".egg-info")
                )
            )
        ]

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
            extension = "    " if is_last else "\u2502   "

            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                _walk(entry, prefix + extension)
            else:
                lines.append(f"{prefix}{connector}{entry.name}")

    lines.append(f"{repo_name}/")
    _walk(ROOT)
    return "\n".join(lines)


def _collect_code_execution_stats(
    file_git_stats: dict[str, dict],
) -> dict:
    """Estimate code/script activity from git commit frequency.

    Uses per-file commit counts as a proxy for how actively code and
    script files are used/developed.
    """
    code_runs: list[tuple[str, int, str | None]] = []
    script_runs: list[tuple[str, int, str | None]] = []

    for filepath, stats in file_git_stats.items():
        ext = Path(filepath).suffix.lower()
        entry = (filepath, stats["commits"], stats.get("last_commit"))

        if ext in _CODE_EXTENSIONS:
            code_runs.append(entry)
        if ext in _SCRIPT_EXTENSIONS:
            script_runs.append(entry)

    code_runs.sort(key=lambda x: x[1], reverse=True)
    script_runs.sort(key=lambda x: x[1], reverse=True)

    return {
        "code_files": code_runs[:30],
        "script_files": script_runs[:30],
    }


def _format_size(size_bytes: int) -> str:
    """Format byte size to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def _md_badge(label: str, value: str, color: str = "blue") -> str:
    """Generate a shields.io-style static badge in Markdown."""
    label_enc = label.replace(" ", "%20").replace("-", "--")
    value_enc = value.replace(" ", "%20").replace("-", "--")
    return f"![{label}](https://img.shields.io/badge/{label_enc}-{value_enc}-{color})"


# ---------------------------------------------------------------------------
# Markdown report generator
# ---------------------------------------------------------------------------


def gather_stats(*, spinner: Spinner | None = None) -> dict:
    """Gather all repository statistics."""
    if spinner:
        spinner.update("Collecting file stats")
    file_stats = _collect_file_stats()

    if spinner:
        spinner.update("Collecting git stats")
    git_stats = _collect_git_stats()

    if spinner:
        spinner.update("Collecting directory sizes")
    directories = [
        {"name": n, "size_bytes": s, "file_count": c}
        for n, s, c in _collect_directory_sizes()
    ]

    if spinner:
        spinner.update("Collecting per-file git history")
    file_git_stats = _collect_file_git_stats()

    if spinner:
        spinner.update("Collecting file access stats")
    file_access_stats = _collect_file_access_stats()

    if spinner:
        spinner.update("Building repository tree")
    repo_tree = _build_repo_tree()

    if spinner:
        spinner.update("Analyzing code activity patterns")
    execution_stats = _collect_code_execution_stats(file_git_stats)

    return {
        "files": file_stats,
        "git": git_stats,
        "directories": directories,
        "file_git_stats": file_git_stats,
        "file_access_stats": file_access_stats,
        "repo_tree": repo_tree,
        "execution_stats": execution_stats,
    }


def generate_markdown(stats: dict) -> str:
    """Generate the full Markdown report from gathered statistics."""
    lines: list[str] = []
    now = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    file_stats = stats["files"]
    git_stats = stats["git"]
    file_git = stats.get("file_git_stats", {})
    file_access = stats.get("file_access_stats", {})
    execution = stats.get("execution_stats", {})
    repo_name = ROOT.name

    # ── Title ──
    lines.append(f"# \U0001f534 Repository Sauron Report \u2014 {repo_name}")
    lines.append("")
    lines.append("> *The all-seeing eye peers into every corner of your repository.*")
    lines.append(">")
    lines.append(f"> **Generated:** {now}")
    lines.append(f"> **Version:** {SCRIPT_VERSION}")
    if git_stats.get("current_branch"):
        lines.append(f"> **Branch:** `{git_stats['current_branch']}`")
    lines.append("")

    # ── Badges ──
    lines.append(_md_badge("files", str(file_stats["total_files"]), "blue"))
    lines.append(
        _md_badge("size", _format_size(file_stats["total_size_bytes"]), "green")
    )
    if git_stats.get("available"):
        lines.append(
            _md_badge("commits", str(git_stats.get("total_commits", 0)), "orange")
        )
        lines.append(
            _md_badge("contributors", str(git_stats.get("author_count", 0)), "purple")
        )
    lines.append(
        _md_badge(
            "code files", str(file_stats.get("code_file_count", 0)), "brightgreen"
        )
    )
    lines.append(
        _md_badge("script files", str(file_stats.get("script_file_count", 0)), "yellow")
    )
    lines.append("")

    # ── Table of Contents ──
    lines.append("---")
    lines.append("")
    lines.append("## \U0001f4d1 Table of Contents")
    lines.append("")
    lines.append("- [Overview](#-overview)")
    lines.append("- [Repository Structure](#-repository-structure)")
    lines.append("- [File Types](#-file-types)")
    lines.append("- [Languages](#-languages)")
    lines.append("- [Code & Script Activity](#-code--script-activity)")
    lines.append("- [Directory Sizes](#-directory-sizes)")
    lines.append("- [Largest Files](#-largest-files)")
    lines.append("- [File Access Statistics](#-file-access-statistics)")
    lines.append("- [Git History](#-git-history)")
    lines.append("- [Per-File Git Statistics](#-per-file-git-statistics)")
    lines.append("- [Contributors](#-contributors)")
    lines.append("- [Recommended Scripts](#-recommended-scripts)")
    lines.append("")

    # ── Overview ──
    lines.append("---")
    lines.append("")
    lines.append("## \U0001f4ca Overview")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append("> High-level repository metrics at a glance.")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| **Total files** | {file_stats['total_files']} |")
    lines.append(f"| **Total directories** | {file_stats['total_dirs']} |")
    lines.append(f"| **Total size** | {_format_size(file_stats['total_size_bytes'])} |")
    avg_file = file_stats.get("avg_file_size_bytes", 0)
    if avg_file:
        lines.append(f"| **Avg file size** | {_format_size(avg_file)} |")
    lines.append(f"| **Code files** | {file_stats.get('code_file_count', 0)} |")
    lines.append(f"| **Script files** | {file_stats.get('script_file_count', 0)} |")

    dir_stats = stats["directories"]
    if dir_stats:
        total_dir_size = sum(d["size_bytes"] for d in dir_stats)
        dir_count = len(dir_stats)
        avg_dir = total_dir_size // dir_count if dir_count else 0
        lines.append(
            f"| **Avg directory size** | {_format_size(avg_dir)} ({dir_count} dirs) |"
        )

    total_lines = sum(file_stats["extension_lines"].values())
    if total_lines:
        lines.append(f"| **Total lines (text)** | {total_lines:,} |")

    if git_stats.get("available"):
        lines.append(f"| **Total commits** | {git_stats.get('total_commits', 0)} |")
    lines.append("")

    # ── Repository Structure ──
    lines.append("---")
    lines.append("")
    lines.append("## \U0001f333 Repository Structure")
    lines.append("")
    lines.append("> [!TIP]")
    lines.append(
        "> Complete directory and file tree of the repository "
        "(excluding build artifacts and caches)."
    )
    lines.append("")
    lines.append("<details>")
    lines.append(
        "<summary><strong>Click to expand full repository tree</strong></summary>"
    )
    lines.append("")
    lines.append("```")
    lines.append(stats.get("repo_tree", "(tree unavailable)"))
    lines.append("```")
    lines.append("")
    lines.append("</details>")
    lines.append("")

    # ── File Types ──
    lines.append("---")
    lines.append("")
    lines.append("## \U0001f4c1 File Types")
    lines.append("")
    lines.append("> Most common file extensions in the repository.")
    lines.append("")
    ext_counts = file_stats["extension_counts"]
    if ext_counts:
        lines.append("| Extension | Files | Lines |")
        lines.append("|-----------|------:|------:|")
        lines_by_ext = file_stats["extension_lines"]
        for ext, count in list(ext_counts.items())[:15]:
            line_count = lines_by_ext.get(ext)
            line_str = f"{line_count:,}" if line_count else "\u2014"
            lines.append(f"| `{ext}` | {count} | {line_str} |")
        lines.append("")

    # ── Languages ──
    languages = file_stats.get("languages", [])
    if languages:
        lines.append("---")
        lines.append("")
        lines.append("## \U0001f5e3\ufe0f Languages")
        lines.append("")
        lines.append(
            "> Language breakdown by file count (percentage of recognized files)."
        )
        lines.append("")
        lines.append("| Language | Files | Lines | % |")
        lines.append("|----------|------:|------:|---:|")
        for lang in languages:
            pct_str = f"{lang['percentage']:.1f}%"
            lang_lines = f"{lang['lines']:,}" if lang["lines"] else "\u2014"
            lines.append(
                f"| **{lang['language']}** | {lang['files']}"
                f" | {lang_lines} | {pct_str} |"
            )
        lines.append("")

        # Language bar chart using diff code block for color
        lines.append("```diff")
        for lang in languages[:10]:
            bar_len = max(1, int(lang["percentage"] / 2))
            bar = "\u2588" * bar_len
            lines.append(f"+ {lang['language']:<20s} {bar} {lang['percentage']:.1f}%")
        lines.append("```")
        lines.append("")

    # ── Code & Script Activity ──
    lines.append("---")
    lines.append("")
    lines.append("## \u26a1 Code & Script Activity")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(
        "> Commit frequency per file as a proxy for how actively code "
        "and scripts are used/developed."
    )
    lines.append(
        "> Files with more commits are being changed (and likely run) more frequently."
    )
    lines.append("")

    code_files = execution.get("code_files", [])
    script_files = execution.get("script_files", [])

    if code_files:
        lines.append("### Code Files (by commit activity)")
        lines.append("")
        lines.append("| File | Commits | Last Commit |")
        lines.append("|------|--------:|-------------|")
        for filepath, commits, last_commit in code_files[:20]:
            last_date = last_commit[:10] if last_commit else "\u2014"
            lines.append(f"| `{filepath}` | {commits} | {last_date} |")
        lines.append("")

    if script_files:
        lines.append("### Script Files (by commit activity)")
        lines.append("")
        lines.append("| Script | Commits | Last Commit |")
        lines.append("|--------|--------:|-------------|")
        for filepath, commits, last_commit in script_files[:20]:
            last_date = last_commit[:10] if last_commit else "\u2014"
            lines.append(f"| `{filepath}` | {commits} | {last_date} |")
        lines.append("")

    # ── Directory Sizes ──
    if dir_stats:
        lines.append("---")
        lines.append("")
        lines.append("## \U0001f4e6 Directory Sizes")
        lines.append("")
        lines.append(
            f"> All {len(dir_stats)} directories sorted by size (largest first)."
        )
        lines.append("")
        lines.append("<details>")
        lines.append(
            "<summary><strong>Click to expand directory sizes</strong></summary>"
        )
        lines.append("")
        lines.append("| Directory | Size | Files |")
        lines.append("|-----------|-----:|------:|")
        lines.extend(
            f"| `{d['name']}/` | {_format_size(d['size_bytes'])} | {d['file_count']} |"
            for d in dir_stats
        )
        lines.append("")
        lines.append("</details>")
        lines.append("")

    # ── Largest Files ──
    largest = file_stats["largest_files"]
    if largest:
        lines.append("---")
        lines.append("")
        lines.append("## \U0001f418 Largest Files")
        lines.append("")
        lines.append("> Individual files sorted by size (top 15).")
        lines.append("")
        lines.append("| File | Size |")
        lines.append("|------|-----:|")
        for path, size in largest:
            lines.append(f"| `{path}` | {_format_size(size)} |")
        lines.append("")

    # ── File Access Statistics ──
    lines.append("---")
    lines.append("")
    lines.append("## \U0001f550 File Access Statistics")
    lines.append("")
    lines.append("> [!WARNING]")
    lines.append("> File access times (`atime`) depend on OS/filesystem configuration.")
    lines.append(
        "> Many systems use `relatime` or `noatime` mount options "
        "which may not reflect actual access."
    )
    lines.append("")

    if file_access:
        sorted_access = sorted(
            file_access.items(),
            key=lambda x: x[1]["last_accessed_iso"],
            reverse=True,
        )

        lines.append("<details>")
        lines.append(
            "<summary><strong>Click to expand file access stats</strong></summary>"
        )
        lines.append("")
        lines.append("| File | Last Accessed |")
        lines.append("|------|---------------|")
        for filepath, access_info in sorted_access[:50]:
            lines.append(f"| `{filepath}` | {access_info['last_accessed']} |")
        if len(sorted_access) > 50:
            lines.append(f"| *... and {len(sorted_access) - 50} more files* | |")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    # ── Git History ──
    if git_stats.get("available"):
        lines.append("---")
        lines.append("")
        lines.append("## \U0001f4dc Git History")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| **Total commits** | {git_stats.get('total_commits', 0)} |")
        lines.append(f"| **Contributors** | {git_stats.get('author_count', 0)} |")
        lines.append(f"| **Branches** | {git_stats.get('branch_count', 0)} |")
        lines.append(f"| **Tags** | {git_stats.get('tag_count', 0)} |")
        if git_stats.get("current_branch"):
            lines.append(f"| **Current branch** | `{git_stats['current_branch']}` |")
        if git_stats.get("latest_tag"):
            lines.append(f"| **Latest tag** | `{git_stats['latest_tag']}` |")
        if git_stats.get("first_commit_date"):
            lines.append(
                f"| **First commit** | {git_stats['first_commit_date'][:10]} |"
            )
        if git_stats.get("last_commit_date"):
            lines.append(f"| **Last commit** | {git_stats['last_commit_date'][:10]} |")
        if git_stats.get("remote_url"):
            lines.append(f"| **Remote** | `{git_stats['remote_url']}` |")
        lines.append("")

    # ── Per-File Git Statistics ──
    if file_git:
        lines.append("---")
        lines.append("")
        lines.append("## \U0001f4dd Per-File Git Statistics")
        lines.append("")
        lines.append("> Commit count and last commit date for every tracked file.")
        lines.append("")

        sorted_files = sorted(
            file_git.items(),
            key=lambda x: x[1]["commits"],
            reverse=True,
        )

        lines.append("<details>")
        lines.append(
            "<summary><strong>Click to expand per-file git stats</strong></summary>"
        )
        lines.append("")
        lines.append("| File | Commits | Last Commit |")
        lines.append("|------|--------:|-------------|")
        for filepath, fstats in sorted_files:
            last_date = (
                fstats["last_commit"][:10] if fstats.get("last_commit") else "\u2014"
            )
            lines.append(f"| `{filepath}` | {fstats['commits']} | {last_date} |")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    # ── Contributors ──
    authors = git_stats.get("authors", []) if git_stats.get("available") else []
    if authors:
        total_count = git_stats.get("author_count", len(authors))
        shown = min(len(authors), 10)
        lines.append("---")
        lines.append("")
        lines.append("## \U0001f465 Contributors")
        lines.append("")
        lines.append(f"> Top {shown} of {total_count} contributors, ranked by commits.")
        lines.append("")
        lines.append("| Contributor | Commits |")
        lines.append("|-------------|--------:|")
        lines.extend(f"| **{a['name']}** | {a['commits']} |" for a in authors[:10])
        if total_count > 10:
            lines.append(f"| *... and {total_count - 10} more* | |")
        lines.append("")

    # ── Recommended Scripts ──
    lines.append("---")
    lines.append("")
    lines.append("## \U0001f527 Recommended Scripts")
    lines.append("")
    lines.append("> Scripts that expand on repository information and health checks.")
    lines.append(">")
    lines.append(
        "> **Source:** "
        "[simple-python-boilerplate]"
        "(https://github.com/JoJo275/simple-python-boilerplate) "
        "by [JoJo275](https://github.com/JoJo275) on GitHub"
    )
    lines.append(">")
    lines.append("> Scripts are located in the `scripts/` directory.")
    lines.append(">")
    lines.append(
        "> *These scripts may already exist in this repository if it was "
        "forked from or based on the source.*"
    )
    lines.append(
        "> *If not, visit the "
        "[source repo](https://github.com/JoJo275/simple-python-boilerplate) "
        "by JoJo275 to obtain them.*"
    )
    lines.append("")
    lines.append("| Script | Description |")
    lines.append("|--------|-------------|")
    lines.append(
        "| `python scripts/git_doctor.py` "
        "| Git health dashboard \u2014 config, branch ops, integrity |"
    )
    lines.append(
        "| `python scripts/env_inspect.py` | Environment, packages, PATH inspection |"
    )
    lines.append(
        "| `python scripts/check_python_support.py` "
        "| Python version consistency across configs |"
    )
    lines.append(
        "| `python scripts/repo_doctor.py` | Repository structure health checks |"
    )
    lines.append(
        "| `python scripts/dep_versions.py show` "
        "| Dependency versions and update status |"
    )
    lines.append(
        "| `python scripts/env_doctor.py` | Development environment diagnostics |"
    )
    lines.append(
        "| `python scripts/doctor.py` | Unified health check (runs all doctors) |"
    )
    lines.append(
        "| `python scripts/workflow_versions.py` "
        "| GitHub Actions SHA-pinned version status |"
    )
    lines.append("")

    # ── Footer ──
    lines.append("---")
    lines.append("")
    lines.append(
        f"<sub>Generated by <strong>repo_sauron.py</strong> "
        f"v{SCRIPT_VERSION} \u2014 the all-seeing eye &bull; {now}</sub>"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="repo-sauron",
        description=(
            "Repository statistics dashboard \u2014 generates a Markdown report."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="repo-sauron-report.md",
        help="Output file path (default: repo-sauron-report.md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON instead of Markdown",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output; exit code only",
    )
    args = parser.parse_args()

    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)

    c = Colors()
    start = time.monotonic()

    with Spinner("Scanning repository", color="magenta") as spin:
        stats = gather_stats(spinner=spin)

    elapsed = time.monotonic() - start

    if args.json_output:
        json_stats = {k: v for k, v in stats.items() if k != "repo_tree"}
        json_stats["repo_tree_lines"] = stats.get("repo_tree", "").count("\n") + 1
        print(json.dumps(json_stats, indent=2))
        if not args.quiet:
            print(
                f"\n{c.dim(f'Completed in {elapsed:.1f}s')}",
                file=sys.stderr,
            )
    else:
        markdown = generate_markdown(stats)
        output_path = Path(args.output)
        output_path.write_text(markdown, encoding="utf-8")

        if not args.quiet:
            print()
            checkmark = "\u2713"
            print(f"  {c.green(checkmark)} {c.bold('Report generated successfully')}")
            print(f"  {c.dim('File:')} {c.cyan(str(output_path.resolve()))}")
            elapsed_str = f"Completed in {elapsed:.1f}s"
            print(f"  {c.dim(elapsed_str)}")
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
