"""Insights collector — derived warnings from cross-section analysis."""

from __future__ import annotations

from typing import Any, ClassVar

from _env_collectors._base import BaseCollector

_tier = None


def _get_tier():  # type: ignore[no-untyped-def]
    global _tier
    if _tier is None:
        from _env_collectors import Tier

        _tier = Tier
    return _tier


class InsightsCollector(BaseCollector):
    """Derive warnings and recommendations from already-collected sections."""

    name = "insights"
    timeout = 5.0
    _sections: ClassVar[dict[str, Any]] = {}

    @property
    def tier(self):  # type: ignore[override]
        return _get_tier().STANDARD

    def collect(self) -> dict[str, Any]:
        warnings: list[dict[str, str]] = []
        s = self._sections

        # Virtualenv not active
        runtimes = s.get("runtimes", {})
        python_info = runtimes.get("python", {})
        if not python_info.get("in_venv", False):
            warnings.append(
                {
                    "severity": "warn",
                    "message": "Not running inside a virtual environment",
                    "section": "venv",
                }
            )

        # Git dirty
        git = s.get("git", {})
        if git.get("dirty"):
            warnings.append(
                {
                    "severity": "warn",
                    "message": "Git working tree is dirty — builds may be non-reproducible",
                    "section": "git",
                }
            )

        # PATH has dead entries
        path_data = s.get("path", {})
        dead = path_data.get("dead_entries", 0)
        if dead > 0:
            warnings.append(
                {
                    "severity": "warn",
                    "message": f"PATH has {dead} non-existent director{'ies' if dead != 1 else 'y'}",
                    "section": "path",
                }
            )

        # PATH duplicates
        dups = path_data.get("duplicates", 0)
        if dups > 0:
            warnings.append(
                {
                    "severity": "info",
                    "message": f"PATH has {dups} duplicate entr{'ies' if dups != 1 else 'y'}",
                    "section": "path",
                }
            )

        # Secret env vars found
        security = s.get("security", {})
        secret_vars = security.get("secret_env_vars", [])
        if secret_vars:
            warnings.append(
                {
                    "severity": "warn",
                    "message": f"{len(secret_vars)} secret-like environment variable(s) detected",
                    "section": "security",
                }
            )

        # Insecure PATH
        insecure = security.get("insecure_path_entries", [])
        if insecure:
            warnings.append(
                {
                    "severity": "fail",
                    "message": f"{len(insecure)} insecure PATH entr{'ies' if len(insecure) != 1 else 'y'} found",
                    "section": "security",
                }
            )

        # SSH keys exposed
        ssh = security.get("ssh_keys_exposed", [])
        if ssh:
            warnings.append(
                {
                    "severity": "fail",
                    "message": f"{len(ssh)} SSH/private key(s) exposed in environment",
                    "section": "security",
                }
            )

        # Filesystem: disk nearly full
        fs = s.get("filesystem", {})
        disk = fs.get("disk", {})
        pct = disk.get("percent_used", 0)
        if pct > 90:
            warnings.append(
                {
                    "severity": "fail",
                    "message": f"Disk {pct}% full — installs/builds may fail",
                    "section": "filesystem",
                }
            )
        elif pct > 80:
            warnings.append(
                {
                    "severity": "warn",
                    "message": f"Disk {pct}% full — consider freeing space",
                    "section": "filesystem",
                }
            )

        # Temp dir not writable
        writable = fs.get("writable", {})
        tmp = writable.get("temp_dir", {})
        if tmp and not tmp.get("writable", True):
            warnings.append(
                {
                    "severity": "fail",
                    "message": "Temp directory is not writable",
                    "section": "filesystem",
                }
            )

        # Network: DNS or outbound issues
        network = s.get("network", {})
        if not network.get("dns_resolves", True):
            warnings.append(
                {
                    "severity": "warn",
                    "message": "DNS resolution failed (pypi.org) — package installs may fail",
                    "section": "network",
                }
            )
        elif not network.get("outbound_https", True):
            warnings.append(
                {
                    "severity": "warn",
                    "message": "DNS works but outbound HTTPS is blocked — package installs may fail",
                    "section": "network",
                }
            )

        # Container/CI detection
        container = s.get("container", {})
        if container.get("ci"):
            warnings.append(
                {
                    "severity": "info",
                    "message": f"CI environment detected: {container['ci']}",
                    "section": "container",
                }
            )
        if container.get("wsl"):
            warnings.append(
                {
                    "severity": "info",
                    "message": "Running under WSL — path behavior differs from native Windows",
                    "section": "container",
                }
            )

        return {"warnings": warnings, "count": len(warnings)}
