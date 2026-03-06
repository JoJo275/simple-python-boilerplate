"""Shared utilities for doctor-family scripts.

Provides low-level helpers used by ``doctor.py``, ``env_doctor.py``,
and potentially other diagnostic scripts.  Centralises command
execution, package introspection, path checks, and pre-commit hook
detection so each script doesn't re-implement the same patterns.

Usage::

    from _doctor_common import get_version, get_package_version

    version = get_version(["ruff", "--version"])
    pkg = get_package_version("simple-python-boilerplate")

.. note::
    This is a shared internal module (prefixed with ``_``).  It is excluded
    from the command reference generator and is not intended as a standalone
    CLI.  See ADR 031 for script conventions.
"""

from __future__ import annotations

import importlib.metadata
import shutil
import subprocess  # nosec B404
from pathlib import Path

__all__ = [
    "HOOK_STAGES",
    "check_hook_installed",
    "check_path_exists",
    "get_package_version",
    "get_version",
]

SCRIPT_VERSION = "1.0.0"

# Pre-commit hook stages that this project expects installed.
HOOK_STAGES = ("pre-commit", "commit-msg", "pre-push")


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------


def get_version(cmd: list[str], *, timeout: int = 10) -> str:
    """Run a command and extract its first line of output.

    Handles both PATH-based lookups (``["ruff", "--version"]``) and
    absolute-path commands (``[sys.executable, "-m", "pip", ...]``).

    Args:
        cmd: Command and arguments to run.
        timeout: Maximum seconds to wait for the command.

    Returns:
        First line of stdout (or stderr), ``"not found"`` if the
        executable doesn't exist, or ``"error"`` on failure/timeout.
    """
    first = cmd[0]
    # If it's already an absolute path that exists, use it directly;
    # otherwise look it up on PATH via shutil.which.
    if Path(first).is_absolute() and Path(first).exists():
        exe: str = first
    else:
        found = shutil.which(first)
        if not found:
            return "not found"
        exe = found
    try:
        result = subprocess.run(  # nosec B603
            [exe, *cmd[1:]],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return (
            result.stdout.strip().split("\n")[0] or result.stderr.strip().split("\n")[0]
        )
    except (subprocess.TimeoutExpired, OSError):
        return "error"


# ---------------------------------------------------------------------------
# Package introspection
# ---------------------------------------------------------------------------


def get_package_version(package: str) -> str:
    """Get installed package version.

    Args:
        package: Distribution name (e.g. ``"simple-python-boilerplate"``).

    Returns:
        Version string, or ``"not installed"`` if the package isn't found.
    """
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def check_path_exists(path: Path) -> str:
    """Check if a path exists and report its type.

    Args:
        path: Filesystem path to check.

    Returns:
        ``"directory"``, ``"file"``, or ``"missing"``.
    """
    if not path.exists():
        return "missing"
    if path.is_dir():
        return "directory"
    return "file"


# ---------------------------------------------------------------------------
# Pre-commit hook detection
# ---------------------------------------------------------------------------


def check_hook_installed(hook_path: Path) -> str:
    """Check if a git hook file is a real pre-commit hook (not a sample).

    Reads the hook file content to distinguish between a pre-commit
    managed hook, a Git sample, a custom script, or a missing file.

    Args:
        hook_path: Path to the hook file
            (e.g. ``root / ".git" / "hooks" / "pre-commit"``).

    Returns:
        ``"installed"`` if managed by pre-commit, ``"sample"`` if it's
        a Git sample hook, ``"custom"`` for other scripts, or
        ``"missing"`` if absent.
    """
    if not hook_path.is_file():
        return "missing"
    try:
        content = hook_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "missing"
    if "pre-commit" in content:
        return "installed"
    if "This sample" in content or ".sample" in hook_path.name:
        return "sample"
    return "custom"
