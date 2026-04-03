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
                    "hint": "Running outside a venv means pip install affects the system Python.",
                    "action": "Run 'hatch shell' to enter the project virtual environment.",
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
                    "hint": "Uncommitted changes mean version tags and builds won't be reproducible.",
                    "action": "Review changes with 'git status' then commit or stash.",
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
                    "hint": "Dead PATH entries slow down command lookup and can cause confusing errors.",
                    "action": "Remove stale entries from your PATH environment variable.",
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
                    "hint": "Duplicate PATH entries are harmless but indicate messy shell config.",
                    "action": "Clean up duplicate entries in your shell profile (.bashrc, $PROFILE, etc.).",
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
                    "hint": "Environment variables matching secret patterns (API_KEY, TOKEN, etc.) are visible to all processes.",
                    "action": "Use a .env file or secrets manager instead of exporting secrets in shell config.",
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
                    "hint": "World-writable directories in PATH allow any user to inject malicious executables.",
                    "action": "Remove world-writable directories from PATH or fix their permissions (chmod 755).",
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
                    "hint": "Private key paths in environment variables risk accidental exposure in logs or error reports.",
                    "action": "Use an SSH agent instead of storing key paths in environment variables.",
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
                    "hint": "Very low disk space will cause pip installs, builds, and test runs to fail.",
                    "action": "Free disk space: remove old venvs, Docker images, or build artifacts.",
                }
            )
        elif pct > 80:
            warnings.append(
                {
                    "severity": "warn",
                    "message": f"Disk {pct}% full — consider freeing space",
                    "section": "filesystem",
                    "hint": "Getting close to full disk. Builds and installs may start failing soon.",
                    "action": "Run 'task clean' to remove build caches, or clear Docker/temp files.",
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
                    "hint": "Many tools (pip, pytest, compilers) need a writable temp directory.",
                    "action": "Check permissions on the TMPDIR/TEMP directory, or set TMPDIR to a writable path.",
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
                    "hint": "Cannot resolve pypi.org — you may be offline or behind a restrictive firewall.",
                    "action": "Check your network connection and DNS settings. Try 'nslookup pypi.org'.",
                }
            )
        elif not network.get("outbound_https", True):
            warnings.append(
                {
                    "severity": "warn",
                    "message": "DNS works but outbound HTTPS is blocked — package installs may fail",
                    "section": "network",
                    "hint": "DNS resolves but HTTPS connections are blocked — proxy or firewall issue.",
                    "action": "Configure pip to use your proxy: pip config set global.proxy http://proxy:port",
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
                    "hint": "Running in a CI environment — some local dev features may behave differently.",
                    "action": "No action needed. CI-specific behavior is expected.",
                }
            )
        if container.get("wsl"):
            warnings.append(
                {
                    "severity": "info",
                    "message": "Running under WSL — path behavior differs from native Windows",
                    "section": "container",
                    "hint": "WSL translates paths between Linux and Windows formats, which can cause issues with some tools.",
                    "action": "Use Linux-native paths when possible. Access Windows files via /mnt/c/.",
                }
            )

        return {"warnings": warnings, "count": len(warnings)}
