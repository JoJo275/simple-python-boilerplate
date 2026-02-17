#!/usr/bin/env python3
"""Clean utility for repository maintenance tasks.

Usage:
    spb-clean --todo     Archive completed TODO items

Or if running as a script:
    python -m simple_python_boilerplate.dev_tools.clean --todo
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


def get_repo_root() -> Path:
    """Find the repository root by looking for pyproject.toml."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback to current working directory
    return Path.cwd()


def archive_todos() -> int:
    """Move completed TODO items from todo.md to archive.md.

    Returns:
        Number of items archived.
    """
    repo_root = get_repo_root()
    todo_file = repo_root / "docs" / "notes" / "todo.md"
    archive_file = repo_root / "docs" / "notes" / "archive.md"

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
        # Remove the item and any trailing newline
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
        # Add new month section at the end
        if not archive_content.endswith("\n"):
            archive_content += "\n"
        archive_content += f"\n{month_header}\n\n### Completed\n\n"

    # Find where to insert items (after the month's "### Completed" or after month header)
    month_section_pattern = re.compile(
        rf"({re.escape(month_header)}.*?)(### Completed\n+)", re.DOTALL
    )

    match = month_section_pattern.search(archive_content)
    if match:
        # Insert after "### Completed\n"
        insert_pos = match.end()
        items_text = "\n".join(completed_items) + "\n"
        archive_content = (
            archive_content[:insert_pos] + items_text + archive_content[insert_pos:]
        )
    else:
        # Fallback: just append to end with the items
        items_text = "\n".join(completed_items) + "\n"
        archive_content += items_text

    # Write updated files
    todo_file.write_text(new_todo_content, encoding="utf-8")
    archive_file.write_text(archive_content, encoding="utf-8")

    print(f"Archived {len(completed_items)} completed item(s) to {current_month}:")
    for item in completed_items:
        print(f"  {item}")

    return len(completed_items)


def main() -> int:
    """Main entry point for the clean CLI.

    Returns:
        Exit code (0 = success).
    """
    parser = argparse.ArgumentParser(
        prog="spb-clean",
        description="Repository maintenance and cleanup utilities.",
        epilog="Example: spb-clean --todo",
    )

    # Add arguments for different clean actions
    parser.add_argument(
        "--todo",
        action="store_true",
        help="Archive completed TODO items from docs/notes/todo.md",
    )

    # Placeholder for future clean actions
    # parser.add_argument(
    #     "--cache",
    #     action="store_true",
    #     help="Clean __pycache__ and .pyc files",
    # )
    # parser.add_argument(
    #     "--build",
    #     action="store_true",
    #     help="Clean build artifacts (dist/, build/, *.egg-info)",
    # )

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return 0

    # Execute requested actions
    if args.todo:
        archive_todos()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
