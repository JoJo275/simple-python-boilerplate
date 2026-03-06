#!/usr/bin/env python3
"""Print a diagnostics bundle for bug reports and environment debugging.

Collects: Python version, OS, Hatch version, active environment, key tool
versions, important paths, git status, configuration status, and health
checks (pre-commit hooks, editable install, pyproject validity, etc.).

Flags::

    -o, --output PATH   Write output to file (e.g. var/doctor.txt)
    --markdown           Output as markdown (for GitHub issues)
    --json               Output as JSON (machine-readable)
    -q, --quiet          Print a one-line summary only
    --version            Print version and exit

Usage::

    python scripts/doctor.py
    python scripts/doctor.py --output var/doctor.txt
    python scripts/doctor.py --markdown   # For GitHub issues
    python scripts/doctor.py --json       # Machine-readable output
    python scripts/doctor.py --quiet      # One-line summary
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess  # nosec B404
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

from _imports import find_repo_root

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "2.0.0"

ROOT = find_repo_root()


def get_version(cmd: list[str]) -> str:
    """Run a command and extract its version output.

    Handles both PATH-based lookups (``["ruff", "--version"]``) and
    absolute-path commands (``[sys.executable, "-m", "pip", ...]``).
    """
    first = cmd[0]
    # If it's already an absolute path that exists, use it directly;
    # otherwise look it up on PATH via shutil.which.
    if Path(first).is_absolute() and Path(first).exists():
        exe: str = first
    else:
        found = shutil.which(first)
        if not found:
            return "not found"
        exe = found
    try:
        result = subprocess.run(  # nosec B603
            [exe, *cmd[1:]],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (
            result.stdout.strip().split("\n")[0] or result.stderr.strip().split("\n")[0]
        )
    except (subprocess.TimeoutExpired, OSError):
        return "error"


def get_package_version(package: str) -> str:
    """Get installed package version."""
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def check_path_exists(path: Path) -> str:
    """Check if a path exists and its type."""
    if not path.exists():
        return "missing"
    if path.is_dir():
        return "directory"
    return "file"


def _git_info() -> dict[str, str]:
    """Collect git repository information (branch, commit, dirty state)."""
    result: dict[str, str] = {}
    git_exe = shutil.which("git")
    if not git_exe:
        return {"status": "git not found"}

    def _run_git(*args: str) -> str:
        try:
            proc = subprocess.run(  # nosec B603
                [git_exe, *args],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=ROOT,
            )
            return proc.stdout.strip() if proc.returncode == 0 else ""
        except (subprocess.TimeoutExpired, OSError):
            return ""

    result["branch"] = _run_git("rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    result["commit"] = _run_git("rev-parse", "--short", "HEAD") or "unknown"
    result["commit_date"] = _run_git("log", "-1", "--format=%ci") or "unknown"

    # Dirty = uncommitted changes exist
    dirty_check = _run_git("status", "--porcelain")
    result["dirty"] = "yes" if dirty_check else "no"

    return result


# ---------------------------------------------------------------------------
# Health check helpers
# ---------------------------------------------------------------------------


def _check_hook_installed(hook_path: Path) -> str:
    """Check if a git hook file is a real pre-commit hook (not a sample).

    Returns:
        ``"installed"`` if the hook exists and appears to be managed by
        pre-commit, ``"sample"`` if it's a Git sample hook, ``"custom"``
        if it's some other script, or ``"missing"`` if absent.
    """
    if not hook_path.is_file():
        return "missing"
    try:
        content = hook_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "missing"
    if "pre-commit" in content:
        return "installed"
    if "This sample" in content or ".sample" in hook_path.name:
        return "sample"
    return "custom"


def _check_precommit_hooks(root: Path) -> dict[str, str]:
    """Check whether the three expected pre-commit hook stages are installed."""
    hooks_dir = root / ".git" / "hooks"
    return {
        "pre-commit": _check_hook_installed(hooks_dir / "pre-commit"),
        "commit-msg": _check_hook_installed(hooks_dir / "commit-msg"),
        "pre-push": _check_hook_installed(hooks_dir / "pre-push"),
    }


def _check_editable_install() -> dict[str, str]:
    """Check if the package is importable and where it's installed from."""
    result: dict[str, str] = {}
    try:
        dist = importlib.metadata.distribution("simple-python-boilerplate")
        location = str(dist._path.parent) if hasattr(dist, "_path") else "unknown"  # type: ignore[attr-defined]
        result["installed"] = "yes"
        result["version"] = dist.metadata["Version"] or "unknown"
        # Check if it's an editable install (src/ in the path)
        if "src" in location or "site-packages" not in location:
            result["editable"] = "yes"
        else:
            result["editable"] = "no"
        result["location"] = location
    except importlib.metadata.PackageNotFoundError:
        result["installed"] = "no"
        result["editable"] = "N/A"
        result["version"] = "N/A"
        result["location"] = "N/A"
    return result


def _check_pyproject(root: Path) -> dict[str, str]:
    """Validate pyproject.toml can be parsed and has expected sections."""
    pyproject = root / "pyproject.toml"
    result: dict[str, str] = {}

    if not pyproject.is_file():
        result["status"] = "missing"
        return result

    if tomllib is None:
        result["status"] = "cannot parse (tomllib unavailable)"
        return result

    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        result["parseable"] = "yes"
    except Exception as exc:
        result["parseable"] = f"no ({exc!s})"
        return result

    # Check key sections exist
    project = data.get("project", {})
    result["project.name"] = project.get("name", "MISSING")
    result["requires-python"] = project.get("requires-python", "not set")

    # Check optional-dependencies groups
    opt_deps = project.get("optional-dependencies", {})
    groups = sorted(opt_deps.keys()) if opt_deps else []
    result["optional-dep-groups"] = ", ".join(groups) if groups else "none"

    # Check build system
    build = data.get("build-system", {})
    result["build-backend"] = build.get("build-backend", "not set")

    return result


def _check_python_compat(root: Path) -> dict[str, str]:
    """Check if current Python version meets requires-python constraint."""
    result: dict[str, str] = {}
    pyproject = root / "pyproject.toml"

    if not pyproject.is_file() or tomllib is None:
        result["status"] = "cannot check"
        return result

    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except Exception:
        result["status"] = "cannot parse pyproject.toml"
        return result

    requires = data.get("project", {}).get("requires-python", "")
    if not requires:
        result["status"] = "no requires-python set"
        return result

    current = sys.version.split()[0]
    result["current"] = current
    result["requires"] = requires

    # Simple >=X.Y check (covers the common case)
    match = re.match(r">=(\d+)\.(\d+)", requires)
    if match:
        req_major, req_minor = int(match.group(1)), int(match.group(2))
        cur_parts = [int(x) for x in current.split(".")[:2]]
        if (cur_parts[0], cur_parts[1]) >= (req_major, req_minor):
            result["compatible"] = "yes"
        else:
            result["compatible"] = f"NO (need >={req_major}.{req_minor})"
    else:
        result["compatible"] = f"unknown (complex specifier: {requires})"

    return result


def _check_key_config_files(root: Path) -> dict[str, str]:
    """Check presence of key configuration files."""
    files = {
        ".pre-commit-config.yaml": root / ".pre-commit-config.yaml",
        "Taskfile.yml": root / "Taskfile.yml",
        "mkdocs.yml": root / "mkdocs.yml",
        ".repo-doctor.toml": root / ".repo-doctor.toml",
        "release-please-config.json": root / "release-please-config.json",
        ".release-please-manifest.json": root / ".release-please-manifest.json",
    }
    return {name: "present" if p.is_file() else "MISSING" for name, p in files.items()}


def _check_hatch_env() -> dict[str, str]:
    """Check if hatch default environment exists."""
    result: dict[str, str] = {}
    hatch_exe = shutil.which("hatch")
    if not hatch_exe:
        result["status"] = "hatch not found"
        return result

    try:
        proc = subprocess.run(  # nosec B603
            [hatch_exe, "env", "show", "--json"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode == 0:
            try:
                envs = json.loads(proc.stdout)
                if isinstance(envs, dict):
                    result["environments"] = ", ".join(sorted(envs.keys()))
                elif isinstance(envs, list):
                    names = [
                        e["name"] for e in envs if isinstance(e, dict) and "name" in e
                    ]
                    result["environments"] = ", ".join(names) if names else "none found"
                else:
                    result["environments"] = "unknown format"
            except (json.JSONDecodeError, TypeError):
                # Fallback: just report raw output
                result["environments"] = proc.stdout.strip()[:100] or "none"
        else:
            result["status"] = "hatch env show failed"
    except (subprocess.TimeoutExpired, OSError):
        result["status"] = "error running hatch"

    return result


def _check_venv_activation() -> dict[str, str]:
    """Enhanced environment detection with guidance."""
    result: dict[str, str] = {}
    venv = os.environ.get("VIRTUAL_ENV", "")
    hatch_env = os.environ.get("HATCH_ENV", "")

    if venv:
        result["virtual_env"] = Path(venv).name
        result["virtual_env_path"] = venv
        result["activated"] = "yes"
    else:
        result["virtual_env"] = "none"
        result["virtual_env_path"] = "N/A"
        result["activated"] = "no"

    result["hatch_env"] = hatch_env if hatch_env else "none"

    # Check if a .venv directory exists even if not activated
    venv_dir = ROOT / ".venv"
    if venv_dir.is_dir() and not venv:
        result["note"] = ".venv/ exists but is NOT activated"
    elif not venv_dir.is_dir() and not venv and not hatch_env:
        result["note"] = "no venv found — run 'hatch shell' or create a .venv"

    # Check if running inside hatch
    if hatch_env:
        result["running_via"] = "hatch"
    elif venv:
        result["running_via"] = "virtualenv"
    else:
        result["running_via"] = "system Python (not recommended)"

    return result


def collect_diagnostics() -> dict[str, str | dict[str, str]]:
    """Collect all diagnostic information."""
    info: dict[str, str | dict[str, str]] = {}

    # Timestamp (UTC for unambiguous reports)
    info["timestamp"] = datetime.now(tz=UTC).isoformat()

    # System
    info["system"] = {
        "os": f"{platform.system()} {platform.release()}",
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version.split()[0],
        "python_path": sys.executable,
        "python_bits": "64-bit" if sys.maxsize > 2**32 else "32-bit",
    }

    # Virtual Environment (enhanced)
    info["environment"] = _check_venv_activation()

    # Tool versions — collected in parallel to reduce wall-clock time
    tool_cmds: dict[str, list[str]] = {
        "hatch": ["hatch", "--version"],
        "pip": [sys.executable, "-m", "pip", "--version"],
        "task": ["task", "--version"],
        "ruff": ["ruff", "--version"],
        "mypy": ["mypy", "--version"],
        "pytest": ["pytest", "--version"],
        "pre-commit": ["pre-commit", "--version"],
        "git": ["git", "--version"],
        "actionlint": ["actionlint", "--version"],
        "cz": ["cz", "version"],
    }

    tools: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=len(tool_cmds)) as pool:
        futures = {
            pool.submit(get_version, cmd): name for name, cmd in tool_cmds.items()
        }
        for future in as_completed(futures):
            tools[futures[future]] = future.result()

    # Preserve a stable key order (same as tool_cmds definition)
    info["tools"] = {name: tools[name] for name in tool_cmds}

    # Git repository — also collected in parallel with tools above
    info["git"] = _git_info()

    # Package status
    info["package"] = {
        "simple-python-boilerplate": get_package_version("simple-python-boilerplate"),
    }

    # Key paths
    info["paths"] = {
        "root": str(ROOT),
        "pyproject.toml": check_path_exists(ROOT / "pyproject.toml"),
        "src/": check_path_exists(ROOT / "src"),
        ".git/": check_path_exists(ROOT / ".git"),
        ".git/hooks/pre-commit": check_path_exists(
            ROOT / ".git" / "hooks" / "pre-commit"
        ),
        ".git/hooks/commit-msg": check_path_exists(
            ROOT / ".git" / "hooks" / "commit-msg"
        ),
        ".git/hooks/pre-push": check_path_exists(ROOT / ".git" / "hooks" / "pre-push"),
    }

    # -----------------------------------------------------------------------
    # Health checks
    # -----------------------------------------------------------------------

    # Pre-commit hook installation
    info["hooks"] = _check_precommit_hooks(ROOT)

    # Editable install check
    info["install"] = _check_editable_install()

    # Python version compatibility
    info["python_compat"] = _check_python_compat(ROOT)

    # pyproject.toml validation
    info["pyproject"] = _check_pyproject(ROOT)

    # Key config files
    info["config_files"] = _check_key_config_files(ROOT)

    # Hatch environment status
    info["hatch_envs"] = _check_hatch_env()

    return info


def format_plain(info: dict[str, str | dict[str, str]]) -> str:
    """Format diagnostics as plain text."""
    lines = ["=" * 60, "DIAGNOSTICS REPORT", "=" * 60, ""]

    for section, data in info.items():
        lines.append(f"[{section.upper()}]")
        if isinstance(data, dict):
            for key, value in data.items():
                lines.append(f"  {key}: {value}")
        else:
            lines.append(f"  {data}")
        lines.append("")

    return "\n".join(lines)


def format_markdown(info: dict[str, str | dict[str, str]]) -> str:
    """Format diagnostics as markdown for GitHub issues."""
    lines = [
        "<details>",
        "<summary>Environment diagnostics</summary>",
        "",
        "```",
    ]

    for section, data in info.items():
        lines.append(f"[{section}]")
        if isinstance(data, dict):
            for key, value in data.items():
                lines.append(f"  {key}: {value}")
        else:
            lines.append(f"  {data}")

    lines.extend(["```", "</details>"])
    return "\n".join(lines)


def format_json(info: dict[str, str | dict[str, str]]) -> str:
    """Format diagnostics as JSON for scripting and automation."""
    return json.dumps(info, indent=2)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="doctor",
        description="Print a diagnostics bundle for bug reports.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Write output to file (e.g., var/doctor.txt)",
    )

    fmt_group = parser.add_mutually_exclusive_group()
    fmt_group.add_argument(
        "--markdown",
        action="store_true",
        help="Output as markdown (for GitHub issues)",
    )
    fmt_group.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (machine-readable)",
    )
    fmt_group.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Print a one-line summary only",
    )
    args = parser.parse_args()

    info = collect_diagnostics()

    if args.quiet:
        section_count = len(info)
        output = f"doctor {SCRIPT_VERSION} — {section_count} sections collected, all OK"
    elif args.json:
        output = format_json(info)
    elif args.markdown:
        output = format_markdown(info)
    else:
        output = format_plain(info)

    print(output)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"\nSaved to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
