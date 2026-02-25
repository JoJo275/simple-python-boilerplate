"""Unit tests for scripts/dep_versions.py helper functions."""

from __future__ import annotations

import sys
from pathlib import Path

# scripts/ is not an installed package — add it to sys.path so we can import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

from dep_versions import (
    SCRIPT_VERSION,
    _capitalise,
    _get_req_files,
    _normalise_name,
    _parse_deps_from_toml,
    _update_minimum_specifier,
)

# ---------------------------------------------------------------------------
# _normalise_name
# ---------------------------------------------------------------------------


class TestNormaliseName:
    """Tests for PEP 503 name normalisation."""

    def test_simple_name(self) -> None:
        assert _normalise_name("pytest") == "pytest"

    def test_hyphen_underscore_dot(self) -> None:
        assert _normalise_name("mkdocs-material") == "mkdocs-material"
        assert _normalise_name("mkdocs_material") == "mkdocs-material"
        assert _normalise_name("mkdocs.material") == "mkdocs-material"

    def test_strips_version_constraint(self) -> None:
        assert _normalise_name("requests>=2.28") == "requests"
        assert _normalise_name("click>=8.0") == "click"
        assert _normalise_name("ruff~=0.9.0") == "ruff"

    def test_strips_extras(self) -> None:
        assert _normalise_name("mkdocstrings[python]>=0.27") == "mkdocstrings"

    def test_case_insensitive(self) -> None:
        assert _normalise_name("PyYAML") == "pyyaml"
        assert _normalise_name("MkDocs") == "mkdocs"

    def test_consecutive_separators(self) -> None:
        assert _normalise_name("some--weird__name") == "some-weird-name"


# ---------------------------------------------------------------------------
# _capitalise
# ---------------------------------------------------------------------------


class TestCapitalise:
    """Tests for _capitalise — first-letter-only capitalisation."""

    def test_lowercase_string(self) -> None:
        assert _capitalise("hello world") == "Hello world"

    def test_preserves_interior_case(self) -> None:
        assert _capitalise("pyPI metadata") == "PyPI metadata"

    def test_empty_string(self) -> None:
        assert _capitalise("") == ""

    def test_single_char(self) -> None:
        assert _capitalise("a") == "A"

    def test_already_capitalised(self) -> None:
        assert _capitalise("Already Fine") == "Already Fine"


# ---------------------------------------------------------------------------
# _parse_deps_from_toml
# ---------------------------------------------------------------------------


class TestParseDepsFromToml:
    """Tests for tomllib-based TOML dependency parser."""

    SAMPLE_TOML = """\
[project]
name = "my-project"
dependencies = [
    "requests>=2.28",
    "click>=8.0",
]

[project.optional-dependencies]
test = [
    "pytest",
    "pytest-cov",
]
dev = [
    "my-project[test]",
    "ruff",
    "mypy",
]
"""

    def test_reads_dependencies(self) -> None:
        groups = _parse_deps_from_toml(self.SAMPLE_TOML)
        assert "dependencies" in groups
        assert groups["dependencies"] == ["requests>=2.28", "click>=8.0"]

    def test_reads_optional_dependencies(self) -> None:
        groups = _parse_deps_from_toml(self.SAMPLE_TOML)
        assert "test" in groups
        assert "pytest" in groups["test"]
        assert "pytest-cov" in groups["test"]

    def test_reads_dev_group(self) -> None:
        groups = _parse_deps_from_toml(self.SAMPLE_TOML)
        assert "dev" in groups
        assert "ruff" in groups["dev"]

    def test_no_dependencies_section(self) -> None:
        toml = '[project]\nname = "empty"\n'
        groups = _parse_deps_from_toml(toml)
        assert "dependencies" not in groups

    def test_empty_dependencies(self) -> None:
        toml = '[project]\nname = "empty"\ndependencies = []\n'
        groups = _parse_deps_from_toml(toml)
        assert "dependencies" not in groups  # empty list is falsy

    def test_no_optional_dependencies(self) -> None:
        toml = '[project]\nname = "no-extras"\ndependencies = ["click"]\n'
        groups = _parse_deps_from_toml(toml)
        assert len(groups) == 1
        assert "dependencies" in groups


# ---------------------------------------------------------------------------
# _update_minimum_specifier
# ---------------------------------------------------------------------------


class TestUpdateMinimumSpecifier:
    """Tests for version specifier updates."""

    def test_updates_gte_constraint(self) -> None:
        assert _update_minimum_specifier("ruff>=0.9.0", "0.15.0") == "ruff>=0.15.0"

    def test_updates_compatible_release(self) -> None:
        assert _update_minimum_specifier("mkdocs~=1.6", "1.6.1") == "mkdocs~=1.6.1"

    def test_leaves_exact_pin(self) -> None:
        # == pins are intentional — don't auto-bump them
        assert _update_minimum_specifier("click==8.0.0", "8.1.0") == "click==8.0.0"

    def test_no_constraint(self) -> None:
        # Bare package name — nothing to update
        assert _update_minimum_specifier("pytest", "9.0.2") == "pytest"

    def test_with_extras(self) -> None:
        result = _update_minimum_specifier("mkdocstrings[python]>=0.27", "0.29.1")
        assert result == "mkdocstrings[python]>=0.29.1"

    def test_multiple_constraints(self) -> None:
        # Only the >= part should change
        result = _update_minimum_specifier("mkdocs>=1.6,<2.0", "1.6.1")
        # The >= should be updated, < should be left alone
        assert ">=1.6.1" in result


# ---------------------------------------------------------------------------
# _get_req_files
# ---------------------------------------------------------------------------


class TestGetReqFiles:
    """Tests for lazy requirements file discovery."""

    def test_returns_list_of_paths(self) -> None:
        result = _get_req_files()
        assert isinstance(result, list)
        assert all(isinstance(p, Path) for p in result)

    def test_finds_requirements_txt(self) -> None:
        result = _get_req_files()
        names = [p.name for p in result]
        assert "requirements.txt" in names

    def test_finds_requirements_dev_txt(self) -> None:
        result = _get_req_files()
        names = [p.name for p in result]
        assert "requirements-dev.txt" in names


# ---------------------------------------------------------------------------
# SCRIPT_VERSION
# ---------------------------------------------------------------------------


class TestScriptVersion:
    """Validate version constant is well-formed."""

    def test_version_is_string(self) -> None:
        assert isinstance(SCRIPT_VERSION, str)

    def test_version_format(self) -> None:
        """Version should follow semver-ish X.Y.Z pattern."""
        parts = SCRIPT_VERSION.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)
