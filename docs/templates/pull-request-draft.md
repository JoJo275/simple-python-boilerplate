<!-- WORKING COPY — edit freely, this does NOT affect .github/PULL_REQUEST_TEMPLATE.md -->
<!-- Use this file to draft your PR description before pasting it into GitHub. -->
<!-- Suggested branch rename: refactor/extract-doctor-common -->
<!--
  Suggested PR titles (must use conventional commit format — type: description):

  Full titles:
    refactor: extract shared doctor helpers into _doctor_common.py
    refactor(scripts): centralise doctor-family utilities in _doctor_common

  Available prefixes:
    feat:     — new feature or capability
    fix:      — bug fix
    docs:     — documentation only
    chore:    — maintenance, no production code change
    refactor: — code restructuring, no behavior change
    test:     — adding or updating tests
    ci:       — CI/CD workflow changes
    style:    — formatting, no logic change
    perf:     — performance improvement
    build:    — build system or dependency changes
    revert:   — reverts a previous commit
-->
<!-- Suggested labels: refactor, scripts, testing -->

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

Extract shared helpers from `doctor.py` and `env_doctor.py` into a new
`_doctor_common.py` module. Improve doctor script output with Windows ANSI
fallback, progress spinner, clearer labelling, and explicit hatch environment
categorisation.

**What changes you made:**

- Created `scripts/_doctor_common.py` (v1.0.0) — shared utilities:
  `get_version()`, `get_package_version()`, `check_path_exists()`,
  `check_hook_installed()`, and `HOOK_STAGES` constant.
- Updated `scripts/doctor.py` (v2.3.0 → v2.4.0) — imports shared helpers
  from `_doctor_common`; hatch envs now explicitly labelled as
  *user-defined* vs *internal*; added Spinner progress indicator;
  `pip_install` section label clarification; descriptive git dirty values;
  optional `actionlint` handling.
- Updated `scripts/env_doctor.py` (v1.1.0 → v1.2.0) — uses
  `get_version`, `get_package_version`, `check_hook_installed` from
  `_doctor_common`; fixed "Hatch Hatch" version duplication; added
  Colors and timing to output.
- Updated `scripts/_colors.py` (v1.0.0 → v1.1.0) — Windows VT processing
  via `SetConsoleMode` with graceful fallback; fixed bandit B105 false
  positive on `status_icon()`.
- Added `tests/unit/test_doctor_common.py` — 22 tests covering all
  extracted helpers.
- Fixed `tests/unit/test_env_doctor.py` — broken `_colorize` import;
  updated mock targets after refactoring.
- Fixed TTY color tests across `test_doctor.py`, `test_env_doctor.py`,
  `test_repo_doctor.py`, `test_colors.py` — mock `_enable_windows_ansi`
  for Windows VT processing in pytest capture context.
- Updated `scripts/README.md` — listed `_doctor_common.py` as shared
  internal module.

**Why you made them:**

`doctor.py` and `env_doctor.py` duplicated command execution, package
lookup, path checking, and hook detection logic.  Centralising into
`_doctor_common.py` removes ~80 lines of duplication and ensures
bug fixes apply to both scripts simultaneously.  The output improvements
(spinner, labelled hatch envs, clearer dirty/install labels) came from
real-world usage feedback.

## Related Issue

<!-- Use one of: Fixes #123, Closes #123, Resolves #123, Related to #123 -->
<!-- If no issue exists, write "N/A" and briefly explain (e.g., maintenance, small refactor) -->

N/A — maintenance refactor to reduce duplication across doctor-family scripts.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [x] 🔧 Refactor (no functional changes)
- [x] 🧪 Test update

## How to Test

<!-- Help reviewers verify your changes. Don't make them guess! -->

**Steps:**

1. Run `python scripts/doctor.py` — verify spinner, hatch envs show "user_defined" and "internal" labels, `pip_install` label, descriptive `dirty` value
2. Run `python scripts/env_doctor.py` — verify colored output, timing line, no "Hatch Hatch" duplication
3. Run `python scripts/doctor.py --json | python -c "import sys,json; d=json.load(sys.stdin); print(d['hatch_envs'])"` — verify `user_defined` and `internal` keys
4. Run full test suite

**Test command(s):**

```bash
python -m pytest tests/unit/test_doctor_common.py tests/unit/test_doctor.py tests/unit/test_env_doctor.py tests/unit/test_colors.py tests/unit/test_repo_doctor.py tests/unit/test_workflow_versions.py -v
```

**Screenshots / Demo (if applicable):**

<!-- Add screenshots, GIFs, or video links to help explain your changes -->

## Risk / Impact

<!-- What's the blast radius? What could go wrong? -->

**Risk level:** Low

**What could break:** Test mock targets changed from `env_doctor.importlib.metadata.version` to `env_doctor.get_package_version` — any downstream tests that mock the old path will fail.

**Rollback plan:** Revert this PR

<!-- Or: "Toggle feature flag X" / "Run migration Y" / etc. -->

## Dependencies (if applicable)

<!-- Delete this section if not applicable -->
<!-- List any PRs that must be merged before/after this one -->

**Depends on:** <!-- e.g., #456, or org/other-repo#123 -->

**Blocked by:** <!-- e.g., waiting for deployment of #456 -->

## Breaking Changes / Migrations (if applicable)

<!-- Delete this section if not applicable -->

- [ ] Config changes required
- [ ] Data migration needed
- [ ] API changes (document below)
- [ ] Dependency changes

**Details:**

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

- Verify `_doctor_common.py` API surface is appropriate — should anything else be shared?
- Check that mock targets in test_env_doctor.py are correct after the refactor.
- Confirm the `# nosec B105` on `_colors.py:159` is a genuine false positive (dict maps status labels to ANSI codes, not passwords).

## Additional Notes

- `test_env_doctor.py` had a pre-existing broken import (`_colorize` from `env_doctor`) that caused collection-time ImportError. It was masked by `__pycache__`. Fixed in this PR.
- All 321 tests pass across 6 test files.
- Bandit reports zero issues after the `# nosec B105` annotation.
