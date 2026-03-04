"""Shared progress-indicator utilities for scripts.

Provides a lightweight, zero-dependency progress bar and spinner that
adapt to terminal capabilities (Unicode vs ASCII fallback).

This module is intended to be imported by other scripts in the
``scripts/`` directory — it is not a CLI and should not be run directly.

Usage::

    from _progress import ProgressBar, Spinner

    # Determinate progress (known total)
    bar = ProgressBar(total=72, label="Applying labels")
    for item in items:
        bar.update(item_name)
    bar.finish()

    # Indeterminate progress (unknown total / spinner)
    with Spinner("Fetching latest versions") as spin:
        for pkg in packages:
            spin.update(pkg)
    # spinner auto-finishes on context-manager exit

.. note::
    This is a shared internal module (prefixed with ``_``). It is excluded
    from the command reference generator and is not intended as a standalone
    CLI. See ADR 031 for script conventions.
"""

from __future__ import annotations

import locale
import logging
import shutil
import sys

SCRIPT_VERSION = "1.1.0"

__all__ = ["ProgressBar", "Spinner"]

logger = logging.getLogger(__name__)


def _terminal_width() -> int:
    """Get terminal width, with a sensible fallback."""
    return shutil.get_terminal_size((80, 24)).columns


def _is_interactive() -> bool:
    """Return True if stdout is a TTY (not piped/redirected)."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _supports_unicode() -> bool:
    """Return True if the terminal likely supports Unicode characters."""
    try:
        encoding = sys.stdout.encoding or locale.getpreferredencoding(False)
        return encoding.lower().replace("-", "") in {"utf8", "utf16", "utf32"}
    except Exception:
        return False


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with an appropriate ellipsis."""
    if len(text) <= max_len:
        return text
    ellipsis = "\u2026" if _supports_unicode() else "..."
    return text[: max_len - len(ellipsis)] + ellipsis


# ── Bar styles ────────────────────────────────────────────────

# (filled, empty, left_bracket, right_bracket)
_STYLE_UNICODE = ("\u2588", "\u2591", "[", "]")  # █ ░
_STYLE_ASCII = ("#", "-", "[", "]")  # [###-----]


def _pick_bar_style() -> tuple[str, str, str, str]:
    """Choose the best bar style the terminal can render."""
    return _STYLE_UNICODE if _supports_unicode() else _STYLE_ASCII


# ── Spinner frames ────────────────────────────────────────────

_SPINNER_UNICODE = [
    "\u280b",
    "\u2819",
    "\u2838",
    "\u2834",
    "\u2826",
    "\u2807",
]  # braille
_SPINNER_ASCII = ["|", "/", "-", "\\"]


def _pick_spinner_frames() -> list[str]:
    """Choose spinner frames the terminal can render."""
    return _SPINNER_UNICODE if _supports_unicode() else _SPINNER_ASCII


class ProgressBar:
    """Determinate progress bar for loops with a known total.

    Example::

        bar = ProgressBar(total=72, label="Applying labels")
        for i, item in enumerate(items, 1):
            do_work(item)
            bar.update(item.name)
        bar.finish()
    """

    def __init__(self, total: int, label: str = "Progress") -> None:
        self.total = total
        self.label = label
        self.current = 0
        self._interactive = _is_interactive()
        self._fill, self._empty, self._lb, self._rb = _pick_bar_style()
        if total <= 0:
            logger.warning(
                "ProgressBar created with total=%d; progress will not render.", total
            )

    def __enter__(self) -> ProgressBar:
        """Support context-manager usage."""
        return self

    def __exit__(self, *_: object) -> None:
        self.finish()

    def update(self, item_name: str = "") -> None:
        """Advance by one step and redraw."""
        self.current += 1
        if not self._interactive:
            return
        self._draw(item_name)

    def _draw(self, item_name: str = "") -> None:
        width = _terminal_width()
        pct = int(self.current / self.total * 100) if self.total else 0
        counter = f"{self.current}/{self.total} ({pct:>3}%)"
        prefix = f"{self.label}  "
        display_name = _truncate(item_name, 30)

        # Calculate bar width from remaining space
        overhead = (
            len(prefix)
            + len(self._lb)
            + len(self._rb)
            + len(counter)
            + len(display_name)
            + 6
        )
        bar_width = max(width - overhead, 10)

        filled = int(bar_width * self.current / self.total) if self.total else 0
        bar = self._fill * filled + self._empty * (bar_width - filled)

        line = f"\r{prefix}{self._lb}{bar}{self._rb}  {counter}  {display_name}"
        sys.stdout.write(line.ljust(width))
        sys.stdout.flush()

    def finish(self, message: str = "") -> None:
        """Complete the bar and move to a new line.

        Args:
            message: Optional final message to display (replaces the bar line).
        """
        if self._interactive:
            if message:
                width = _terminal_width()
                sys.stdout.write(f"\r{message}".ljust(width) + "\n")
            else:
                sys.stdout.write("\n")
            sys.stdout.flush()


class Spinner:
    """Indeterminate spinner for operations without a known total.

    Supports context-manager usage::

        with Spinner("Querying PyPI") as spin:
            for pkg in packages:
                result = fetch(pkg)
                spin.update(pkg)

    Or manual usage::

        spin = Spinner("Scanning")
        spin.update("file1.yml")
        spin.update("file2.yml")
        spin.finish()
    """

    def __init__(self, label: str = "Working") -> None:
        self.label = label
        self.count = 0
        self._interactive = _is_interactive()
        self._frames = _pick_spinner_frames()

    def __enter__(self) -> Spinner:
        return self

    def __exit__(self, *_: object) -> None:
        self.finish()

    def update(self, item_name: str = "") -> None:
        """Tick the spinner forward and redraw."""
        self.count += 1
        if not self._interactive:
            return
        self._draw(item_name)

    def _draw(self, item_name: str = "") -> None:
        width = _terminal_width()
        frame = self._frames[self.count % len(self._frames)]
        display_name = _truncate(item_name, 40)
        line = f"\r  {frame} {self.label}  [{self.count}]  {display_name}"
        sys.stdout.write(line.ljust(width))
        sys.stdout.flush()

    def finish(self, message: str = "") -> None:
        """Clear the spinner line and optionally print a final message."""
        if self._interactive:
            if message:
                sys.stdout.write(f"\r{message}".ljust(_terminal_width()) + "\n")
            else:
                sys.stdout.write("\r" + " " * _terminal_width() + "\r")
            sys.stdout.flush()
