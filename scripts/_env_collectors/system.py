"""System info collector — OS, arch, hostname, shell, cwd, privilege, locale."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any

from _env_collectors._base import BaseCollector

# Avoid circular import at module level
_tier = None


def _get_tier():  # type: ignore[no-untyped-def]
    global _tier
    if _tier is None:
        from _env_collectors import Tier

        _tier = Tier
    return _tier


class SystemCollector(BaseCollector):
    """Collect OS, architecture, hostname, shell, cwd, privilege, locale."""

    name = "system"
    timeout = 5.0

    @property
    def tier(self):  # type: ignore[override]
        return _get_tier().MINIMAL

    def collect(self) -> dict[str, Any]:
        env = os.environ
        shell = env.get("SHELL") or env.get("COMSPEC") or "unknown"

        is_root = False
        if sys.platform != "win32":
            is_root = os.getuid() == 0  # type: ignore[attr-defined]
        else:
            import ctypes

            is_root = bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]

        import locale

        try:
            current_locale = locale.getlocale()
            locale_str = (
                f"{current_locale[0]}.{current_locale[1]}"
                if current_locale[0]
                else "unknown"
            )
        except Exception:
            locale_str = "unknown"

        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "kernel": platform.platform(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "username": env.get("USER") or env.get("USERNAME") or "unknown",
            "shell": shell,
            "cwd": str(Path.cwd()),
            "privilege": "root" if is_root else "user",
            "locale": locale_str,
            "cpu_count": os.cpu_count(),
            "encoding": sys.getdefaultencoding(),
            "filesystem_encoding": sys.getfilesystemencoding(),
        }
