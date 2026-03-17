#!/usr/bin/env bash
# Test the docker compose stack: build, run, validate, and clean up.
#
# Usage:
#   bash scripts/test_docker_compose.sh
set -euo pipefail

IMAGE="simple-python-boilerplate:local"

cleanup() {
    echo "--- Cleaning up ---"
    docker compose down 2>/dev/null || true
}
trap cleanup EXIT

echo "=== Docker Compose Test ==="

echo "--- Building and starting containers ---"
docker compose up -d --build

echo "--- Showing running containers ---"
docker compose ps

echo "--- Showing container logs ---"
docker compose logs

echo "--- Verifying container runs correctly ---"
docker compose run --rm app --help

echo "--- Stopping containers ---"
docker compose down

echo "=== Docker Compose Test PASSED ==="
