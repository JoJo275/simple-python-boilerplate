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
import time
from pathlib import Path

from _colors import Colors
from _colors import status_icon as _icon
from _colors import supports_color as _supports_color
from _doctor_common import check_hook_installed, get_package_version, get_version
from _imports import find_repo_root

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.2.0"

ROOT = find_repo_root()
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
    """Check if the project is installed (ideally in editable mode).

    Uses PEP 610 ``direct_url.json`` (via ``importlib.metadata``) to
    detect editable installs.  Falls back to checking whether the
    package's ``__file__`` points into the repo's ``src/`` tree.

    Returns:
        Tuple of (passed, message).
    """
    pkg = "simple-python-boilerplate"
    version = get_package_version(pkg)
    if version == "not installed":
        return (
            False,
            "Package not installed — run: hatch shell (or pip install -e '.[dev]')",
        )

    # --- PEP 610: check direct_url.json for editable marker -----------
    try:
        import json as _json

        dist = importlib.metadata.distribution(pkg)
        du_text = dist.read_text("direct_url.json")
        if du_text:
            du = _json.loads(du_text)
            if du.get("dir_info", {}).get("editable", False):
                return True, f"Editable install OK (v{version})"
            return True, f"Installed v{version} (non-editable direct install)"
    except (importlib.metadata.PackageNotFoundError, KeyError, ValueError):
        pass

    # --- Fallback: check if imported module lives in src/ tree ---------
    try:
        import simple_python_boilerplate as _spb

        mod_path = Path(_spb.__file__).resolve()
        src_dir = ROOT / "src"
        if src_dir.exists() and src_dir.resolve() in mod_path.parents:
            return True, f"Editable install OK (v{version})"
    except (ImportError, AttributeError, TypeError):
        pass

    return True, f"Installed v{version} (may not be editable)"


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
    version = get_version(["hatch", "--version"])
    if version == "not found":
        return False, "Hatch not found — install: pipx install hatch"
    if version == "error":
        return False, "Hatch found but failed to run"
    # hatch --version outputs "Hatch, version X.Y.Z" — avoid
    # prefixing with "Hatch" again
    if version.lower().startswith("hatch"):
        return True, version
    return True, f"Hatch {version}"


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

    Uses :func:`_doctor_common.check_hook_installed` for detailed
    hook status detection (distinguishes installed, sample, custom,
    and missing hooks).

    Returns:
        Tuple of (passed, message).
    """
    installed: list[str] = []
    missing: list[str] = []

    for name, path in HOOK_FILES.items():
        status = check_hook_installed(path)
        if status == "installed":
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
    c = Colors(enabled=use_color)

    elapsed_start = time.monotonic()

    print()
    print(c.bold("Environment Health Check"))
    print(c.dim("=" * 50))

    # Core checks
    for r in results:
        if r["group"] == "core":
            print(
                f"  [{_icon(r['status'], use_color=use_color)}]"
                f" {c.dim(r['name'] + ':')} {r['message']}"
            )

    # Dev tool checks
    print()
    print(c.bold("Development Tools"))
    print(c.dim("-" * 50))
    for r in results:
        if r["group"] in ("tools", "optional"):
            print(f"  [{_icon(r['status'], use_color=use_color)}] {r['message']}")

    # Summary
    elapsed = time.monotonic() - elapsed_start
    print()
    total = len(results)
    passed_count = total - failures
    if failures == 0:
        summary = f"All {total} checks passed!"
        print(c.green(summary))
    else:
        summary = f"{passed_count}/{total} checks passed, {failures} failed"
        print(c.red(summary))
    print(c.dim(f"Completed in {elapsed:.1f}s"))
    print()

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
