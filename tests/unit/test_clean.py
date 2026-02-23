"""Unit tests for the dev_tools.clean module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from simple_python_boilerplate.dev_tools.clean import (
    archive_todos,
    get_repo_root,
    main,
)


class TestGetRepoRoot:
    """Tests for the get_repo_root function."""

    def test_finds_repo_root_from_module_location(self) -> None:
        """Should find repo root by locating pyproject.toml."""
        result = get_repo_root()
        assert isinstance(result, Path)
        assert (result / "pyproject.toml").exists()

    def test_returns_path_object(self) -> None:
        """Should return a Path object."""
        result = get_repo_root()
        assert isinstance(result, Path)


class TestArchiveTodos:
    """Tests for the archive_todos function."""

    def test_archive_with_no_completed_items(self, tmp_path: Path) -> None:
        """Should return 0 when no completed items exist."""
        # Setup mock repo structure
        notes_dir = tmp_path / "docs" / "notes"
        notes_dir.mkdir(parents=True)

        todo_file = notes_dir / "todo.md"
        todo_file.write_text("# TODO\n\n- [ ] Incomplete task\n", encoding="utf-8")

        archive_file = notes_dir / "archive.md"
        archive_file.write_text("# Archive\n\n", encoding="utf-8")

        # Patch get_repo_root to return our tmp_path
        with patch(
            "simple_python_boilerplate.dev_tools.clean.get_repo_root",
            return_value=tmp_path,
        ):
            result = archive_todos()
            assert result == 0

    def test_archive_single_completed_item(self, tmp_path: Path) -> None:
        """Should archive a single completed item."""
        notes_dir = tmp_path / "docs" / "notes"
        notes_dir.mkdir(parents=True)

        todo_file = notes_dir / "todo.md"
        todo_file.write_text(
            "# TODO\n\n- [x] Completed task\n- [ ] Incomplete task\n",
            encoding="utf-8",
        )

        archive_file = notes_dir / "archive.md"
        archive_file.write_text("# Archive\n\n", encoding="utf-8")

        with patch(
            "simple_python_boilerplate.dev_tools.clean.get_repo_root",
            return_value=tmp_path,
        ):
            result = archive_todos()
            assert result == 1

            # Verify todo.md no longer has the completed item
            todo_content = todo_file.read_text(encoding="utf-8")
            assert "[x] Completed task" not in todo_content
            assert "[ ] Incomplete task" in todo_content

    def test_archive_multiple_completed_items(self, tmp_path: Path) -> None:
        """Should archive multiple completed items."""
        notes_dir = tmp_path / "docs" / "notes"
        notes_dir.mkdir(parents=True)

        todo_file = notes_dir / "todo.md"
        todo_file.write_text(
            "# TODO\n\n- [x] Task 1\n- [X] Task 2\n- [ ] Task 3\n",
            encoding="utf-8",
        )

        archive_file = notes_dir / "archive.md"
        archive_file.write_text("# Archive\n\n", encoding="utf-8")

        with patch(
            "simple_python_boilerplate.dev_tools.clean.get_repo_root",
            return_value=tmp_path,
        ):
            result = archive_todos()
            assert result == 2

    def test_archive_exits_when_todo_file_missing(self, tmp_path: Path) -> None:
        """Should exit with error when todo.md doesn't exist."""
        notes_dir = tmp_path / "docs" / "notes"
        notes_dir.mkdir(parents=True)

        # Only create archive, not todo
        archive_file = notes_dir / "archive.md"
        archive_file.write_text("# Archive\n\n", encoding="utf-8")

        with (
            patch(
                "simple_python_boilerplate.dev_tools.clean.get_repo_root",
                return_value=tmp_path,
            ),
            pytest.raises(SystemExit),
        ):
            archive_todos()

    def test_archive_exits_when_archive_file_missing(self, tmp_path: Path) -> None:
        """Should exit with error when archive.md doesn't exist."""
        notes_dir = tmp_path / "docs" / "notes"
        notes_dir.mkdir(parents=True)

        # Only create todo, not archive
        todo_file = notes_dir / "todo.md"
        todo_file.write_text("# TODO\n\n- [x] Completed\n", encoding="utf-8")

        with (
            patch(
                "simple_python_boilerplate.dev_tools.clean.get_repo_root",
                return_value=tmp_path,
            ),
            pytest.raises(SystemExit),
        ):
            archive_todos()


class TestMain:
    """Tests for the main CLI entry point."""

    def test_main_with_no_args_returns_zero(self) -> None:
        """Main should return 0 and print help when no args given."""
        with patch("sys.argv", ["spb-clean"]):
            result = main()
            assert result == 0

    def test_main_with_todo_flag(self, tmp_path: Path) -> None:
        """Main should call archive_todos when --todo is passed."""
        notes_dir = tmp_path / "docs" / "notes"
        notes_dir.mkdir(parents=True)

        todo_file = notes_dir / "todo.md"
        todo_file.write_text("# TODO\n\n- [ ] Task\n", encoding="utf-8")

        archive_file = notes_dir / "archive.md"
        archive_file.write_text("# Archive\n\n", encoding="utf-8")

        with (
            patch("sys.argv", ["spb-clean", "--todo"]),
            patch(
                "simple_python_boilerplate.dev_tools.clean.get_repo_root",
                return_value=tmp_path,
            ),
        ):
            result = main()
            assert result == 0
