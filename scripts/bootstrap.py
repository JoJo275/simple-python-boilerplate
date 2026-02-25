#!/usr/bin/env python3
"""One-command setup for fresh clones.

Typical actions:
1. Verify Python version meets requirements
2. Check Git repository
3. Check Hatch is installed
4. Create all Hatch environments (default, docs, test matrix)
5. Install pre-commit hooks (all stages)
6. Check Task runner availability
7. Verify editable install
8. Print next steps

Usage::

    python scripts/bootstrap.py
    python scripts/bootstrap.py --skip-hooks
    python scripts/bootstrap.py --skip-test-matrix  # Skip test.py3.x (3.11, 3.12, 3.13) envs
    python scripts/bootstrap.py --dry-run            # Show what would happen
"""

from __future__ import annotations

import argparse
import contextlib
import json
import logging
import shutil
import subprocess  # nosec B404
import sys
import time
from pathlib import Path

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
MIN_PYTHON = (3, 11)
TOTAL_STEPS = 7
SCRIPT_VERSION = "1.1.0"

# Default timeout for subprocess calls (5 minutes). Prevents hanging forever
# if a command (e.g., hatch env create) gets stuck.
_TIMEOUT = 300


def run_cmd(
    cmd: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    dry_run: bool = False,
    timeout: int = _TIMEOUT,
) -> subprocess.CompletedProcess[str]:
    """Run a command with standard settings.

    Args:
        cmd: Command and arguments to run.
        check: Raise on non-zero exit code.
        capture: Capture stdout/stderr instead of printing.
        dry_run: If True, log the command but don't execute it.
        timeout: Maximum seconds to wait for the command.

    Returns:
        Completed process result (or a dummy result in dry-run mode).
    """
    log.debug("  $ %s", " ".join(cmd))
    if dry_run:
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
    return subprocess.run(  # nosec B603
        cmd,
        cwd=ROOT,
        check=check,
        capture_output=capture,
        text=True,
        timeout=timeout,
    )


def check_python() -> bool:
    """Verify Python version."""
    log.info("\n[1/%d] Checking Python version...", TOTAL_STEPS)
    current = sys.version_info[:2]
    min_str = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    cur_str = f"{current[0]}.{current[1]}"

    if current >= MIN_PYTHON:
        log.info("  ✓ Python %s (>= %s)", cur_str, min_str)
        return True
    else:
        log.error("  ✗ Python %s — requires >= %s", cur_str, min_str)
        log.error("  Install Python %s+: https://www.python.org/downloads/", min_str)
        return False


def check_git() -> bool:
    """Verify Git is installed and we're inside a Git repository."""
    log.info("\n[2/%d] Checking Git...", TOTAL_STEPS)
    git = shutil.which("git")
    if not git:
        log.error("  ✗ Git not found")
        log.error("  Install from: https://git-scm.com/downloads")
        return False

    git_dir = ROOT / ".git"
    if not git_dir.is_dir():
        log.error("  ✗ Not a Git repository (no .git/ directory)")
        log.error("  Run: git init")
        return False

    log.info("  ✓ Git repository detected")
    return True


def check_hatch() -> bool:
    """Verify Hatch is installed."""
    log.info("\n[3/%d] Checking Hatch...", TOTAL_STEPS)
    hatch = shutil.which("hatch")
    if not hatch:
        log.error("  ✗ Hatch not found")
        if shutil.which("pipx"):
            log.error("  Install with: pipx install hatch")
        else:
            log.error("  Install with: pip install --user hatch")
            log.error("  (Recommended: install pipx first, then: pipx install hatch)")
        return False

    result = run_cmd(["hatch", "--version"], capture=True, check=False)
    if result.returncode == 0:
        log.info("  ✓ %s", result.stdout.strip())
        return True
    log.error("  ✗ Hatch found but failed to run")
    return False


def create_hatch_env(*, skip_test_matrix: bool = False, dry_run: bool = False) -> bool:
    """Create all Hatch environments (default, docs, test matrix).

    Args:
        skip_test_matrix: If True, skip creating test.py3.x environments.
        dry_run: If True, show what would happen without executing.

    Returns:
        True if all environments were created successfully.
    """
    log.info("\n[4/%d] Creating Hatch environments...", TOTAL_STEPS)

    # Environments to create
    envs = ["default", "docs"]
    if not skip_test_matrix:
        envs.extend(["test.py3.11", "test.py3.12", "test.py3.13"])

    # Query existing environments once (not per-env)
    existing_env_names: set[str] = set()
    if not dry_run:
        result = run_cmd(["hatch", "env", "show", "--json"], capture=True, check=False)
        if result.returncode == 0:
            with contextlib.suppress(json.JSONDecodeError, AttributeError):
                existing_env_names = set(json.loads(result.stdout).keys())

    all_ok = True
    for env in envs:
        try:
            if not dry_run and env in existing_env_names:
                log.info("  ✓ %s environment already exists", env)
            else:
                run_cmd(["hatch", "env", "create", env], dry_run=dry_run)
                label = "Would create" if dry_run else "Created"
                log.info("  ✓ %s %s environment", label, env)
        except subprocess.CalledProcessError as e:
            log.error("  ✗ Failed to create %s: %s", env, e)
            all_ok = False

    return all_ok


def install_hooks(*, skip: bool = False, dry_run: bool = False) -> bool:
    """Install pre-commit hooks.

    Args:
        skip: If True, skip hook installation entirely.
        dry_run: If True, show what would happen without executing.

    Returns:
        True if hooks were installed (or skipped) successfully.
    """
    log.info("\n[5/%d] Installing pre-commit hooks...", TOTAL_STEPS)
    if skip:
        log.info("  → Skipped (--skip-hooks)")
        return True

    # Build base command: direct pre-commit or via hatch
    pre_commit = shutil.which("pre-commit")
    if pre_commit:
        base = [pre_commit]
    else:
        log.info("  Using pre-commit via Hatch...")
        base = ["hatch", "run", "pre-commit"]

    stages = ["pre-commit", "commit-msg", "pre-push"]
    try:
        for stage in stages:
            cmd = [*base, "install"]
            if stage != "pre-commit":
                cmd.extend(["--hook-type", stage])
            run_cmd(cmd, dry_run=dry_run)
        label = "Would install" if dry_run else "Installed"
        log.info("  ✓ %s all hook stages", label)
        return True
    except subprocess.CalledProcessError as e:
        log.error("  ✗ Failed: %s", e)
        return False


def check_task_runner() -> bool:
    """Check if Task runner is available (advisory only).

    Returns:
        True always — Task is optional so this never blocks setup.
    """
    log.info("\n[6/%d] Checking Task runner...", TOTAL_STEPS)
    task = shutil.which("task")
    if task:
        log.info("  ✓ Task runner available")
    else:
        log.warning("  ⚠ Task not found (optional but recommended)")
        log.warning("  Install from: https://taskfile.dev/installation/")
    return True


def verify_setup(*, dry_run: bool = False) -> bool:
    """Run a quick sanity check.

    Args:
        dry_run: If True, skip actual verification.

    Returns:
        True if the setup is verified (or dry-run mode).
    """
    log.info("\n[7/%d] Verifying setup...", TOTAL_STEPS)
    if dry_run:
        log.info("  → Would verify package version")
        return True
    try:
        # Quick test run
        result = run_cmd(
            [
                "hatch",
                "run",
                "python",
                "-c",
                "from simple_python_boilerplate import __version__; print(__version__)",
            ],
            capture=True,
        )
        version = result.stdout.strip()
        log.info("  ✓ Package version: %s", version)
        return True
    except subprocess.CalledProcessError as e:
        log.error("  ✗ Verification failed: %s", e)
        return False


def print_next_steps() -> None:
    """Print helpful next steps."""
    log.info("\n" + "=" * 60)
    log.info("SETUP COMPLETE")
    log.info("=" * 60)
    log.info("""
Next steps:

  1. Enter the dev environment:
     $ hatch shell

  2. Verify the package is importable:
     $ hatch run python -c "import simple_python_boilerplate"

  3. Verify tools work:
     $ task check        # Run all quality gates
     $ task test         # Run tests
     $ task --list       # See all available tasks

  4. Customize the template:
     $ python scripts/customize.py

  5. (Optional) Enable GitHub workflows:
     $ python scripts/customize.py --enable-workflows OWNER/REPO
     - Or set repository variable: vars.ENABLE_WORKFLOWS = 'true'

Documentation: https://YOURNAME.github.io/YOURREPO/
""")


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="bootstrap",
        description="One-command setup for fresh clones.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--skip-hooks",
        action="store_true",
        help="Skip pre-commit hook installation",
    )
    parser.add_argument(
        "--skip-test-matrix",
        action="store_true",
        help="Skip creating test.py3.x environments (faster setup)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress informational output (errors and warnings still shown)",
    )
    args = parser.parse_args()

    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)

    start_time = time.monotonic()

    log.info("=" * 60)
    label = (
        "BOOTSTRAP: Dry run"
        if args.dry_run
        else "BOOTSTRAP: Setting up development environment"
    )
    log.info("%s", label)
    log.info("=" * 60)

    # Run prerequisite checks
    all_ok = True
    all_ok &= check_python()
    all_ok &= check_git()
    all_ok &= check_hatch()

    if not all_ok:
        log.error("\n✗ Prerequisites not met. Fix the issues above and re-run.")
        return 1

    # Setup steps
    all_ok &= create_hatch_env(
        skip_test_matrix=args.skip_test_matrix, dry_run=args.dry_run
    )
    all_ok &= install_hooks(skip=args.skip_hooks, dry_run=args.dry_run)
    check_task_runner()
    all_ok &= verify_setup(dry_run=args.dry_run)

    elapsed = time.monotonic() - start_time

    if all_ok:
        print_next_steps()
        log.info("Completed in %.1fs", elapsed)
        return 0
    else:
        log.warning("\n⚠ Setup completed with warnings. Review the output above.")
        log.info("Completed in %.1fs", elapsed)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
