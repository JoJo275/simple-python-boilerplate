"""Caching adapter for environment data collection.

Wraps ``_env_collectors.gather_env_info()`` with an in-memory cache
and TTL. Stores one previous scan for diff comparison.

Performance notes:
    - ``gather_env_info()`` is CPU/IO-bound (subprocess calls, filesystem
      scans). It runs in a thread-pool executor to avoid blocking the
      async event loop.
    - A background warmup task populates the cache at startup so the
      first page load is instant.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import time
from typing import Any

from _env_collectors import Tier, gather_env_info
from _env_collectors._redact import RedactLevel

_DEFAULT_TTL = 30  # seconds

# Thread pool for running blocking collector calls off the event loop
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


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


def _collect_sync(
    tier: Tier,
    redact_level: RedactLevel,
) -> dict[str, Any]:
    """Blocking collection — runs in thread pool."""
    return gather_env_info(tier=tier, redact_level=redact_level)


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


async def get_report_async(
    *,
    tier: Tier = Tier.STANDARD,
    redact_level: RedactLevel = RedactLevel.SECRETS,
    force: bool = False,
) -> dict[str, Any]:
    """Async version — runs collection in thread pool to avoid blocking.

    Args:
        tier: Collection tier.
        redact_level: Redaction level.
        force: Force fresh scan (ignore cache).

    Returns:
        Full environment report dict.
    """
    if force or _cache.is_stale():
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(_executor, _collect_sync, tier, redact_level)
        _cache.update(data)
    return _cache.current  # type: ignore[return-value]


def get_previous() -> dict[str, Any] | None:
    """Return the previous scan result (for diff)."""
    return _cache.previous


def invalidate_cache() -> None:
    """Force the next ``get_report()`` call to re-scan."""
    _cache.invalidate()


async def warmup_cache(
    tier: Tier = Tier.STANDARD,
    redact_level: RedactLevel = RedactLevel.SECRETS,
) -> None:
    """Pre-populate cache in background so first page load is instant."""
    await get_report_async(tier=tier, redact_level=redact_level)
