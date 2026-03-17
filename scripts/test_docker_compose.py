#!/usr/bin/env python3
"""Test the docker compose stack: build, run, validate, and clean up.

Builds the image via docker compose, starts the container, verifies it
exits successfully (for CLI tools) or responds to a health check (for
services), and tears everything down.

Flags::

    --help       Show help message and exit
    --dry-run    Show what would be executed without running
    --version    Print version and exit

Usage::

    python scripts/test_docker_compose.py
    python scripts/test_docker_compose.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import subprocess  # nosec B404
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.0.0"
IMAGE_NAME = "simple-python-boilerplate:local"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(args: list[str], *, check: bool = True, timeout: int = 120) -> int:
    """Run a command and return the exit code."""
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
    if result.returncode != 0 and result.stderr:
        for line in result.stderr.splitlines():
            logger.error("  %s", line)
    return result.returncode


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
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    steps: list[tuple[str, list[str]]] = [
        ("Build and start containers", ["docker", "compose", "up", "-d", "--build"]),
        ("Show running containers", ["docker", "compose", "ps"]),
        ("Show container logs", ["docker", "compose", "logs"]),
        (
            "Verify container ran successfully",
            ["docker", "compose", "run", "--rm", "app", "--help"],
        ),
        ("Stop and remove containers", ["docker", "compose", "down"]),
    ]

    if args.dry_run:
        print("Dry run — would execute:")
        for desc, cmd in steps:
            print(f"  [{desc}] {' '.join(cmd)}")
        return 0

    failed = False
    for desc, cmd in steps:
        logger.info("Step: %s", desc)
        try:
            code = _run(cmd)
            if code != 0:
                logger.error("Step failed: %s (exit %d)", desc, code)
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

    # Always clean up
    try:
        subprocess.run(  # nosec B603 B607
            ["docker", "compose", "down"],
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
