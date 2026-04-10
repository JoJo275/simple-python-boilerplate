"""Tests for entry_points.py — script wrapper entry points.

Tests _run_script, _run_dashboard, and backward-compat re-export modules.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

# ── _run_script ──────────────────────────────────────────────


class TestRunScript:
    """Tests for _run_script() subprocess launcher."""

    def test_run_script_missing_script_exits_1(self, tmp_path):
        from simple_python_boilerplate.entry_points import _run_script

        with (
            patch(
                "simple_python_boilerplate.entry_points._BUNDLED_SCRIPTS",
                tmp_path,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            _run_script("nonexistent.py")
        assert exc_info.value.code == 1

    def test_run_script_calls_subprocess(self, tmp_path):
        from simple_python_boilerplate.entry_points import _run_script

        script = tmp_path / "test_script.py"
        script.write_text("print('hello')")

        with (
            patch(
                "simple_python_boilerplate.entry_points._BUNDLED_SCRIPTS",
                tmp_path,
            ),
            patch("sys.argv", ["spb-test"]),
            patch("subprocess.call", return_value=0) as mock_call,
            pytest.raises(SystemExit) as exc_info,
        ):
            _run_script("test_script.py")

        assert exc_info.value.code == 0
        args = mock_call.call_args
        assert str(script) in args[0][0][1]

    def test_run_script_sets_spb_repo_root(self, tmp_path):
        from simple_python_boilerplate.entry_points import _run_script

        script = tmp_path / "s.py"
        script.write_text("")

        with (
            patch(
                "simple_python_boilerplate.entry_points._BUNDLED_SCRIPTS",
                tmp_path,
            ),
            patch("sys.argv", ["cmd"]),
            patch("subprocess.call", return_value=0) as mock_call,
            pytest.raises(SystemExit),
        ):
            _run_script("s.py")

        env = mock_call.call_args[1].get("env") or mock_call.call_args.kwargs.get(
            "env", {}
        )
        assert "SPB_REPO_ROOT" in env

    def test_run_script_forwards_args(self, tmp_path):
        from simple_python_boilerplate.entry_points import _run_script

        script = tmp_path / "s.py"
        script.write_text("")

        with (
            patch(
                "simple_python_boilerplate.entry_points._BUNDLED_SCRIPTS",
                tmp_path,
            ),
            patch("sys.argv", ["cmd", "--flag", "value"]),
            patch("subprocess.call", return_value=0) as mock_call,
            pytest.raises(SystemExit),
        ):
            _run_script("s.py")

        cmd_list = mock_call.call_args[0][0]
        assert "--flag" in cmd_list
        assert "value" in cmd_list


# ── _run_dashboard ───────────────────────────────────────────


class TestRunDashboard:
    """Tests for _run_dashboard() subprocess launcher."""

    def test_dashboard_missing_app_exits_1(self, tmp_path):
        from simple_python_boilerplate.entry_points import _run_dashboard

        with (
            patch(
                "simple_python_boilerplate.entry_points._BUNDLED_TOOLS",
                tmp_path,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            _run_dashboard()
        assert exc_info.value.code == 1

    def test_dashboard_calls_subprocess(self, tmp_path):
        from simple_python_boilerplate.entry_points import _run_dashboard

        app = tmp_path / "dev_tools" / "env_dashboard" / "app.py"
        app.parent.mkdir(parents=True)
        app.write_text("print('dashboard')")

        with (
            patch(
                "simple_python_boilerplate.entry_points._BUNDLED_TOOLS",
                tmp_path,
            ),
            patch("sys.argv", ["spb-dashboard"]),
            patch("subprocess.call", return_value=0) as mock_call,
            pytest.raises(SystemExit) as exc_info,
        ):
            _run_dashboard()

        assert exc_info.value.code == 0
        mock_call.assert_called_once()


# ── Backward-compat re-exports ───────────────────────────────


class TestBackwardCompatMainModule:
    """Verify main.py re-exports the 4 core entry points."""

    def test_main_importable(self):
        from simple_python_boilerplate.main import main

        assert callable(main)

    def test_print_version_importable(self):
        from simple_python_boilerplate.main import print_version

        assert callable(print_version)

    def test_doctor_importable(self):
        from simple_python_boilerplate.main import doctor

        assert callable(doctor)

    def test_start_importable(self):
        from simple_python_boilerplate.main import start

        assert callable(start)

    def test_all_exported(self):
        from simple_python_boilerplate import main as main_mod

        assert set(main_mod.__all__) == {"main", "print_version", "doctor", "start"}


class TestBackwardCompatScriptsCliModule:
    """Verify scripts_cli.py re-exports the 18 script entry points."""

    def test_git_doctor_importable(self):
        from simple_python_boilerplate.scripts_cli import git_doctor

        assert callable(git_doctor)

    def test_dashboard_importable(self):
        from simple_python_boilerplate.scripts_cli import dashboard

        assert callable(dashboard)

    def test_all_18_names_exported(self):
        from simple_python_boilerplate import scripts_cli

        assert len(scripts_cli.__all__) == 18


# ── Script wrapper function names ────────────────────────────


class TestScriptWrappersDefined:
    """Verify each of the 18 script wrapper functions exists and is callable."""

    @pytest.mark.parametrize(
        "name",
        [
            "git_doctor",
            "env_doctor",
            "repo_doctor",
            "doctor_bundle",
            "env_inspect",
            "repo_sauron",
            "clean",
            "bootstrap",
            "dep_versions",
            "workflow_versions",
            "check_todos",
            "check_python_support",
            "changelog_check",
            "apply_labels",
            "archive_todos",
            "customize",
            "check_known_issues",
            "dashboard",
        ],
    )
    def test_wrapper_exists(self, name):
        import simple_python_boilerplate.entry_points as ep

        func = getattr(ep, name, None)
        assert func is not None, f"Missing entry point function: {name}"
        assert callable(func)
