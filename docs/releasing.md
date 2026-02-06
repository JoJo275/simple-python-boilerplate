# Releasing

This guide covers the release process for publishing new versions.

---

## Overview

Releases are triggered by pushing a version tag (e.g., `v1.0.0`) to the repository. The [release workflow](../.github/workflows/release.yml) automatically builds distribution artifacts when a tag matching `v*.*.*` is pushed.

---

## Release Checklist

### Before Releasing

1. **Ensure all tests pass**

   ```bash
   pytest
   ```

2. **Verify linting and type checks pass**

   ```bash
   ruff check src/ tests/
   mypy src/
   ```

3. **Update the changelog**

   Move items from `[Unreleased]` to a new version section in [CHANGELOG.md](../CHANGELOG.md):

   ```markdown
   ## [1.0.0] - 2026-02-06

   ### Added
   - New feature X
   ```

4. **Update the version number**

   Edit the version in [pyproject.toml](../pyproject.toml):

   ```toml
   [project]
   version = "1.0.0"
   ```

5. **Commit the version bump**

   ```bash
   git add CHANGELOG.md pyproject.toml
   git commit -m "chore: release v1.0.0"
   ```

---

## Creating a Release

### 1. Tag the Release

```bash
git tag v1.0.0
git push origin v1.0.0
```

### 2. Verify the Workflow

The [release workflow](../.github/workflows/release.yml) will:

- Build source distribution (`sdist`)
- Build wheel distribution (`wheel`)
- Upload artifacts to GitHub Actions

Check the **Actions** tab in GitHub to verify the build succeeded.

### 3. Create a GitHub Release (Optional)

1. Go to **Releases** in your GitHub repository
2. Click **Draft a new release**
3. Select the tag you just pushed
4. Add release notes (copy from CHANGELOG)
5. Attach the built artifacts from the workflow
6. Publish the release

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

### Enable the Workflow

Uncomment the `publish` job in [.github/workflows/release.yml](../.github/workflows/release.yml):

```yaml
publish:
  name: Publish to PyPI
  needs: build
  runs-on: ubuntu-latest
  environment: release
  permissions:
    id-token: write  # Required for trusted publishing

  steps:
    - name: Download distribution artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
```

### Create GitHub Environment

1. Go to **Settings → Environments** in your repository
2. Create an environment named `release`
3. (Optional) Add required reviewers for manual approval

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

---

## Troubleshooting

### Build Fails

- Ensure `pyproject.toml` is valid
- Check that all required files are included
- Verify `python -m build` works locally

### Tag Already Exists

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0
```

### Wrong Version Tagged

1. Delete the incorrect tag (see above)
2. Fix the version in `pyproject.toml`
3. Commit and create a new tag

---

## See Also

- [CHANGELOG.md](../CHANGELOG.md) — Version history
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Contribution guidelines
- [Keep a Changelog](https://keepachangelog.com/) — Changelog format
- [Semantic Versioning](https://semver.org/) — Versioning specification
