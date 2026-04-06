"""CI/CD status collector — workflow files and configuration.

Discovers:
- GitHub Actions workflow files in .github/workflows/
- Workflow names, triggers, and SHA-pinned status
- CI configuration presence (codecov, dependabot, release-please)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from _env_collectors._base import BaseCollector

_tier = None


def _get_tier():  # type: ignore[no-untyped-def]
    global _tier
    if _tier is None:
        from _env_collectors import Tier

        _tier = Tier
    return _tier


def _parse_workflow_files(repo_root: Path) -> list[dict[str, str]]:
    """Parse GitHub Actions workflow YAML files."""
    workflows_dir = repo_root / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return []

    workflows: list[dict[str, str]] = []
    for f in sorted(workflows_dir.glob("*.yml")):
        if f.name.startswith("."):
            continue
        try:
            content = f.read_text(encoding="utf-8")
            name = ""
            triggers: list[str] = []

            # Extract workflow name
            name_match = re.search(
                r"^name:\s*['\"]?(.+?)['\"]?\s*$", content, re.MULTILINE
            )
            if name_match:
                name = name_match.group(1).strip()

            # Extract triggers (on: section)
            on_match = re.search(r"^on:\s*(.+)$", content, re.MULTILINE)
            if on_match:
                trigger_val = on_match.group(1).strip()
                if trigger_val and trigger_val != "":
                    triggers = [trigger_val]

            # Multi-line on: block
            on_block = re.findall(r"^on:\s*\n((?:\s+\w.*\n?)+)", content, re.MULTILINE)
            if on_block:
                for line in on_block[0].splitlines():
                    t = line.strip().rstrip(":")
                    if t and not t.startswith("#"):
                        triggers.append(t)

            # Count uses: lines (action references)
            action_count = len(re.findall(r"uses:", content))

            # Check SHA-pinned
            uses_lines = re.findall(r"uses:\s*(.+)", content)
            sha_pinned = 0
            tag_pinned = 0
            for use in uses_lines:
                use = use.strip()
                if "@" in use:
                    ref = use.split("@")[-1].strip()
                    if re.match(r"^[0-9a-f]{40}$", ref):
                        sha_pinned += 1
                    else:
                        tag_pinned += 1

            workflows.append(
                {
                    "file": f.name,
                    "name": name or f.stem,
                    "triggers": ", ".join(triggers[:3]) if triggers else "—",
                    "actions": action_count,
                    "sha_pinned": sha_pinned,
                    "tag_pinned": tag_pinned,
                }
            )
        except OSError:
            continue

    return workflows


def _detect_ci_configs(repo_root: Path) -> dict[str, bool]:
    """Detect presence of CI-related config files."""
    configs = {
        "codecov": (repo_root / "codecov.yml").is_file()
        or (repo_root / ".codecov.yml").is_file(),
        "dependabot": (repo_root / ".github" / "dependabot.yml").is_file(),
        "release_please": (repo_root / "release-please-config.json").is_file(),
        "renovate": (repo_root / "renovate.json").is_file()
        or (repo_root / ".renovaterc.json").is_file(),
        "github_actions": (repo_root / ".github" / "workflows").is_dir(),
    }
    return configs


class CiCdStatusCollector(BaseCollector):
    """Collect CI/CD workflow configuration and status."""

    name = "ci_cd_status"
    timeout = 10.0

    @property
    def tier(self):  # type: ignore[override]
        return _get_tier().STANDARD

    def collect(self) -> dict[str, Any]:
        from _imports import find_repo_root

        repo_root = find_repo_root()

        workflows = _parse_workflow_files(repo_root)
        ci_configs = _detect_ci_configs(repo_root)

        total_actions = sum(w.get("actions", 0) for w in workflows)
        total_sha = sum(w.get("sha_pinned", 0) for w in workflows)
        total_tag = sum(w.get("tag_pinned", 0) for w in workflows)

        return {
            "workflows": workflows,
            "total_workflows": len(workflows),
            "ci_configs": ci_configs,
            "total_actions": total_actions,
            "sha_pinned_count": total_sha,
            "tag_pinned_count": total_tag,
            "sha_pinned_pct": round(total_sha / max(total_sha + total_tag, 1) * 100),
        }
