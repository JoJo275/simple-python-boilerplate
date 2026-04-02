"""Caching adapter for environment data collection.

Wraps ``_env_collectors.gather_env_info()`` with an in-memory cache
and TTL. Stores one previous scan for diff comparison.
"""

from __future__ import annotations

import time
from typing import Any

from _env_collectors import Tier, gather_env_info
from _env_collectors._redact import RedactLevel

_DEFAULT_TTL = 30  # seconds


class _Cache:
    """Simple in-memory cache with TTL."""

    def __init__(self) -> None:
        self.current: dict[str, Any] | None = None
        self.previous: dict[str, Any] | None = None
        self.timestamp: float = 0.0
        self.ttl: float = _DEFAULT_TTL

    def is_stale(self) -> bool:
        return self.current is None or (time.monotonic() - self.timestamp) > self.ttl

    def update(self, data: dict[str, Any]) -> None:
        self.previous = self.current
        self.current = data
        self.timestamp = time.monotonic()

    def invalidate(self) -> None:
        self.timestamp = 0.0


_cache = _Cache()


def get_report(
    *,
    tier: Tier = Tier.STANDARD,
    redact_level: RedactLevel = RedactLevel.SECRETS,
    force: bool = False,
) -> dict[str, Any]:
    """Get environment report, using cache if not stale.

    Args:
        tier: Collection tier.
        redact_level: Redaction level.
        force: Force fresh scan (ignore cache).

    Returns:
        Full environment report dict.
    """
    if force or _cache.is_stale():
        data = gather_env_info(tier=tier, redact_level=redact_level)
        _cache.update(data)
    return _cache.current  # type: ignore[return-value]


def get_previous() -> dict[str, Any] | None:
    """Return the previous scan result (for diff)."""
    return _cache.previous


def invalidate_cache() -> None:
    """Force the next ``get_report()`` call to re-scan."""
    _cache.invalidate()
