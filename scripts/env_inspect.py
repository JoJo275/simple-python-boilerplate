#!/usr/bin/env python3
"""Environment and dependency inspector — full inventory of your setup.

Shows a comprehensive view of your development environment:
  - Python version, location, and supported versions for the project
  - Git version and location
  - Virtual environment status (global vs local)
  - All installed packages with versions and update availability
  - Entry points registered by installed packages
  - Build and environment tools found on PATH (hatch, tox, nox, etc.)
  - Python version support validation (cross-checks pyproject.toml sources)
  - Key PATH directories with duplicate detection
  - Related scripts for further investigation

This complements ``dep_versions.py`` (which focuses on project deps
declared in pyproject.toml) by showing the full picture including
globally installed packages, entry points, and PATH.

Flags::

    --json              Output as JSON (for CI integration)
    --section SECTION   Only show a specific section
                        (python, git, venv, packages, entrypoints,
                         build-tools, python-support, path)
    -q, --quiet         Suppress output; exit code only
    --no-color          Disable colored output
    --version           Print version and exit

Usage::

    python scripts/env_inspect.py
    python scripts/env_inspect.py --json
    python scripts/env_inspect.py --section packages
    python scripts/env_inspect.py --section build-tools
    python scripts/env_inspect.py --section python-support
    python scripts/env_inspect.py --section path

Portability:
    Can be used in other repos. Requires shared modules from this repo's
    scripts/ directory: ``_colors.py``, ``_imports.py``, ``_progress.py``,
    ``_ui.py``.  Also optionally imports ``check_python_support.py`` for
    the python-support section.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.metadata
import json
import logging
import os
import platform
import re
import shutil
import subprocess  # nosec B404
import sys
import time
import tomllib
from pathlib import Path

# -- Local script modules (not third-party; live in scripts/) ----------------
from _colors import Colors
from _imports import find_repo_root
from _progress import Spinner
from _ui import UI

log = logging.getLogger(__name__)

SCRIPT_VERSION = "1.1.0"
THEME = "cyan"

ROOT = find_repo_root()


# ---------------------------------------------------------------------------
# Python info
# ---------------------------------------------------------------------------


def _python_info() -> dict:
    """Gather Python interpreter details."""
    info: dict = {
        "version": platform.python_version(),
        "version_tuple": list(sys.version_info[:3]),
        "implementation": platform.python_implementation(),
        "compiler": platform.python_compiler(),
        "executable": sys.executable,
        "prefix": sys.prefix,
        "base_prefix": sys.base_prefix,
        "in_venv": sys.prefix != sys.base_prefix,
        "platform": platform.platform(),
        "architecture": platform.machine(),
    }

    # Project-supported versions from pyproject.toml
    pyproject = ROOT / "pyproject.toml"
    if pyproject.is_file():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            info["requires_python"] = data.get("project", {}).get("requires-python", "")
            classifiers = data.get("project", {}).get("classifiers", [])
            supported = []
            for c in classifiers:
                m = re.match(r"Programming Language :: Python :: (\d+\.\d+)$", c)
                if m:
                    supported.append(m.group(1))
            info["supported_versions"] = supported
        except (OSError, ValueError):
            pass

    return info


# ---------------------------------------------------------------------------
# Git info
# ---------------------------------------------------------------------------


def _git_info() -> dict:
    """Gather git version and location."""
    git_cmd = shutil.which("git")
    info: dict = {"available": git_cmd is not None, "path": git_cmd}

    if git_cmd:
        try:
            result = subprocess.run(  # nosec B603
                [git_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                m = re.search(r"(\d+\.\d+[\.\d]*)", result.stdout)
                info["version"] = m.group(1) if m else result.stdout.strip()
        except (subprocess.TimeoutExpired, OSError):
            pass

    return info


# ---------------------------------------------------------------------------
# Package inventory
# ---------------------------------------------------------------------------


def _all_installed_packages() -> list[dict]:
    """List all packages installed in the current environment."""
    packages = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"]
        version = dist.metadata["Version"]
        summary = dist.metadata.get("Summary", "")
        location = str(dist._path.parent) if hasattr(dist, "_path") else ""

        packages.append(
            {
                "name": name,
                "version": version,
                "summary": summary or "",
                "location": location,
            }
        )

    # Deduplicate by name (keep first seen)
    seen: set[str] = set()
    unique: list[dict] = []
    for pkg in sorted(packages, key=lambda p: (p["name"] or "").lower()):
        key = (pkg["name"] or "").lower()
        if key not in seen:
            seen.add(key)
            unique.append(pkg)

    return unique


def _check_outdated_packages() -> dict[str, str]:
    """Use pip to find outdated packages. Returns {name: latest_version}."""
    try:
        result = subprocess.run(  # nosec B603
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {pkg["name"].lower(): pkg["latest_version"] for pkg in data}
    except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError):
        pass
    return {}


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def _collect_entry_points() -> list[dict]:
    """Collect console_scripts entry points from installed packages."""
    entries = [
        {"name": ep.name, "value": ep.value, "group": "console_scripts"}
        for ep in importlib.metadata.entry_points(group="console_scripts")
    ]
    entries.extend(
        {"name": ep.name, "value": ep.value, "group": "gui_scripts"}
        for ep in importlib.metadata.entry_points(group="gui_scripts")
    )

    return sorted(entries, key=lambda e: e["name"])


# ---------------------------------------------------------------------------
# PATH inspection
# ---------------------------------------------------------------------------


def _inspect_path() -> list[dict]:
    """Inspect PATH directories and count executables in each."""
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    results = []
    seen: set[str] = set()

    for dir_path in path_dirs:
        # Normalize for duplicate detection (case-insensitive on Windows)
        normalized = os.path.normcase(os.path.normpath(dir_path))
        is_duplicate = normalized in seen
        seen.add(normalized)

        p = Path(dir_path)
        if not p.is_dir():
            results.append(
                {
                    "path": dir_path,
                    "exists": False,
                    "executable_count": 0,
                    "duplicate": is_duplicate,
                }
            )
            continue

        try:
            executables = sum(
                1 for f in p.iterdir() if f.is_file() and os.access(f, os.X_OK)
            )
        except (PermissionError, OSError):
            executables = 0

        results.append(
            {
                "path": dir_path,
                "exists": True,
                "executable_count": executables,
                "duplicate": is_duplicate,
            }
        )

    return results


# ---------------------------------------------------------------------------
# Hatch env status
# ---------------------------------------------------------------------------


def _hatch_info() -> dict | None:
    """Get Hatch environment info if hatch is available."""
    hatch = shutil.which("hatch")
    if not hatch:
        return None

    info: dict = {"available": True, "path": hatch}

    try:
        result = subprocess.run(  # nosec B603
            [hatch, "version"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=ROOT,
        )
        if result.returncode == 0:
            info["version"] = result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        pass

    try:
        result = subprocess.run(  # nosec B603
            [hatch, "env", "show", "--json"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=ROOT,
        )
        if result.returncode == 0:
            with contextlib.suppress(json.JSONDecodeError):
                info["environments"] = json.loads(result.stdout)
    except (subprocess.TimeoutExpired, OSError):
        pass

    return info


# ---------------------------------------------------------------------------
# Main collector
# ---------------------------------------------------------------------------


def gather_env_info(*, check_updates: bool = True) -> dict:
    """Gather all environment information."""
    info: dict = {
        "python": _python_info(),
        "git": _git_info(),
        "packages": _all_installed_packages(),
        "entry_points": _collect_entry_points(),
        "path": _inspect_path(),
    }

    if check_updates:
        info["outdated"] = _check_outdated_packages()

    # Build system info from pyproject.toml
    pyproject = ROOT / "pyproject.toml"
    if pyproject.is_file():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            build_sys = data.get("build-system", {})
            info["build_backend"] = build_sys.get("build-backend", "")
            info["build_requires"] = build_sys.get("requires", [])
        except (OSError, ValueError):
            pass

    hatch = _hatch_info()
    if hatch:
        info["hatch"] = hatch

    return info


# ---------------------------------------------------------------------------
# Build tools detection
# ---------------------------------------------------------------------------

_BUILD_TOOLS: list[tuple[str, str, list[str]]] = [
    # (display_name, executable, version_args)
    ("Hatch", "hatch", ["--version"]),
    ("tox", "tox", ["--version"]),
    ("nox", "nox", ["--version"]),
    ("Poetry", "poetry", ["--version"]),
    ("PDM", "pdm", ["--version"]),
    ("Flit", "flit", ["--version"]),
    ("pip", "pip", ["--version"]),
    ("pipx", "pipx", ["--version"]),
    ("uv", "uv", ["--version"]),
    ("conda", "conda", ["--version"]),
    ("mamba", "mamba", ["--version"]),
    ("virtualenv", "virtualenv", ["--version"]),
]


def _detect_build_tools() -> list[dict]:
    """Detect installed build/environment tools."""
    tools = []
    for name, exe, ver_args in _BUILD_TOOLS:
        path = shutil.which(exe)
        if not path:
            continue
        version = "unknown"
        try:
            result = subprocess.run(  # nosec B603
                [path, *ver_args],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            if result.returncode == 0:
                # Extract version from output (first line, strip tool name)
                out = (result.stdout + result.stderr).strip().splitlines()[0]
                # Try to find a version-like pattern
                m = re.search(r"(\d+\.\d+[\w.+-]*)", out)
                version = m.group(1) if m else out.strip()
        except (subprocess.TimeoutExpired, OSError):
            pass
        tools.append(
            {"name": name, "executable": exe, "path": path, "version": version}
        )
    return tools


# ---------------------------------------------------------------------------
# Python support validation
# ---------------------------------------------------------------------------


def _check_python_support_summary() -> dict | None:
    """Run a lightweight python-support check and return a summary.

    Imports from check_python_support.py to get version consistency data.
    Returns None if the check is unavailable.
    """
    try:
        # Import inline to avoid hard dependency
        from check_python_support import check_python_support

        result = check_python_support(quiet=True, no_color=True)
        return {
            "ok": result["ok"],
            "sources": result.get("sources", {}),
            "mismatches": result.get("mismatches", []),
            "current_meets_minimum": result.get("current_meets_minimum", True),
            "code_min_version": result.get("code_analysis", {}).get("code_min_version"),
        }
    except Exception:
        return None


def print_env_info(
    info: dict,
    *,
    no_color: bool = False,
    section: str | None = None,
) -> None:
    """Print environment info as a dashboard."""
    c = Colors(enabled=not no_color)
    ui = UI(
        title="Environment Inspector",
        version=SCRIPT_VERSION,
        theme=THEME,
        no_color=no_color,
    )
    ui.header()

    show_all = section is None

    # ── Python ──
    if show_all or section == "python":
        py = info["python"]
        ui.section("Python")
        ui.info_line(
            "Core Python runtime info. Verify the version matches your project's"
        )
        ui.info_line(
            "requires-python constraint and that you're using the right executable."
        )
        ui.blank()
        ui.kv("Version", py["version"])
        ui.kv("Implementation", py["implementation"])
        ui.kv("Executable", py["executable"])
        ui.kv("Platform", py["platform"])
        ui.kv("Architecture", py["architecture"])
        ui.kv("In virtualenv", c.green("Yes") if py["in_venv"] else c.yellow("No"))
        if py.get("requires_python"):
            ui.kv("requires-python", py["requires_python"])
        if py.get("supported_versions"):
            ui.kv("Supported versions", ", ".join(py["supported_versions"]))

            # Check if current version is in the supported list
            current = f"{sys.version_info.major}.{sys.version_info.minor}"
            if current in py["supported_versions"]:
                ui.status_line(
                    "check", f"Current Python {current} is supported", "green"
                )
            else:
                ui.status_line(
                    "warn", f"Current Python {current} not in supported list", "yellow"
                )

    # ── Git ──
    if show_all or section == "git":
        git = info["git"]
        ui.section("Git")
        ui.info_line("Git is required for version control and hatch-vcs versioning.")
        ui.blank()
        if git["available"]:
            ui.kv("Version", git.get("version", "unknown"))
            ui.kv("Path", git["path"] or "unknown")
        else:
            ui.status_line("cross", "Git not found on PATH", "red")

    # ── Virtual Environment ──
    if show_all or section == "venv":
        py = info["python"]
        ui.section("Virtual Environment")
        ui.info_line(
            "Shows whether you're inside a virtual environment. "
            "Working inside a venv prevents polluting the global Python."
        )
        # Detect workflow tool dynamically
        hatch_info = info.get("hatch")
        env_cmd = "hatch shell" if hatch_info else "your env manager's shell command"
        if py["in_venv"]:
            ui.kv("Status", c.green("Active"))
            ui.kv("Prefix", py["prefix"])
            ui.kv("Base prefix", py["base_prefix"])
        else:
            ui.kv("Status", c.yellow("Not in a virtualenv"))
            ui.info_line(f"Run '{env_cmd}' to enter the dev environment.")

    # ── Hatch / Build System ──
    if show_all and info.get("hatch"):
        hatch = info["hatch"]
        ui.section("Hatch")
        ui.info_line(
            "Hatch manages environments and builds. "
            "Use 'hatch shell' to enter the dev environment."
        )
        ui.kv("Version", hatch.get("version", "unknown"))
        ui.kv("Path", hatch.get("path", "unknown"))
        # Show build backend dynamically
        build_backend = info.get("build_backend", "")
        if build_backend:
            ui.kv("Build backend", build_backend)
        build_requires = info.get("build_requires", [])
        if build_requires:
            ui.kv("Build requires", ", ".join(build_requires))

    # ── Packages ──
    if show_all or section == "packages":
        packages = info["packages"]
        outdated = info.get("outdated", {})
        ui.section(f"Installed Packages ({len(packages)})")
        ui.info_line(
            "All packages in the current environment. Outdated packages "
            "may need upgrading — run 'python scripts/dep_versions.py' for details."
        )

        ui.table_header(
            [
                ("Package", 30),
                ("Version", 12),
                ("Latest", 12),
                ("Status", 10),
            ]
        )

        for pkg in packages:
            name = pkg["name"] or ""
            ver = pkg["version"] or ""
            name_lower = name.lower()
            latest = outdated.get(name_lower, "")

            if latest and latest != ver:
                status = c.yellow("outdated")
                name_col = c.yellow(name)
            else:
                status = c.green("ok") if ver else c.dim("-")
                name_col = name

            ui.table_row(
                [
                    (name_col, 30),
                    (ver, 12),
                    (latest or c.dim("-"), 12),
                    (status, 10),
                ]
            )

        outdated_count = len(outdated)
        ui.blank()
        ui.info_line(
            f"{len(packages)} package(s) installed"
            + (f", {outdated_count} outdated" if outdated_count else "")
        )

    # ── Entry Points ──
    if show_all or section == "entrypoints":
        eps = info["entry_points"]
        ui.section(f"Entry Points ({len(eps)})")
        ui.info_line("Console commands registered by installed packages. These are")
        ui.info_line("the CLI tools available in your environment. If your package")
        ui.info_line("defines [project.scripts] in pyproject.toml, its commands")
        ui.info_line("appear here after installation.")
        ui.blank()
        if eps:
            ui.table_header([("Command", 25), ("Target", 50)])
            for ep in eps:
                ui.table_row(
                    [
                        (c.cyan(ep["name"]), 25),
                        (c.dim(ep["value"]), 50),
                    ]
                )
        else:
            ui.info_line("No console_scripts or gui_scripts entry points found.")

    # ── Build Tools ──
    if show_all or section == "build-tools":
        build_tools = info.get("build_tools", [])
        ui.section(f"Build & Environment Tools ({len(build_tools)})")
        ui.info_line("Build tools, environment managers, and package installers found")
        ui.info_line("on PATH. Verify the expected tool is available and up to date.")
        if build_tools:
            ui.table_header([("Tool", 16), ("Version", 16), ("Path", 40)])
            for t in build_tools:
                path_display = t["path"]
                if len(path_display) > 40:
                    path_display = "..." + path_display[-37:]
                ui.table_row([(t["name"], 16), (t["version"], 16), (path_display, 40)])
        else:
            ui.info_line("No build/environment tools found on PATH.")

    # ── Python Support Validation ──
    if show_all or section == "python-support":
        py_support = info.get("python_support")
        if py_support is not None:
            ui.section("Python Version Support")
            ui.info_line(
                "Cross-checks pyproject.toml, classifiers, Hatch matrix, and CI matrix."
            )
            ui.info_line(
                "Mismatches here can cause CI failures or user-facing compatibility issues."
            )
            ui.blank()
            sources = py_support.get("sources", {})
            if sources.get("requires-python"):
                ui.kv("requires-python", sources["requires-python"])
            if sources.get("classifiers"):
                ui.kv("Classifiers", sources["classifiers"])
            if py_support.get("code_min_version"):
                ui.kv("Code min version", py_support["code_min_version"])
            if py_support["ok"]:
                ui.status_line("check", "All version sources consistent", "green")
            else:
                for m in py_support.get("mismatches", []):
                    ui.status_line("cross", m, "red")
            if not py_support.get("current_meets_minimum", True):
                ui.status_line("warn", "Current Python does not meet minimum", "yellow")
            ui.info_line(
                "Run 'python scripts/check_python_support.py' for full analysis"
            )

    # ── PATH ──
    if show_all or section == "path":
        path_dirs = info["path"]
        dup_count = sum(1 for d in path_dirs if d.get("duplicate"))
        label = f"PATH Directories ({len(path_dirs)}"
        if dup_count:
            label += f", {dup_count} duplicate{'s' if dup_count != 1 else ''}"
        label += ")"
        ui.section(label)
        ui.info_line("Directories on your system PATH. Duplicates waste lookup time.")
        ui.info_line("Directory: the path entry.  Exists: whether it's on disk.")
        ui.info_line(
            "Execs: number of executable files found.  Note: flags duplicates."
        )
        ui.blank()
        ui.table_header([("Directory", 45), ("Exists", 8), ("Execs", 7), ("Note", 14)])
        for d in path_dirs:
            exists_str = c.green("Yes") if d["exists"] else c.red("No")
            exe_count = str(d["executable_count"]) if d["exists"] else c.dim("-")
            note = c.yellow("(duplicate)") if d.get("duplicate") else ""
            # Truncate long paths
            path_display = d["path"]
            if len(path_display) > 45:
                path_display = "..." + path_display[-42:]
            ui.table_row(
                [
                    (path_display, 45),
                    (exists_str, 8),
                    (exe_count, 7),
                    (note, 14),
                ]
            )
        if dup_count:
            ui.blank()
            ui.status_line(
                "warn",
                f"{dup_count} duplicate PATH entr{'ies' if dup_count != 1 else 'y'} "
                "found — consider cleaning up your PATH",
                "yellow",
            )

    # ── Recommended Scripts ──
    if show_all:
        ui.recommended_scripts(
            [
                "check_python_support",
                "dep_versions",
                "env_doctor",
                "doctor",
                "repo_sauron",
            ],
            preamble="Scripts that expand on environment information and health checks.",
        )

    ui.blank()
    ui.separator(double=True, themed=True)
    print()


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="env-inspect",
        description="Environment and dependency inspector.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON",
    )
    parser.add_argument(
        "--section",
        choices=[
            "python",
            "git",
            "venv",
            "packages",
            "entrypoints",
            "build-tools",
            "python-support",
            "path",
        ],
        help="Only show a specific section",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output; exit code only",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Quick import and arg-parse health check; exit 0 immediately",
    )
    args = parser.parse_args()

    if args.smoke:
        print(f"env_inspect {SCRIPT_VERSION}: smoke ok")
        return 0

    level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(message)s", level=level)

    start = time.monotonic()
    # Only check for package updates when showing the packages section
    check_updates = not args.quiet and (
        args.section is None or args.section == "packages"
    )

    with Spinner("Gathering environment info", color="cyan") as spin:
        spin.update("Python info")
        info = gather_env_info(check_updates=check_updates)
        spin.update("Build tools")
        info["build_tools"] = _detect_build_tools()
        spin.update("Python support")
        info["python_support"] = _check_python_support_summary()

    elapsed = time.monotonic() - start

    if args.json_output:
        # Serialize PATH info strings properly
        print(json.dumps(info, indent=2, default=str))
    elif not args.quiet:
        print_env_info(info, no_color=args.no_color, section=args.section)
        c = Colors(enabled=not args.no_color)
        print(f"  {c.dim(f'Completed in {elapsed:.1f}s')}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
