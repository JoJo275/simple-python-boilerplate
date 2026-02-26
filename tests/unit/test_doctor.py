"""Unit tests for scripts/doctor.py helper and formatting functions."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# scripts/ is not an installed package — add it to sys.path so we can import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

from doctor import (
    SCRIPT_VERSION,
    _git_info,
    check_path_exists,
    format_json,
    format_markdown,
    format_plain,
    get_package_version,
    get_version,
)

# ---------------------------------------------------------------------------
# SCRIPT_VERSION
# ---------------------------------------------------------------------------


class TestScriptVersion:
    """Validate version constant is well-formed."""

    def test_version_is_string(self) -> None:
        assert isinstance(SCRIPT_VERSION, str)

    def test_version_format(self) -> None:
        parts = SCRIPT_VERSION.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)


# ---------------------------------------------------------------------------
# get_version
# ---------------------------------------------------------------------------


class TestGetVersion:
    """Tests for CLI version detection."""

    def test_returns_not_found_for_missing_command(self) -> None:
        with patch("doctor.shutil.which", return_value=None):
            assert get_version(["nonexistent-tool", "--version"]) == "not found"

    def test_returns_stdout_first_line(self) -> None:
        mock_result = MagicMock()
        mock_result.stdout = "tool 1.2.3\nsome other info"
        mock_result.stderr = ""

        with (
            patch("doctor.shutil.which", return_value="/usr/bin/tool"),
            patch("doctor.subprocess.run", return_value=mock_result),
        ):
            result = get_version(["tool", "--version"])

        assert result == "tool 1.2.3"

    def test_falls_back_to_stderr(self) -> None:
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "tool 2.0.0 from stderr"

        with (
            patch("doctor.shutil.which", return_value="/usr/bin/tool"),
            patch("doctor.subprocess.run", return_value=mock_result),
        ):
            result = get_version(["tool", "--version"])

        assert result == "tool 2.0.0 from stderr"

    def test_returns_error_on_timeout(self) -> None:
        with (
            patch("doctor.shutil.which", return_value="/usr/bin/tool"),
            patch(
                "doctor.subprocess.run",
                side_effect=subprocess.TimeoutExpired(cmd="tool", timeout=10),
            ),
        ):
            assert get_version(["tool", "--version"]) == "error"

    def test_returns_error_on_os_error(self) -> None:
        with (
            patch("doctor.shutil.which", return_value="/usr/bin/tool"),
            patch("doctor.subprocess.run", side_effect=OSError("permission denied")),
        ):
            assert get_version(["tool", "--version"]) == "error"


# ---------------------------------------------------------------------------
# get_package_version
# ---------------------------------------------------------------------------


class TestGetPackageVersion:
    """Tests for installed package version lookup."""

    def test_returns_version_for_installed_package(self) -> None:
        # pytest is always installed in the test environment
        result = get_package_version("pytest")
        assert result != "not installed"
        assert "." in result  # version string contains dots

    def test_returns_not_installed_for_missing_package(self) -> None:
        assert get_package_version("nonexistent-pkg-xyz-123") == "not installed"


# ---------------------------------------------------------------------------
# check_path_exists
# ---------------------------------------------------------------------------


class TestCheckPathExists:
    """Tests for path existence checker."""

    def test_returns_directory_for_dir(self, tmp_path: Path) -> None:
        assert check_path_exists(tmp_path) == "directory"

    def test_returns_file_for_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello")
        assert check_path_exists(f) == "file"

    def test_returns_missing_for_nonexistent(self, tmp_path: Path) -> None:
        assert check_path_exists(tmp_path / "nope") == "missing"


# ---------------------------------------------------------------------------
# format_plain
# ---------------------------------------------------------------------------

SAMPLE_INFO: dict[str, str | dict[str, str]] = {
    "timestamp": "2026-02-25T12:00:00+00:00",
    "system": {
        "os": "Windows 10",
        "python_version": "3.13.5",
    },
    "tools": {
        "hatch": "Hatch, version 1.14.0",
        "git": "git version 2.47.1",
    },
}


class TestFormatPlain:
    """Tests for plain-text formatting."""

    def test_contains_header(self) -> None:
        output = format_plain(SAMPLE_INFO)
        assert "DIAGNOSTICS REPORT" in output

    def test_contains_section_names(self) -> None:
        output = format_plain(SAMPLE_INFO)
        assert "[TIMESTAMP]" in output
        assert "[SYSTEM]" in output
        assert "[TOOLS]" in output

    def test_contains_values(self) -> None:
        output = format_plain(SAMPLE_INFO)
        assert "python_version: 3.13.5" in output
        assert "Windows 10" in output

    def test_scalar_values_rendered(self) -> None:
        output = format_plain(SAMPLE_INFO)
        assert "2026-02-25T12:00:00+00:00" in output


# ---------------------------------------------------------------------------
# format_markdown
# ---------------------------------------------------------------------------


class TestFormatMarkdown:
    """Tests for markdown formatting."""

    def test_wraps_in_details_tag(self) -> None:
        output = format_markdown(SAMPLE_INFO)
        assert output.startswith("<details>")
        assert "</details>" in output

    def test_contains_code_block(self) -> None:
        output = format_markdown(SAMPLE_INFO)
        assert "```" in output

    def test_contains_values(self) -> None:
        output = format_markdown(SAMPLE_INFO)
        assert "python_version: 3.13.5" in output


# ---------------------------------------------------------------------------
# format_json
# ---------------------------------------------------------------------------


class TestFormatJson:
    """Tests for JSON formatting."""

    def test_valid_json(self) -> None:
        output = format_json(SAMPLE_INFO)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_roundtrips_data(self) -> None:
        output = format_json(SAMPLE_INFO)
        parsed = json.loads(output)
        assert parsed["timestamp"] == "2026-02-25T12:00:00+00:00"
        assert parsed["system"]["python_version"] == "3.13.5"

    def test_pretty_printed(self) -> None:
        output = format_json(SAMPLE_INFO)
        # json.dumps with indent=2 produces multi-line output
        assert "\n" in output


# ---------------------------------------------------------------------------
# _git_info (mocked)
# ---------------------------------------------------------------------------


class TestGitInfo:
    """Tests for git repository info collection."""

    def test_returns_dict(self) -> None:
        result = _git_info()
        assert isinstance(result, dict)

    def test_contains_expected_keys(self) -> None:
        result = _git_info()
        # If git is available (it should be in dev), we get branch/commit/dirty
        if "status" not in result:  # git found
            assert "branch" in result
            assert "commit" in result
            assert "dirty" in result

    def test_returns_status_when_git_missing(self) -> None:
        with patch("doctor.shutil.which", return_value=None):
            result = _git_info()

        assert result == {"status": "git not found"}

    def test_handles_subprocess_failure(self) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with (
            patch("doctor.shutil.which", return_value="/usr/bin/git"),
            patch("doctor.subprocess.run", return_value=mock_result),
        ):
            result = _git_info()

        assert result["branch"] == "unknown"
        assert result["commit"] == "unknown"
