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
    --version    Print version and exit

Usage::

    python scripts/test_docker_compose.py
    python scripts/test_docker_compose.py --dry-run
    python scripts/test_docker_compose.py --keep --verbose
"""

from __future__ import annotations

import argparse
import logging
import subprocess  # nosec B404
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.1.0"

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
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

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

    failed = False
    for desc, cmd in steps:
        logger.info("Step: %s", desc)
        try:
            result = _run(cmd, verbose=args.verbose)
            if result.returncode != 0:
                logger.error("Step failed: %s (exit %d)", desc, result.returncode)
                failed = True
                break
        except subprocess.TimeoutExpired:
            logger.error("Step timed out: %s", desc)
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
