#!/usr/bin/env python3
"""Quick environment health check for daily development.

Verifies that the development environment is correctly set up:
Python version, virtual environment, editable install, Hatch,
Task, pre-commit hooks, and key tool availability.

Lighter than repo_doctor.py — focuses on environment readiness
rather than repository structure.

Usage::

    python scripts/env_doctor.py
    python scripts/env_doctor.py --strict
"""

from __future__ import annotations

import argparse
import importlib.metadata
import os
import shutil
import struct
import subprocess  # nosec B404
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
MIN_PYTHON = (3, 11)

# Tools expected in the dev environment
EXPECTED_TOOLS = ["ruff", "mypy", "pytest", "bandit", "pre-commit"]

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
        return False, 'Package not installed — run: pip install -e ".[dev]"'


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
        result = subprocess.run(  # nosec B603 — resolved path from shutil.which, no user input
            [hatch, "version"],
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
    installed = []
    missing = []

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


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

CHECKS = [
    ("Python version", check_python_version),
    ("Architecture", check_architecture),
    ("Git repository", check_git_repo),
    ("Virtual environment", check_venv_active),
    ("Editable install", check_editable_install),
    ("Hatch", check_hatch),
    ("Task runner", check_task),
    ("Pre-commit hooks", check_pre_commit_hooks),
]


def run_checks(strict: bool = False) -> int:
    """Run all environment checks and print results.

    Args:
        strict: If True, treat warnings (Task not found) as failures.

    Returns:
        Exit code: 0 if all passed, 1 if any failed.
    """
    # Optional tools that don't fail unless --strict
    optional = {"Task runner", "Architecture"}

    failures = 0
    print("Environment Health Check")
    print("=" * 50)

    # Core checks
    for name, check_fn in CHECKS:
        passed, msg = check_fn()
        icon = "PASS" if passed else "FAIL"
        if not passed and name in optional and not strict:
            icon = "WARN"
        else:
            if not passed:
                failures += 1
        print(f"  [{icon}] {name}: {msg}")

    # Dev tool checks
    print()
    print("Development Tools")
    print("-" * 50)
    for tool in EXPECTED_TOOLS:
        passed, msg = check_tool_available(tool)
        icon = "PASS" if passed else "FAIL"
        if not passed:
            failures += 1
        print(f"  [{icon}] {msg}")

    # Summary
    print()
    total = len(CHECKS) + len(EXPECTED_TOOLS)
    passed_count = total - failures
    if failures == 0:
        print(f"All {total} checks passed!")
    else:
        print(f"{passed_count}/{total} checks passed, {failures} failed")

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
        "--strict",
        action="store_true",
        help="Treat optional tool warnings as failures",
    )
    args = parser.parse_args()
    return run_checks(strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
