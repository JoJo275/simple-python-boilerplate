<!-- WORKING COPY — edit freely, this does NOT affect .github/PULL_REQUEST_TEMPLATE.md -->
<!-- Use this file to draft your PR description before pasting it into GitHub. -->
<!-- Suggested branch rename: feat/developer-tooling-overhaul -->
<!--
  Suggested PR titles (must use conventional commit format — type: description):

  Full titles:
    feat: overhaul developer tooling, diagnostics, and documentation
    feat: enhance scripts, tests, docs, and VS Code config for v1.0 readiness

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

<!-- Suggested labels: enhancement, documentation, developer-experience, scripts, tests -->

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

Major overhaul of developer tooling, diagnostics, documentation, container
support, and test coverage across 116 files (+13,053 / -1,955 lines) —
bringing the template to v1.0 release readiness.

**What changes you made:**

- **`git_doctor.py`** — major rewrite: git config reference export
  (`--export-config`), auto-apply (`--apply-recommended`), branch
  characteristics, commit activity charts, file change summaries,
  fetch/prune at startup, column-header config display, improved
  status overview
- **`workflow_versions.py`** — rate-limit handling overhaul: early
  bail-out on 403, single warning instead of spam, summary of skipped
  actions, GitHub token setup guide in docstring
- **`customize.py`** — added missing container files to STRIPPABLE,
  corrected advanced-workflows count, added drift TODOs
- **Container tooling** — new `test_containerfile.py`,
  `test_docker_compose.py`, shared `_container_common.py`, bash
  equivalents, `devcontainer-build.yml` workflow
- **Documentation** — major expansion of `USING_THIS_TEMPLATE.md`
  (containers, VS Code config, LLM-assisted setup note, editor/git
  handling, git configuration); new `branch-workflows.md`,
  `scripts.md` reference; 5 new ADRs (036-040); enhanced
  troubleshooting, learning notes, release docs
- **Tests** — new test suites for customize (interactive + unit),
  workflow_versions (rate-limit), test_containerfile,
  test_docker_compose; expanded existing test files
- **VS Code** — updated `.vscode/settings.json`, expanded
  `.code-workspace` with extension recommendations
- **CI/CD** — SHA-pinned action updates across ~20 workflow files,
  new `devcontainer-build.yml`, updated `repo_doctor.d/` rules
- **Security** — enhanced SECURITY.md with PGP setup instructions

**Why you made them:**

The template had gaps in developer experience: limited diagnostics,
sparse container testing, no rate-limit handling in workflow_versions,
incomplete test coverage for scripts, and documentation that didn't
cover containers or VS Code config. This PR fills those gaps for a
complete, well-documented v1.0 release.

## Related Issue

N/A — accumulated improvements toward v1.0 release readiness
(see ADR 040).

## Type of Change

- [x] 🐛 Bug fix (non-breaking change that fixes an issue)
- [x] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] 📚 Documentation update
- [x] 🔧 Refactor (no functional changes)
- [x] 🧪 Test update

## How to Test

**Steps:**

1. Run `python scripts/git_doctor.py` — verify status overview, config
   table with column headers, and health checks
2. Run `python scripts/workflow_versions.py show --filter stale` — verify
   no rate-limit spam (if unauthenticated, one warning then skip)
3. Run `python scripts/customize.py --dry-run` — verify container files
   appear in STRIPPABLE listing
4. Open the project in VS Code as a workspace — verify settings and
   extension recommendations load

**Test command(s):**

```bash
# Full test suite
task test

# New/modified test files
pytest tests/unit/test_customize.py tests/unit/test_customize_interactive.py -v
pytest tests/unit/test_workflow_versions.py -v
pytest tests/unit/test_test_containerfile.py tests/unit/test_test_docker_compose.py -v

# Verify scripts parse cleanly
python -c "import ast, pathlib; [ast.parse(f.read_text('utf-8')) for f in pathlib.Path('scripts').glob('*.py')]"
```

**Screenshots / Demo (if applicable):**

<!-- Add screenshots of workflow_versions rate-limit handling, git_doctor output -->

## Risk / Impact

**Risk level:** Low

**What could break:** `git_doctor.py` is the largest change — output
formatting regressions affect DX but not production code or CI gates.
`workflow_versions.py` rate-limit changes are purely additive (cached
responses still work). VS Code settings are additive and only apply when
opening the workspace file.

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
- [x] Relevant tests pass locally (or explained in Additional Notes)
- [x] No security concerns introduced (or flagged for review)
- [x] No performance regressions expected (or flagged for review)

## Reviewer Focus (Optional)

- **`scripts/workflow_versions.py`** — review the rate-limit bail-out
  logic in `_gh_api()` and the docstring token setup guide for accuracy
- **`scripts/customize.py`** — verify STRIPPABLE paths match actual repo
  files (path integrity tests catch this, but a visual check is good)
- **`docs/USING_THIS_TEMPLATE.md`** — review the new LLM-assisted setup
  note and container sections for clarity
- **New test files** — check that mocked boundaries are reasonable and
  tests aren't testing implementation details

## Additional Notes

- This branch has ~20 commits across 116 files. Consider squash-merging
  to keep main's history clean.
- `git-config-reference.md` and `test-config-ref.md` are auto-generated —
  don't review their content line-by-line.
- The `workflow_versions.py` token guide recommends fine-grained tokens
  scoped to public-repo metadata only — verify this matches GitHub's
  current token UI.
