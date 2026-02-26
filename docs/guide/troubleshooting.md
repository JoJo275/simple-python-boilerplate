# Troubleshooting & FAQ

Common problems, error messages, and their solutions. If you're stuck,
check here before opening an issue.

<!-- TODO (template users): Add project-specific troubleshooting entries
     as you discover them. Remove template-specific entries that don't
     apply to your project. -->

---

## Installation & Setup

### `ModuleNotFoundError: No module named 'simple_python_boilerplate'`

**Cause:** The package isn't installed. The `src/` layout intentionally
prevents direct imports without installation.

**Fix:**

```bash
# Using Hatch (recommended)
hatch shell

# Or manual install
pip install -e .
```

The `-e` flag means "editable" — your source changes reflect immediately
without reinstalling. See [ADR 001](../adr/001-src-layout.md) for why the
`src/` layout requires this.

---

### `pip install -e .` fails with build errors

**Cause:** Usually a missing build dependency or wrong Python version.

**Fix:**

1. Check Python version: `python --version` (need 3.11+)
2. Upgrade pip: `pip install --upgrade pip`
3. Try Hatch instead: `hatch shell` (handles everything automatically)

---

### Hatch environment is stale after removing a dependency

**Cause:** Hatch doesn't auto-uninstall removed packages. If you remove a
dependency from `pyproject.toml`, the old package silently remains in the env.

**Fix:**

```bash
hatch env remove default
hatch shell  # recreates the environment from scratch
```

---

### `command not found: hatch`

**Cause:** Hatch isn't installed globally or isn't on your PATH.

**Fix:**

```bash
# Install globally (recommended)
pip install hatch

# Or use pipx for isolation
pipx install hatch

# Verify
hatch --version
```

---

### `command not found: task`

**Cause:** Task runner (go-task) isn't installed.

**Fix:**

See [Task installation docs](https://taskfile.dev/installation/). On macOS:
`brew install go-task`. On Windows: `choco install go-task` or
`scoop install task`.

Task is optional — every `task <name>` command has a `hatch run` equivalent
documented in the [Taskfile.yml](../../Taskfile.yml).

---

## Pre-commit Hooks

### Pre-commit hooks aren't running

**Cause:** Hooks aren't installed in your local git repo.

**Fix:**

```bash
pre-commit install                              # pre-commit stage
pre-commit install --hook-type commit-msg        # commit-msg stage
pre-commit install --hook-type pre-push          # pre-push stage
```

All three stages need to be installed separately. See
[ADR 008](../adr/008-pre-commit-hooks.md) for the full hook inventory.

---

### `deptry` hook fails with import errors

**Cause:** `deptry` needs access to your installed packages (unlike most hooks
that run in pre-commit's isolated environment). It runs as a `local`/`system`
hook via `hatch run deptry .`.

**Fix:**

1. Make sure you're in the Hatch environment: `hatch shell`
2. Run manually to see the full error: `hatch run deptry .`
3. If packages are missing, recreate the env: `hatch env remove default && hatch shell`

---

### Hook fails on first run / downloads slowly

**Cause:** Pre-commit downloads and caches hook environments on first use.
This is normal.

**Fix:** Wait for the download. Subsequent runs are fast (cached). To
pre-download all hooks: `pre-commit install-hooks`.

---

### `check-shebang-scripts-are-executable` fails

**Cause:** A script has a shebang (`#!/usr/bin/env python3`) but isn't
marked as executable in git.

**Fix:**

```bash
git add --chmod=+x scripts/my_script.py
```

---

## Git & Commits

### Commit rejected: "commit message does not match pattern"

**Cause:** The `commit-msg` hook (commitizen) validates that your message
follows Conventional Commits format.

**Fix:** Use the correct format:

```
<type>(<scope>): <description>

# Examples:
feat(cli): add verbose flag
fix: handle empty input gracefully
docs: update installation guide
chore: bump ruff to 0.15.1
```

Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`,
`build`, `ci`, `chore`, `revert`.

Or use the interactive helper: `task commit` (runs `cz commit`).

---

### Push rejected: tests fail in pre-push hook

**Cause:** The pre-push hook runs `pytest` and `pip-audit`. If tests fail
or vulnerabilities are found, the push is blocked.

**Fix:**

1. Run tests locally: `hatch run test:run` or `task test`
2. Fix failures
3. Push again

To bypass in emergencies (not recommended): `git push --no-verify`.

---

## CI/CD & GitHub Actions

### Workflows don't run on my fork

**Cause:** Repository guards disable all workflows by default on forks and
clones. This is intentional — see
[ADR 011](../adr/011-repository-guard-pattern.md).

**Fix (pick one):**

| Method | How |
|--------|-----|
| **Script** | `python scripts/customize.py --enable-workflows myorg/myrepo` |
| **Global** | Set repo variable `ENABLE_WORKFLOWS = 'true'` (Settings → Secrets and variables → Actions → Variables) |
| **Per-workflow** | Set `ENABLE_<NAME> = 'true'` (e.g. `ENABLE_TEST`) |
| **Edit YAML** | Replace `YOURNAME/YOURREPO` with your repo slug in each file |

---

### CI gate times out / stays pending

**Cause:** A required check name was changed (workflow job renamed) but
`REQUIRED_CHECKS` in `ci-gate.yml` still references the old name.

**Fix:**

1. Check which checks are missing: look at the PR's Checks tab
2. Update `REQUIRED_CHECKS` in `.github/workflows/ci-gate.yml`
3. Verify: `grep -r 'ci-gate: required' .github/workflows/`

---

### "Resource not accessible by integration" error

**Cause:** The workflow's `permissions:` block doesn't include the needed
permission.

**Fix:** Add the required permission to the workflow. Common ones:

```yaml
permissions:
  contents: read          # Read repo contents (default)
  contents: write         # Push commits, create releases
  pull-requests: write    # Comment on PRs, approve
  issues: write           # Label, comment on issues
  packages: write         # Push container images
```

---

### Path-filtered workflow doesn't run on my PR

**Cause:** The PR doesn't change files matching the workflow's path filter.
This is expected behavior — e.g., `bandit.yml` only runs when Python source
files change.

**Fix:** No fix needed. These workflows also run on `push` to `main` and on
schedules, so nothing slips through permanently.

---

### Dependabot PRs fail CI

**Cause:** Dependabot can't access repository secrets, which may be needed
by some workflows.

**Fix:** The `auto-merge-dependabot.yml` workflow handles this — it auto-
approves and merges minor/patch updates after CI passes. For major version
bumps, review manually.

---

## Testing

### Tests pass locally but fail in CI

**Cause:** Common reasons:

- Different Python version (CI runs 3.11, 3.12, 3.13)
- Missing editable install (CI does `pip install -e ".[test]"`)
- Platform-specific behavior (CI runs Ubuntu)
- Stale cached dependencies

**Fix:**

1. Run the full matrix locally: `hatch run test:run` (tests all Python versions)
2. Check the CI log for the specific Python version that failed
3. Ensure your Hatch env is fresh: `hatch env remove default && hatch shell`

---

### `pytest` can't find tests

**Cause:** Tests need to be in `tests/` and follow pytest naming conventions.

**Fix:**

- Test files: `test_*.py` or `*_test.py`
- Test functions: `def test_*()`
- Test classes: `class Test*`
- Verify pytest config in `pyproject.toml` under `[tool.pytest.ini_options]`

---

### Coverage report shows 0% / missing lines

**Cause:** Coverage is measuring the installed package, not your source files.

**Fix:** Make sure `[tool.coverage.run]` in `pyproject.toml` has
`source = ["simple_python_boilerplate"]` (not `src/simple_python_boilerplate`).
The `--cov` flag should point to the package name, not the file path.

---

## Linting & Type Checking

### Ruff reports errors that don't matter

**Cause:** Some rules may not apply to your project.

**Fix:** Disable specific rules in `pyproject.toml`:

```toml
[tool.ruff.lint]
ignore = ["E501"]  # Already disabled — line length

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # Allow assert in tests
```

See the [Ruff rule index](https://docs.astral.sh/ruff/rules/) to understand
each code.

---

### mypy errors on third-party libraries

**Cause:** The library doesn't ship type stubs.

**Fix:**

```toml
# In pyproject.toml
[[tool.mypy.overrides]]
module = ["some_library.*"]
ignore_missing_imports = true
```

Or install stubs: `pip install types-requests` (for requests, etc.).

---

## Documentation

### `mkdocs build` fails with link warnings

**Cause:** MkDocs in `--strict` mode flags broken internal links. Links to
files outside `docs/` (like `pyproject.toml`) are expected to produce INFO
messages — these are downgraded via the `validation:` config in `mkdocs.yml`.

**Fix:**

- For broken doc-to-doc links: fix the relative path
- For repo-file links (pyproject.toml, workflows): these work on GitHub but
  MkDocs can't resolve them — this is expected
- Check the full output for actual `ERROR` lines vs. `INFO` messages

---

### API docs show "Module not found"

**Cause:** `mkdocstrings` can't find your package. Usually means it's not
installed in the docs environment.

**Fix:**

```bash
# Use the docs environment (includes mkdocstrings + your package)
hatch run docs:build

# Don't use raw mkdocs commands — they won't have your package
```

---

## Containers

### Container build fails

**Cause:** Common reasons:

- `Containerfile` references files not in the build context
- Build arg or Python version mismatch
- Network issues downloading packages

**Fix:**

1. Build locally to see errors: `docker build -f Containerfile .`
2. Check the stage that fails in the multi-stage build
3. Ensure all `COPY` paths exist relative to the repo root

---

### Container image is too large

**Cause:** The multi-stage build should produce a ~150 MB image. If it's
larger, dev dependencies may be leaking into the runtime stage.

**Fix:** Check that the final `FROM` stage in `Containerfile` only copies
the built package, not the full build environment. The runtime stage should
not have `pip install -e ".[dev]"`.

---

## Miscellaneous

### `_typos.toml` — typos flags a valid word

**Cause:** The typos spellchecker doesn't know the word.

**Fix:** Add it to `_typos.toml`:

```toml
[default.extend-words]
# Word = "Word" keeps the original casing
MySacronym = "MySacronym"
```

---

### Scripts fail on Windows with "permission denied"

**Cause:** Windows doesn't use Unix file permissions the same way.

**Fix:**

- Use `python scripts/my_script.py` instead of `./scripts/my_script.py`
- Or ensure Git is configured to handle line endings:
  `git config core.autocrlf true`

---

## Still Stuck?

1. Search existing [issues](https://github.com/JoJo275/simple-python-boilerplate/issues) — someone may have hit the same problem
2. Run the diagnostic tool: `spb-doctor` or `python scripts/doctor.py`
3. Open a [new issue](https://github.com/JoJo275/simple-python-boilerplate/issues/new) with:
   - What you tried
   - Expected vs. actual behavior
   - Output of `spb-doctor`
   - Python version and OS

---

## Related Documentation

- [Dev Setup](../development/dev-setup.md) — environment setup guide
- [CI/CD Design](../design/ci-cd-design.md) — pipeline architecture and debugging
- [Using This Template](../USING_THIS_TEMPLATE.md) — first-time setup checklist
- [Tooling](../tooling.md) — what each tool does
