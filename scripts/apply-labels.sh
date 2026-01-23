#!/usr/bin/env bash
set -euo pipefail

# Wrapper around scripts/apply_labels.py
#
# Usage:
#   ./scripts/apply-labels.sh baseline
#   ./scripts/apply-labels.sh extended
#   ./scripts/apply-labels.sh baseline OWNER/REPO
#   ./scripts/apply-labels.sh baseline --dry-run

SET="${1:-}"
ARG="${2:-}"

if [[ -z "${SET}" ]]; then
  echo "Usage: $0 {baseline|extended} [OWNER/REPO|--dry-run]" >&2
  exit 2
fi

if [[ "${ARG}" == "--dry-run" ]]; then
  python3 scripts/apply_labels.py --set "${SET}" --dry-run
  exit 0
fi

if [[ -n "${ARG}" ]]; then
  python3 scripts/apply_labels.py --set "${SET}" --repo "${ARG}"
else
  python3 scripts/apply_labels.py --set "${SET}"
fi
