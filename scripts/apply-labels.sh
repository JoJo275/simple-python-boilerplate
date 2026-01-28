#!/usr/bin/env bash
set -euo pipefail

# Wrapper around scripts/apply_labels.py
#
# Usage:
#   ./scripts/apply-labels.sh baseline
#   ./scripts/apply-labels.sh extended
#   ./scripts/apply-labels.sh baseline OWNER/REPO
#   ./scripts/apply-labels.sh baseline --dry-run

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SET="${1:-}"
shift || true
EXTRA_ARGS=("$@")

if [[ -z "${SET}" || ! "${SET}" =~ ^(baseline|extended)$ ]]; then
  echo "Usage: $0 {baseline|extended} [OWNER/REPO] [--dry-run]" >&2
  exit 2
fi

python3 "${SCRIPT_DIR}/apply_labels.py" --set "${SET}" "${EXTRA_ARGS[@]}"
