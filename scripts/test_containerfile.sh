#!/usr/bin/env bash
# Test the Containerfile: build image, run basic checks, and clean up.
#
# Usage:
#   bash scripts/test_containerfile.sh
#   KEEP_IMAGE=1 bash scripts/test_containerfile.sh   # skip image removal
set -euo pipefail

IMAGE="simple-python-boilerplate:test"

cleanup() {
    if [ "${KEEP_IMAGE:-0}" != "1" ]; then
        echo "--- Removing test image ---"
        docker rmi "$IMAGE" 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo "=== Containerfile Test ==="

echo "--- Building image from Containerfile ---"
docker build -t "$IMAGE" -f Containerfile .

echo "--- Verifying entrypoint (--help) ---"
docker run --rm "$IMAGE" --help

echo "--- Checking non-root user ---"
docker run --rm --entrypoint id "$IMAGE"

echo "--- Checking Python is available ---"
docker run --rm --entrypoint python "$IMAGE" --version

echo "=== Containerfile Test PASSED ==="
