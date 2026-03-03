-- =============================================================================
-- Example Reusable Queries
-- =============================================================================
-- Named, reusable SQL queries for application use.
--
-- These can be loaded by the application at startup (e.g., using aiosql,
-- yesql, or a simple file reader) and called by name.
--
-- Naming convention: use -- name: <query_name> comments if using a query
-- loader library, or just organize by section for manual use.
--
-- TODO (template users): Replace these examples with your actual queries
--   or delete this file. Organize into subdirectories by domain if the
--   query count grows (e.g., queries/users/, queries/reports/).
-- =============================================================================

-- ── List queries ─────────────────────────────────────────────

-- name: get_all_users
-- Get all active users, most recent first
SELECT id, name, email, created_at
FROM users
WHERE is_active = 1
ORDER BY created_at DESC;

-- name: get_all_users_paginated
-- Paginated user listing (pass :limit and :offset)
SELECT id, name, email, created_at
FROM users
WHERE is_active = 1
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset;

-- ── Lookup queries ───────────────────────────────────────────

-- name: get_user_by_id
SELECT id, name, email, is_active, created_at, updated_at
FROM users
WHERE id = :user_id;

-- name: get_user_by_email
SELECT id, name, email, is_active, created_at, updated_at
FROM users
WHERE email = :email;

-- ── Search queries ───────────────────────────────────────────

-- name: search_users_by_name
-- Case-insensitive prefix search
SELECT id, name, email, created_at
FROM users
WHERE name LIKE :search || '%'
ORDER BY name;
