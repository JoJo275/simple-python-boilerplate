#!/usr/bin/env python3
"""Repository statistics dashboard — the all-seeing eye for any git repo.

Compiles and displays comprehensive statistics about the current repository:
file counts by type, lines of code, language breakdown, directory sizes
(all directories, sorted largest-first), git history stats, full
contributor list, average file/directory sizes, and more. Works on any
git repository, not just this template.

Named after Sauron's all-seeing eye from The Lord of the Rings.

Flags::

    --json              Output as JSON (for CI integration)
    --section SECTION   Only show a specific section
                        (overview, files, languages, directories, largest,
                         git, contributors)
    -q, --quiet         Suppress output; exit code only
    --no-color          Disable colored output
    --version           Print version and exit

Usage::

    python scripts/repo_sauron.py
    python scripts/repo_sauron.py --json
    python scripts/repo_sauron.py --section languages
    python scripts/repo_sauron.py --section contributors
    python scripts/repo_sauron.py --no-color
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess  # nosec B404
import time
from collections import Counter
from pathlib import Path

# -- Local script modules (not third-party; live in scripts/) ----------------
from _colors import Colors
from _imports import find_repo_root
from _progress import Spinner
from _ui import UI

log = logging.getLogger(__name__)

SCRIPT_VERSION = "1.1.0"
THEME = "magenta"

ROOT = find_repo_root()

# Directories to skip when counting files (common build/cache artifacts)
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

# Map file extensions to language names for the language breakdown
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


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _run_git(args: list[str]) -> tuple[int, str]:
    """Run a git command and return (returncode, stdout)."""
    if _GIT_CMD is None:
        return 1, ""
    try:
        result = subprocess.run(  # nosec B603
            [_GIT_CMD, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
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

    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Skip excluded directories in-place
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

            # Map to language
            lang = _EXT_TO_LANGUAGE.get(ext)
            # Detect Containerfile/Dockerfile by name
            if lang is None and fname.lower() in ("containerfile", "dockerfile"):
                lang = "Dockerfile"
            if lang:
                language_files[lang] += 1

            # Count lines for text files
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

    # Build language percentage breakdown
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
    }


def _collect_git_stats() -> dict:
    """Collect git repository statistics."""
    stats: dict = {"available": False}

    code, out = _run_git(["rev-parse", "--is-inside-work-tree"])
    if code != 0 or out != "true":
        return stats

    stats["available"] = True

    # Total commits
    code, out = _run_git(["rev-list", "--count", "HEAD"])
    stats["total_commits"] = int(out) if code == 0 and out.isdigit() else 0

    # Authors
    code, out = _run_git(["shortlog", "-sn", "--no-merges", "HEAD"])
    if code == 0 and out:
        authors = []
        for line in out.splitlines():
            parts = line.strip().split("\t", 1)
            if len(parts) == 2:
                authors.append(
                    {"commits": int(parts[0].strip()), "name": parts[1].strip()}
                )
        stats["authors"] = authors[:10]
        stats["author_count"] = len(authors)
    else:
        stats["authors"] = []
        stats["author_count"] = 0

    # Branches
    code, out = _run_git(["branch", "--list"])
    if code == 0:
        branches = [b.strip().lstrip("* ") for b in out.splitlines() if b.strip()]
        stats["branch_count"] = len(branches)
    else:
        stats["branch_count"] = 0

    # Tags
    code, out = _run_git(["tag", "--list"])
    if code == 0:
        tags = [t.strip() for t in out.splitlines() if t.strip()]
        stats["tag_count"] = len(tags)
        stats["latest_tag"] = tags[-1] if tags else None
    else:
        stats["tag_count"] = 0
        stats["latest_tag"] = None

    # Current branch
    code, out = _run_git(["branch", "--show-current"])
    stats["current_branch"] = out if code == 0 else None

    # First and last commit dates
    code, out = _run_git(["log", "--reverse", "--format=%aI", "-1"])
    stats["first_commit_date"] = out if code == 0 and out else None

    code, out = _run_git(["log", "--format=%aI", "-1"])
    stats["last_commit_date"] = out if code == 0 and out else None

    # Remote URL
    code, out = _run_git(["remote", "get-url", "origin"])
    stats["remote_url"] = out if code == 0 and out else None

    return stats


def _collect_directory_sizes() -> list[tuple[str, int, int]]:
    """Get all directory sizes sorted largest-first (name, byte_size, file_count).

    Includes all directories in the repo (top-level and subdirectories),
    excluding hidden dirs and build artifacts. Sorted by size descending.
    """
    dirs: list[tuple[str, int, int]] = []

    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Skip hidden and build artifact dirs
        dirnames[:] = [
            d
            for d in dirnames
            if d not in SKIP_DIRS
            and not d.startswith(".")
            and not d.endswith(".egg-info")
        ]

        rel_path = Path(dirpath).relative_to(ROOT)
        if str(rel_path) == ".":
            continue  # Skip root itself

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


def _format_size(size_bytes: int) -> str:
    """Format byte size to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def gather_stats() -> dict:
    """Gather all repository statistics."""
    return {
        "files": _collect_file_stats(),
        "git": _collect_git_stats(),
        "directories": [
            {"name": n, "size_bytes": s, "file_count": c}
            for n, s, c in _collect_directory_sizes()
        ],
    }


def print_stats(
    stats: dict,
    *,
    no_color: bool = False,
    section: str | None = None,
) -> None:
    """Print the statistics dashboard."""
    c = Colors(enabled=not no_color)
    ui = UI(
        title="Repository Stats",
        version=SCRIPT_VERSION,
        theme=THEME,
        no_color=no_color,
    )
    ui.header()

    file_stats = stats["files"]
    git_stats = stats["git"]
    show_all = section is None

    # ── Overview ──
    if show_all or section == "overview":
        ui.section("Overview")
        ui.info_line("High-level repository metrics at a glance")
        ui.kv("Total files", str(file_stats["total_files"]))
        ui.kv(
            "Total directories",
            str(file_stats["total_dirs"]),
            hint="Includes all subdirectories (excludes .git, caches, build artifacts)",
        )
        ui.kv("Total size", _format_size(file_stats["total_size_bytes"]))
        avg_file = file_stats.get("avg_file_size_bytes", 0)
        if avg_file:
            ui.kv(
                "Avg file size",
                _format_size(avg_file),
                hint="Total size ÷ total files",
            )

        dir_stats = stats["directories"]
        if dir_stats:
            total_dir_size = sum(d["size_bytes"] for d in dir_stats)
            dir_count = len(dir_stats)
            avg_dir = total_dir_size // dir_count if dir_count else 0
            ui.kv(
                "Avg directory size",
                _format_size(avg_dir),
                hint=f"Across {dir_count} directories",
            )

        total_lines = sum(file_stats["extension_lines"].values())
        if total_lines:
            ui.kv("Total lines (text)", f"{total_lines:,}")

    # ── File types ──
    if show_all or section == "files":
        ui.section("File Types (top 15)")
        ui.info_line("Most common file extensions in the repository")
        ext_counts = file_stats["extension_counts"]
        if ext_counts:
            ui.table_header([("Extension", 14), ("Files", 8), ("Lines", 10)])
            lines_by_ext = file_stats["extension_lines"]
            for ext, count in list(ext_counts.items())[:15]:
                line_count = lines_by_ext.get(ext)
                line_str = f"{line_count:,}" if line_count else c.dim("-")
                ui.table_row([(ext, 14), (str(count), 8), (line_str, 10)])

    # ── Languages ──
    if show_all or section == "languages":
        languages = file_stats.get("languages", [])
        if languages:
            ui.section("Languages")
            ui.info_line(
                "Language breakdown by file count (percentage of recognized files)"
            )
            ui.table_header([("Language", 22), ("Files", 8), ("Lines", 10), ("%", 8)])
            for lang in languages:
                pct_str = f"{lang['percentage']:.1f}%"
                lines = f"{lang['lines']:,}" if lang["lines"] else c.dim("-")
                ui.table_row(
                    [
                        (lang["language"], 22),
                        (str(lang["files"]), 8),
                        (lines, 10),
                        (pct_str, 8),
                    ]
                )

    # ── Directory sizes ──
    if show_all or section == "directories":
        dir_stats = stats["directories"]
        if dir_stats:
            ui.section(f"Directory Sizes ({len(dir_stats)} directories, largest first)")
            ui.info_line(
                "All directories in repo sorted by size (descending). "
                "Includes subdirectories."
            )
            ui.table_header([("Directory", 35), ("Size", 12), ("Files", 8)])
            for d in dir_stats:
                ui.table_row(
                    [
                        (d["name"] + "/", 35),
                        (_format_size(d["size_bytes"]), 12),
                        (str(d["file_count"]), 8),
                    ]
                )

    # ── Largest files ──
    if show_all or section == "largest":
        largest = file_stats["largest_files"]
        if largest:
            ui.section("Largest Files (top 15)")
            ui.info_line("Individual files sorted by size")
            ui.table_header([("File", 50), ("Size", 12)])
            for path, size in largest:
                ui.table_row([(path, 50), (_format_size(size), 12)])

    # ── Git stats ──
    if show_all or section == "git":
        if git_stats["available"]:
            ui.section("Git History")
            ui.info_line("Repository commit history and branch information")
            ui.kv("Total commits", str(git_stats.get("total_commits", 0)))
            ui.kv(
                "Contributors",
                str(git_stats.get("author_count", 0)),
                hint="Unique commit authors (see Contributors section for details)",
            )
            ui.kv("Branches", str(git_stats.get("branch_count", 0)))
            ui.kv("Tags", str(git_stats.get("tag_count", 0)))
            if git_stats.get("current_branch"):
                ui.kv("Current branch", git_stats["current_branch"])
            if git_stats.get("latest_tag"):
                ui.kv("Latest tag", git_stats["latest_tag"])
            if git_stats.get("first_commit_date"):
                ui.kv(
                    "First commit",
                    git_stats["first_commit_date"][:10],
                    hint="Date of the earliest commit in the repository",
                )
            if git_stats.get("last_commit_date"):
                ui.kv(
                    "Last commit",
                    git_stats["last_commit_date"][:10],
                    hint="Date of the most recent commit",
                )
            if git_stats.get("remote_url"):
                ui.kv("Remote", git_stats["remote_url"])
        else:
            ui.section("Git")
            ui.status_line("warn", "Not a git repository", "yellow")

    # ── Contributors ──
    if show_all or section == "contributors":
        authors = git_stats.get("authors", []) if git_stats.get("available") else []
        if authors:
            total_count = git_stats.get("author_count", len(authors))
            shown = min(len(authors), 10)
            ui.section(f"Contributors (top {shown} of {total_count})")
            ui.info_line("Ranked by number of commits, most to least")
            ui.table_header([("Contributor", 30), ("Commits", 10)])
            for a in authors[:10]:
                ui.table_row([(a["name"], 30), (str(a["commits"]), 10)])
            if total_count > 10:
                ui.info_line(f"  ... and {total_count - 10} more contributor(s)")

    # ── Related Scripts ──
    if show_all:
        ui.section("Related Scripts")
        ui.info_line(
            "Other scripts in this repo that expand on repository information."
        )
        ui.info_line("Source: simple-python-boilerplate template (scripts/ directory)")
        ui.blank()
        ui.info_line(
            f"  {c.cyan('python scripts/git_doctor.py')}"
            "              — Git health dashboard, config, branch ops"
        )
        ui.info_line(
            f"  {c.cyan('python scripts/env_inspect.py')}"
            "             — Environment, packages, PATH inspection"
        )
        ui.info_line(
            f"  {c.cyan('python scripts/check_python_support.py')}"
            "    — Python version consistency across configs"
        )
        ui.info_line(
            f"  {c.cyan('python scripts/repo_doctor.py')}"
            "             — Repository structure health checks"
        )
        ui.info_line(
            f"  {c.cyan('python scripts/dep_versions.py show')}"
            "       — Dependency versions and update status"
        )

    ui.blank()
    ui.separator(double=True)
    print()


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="repo-sauron",
        description="Repository statistics dashboard — the all-seeing eye.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON",
    )
    parser.add_argument(
        "--section",
        choices=[
            "overview",
            "files",
            "languages",
            "directories",
            "largest",
            "git",
            "contributors",
        ],
        help="Only show a specific section",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output; exit code only",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    args = parser.parse_args()

    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)

    start = time.monotonic()

    with Spinner("Scanning repository", color="magenta") as spin:
        spin.update("Collecting file stats")
        stats = gather_stats()

    elapsed = time.monotonic() - start

    if args.json_output:
        print(json.dumps(stats, indent=2))
    elif not args.quiet:
        print_stats(stats, no_color=args.no_color, section=args.section)
        c = Colors(enabled=not args.no_color)
        print(f"  {c.dim(f'Completed in {elapsed:.1f}s')}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
