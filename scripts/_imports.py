"""Shared import helper for scripts.

Provides a safe way to import sibling modules from the ``scripts/``
directory without relying on ``sys.path`` or the current working
directory.  This works regardless of how the script is invoked
(from repo root, from ``scripts/``, via absolute path, etc.).

This module is intended to be imported by other scripts in the
``scripts/`` directory — it is not a CLI and should not be run directly.

Usage::

    from _imports import import_sibling

    _progress = import_sibling("_progress")
    ProgressBar = _progress.ProgressBar

.. note::
    This is a shared internal module (prefixed with ``_``). It is excluded
    from the command reference generator and is not intended as a standalone
    CLI. See ADR 031 for script conventions.

.. note::
    If you add a new shared internal module under ``scripts/``, import it
    via ``import_sibling()`` rather than a bare ``from _module import X``
    to ensure it works regardless of working directory.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

__all__ = ["find_repo_root", "import_sibling"]

SCRIPT_VERSION = "1.1.0"

_SCRIPTS_DIR = Path(__file__).resolve().parent


def find_repo_root(start: Path | None = None) -> Path:
    """Walk up from *start* until a directory containing ``pyproject.toml`` is found.

    This replaces the brittle ``Path(__file__).resolve().parent.parent``
    pattern that breaks if a script is moved to a different directory depth.

    Args:
        start: Starting directory.  Defaults to the ``scripts/`` directory
            (i.e. ``_SCRIPTS_DIR``).

    Returns:
        The repository root directory.

    Raises:
        FileNotFoundError: If no ``pyproject.toml`` is found before the
            filesystem root.
    """
    current = (start or _SCRIPTS_DIR).resolve()
    for parent in (current, *current.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = f"Cannot find repo root (no pyproject.toml above {current})"
    raise FileNotFoundError(msg)


def import_sibling(name: str) -> ModuleType:
    """Import a module from the same directory as this file (``scripts/``).

    Uses importlib.util to load from an explicit file path instead of
    polluting sys.path — safer and works regardless of working directory
    or invocation method.

    Args:
        name: Module name (without .py extension).

    Returns:
        The imported module.

    Raises:
        ImportError: If the module cannot be found.
    """
    if name in sys.modules:
        return sys.modules[name]
    path = _SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        msg = f"Cannot find module '{name}' at {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
