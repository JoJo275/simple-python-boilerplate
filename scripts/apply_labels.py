#!/usr/bin/env python3
"""Apply GitHub labels to a repository using GitHub CLI.

Requirements:
  - Python 3
  - GitHub CLI (`gh`) installed and authenticated (`gh auth login`)

Usage:
  scripts/apply_labels.py --set baseline --repo OWNER/REPO
  scripts/apply_labels.py --set extended --repo OWNER/REPO
  scripts/apply_labels.py --set baseline --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True)


def default_repo() -> str | None:
    p = run(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"])
    if p.returncode != 0:
        return None
    return (p.stdout or "").strip() or None

def gh_api(method: str, endpoint: str, fields: dict[str, str]) -> subprocess.CompletedProcess:
    cmd = ["gh", "api", "-X", method, endpoint]
    for k, v in fields.items():
        cmd += ["-f", f"{k}={v}"]
    return run(cmd)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["baseline", "extended"], required=True)
    ap.add_argument("--repo", help="OWNER/REPO; default is current repo")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = args.repo or default_repo()
    if not repo:
        print("Error: could not determine repo. Run inside a repo or pass --repo OWNER/REPO.", file=sys.stderr)
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

    labels = json.loads(spec.read_text(encoding="utf-8"))

    created = updated = 0
    for lab in labels:
        name = lab["name"]
        color = lab["color"].lstrip("#")
        desc = lab.get("description", "")

        if args.dry_run:
            print(f"[DRY] upsert: {name} (#{color}) - {desc}")
            continue

        # Try create
        p = gh_api("POST", f"repos/{repo}/labels", {"name": name, "color": color, "description": desc})
        if p.returncode == 0:
            created += 1
            continue

        # Update existing (name must be URL-encoded)
        encoded = urllib.parse.quote(name, safe="")
        p2 = gh_api("PATCH", f"repos/{repo}/labels/{encoded}", {"new_name": name, "color": color, "description": desc})
        if p2.returncode == 0:
            updated += 1
            continue

        print(f"Failed to upsert label: {name}", file=sys.stderr)
        if p.stderr:
            print(p.stderr.strip(), file=sys.stderr)
        if p2.stderr:
            print(p2.stderr.strip(), file=sys.stderr)
        return 1

    print(f"Done. Created: {created}, Updated: {updated}. Repo: {repo}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
