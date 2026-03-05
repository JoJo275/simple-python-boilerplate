<!-- WORKING COPY — edit freely, this does NOT affect .github/PULL_REQUEST_TEMPLATE.md -->
<!-- Use this file to draft your PR description before pasting it into GitHub. -->
<!-- Suggested branch rename: feat/customize-disclaimers-and-script-enhancements -->
<!--
  Suggested PR titles (must use conventional commit format — type: description):

  Full titles:
    feat: overhaul customize.py disclaimers, script infrastructure, and documentation
    feat: improve customize.py template cleanup UX with detailed disclaimers and consequence descriptions

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
<!-- Suggested labels: enhancement, scripts, documentation -->

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

Overhauls `scripts/customize.py` disclaimers, labels, and documentation
to give template users much clearer information about what gets removed
and what downstream consequences to expect. Also includes earlier commits
that added `_imports.py` / `find_repo_root()` infrastructure, template
cleanup support, input validation, and other script enhancements.

**What changes you made:**

- **Disclaimer overhaul (TEMPLATE_CLEANUP):** Every disclaimer now starts
  with a `⚠` marker, explicitly lists the files that will be removed,
  and describes downstream consequences (broken mkdocs.yml nav links,
  broken Taskfile tasks, broken pre-commit hooks, lost Copilot context, etc.)
- **Label accuracy:** Labels that previously listed only a subset of files
  in a directory now include "etc." to signal there are more files than
  listed (e.g., `docs-design` now reads "architecture, tool decisions,
  CI/CD design, database, etc." instead of just "architecture, tool decisions")
- **docs-notes disclaimer:** Refactored from dismissive "scratchpad notes,
  safe to remove" to acknowledge the value of each file — learning.md
  (packaging lessons), resources.md (curated tool links), tool-comparison.md
  (side-by-side evaluations), etc. — and recommend keeping them as reference
- **Inline comment fix:** `TEMPLATE_PROJECT_NAME` comment changed from
  "kebab-case repo/package name" to "kebab-case repo slug / PyPI name"
  to avoid confusion with the Python package name
- **Script infrastructure (earlier commits):** Added `_imports.py` with
  `find_repo_root()` for reliable path resolution, integrated `_progress.py`
  for progress bars, added input validation for project/package names,
  bumped to SCRIPT_VERSION 1.2.0
- **Template cleanup feature (earlier commits):** Added `--template-cleanup`
  flag with support for adr-files, docs-notes, docs-design, docs-reference,
  docs-development, docs-guide, placeholder-code, utility-scripts,
  advanced-workflows; interactive disclaimers with confirmation

**Why you made them:**

The previous disclaimers were vague about consequences. A user selecting
"docs-design" had no idea it would also remove `ci-cd-design.md` and
`database.md`, or that Copilot would lose architectural context. The
`docs-notes` disclaimer dismissed files like `learning.md` and `resources.md`
as "scratchpad notes" when they contain genuinely useful onboarding content.
Users deserve to make informed decisions about what to remove.

## Related Issue

N/A — ongoing improvement to template UX and customize.py usability.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [x] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] 📚 Documentation update
- [x] 🔧 Refactor (no functional changes)
- [ ] 🧪 Test update

## How to Test

**Steps:**

1. Run `python scripts/customize.py --dry-run` and step through the
   interactive wizard to Step 4 (Template Cleanup)
2. Select several cleanup items (e.g., `docs-design`, `docs-notes`,
   `utility-scripts`, `advanced-workflows`)
3. Verify each disclaimer now starts with `⚠`, lists specific files,
   and describes downstream consequences
4. Verify labels include "etc." where appropriate
5. Check that `--non-interactive` mode still works:
   ```bash
   python scripts/customize.py --dry-run --non-interactive \
       --project-name test-proj --author "Test" --github-user testuser \
       --template-cleanup docs-notes docs-design advanced-workflows
   ```

**Test command(s):**

```bash
# Syntax check
python -c "import ast; ast.parse(open('scripts/customize.py', encoding='utf-8').read()); print('OK')"

# Dry-run interactive walkthrough
python scripts/customize.py --dry-run

# Dry-run non-interactive with cleanup
python scripts/customize.py --dry-run --non-interactive \
    --project-name my-project --author "Jane Doe" \
    --github-user janedoe \
    --template-cleanup adr-files docs-notes placeholder-code
```

## Risk / Impact

**Risk level:** Low

**What could break:** Nothing functional. These are string changes to
disclaimers and labels shown during interactive setup. The script's
actual file-deletion logic is unchanged.

**Rollback plan:** Revert this PR

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [x] No new warnings (or explained in Additional Notes)
- [ ] I have added tests that prove my fix is effective or that my feature works
- [x] Relevant tests pass locally (or explained in Additional Notes)
- [x] No security concerns introduced (or flagged for review)
- [x] No performance regressions expected (or flagged for review)

## Reviewer Focus (Optional)

Please focus on:
1. **Disclaimer accuracy** — verify the listed files match what actually
   exists in each directory and that consequence descriptions are correct
2. **docs-notes tone** — the disclaimer was rewritten to acknowledge value
   rather than dismiss; check that it doesn't overstate the importance
3. **Label completeness** — verify that labels with "etc." aren't misleading
   in the other direction (implying more files than actually exist)

## Additional Notes

- The E501 (line too long) warnings in the IDE are expected — this project
  disables E501 in ruff config. The long disclaimer strings are intentional
  for readability.
- The `utility-scripts` paths were verified to be accurate and complete.
  All scripts in `scripts/` are either in `utility-scripts`, covered by
  another STRIPPABLE group (labels, repo-doctor, db), or deliberately kept
  (bootstrap.py, clean.py, customize.py, _imports.py, _progress.py).
- No unit tests exist for the disclaimer text itself — this is user-facing
  copy, best verified by running `--dry-run` interactively.
