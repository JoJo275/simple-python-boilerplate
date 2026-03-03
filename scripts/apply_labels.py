#!/usr/bin/env python3
"""Apply GitHub labels to a repository using GitHub CLI.

Requirements:
  - Python 3
  - GitHub CLI (``gh``) installed and authenticated (``gh auth login``)

Flags::

    --set {baseline,extended}  Label set to apply (required)
    --repo OWNER/REPO          Target repository (default: current repo)
    --dry-run                  Print commands without executing them

Usage::

    scripts/apply_labels.py --set baseline --repo OWNER/REPO
    scripts/apply_labels.py --set extended --repo OWNER/REPO
    scripts/apply_labels.py --set baseline --dry-run

For visual example of extended set, see
https://github.com/JoJo275/simple-python-boilerplate/labels?page=1.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess  # nosec B404
import sys
import urllib.parse
from pathlib import Path

SCRIPT_VERSION = "1.2.0"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def _terminal_width() -> int:
    """Get terminal width, with a sensible fallback."""
    return shutil.get_terminal_size((80, 24)).columns


def _is_interactive() -> bool:
    """Return True if stdout is a TTY (not piped/redirected)."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _print_progress(
    current: int,
    total: int,
    label_name: str,
    *,
    bar_width: int | None = None,
) -> None:
    """Print an inline progress bar that overwrites itself.

    Example output::

        Applying labels  [████████████░░░░░░░░]  12/72 (17%)  bug

    Degrades gracefully:
    - If stdout is not a TTY (piped), prints nothing (final summary suffices).
    - On narrow terminals the bar shrinks or is omitted.
    """
    if not _is_interactive():
        return

    pct = int(current / total * 100) if total else 0
    counter = f"{current}/{total} ({pct:>3}%)"
    prefix = "Applying labels  "

    # Truncate long label names so the bar fits one line
    max_label_len = 30
    display_name = (
        label_name[: max_label_len - 1] + "…"
        if len(label_name) > max_label_len
        else label_name
    )

    if bar_width is None:
        # Reserve space for: prefix + [bar] + counter + label + padding
        overhead = (
            len(prefix) + len(counter) + len(display_name) + 8
        )  # brackets + spaces
        bar_width = max(_terminal_width() - overhead, 10)

    filled = int(bar_width * current / total) if total else 0
    bar = "█" * filled + "░" * (bar_width - filled)

    line = f"\r{prefix}[{bar}]  {counter}  {display_name}"
    # Pad with spaces to clear leftover chars from previous longer lines
    sys.stdout.write(line.ljust(_terminal_width()))
    sys.stdout.flush()


def _finish_progress() -> None:
    """Move to a new line after the progress bar is complete."""
    if _is_interactive():
        sys.stdout.write("\n")
        sys.stdout.flush()


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True)  # nosec B603


def gh_exists() -> bool:
    """Check if GitHub CLI is installed."""
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)  # nosec B603 B607
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def default_repo() -> str | None:
    p = run(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"])
    if p.returncode != 0:
        return None
    return (p.stdout or "").strip() or None


def gh_api(
    method: str, endpoint: str, fields: dict[str, str]
) -> subprocess.CompletedProcess:
    cmd = ["gh", "api", "-X", method, endpoint]
    for k, v in fields.items():
        cmd += ["-f", f"{k}={v}"]
    return run(cmd)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Apply GitHub labels to a repository from a JSON label set.",
    )
    ap.add_argument("--set", choices=["baseline", "extended"], required=True)
    ap.add_argument("--repo", help="OWNER/REPO; default is current repo")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    args = ap.parse_args()

    # Ensure gh is installed
    if not gh_exists():
        print(
            "Error: GitHub CLI (gh) is not installed. Install from https://cli.github.com/",
            file=sys.stderr,
        )
        return 2

    repo = args.repo or default_repo()
    if not repo:
        print(
            "Error: could not determine repo. Run inside a repo or pass --repo OWNER/REPO.",
            file=sys.stderr,
        )
        return 2

    spec = ROOT / "labels" / f"{args.set}.json"
    if not spec.exists():
        print(f"Error: missing label spec: {spec}", file=sys.stderr)
        return 2

    # Ensure gh auth
    st = run(["gh", "auth", "status"])
    if st.returncode != 0:
        print("Error: gh is not authenticated. Run: gh auth login", file=sys.stderr)
        return 2

    try:
        labels: list[dict[str, str]] = json.loads(spec.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {spec}: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"[DRY RUN] Would process {len(labels)} labels for {repo}")
        for lab in labels:
            name = lab["name"]
            color = lab["color"].lstrip("#")
            desc = lab.get("description", "")
            print(f"  upsert: {name} (#{color}) - {desc}")
        return 0

    total = len(labels)
    print(f"Processing {total} labels for {repo}…")

    created = updated = 0
    failures: list[str] = []

    for i, lab in enumerate(labels, start=1):
        name = lab["name"]
        color = lab["color"].lstrip("#")
        desc = lab.get("description", "")

        _print_progress(i, total, name)

        # Try create
        p = gh_api(
            "POST",
            f"repos/{repo}/labels",
            {"name": name, "color": color, "description": desc},
        )
        if p.returncode == 0:
            created += 1
            continue

        # Update existing (name must be URL-encoded)
        encoded = urllib.parse.quote(name, safe="")
        p2 = gh_api(
            "PATCH",
            f"repos/{repo}/labels/{encoded}",
            {"new_name": name, "color": color, "description": desc},
        )
        if p2.returncode == 0:
            updated += 1
            continue

        # Record failure but continue processing
        error_msg = f"Failed to upsert label: {name}"
        if p.stderr:
            error_msg += f"\n  POST error: {p.stderr.strip()}"
        if p2.stderr:
            error_msg += f"\n  PATCH error: {p2.stderr.strip()}"
        failures.append(error_msg)

    _finish_progress()
    print(f"Done. Created: {created}, Updated: {updated}. Repo: {repo}")

    if failures:
        print(f"\n{len(failures)} label(s) failed:", file=sys.stderr)
        for msg in failures:
            print(msg, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
