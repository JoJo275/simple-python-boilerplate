-- =============================================================================
-- Teardown test database
-- =============================================================================
-- Drops all test tables and indexes after integration tests.
-- Run after integration tests to leave a clean state.
--
-- Usage:
--   sqlite3 var/test.sqlite3 < tests/integration/sql/teardown_test_db.sql
--
-- TODO (template users): Update this to match your actual test schema.
--   Every table/index created in setup_test_db.sql should be dropped here.
-- =============================================================================

-- ── Drop indexes ─────────────────────────────────────────────
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_users_is_active;

-- ── Drop tables ──────────────────────────────────────────────
DROP TABLE IF EXISTS users;
