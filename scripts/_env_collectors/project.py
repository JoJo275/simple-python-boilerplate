"""Project collector — repo root, lockfiles, build/test/lint tools, configs."""

from __future__ import annotations

import shutil
from typing import Any

from _imports import find_repo_root

from _env_collectors._base import BaseCollector

_tier = None


def _get_tier():  # type: ignore[no-untyped-def]
    global _tier
    if _tier is None:
        from _env_collectors import Tier

        _tier = Tier
    return _tier


_LOCKFILES = [
    "requirements.txt",
    "requirements-dev.txt",
    "requirements.lock",
    "poetry.lock",
    "Pipfile.lock",
    "pdm.lock",
    "uv.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
]

_CONFIG_FILES = [
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "tox.ini",
    "noxfile.py",
    ".flake8",
    ".pylintrc",
    "mypy.ini",
    ".mypy.ini",
    ".pre-commit-config.yaml",
    "Taskfile.yml",
    "Makefile",
    "Containerfile",
    "Dockerfile",
    "docker-compose.yml",
    ".tool-versions",
    ".python-version",
    ".node-version",
    ".nvmrc",
    "mkdocs.yml",
]

_BUILD_TOOLS = [
    ("Hatch", "hatch"),
    ("tox", "tox"),
    ("nox", "nox"),
    ("Poetry", "poetry"),
    ("PDM", "pdm"),
    ("Flit", "flit"),
    ("pip", "pip"),
    ("pipx", "pipx"),
    ("uv", "uv"),
    ("conda", "conda"),
    ("mamba", "mamba"),
]


class ProjectCollector(BaseCollector):
    """Detect project structure, lockfiles, build tools, and config files."""

    name = "project"
    timeout = 5.0

    @property
    def tier(self):  # type: ignore[override]
        return _get_tier().MINIMAL

    def collect(self) -> dict[str, Any]:
        root = find_repo_root()
        lockfiles = [f for f in _LOCKFILES if (root / f).is_file()]
        configs = [f for f in _CONFIG_FILES if (root / f).is_file()]
        tools = [
            {"name": name, "available": shutil.which(exe) is not None}
            for name, exe in _BUILD_TOOLS
        ]

        return {
            "repo_root": str(root),
            "lockfiles": lockfiles,
            "config_files": configs,
            "build_tools": tools,
        }
