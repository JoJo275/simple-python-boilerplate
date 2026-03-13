# Branch Workflows

<!-- TODO (template users): Update this document with your team's actual
     branch naming conventions, merge strategy preferences, and workflow
     patterns. Remove sections that don't apply to your team. -->

This guide covers branch management patterns, team collaboration workflows,
and common scenarios when working with feature branches and `main`.

For the release process itself (release-please, version bumps, CHANGELOG),
see [Releasing](../releasing.md).

---

## Branch Lifecycle

```text
create branch → commit → push → open PR → CI passes → review → merge → delete branch
```

Every code change follows this pattern. Direct pushes to `main` are blocked
by branch protection.

### Quick Reference

```bash
# Start a new branch from latest main
git fetch origin
git switch -c feature/my-feature origin/main

# Push and set upstream tracking
git push -u origin HEAD

# After PR is merged, clean up local branch
git switch main
git pull --ff-only
git branch -d feature/my-feature
```

---

## Keeping Your Branch Up to Date

When `main` moves ahead while you're working on a feature branch, you need
to incorporate those changes. Use **rebase**, not merge:

```bash
git fetch origin                  # download latest commits
git rebase origin/main            # replay your commits on top of updated main
git push --force-with-lease       # update remote (rebase rewrites history)
```

> **Why `--force-with-lease`?** It refuses to push if someone else pushed
> to your branch since your last fetch — preventing you from accidentally
> overwriting their work. Never use bare `--force`.

### When to Rebase

<!-- TODO (template users): Adjust these guidelines based on your team's
     rebase frequency preferences. Some teams rebase daily, others only
     before merge. -->

| Situation | Action |
| --------- | ------ |
| `main` has new commits you need | `git fetch origin && git rebase origin/main` |
| CI fails due to main changes | Rebase to get the fixes |
| Before requesting review | Rebase to ensure branch is current |
| Merge conflicts appear on PR | Rebase locally, resolve, force-push |
| Long-running branch (>1 week) | Rebase periodically to avoid conflict buildup |

### Understanding "Up to Date" vs "Diverged"

The git doctor shows two related but different characteristics:

- **"Up to date with main"** — Your branch contains all commits from `main`.
  There are 0 commits on `main` that aren't reachable from your branch.
  Measured by: `git rev-list --count HEAD..origin/main` = 0.

- **"Diverged from main"** — Your branch tip (HEAD) points to a different
  commit than `main`'s tip. This happens whenever you have commits of your
  own, even if you've rebased on top of the latest `main`.

**These are not contradictory.** A branch can be both "up to date" AND
"diverged" simultaneously. This is the *normal* state for an active feature
branch that's been rebased onto `main`:

```text
main:     A ← B ← C           (main tip = C)
branch:   A ← B ← C ← D ← E  (branch tip = E, contains all of main's commits)

Result:
  ✅ "up to date with main"  — 0 commits behind (C is reachable from E)
  📌 "diverged from main"    — branch tip E ≠ main tip C
```

The concerning case is when a branch is **behind main AND diverged** — that
means `main` has new commits your branch doesn't have yet:

```text
main:     A ← B ← C ← F ← G       (main moved ahead)
branch:   A ← B ← C ← D ← E       (branch doesn't have F, G)

Result:
  ⚠️ "2 commit(s) behind main"  — F and G are not on this branch
  📌 "diverged from main"       — branch tip E ≠ main tip G
```

**Fix:** `git fetch origin && git rebase origin/main` to incorporate `F`
and `G` into your branch.

---

## Working with the Release PR

<!-- TODO (template users): Adjust this section based on how your team
     handles release timing. Some teams merge the Release PR immediately
     after every feature; others batch features into releases. -->

release-please automatically creates a Release PR when releasable commits
land on `main`. This PR accumulates entries until you merge it.

### Feature Branch + Open Release PR

If a release-please PR is open while you're on a feature branch:

1. **Ignore it** — finish your feature work normally
2. **Merge your feature PR** to `main`
3. release-please re-runs and updates the Release PR to include your commits
4. Merge the Release PR when ready to cut a release

### Merging Release PR Before Your Branch

If you want to ship a release of previous work before continuing:

```bash
# After merging the release-please PR on GitHub:
git fetch origin
git rebase origin/main            # incorporate version bump
git push --force-with-lease       # update your branch
```

Conflicts are unlikely since release-please only touches `CHANGELOG.md`,
`__init__.py`, and `.release-please-manifest.json`.

---

## Common Scenarios

### Stale Branch Recovery

When a branch has been idle for many days and `main` has moved significantly:

```bash
git fetch origin
git rebase origin/main            # may have conflicts
# Resolve any conflicts, then:
git add <resolved-files>
git rebase --continue
git push --force-with-lease
```

If conflicts are too complex, you can abort and start fresh:

```bash
git rebase --abort                # undo the rebase attempt
git switch -c feature/my-feature-v2 origin/main  # fresh branch
git cherry-pick <commit-shas>     # selectively bring over your work
```

### Working on Multiple Features

Keep each feature on its own branch. Don't pile unrelated changes together:

```bash
# Feature A
git switch -c feature/add-login origin/main
# ... work, commit, push, open PR

# Feature B (independent of A)
git switch -c feature/add-dashboard origin/main
# ... work, commit, push, open PR
```

### Stacked Branches (Branching off a Feature Branch)

<!-- TODO (template users): Consider whether your team uses stacked branches.
     If not, this section can be removed. Stacked branches add complexity
     and are mainly useful for large features that benefit from incremental
     review. -->

Sometimes you need to build on work that's still under review:

```bash
git switch -c feature/part-2 feature/part-1   # branch from the feature, not main
```

**Warning:** When `feature/part-1` is merged via rebase+merge, its commit
SHAs change. You'll need to rebase `part-2` onto `main` afterward:

```bash
# After part-1 is merged to main:
git fetch origin
git rebase origin/main            # part-2 now sits on main (with part-1's changes)
git push --force-with-lease
```

---

## CI Workflow Triggers

<!-- TODO (template users): Update this table if you add or remove workflows,
     or change their trigger conditions. Keep in sync with docs/workflows.md. -->

Understanding when CI runs helps avoid surprise failures:

| What you do | What triggers |
| ----------- | ------------- |
| Push to feature branch (no PR) | Nothing — CI only runs on PRs targeting `main` |
| Open PR targeting `main` | All PR workflows (lint, test, typecheck, security) |
| Push to PR branch | CI re-runs on the updated PR |
| Merge PR to `main` | Push-to-main workflows (release-please, doctor-all) |
| release-please creates tag | Release workflow (build, publish, SBOM) |

> **Pre-commit hooks** are your local safety net. They catch issues before
> code reaches CI. See the [Releasing guide](../releasing.md) for hook
> installation instructions.

### Skipped Workflows

Some workflows have **repository guards** — they only run if repository
variables are set or the repo slug matches a configured value. If a workflow
shows as "skipped" in your PR checks:

1. Check the workflow's `if:` condition for a `YOURNAME/YOURREPO` guard
2. Either replace the placeholder with your repo slug, or set the
   corresponding repository variable in Settings → Variables → Actions

Common guards:

| Workflow | Variable to enable |
| -------- | ------------------ |
| Doctor All | `ENABLE_DOCTOR_ALL` or `ENABLE_WORKFLOWS` |
| Repo Doctor | `ENABLE_REPO_DOCTOR` or `ENABLE_WORKFLOWS` |
| Release Please | `ENABLE_RELEASE_PLEASE` |
| Release | `ENABLE_RELEASE` |
| Commit Lint | `ENABLE_COMMIT_LINT` |

> **Skipped ≠ failed.** The CI gate treats skipped workflows as passing.
> This is by design — optional workflows shouldn't block merges.

---

## Branch Naming Conventions

| Prefix | Use for | Example |
| ------ | ------- | ------- |
| `feature/` | New functionality | `feature/add-login` |
| `fix/` | Bug fixes | `fix/null-byte-check` |
| `chore/` | Maintenance, deps | `chore/update-ruff` |
| `docs/` | Documentation | `docs/release-guide` |
| `spike/` | Experimental / exploratory | `spike/try-fastapi` |
| `wip/` | Work in progress / scratch | `wip/2026-03-06-scratch` |
| `hotfix/` | Urgent production fixes | `hotfix/critical-auth-bug` |
| `release/` | Manual release prep | `release/v2.0.0` |
| `refactor/` | Code restructuring | `refactor/extract-auth` |
| `test/` | Test additions/experiments | `test/integration-suite` |
| `ci/` | CI/CD changes | `ci/add-matrix-test` |

> For the full branch prefixes reference, see
> [learning.md — Branch Prefixes](../notes/learning.md#branch-prefixes).

---

## Post-Merge Cleanup

After a PR is merged, clean up stale local branches:

```bash
# Update remote refs and prune deleted branches
git fetch --prune

# Delete local branches whose remote is gone
git branch -vv | grep ': gone]' | awk '{print $1}' | xargs git branch -d

# Or manually:
git branch -d feature/my-feature
```

The git doctor script flags stale branches (>30 days since last commit)
and branches whose remote tracking ref is `[gone]`.

---

## See Also

- [Releasing](../releasing.md) — Release process, conventional commits, version bumps
- [Pull Requests](pull-requests.md) — PR creation and review guidelines
- [Workflows](../workflows.md) — CI/CD workflow reference
- [ADR 022 — Rebase+merge strategy](../adr/022-rebase-merge-strategy.md)
- [ADR 023 — Branch protection rules](../adr/023-branch-protection-rules.md)
