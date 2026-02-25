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
#
# Pinning the base image:
#   The base image is pinned to a specific digest for reproducible
#   builds. To update, run:
#     docker pull python:3.12-slim
#     docker inspect --format='{{index .RepoDigests 0}}' python:3.12-slim
#   Then replace the digest below.
# ──────────────────────────────────────────────────────────────

# Base image digest — pin for reproducibility (update via comment above)
ARG PYTHON_BASE=python:3.12-slim@sha256:41563b9752d16a220983617270a893a0ddd478717e1b9af7ca1df5c5fdb13c34

# ── Stage 1: Build ────────────────────────────────────────────
FROM ${PYTHON_BASE} AS builder

WORKDIR /build

# Install build tool first (layer cached independently of source changes)
COPY pyproject.toml README.md LICENSE ./
RUN python -m pip install --no-cache-dir build

# Copy source and build the wheel
COPY src/ src/
RUN python -m build --wheel --outdir /build/dist

# ── Stage 2: Runtime ──────────────────────────────────────────
FROM ${PYTHON_BASE} AS runtime

# OCI image metadata
# See: https://github.com/opencontainers/image-spec/blob/main/annotations.md
LABEL org.opencontainers.image.title="simple-python-boilerplate" \
      org.opencontainers.image.description="A Python boilerplate project" \
      org.opencontainers.image.source="https://github.com/YOUR_USERNAME/simple-python-boilerplate" \
      org.opencontainers.image.licenses="Apache-2.0"

# Don't run as root
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home app

WORKDIR /app

# Install only the built wheel (no build tools in final image)
COPY --from=builder /build/dist/*.whl /tmp/
RUN python -m pip install --no-cache-dir /tmp/*.whl \
    && rm -rf /tmp/*.whl

USER app

# Healthcheck — uncomment if this becomes an HTTP service:
# HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
#   CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

# Default command — runs the CLI entry point
ENTRYPOINT ["spb"]
