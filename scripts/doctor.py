#!/usr/bin/env python3
"""Print a diagnostics bundle for bug reports and environment debugging.

Collects: Python version, OS, Hatch version, active environment, key tool
versions, important paths, git status, and configuration status.

Usage::

    python scripts/doctor.py
    python scripts/doctor.py --version
    python scripts/doctor.py --output var/doctor.txt
    python scripts/doctor.py --markdown   # For GitHub issues
    python scripts/doctor.py --json       # Machine-readable output
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess  # nosec B404
import sys
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.1.0"

ROOT = Path(__file__).resolve().parent.parent


def get_version(cmd: list[str]) -> str:
    """Run a command and extract its version output."""
    exe = shutil.which(cmd[0])
    if not exe:
        return "not found"
    try:
        result = subprocess.run(  # nosec B603
            [exe, *cmd[1:]],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (
            result.stdout.strip().split("\n")[0] or result.stderr.strip().split("\n")[0]
        )
    except (subprocess.TimeoutExpired, OSError):
        return "error"


def get_package_version(package: str) -> str:
    """Get installed package version."""
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def check_path_exists(path: Path) -> str:
    """Check if a path exists and its type."""
    if not path.exists():
        return "missing"
    if path.is_dir():
        return "directory"
    return "file"


def _git_info() -> dict[str, str]:
    """Collect git repository information (branch, commit, dirty state)."""
    result: dict[str, str] = {}
    git_exe = shutil.which("git")
    if not git_exe:
        return {"status": "git not found"}

    def _run_git(*args: str) -> str:
        try:
            proc = subprocess.run(  # nosec B603
                [git_exe, *args],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=ROOT,
            )
            return proc.stdout.strip() if proc.returncode == 0 else ""
        except (subprocess.TimeoutExpired, OSError):
            return ""

    result["branch"] = _run_git("rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    result["commit"] = _run_git("rev-parse", "--short", "HEAD") or "unknown"
    result["commit_date"] = _run_git("log", "-1", "--format=%ci") or "unknown"

    # Dirty = uncommitted changes exist
    dirty_check = _run_git("status", "--porcelain")
    result["dirty"] = "yes" if dirty_check else "no"

    return result


def collect_diagnostics() -> dict[str, str | dict[str, str]]:
    """Collect all diagnostic information."""
    info: dict[str, str | dict[str, str]] = {}

    # Timestamp (UTC for unambiguous reports)
    info["timestamp"] = datetime.now(tz=UTC).isoformat()

    # System
    info["system"] = {
        "os": f"{platform.system()} {platform.release()}",
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version.split()[0],
        "python_path": sys.executable,
        "python_bits": "64-bit" if sys.maxsize > 2**32 else "32-bit",
    }

    # Virtual Environment
    venv = os.environ.get("VIRTUAL_ENV", "")
    info["environment"] = {
        "virtual_env": Path(venv).name if venv else "none",
        "virtual_env_path": venv or "N/A",
        "hatch_env": os.environ.get("HATCH_ENV", "none"),
    }

    # Tool versions
    info["tools"] = {
        "hatch": get_version(["hatch", "--version"]),
        "pip": get_version([sys.executable, "-m", "pip", "--version"]),
        "task": get_version(["task", "--version"]),
        "ruff": get_version(["ruff", "--version"]),
        "mypy": get_version(["mypy", "--version"]),
        "pytest": get_version(["pytest", "--version"]),
        "pre-commit": get_version(["pre-commit", "--version"]),
        "git": get_version(["git", "--version"]),
    }

    # Git repository
    info["git"] = _git_info()

    # Package status
    info["package"] = {
        "simple-python-boilerplate": get_package_version("simple-python-boilerplate"),
    }

    # Key paths
    info["paths"] = {
        "root": str(ROOT),
        "pyproject.toml": check_path_exists(ROOT / "pyproject.toml"),
        "src/": check_path_exists(ROOT / "src"),
        ".git/": check_path_exists(ROOT / ".git"),
        ".git/hooks/pre-commit": check_path_exists(
            ROOT / ".git" / "hooks" / "pre-commit"
        ),
        ".git/hooks/commit-msg": check_path_exists(
            ROOT / ".git" / "hooks" / "commit-msg"
        ),
        ".git/hooks/pre-push": check_path_exists(ROOT / ".git" / "hooks" / "pre-push"),
    }

    return info


def format_plain(info: dict[str, str | dict[str, str]]) -> str:
    """Format diagnostics as plain text."""
    lines = ["=" * 60, "DIAGNOSTICS REPORT", "=" * 60, ""]

    for section, data in info.items():
        lines.append(f"[{section.upper()}]")
        if isinstance(data, dict):
            for key, value in data.items():
                lines.append(f"  {key}: {value}")
        else:
            lines.append(f"  {data}")
        lines.append("")

    return "\n".join(lines)


def format_markdown(info: dict[str, str | dict[str, str]]) -> str:
    """Format diagnostics as markdown for GitHub issues."""
    lines = [
        "<details>",
        "<summary>Environment diagnostics</summary>",
        "",
        "```",
    ]

    for section, data in info.items():
        lines.append(f"[{section}]")
        if isinstance(data, dict):
            for key, value in data.items():
                lines.append(f"  {key}: {value}")
        else:
            lines.append(f"  {data}")

    lines.extend(["```", "</details>"])
    return "\n".join(lines)


def format_json(info: dict[str, str | dict[str, str]]) -> str:
    """Format diagnostics as JSON for scripting and automation."""
    return json.dumps(info, indent=2)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="doctor",
        description="Print a diagnostics bundle for bug reports.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Write output to file (e.g., var/doctor.txt)",
    )

    fmt_group = parser.add_mutually_exclusive_group()
    fmt_group.add_argument(
        "--markdown",
        action="store_true",
        help="Output as markdown (for GitHub issues)",
    )
    fmt_group.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (machine-readable)",
    )
    args = parser.parse_args()

    info = collect_diagnostics()

    if args.json:
        output = format_json(info)
    elif args.markdown:
        output = format_markdown(info)
    else:
        output = format_plain(info)

    print(output)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"\nSaved to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
