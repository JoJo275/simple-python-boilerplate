<!-- WORKING COPY — edit freely, this does NOT affect .github/PULL_REQUEST_TEMPLATE.md -->
<!-- Use this file to draft your PR description before pasting it into GitHub. -->
<!-- Suggested branch rename: feat/developer-tooling-and-docs -->
<!--
  Suggested PR titles (must use conventional commit format — type: description):

  Full titles:
    feat: Add developer tooling scripts, UI framework, and documentation enhancements
    feat: Add repo-sauron, env-inspect, repo-doctor improvements, and doc lifecycle templates

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

<!-- Suggested labels: enhancement, documentation, scripts -->

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

Large batch of developer tooling improvements, new scripts, a shared UI framework for script output, and documentation enhancements including a full idea-development lifecycle (explorations, blueprints, implementation plans).

**What changes you made:**

- **New scripts:** `repo_sauron.py` (comprehensive repo analysis with Markdown report), `env_inspect.py` (environment inspection), `env_doctor.py` (environment health checks), `doctor.py` (unified doctor entry point)
- **UI framework:** Added `_ui.py`, `_colors.py`, `_progress.py` shared modules for consistent, color-coded terminal output with progress bars and hyperlinks across all scripts
- **Customization script:** Added dry-run mode, input validation (GitHub usernames, authors, CLI prefixes, descriptions), and report generation (`customize-report.md`, `customize-config.md`)
- **repo_doctor.py:** Major enhancements — more health checks, improved output formatting, UTF-8 encoding fixes for Windows
- **Pre-commit hooks:** Added `auto_chmod_scripts.py` and `check_local_imports.py` custom hooks
- **CI:** New `smoke-test.yml` workflow
- **Documentation:** ADR 041 (env-inspect web dashboard), exploration/blueprint/implementation-plan for the dashboard, idea development lifecycle docs, templates for each doc stage
- **Dependency reporting:** New `dep_versions.py` script and `dep-versions-report.md`
- **Windows fixes:** UTF-8 reconfiguration for stdout/stderr across scripts
- **Tests:** New/updated tests for `_ui.py`, `customize`, `doctor`, `workflow_versions`, `git_doctor`

**Why you made them:**

The template's developer experience needed stronger introspection and diagnostic tooling. Scripts lacked consistent output formatting, and there was no structured process for evolving ideas from exploration to implementation. Windows users hit encoding errors in script output.

## Related Issue

N/A — iterative improvement of template developer tooling and documentation structure.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [x] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] 📚 Documentation update
- [ ] 🔧 Refactor (no functional changes)
- [x] 🧪 Test update

## How to Test

**Steps:**

1. Run the new scripts to verify they produce expected output
2. Run existing tests to confirm nothing is broken
3. Check that dry-run modes work without modifying files

**Test command(s):**

```bash
# Run all tests
task test

# Run specific new/changed test files
hatch run pytest tests/unit/test_ui.py -v
hatch run pytest tests/unit/test_customize_interactive.py -v
hatch run pytest tests/unit/test_doctor.py -v
hatch run pytest tests/unit/test_workflow_versions.py -v

# Verify scripts run
hatch run python scripts/env_inspect.py
hatch run python scripts/repo_sauron.py
hatch run python scripts/doctor.py
hatch run python scripts/dep_versions.py

# Lint check
task lint
task typecheck
```

**Screenshots / Demo (if applicable):**

<!-- Add screenshots, GIFs, or video links showing the new script output -->

## Risk / Impact

**Risk level:** Medium

**What could break:**
- New pre-commit hooks (`auto_chmod_scripts`, `check_local_imports`) could flag files in forks that were previously passing
- UTF-8 reconfiguration on Windows could have side effects in edge-case terminal environments
- `repo_sauron.py` and `repo_doctor.py` read many files — performance may vary on large repos

**Rollback plan:** Revert this PR

## Checklist

- [x] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [ ] No new warnings (or explained in Additional Notes)
- [x] I have added tests that prove my fix is effective or that my feature works
- [ ] Relevant tests pass locally (or explained in Additional Notes)
- [ ] No security concerns introduced (or flagged for review)
- [ ] No performance regressions expected (or flagged for review)

## Reviewer Focus (Optional)

- **`scripts/_ui.py` / `_colors.py` / `_progress.py`** — These are the shared UI modules used by all scripts. Review the API surface and consistency.
- **Customization dry-run logic** in `scripts/customize.py` — Verify the dry-run flag correctly prevents all file writes.
- **Windows UTF-8 handling** — The `sys.stdout`/`sys.stderr` reconfiguration in `_ui.py` and `repo_doctor.py`. Confirm this doesn't break non-Windows environments.
- **50 commits** — This branch accumulated many incremental changes. Consider whether it should be squash-merged to keep main history clean.

## Additional Notes

- 85 files changed, ~19,100 insertions, ~1,300 deletions across 50 commits
- The env-inspect web dashboard (ADR 041, blueprint, exploration, implementation plan) is **documentation only** — no dashboard code is included in this PR
- Generated reports (`repo-sauron-report.md`, `customize-config.md`, `customize-report.md`, `dep-versions-report.md`, `coverage.json`) are checked in as reference artifacts; consider whether these should be gitignored instead
