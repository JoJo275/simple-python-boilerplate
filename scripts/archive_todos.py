#!/usr/bin/env python3
"""Archive completed TODO items from docs/notes/todo.md.

Moves checked items (- [x]) from todo.md to archive.md, organized by month.
This is a dev utility for personal note management, not distributed with
the package.

Usage::

    python scripts/archive_todos.py
    python scripts/archive_todos.py --dry-run
    task clean:todo
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def archive_todos(*, dry_run: bool = False) -> int:
    """Move completed TODO items from todo.md to archive.md.

    Args:
        dry_run: If True, show what would change without modifying files.

    Returns:
        Number of items archived.
    """
    todo_file = ROOT / "docs" / "notes" / "todo.md"
    archive_file = ROOT / "docs" / "notes" / "archive.md"

    # Validate files exist
    if not todo_file.exists():
        print(f"Error: {todo_file} not found")
        sys.exit(1)

    if not archive_file.exists():
        print(f"Error: {archive_file} not found")
        sys.exit(1)

    # Read todo.md
    todo_content = todo_file.read_text(encoding="utf-8")

    # Find all completed items (case-insensitive [x] or [X])
    completed_pattern = re.compile(r"^- \[[xX]\] .+$", re.MULTILINE)
    completed_items = completed_pattern.findall(todo_content)

    if not completed_items:
        print("No completed items found in todo.md")
        return 0

    # Remove completed items from todo.md
    new_todo_content = todo_content
    for item in completed_items:
        new_todo_content = new_todo_content.replace(item + "\n", "")

    # Clean up any double blank lines created by removal
    new_todo_content = re.sub(r"\n{3,}", "\n\n", new_todo_content)

    # Read archive.md
    archive_content = archive_file.read_text(encoding="utf-8")

    # Get current month header
    current_month = datetime.now().strftime("%B %Y")  # e.g., "January 2026"
    month_header = f"## {current_month}"

    # Check if month header exists
    if month_header not in archive_content:
        if not archive_content.endswith("\n"):
            archive_content += "\n"
        archive_content += f"\n{month_header}\n\n### Completed\n\n"

    # Find where to insert items
    month_section_pattern = re.compile(
        rf"({re.escape(month_header)}.*?)(### Completed\n+)", re.DOTALL
    )

    match = month_section_pattern.search(archive_content)
    if match:
        insert_pos = match.end()
        items_text = "\n".join(completed_items) + "\n"
        archive_content = (
            archive_content[:insert_pos] + items_text + archive_content[insert_pos:]
        )
    else:
        items_text = "\n".join(completed_items) + "\n"
        archive_content += items_text

    if dry_run:
        print(f"Would archive {len(completed_items)} item(s) to {current_month}:")
        for item in completed_items:
            print(f"  {item}")
        return len(completed_items)

    # Write updated files
    todo_file.write_text(new_todo_content, encoding="utf-8")
    archive_file.write_text(archive_content, encoding="utf-8")

    print(f"Archived {len(completed_items)} completed item(s) to {current_month}:")
    for item in completed_items:
        print(f"  {item}")

    return len(completed_items)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="archive_todos",
        description="Archive completed TODO items from docs/notes/todo.md.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without modifying files",
    )
    args = parser.parse_args()

    archive_todos(dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
