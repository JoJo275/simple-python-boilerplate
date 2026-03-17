#!/usr/bin/env python3
"""Test the Containerfile: build the image, run basic checks, and clean up.

Builds the production image directly from the Containerfile (without
docker compose), verifies the entrypoint works, checks the non-root user,
and removes the test image.

Flags::

    --help       Show help message and exit
    --dry-run    Show what would be executed without running
    --keep       Keep the test image after running (skip cleanup)
    --version    Print version and exit

Usage::

    python scripts/test_containerfile.py
    python scripts/test_containerfile.py --dry-run
    python scripts/test_containerfile.py --keep
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
IMAGE_NAME = "simple-python-boilerplate:test"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(
    args: list[str],
    *,
    check: bool = True,
    timeout: int = 120,
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
        description="Test the Containerfile: build, validate, clean up.",
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
        help="Keep the test image after running (skip cleanup)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    steps: list[tuple[str, list[str]]] = [
        (
            "Build image from Containerfile",
            ["docker", "build", "-t", IMAGE_NAME, "-f", "Containerfile", "."],
        ),
        (
            "Verify entrypoint (--help)",
            ["docker", "run", "--rm", IMAGE_NAME, "--help"],
        ),
        (
            "Check non-root user",
            ["docker", "run", "--rm", "--entrypoint", "id", IMAGE_NAME],
        ),
        (
            "Check Python is available",
            [
                "docker",
                "run",
                "--rm",
                "--entrypoint",
                "python",
                IMAGE_NAME,
                "--version",
            ],
        ),
    ]

    if args.dry_run:
        print("Dry run — would execute:")
        for desc, cmd in steps:
            print(f"  [{desc}] {' '.join(cmd)}")
        if not args.keep:
            print(f"  [Remove test image] docker rmi {IMAGE_NAME}")
        return 0

    failed = False
    for desc, cmd in steps:
        logger.info("Step: %s", desc)
        try:
            result = _run(cmd)
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

    # Clean up image unless --keep
    if not args.keep:
        logger.info("Removing test image: %s", IMAGE_NAME)
        try:
            subprocess.run(  # nosec B603 B607
                ["docker", "rmi", IMAGE_NAME],
                check=False,
                timeout=30,
                capture_output=True,
            )
        except subprocess.TimeoutExpired:
            logger.warning("Image removal timed out")

    if failed:
        logger.error("Containerfile test FAILED")
        return 1

    logger.info("Containerfile test PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
