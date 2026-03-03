-- =============================================================================
-- Setup test database schema
-- =============================================================================
-- Creates test tables in a fresh SQLite database.
-- Run before integration tests.
--
-- Usage:
--   sqlite3 :memory: < tests/integration/sql/setup_test_db.sql
--   sqlite3 var/test.sqlite3 < tests/integration/sql/setup_test_db.sql
--
-- TODO (template users): Replace the example tables below with your actual
--   test schema. Keep this in sync with db/schema.sql (or source it directly).
-- =============================================================================

-- ── Pragmas ──────────────────────────────────────────────────
PRAGMA foreign_keys = ON;

-- ── Tables ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    is_active  INTEGER NOT NULL DEFAULT 1,  -- 0 = inactive, 1 = active
    created_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- ── Indexes ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_users_email     ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- ── Seed test data ───────────────────────────────────────────
INSERT OR IGNORE INTO users (name, email) VALUES
    ('Alice Admin',       'alice@example.com'),
    ('Bob Builder',       'bob@example.com'),
    ('Carol Contributor', 'carol@example.com');
