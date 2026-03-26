"""Shared dashboard UI utilities for scripts.

Provides a uniform output layout based on the ``git_doctor.py`` dashboard
style: box-drawing headers, section dividers, key-value pairs, and
summary footers.  Every CLI script imports from here so output has a
consistent, professional look with a per-script color theme.

The module respects terminal capabilities (Unicode/ASCII fallback) and
integrates with :mod:`_colors` for color detection and styling.

Usage::

    from _ui import UI

    ui = UI(title="Python Support", version="1.0.0", theme="green")
    ui.header()                          # ╔══ Python Support  v1.0.0 ══╗
    ui.section("Sources")                # ┌── Sources ──────────────────┐
    ui.kv("requires-python", ">=3.11")   #     requires-python:   >=3.11
    ui.kv("Hatch matrix", "3.11, 3.12, 3.13")
    ui.status_line("check", "All sources consistent", "green")
    ui.footer(passed=5, failed=0, warned=0)

.. note::
    This is a shared internal module (prefixed with ``_``). It is excluded
    from the command reference generator and is not intended as a standalone
    CLI. See ADR 031 for script conventions.
"""

from __future__ import annotations

from typing import ClassVar

from _colors import Colors, supports_unicode, unicode_symbols

__all__ = ["UI"]

SCRIPT_VERSION = "1.0.0"


class UI:
    """Uniform dashboard output matching the git_doctor.py style.

    Args:
        title: Dashboard title shown in the header box.
        version: Script version shown dimmed next to the title.
        theme: Color name for the main border/accent color.
            One of: ``"cyan"``, ``"blue"``, ``"green"``, ``"yellow"``,
            ``"magenta"``, ``"red"``, ``"white"``.
        no_color: Force disable colors (e.g. from ``--no-color`` flag).
    """

    # Map from color name to Colors method name
    _THEME_METHODS: ClassVar[dict[str, str]] = {
        "cyan": "cyan",
        "blue": "blue",
        "green": "green",
        "yellow": "yellow",
        "magenta": "magenta",
        "red": "red",
        "white": "white",
    }

    def __init__(
        self,
        title: str,
        version: str,
        theme: str = "cyan",
        *,
        no_color: bool = False,
    ) -> None:
        self.title = title
        self.version = version
        self.theme = theme
        self.c = Colors(enabled=not no_color)
        self.sym = unicode_symbols()
        self._use_unicode = supports_unicode()

        # Box-drawing characters (Unicode with ASCII fallback)
        u = self._use_unicode
        self.h_line = "\u2500" if u else "-"  # ─
        self.h_double = "\u2550" if u else "="  # ═
        self.tl = "\u250c" if u else "+"  # ┌
        self.tr = "\u2510" if u else "+"  # ┐
        self.bl = "\u2514" if u else "+"  # └
        self.br = "\u2518" if u else "+"  # ┘
        self.tl_d = "\u2554" if u else "+"  # ╔
        self.tr_d = "\u2557" if u else "+"  # ╗
        self.bl_d = "\u255a" if u else "+"  # ╚
        self.br_d = "\u255d" if u else "+"  # ╝
        self.vl = "\u2502" if u else "|"  # │
        self.vl_d = "\u2551" if u else "|"  # ║
        self.dot = "\u2022" if u else "*"  # •

    @property
    def _accent(self) -> str:
        """Return the method name for the theme color."""
        return self._THEME_METHODS.get(self.theme, "cyan")

    def _themed(self, text: str) -> str:
        """Apply the theme color to *text*."""
        return getattr(self.c, self._accent)(text)

    # ── Layout elements ────────────────────────────────────────

    def header(self, *, width: int = 60) -> None:
        """Print the main dashboard header with double-border box."""
        border = self.h_double * width
        print()
        print(self.c.bold(self._themed(f"  {self.tl_d}{border}{self.tr_d}")))
        print(
            f"  {self.c.bold(self._themed(self.vl_d))} "
            f"{self.c.bold(self._themed(self.title))}  "
            f"{self.c.dim(f'v{self.version}')}"
        )
        print(self.c.bold(self._themed(f"  {self.bl_d}{border}{self.br_d}")))

    def section(self, title: str, *, width: int = 60) -> None:
        """Print a section header with single-border box."""
        border = self.h_line * width
        print()
        print(self._themed(f"  {self.tl}{border}{self.tr}"))
        print(f"  {self._themed(self.vl)} {self.c.bold(title)}")
        print(self._themed(f"  {self.bl}{border}{self.br}"))

    def kv(
        self,
        label: str,
        value: str,
        *,
        width: int = 22,
        hint: str = "",
    ) -> None:
        """Print a key-value pair with consistent alignment.

        Args:
            label: Left-side label.
            value: Right-side value.
            width: Column width for label alignment.
            hint: Optional hint shown dimmed below the value.
        """
        print(f"    {label + ':':{width}s} {value}")
        if hint:
            print(f"    {'':{width}s} {self.c.dim(hint)}")

    def status_line(
        self,
        icon_name: str,
        message: str,
        color: str = "green",
    ) -> None:
        """Print a status indicator line (e.g. ✓ All checks passed).

        Args:
            icon_name: Symbol key from ``unicode_symbols()`` —
                ``"check"``, ``"cross"``, ``"warn"``, ``"info"``.
            message: Status message text.
            color: Color for both icon and message.
        """
        icon = self.sym.get(icon_name, icon_name)
        color_fn = getattr(self.c, color, self.c.green)
        print(f"  {color_fn(icon)} {color_fn(message)}")

    def info_line(self, message: str) -> None:
        """Print a dimmed informational line (indented)."""
        print(f"    {self.c.dim(message)}")

    def separator(self, *, width: int = 60, double: bool = False) -> None:
        """Print a horizontal separator line."""
        char = self.h_double if double else self.h_line
        print(f"  {self.c.dim(char * width)}")

    def blank(self) -> None:
        """Print a blank line."""
        print()

    def table_header(
        self,
        columns: list[tuple[str, int]],
    ) -> None:
        """Print a table header row with underlines.

        Args:
            columns: List of ``(header_text, column_width)`` tuples.
        """
        hdr_parts = []
        line_parts = []
        for text, w in columns:
            hdr_parts.append(self.c.dim(text.ljust(w)))
            line_parts.append(self.c.dim(self.h_line * w))
        print(f"    {' '.join(hdr_parts)}")
        print(f"    {' '.join(line_parts)}")

    def table_row(
        self,
        cells: list[tuple[str, int]],
    ) -> None:
        """Print a table data row.

        Args:
            cells: List of ``(cell_text, column_width)`` tuples.
                Cell text may contain ANSI codes; alignment uses
                the raw width.
        """
        parts = []
        for text, w in cells:
            # Pad based on visible length (strip ANSI for measurement)
            from _colors import strip_ansi

            visible_len = len(strip_ansi(text))
            padding = max(w - visible_len, 0)
            parts.append(text + " " * padding)
        print(f"    {' '.join(parts)}")

    def footer(
        self,
        passed: int,
        failed: int,
        warned: int = 0,
        *,
        elapsed: float | None = None,
    ) -> None:
        """Print a summary footer with pass/fail/warn counts.

        Args:
            passed: Number of passed checks.
            failed: Number of failed checks.
            warned: Number of warnings.
            elapsed: Optional elapsed time in seconds.
        """
        total = passed + failed + warned
        print()
        self.separator(double=True)

        parts = [self.c.green(f"{passed} passed")]
        if warned:
            parts.append(self.c.yellow(f"{warned} warned"))
        if failed:
            parts.append(self.c.red(f"{failed} failed"))

        summary = f"  {self.c.bold('Summary:')} {', '.join(parts)} / {total} total"
        print(summary)

        if elapsed is not None:
            print(f"  {self.c.dim(f'Completed in {elapsed:.1f}s')}")
        print()

    # ── Convenience: quick status bar ──────────────────────────

    def quick_status(
        self,
        items: list[tuple[str, str, str]],
        *,
        label_width: int = 22,
    ) -> None:
        """Print a quick status bar (like git_doctor's top indicators).

        Args:
            items: List of ``(label, status_text, color)`` tuples.
                ``color`` is a Colors method name.
            label_width: Padding width for labels.
        """
        print()
        for label, status_text, color in items:
            icon_name = {
                "green": "check",
                "yellow": "warn",
                "red": "cross",
            }.get(color, "info")
            icon = self.sym.get(icon_name, "?")
            color_fn = getattr(self.c, color, self.c.green)
            print(
                f"  {color_fn(icon)} "
                f"{self.c.dim(label.ljust(label_width))} "
                f"{color_fn(status_text)}"
            )
