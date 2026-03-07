"""Unit tests for scripts/customize.py helper functions."""

from __future__ import annotations

import sys
from pathlib import Path

# scripts/ is not an installed package — add it to sys.path so we can import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

from customize import (
    SCRIPT_VERSION,
    _should_process,
    _validate_package_name,
    _validate_project_name,
)

# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


class TestMetadata:
    """Verify module-level metadata."""

    def test_version_is_string(self) -> None:
        assert isinstance(SCRIPT_VERSION, str)

    def test_version_format(self) -> None:
        parts = SCRIPT_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


# ---------------------------------------------------------------------------
# _validate_project_name
# ---------------------------------------------------------------------------


class TestValidateProjectName:
    """Tests for _validate_project_name()."""

    def test_valid_name(self) -> None:
        assert _validate_project_name("my-project") is None

    def test_valid_name_with_numbers(self) -> None:
        assert _validate_project_name("project-123") is None

    def test_empty_name_rejected(self) -> None:
        result = _validate_project_name("")
        assert result is not None  # returns error message

    def test_uppercase_rejected(self) -> None:
        result = _validate_project_name("MyProject")
        assert result is not None

    def test_underscore_rejected(self) -> None:
        result = _validate_project_name("my_project")
        assert result is not None


# ---------------------------------------------------------------------------
# _validate_package_name
# ---------------------------------------------------------------------------


class TestValidatePackageName:
    """Tests for _validate_package_name()."""

    def test_valid_package_name(self) -> None:
        assert _validate_package_name("my_package") is None

    def test_empty_rejected(self) -> None:
        result = _validate_package_name("")
        assert result is not None

    def test_hyphen_rejected(self) -> None:
        result = _validate_package_name("my-package")
        assert result is not None

    def test_starts_with_number_rejected(self) -> None:
        result = _validate_package_name("123package")
        assert result is not None


# ---------------------------------------------------------------------------
# _should_process
# ---------------------------------------------------------------------------


class TestShouldProcess:
    """Tests for _should_process()."""

    def test_python_file_in_repo_accepted(self, project_root: Path) -> None:
        # Use an actual file in the repo that should be processable
        f = project_root / "pyproject.toml"
        assert _should_process(f) is True

    def test_git_dir_rejected(self, project_root: Path) -> None:
        git_config = project_root / ".git" / "config"
        if git_config.exists():
            assert _should_process(git_config) is False

    def test_nonexistent_file_rejected(self, project_root: Path) -> None:
        f = project_root / "nonexistent_abc_xyz.py"
        assert _should_process(f) is False
