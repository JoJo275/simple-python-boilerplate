"""Unit tests for scripts/workflow_versions.py."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# scripts/ is not an installed package — add it to sys.path so we can import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

from workflow_versions import (
    _USES_RE,
    SCRIPT_VERSION,
    _build_parser,
    _Colors,
    _repo_slug,
    _shorten_description,
    _unique_by_slug,
    scan_workflows,
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
# _USES_RE
# ---------------------------------------------------------------------------


class TestUsesRegex:
    """Tests for the ``uses:`` line regex."""

    def test_simple_action(self) -> None:
        sha = "a" * 40
        line = f"      - uses: actions/checkout@{sha} # v4.2.0"
        m = _USES_RE.match(line)
        assert m is not None
        assert m.group("action") == "actions/checkout"
        assert m.group("ref") == sha
        assert "v4.2.0" in m.group("trail")

    def test_sub_path_action(self) -> None:
        sha = "a" * 40
        line = f"      uses: github/codeql-action/init@{sha}"
        m = _USES_RE.match(line)
        assert m is not None
        assert m.group("action") == "github/codeql-action/init"

    def test_no_comment(self) -> None:
        sha = "a" * 40
        line = f"      uses: actions/upload-artifact@{sha}"
        m = _USES_RE.match(line)
        assert m is not None
        assert m.group("trail").strip() == ""

    def test_description_with_version_in_parens(self) -> None:
        sha = "a" * 40
        line = f"      - uses: actions/checkout@{sha} # Checkout code (v4.2.0)"
        m = _USES_RE.match(line)
        assert m is not None
        assert "v4.2.0" in m.group("trail")

    def test_non_sha_ref_does_not_match(self) -> None:
        line = "      uses: actions/checkout@v4"
        m = _USES_RE.match(line)
        assert m is None

    def test_short_sha_does_not_match(self) -> None:
        line = "      uses: actions/checkout@abc123"
        m = _USES_RE.match(line)
        assert m is None


# ---------------------------------------------------------------------------
# _repo_slug
# ---------------------------------------------------------------------------


class TestRepoSlug:
    """Tests for stripping sub-path from action references."""

    def test_simple_action(self) -> None:
        assert _repo_slug("actions/checkout") == "actions/checkout"

    def test_sub_path_action(self) -> None:
        assert _repo_slug("github/codeql-action/init") == "github/codeql-action"

    def test_deep_sub_path(self) -> None:
        assert _repo_slug("owner/repo/a/b/c") == "owner/repo"


# ---------------------------------------------------------------------------
# _shorten_description
# ---------------------------------------------------------------------------


class TestShortenDescription:
    """Tests for action description shortening."""

    def test_strips_this_action_prefix(self) -> None:
        result = _shorten_description("This action checks out your repository")
        assert not result.startswith("This action")
        assert "checks out" in result.lower()

    def test_strips_github_action_prefix(self) -> None:
        result = _shorten_description("A GitHub Action for running tests")
        assert not result.startswith("A GitHub Action")
        assert "running tests" in result.lower()

    def test_takes_first_sentence(self) -> None:
        result = _shorten_description("Uploads artifacts. This is extra info.")
        assert "extra" not in result

    def test_capitalises_first_letter(self) -> None:
        result = _shorten_description("checks out code")
        assert result[0].isupper()

    def test_truncates_long_descriptions(self) -> None:
        long_desc = "A" * 60
        result = _shorten_description(long_desc)
        assert len(result) <= 51  # 47 + "…" = 48, or word break

    def test_strips_trailing_punctuation(self) -> None:
        result = _shorten_description("Upload artifacts.")
        assert not result.endswith(".")

    def test_empty_string(self) -> None:
        assert _shorten_description("") == ""

    def test_short_description_unchanged(self) -> None:
        result = _shorten_description("Run tests")
        assert result == "Run tests"


# ---------------------------------------------------------------------------
# _unique_by_slug
# ---------------------------------------------------------------------------


class TestUniqueBySlug:
    """Tests for the slug-based deduplication helper."""

    def test_deduplicates(self) -> None:
        rows = [
            {"action": "actions/checkout", "file": "a.yml"},
            {"action": "actions/checkout", "file": "b.yml"},
            {"action": "actions/upload-artifact", "file": "a.yml"},
        ]
        result = _unique_by_slug(rows)
        assert len(result) == 2
        actions = [r["action"] for r in result]
        assert "actions/checkout" in actions
        assert "actions/upload-artifact" in actions

    def test_keeps_first_occurrence(self) -> None:
        rows = [
            {"action": "actions/checkout", "file": "first.yml"},
            {"action": "actions/checkout", "file": "second.yml"},
        ]
        result = _unique_by_slug(rows)
        assert result[0]["file"] == "first.yml"

    def test_sub_path_deduplicates_by_repo(self) -> None:
        rows = [
            {"action": "github/codeql-action/init", "file": "a.yml"},
            {
                "action": "github/codeql-action/analyze",
                "file": "a.yml",
            },
        ]
        result = _unique_by_slug(rows)
        assert len(result) == 1

    def test_empty_list(self) -> None:
        assert _unique_by_slug([]) == []


# ---------------------------------------------------------------------------
# _Colors
# ---------------------------------------------------------------------------


class TestColors:
    """Tests for the color support class."""

    def test_enabled_wraps_text(self) -> None:
        c = _Colors(enabled=True)
        result = c.red("error")
        assert "\033[31m" in result
        assert "\033[0m" in result
        assert "error" in result

    def test_disabled_returns_plain_text(self) -> None:
        c = _Colors(enabled=False)
        assert c.red("error") == "error"
        assert c.green("ok") == "ok"
        assert c.bold("title") == "title"

    def test_all_color_methods(self) -> None:
        c = _Colors(enabled=True)
        for method in ("bold", "dim", "red", "green", "yellow", "blue", "cyan"):
            result = getattr(c, method)("test")
            assert "test" in result
            assert "\033[" in result

    def test_auto_detect_respects_no_color_env(self) -> None:
        with patch.dict("os.environ", {"NO_COLOR": "1"}, clear=False):
            c = _Colors()
            assert c.enabled is False

    def test_auto_detect_respects_force_color_env(self) -> None:
        with patch.dict(
            "os.environ",
            {"FORCE_COLOR": "1"},
            clear=False,
        ):
            # Remove NO_COLOR if present
            env = dict(os.environ)
            env.pop("NO_COLOR", None)
            env["FORCE_COLOR"] = "1"
            with patch.dict("os.environ", env, clear=True):
                c = _Colors()
                assert c.enabled is True


# ---------------------------------------------------------------------------
# _build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    """Tests for CLI argument parser."""

    def test_version_flag(self) -> None:
        parser = _build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0

    def test_show_defaults(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["show"])
        assert args.command == "show"
        assert args.offline is False
        assert args.json_output is False

    def test_show_offline(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["show", "--offline"])
        assert args.offline is True

    def test_show_json(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["show", "--json"])
        assert args.json_output is True

    def test_update_comments_command(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["update-comments"])
        assert args.command == "update-comments"

    def test_upgrade_with_action_and_version(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["upgrade", "actions/checkout", "v6.1.0"])
        assert args.command == "upgrade"
        assert args.action == "actions/checkout"
        assert args.version == "v6.1.0"

    def test_upgrade_without_args(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["upgrade"])
        assert args.action is None
        assert args.version is None

    def test_no_command_defaults_to_none(self) -> None:
        parser = _build_parser()
        args = parser.parse_args([])
        assert args.command is None

    def test_color_flag(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["--color", "show"])
        assert args.color is True

    def test_no_color_flag(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["--no-color", "show"])
        assert args.color is False

    def test_color_default_is_none(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["show"])
        assert args.color is None

    def test_upgrade_dry_run_flag(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["upgrade", "--dry-run"])
        assert args.dry_run is True

    def test_upgrade_dry_run_default(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["upgrade"])
        assert args.dry_run is False


# ---------------------------------------------------------------------------
# scan_workflows (offline / mocked)
# ---------------------------------------------------------------------------


class TestScanWorkflows:
    """Tests for workflow scanning with mocked filesystem."""

    def test_no_workflows_dir(self, tmp_path: Path) -> None:
        with patch("workflow_versions.WORKFLOWS_DIR", tmp_path / "nope"):
            assert scan_workflows(resolve_tags=False) == []

    def test_scans_uses_lines(self, tmp_path: Path) -> None:
        wf_dir = tmp_path / "workflows"
        wf_dir.mkdir()
        sha = "a" * 40
        content = (
            "jobs:\n"
            "  build:\n"
            "    steps:\n"
            f"      - uses: actions/checkout@{sha} # v4.2.0\n"
        )
        (wf_dir / "test.yml").write_text(content)

        with patch("workflow_versions.WORKFLOWS_DIR", wf_dir):
            rows = scan_workflows(resolve_tags=False, check_latest=False)

        assert len(rows) == 1
        assert rows[0]["action"] == "actions/checkout"
        assert rows[0]["sha"] == sha
        assert rows[0]["comment_tag"] == "v4.2.0"

    def test_detects_description_with_parens(self, tmp_path: Path) -> None:
        wf_dir = tmp_path / "workflows"
        wf_dir.mkdir()
        sha = "b" * 40
        content = (
            "jobs:\n"
            "  build:\n"
            "    steps:\n"
            f"      - uses: actions/checkout@{sha}"
            " # Checkout code (v4.2.0)\n"
        )
        (wf_dir / "ci.yml").write_text(content)

        with patch("workflow_versions.WORKFLOWS_DIR", wf_dir):
            rows = scan_workflows(resolve_tags=False, check_latest=False)

        assert rows[0]["comment_tag"] == "v4.2.0"
        assert rows[0]["has_description"] == "yes"

    def test_detects_missing_comment(self, tmp_path: Path) -> None:
        wf_dir = tmp_path / "workflows"
        wf_dir.mkdir()
        sha = "c" * 40
        content = f"      uses: actions/checkout@{sha}\n"
        (wf_dir / "ci.yml").write_text(content)

        with patch("workflow_versions.WORKFLOWS_DIR", wf_dir):
            rows = scan_workflows(resolve_tags=False, check_latest=False)

        assert rows[0]["comment_tag"] is None

    def test_multiple_actions_across_files(self, tmp_path: Path) -> None:
        wf_dir = tmp_path / "workflows"
        wf_dir.mkdir()
        sha1 = "a" * 40
        sha2 = "b" * 40
        (wf_dir / "a.yml").write_text(f"      uses: actions/checkout@{sha1} # v4\n")
        (wf_dir / "b.yml").write_text(
            f"      uses: actions/upload-artifact@{sha2} # v3\n"
        )

        with patch("workflow_versions.WORKFLOWS_DIR", wf_dir):
            rows = scan_workflows(resolve_tags=False, check_latest=False)

        assert len(rows) == 2
        actions = {r["action"] for r in rows}
        assert "actions/checkout" in actions
        assert "actions/upload-artifact" in actions


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    """Integration-style tests for the main entry point."""

    def test_returns_1_when_no_workflows_dir(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from workflow_versions import main

        with (
            patch(
                "workflow_versions.WORKFLOWS_DIR",
                tmp_path / "missing",
            ),
            patch("sys.argv", ["workflow_versions", "show"]),
        ):
            ret = main()
        assert ret == 1
        assert "No workflows directory" in capsys.readouterr().out

    def test_show_json_empty(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from workflow_versions import main

        wf_dir = tmp_path / "workflows"
        wf_dir.mkdir()

        with (
            patch("workflow_versions.WORKFLOWS_DIR", wf_dir),
            patch(
                "sys.argv",
                ["workflow_versions", "show", "--json"],
            ),
        ):
            ret = main()
        assert ret == 0
        out = capsys.readouterr().out
        # Extract JSON array from output (skip header line)
        json_start = out.index("[")
        output = json.loads(out[json_start:])
        assert output == []

    def test_show_json_with_actions(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from workflow_versions import main

        wf_dir = tmp_path / "workflows"
        wf_dir.mkdir()
        sha = "d" * 40
        (wf_dir / "ci.yml").write_text(f"      uses: actions/checkout@{sha} # v4.2.0\n")

        with (
            patch("workflow_versions.WORKFLOWS_DIR", wf_dir),
            patch(
                "sys.argv",
                [
                    "workflow_versions",
                    "show",
                    "--json",
                    "--offline",
                ],
            ),
        ):
            ret = main()
        assert ret == 0
        out = capsys.readouterr().out
        # Extract JSON (skip the header line)
        json_start = out.index("[")
        data = json.loads(out[json_start:])
        assert len(data) == 1
        assert data[0]["action"] == "actions/checkout"
        assert data[0]["comment_tag"] == "v4.2.0"

    def test_show_returns_0(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from workflow_versions import main

        wf_dir = tmp_path / "workflows"
        wf_dir.mkdir()
        sha = "e" * 40
        (wf_dir / "ci.yml").write_text(f"      uses: actions/checkout@{sha} # v4.2.0\n")

        with (
            patch("workflow_versions.WORKFLOWS_DIR", wf_dir),
            patch(
                "sys.argv",
                ["workflow_versions", "show", "--offline"],
            ),
        ):
            ret = main()
        assert ret == 0
