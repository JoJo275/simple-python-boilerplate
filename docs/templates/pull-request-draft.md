<!-- WORKING COPY — edit freely, this does NOT affect .github/PULL_REQUEST_TEMPLATE.md -->
<!-- Use this file to draft your PR description before pasting it into GitHub. -->
<!-- Suggested branch rename: feat: scripts-workflows-docs-improvements -->
<!-- Suggested labels: enhancement, documentation, ci -->

<!--
  ╔══════════════════════════════════════════════════════════════╗
  ║  This PR description is for HUMAN REVIEWERS.                 ║
  ║                                                              ║
  ║  Release automation (release-please) reads individual        ║
  ║  commit messages on main — not this description.             ║
  ║  Write commits with conventional format (feat:, fix:, etc.)  ║
  ║  and include (#PR) or (#issue) references in each commit.    ║
  ║                                                              ║
  ║  This template captures: WHY you made changes, HOW to test   ║
  ║  them, and WHAT reviewers should focus on.                   ║
  ╚══════════════════════════════════════════════════════════════╝
-->

## Description

Comprehensive improvements to utility scripts, CI workflows, and documentation across the template repository.

**What changes you made:**

### Scripts (`scripts/`)

- **`dep_versions.py`** (v1.0 → v1.2.0): Major overhaul of the dependency version manager
  - Added `--version` and `--dry-run` flags
  - Replaced hand-rolled TOML line parser with `tomllib.loads()` (stdlib)
  - Hardened `_latest_version()` with JSON-first parsing (`pip index versions --format=json`), text fallback
  - Added `_warn_if_no_venv()` to warn when upgrading outside a virtual environment
  - Replaced import-time `REQ_FILES` global with lazy `_get_req_files()` function
  - Added `_update_minimum_specifier()` and `update_specifiers_in_toml()` — auto-updates `>=`/`~=` constraints after upgrade
  - Added `timeout=120` to `upgrade_package()` subprocess call
  - Fixed mypy error: `meta.get("Summary")` → `meta["Summary"]` (PackageMetadata bracket access)

- **`doctor.py`** (new v1.2.0): Diagnostics bundle generator improvements
  - Fixed `hatch version` → `hatch --version` (was printing project version, not Hatch's)
  - Added `--version`, `--json`, and `--quiet` CLI flags
  - Fixed `datetime.now()` → `datetime.now(tz=UTC)` for unambiguous timestamps
  - Added git info section (branch, commit SHA, commit date, dirty state)
  - Added `pip`, `actionlint`, and `cz` to tool version checks
  - Fixed `get_version()` to handle absolute paths (e.g., `sys.executable`) directly instead of routing through `shutil.which()`
  - Parallelized tool version collection with `ThreadPoolExecutor` (~10 serial subprocess calls → concurrent)
  - Added proper type annotations to `format_plain`/`format_markdown` (bare `dict` → typed)

- **`env_doctor.py`**: Fixed same `hatch version` → `hatch --version` bug

- **Other scripts**: Enhancements to `bootstrap.py`, `changelog_check.py`, `check_todos.py`, `archive_todos.py`, `clean.py`, `customize.py` (logging, quiet modes, version flags, error handling)

### CI Workflows (`.github/workflows/`)

- **`cache-cleanup.yml`** (new): Cleans GitHub Actions caches when PR branches are closed. Uses `gh actions-cache` CLI (no third-party actions).
- **`regenerate-files.yml`** (new): Weekly regeneration of `requirements.txt` and `requirements-dev.txt` from `pyproject.toml`, with automatic version comment refresh via `dep_versions.py update-comments`.
- Updates to `ci-gate.yml`, `docs-build.yml`, `docs-deploy.yml`, `scorecard.yml`, `security-codeql.yml` for consistency and correctness.

### Documentation

- **`docs/notes/learning.md`**: Added DX, UX, GHCR terms
- **`docs/workflows.md`**: Updated workflow count (27 → 29), added cache-cleanup and regenerate-files to Maintenance table
- **`.github/copilot-instructions.md`**: Updated workflow count and Maintenance category
- **`docs/guide/getting-started.md`** (new): Comprehensive getting started guide
- **`docs/reference/api.md`** (new): API reference documentation
- Various other doc improvements and cleanup

### Tests

- **`tests/unit/test_dep_versions.py`** (new): 39 tests covering `_normalise_name`, `_capitalise`, `_parse_deps_from_toml`, `_update_minimum_specifier`, `_get_req_files`, `SCRIPT_VERSION`, plus mock-based tests for `_warn_if_no_venv`, `_latest_version`, and `upgrade_package`
- **`tests/unit/test_doctor.py`** (new): 30 tests covering `get_version`, `get_package_version`, `check_path_exists`, `format_plain`, `format_markdown`, `format_json`, `_git_info`, `collect_diagnostics` parallelism, and timestamp UTC validation

**Why you made them:**

The utility scripts lacked robustness (no tests, fragile parsing, missing CLI features), the CI pipeline was missing cache management and requirements file regeneration, and documentation had gaps. These changes bring the template's tooling up to production quality.

## Related Issue

N/A — accumulated improvements across scripts, CI, and documentation. No single tracking issue.

## Type of Change

- [x] 🐛 Bug fix (non-breaking change that fixes an issue)
- [x] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] 📚 Documentation update
- [x] 🔧 Refactor (no functional changes)
- [x] 🧪 Test update

## How to Test

**Steps:**

1. Run all unit tests to verify script changes
2. Smoke test the CLI scripts directly
3. Validate workflows with actionlint

**Test command(s):**

```bash
# Run all unit tests
hatch run pytest tests/unit/ -v

# Focused test runs
hatch run pytest tests/unit/test_dep_versions.py -v   # 39 tests
hatch run pytest tests/unit/test_doctor.py -v          # 30 tests

# Smoke test CLI scripts
hatch run python scripts/doctor.py --version       # doctor 1.2.0
hatch run python scripts/doctor.py --quiet          # one-line summary
hatch run python scripts/doctor.py --json           # JSON output
hatch run python scripts/dep_versions.py --version  # dep_versions 1.2.0
hatch run python scripts/dep_versions.py upgrade --dry-run  # preview upgrades

# Quality checks
hatch run ruff check scripts/doctor.py scripts/dep_versions.py scripts/env_doctor.py
hatch run mypy scripts/doctor.py scripts/dep_versions.py

# Validate workflows
hatch run pre-commit run actionlint --all-files
```

## Risk / Impact

**Risk level:** Low

**What could break:**

- `dep_versions.py upgrade` now also updates `>=`/`~=` specifiers in pyproject.toml after upgrading — this is new behavior. It leaves `==` pins untouched.
- `doctor.py` parallelized tool detection could theoretically surface race conditions, but `ThreadPoolExecutor` + `get_version` are stateless and independent.
- `hatch --version` fix in both `doctor.py` and `env_doctor.py` changes the output of those commands (now shows Hatch's actual version instead of the project version).

**Rollback plan:** Revert this PR

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [x] No new warnings (or explained in Additional Notes)
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] Relevant tests pass locally (or explained in Additional Notes)
- [x] No security concerns introduced (or flagged for review)
- [x] No performance regressions expected (or flagged for review)

## Reviewer Focus (Optional)

- **`dep_versions.py` specifier updater** (`_update_minimum_specifier` and `update_specifiers_in_toml`): Verify the regex correctly handles edge cases like compound constraints (`>=1.6,<2.0`) and extras (`mkdocstrings[python]>=0.27`).
- **`doctor.py` parallelism**: Confirm `ThreadPoolExecutor` usage is correct and results maintain stable key order.
- **New workflows**: `cache-cleanup.yml` and `regenerate-files.yml` use repository guard pattern (`vars.ENABLE_*`) — they won't run until the corresponding variable is created in repo settings.

## Additional Notes

- The two new workflows (`cache-cleanup.yml`, `regenerate-files.yml`) require enabling repository variables (`vars.ENABLE_CACHE_CLEANUP`, `vars.ENABLE_REGENERATE_FILES`) before they'll run — this is the standard repository guard pattern per ADR 011.
- `dep_versions.py` still uses `_DEP_RE` regex for line-level editing (preserving indentation, comments, commas) even though `_parse_deps_from_toml` now uses `tomllib` for reading. This is intentional — `tomllib` can parse but can't round-trip edits while preserving formatting.
- Scripts import via `sys.path.insert(0, ...)` in tests since `scripts/` is not an installed package. This is the established pattern (see `test_archive_todos.py`).
