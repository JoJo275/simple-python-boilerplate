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

Flags::

    --dry-run            Show what would happen without making changes
    --skip-hooks         Skip pre-commit hook installation
    --skip-test-matrix   Skip creating test.py3.x environments (faster setup)
    -q, --quiet          Suppress informational output (errors/warnings still shown)
    --version            Print version and exit

Usage::

    python scripts/bootstrap.py                            # full setup
    python scripts/bootstrap.py --skip-hooks               # skip hook install
    python scripts/bootstrap.py --skip-hooks --skip-test-matrix  # fastest setup
    python scripts/bootstrap.py --dry-run                  # preview

Portability:
    Repo-specific — expects Hatch, pre-commit, and this project's
    layout.  Requires shared modules: ``_colors.py``, ``_imports.py``,
    ``_ui.py``, ``_progress.py``.
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

# -- Local script modules (not third-party; live in scripts/) ----------------
from _colors import Colors, unicode_symbols
from _imports import find_repo_root
from _progress import Spinner
from _ui import UI

log = logging.getLogger(__name__)

ROOT = find_repo_root()
MIN_PYTHON = (3, 11)
TOTAL_STEPS = 7
SCRIPT_VERSION = "1.5.0"

# Theme color for this script's dashboard output.
THEME = "green"

# TODO (template users): Update MIN_PYTHON if your project supports
#   a different minimum Python version. Update TOTAL_STEPS if you
#   add or remove setup phases.

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
    c = Colors()
    log.info("\n%s", c.bold(f"[1/{TOTAL_STEPS}] Checking Python version..."))
    current = sys.version_info[:2]
    min_str = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    cur_str = f"{current[0]}.{current[1]}"

    sym = unicode_symbols()
    if current >= MIN_PYTHON:
        log.info(
            "  %s Python %s (>= %s)", c.green(sym["check"]), c.green(cur_str), min_str
        )
        return True
    else:
        log.error(
            "  %s Python %s %s requires >= %s",
            c.red(sym["cross"]),
            cur_str,
            sym["dash"],
            min_str,
        )
        log.error(
            "  Install Python %s+: %s",
            min_str,
            c.cyan("https://www.python.org/downloads/"),
        )
        return False


def check_git() -> bool:
    """Verify Git is installed and we're inside a Git repository."""
    c = Colors()
    log.info("\n%s", c.bold(f"[2/{TOTAL_STEPS}] Checking Git..."))
    sym = unicode_symbols()
    git = shutil.which("git")
    if not git:
        log.error("  %s Git not found", c.red(sym["cross"]))
        log.error("  Install from: %s", c.cyan("https://git-scm.com/downloads"))
        return False

    git_dir = ROOT / ".git"
    if not git_dir.is_dir():
        log.error("  %s Not a Git repository (no .git/ directory)", c.red(sym["cross"]))
        log.error("  Run: %s", c.cyan("git init"))
        return False

    log.info("  %s Git repository detected", c.green(sym["check"]))
    return True


def check_hatch() -> bool:
    """Verify Hatch is installed."""
    c = Colors()
    log.info("\n%s", c.bold(f"[3/{TOTAL_STEPS}] Checking Hatch..."))
    sym = unicode_symbols()
    hatch = shutil.which("hatch")
    if not hatch:
        log.error("  %s Hatch not found", c.red(sym["cross"]))
        if shutil.which("pipx"):
            log.error("  Install with: %s", c.cyan("pipx install hatch"))
        else:
            log.error("  Install with: %s", c.cyan("pip install --user hatch"))
            log.error(
                "  (Recommended: install pipx first, then: %s)",
                c.cyan("pipx install hatch"),
            )
            log.error(
                "  Why pipx? It installs Hatch in an isolated environment, avoiding"
            )
            log.error(
                "  dependency conflicts with your project's packages. pip install"
            )
            log.error(
                "  --user puts Hatch and its dependencies into your global Python,"
            )
            log.error("  which can cause version conflicts that are hard to diagnose.")
        return False

    result = run_cmd(["hatch", "--version"], capture=True, check=False)
    if result.returncode == 0:
        log.info("  %s %s", c.green(sym["check"]), result.stdout.strip())
        return True
    log.error("  %s Hatch found but failed to run", c.red(sym["cross"]))
    return False


def create_hatch_env(*, skip_test_matrix: bool = False, dry_run: bool = False) -> bool:
    """Create all Hatch environments (default, docs, test matrix).

    Args:
        skip_test_matrix: If True, skip creating test.py3.x environments.
        dry_run: If True, show what would happen without executing.

    Returns:
        True if all environments were created successfully.
    """
    c = Colors()
    log.info("\n%s", c.bold(f"[4/{TOTAL_STEPS}] Creating Hatch environments..."))

    # Environments to create
    envs = ["default", "docs"]
    if not skip_test_matrix:
        envs.extend(["test.py3.11", "test.py3.12", "test.py3.13"])

    sym = unicode_symbols()
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
                log.info(
                    "  %s %s environment already exists",
                    c.green(sym["check"]),
                    c.cyan(env),
                )
            else:
                with Spinner(f"Creating {env} environment") as spin:
                    spin.update(env)
                    run_cmd(["hatch", "env", "create", env], dry_run=dry_run)
                label = "Would create" if dry_run else "Created"
                log.info(
                    "  %s %s %s environment", c.green(sym["check"]), label, c.cyan(env)
                )
        except subprocess.CalledProcessError as e:
            log.error("  %s Failed to create %s: %s", c.red(sym["cross"]), env, e)
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
    c = Colors()
    log.info("\n%s", c.bold(f"[5/{TOTAL_STEPS}] Installing pre-commit hooks..."))
    sym = unicode_symbols()
    if skip:
        log.info("  %s Skipped (--skip-hooks)", c.dim(sym["arrow"]))
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
        with Spinner("Installing hook stages") as spin:
            for stage in stages:
                spin.update(stage)
                cmd = [*base, "install"]
                if stage != "pre-commit":
                    cmd.extend(["--hook-type", stage])
                run_cmd(cmd, dry_run=dry_run)
        label = "Would install" if dry_run else "Installed"
        log.info("  %s %s all hook stages", c.green(sym["check"]), label)
        return True
    except subprocess.CalledProcessError as e:
        log.error("  %s Failed: %s", c.red(sym["cross"]), e)
        return False


def check_task_runner() -> bool:
    """Check if Task runner is available (advisory only).

    Returns:
        True always — Task is optional so this never blocks setup.
    """
    c = Colors()
    log.info("\n%s", c.bold(f"[6/{TOTAL_STEPS}] Checking Task runner..."))
    sym = unicode_symbols()
    task = shutil.which("task")
    if task:
        log.info("  %s Task runner available", c.green(sym["check"]))
    else:
        log.warning(
            "  %s Task not found (optional but recommended)", c.yellow(sym["warn"])
        )
        log.warning("  Install from: %s", c.cyan("https://taskfile.dev/installation/"))
    return True


def verify_setup(*, dry_run: bool = False) -> bool:
    """Run a quick sanity check.

    Args:
        dry_run: If True, skip actual verification.

    Returns:
        True if the setup is verified (or dry-run mode).
    """
    c = Colors()
    log.info("\n%s", c.bold(f"[7/{TOTAL_STEPS}] Verifying setup..."))
    sym = unicode_symbols()
    if dry_run:
        log.info("  %s Would verify package version", c.dim(sym["arrow"]))
        return True
    try:
        with Spinner("Verifying package install") as spin:
            spin.update("importing package")
            # Quick test run
            # TODO (template users): Replace 'simple_python_boilerplate' with
            #   your package name after running customize.py.
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
            spin.update("checking version")
        version = result.stdout.strip()
        log.info("  %s Package version: %s", c.green(sym["check"]), c.cyan(version))
        return True
    except subprocess.CalledProcessError as e:
        log.error("  %s Verification failed: %s", c.red(sym["cross"]), e)
        return False


def print_next_steps(ui: UI) -> None:
    """Print helpful next steps and recommended scripts."""
    # TODO (template users): Update the package name and URLs below
    #   after running customize.py, or remove this function if your
    #   bootstrap has different post-setup instructions.
    c = Colors()
    ui.section("Setup Complete — Next Steps")
    log.info("")
    log.info("  1. Enter the dev environment:")
    log.info("     $ %s", c.cyan("hatch shell"))
    log.info("")
    log.info("  2. Verify the package is importable:")
    log.info(
        "     $ %s", c.cyan('hatch run python -c "import simple_python_boilerplate"')
    )
    log.info("")
    log.info("  3. Verify tools work:")
    log.info(
        "     $ %s        %s", c.cyan("task check"), c.dim("# Run all quality gates")
    )
    log.info("     $ %s         %s", c.cyan("task test"), c.dim("# Run tests"))
    log.info(
        "     $ %s       %s", c.cyan("task --list"), c.dim("# See all available tasks")
    )
    log.info("")
    log.info("  4. Customize the template:")
    log.info("     $ %s", c.cyan("python scripts/customize.py"))
    log.info("")
    log.info("  5. (Optional) Enable GitHub workflows:")
    log.info(
        "     $ %s", c.cyan("python scripts/customize.py --enable-workflows OWNER/REPO")
    )
    log.info(
        "     %s", c.dim("Or set repository variable: vars.ENABLE_WORKFLOWS = 'true'")
    )
    log.info("")
    log.info(
        "  %s",
        c.dim("Documentation: https://JoJo275.github.io/simple-python-boilerplate/"),
    )
    log.info("")

    ui.recommended_scripts(
        ["customize", "doctor", "repo_sauron", "dep_versions", "clean"],
        preamble="Scripts that help after initial setup.",
    )


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
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Quick import and arg-parse health check; exit 0 immediately",
    )
    args = parser.parse_args()

    if args.smoke:
        print(f"bootstrap {SCRIPT_VERSION}: smoke ok")
        return 0

    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)

    ui = UI(title="Bootstrap", version=SCRIPT_VERSION, theme=THEME)

    start_time = time.monotonic()

    if not args.quiet:
        ui.header()
        if args.dry_run:
            ui.info_line("Dry run mode — no changes will be made")

    # Run prerequisite checks
    all_ok = True
    all_ok &= check_python()
    all_ok &= check_git()
    all_ok &= check_hatch()

    sym = unicode_symbols()
    c = Colors()
    if not all_ok:
        log.error(
            "\n%s %s",
            c.red(sym["cross"]),
            c.red("Prerequisites not met. Fix the issues above and re-run."),
        )
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
        print_next_steps(ui)
        log.info("%s", c.dim(f"Completed in {elapsed:.1f}s"))
        return 0
    else:
        log.warning(
            "\n%s %s",
            c.yellow(sym["warn"]),
            c.yellow("Setup completed with warnings. Review the output above."),
        )
        log.info("%s", c.dim(f"Completed in {elapsed:.1f}s"))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
