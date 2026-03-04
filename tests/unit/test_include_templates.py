"""Unit tests for mkdocs-hooks/include_templates.py."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

# mkdocs-hooks/ is not an installed package — add it to sys.path so we can
# import the module directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "mkdocs-hooks"))

from include_templates import (
    _TEMPLATES_DIR,
    HOOK_VERSION,
    on_files,
)

# ---------------------------------------------------------------------------
# Helpers — lightweight fakes for MkDocs types
# ---------------------------------------------------------------------------


def _make_config(
    docs_dir: str | Path = "/docs",
    site_dir: str | Path = "/site",
    use_directory_urls: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a minimal dict that behaves like ``MkDocsConfig``."""
    return {
        "docs_dir": str(docs_dir),
        "site_dir": str(site_dir),
        "use_directory_urls": use_directory_urls,
        "extra": extra or {},
    }


def _make_files(src_paths: list[str] | None = None) -> MagicMock:
    """Create a fake Files collection.

    Each file in the collection has a ``src_path`` attribute.
    """
    files = MagicMock()
    file_objects = []
    for src in src_paths or []:
        f = MagicMock()
        f.src_path = src
        file_objects.append(f)
    files.__iter__ = lambda self: iter(file_objects)
    files.append = MagicMock()
    return files


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


class TestHookVersion:
    """Validate the version constant."""

    def test_version_is_string(self) -> None:
        assert isinstance(HOOK_VERSION, str)

    def test_version_format(self) -> None:
        parts = HOOK_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


class TestTemplatesDir:
    """Validate the templates directory constant."""

    def test_is_string(self) -> None:
        assert isinstance(_TEMPLATES_DIR, str)

    def test_is_templates(self) -> None:
        assert _TEMPLATES_DIR == "templates"


# ---------------------------------------------------------------------------
# on_files — disabled
# ---------------------------------------------------------------------------


class TestOnFilesDisabled:
    """Test the hook when it's disabled via extra config."""

    def test_disabled_returns_files_unchanged(self) -> None:
        files = _make_files()
        config = _make_config(extra={"include_templates": False})
        result = on_files(files, config=config)
        assert result is files

    def test_enabled_by_default(self, tmp_path: Path) -> None:
        """With no extra key, the hook runs (enabled is the default)."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        files = _make_files()
        config = _make_config(docs_dir=docs_dir)
        result = on_files(files, config=config)
        assert result is files


# ---------------------------------------------------------------------------
# on_files — no templates directory
# ---------------------------------------------------------------------------


class TestOnFilesNoTemplatesDir:
    """Test when templates/ directory doesn't exist."""

    def test_returns_files_unchanged(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        # No templates/ subdirectory
        files = _make_files()
        config = _make_config(docs_dir=docs_dir)
        result = on_files(files, config=config)
        assert result is files
        files.append.assert_not_called()


# ---------------------------------------------------------------------------
# on_files — with templates
# ---------------------------------------------------------------------------


class TestOnFilesWithTemplates:
    """Test when templates/ directory exists with files."""

    def test_adds_missing_files(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        tpl_dir = docs_dir / "templates"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "example.md").write_text("# Template")

        files = _make_files([])  # empty collection — template is missing
        config = _make_config(docs_dir=docs_dir, site_dir=tmp_path / "site")

        with patch("mkdocs.structure.files.File") as MockFile:
            MockFile.return_value = MagicMock()
            result = on_files(files, config=config)

        files.append.assert_called_once()
        assert result is files

    def test_skips_already_included_files(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        tpl_dir = docs_dir / "templates"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "example.md").write_text("# Template")

        # File already in collection
        files = _make_files(["templates/example.md"])
        config = _make_config(docs_dir=docs_dir, site_dir=tmp_path / "site")

        result = on_files(files, config=config)
        files.append.assert_not_called()
        assert result is files

    def test_adds_multiple_missing_files(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        tpl_dir = docs_dir / "templates"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "a.md").write_text("A")
        (tpl_dir / "b.md").write_text("B")

        files = _make_files([])
        config = _make_config(docs_dir=docs_dir, site_dir=tmp_path / "site")

        with patch("mkdocs.structure.files.File") as MockFile:
            MockFile.return_value = MagicMock()
            on_files(files, config=config)

        assert files.append.call_count == 2

    def test_skips_subdirectories(self, tmp_path: Path) -> None:
        """Directories inside templates/ should not be added (only files)."""
        docs_dir = tmp_path / "docs"
        tpl_dir = docs_dir / "templates"
        sub_dir = tpl_dir / "subdir"
        sub_dir.mkdir(parents=True)
        # Only a directory, no files
        files = _make_files([])
        config = _make_config(docs_dir=docs_dir, site_dir=tmp_path / "site")
        on_files(files, config=config)
        files.append.assert_not_called()

    def test_nested_files_added(self, tmp_path: Path) -> None:
        """Files in subdirectories of templates/ should be added."""
        docs_dir = tmp_path / "docs"
        sub = docs_dir / "templates" / "subdir"
        sub.mkdir(parents=True)
        (sub / "nested.md").write_text("Nested")

        files = _make_files([])
        config = _make_config(docs_dir=docs_dir, site_dir=tmp_path / "site")

        with patch("mkdocs.structure.files.File") as MockFile:
            MockFile.return_value = MagicMock()
            on_files(files, config=config)

        files.append.assert_called_once()
