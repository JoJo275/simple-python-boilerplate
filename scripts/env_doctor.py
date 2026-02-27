#!/usr/bin/env python3
"""Quick environment health check for daily development.

Verifies that the development environment is correctly set up:
Python version, virtual environment, editable install, Hatch,
Task, pre-commit hooks, and key tool availability.

Lighter than repo_doctor.py — focuses on environment readiness
rather than repository structure.

Note:
    The ``cz`` tool check requires the ``commitizen`` package to be
    installed (it provides the ``cz`` CLI).  If you see ``cz not found
    in PATH``, install it via ``hatch shell`` (which pulls in the dev
    extras) or ``pipx install commitizen``.

Flags::

    --strict     Treat optional tool warnings as failures
    --no-color   Disable colored output
    --json       Output results as JSON (for CI integration)
    --version    Print version and exit

Usage::

    python scripts/env_doctor.py
    python scripts/env_doctor.py --strict
    python scripts/env_doctor.py --json
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import shutil
import struct
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import TextIO

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.0.0"

ROOT = Path(__file__).resolve().parent.parent
MIN_PYTHON = (3, 11)

# Tools expected in the dev environment
EXPECTED_TOOLS = ["ruff", "mypy", "pytest", "bandit", "pre-commit", "cz", "deptry"]

# Optional tools — reported but don't fail unless --strict
OPTIONAL_TOOLS = ["actionlint"]

# Pre-commit hook files to check
HOOK_FILES = {
    "pre-commit": ROOT / ".git" / "hooks" / "pre-commit",
    "commit-msg": ROOT / ".git" / "hooks" / "commit-msg",
    "pre-push": ROOT / ".git" / "hooks" / "pre-push",
}


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------


def check_python_version() -> tuple[bool, str]:
    """Verify Python version meets minimum requirement.

    Returns:
        Tuple of (passed, message).
    """
    current = sys.version_info[:2]
    ok = current >= MIN_PYTHON
    version_str = f"{current[0]}.{current[1]}"
    min_str = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    if ok:
        return True, f"Python {version_str} (>= {min_str})"
    return False, f"Python {version_str} — requires >= {min_str}"


def check_architecture() -> tuple[bool, str]:
    """Report Python architecture (32-bit vs 64-bit).

    Returns:
        Tuple of (passed, message).
    """
    bits = struct.calcsize("P") * 8
    return True, f"{bits}-bit Python"


def check_venv_active() -> tuple[bool, str]:
    """Check if a virtual environment is active.

    Returns:
        Tuple of (passed, message).
    """
    venv = os.environ.get("VIRTUAL_ENV", "")
    if venv:
        return True, f"Virtual env active: {Path(venv).name}"
    return False, "No virtual environment active"


def check_editable_install() -> tuple[bool, str]:
    """Check if the project is installed in editable mode.

    Returns:
        Tuple of (passed, message).
    """
    try:
        version = importlib.metadata.version("simple-python-boilerplate")
        return True, f"Editable install OK (v{version})"
    except importlib.metadata.PackageNotFoundError:
        return (
            False,
            "Package not installed — run: hatch shell (or pip install -e '.[dev]')",
        )


def check_tool_available(tool: str) -> tuple[bool, str]:
    """Check if a development tool is available.

    Args:
        tool: Name of the tool/command to check.

    Returns:
        Tuple of (passed, message).
    """
    if shutil.which(tool):
        return True, f"{tool} available"
    return False, f"{tool} not found in PATH"


def check_hatch() -> tuple[bool, str]:
    """Check if Hatch is installed and accessible.

    Returns:
        Tuple of (passed, message).
    """
    hatch = shutil.which("hatch")
    if not hatch:
        return False, "Hatch not found — install: pipx install hatch"
    try:
        result = subprocess.run(  # nosec B603
            [hatch, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        version = result.stdout.strip()
        return True, f"Hatch {version}"
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False, "Hatch found but failed to run"


def check_task() -> tuple[bool, str]:
    """Check if Task runner is installed.

    Returns:
        Tuple of (passed, message).
    """
    task = shutil.which("task")
    if not task:
        return False, "Task not found (optional) — install: https://taskfile.dev"
    return True, "Task available"


def check_pre_commit_hooks() -> tuple[bool, str]:
    """Check if all pre-commit hook stages are installed.

    Returns:
        Tuple of (passed, message).
    """
    installed: list[str] = []
    missing: list[str] = []

    for name, path in HOOK_FILES.items():
        if path.exists():
            installed.append(name)
        else:
            missing.append(name)

    if not missing:
        return True, f"All hooks installed ({', '.join(installed)})"
    if not installed:
        return False, "No hooks installed — run: task pre-commit:install"
    return False, f"Missing hooks: {', '.join(missing)} — run: task pre-commit:install"


def check_git_repo() -> tuple[bool, str]:
    """Check if we're inside a git repository.

    Returns:
        Tuple of (passed, message).
    """
    git_dir = ROOT / ".git"
    if git_dir.is_dir():
        return True, "Git repository detected"
    return False, "Not a git repository"


def check_git_user_config() -> tuple[bool, str]:
    """Check if git user.name and user.email are configured.

    Returns:
        Tuple of (passed, message).
    """
    git = shutil.which("git")
    if not git:
        return False, "git not found in PATH"

    missing: list[str] = []
    for key in ("user.name", "user.email"):
        try:
            result = subprocess.run(  # nosec B603
                [git, "config", key],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if not result.stdout.strip():
                missing.append(key)
        except (subprocess.TimeoutExpired, OSError):
            missing.append(key)

    if not missing:
        return True, "Git user.name and user.email configured"
    return (
        False,
        f"Git config missing: {', '.join(missing)} — run: git config --global {missing[0]} <value>",
    )


def check_pyproject_toml() -> tuple[bool, str]:
    """Check if pyproject.toml exists in the project root.

    Returns:
        Tuple of (passed, message).
    """
    pyproject = ROOT / "pyproject.toml"
    if pyproject.is_file():
        return True, "pyproject.toml found"
    return False, "pyproject.toml missing — project configuration is incomplete"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

CHECKS = [
    ("Python version", check_python_version),
    ("Architecture", check_architecture),
    ("Git repository", check_git_repo),
    ("Git user config", check_git_user_config),
    ("pyproject.toml", check_pyproject_toml),
    ("Virtual environment", check_venv_active),
    ("Editable install", check_editable_install),
    ("Hatch", check_hatch),
    ("Task runner", check_task),
    ("Pre-commit hooks", check_pre_commit_hooks),
]


# ---------------------------------------------------------------------------
# Color output helpers
# ---------------------------------------------------------------------------


def _supports_color(stream: TextIO) -> bool:
    """Detect whether the output stream supports ANSI color.

    Returns:
        True if color is likely supported.
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return hasattr(stream, "isatty") and stream.isatty()


def _colorize(text: str, code: str, *, use_color: bool) -> str:
    """Wrap text in ANSI escape codes if color is enabled.

    Args:
        text: The text to colorize.
        code: ANSI color code (e.g. '32' for green).
        use_color: Whether to apply color.

    Returns:
        Colorized string, or plain text if color is disabled.
    """
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def _icon(status: str, *, use_color: bool) -> str:
    """Return a colored status icon.

    Args:
        status: One of 'PASS', 'FAIL', 'WARN'.
        use_color: Whether to apply color.

    Returns:
        Formatted status string.
    """
    colors = {"PASS": "32", "FAIL": "31", "WARN": "33"}  # nosec
    return _colorize(status, colors.get(status, "0"), use_color=use_color)


def _collect_results(
    strict: bool = False,
) -> tuple[list[dict[str, str]], int]:
    """Run all checks and collect structured results.

    Args:
        strict: If True, treat optional items as required.

    Returns:
        Tuple of (list of result dicts, failure count).
    """
    optional_checks = {"Task runner", "Architecture"}
    results: list[dict[str, str]] = []
    failures = 0

    # Core checks
    for name, check_fn in CHECKS:
        passed, msg = check_fn()
        status = "PASS" if passed else "FAIL"
        if not passed and name in optional_checks and not strict:
            status = "WARN"
        else:
            if not passed:
                failures += 1
        results.append(
            {"name": name, "status": status, "message": msg, "group": "core"}
        )

    # Required dev tools
    for tool in EXPECTED_TOOLS:
        passed, msg = check_tool_available(tool)
        status = "PASS" if passed else "FAIL"
        if not passed:
            failures += 1
        results.append(
            {"name": tool, "status": status, "message": msg, "group": "tools"}
        )

    # Optional tools
    for tool in OPTIONAL_TOOLS:
        passed, msg = check_tool_available(tool)
        status = "PASS" if passed else "WARN"
        if not passed and strict:
            status = "FAIL"
            failures += 1
        results.append(
            {
                "name": tool,
                "status": status,
                "message": msg,
                "group": "optional",
            }
        )

    return results, failures


def run_checks(
    strict: bool = False,
    *,
    color: bool | None = None,
    output_json: bool = False,
) -> int:
    """Run all environment checks and print results.

    Args:
        strict: If True, treat warnings (Task not found) as failures.
        color: Force color on/off. None = auto-detect.
        output_json: If True, output results as JSON instead of text.

    Returns:
        Exit code: 0 if all passed, 1 if any failed.
    """
    results, failures = _collect_results(strict)

    if output_json:
        total = len(results)
        passed_count = total - failures
        payload = {
            "version": SCRIPT_VERSION,
            "total": total,
            "passed": passed_count,
            "failed": failures,
            "checks": results,
        }
        print(json.dumps(payload, indent=2))
        return 1 if failures else 0

    use_color = color if color is not None else _supports_color(sys.stdout)

    print(_colorize("Environment Health Check", "1", use_color=use_color))
    print("=" * 50)

    # Core checks
    for r in results:
        if r["group"] == "core":
            print(
                f"  [{_icon(r['status'], use_color=use_color)}]"
                f" {r['name']}: {r['message']}"
            )

    # Dev tool checks
    print()
    print(_colorize("Development Tools", "1", use_color=use_color))
    print("-" * 50)
    for r in results:
        if r["group"] in ("tools", "optional"):
            print(f"  [{_icon(r['status'], use_color=use_color)}] {r['message']}")

    # Summary
    print()
    total = len(results)
    passed_count = total - failures
    if failures == 0:
        print(_colorize(f"All {total} checks passed!", "32", use_color=use_color))
    else:
        print(
            _colorize(
                f"{passed_count}/{total} checks passed, {failures} failed",
                "31",
                use_color=use_color,
            )
        )

    return 1 if failures else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point for env_doctor.

    Returns:
        Exit code from run_checks().
    """
    parser = argparse.ArgumentParser(
        description="Quick environment health check for development.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat optional tool warnings as failures",
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
    color = False if args.no_color else None
    return run_checks(strict=args.strict, color=color, output_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
