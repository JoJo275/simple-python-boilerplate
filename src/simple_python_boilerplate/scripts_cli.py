"""CLI entry points for bundled utility scripts.

Provides globally-installable commands for all scripts in ``scripts/``.
Each entry point locates the bundled script within the installed package
and runs it via subprocess from the user's current working directory.

This means you can ``pipx install .`` once from the template repo and
use commands like ``spb-git-doctor`` from **any** repository on your
machine — the script will inspect whichever repo you're currently in.

How it works:
    1. Entry point functions are registered in ``pyproject.toml`` under
       ``[project.scripts]``.
    2. Each function calls ``_run_script()`` which locates the bundled
       script file relative to the installed package.
    3. The script is executed as a subprocess with ``cwd=Path.cwd()``.
    4. The ``SPB_REPO_ROOT`` env var is set to CWD so ``_imports.py``
       ``find_repo_root()`` discovers the correct repo root.

Environment variable:
    ``SPB_REPO_ROOT``: When set, ``scripts/_imports.py`` uses this path
    as the repo root instead of walking up from the script file location.
    Entry points set this automatically to the current working directory.

See Also:
    - ``scripts/_imports.py`` — Repo root discovery (reads ``SPB_REPO_ROOT``)
    - ``pyproject.toml`` — Entry point registration under ``[project.scripts]``
    - ``docs/guide/entry-points.md`` — User documentation
"""

from __future__ import annotations

import os
import subprocess  # nosec B404
import sys
from pathlib import Path

# The scripts/ directory is force-included in the wheel at
# simple_python_boilerplate/_bundled_scripts/
_BUNDLED_SCRIPTS = Path(__file__).resolve().parent / "_bundled_scripts" / "scripts"

# The tools/ directory is force-included at
# simple_python_boilerplate/_bundled_tools/
_BUNDLED_TOOLS = Path(__file__).resolve().parent / "_bundled_tools" / "tools"


def _run_script(script_name: str) -> None:
    """Locate and run a bundled script from the user's CWD.

    Args:
        script_name: Filename of the script (e.g. ``"git_doctor.py"``).
    """
    script_path = _BUNDLED_SCRIPTS / script_name
    if not script_path.is_file():
        sys.stderr.write(f"Error: bundled script not found at {script_path}\n")
        sys.exit(1)

    cwd = str(Path.cwd())
    env = os.environ.copy()
    env["SPB_REPO_ROOT"] = cwd

    # Add the bundled scripts dir to PYTHONPATH so _imports.py and
    # sibling modules (_colors.py, _progress.py, etc.) can be found.
    scripts_dir = str(_BUNDLED_SCRIPTS)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{scripts_dir}{os.pathsep}{existing}" if existing else scripts_dir
    )

    raise SystemExit(
        subprocess.call(  # nosec B603
            [sys.executable, str(script_path), *sys.argv[1:]],
            cwd=cwd,
            env=env,
        )
    )


def _run_dashboard() -> None:
    """Locate and run the bundled dashboard web app from the user's CWD."""
    app_module = _BUNDLED_TOOLS / "dev_tools" / "env_dashboard" / "app.py"
    if not app_module.is_file():
        sys.stderr.write(f"Error: bundled dashboard not found at {app_module}\n")
        sys.exit(1)

    cwd = str(Path.cwd())
    env = os.environ.copy()
    env["SPB_REPO_ROOT"] = cwd

    # Add bundled directories to PYTHONPATH so imports resolve
    scripts_dir = str(_BUNDLED_SCRIPTS)
    tools_parent = str(
        _BUNDLED_TOOLS.parent
    )  # Parent of tools/ so "tools.dev_tools..." works
    existing = env.get("PYTHONPATH", "")
    parts = [tools_parent, scripts_dir]
    if existing:
        parts.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(parts)

    raise SystemExit(
        subprocess.call(  # nosec B603
            [sys.executable, str(app_module), *sys.argv[1:]],
            cwd=cwd,
            env=env,
        )
    )


# ── Individual entry points ──────────────────────────────────
# Each function is a thin wrapper registered in pyproject.toml.
# They all delegate to _run_script() or _run_dashboard().


def git_doctor() -> None:
    """Git health check and information dashboard."""
    _run_script("git_doctor.py")


def env_doctor() -> None:
    """Development environment health check."""
    _run_script("env_doctor.py")


def repo_doctor() -> None:
    """Repository structure health checks."""
    _run_script("repo_doctor.py")


def doctor_bundle() -> None:
    """Print diagnostics bundle for bug reports."""
    _run_script("doctor.py")


def env_inspect() -> None:
    """Environment and dependency inspector."""
    _run_script("env_inspect.py")


def repo_sauron() -> None:
    """Repository statistics dashboard."""
    _run_script("repo_sauron.py")


def clean() -> None:
    """Remove build artifacts and caches."""
    _run_script("clean.py")


def bootstrap() -> None:
    """One-command setup for fresh clones."""
    _run_script("bootstrap.py")


def dep_versions() -> None:
    """Show/update dependency versions."""
    _run_script("dep_versions.py")


def workflow_versions() -> None:
    """Show/update SHA-pinned GitHub Actions versions."""
    _run_script("workflow_versions.py")


def check_todos() -> None:
    """Scan for TODO (template users) comments."""
    _run_script("check_todos.py")


def check_python_support() -> None:
    """Validate Python version support consistency."""
    _run_script("check_python_support.py")


def changelog_check() -> None:
    """Validate CHANGELOG.md has entry for current PR."""
    _run_script("changelog_check.py")


def apply_labels() -> None:
    """Apply GitHub labels from JSON definitions."""
    _run_script("apply_labels.py")


def archive_todos() -> None:
    """Archive completed TODO items."""
    _run_script("archive_todos.py")


def customize() -> None:
    """Interactive project customization."""
    _run_script("customize.py")


def check_known_issues() -> None:
    """Flag stale resolved entries in known-issues.md."""
    _run_script("check_known_issues.py")


def dashboard() -> None:
    """Start the environment inspection web dashboard."""
    _run_dashboard()
