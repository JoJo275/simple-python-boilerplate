#!/usr/bin/env python3
"""Pre-commit hook: fail if any staged file contains NUL (0x00) bytes.

NUL bytes in source/config files are almost always accidental (binary
corruption, bad copy-paste) and silently break many tools.

Usage (called by pre-commit, receives filenames as arguments):
    python scripts/check_nul_bytes.py file1 file2 ...

Exit codes:
    0 — no NUL bytes found
    1 — one or more files contain NUL bytes
"""

from __future__ import annotations

import sys


def check_file(path: str) -> bool:
    """Return True if the file contains a NUL byte."""
    try:
        with open(path, "rb") as f:
            return b"\x00" in f.read()
    except OSError:
        return False


def main() -> int:
    """Check all files passed as arguments for NUL bytes."""
    found = False
    for path in sys.argv[1:]:
        if check_file(path):
            print(f"ERROR: NUL byte detected in {path}", file=sys.stderr)
            found = True
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
