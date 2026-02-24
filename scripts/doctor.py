#!/usr/bin/env python3
"""Print a diagnostics bundle for bug reports and environment debugging.

Collects: Python version, OS, Hatch version, active environment, key tool
versions, important paths, and configuration status.

Usage::

    python scripts/doctor.py
    python scripts/doctor.py --output var/doctor.txt
    python scripts/doctor.py --markdown   # For GitHub issues
"""

from __future__ import annotations

import argparse
import importlib.metadata
import os
import platform
import shutil
import subprocess  # nosec B404
import sys
from datetime import datetime
from pathlib import Path

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


def collect_diagnostics() -> dict[str, str | dict[str, str]]:
    """Collect all diagnostic information."""
    info: dict[str, str | dict[str, str]] = {}

    # Timestamp
    info["timestamp"] = datetime.now().isoformat()

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
        "hatch": get_version(["hatch", "version"]),
        "task": get_version(["task", "--version"]),
        "ruff": get_version(["ruff", "--version"]),
        "mypy": get_version(["mypy", "--version"]),
        "pytest": get_version(["pytest", "--version"]),
        "pre-commit": get_version(["pre-commit", "--version"]),
        "git": get_version(["git", "--version"]),
    }

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


def format_plain(info: dict) -> str:
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


def format_markdown(info: dict) -> str:
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


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="doctor",
        description="Print a diagnostics bundle for bug reports.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Write output to file (e.g., var/doctor.txt)",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Output as markdown (for GitHub issues)",
    )
    args = parser.parse_args()

    info = collect_diagnostics()
    output = format_markdown(info) if args.markdown else format_plain(info)
    print(output)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"\nSaved to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
