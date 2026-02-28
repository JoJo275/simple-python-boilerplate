<!-- WORKING COPY — edit freely, this does NOT affect .github/PULL_REQUEST_TEMPLATE.md -->
<!-- Use this file to draft your PR description before pasting it into GitHub. -->
<!-- Suggested branch rename: feat/docs-tooling-overhaul -->
<!--
  Suggested PR titles (must use conventional commit format — type: description):

  Full titles:
    feat: docs overhaul, script enhancements, and new ADRs
    feat: comprehensive template documentation and tooling update
    docs: documentation overhaul with new ADRs, tests, and script enhancements

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
<!-- Suggested labels: documentation, enhancement, testing -->

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

Large-scale documentation overhaul, script enhancements, and new ADRs to bring the template repository up to a comprehensive, self-documenting state. Touches 136 files (+15,862 / −6,189 lines) across docs, scripts, tests, and configuration.

**What changes you made:**

- **Script enhancements** — `env_doctor.py`, `repo_doctor.py`, and `workflow_versions.py` gained JSON output support, `--version` flags, color output, filtering/quiet modes, and a new `actions:check` CI gate task
- **9 new ADRs (027–035)** — database strategy, git branching strategy, testing strategy, label management as code, script conventions, dependency grouping, Prettier for Markdown, documentation organization, and Copilot instructions as developer context
- **New MkDocs hook** — `mkdocs-hooks/repo_links.py` rewrites repo-relative links to GitHub URLs during doc builds; registered in `mkdocs.yml`
- **New documentation** — troubleshooting guide (`docs/guide/troubleshooting.md`), CI/CD design doc (`docs/design/ci-cd-design.md`), resources page (`docs/notes/resources.md`), MkDocs hooks README
- **Documentation overhaul** — rewrote or substantially updated nearly every existing doc (ADRs, architecture, tool decisions, development guides, templates, release policy, workflows, repo layout, etc.) for clarity, accuracy, and completeness
- **Markdownlint configuration** — added `.markdownlint-cli2.jsonc` with project-specific rule overrides (MD024 siblings_only, MD033 allowed elements, MD046 disabled)
- **New unit tests** — `test_env_doctor.py`, `test_repo_doctor.py`, `test_repo_links.py`, `test_workflow_versions.py` (~3,200 lines of test coverage)
- **Configuration updates** — `pyproject.toml` (optional deps, version specs), `Taskfile.yml` (new tasks for dep checks, repo health, actions gate), `.pre-commit-config.yaml` refinements, updated `requirements.txt` / `requirements-dev.txt`
- **Template improvements** — added actionable `TODO (template users):` comments throughout config files, SECURITY.md, requirements files, and Copilot instructions

**Why you made them:**

The template's documentation was incomplete, inconsistent, and in places inaccurate. Scripts lacked standard CLI features (JSON output, version flags) expected for automation. Several important architectural decisions were undocumented. The goal is to make the template self-contained and immediately usable without needing to reverse-engineer conventions from the code.

## Related Issue

N/A — ongoing template maturity work; no single issue tracks this effort.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [x] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] 📚 Documentation update
- [x] 🔧 Refactor (no functional changes)
- [x] 🧪 Test update

## How to Test

**Steps:**

1. Run the unit test suite to verify script changes and new tests pass
2. Build the docs site to confirm MkDocs hook and documentation changes render correctly
3. Run the new Taskfile tasks (`task deps:versions`, `task actions:versions`, `task actions:check`) to verify they work
4. Spot-check a few ADRs and docs pages for rendering and link integrity

**Test command(s):**

```bash
# Run all unit tests
hatch run test:run

# Run only the new tests
pytest tests/unit/test_env_doctor.py tests/unit/test_repo_doctor.py tests/unit/test_repo_links.py tests/unit/test_workflow_versions.py -v

# Build docs (strict mode catches broken links/warnings)
hatch run docs:build --strict

# Verify markdownlint config
pre-commit run markdownlint-cli2 --all-files

# Verify new Taskfile tasks exist
task --list
```

## Risk / Impact

**Risk level:** Low

**What could break:**

- MkDocs hook (`repo_links.py`) could rewrite links incorrectly in edge cases — mitigated by unit tests and strict doc builds
- Markdownlint config may flag existing Markdown that was previously unchecked — intentional; violations should be fixed
- Large diff makes review harder — changes are almost entirely documentation and tests with no application logic changes

**Rollback plan:** Revert this PR

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [ ] No new warnings (or explained in Additional Notes)
- [x] I have added tests that prove my fix is effective or that my feature works
- [ ] Relevant tests pass locally (or explained in Additional Notes)
- [ ] No security concerns introduced (or flagged for review)
- [x] No performance regressions expected (or flagged for review)

## Reviewer Focus (Optional)

- **`mkdocs-hooks/repo_links.py`** — New build hook with non-trivial link rewriting logic. Verify the regex patterns and edge-case handling look correct.
- **ADRs 027–035** — New architectural decisions. Confirm the rationale and alternatives are well-captured and consistent with existing project conventions.
- **`scripts/workflow_versions.py`** — Most significant script change. Review the new filtering, JSON output, and CI gate logic.
- **Copilot instructions (`.github/copilot-instructions.md`)** — Updated to reflect all the new conventions. Worth a read-through to confirm accuracy.

## Additional Notes

- This branch has 48 commits. Before merging, consider squashing into a smaller number of logical commits (e.g., one for scripts, one for ADRs, one for docs overhaul, one for tests) to keep `main` history clean.
- The `docs/workflows.md` file was updated but is manually maintained — verify it still accurately reflects the actual workflow files in `.github/workflows/`.
- Some checklist items are left unchecked because full local verification (all tests passing, no warnings) should be confirmed before the PR is marked ready for review.
