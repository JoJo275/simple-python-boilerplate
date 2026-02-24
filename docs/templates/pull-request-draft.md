<!-- WORKING COPY — edit freely, this does NOT affect .github/PULL_REQUEST_TEMPLATE.md -->
<!-- Use this file to draft your PR description before pasting it into GitHub. -->
<!-- Suggested branch rename: feat/developer-experience-scripts -->
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

Developer experience improvements: new utility scripts, workflow consistency fixes, container setup, and documentation enhancements.

**What changes you made:**

- **New scripts** (`scripts/`):
  - `bootstrap.py` — One-command setup for fresh clones (creates all hatch envs, installs pre-commit hooks)
  - `clean.py` — Remove build artifacts and caches (`--dry-run`, `--include-venv`)
  - `doctor.py` — Print diagnostics bundle for bug reports (`--markdown` for GitHub issues)
  - `archive_todos.py` — Moved from `src/dev_tools/clean.py` with proper naming

- **customize.py enhancements**:
  - Added `--enable-workflows OWNER/REPO` flag for quick workflow enablement without full customization

- **Repository slug consistency**:
  - Fixed placeholder inconsistency: `YOURNAME/YOURTEMPLATE` → `YOURNAME/YOURREPO` across 30+ workflow files

- **Container/Dev setup**:
  - Added `.devcontainer/` configuration for VS Code dev containers
  - Added `docker-compose.yml` for local development
  - Added ADR 025 (container strategy)

- **Documentation**:
  - Added ADR 026 (no pip-tools for dependency management)
  - Enhanced `USING_THIS_TEMPLATE.md`, `developer-commands.md`, `release-policy.md`
  - Added `codecov.yml` configuration
  - Updated `copilot-instructions.md` with shebang/executable rules and hatch guidance

- **Tests**: Added `tests/unit/test_api.py`

**Why you made them:**

1. Bootstrap script eliminates manual setup steps for new contributors
2. Clean/doctor scripts provide essential developer utilities that were missing
3. Placeholder inconsistency caused customize.py to miss workflow files
4. Dev container support enables consistent development environments
5. Documentation gaps were causing friction for template users


## Related Issue

N/A — Developer experience improvements and template enhancement work.


## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [x] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] 📚 Documentation update
- [x] 🔧 Refactor (no functional changes)
- [x] 🧪 Test update

## How to Test

**Steps:**
1. Clone fresh or reset to main
2. Run `python scripts/bootstrap.py` — should create all hatch envs and install hooks
3. Run `python scripts/clean.py --dry-run` — should list artifacts without deleting
4. Run `python scripts/doctor.py --markdown` — should output diagnostics in markdown format
5. Run `python scripts/customize.py --enable-workflows --dry-run OWNER/REPO` — should show workflow files to update

**Test command(s):**
```bash
# Verify scripts have no syntax errors
hatch run python -m py_compile scripts/bootstrap.py scripts/clean.py scripts/doctor.py

# Run linting
hatch run ruff check scripts/

# Run tests
hatch run pytest tests/unit/test_api.py -v
```


## Risk / Impact

**Risk level:** Low

**What could break:**
- Workflow files now use `YOURNAME/YOURREPO` — existing forks using `YOURTEMPLATE` would need to update or use customize.py

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

- `scripts/bootstrap.py` — verify the hatch environment creation logic handles edge cases
- `scripts/customize.py` changes — ensure `--enable-workflows` works correctly with existing customization flow


## Additional Notes

Scripts with shebangs are now marked executable in git (`git add --chmod=+x`). The pre-commit hook `check-shebang-scripts-are-executable` enforces this going forward.
