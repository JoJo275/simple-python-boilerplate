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
import shutil
import subprocess  # nosec B404
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_PYTHON = (3, 11)
TOTAL_STEPS = 7

# Module-level verbosity flag, set by CLI parsing
_quiet = False


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
        dry_run: If True, print the command but don't execute it.
        timeout: Maximum seconds to wait for the command.

    Returns:
        Completed process result (or a dummy result in dry-run mode).
    """
    if not _quiet:
        print(f"  $ {' '.join(cmd)}")
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
    print(f"\n[1/{TOTAL_STEPS}] Checking Python version...")
    current = sys.version_info[:2]
    min_str = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    cur_str = f"{current[0]}.{current[1]}"

    if current >= MIN_PYTHON:
        print(f"  ✓ Python {cur_str} (>= {min_str})")
        return True
    else:
        print(f"  ✗ Python {cur_str} — requires >= {min_str}")
        print(f"  Install Python {min_str}+: https://www.python.org/downloads/")
        return False


def check_git() -> bool:
    """Verify Git is installed and we're inside a Git repository."""
    print(f"\n[2/{TOTAL_STEPS}] Checking Git...")
    git = shutil.which("git")
    if not git:
        print("  ✗ Git not found")
        print("  Install from: https://git-scm.com/downloads")
        return False

    git_dir = ROOT / ".git"
    if not git_dir.is_dir():
        print("  ✗ Not a Git repository (no .git/ directory)")
        print("  Run: git init")
        return False

    print("  ✓ Git repository detected")
    return True


def check_hatch() -> bool:
    """Verify Hatch is installed."""
    print(f"\n[3/{TOTAL_STEPS}] Checking Hatch...")
    hatch = shutil.which("hatch")
    if not hatch:
        print("  ✗ Hatch not found")
        if shutil.which("pipx"):
            print("  Install with: pipx install hatch")
        else:
            print("  Install with: pip install --user hatch")
            print("  (Recommended: install pipx first, then: pipx install hatch)")
        return False

    result = run_cmd(["hatch", "--version"], capture=True, check=False)
    if result.returncode == 0:
        print(f"  ✓ {result.stdout.strip()}")
        return True
    print("  ✗ Hatch found but failed to run")
    return False


def create_hatch_env(*, skip_test_matrix: bool = False, dry_run: bool = False) -> bool:
    """Create all Hatch environments (default, docs, test matrix).

    Args:
        skip_test_matrix: If True, skip creating test.py3.x environments.
        dry_run: If True, show what would happen without executing.

    Returns:
        True if all environments were created successfully.
    """
    print(f"\n[4/{TOTAL_STEPS}] Creating Hatch environments...")

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
                print(f"  ✓ {env} environment already exists")
            else:
                run_cmd(["hatch", "env", "create", env], dry_run=dry_run)
                print(
                    f"  ✓ {'Would create' if dry_run else 'Created'} {env} environment"
                )
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to create {env}: {e}")
            all_ok = False

    # Verify package is importable in default environment
    if all_ok and not dry_run:
        try:
            run_cmd(
                ["hatch", "run", "python", "-c", "import simple_python_boilerplate"],
                capture=True,
            )
            print("  ✓ Package importable in default environment")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Package import failed: {e}")
            all_ok = False
    elif dry_run:
        print("  → Would verify package is importable")

    return all_ok


def install_hooks(*, skip: bool = False, dry_run: bool = False) -> bool:
    """Install pre-commit hooks.

    Args:
        skip: If True, skip hook installation entirely.
        dry_run: If True, show what would happen without executing.

    Returns:
        True if hooks were installed (or skipped) successfully.
    """
    print(f"\n[5/{TOTAL_STEPS}] Installing pre-commit hooks...")
    if skip:
        print("  → Skipped (--skip-hooks)")
        return True

    # Build base command: direct pre-commit or via hatch
    pre_commit = shutil.which("pre-commit")
    if pre_commit:
        base = [pre_commit]
    else:
        print("  Using pre-commit via Hatch...")
        base = ["hatch", "run", "pre-commit"]

    stages = ["pre-commit", "commit-msg", "pre-push"]
    try:
        for stage in stages:
            cmd = [*base, "install"]
            if stage != "pre-commit":
                cmd.extend(["--hook-type", stage])
            run_cmd(cmd, dry_run=dry_run)
        label = "Would install" if dry_run else "Installed"
        print(f"  ✓ {label} all hook stages")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {e}")
        return False


def check_task_runner() -> bool:
    """Check if Task runner is available (advisory only).

    Returns:
        True always — Task is optional so this never blocks setup.
    """
    print(f"\n[6/{TOTAL_STEPS}] Checking Task runner...")
    task = shutil.which("task")
    if task:
        print("  ✓ Task runner available")
    else:
        print("  ⚠ Task not found (optional but recommended)")
        print("  Install from: https://taskfile.dev/installation/")
    return True


def verify_setup(*, dry_run: bool = False) -> bool:
    """Run a quick sanity check.

    Args:
        dry_run: If True, skip actual verification.

    Returns:
        True if the setup is verified (or dry-run mode).
    """
    print(f"\n[7/{TOTAL_STEPS}] Verifying setup...")
    if dry_run:
        print("  → Would verify package version")
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
        print(f"  ✓ Package version: {version}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Verification failed: {e}")
        return False


def print_next_steps() -> None:
    """Print helpful next steps."""
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print("""
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
        help="Suppress command echo output (show only results)",
    )
    args = parser.parse_args()

    global _quiet  # intentional module-level state for CLI flag
    _quiet = args.quiet

    start_time = time.monotonic()

    print("=" * 60)
    label = (
        "BOOTSTRAP: Dry run"
        if args.dry_run
        else "BOOTSTRAP: Setting up development environment"
    )
    print(label)
    print("=" * 60)

    # Run prerequisite checks
    all_ok = True
    all_ok &= check_python()
    all_ok &= check_git()
    all_ok &= check_hatch()

    if not all_ok:
        print("\n✗ Prerequisites not met. Fix the issues above and re-run.")
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
        print(f"Completed in {elapsed:.1f}s")
        return 0
    else:
        print("\n⚠ Setup completed with warnings. Review the output above.")
        print(f"Completed in {elapsed:.1f}s")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
