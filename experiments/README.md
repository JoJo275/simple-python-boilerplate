# Experiments

A scratch space for exploratory code, prototypes, and one-off scripts.

## Purpose

This directory is for:

- **Prototyping** — Test ideas before adding them to `src/`
- **Learning** — Try out new libraries or patterns
- **Debugging** — Isolate and reproduce issues
- **One-off scripts** — Quick utilities that don't belong in the main codebase

## Guidelines

- Code here is **not production quality** — no tests, docs, or types required
- Files may be **deleted at any time** — don't rely on anything here
- **Never import from experiments/** in production code
- Prefix files with a date or topic for organization: `2026-02-05_api_test.py`

## Examples

| File                          | Description                |
| ----------------------------- | -------------------------- |
| `example_api_test.py`         | Testing an external API    |
| `example_data_exploration.py` | Quick data analysis script |

## Cleanup

Periodically review and delete old experiments. If something proves useful, refactor it properly into `src/` with tests.
