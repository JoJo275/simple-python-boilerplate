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

    # CI logging — emit log.info() every N steps in non-TTY
    # environments (GitHub Actions, Jenkins, etc.) so CI output
    # isn't silent during long-running loops.  Has no effect on
    # interactive terminals (the visual bar/spinner is used instead).
    bar = ProgressBar(total=100, label="Deploying", log_interval=10)
    spin = Spinner("Scanning", log_interval=25)

.. note::
    This is a shared internal module (prefixed with ``_``). It is excluded
    from the command reference generator and is not intended as a standalone
    CLI. See ADR 031 for script conventions.
"""

from __future__ import annotations

import logging
import shutil
import sys
import threading

from _colors import supports_unicode as _supports_unicode

SCRIPT_VERSION = "1.6.0"

__all__ = [
    "DEFAULT_BAR_COLOR",
    "DEFAULT_SPINNER_COLOR",
    "ProgressBar",
    "Spinner",
]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Color codes for bar fill (ANSI SGR)
# ---------------------------------------------------------------------------

_BAR_COLORS: dict[str, str] = {
    "green": "32",
    "red": "31",
    "yellow": "33",
    "blue": "34",
    "cyan": "36",
    "magenta": "35",
    "white": "37",
}

_SPINNER_COLORS: dict[str, str] = _BAR_COLORS.copy()

# ---------------------------------------------------------------------------
# Default colors — set these to a color name ("cyan", "green", etc.) to
# apply a default color to all ProgressBar / Spinner instances that don't
# pass an explicit ``color=`` argument.  Set to ``None`` for no default.
# ---------------------------------------------------------------------------

DEFAULT_BAR_COLOR: str | None = None
DEFAULT_SPINNER_COLOR: str | None = None


def _terminal_width() -> int:
    """Get terminal width, with a sensible fallback."""
    return shutil.get_terminal_size((80, 24)).columns


def _is_interactive() -> bool:
    """Return True if stdout is a TTY (not piped/redirected)."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


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

    def __init__(
        self,
        total: int,
        label: str = "Progress",
        log_interval: int = 0,
        color: str | None = None,
        *,
        pulse: bool = False,
    ) -> None:
        self.total = total
        self.label = label
        self.current = 0
        self._interactive = _is_interactive()
        self._fill, self._empty, self._lb, self._rb = _pick_bar_style()
        resolved_color = color or DEFAULT_BAR_COLOR
        self._color_code = _BAR_COLORS.get(resolved_color, "") if resolved_color else ""
        # Pulse mode: keep a subtle animation running between update()
        # calls so the bar looks alive even during long-running steps.
        self._pulse = pulse and self._interactive
        self._pulse_thread: threading.Thread | None = None
        self._pulse_stop = threading.Event()
        self._pulse_offset = 0
        # CI logging: In non-interactive environments (CI pipelines like
        # GitHub Actions, Jenkins, etc.) there is no TTY, so progress bars
        # are invisible — the runner just captures text logs.  Setting
        # log_interval to a positive int (e.g. 10) causes a log.info()
        # message every N steps, so CI output shows periodic progress
        # instead of silence during long-running loops.
        #
        # Default is 0 (off) — progress is only drawn on interactive TTYs.
        # Set to a positive int for CI visibility.
        self._log_interval = log_interval
        if total <= 0:
            logger.warning(
                "ProgressBar created with total=%d; progress will not render.", total
            )

    def __enter__(self) -> ProgressBar:
        """Support context-manager usage."""
        if self._pulse:
            self._start_pulse()
        return self

    def __exit__(self, *_: object) -> None:
        self.finish()

    def _start_pulse(self) -> None:
        """Start the background pulse animation thread."""
        if self._pulse_thread is not None:
            return
        self._pulse_stop.clear()
        self._pulse_thread = threading.Thread(target=self._pulse_loop, daemon=True)
        self._pulse_thread.start()

    def _pulse_loop(self) -> None:
        """Background loop that redraws with a shimmer effect."""
        while not self._pulse_stop.is_set():
            self._pulse_offset = (self._pulse_offset + 1) % 4
            self._draw("")
            self._pulse_stop.wait(0.15)

    def update(self, item_name: str = "") -> None:
        """Advance by one step and redraw.

        The counter is capped at ``total`` to prevent bar overflow if
        ``update()`` is called more times than expected.
        """
        self.current = min(self.current + 1, max(self.total, 1))
        if not self._interactive:
            # Emit periodic log messages in non-interactive mode (CI)
            if self._log_interval > 0 and self.current % self._log_interval == 0:
                logger.info("%s: %d/%d", self.label, self.current, self.total)
            return
        self._draw(item_name)

    def reset(self) -> None:
        """Reset the counter to zero for reuse."""
        self.current = 0

    def _draw(self, item_name: str = "") -> None:
        width = _terminal_width()
        # Guard against division by zero when total <= 0
        pct = int(self.current / self.total * 100) if self.total > 0 else 0
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

        filled = int(bar_width * self.current / self.total) if self.total > 0 else 0
        filled_str = self._fill * filled
        empty_str = self._empty * (bar_width - filled)
        if self._color_code and filled_str:
            filled_str = f"\033[{self._color_code}m{filled_str}\033[0m"
        bar = filled_str + empty_str

        line = f"\r{prefix}{self._lb}{bar}{self._rb}  {counter}  {display_name}"
        sys.stdout.write(line.ljust(width))
        sys.stdout.flush()

    def finish(self, message: str = "") -> None:
        """Complete the bar and move to a new line.

        Args:
            message: Optional final message to display (replaces the bar line).
        """
        self._pulse_stop.set()
        if self._pulse_thread is not None:
            self._pulse_thread.join(timeout=1.0)
            self._pulse_thread = None
        if self._interactive:
            if message:
                width = _terminal_width()
                sys.stdout.write(f"\r{message}".ljust(width) + "\n")
            else:
                sys.stdout.write("\n")
            sys.stdout.flush()


class Spinner:
    """Indeterminate spinner for operations without a known total.

    The spinner runs in a background thread so it keeps animating even
    while the main thread is blocked on I/O (subprocess calls, network
    requests, etc.).  Call ``update(item_name)`` to change the status
    text displayed alongside the spinner.

    Supports context-manager usage::

        with Spinner("Querying PyPI") as spin:
            for pkg in packages:
                result = fetch(pkg)
                spin.update(pkg)

    Or manual usage::

        spin = Spinner("Scanning")
        spin.start()
        spin.update("file1.yml")
        spin.update("file2.yml")
        spin.finish()
    """

    def __init__(
        self,
        label: str = "Working",
        log_interval: int = 0,
        color: str | None = None,
        interval: float = 0.08,
        *,
        keep_alive: bool = False,
    ) -> None:
        self.label = label
        self.count = 0
        self._interactive = _is_interactive()
        self._frames = _pick_spinner_frames()
        resolved_color = color or DEFAULT_SPINNER_COLOR
        self._color_code = (
            _SPINNER_COLORS.get(resolved_color, "") if resolved_color else ""
        )
        # keep_alive: when True, the spinner thread keeps animating
        # even when no update() calls are made, so the user sees
        # continuous activity during long-running blocking operations.
        # This is the default behaviour (the background thread always
        # spins).  When False the spinner still spins but the label
        # says "Working" until update() is called.
        self._keep_alive = keep_alive
        self._log_interval = log_interval
        self._interval = interval
        self._current_item: str = ""
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._frame_idx = 0

    def _spin_loop(self) -> None:
        """Background loop that redraws the spinner at a fixed interval."""
        while not self._stop_event.is_set():
            with self._lock:
                self._frame_idx += 1
                item = self._current_item
                count = self.count
            self._draw_frame(item, count)
            self._stop_event.wait(self._interval)

    def _draw_frame(self, item_name: str, count: int) -> None:
        width = _terminal_width()
        frame = self._frames[self._frame_idx % len(self._frames)]
        if self._color_code:
            frame = f"\033[{self._color_code}m{frame}\033[0m"
        display_name = _truncate(item_name, 40)
        line = f"\r  {frame} {self.label}  [{count}]  {display_name}"
        sys.stdout.write(line.ljust(width))
        sys.stdout.flush()

    def start(self) -> None:
        """Start the background spinner thread."""
        if self._interactive and self._thread is None:
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._spin_loop, daemon=True)
            self._thread.start()

    def __enter__(self) -> Spinner:
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.finish()

    def update(self, item_name: str = "") -> None:
        """Tick the spinner forward and update the displayed item."""
        with self._lock:
            self.count += 1
            self._current_item = item_name
        if (
            not self._interactive
            and self._log_interval > 0
            and self.count % self._log_interval == 0
        ):
            logger.info("%s: %d items", self.label, self.count)

    def reset(self) -> None:
        """Reset the counter to zero for reuse."""
        with self._lock:
            self.count = 0
            self._current_item = ""

    def finish(self, message: str = "") -> None:
        """Stop the background thread and clear the spinner line."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        if self._interactive:
            if message:
                sys.stdout.write(f"\r{message}".ljust(_terminal_width()) + "\n")
            else:
                sys.stdout.write("\r" + " " * _terminal_width() + "\r")
            sys.stdout.flush()
