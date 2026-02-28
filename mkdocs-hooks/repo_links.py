"""MkDocs hook: rewrite repo-relative links to absolute GitHub URLs.

Links in ``docs/`` that point outside the docs directory (e.g.
``../../pyproject.toml``) work correctly when browsing on GitHub, but MkDocs
can only resolve links to files within ``docs_dir``.  On the deployed site
these relative links would 404.

This hook intercepts the ``on_page_markdown`` event and rewrites them at
build time to absolute GitHub URLs, so they work in both contexts without
changing any source Markdown files.

How it works:
    1. For each page, finds Markdown links whose target starts with ``../``
    2. Resolves the path relative to the page's location within ``docs/``
    3. If the resolved path escapes ``docs/`` (normalised path starts with
       ``..``), rewrites it to ``{repo_url}/blob/main/{path}`` (files) or
       ``tree/main/`` (directories)

Template users only need to set ``repo_url`` in ``mkdocs.yml`` — all
repo-relative links will point to the correct GitHub repository
automatically.

Configuration (optional ``extra`` keys in ``mkdocs.yml``)::

    extra:
      repo_links_default_branch: develop   # default: main
      repo_links_log: true                 # emit INFO per rewrite

Reference:
    https://www.mkdocs.org/user-guide/configuration/#hooks
"""

# TODO (template users): If your default branch is not ``main``, either
#   set ``extra.repo_links_default_branch`` in ``mkdocs.yml`` or change
#   ``_DEFAULT_BRANCH`` below.

from __future__ import annotations

import logging
import posixpath
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page

# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

# Semantic version of this hook — bump when behaviour changes.
HOOK_VERSION = "1.2.0"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_BRANCH = "main"

log = logging.getLogger("mkdocs.hooks.repo_links")

# Files without extensions that should use blob/ (not tree/).
_EXTENSIONLESS_FILES: frozenset[str] = frozenset(
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

# Matches standard Markdown links whose target starts with ../
# Captures: [link text](../some/path) and [link text](../some/path#anchor)
# The negative lookbehind (?<!!) skips image links: ![alt](../path).
_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\((\.\./[^)]*)\)")


def _is_likely_file(path: str) -> bool:
    """Heuristic: determine if *path* targets a file rather than a directory.

    A path is considered a file if its basename contains a dot (extension)
    or matches a known extensionless filename like ``LICENSE``.
    """
    basename = posixpath.basename(path.rstrip("/"))
    return "." in basename or basename in _EXTENSIONLESS_FILES


def _build_github_url(
    repo_url: str,
    repo_path: str,
    suffix: str,
    branch: str,
) -> str:
    """Build a GitHub URL for a repo-root-relative *repo_path*.

    Args:
        repo_url: Repository base URL (no trailing slash).
        repo_path: Path relative to the repository root.
        suffix: Optional query string and/or fragment to append (e.g.
            ``?plain=1#L10`` or ``#my-heading``).
        branch: Git branch name (e.g. ``main``).

    Returns:
        Absolute GitHub URL using ``blob/`` (file) or ``tree/`` (directory).
    """
    clean = repo_path.rstrip("/")
    kind = "blob" if _is_likely_file(clean) else "tree"
    return f"{repo_url}/{kind}/{branch}/{clean}{suffix}"


def on_page_markdown(
    markdown: str,
    *,
    page: Page,
    config: MkDocsConfig,
    files: Files,
) -> str:
    """Rewrite repo-relative links to absolute GitHub URLs.

    Called by MkDocs for every page *before* the Markdown-to-HTML conversion.
    Only links whose resolved path escapes ``docs/`` are rewritten; internal
    cross-references are left untouched.
    """
    repo_url: str = config.get("repo_url", "").rstrip("/")
    if not repo_url:
        return markdown

    extra: dict[str, object] = config.get("extra", {}) or {}
    branch: str = str(extra.get("repo_links_default_branch", _DEFAULT_BRANCH))
    verbose: bool = bool(extra.get("repo_links_log", False))

    page_dir = posixpath.dirname(page.file.src_path)
    rewrite_count = 0

    def _rewrite(match: re.Match[str]) -> str:
        nonlocal rewrite_count
        text = match.group(1)
        target = match.group(2)

        # Split off query string (?key=val) and fragment (#anchor).
        fragment = ""
        query = ""
        if "?" in target:
            target, query_and_rest = target.split("?", 1)
            if "#" in query_and_rest:
                query, frag = query_and_rest.split("#", 1)
                query = f"?{query}"
                fragment = f"#{frag}"
            else:
                query = f"?{query_and_rest}"
        elif "#" in target:
            target, fragment = target.split("#", 1)
            fragment = f"#{fragment}"

        # Resolve the relative path from the page's directory within docs/.
        resolved = posixpath.normpath(posixpath.join(page_dir, target))

        # Only rewrite if the resolved path escapes docs/ (starts with ..).
        if not resolved.startswith(".."):
            return match.group(0)

        # Strip leading ../ segments to get the repo-root-relative path.
        repo_path = re.sub(r"^(\.\./)+", "", resolved)
        # Preserve trailing slash for directory links.
        if target.endswith("/"):
            repo_path += "/"

        suffix = query + fragment
        url = _build_github_url(repo_url, repo_path, suffix, branch)
        rewrite_count += 1

        if verbose:
            log.info(
                "[repo_links] %s: %s -> %s",
                page.file.src_path,
                match.group(2),
                url,
            )

        return f"[{text}]({url})"

    result = _LINK_RE.sub(_rewrite, markdown)

    if rewrite_count and verbose:
        log.info(
            "[repo_links] %s: rewrote %d link(s)",
            page.file.src_path,
            rewrite_count,
        )

    return result
