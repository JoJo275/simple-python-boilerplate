"""MkDocs hook: rewrite repo-relative links to absolute GitHub URLs.

Links in docs/ that point outside the docs/ directory (e.g. ../../pyproject.toml)
work correctly when reading files on GitHub, but MkDocs can only resolve links
to files within the docs_dir. On the deployed site, these relative links break.

This hook rewrites them at build time to absolute GitHub URLs, so they work in
both contexts without changing any source files.

How it works:
    1. For each page, finds Markdown links targeting ``../`` paths
    2. Resolves the path relative to the page's location in docs/
    3. If the resolved path escapes docs/ (starts with ``..``), rewrites it
       to ``{repo_url}/blob/main/{path}`` (files) or ``tree/main/`` (dirs)

Template users only need to update ``repo_url`` in ``mkdocs.yml`` — all
repo-relative links will point to the correct GitHub repository automatically.

Reference: https://www.mkdocs.org/user-guide/configuration/#hooks
"""

from __future__ import annotations

import posixpath
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page

# Files without extensions that should use blob/ (not tree/).
_EXTENSIONLESS_FILES = frozenset(
    {
        "Containerfile",
        "Dockerfile",
        "Gemfile",
        "LICENSE",
        "Makefile",
        "Procfile",
        "Rakefile",
        "Taskfile",
        "Vagrantfile",
    }
)

# Matches standard Markdown links with relative targets starting with ../
# Captures: [link text](../some/path) or [link text](../some/path#anchor)
_LINK_RE = re.compile(r"\[([^\]]*)\]\((\.\./[^)]*)\)")


def _is_likely_file(path: str) -> bool:
    """Heuristic: determine if a path targets a file (not a directory)."""
    basename = posixpath.basename(path.rstrip("/"))
    return "." in basename or basename in _EXTENSIONLESS_FILES


def _build_github_url(repo_url: str, repo_path: str, fragment: str) -> str:
    """Build a GitHub URL for a repo-root-relative path."""
    clean = repo_path.rstrip("/")
    kind = "blob" if _is_likely_file(clean) else "tree"
    return f"{repo_url}/{kind}/main/{clean}{fragment}"


def on_page_markdown(
    markdown: str,
    *,
    page: Page,
    config: MkDocsConfig,
    files: Files,
) -> str:
    """Rewrite repo-relative links to absolute GitHub URLs."""
    repo_url: str = config.get("repo_url", "").rstrip("/")
    if not repo_url:
        return markdown

    page_dir = posixpath.dirname(page.file.src_path)

    def _rewrite(match: re.Match[str]) -> str:
        text = match.group(1)
        target = match.group(2)

        # Split off fragment (#anchor) if present
        fragment = ""
        if "#" in target:
            target, fragment = target.split("#", 1)
            fragment = f"#{fragment}"

        # Resolve the relative path from the page's directory within docs/
        resolved = posixpath.normpath(posixpath.join(page_dir, target))

        # Only rewrite if the resolved path escapes docs/ (starts with ..)
        if not resolved.startswith(".."):
            return match.group(0)

        # Strip leading ../ segments to get the repo-root-relative path
        repo_path = re.sub(r"^(\.\./)+", "", resolved)
        # Preserve trailing slash for directory links
        if target.endswith("/"):
            repo_path += "/"

        return f"[{text}]({_build_github_url(repo_url, repo_path, fragment)})"

    return _LINK_RE.sub(_rewrite, markdown)
