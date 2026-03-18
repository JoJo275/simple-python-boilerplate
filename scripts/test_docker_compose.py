#!/usr/bin/env python3
"""Test the docker compose stack: build, run, validate, and clean up.

Builds the image via docker compose, runs the container to verify the
entrypoint works and the configuration is valid, then tears everything
down.

Flags::

    --help       Show help message and exit
    --dry-run    Show what would be executed without running
    --keep       Keep containers and images after running (skip cleanup)
    --verbose    Show full command output including stderr
    --timeout N  Per-step timeout in seconds (default: 300)
    --version    Print version and exit

Usage::

    python scripts/test_docker_compose.py
    python scripts/test_docker_compose.py --dry-run
    python scripts/test_docker_compose.py --keep --verbose
    python scripts/test_docker_compose.py --timeout 600
"""

from __future__ import annotations

import argparse
import logging
import re
import subprocess  # nosec B404
import sys

# TODO: Import _imports.find_repo_root and os.chdir(ROOT) to avoid
#   CWD dependency — currently docker compose commands assume the
#   script is run from the repo root.
# TODO: Import Spinner from _progress.py to wrap the docker compose
#   build/up steps (can take 60-300+ seconds with no visual feedback).

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.2.0"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(
    args: list[str],
    *,
    check: bool = True,
    timeout: int = 300,
    verbose: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a command and return the CompletedProcess."""
    logger.info("Running: %s", " ".join(args))
    result = subprocess.run(  # nosec B603
        args,
        check=check,
        timeout=timeout,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        for line in result.stdout.splitlines():
            logger.info("  %s", line)
    if verbose and result.stderr:
        for line in result.stderr.splitlines():
            logger.debug("  stderr: %s", line)
    if result.returncode != 0 and result.stderr:
        for line in result.stderr.splitlines():
            logger.error("  %s", line)
    return result


def _check_docker_available() -> bool:
    """Verify docker CLI is available and the daemon is running."""
    try:
        result = subprocess.run(  # nosec B603 B607
            ["docker", "info"],
            check=False,
            timeout=15,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error(
                "Docker daemon not running or not accessible. "
                "Start Docker Desktop or the docker service first."
            )
            return False
        return True
    except FileNotFoundError:
        logger.error("docker CLI not found on PATH")
        return False
    except subprocess.TimeoutExpired:
        logger.error("docker info timed out \u2014 daemon may be unresponsive")
        return False


def _check_non_root(output: str) -> bool:
    """Verify the container is not running as root (uid=0)."""
    uid_match = re.search(r"uid=(\d+)", output)
    if not uid_match:
        logger.error("Could not parse uid from `id` output: %s", output.strip())
        return False
    if uid_match.group(1) == "0":
        logger.error("Container is running as root (uid=0)")
        return False
    logger.info("  Non-root verified: %s", output.strip().split()[0])
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Test the docker compose stack: build, run, validate, clean up.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without running",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep containers and images after running (skip cleanup)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show full command output including stderr",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        metavar="N",
        help="Per-step timeout in seconds (default: 300)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    if not args.dry_run and not _check_docker_available():
        return 1

    # TODO (template users): Add or remove compose test steps to match your
    #   docker-compose.yml services (e.g. database readiness checks, port
    #   mapping validation, multi-service integration tests).
    # Build first, then run individual checks via `docker compose run`.
    # This avoids `up -d` which would start the CLI and immediately exit.
    steps: list[tuple[str, list[str]]] = [
        ("Build image via docker compose", ["docker", "compose", "build"]),
        ("Validate compose config", ["docker", "compose", "config", "--quiet"]),
        (
            "Verify entrypoint (--help)",
            ["docker", "compose", "run", "--rm", "app", "--help"],
        ),
        (
            "Check non-root user",
            [
                "docker",
                "compose",
                "run",
                "--rm",
                "--entrypoint",
                "id",
                "app",
            ],
        ),
    ]

    if args.dry_run:
        print("Dry run — would execute:")
        for desc, cmd in steps:
            print(f"  [{desc}] {' '.join(cmd)}")
        if not args.keep:
            print("  [Clean up] docker compose down --rmi local --volumes")
        return 0

    step_timeout = args.timeout
    failed = False
    for desc, cmd in steps:
        logger.info("Step: %s", desc)
        try:
            result = _run(cmd, verbose=args.verbose, timeout=step_timeout)
            if result.returncode != 0:
                logger.error("Step failed: %s (exit %d)", desc, result.returncode)
                failed = True
                break
            # Extra validation for the non-root check
            if desc == "Check non-root user" and not _check_non_root(result.stdout):
                failed = True
                break
        except subprocess.TimeoutExpired:
            logger.error(
                "Step timed out after %ds: %s (increase with --timeout)",
                step_timeout,
                desc,
            )
            failed = True
            break
        except subprocess.CalledProcessError as exc:
            logger.error("Step failed: %s (exit %d)", desc, exc.returncode)
            failed = True
            break

    # Always clean up unless --keep
    if not args.keep:
        logger.info("Cleaning up containers and images")
        try:
            subprocess.run(  # nosec B603 B607
                ["docker", "compose", "down", "--rmi", "local", "--volumes"],
                check=False,
                timeout=60,
                capture_output=True,
            )
        except subprocess.TimeoutExpired:
            logger.warning("Cleanup timed out")

    if failed:
        logger.error("Docker compose test FAILED")
        return 1

    logger.info("Docker compose test PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
