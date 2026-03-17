#!/usr/bin/env bash
# Test the docker compose stack: build, run, validate, and clean up.
#
# Usage:
#   bash scripts/test_docker_compose.sh
#   KEEP=1 bash scripts/test_docker_compose.sh    # skip cleanup
#   VERBOSE=1 bash scripts/test_docker_compose.sh # show build output
set -euo pipefail

cleanup() {
    if [ "${KEEP:-0}" != "1" ]; then
        echo "--- Cleaning up containers and images ---"
        docker compose down --rmi local --volumes 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo "=== Docker Compose Test ==="

echo "--- Validating compose config ---"
docker compose config --quiet

echo "--- Building image via docker compose ---"
if [ "${VERBOSE:-0}" = "1" ]; then
    docker compose build
else
    docker compose build --quiet
fi

echo "--- Verifying entrypoint (--help) ---"
docker compose run --rm app --help

echo "--- Checking non-root user ---"
ID_OUTPUT=$(docker compose run --rm --entrypoint id app)
echo "  $ID_OUTPUT"
if echo "$ID_OUTPUT" | grep -q "uid=0"; then
    echo "ERROR: Container is running as root (uid=0)"
    exit 1
fi

echo "=== Docker Compose Test PASSED ==="
