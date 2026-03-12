<!-- WORKING COPY — edit freely, this does NOT affect .github/PULL_REQUEST_TEMPLATE.md -->
<!-- Use this file to draft your PR description before pasting it into GitHub. -->
<!-- Suggested branch rename: feat/developer-tooling-overhaul -->
<!--
  Suggested PR titles (must use conventional commit format — type: description):

  Full titles:
    feat: overhaul developer tooling, diagnostics, and documentation
    feat: enhance git_doctor, env_doctor, documentation, and VS Code config

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

<!-- Suggested labels: enhancement, documentation, developer-experience, scripts -->

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

Major overhaul of developer tooling, diagnostics scripts, documentation, and
VS Code configuration. This PR touches 66 files across scripts, docs, tests,
and editor config — primarily improving the developer experience for both
template authors and template users.

**What changes you made:**

- **`git_doctor.py`** — rewrote from scratch (v2.0.0): added git config
  reference export (`--export-config`), auto-fix (`--fix`), branch
  characteristics, commit activity charts, file change summaries, fetch/prune
  at startup, column-header config display, improved status overview
- **`env_doctor.py`** — expanded with OS/platform checks, Node.js/container
  runtime detection, git remote health, disk space, progress bars
- **VS Code configuration** — added `.vscode/settings.json` (shared project
  settings) and `.vscode/extensions.json`; expanded `.code-workspace` with
  detailed extension recommendations and customization guide
- **Documentation** — major expansion of `USING_THIS_TEMPLATE.md` (containers,
  VS Code config, editor/git file handling, git configuration, copilot
  customization, optional tools); enhanced `repo-layout.md`, learning notes,
  troubleshooting guide
- **Tests** — added unit tests for git_doctor, bootstrap, customize,
  apply_labels, changelog_check, check_todos, check_nul_bytes, imports
- **Scripts** — Unicode symbol support, progress spinners, color improvements,
  version bumps across all scripts
- **Security** — enhanced SECURITY.md with PGP setup instructions, added
  `pgp-key.asc`
- **CI** — added `doctor-all.yml` workflow, updated link-checker config

**Why you made them:**

The template's developer experience had gaps: no shared VS Code settings,
limited diagnostics, sparse documentation for template users on containers
and editor config, and no test coverage for most scripts. This PR fills
those gaps so template users get a more complete, well-documented starting
point.

## Related Issue

N/A — exploratory development and documentation improvements accumulated on
a scratch branch over the course of iterative template development.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [x] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] 📚 Documentation update
- [x] 🔧 Refactor (no functional changes)
- [x] 🧪 Test update

## How to Test

**Steps:**

1. Run `python scripts/git_doctor.py` — verify the status overview shows
   three labeled lines (Working tree, Remote sync, Health) and the Git
   Configuration section has column headers (Key, Scope, Value)
2. Run `python scripts/git_doctor.py --export-config` — verify
   `git-config-reference.md` is generated with the Scope Guide including
   command examples
3. Run `python scripts/git_doctor.py --fix --dry-run` — verify it lists
   recommended settings without applying them
4. Run `python scripts/env_doctor.py` — verify expanded checks run
5. Open the project in VS Code as a workspace — verify settings and
   extension recommendations load

**Test command(s):**

```bash
# Run full test suite
task test

# Run just the new/modified test files
pytest tests/unit/test_git_doctor.py tests/unit/test_env_doctor.py -v
pytest tests/unit/test_bootstrap.py tests/unit/test_customize.py -v
pytest tests/unit/test_apply_labels.py tests/unit/test_check_todos.py -v

# Verify scripts have no syntax errors
python -c "import ast, pathlib; [ast.parse(f.read_text('utf-8')) for f in pathlib.Path('scripts').glob('*.py')]"

# Run diagnostics
python scripts/git_doctor.py
python scripts/env_doctor.py
```

**Screenshots / Demo (if applicable):**

<!-- Add screenshots of git_doctor output showing new formatting -->

## Risk / Impact

**Risk level:** Low

**What could break:** The git_doctor.py rewrite is the biggest change —
if the output formatting regresses, it affects the developer experience
but not any production code or CI gates. VS Code settings are additive
and won't affect users who don't open the workspace file.

**Rollback plan:** Revert this PR

## Dependencies (if applicable)

None — all changes are self-contained within this repository.

## Breaking Changes / Migrations (if applicable)

None. All changes are additive. Existing scripts retain their CLI
interfaces. No config migrations needed.

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [ ] No new warnings (or explained in Additional Notes)
- [x] I have added tests that prove my fix is effective or that my feature works
- [ ] Relevant tests pass locally (or explained in Additional Notes)
- [ ] No security concerns introduced (or flagged for review)
- [x] No performance regressions expected (or flagged for review)

## Reviewer Focus (Optional)

- **`scripts/git_doctor.py`** — this is the largest change (~2600 lines).
  Focus on the display logic in `run()` and the `export_git_config_reference()`
  function. The health checks and data collection functions are lower risk.
- **`docs/USING_THIS_TEMPLATE.md`** — review the new "Editor & Git File
  Handling" and "Git Configuration" sections for accuracy.
- **VS Code config** — verify `.vscode/settings.json` defaults are sensible
  and don't override user preferences inappropriately.

## Additional Notes

- This branch has 42 commits across 66 files (+9924 / -511 lines). Consider
  squash-merging to keep main's history clean.
- The `git-config-reference.md` file is auto-generated — it will be
  regenerated on each `--export-config` run, so don't review its content
  line-by-line.
- Several commits on this branch have overly broad messages (e.g., "enhance
  git_doctor with new features and improvements"). The PR title and this
  description provide the accurate summary for the squash-merge commit.
