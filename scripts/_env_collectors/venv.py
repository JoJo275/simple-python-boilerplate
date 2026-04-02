"""Virtualenv collector — detection, Hatch envs, mismatch."""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess  # nosec B404
import sys
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


class VenvCollector(BaseCollector):
    """Detect virtualenv status and Hatch environments."""

    name = "venv"
    timeout = 15.0

    @property
    def tier(self):  # type: ignore[override]
        return _get_tier().STANDARD

    def collect(self) -> dict[str, Any]:
        in_venv = sys.prefix != sys.base_prefix
        info: dict[str, Any] = {
            "active": in_venv,
            "prefix": sys.prefix,
            "base_prefix": sys.base_prefix,
            "virtual_env": os.environ.get("VIRTUAL_ENV", ""),
            "conda_env": os.environ.get("CONDA_DEFAULT_ENV", ""),
            "hatch_env": os.environ.get("HATCH_ENV_ACTIVE", ""),
        }

        # Hatch environment info
        hatch = shutil.which("hatch")
        if hatch:
            info["hatch"] = self._hatch_info(hatch)

        return info

    @staticmethod
    def _hatch_info(hatch: str) -> dict[str, Any]:
        root = find_repo_root()
        hatch_info: dict[str, Any] = {"available": True, "path": hatch}

        try:
            result = subprocess.run(  # nosec B603
                [hatch, "version"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=root,
            )
            if result.returncode == 0:
                hatch_info["version"] = result.stdout.strip()
        except (subprocess.TimeoutExpired, OSError):
            pass

        try:
            result = subprocess.run(  # nosec B603
                [hatch, "env", "show", "--json"],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=root,
            )
            if result.returncode == 0:
                with contextlib.suppress(json.JSONDecodeError):
                    hatch_info["environments"] = json.loads(result.stdout)
        except (subprocess.TimeoutExpired, OSError):
            pass

        return hatch_info
