#!/usr/bin/env python3
"""One-command setup for fresh clones.

Typical actions:
1. Verify Python version meets requirements
2. Create all Hatch environments (default, docs, test matrix)
3. Install pre-commit hooks (all stages)
4. Verify editable install
5. Print next steps

Usage::

    python scripts/bootstrap.py
    python scripts/bootstrap.py --skip-hooks
    python scripts/bootstrap.py --skip-test-matrix  # Skip test.py3.x (3.11, 3.12, 3.13) envs
"""

from __future__ import annotations

import argparse
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_PYTHON = (3, 11)


def run_cmd(
    cmd: list[str],
    *,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a command with standard settings."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(  # nosec B603
        cmd,
        cwd=ROOT,
        check=check,
        capture_output=capture,
        text=True,
    )


def check_python() -> bool:
    """Verify Python version."""
    print("\n[1/5] Checking Python version...")
    current = sys.version_info[:2]
    min_str = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    cur_str = f"{current[0]}.{current[1]}"

    if current >= MIN_PYTHON:
        print(f"  ✓ Python {cur_str} (>= {min_str})")
        return True
    else:
        print(f"  ✗ Python {cur_str} — requires >= {min_str}")
        return False


def check_hatch() -> bool:
    """Verify Hatch is installed."""
    print("\n[2/5] Checking Hatch...")
    hatch = shutil.which("hatch")
    if not hatch:
        print("  ✗ Hatch not found")
        print("  Install with: pipx install hatch")
        return False

    result = run_cmd(["hatch", "version"], capture=True, check=False)
    if result.returncode == 0:
        print(f"  ✓ Hatch {result.stdout.strip()}")
        return True
    print("  ✗ Hatch found but failed to run")
    return False


def create_hatch_env(*, skip_test_matrix: bool = False) -> bool:
    """Create all Hatch environments (default, docs, test matrix).

    Args:
        skip_test_matrix: If True, skip creating test.py3.x environments.

    Returns:
        True if all environments were created successfully.
    """
    print("\n[3/5] Creating Hatch environments...")

    # Environments to create
    envs = ["default", "docs"]
    if not skip_test_matrix:
        envs.extend(["test.py3.11", "test.py3.12", "test.py3.13"])

    all_ok = True
    for env in envs:
        try:
            # Check if env exists
            result = run_cmd(
                ["hatch", "env", "show", "--json"], capture=True, check=False
            )
            if result.returncode == 0 and env in result.stdout:
                print(f"  ✓ {env} environment already exists")
            else:
                run_cmd(["hatch", "env", "create", env])
                print(f"  ✓ Created {env} environment")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to create {env}: {e}")
            all_ok = False

    # Verify package is importable in default environment
    if all_ok:
        try:
            run_cmd(
                ["hatch", "run", "python", "-c", "import simple_python_boilerplate"],
                capture=True,
            )
            print("  ✓ Package importable in default environment")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Package import failed: {e}")
            all_ok = False

    return all_ok


def install_hooks(*, skip: bool = False) -> bool:
    """Install pre-commit hooks."""
    print("\n[4/5] Installing pre-commit hooks...")
    if skip:
        print("  → Skipped (--skip-hooks)")
        return True

    pre_commit = shutil.which("pre-commit")
    if not pre_commit:
        # Try via hatch
        print("  Using pre-commit via Hatch...")
        stages = ["pre-commit", "commit-msg", "pre-push"]
        try:
            for stage in stages:
                if stage == "pre-commit":
                    run_cmd(["hatch", "run", "pre-commit", "install"])
                else:
                    run_cmd(
                        ["hatch", "run", "pre-commit", "install", "--hook-type", stage]
                    )
            print("  ✓ All hook stages installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed: {e}")
            return False

    try:
        run_cmd([pre_commit, "install"])
        run_cmd([pre_commit, "install", "--hook-type", "commit-msg"])
        run_cmd([pre_commit, "install", "--hook-type", "pre-push"])
        print("  ✓ All hook stages installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {e}")
        return False


def verify_setup() -> bool:
    """Run a quick sanity check."""
    print("\n[5/5] Verifying setup...")
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
    args = parser.parse_args()

    print("=" * 60)
    print("BOOTSTRAP: Setting up development environment")
    print("=" * 60)

    # Run all checks
    all_ok = True
    all_ok &= check_python()
    all_ok &= check_hatch()

    if not all_ok:
        print("\n✗ Prerequisites not met. Fix the issues above and re-run.")
        return 1

    # Setup steps
    all_ok &= create_hatch_env(skip_test_matrix=args.skip_test_matrix)
    all_ok &= install_hooks(skip=args.skip_hooks)
    all_ok &= verify_setup()

    if all_ok:
        print_next_steps()
        return 0
    else:
        print("\n⚠ Setup completed with warnings. Review the output above.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
