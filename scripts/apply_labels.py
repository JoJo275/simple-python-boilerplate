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
import subprocess  # nosec B404
import sys
import urllib.parse

from _imports import find_repo_root, import_sibling

ProgressBar = import_sibling("_progress").ProgressBar

SCRIPT_VERSION = "1.3.0"

ROOT = find_repo_root()


# TODO (template users): If you need to authenticate with a GitHub
#   App token instead of a personal gh CLI session, update gh_exists()
#   and the gh_api() helper to accept a --token flag.
def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
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


# TODO (template users): If your workflow needs retry logic or rate-limit
#   handling for GitHub API calls, wrap gh_api() with a retry decorator.
def gh_api(
    method: str, endpoint: str, fields: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    cmd = ["gh", "api", "-X", method, endpoint]
    for k, v in fields.items():
        cmd += ["-f", f"{k}={v}"]
    return run(cmd)


def _get_existing_label(repo: str, encoded_name: str) -> dict[str, str] | None:
    """Fetch an existing label from the GitHub API.

    Returns the label dict (name, color, description) or None on failure.
    """
    p = run(["gh", "api", f"repos/{repo}/labels/{encoded_name}"])
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)  # type: ignore[no-any-return]
    except (json.JSONDecodeError, TypeError):
        return None


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

    created = updated = up_to_date = 0
    failures: list[str] = []
    bar = ProgressBar(total=total, label="Applying labels")

    for lab in labels:
        name = lab["name"]
        color = lab["color"].lstrip("#")
        desc = lab.get("description", "")

        bar.update(name)

        # Try create
        p = gh_api(
            "POST",
            f"repos/{repo}/labels",
            {"name": name, "color": color, "description": desc},
        )
        if p.returncode == 0:
            created += 1
            continue

        # Label already exists — check whether it actually needs updating
        encoded = urllib.parse.quote(name, safe="")
        existing = _get_existing_label(repo, encoded)

        if existing is not None:
            # Compare current vs desired (GitHub returns color without '#')
            cur_color = (existing.get("color") or "").lstrip("#").lower()
            cur_desc = existing.get("description") or ""
            if cur_color == color.lower() and cur_desc == desc:
                up_to_date += 1
                continue

        # Values differ (or couldn't fetch) — PATCH to update
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

    bar.finish()
    parts = []
    if created:
        parts.append(f"{created} created")
    if updated:
        parts.append(f"{updated} updated")
    if up_to_date:
        parts.append(f"{up_to_date} already up to date")
    summary = ", ".join(parts) if parts else "no changes"
    print(f"Done: {summary}. Repo: {repo}")

    if failures:
        print(f"\n{len(failures)} label(s) failed:", file=sys.stderr)
        for msg in failures:
            print(msg, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
