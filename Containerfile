# ──────────────────────────────────────────────────────────────
# Containerfile (OCI-compatible, works with Podman and Docker)
# ──────────────────────────────────────────────────────────────
# Builds a minimal container image for the application.
#
# Usage:
#   podman build -t simple-python-boilerplate -f Containerfile .
#   podman run --rm simple-python-boilerplate
#
# Or with Docker:
#   docker build -t simple-python-boilerplate -f Containerfile .
#   docker run --rm simple-python-boilerplate
#
# Multi-stage build:
#   Stage 1 (builder) – installs build tools + builds the wheel
#   Stage 2 (runtime) – copies only the installed package into
#                        a slim image with no build tooling
# ──────────────────────────────────────────────────────────────

# ── Stage 1: Build ────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies first (layer caching)
COPY pyproject.toml README.md ./
COPY src/ src/

RUN python -m pip install --no-cache-dir build \
    && python -m build --wheel --outdir /build/dist

# ── Stage 2: Runtime ──────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Don't run as root
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home app

WORKDIR /app

# Install only the built wheel (no build tools in final image)
COPY --from=builder /build/dist/*.whl /tmp/
RUN python -m pip install --no-cache-dir /tmp/*.whl \
    && rm -rf /tmp/*.whl

USER app

# Default command — runs the CLI entry point
ENTRYPOINT ["spb"]
