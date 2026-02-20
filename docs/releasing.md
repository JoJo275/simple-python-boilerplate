# Releasing

This guide covers the automated release process and how releases are created.

---

## Overview

Releases are **fully automated** via [release-please](https://github.com/googleapis/release-please). The workflow:

1. Conventional commits land on `main` (via rebase+merge)
2. release-please creates a **Release PR** with version bump + CHANGELOG update
3. You review/edit the Release PR and merge it
4. release-please creates a **git tag** and **GitHub Release**
5. The tag triggers the [release workflow](.github/workflows/release.yml) which builds, publishes, and attaches artifacts

**No manual version bumping, tagging, or CHANGELOG editing required.**

---

## How It Works

### The Release PR

When releasable commits exist on `main` (i.e., commits with `feat:`, `fix:`, `perf:`, or `BREAKING CHANGE`), release-please automatically creates or updates a Release PR titled something like:

```
chore(main): release 1.2.0
```

This PR contains:
- **CHANGELOG.md** — new entries generated from commit messages
- **`__init__.py`** — updated `__version__` fallback
- **`.release-please-manifest.json`** — updated version tracker

**You can edit this PR before merging.** This is your chance to:
- Clean up redundant CHANGELOG entries
- Reword entries for clarity
- Add context that commit messages didn't capture

### Version Determination (SemVer)

release-please reads conventional commit prefixes to determine the version bump:

| Commit type | Version bump | Example |
|-------------|-------------|---------|
| `fix:` | **Patch** (0.0.X) | `fix: handle null input` |
| `feat:` | **Minor** (0.X.0) | `feat: add user login` |
| `feat!:` or `BREAKING CHANGE:` footer | **Major** (X.0.0) | `feat!: remove deprecated API` |
| `perf:` | **Patch** (0.0.X) | `perf: cache DB queries` |
| `docs:`, `chore:`, `ci:`, etc. | **No release** | Only releasable types trigger a Release PR |

> While the project is pre-1.0 (`major_version_zero: true`), breaking changes bump minor instead of major.

### What Triggers a Release

A Release PR is created/updated when **any** of these commit types land on `main`:
- `feat:` — new features
- `fix:` — bug fixes
- `perf:` — performance improvements
- `revert:` — reverted changes
- Any commit with a `BREAKING CHANGE:` footer

Commits with `docs:`, `chore:`, `ci:`, `test:`, `refactor:`, `style:`, `build:` **do not** trigger releases on their own (they are hidden from the CHANGELOG by default).

### CHANGELOG Format

The CHANGELOG is automatically generated. With rebase+merge, each conventional commit becomes its own entry:

```markdown
## [1.2.0](https://github.com/owner/repo/compare/v1.1.0...v1.2.0) (2026-03-15)

### Features

* add user authentication module (#42)
* add login CLI command (#42)
* add password hashing utility (#43)

### Bug Fixes

* handle empty username in auth flow (#44)
* correct token expiration calculation (#44)
```

### After Merging the Release PR

When you merge the Release PR, release-please automatically:

1. Creates a git tag (e.g., `v1.2.0`)
2. Creates a GitHub Release with CHANGELOG entries as release notes

The tag then triggers the [release.yml](.github/workflows/release.yml) workflow which:

1. Builds sdist + wheel (hatch-vcs reads the tag for version)
2. Generates SLSA build provenance attestations
3. Publishes to PyPI (if `PUBLISH_TOKEN` secret is configured)
4. Generates SPDX and CycloneDX SBOMs
5. Uploads all artifacts to the GitHub Release

---

## Tools in This Workflow

| Tool | Role | Configuration |
|------|------|---------------|
| **release-please** | Creates Release PR, bumps version, generates CHANGELOG, creates tags + GitHub Releases | `release-please-config.json`, `.release-please-manifest.json` |
| **hatch-vcs** | Derives Python package version from git tags at build time | `pyproject.toml` `[tool.hatch.version]` |
| **commitizen** | Validates commit messages locally (pre-commit hook) + interactive `cz commit` | `pyproject.toml` `[tool.commitizen]` |
| **commit-lint.yml** | CI safety net — validates all PR commits follow conventional format | `.github/workflows/commit-lint.yml` |
| **release.yml** | Builds, publishes, generates SBOMs on tag push | `.github/workflows/release.yml` |

---

## Commit Message Conventions

Since rebase+merge preserves individual commits, **every commit message matters**:

```
feat: add user login endpoint (#42)

Why: Users need to authenticate to access protected resources.

What changed: Added /api/login endpoint with JWT token generation.

How tested: Unit tests for auth module, integration test for login flow.
```

**Key conventions:**
- Use conventional prefix (`feat:`, `fix:`, etc.) for meaningful changes
- The `(#PR)` reference is added automatically by GitHub (see below)
- Use non-conventional messages for WIP/iteration (they won't appear in CHANGELOG)
- The PR description is for **human reviewers** — automation reads commits, not the PR body

### PR Linkage (Automatic)

With rebase+merge, GitHub automatically appends `(#PR)` to each commit's subject line when you merge via the web UI. **No configuration or manual effort needed.**

**The flow:**

1. You write locally: `feat: add user authentication`
2. You push and open PR #42
3. When you click "Rebase and merge", each commit becomes: `feat: add user authentication (#42)`
4. release-please reads the commit on `main` and generates CHANGELOG with `(#42)` as a clickable link

This means every commit on `main` automatically points back to its PR — preserving the review context, discussion, and approval history even though rebase+merge doesn't create merge commits.

**Optional: Issue references in commit body.** If you also want to link to issues (requirements, bug reports), add a footer:

```
feat: add user authentication

Refs: #15
```

GitHub's closing keywords (`Fixes #28`, `Closes #30`, `Resolves #15`) also work and will auto-close the referenced issue on merge.

---

## Publishing to PyPI

PyPI publishing is disabled by default. To enable:

### Setup Trusted Publishing

1. Go to [PyPI](https://pypi.org/) and create an account
2. Create a new project or claim the package name
3. Configure **Trusted Publishing**:
   - Publisher: GitHub Actions
   - Repository: `your-username/simple-python-boilerplate`
   - Workflow: `release.yml`
   - Environment: `release`

### Add the Secret

Add `PUBLISH_TOKEN` in Settings → Secrets and variables → Actions → Secrets.

### Create GitHub Environment

1. Go to **Settings → Environments** in your repository
2. Create an environment named `release`
3. (Optional) Add required reviewers for manual approval

---

## GitHub Repository Settings

Configure these settings to enforce the release workflow:

### Merge Strategy
- **Enable:** "Allow rebase merging"
- **Disable:** "Allow merge commits" and "Allow squash merging"
- **Enable:** "Automatically delete head branches"

### Branch Protection (main)
- Require status checks to pass before merging
- Require pull request reviews before merging
- Require linear history

### Repository Variables
Enable the workflows by setting these in Settings → Variables:
- `ENABLE_RELEASE_PLEASE = true`
- `ENABLE_RELEASE = true`
- `ENABLE_COMMIT_LINT = true`

### Workflow Guards Quick Reference

What runs, what doesn't, and why:

| Trigger | Workflow | Guard (must be set) | What happens |
|---------|----------|--------------------|--------------|
| Push to `main` | `release-please.yml` | `ENABLE_RELEASE_PLEASE` variable | Creates/updates a Release PR with CHANGELOG + version bump |
| PR targeting `main` | `commit-lint.yml` | `ENABLE_COMMIT_LINT` variable | Validates all PR commits follow conventional format |
| Tag push `v*.*.*` | `release.yml` → **build** job | `ENABLE_RELEASE` variable | Builds sdist + wheel, generates SLSA attestations |
| Tag push `v*.*.*` | `release.yml` → **publish** job | `PUBLISH_TOKEN` **secret** | Publishes to PyPI. **If secret is missing, skips gracefully** (workflow stays green) |
| Tag push `v*.*.*` | `release.yml` → **sbom** job | `ENABLE_RELEASE` variable | Generates SPDX + CycloneDX SBOMs |
| Tag push `v*.*.*` | `release.yml` → **upload-assets** job | `ENABLE_RELEASE` variable | Uploads dist + SBOMs to the GitHub Release |

**Key point:** Setting `ENABLE_RELEASE = true` does **not** publish to PyPI. It builds artifacts and uploads them to the GitHub Release. PyPI publishing only happens if you also add the `PUBLISH_TOKEN` secret. Without it, the publish step shows a notice and passes.

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

| Version Part | When to Increment |
|--------------|-------------------|
| **MAJOR** (1.x.x) | Breaking API changes |
| **MINOR** (x.1.x) | New features, backward compatible |
| **PATCH** (x.x.1) | Bug fixes, backward compatible |

### Pre-release Versions

For pre-releases, use suffixes:

- `1.0.0a1` — Alpha
- `1.0.0b1` — Beta
- `1.0.0rc1` — Release candidate

### How Version Is Determined

The package version comes from **git tags** via hatch-vcs:

| Context | Version source | Example |
|---------|---------------|---------|
| Tagged release | Git tag | `1.2.0` |
| Dev build (after tag) | Tag + distance + hash | `1.2.1.dev3+gabcdef` |
| No tags exist | Fallback in `__init__.py` | `0.1.0` |
| Outside git repo | Fallback | `0.0.0+unknown` |

---

## Troubleshooting

### Release PR Not Appearing

- Ensure `ENABLE_RELEASE_PLEASE` variable is set to `true`
- Check that releasable commits exist (`feat:`, `fix:`, `perf:`, or breaking)
- Verify the release-please workflow ran successfully in the Actions tab

### Version Mismatch

- hatch-vcs derives version from the **latest tag** — ensure the tag exists
- Run `hatch version` locally to see what version hatch-vcs resolves
- The `__init__.py` fallback is only used when `_version.py` is not generated

### Build Fails

- Ensure `pyproject.toml` is valid
- Check that hatch-vcs can find a tag: `git describe --tags`
- Verify `python -m build` works locally

### Tag Already Exists

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0
```

---

## Pros and Cons of This Workflow

### Pros

- **Fully automated** — no manual version bumps, tags, or CHANGELOG editing
- **Reviewable** — Release PR can be edited before merge
- **Consistent** — SemVer enforced by commit conventions, not human judgment
- **No CHANGELOG conflicts** — generated from commits, never hand-edited on main
- **Fine-grained** — individual commits appear in CHANGELOG (rebase+merge)
- **Traceable** — commits → PRs → issues → CHANGELOG → GitHub Release

### Cons

- **Commit discipline** — every conventional commit on main appears in CHANGELOG
- **Noisy commits** — iterative fix: commits within a PR produce multiple entries (mitigated by editing Release PR)
- **Changed SHAs** — rebase+merge re-hashes commits (original branch SHAs lost)
- **No merge graph** — cannot visually see where a PR started/ended in `git log --graph`
- **Two version sources** — hatch-vcs (build-time) + `__init__.py` fallback (human-readable)
- **Google dependency** — release-please is maintained by Google

### Alternative Workflows That Could Replace Parts

| Tool | What it could replace | Trade-off |
|------|----------------------|-----------|
| **python-semantic-release** | release-please | No reviewable Release PR; pushes tags directly |
| **towncrier** | CHANGELOG generation | Fragment files per PR; can't auto-determine version |
| **git-cliff** | CHANGELOG generation | CLI only; no PR/release automation |
| **squash+merge** | rebase+merge | Cleaner but loses individual commit detail |

---

## See Also

- [Release Policy](release-policy.md) — Versioning, deprecation, and support policy
- [CHANGELOG.md](../CHANGELOG.md) — Version history
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Contribution guidelines
- [ADR 021 — Automated release pipeline](adr/021-automated-release-pipeline.md)
- [ADR 022 — Rebase+merge strategy](adr/022-rebase-merge-strategy.md)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [release-please](https://github.com/googleapis/release-please)
- [hatch-vcs](https://github.com/ofek/hatch-vcs)
- [commitizen](https://commitizen-tools.github.io/commitizen/)
