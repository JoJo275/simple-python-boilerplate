<!-- WORKING COPY — edit freely, this does NOT affect .github/PULL_REQUEST_TEMPLATE.md -->
<!-- Use this file to draft your PR description before pasting it into GitHub. -->
<!-- Suggested branch rename: feat/template-scaffolding-and-ci-hardening -->

## Description

Large foundational PR that builds out the template repository's CI/CD infrastructure, documentation, developer tooling, and project scaffolding. This is the initial "make the template production-ready" pass.

**What changes you made:**

- **CI/CD (26 workflows):** Added repository guard pattern (`ENABLE_*` variables) across all workflows, added ci-gate workflow, auto-merge-dependabot, docs-deploy, and changelog workflows. Fixed corrupted SHA pins (trivy-action, scorecard-action). Fixed container build failures (README.md and LICENSE missing from build context). Added full cron comment blocks with UTC/DST conversions to all scheduled workflows.
- **Scripts (5 new):** `customize.py` (interactive project customization), `env_doctor.py` (environment health checks), `check_todos.py` (template TODO scanner), `changelog_check.py` (CHANGELOG/tag drift detection), `check_nul_bytes.py` replaced with precommit version.
- **Documentation (major):** New `releasing.md` (full release guide with Mermaid diagrams), `learning.md` (1000+ line developer reference), `tool-decisions.md`, ADR template, ADRs 023 (branch protection) and 024 (ci-gate pattern). Overhauled `architecture.md`, `copilot-instructions.md`, `workflows.md`, `CONTRIBUTING.md`, `README.md`, and `USING_THIS_TEMPLATE.md`.
- **Templates:** Reorganized issue templates into `docs/templates/issue_templates/` (issue forms + legacy markdown). Added PR description draft template. Added PR labeler config (`.github/labeler.yml`).
- **Pre-commit:** Updated hooks, added deptry for dependency hygiene.
- **Config:** Updated `pyproject.toml`, `mkdocs.yml`, `Taskfile.yml`, `_typos.toml`, `.containerignore`, `.dockerignore`.
- **Tests:** Added integration tests, unit test fixtures, updated conftest.

**Why you made them:**

The boilerplate was a skeleton — workflows existed but had broken SHAs, no guard pattern (all workflows ran unconditionally), no release documentation, sparse developer guidance, and missing tooling scripts. This PR brings it to a state where a template user can fork, run `scripts/customize.py`, and have a fully working project with tested CI, documented processes, and production-quality tooling.

## Related Issue

N/A — initial template buildout across all project areas.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [x] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] 📚 Documentation update
- [x] 🔧 Refactor (no functional changes)
- [x] 🧪 Test update

## How to Test

**Steps:**
1. Verify all CI workflows pass on this PR (Actions tab)
2. Verify container build succeeds (nightly-security includes a container rebuild)
3. Verify docs build: `hatch run docs:build`
4. Verify tests pass: `task test`
5. Verify pre-commit hooks: `pre-commit run --all-files`

**Test command(s):**
```bash
task test                              # run test suite
task lint                              # ruff lint + format check
task typecheck                         # mypy
pre-commit run --all-files             # all pre-commit hooks
hatch run docs:build                   # mkdocs build
python scripts/env_doctor.py           # environment health check
python scripts/check_todos.py          # verify template TODOs are documented
```

## Risk / Impact

**Risk level:** Medium

**What could break:**
- Workflow guard variables (`ENABLE_*`) must be set in repo Settings → Variables for workflows to run. Without them, all guarded workflows skip silently — this is intentional but could surprise someone expecting them to run.
- SHA-pinned action updates could have unexpected behavior differences (trivy v0.34.1, scorecard v2.4.3).
- MkDocs nav structure changed — any bookmarked deep links to old doc paths may break.

**Rollback plan:** Revert this PR. All changes are additive or config-based — no data migrations or irreversible state changes.

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [ ] No new warnings (or explained in Additional Notes)
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] Relevant tests pass locally (or explained in Additional Notes)
- [x] No security concerns introduced (or flagged for review)
- [x] No performance regressions expected (or flagged for review)

## Reviewer Focus (Optional)

- **SHA pins:** Verify the trivy-action (`e368e328...`) and scorecard-action (`4eaacf05...`) SHAs match their claimed versions (v0.34.1 and v2.4.3 respectively).
- **Guard pattern:** Spot-check a few workflows to confirm the `vars.ENABLE_*` guard is consistent.
- **`scripts/customize.py`:** This is the most complex new code — interactive project renaming with `--dry-run` support.
- **`.containerignore` / `.dockerignore`:** These were the root cause of multiple nightly-security failures. Confirm `!README.md` and `LICENSE` are no longer excluded.

## Additional Notes

- **91 files changed** across CI, docs, scripts, templates, tests, and config. This is intentionally one large PR because the changes are deeply interdependent (e.g., new workflows reference new docs, new docs reference new scripts, copilot-instructions references new ADRs).
- **Dependabot PR #8** is open separately — that's an independent actions version bump and can be merged before or after this PR.
- **Pre-commit-update PR #9** was auto-created by the `pre-commit-update.yml` workflow (which required enabling "Allow GitHub Actions to create and approve pull requests" in repo settings).
- **Post-merge:** Set the repository variables (`ENABLE_RELEASE_PLEASE`, `ENABLE_RELEASE`, `ENABLE_COMMIT_LINT`, etc.) in Settings → Variables to activate the guarded workflows. See `docs/releasing.md` § "Repository Variables" for the full list.
