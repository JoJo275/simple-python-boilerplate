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
import logging
import os
import platform
import shutil
import struct
import subprocess  # nosec B404
import sys
import time
from collections.abc import Callable
from pathlib import Path

from _colors import Colors
from _colors import status_icon as _icon
from _colors import supports_color as _supports_color
from _doctor_common import check_hook_installed, get_package_version, get_version
from _imports import find_repo_root
from _progress import ProgressBar

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.4.0"

logger = logging.getLogger(__name__)

ROOT = find_repo_root()
# TODO (template users): Update MIN_PYTHON to match your project's
#   minimum supported Python version (see pyproject.toml requires-python).
MIN_PYTHON = (3, 11)

# TODO (template users): Update EXPECTED_TOOLS and OPTIONAL_TOOLS to
#   match the dev tools your project actually uses. Remove tools you
#   don't need and add any project-specific ones.
# Tools expected in the dev environment
EXPECTED_TOOLS = ["ruff", "mypy", "pytest", "bandit", "pre-commit", "cz", "deptry"]

# Optional tools — reported but don't fail unless --strict
OPTIONAL_TOOLS = ["actionlint"]

# TODO (template users): If you add or remove pre-commit hook stages,
#   update HOOK_FILES to match.
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


def check_os_platform() -> tuple[bool, str]:
    """Report the operating system and platform.

    Returns:
        Tuple of (passed, message). Always passes (informational).
    """
    os_name = platform.system()
    os_version = platform.version()
    machine = platform.machine()
    return True, f"{os_name} {os_version} ({machine})"


def check_pip_version() -> tuple[bool, str]:
    """Check if pip is available and report its version.

    Returns:
        Tuple of (passed, message).
    """
    version = get_version([sys.executable, "-m", "pip", "--version"])
    if version == "not found":
        return False, "pip not found"
    if version == "error":
        return False, "pip found but failed to run"
    # pip --version outputs: "pip X.Y.Z from /path ..." — extract version
    parts = version.split()
    if len(parts) >= 2:
        return True, f"pip {parts[1]}"
    return True, version


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


def check_node_available() -> tuple[bool, str]:
    """Check if Node.js is available (needed by prettier, markdownlint-cli2 hooks).

    Returns:
        Tuple of (passed, message).
    """
    node = shutil.which("node")
    if not node:
        return (
            False,
            "Node.js not found — needed by prettier/markdownlint pre-commit hooks",
        )
    version = get_version(["node", "--version"])
    if version in ("not found", "error"):
        return False, "Node.js found but failed to get version"
    return True, f"Node.js {version}"


def check_container_runtime() -> tuple[bool, str]:
    """Check if Docker or Podman is available for container workflows.

    Returns:
        Tuple of (passed, message).
    """
    for runtime in ("docker", "podman"):
        if shutil.which(runtime):
            version = get_version([runtime, "--version"])
            if version not in ("not found", "error"):
                return True, f"{runtime}: {version}"
            return True, f"{runtime} available"
    return False, "No container runtime (docker/podman) found"


def check_git_remote() -> tuple[bool, str]:
    """Check if a git remote origin is configured.

    Returns:
        Tuple of (passed, message).
    """
    git = shutil.which("git")
    if not git:
        return False, "git not found in PATH"
    try:
        result = subprocess.run(  # nosec B603
            [git, "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(ROOT),
        )
        url = result.stdout.strip()
        if url:
            return True, f"Git remote origin: {url}"
        return False, "No remote 'origin' configured"
    except (subprocess.TimeoutExpired, OSError):
        return False, "Could not check git remote"


def check_hatch_env_exists() -> tuple[bool, str]:
    """Check if the Hatch default environment is created.

    Returns:
        Tuple of (passed, message).
    """
    hatch = shutil.which("hatch")
    if not hatch:
        return False, "Hatch not found — cannot check env"
    try:
        result = subprocess.run(  # nosec B603
            [hatch, "env", "find", "default"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(ROOT),
        )
        env_path = result.stdout.strip()
        if result.returncode == 0 and env_path and Path(env_path).is_dir():
            return True, f"Hatch default env exists: {Path(env_path).name}"
        return False, "Hatch default env not created — run: hatch env create default"
    except (subprocess.TimeoutExpired, OSError):
        return False, "Could not check Hatch env"


def check_disk_space() -> tuple[bool, str]:
    """Warn if disk space on the project drive is below 1 GB.

    Returns:
        Tuple of (passed, message).
    """
    try:
        usage = shutil.disk_usage(ROOT)
        free_gb = usage.free / (1024**3)
        if free_gb < 1.0:
            return False, f"Low disk space: {free_gb:.1f} GB free"
        return True, f"Disk space: {free_gb:.1f} GB free"
    except OSError:
        return True, "Could not check disk space"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

CHECKS = [
    ("OS / Platform", check_os_platform),
    ("Python version", check_python_version),
    ("Architecture", check_architecture),
    ("pip", check_pip_version),
    ("Disk space", check_disk_space),
    ("Git repository", check_git_repo),
    ("Git user config", check_git_user_config),
    ("Git remote", check_git_remote),
    ("pyproject.toml", check_pyproject_toml),
    ("Virtual environment", check_venv_active),
    ("Editable install", check_editable_install),
    ("Hatch", check_hatch),
    ("Hatch default env", check_hatch_env_exists),
    ("Task runner", check_task),
    ("Pre-commit hooks", check_pre_commit_hooks),
]

# Additional optional checks with richer output than simple tool availability.
# Placed here (after function definitions) to avoid forward references.
OPTIONAL_CHECKS = [
    ("Node.js", check_node_available),
    ("Container runtime", check_container_runtime),
]


def _total_check_count() -> int:
    """Return the total number of checks that will run."""
    return (
        len(CHECKS) + len(EXPECTED_TOOLS) + len(OPTIONAL_TOOLS) + len(OPTIONAL_CHECKS)
    )


def _collect_results(
    strict: bool = False,
    on_progress: Callable[[str], None] | None = None,
) -> tuple[list[dict[str, str]], int]:
    """Run all checks and collect structured results.

    Args:
        strict: If True, treat optional items as required.
        on_progress: Optional callback invoked with the check name
            after each check completes (drives the progress bar).

    Returns:
        Tuple of (list of result dicts, failure count).
    """
    optional_checks = {
        "Task runner",
        "Architecture",
        "OS / Platform",
        "pip",
        "Disk space",
        "Git remote",
        "Hatch default env",
    }
    results: list[dict[str, str]] = []
    failures = 0

    def _tick(name: str) -> None:
        if on_progress:
            on_progress(name)

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
        _tick(name)

    # Required dev tools
    for tool in EXPECTED_TOOLS:
        passed, msg = check_tool_available(tool)
        status = "PASS" if passed else "FAIL"
        if not passed:
            failures += 1
        results.append(
            {"name": tool, "status": status, "message": msg, "group": "tools"}
        )
        _tick(tool)

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
        _tick(tool)

    # Optional checks (richer than simple tool lookup)
    for name, check_fn in OPTIONAL_CHECKS:
        passed, msg = check_fn()
        status = "PASS" if passed else "WARN"
        if not passed and strict:
            status = "FAIL"
            failures += 1
        results.append(
            {"name": name, "status": status, "message": msg, "group": "optional"}
        )
        _tick(name)

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
    elapsed_start = time.monotonic()

    # Show a progress bar while checks run (interactive terminals only).
    # JSON mode skips the bar since only machine-readable output matters.
    total = _total_check_count()
    bar: ProgressBar | None = None
    if not output_json:
        bar = ProgressBar(total=total, label="Checking", color="green")

    def _on_progress(name: str) -> None:
        if bar is not None:
            bar.update(name)

    results, failures = _collect_results(strict, on_progress=_on_progress)

    if bar is not None:
        bar.finish()

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

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    color = False if args.no_color else None
    return run_checks(strict=args.strict, color=color, output_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
