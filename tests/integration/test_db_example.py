"""Example database integration tests."""

# TODO: Replace placeholder tests with actual integration tests for your database layer

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def test_db(tmp_path: Path) -> sqlite3.Connection:
    """Create an in-memory test database."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_placeholder_db_test(test_db: sqlite3.Connection) -> None:
    """Placeholder integration test."""
    cursor = test_db.execute("SELECT 1 as value")
    row = cursor.fetchone()
    assert row["value"] == 1


# Example integration test:
#
# def test_user_creation(test_db: sqlite3.Connection) -> None:
#     test_db.execute('''
#         CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
#     ''')
#     test_db.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
#     test_db.commit()
#
#     cursor = test_db.execute("SELECT name FROM users WHERE id = 1")
#     assert cursor.fetchone()["name"] == "Alice"
