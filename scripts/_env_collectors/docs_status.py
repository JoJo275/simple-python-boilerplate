"""Documentation status collector — MkDocs config, broken links, ADRs.

Discovers:
- MkDocs configuration and build readiness
- Documentation file inventory
- ADR count and status
- Broken internal links (basic check)
"""

from __future__ import annotations

import re
import shutil
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


def _parse_mkdocs_config(repo_root: Path) -> dict[str, Any]:
    """Parse mkdocs.yml for config info."""
    mkdocs_file = repo_root / "mkdocs.yml"
    if not mkdocs_file.is_file():
        return {"found": False}

    try:
        content = mkdocs_file.read_text(encoding="utf-8")
        site_name = ""
        theme = ""

        name_match = re.search(
            r"^site_name:\s*['\"]?(.+?)['\"]?\s*$", content, re.MULTILINE
        )
        if name_match:
            site_name = name_match.group(1).strip()

        theme_match = re.search(
            r"name:\s*['\"]?(material|readthedocs|mkdocs)['\"]?", content
        )
        if theme_match:
            theme = theme_match.group(1)

        # Count nav entries
        nav_count = len(re.findall(r"^\s+-\s+", content, re.MULTILINE))

        # Check for plugins
        plugins = re.findall(r"^\s+-\s+(\w+)", content, re.MULTILINE)

        return {
            "found": True,
            "site_name": site_name,
            "theme": theme,
            "nav_entries": nav_count,
            "plugins": plugins[:10],
        }
    except OSError:
        return {"found": False}


def _scan_docs_directory(repo_root: Path) -> dict[str, Any]:
    """Scan docs/ directory for inventory."""
    docs_dir = repo_root / "docs"
    if not docs_dir.is_dir():
        return {"found": False, "files": [], "total_files": 0}

    md_files: list[str] = []
    other_files: list[str] = []
    total_size = 0

    try:
        for f in docs_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(repo_root))
                total_size += f.stat().st_size
                if f.suffix == ".md":
                    md_files.append(rel)
                else:
                    other_files.append(rel)
    except OSError:
        pass

    return {
        "found": True,
        "markdown_files": len(md_files),
        "other_files": len(other_files),
        "total_files": len(md_files) + len(other_files),
        "total_size_kb": round(total_size / 1024, 1),
    }


def _scan_adrs(repo_root: Path) -> dict[str, Any]:
    """Scan ADR directory for architecture decision records."""
    adr_dir = repo_root / "docs" / "adr"
    if not adr_dir.is_dir():
        return {"found": False, "count": 0, "adrs": []}

    adrs: list[dict[str, str]] = []
    try:
        for f in sorted(adr_dir.glob("*.md")):
            if f.name.startswith("_") or f.name == "README.md":
                continue
            # Extract title from first heading
            title = f.stem
            try:
                content = f.read_text(encoding="utf-8")
                heading = re.search(r"^#\s+(.+)", content, re.MULTILINE)
                if heading:
                    title = heading.group(1).strip()
            except OSError:
                pass
            adrs.append({"file": f.name, "title": title})
    except OSError:
        pass

    return {
        "found": True,
        "count": len(adrs),
        "adrs": adrs[:20],  # Show first 20
        "total": len(adrs),
    }


def _check_broken_links(repo_root: Path) -> list[dict[str, str]]:
    """Basic check for broken internal markdown links."""
    docs_dir = repo_root / "docs"
    if not docs_dir.is_dir():
        return []

    broken: list[dict[str, str]] = []
    try:
        for md_file in docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8", errors="replace")
            # Find relative markdown links
            for match in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", content):
                target = match.group(2)
                # Skip external URLs, anchors, and template variables
                if target.startswith(("http", "#", "mailto:", "{{", "/")):
                    continue
                # Strip anchor from target
                target_path = target.split("#")[0]
                if not target_path:
                    continue
                resolved = (md_file.parent / target_path).resolve()
                if not resolved.exists():
                    broken.append(
                        {
                            "file": str(md_file.relative_to(repo_root)),
                            "link": target,
                            "text": match.group(1)[:40],
                        }
                    )
    except OSError:
        pass

    return broken[:20]  # Limit results


class DocsStatusCollector(BaseCollector):
    """Collect documentation status and health information."""

    name = "docs_status"
    timeout = 15.0

    @property
    def tier(self):  # type: ignore[override]
        return _get_tier().STANDARD

    def collect(self) -> dict[str, Any]:
        from _imports import find_repo_root

        repo_root = find_repo_root()

        mkdocs = _parse_mkdocs_config(repo_root)
        docs_scan = _scan_docs_directory(repo_root)
        adrs = _scan_adrs(repo_root)
        broken_links = _check_broken_links(repo_root)
        mkdocs_available = shutil.which("mkdocs") is not None

        return {
            "mkdocs": mkdocs,
            "mkdocs_available": mkdocs_available,
            "docs": docs_scan,
            "adrs": adrs,
            "broken_links": broken_links,
            "broken_link_count": len(broken_links),
        }
