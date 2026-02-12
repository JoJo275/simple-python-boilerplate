# Pull Request Guidelines

How to create, review, and merge pull requests in this project.

## Before Opening a PR

1. **Create a feature branch** from `main`
   ```bash
   git checkout main
   git pull --ff-only
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear, atomic commits

   Follow the [Conventional Commits](https://www.conventionalcommits.org/) format (see [development.md](development.md#commit-messages-conventional-commits) for the full rules):
   ```bash
   git commit -m "feat: add user authentication"
   ```

3. **Run quality checks locally**

   **Quick (fix & test):**
   ```bash
   ruff format . && ruff check --fix . && pytest
   ```

   **Apply fixes:**
   ```bash
   ruff format .             # Auto-format code
   ruff check --fix .        # Auto-fix lint issues
   ```

   **Verify (CI-like):**
   ```bash
   pytest                    # Tests pass
   ruff check .              # Linting passes
   ruff format --check .     # Formatting correct
   pyright                   # Type checking (optional, recommended)
   ```

   > See [developer-commands.md](developer-commands.md) for the full command reference.

4. **Push your branch**
   ```bash
   git push -u origin feature/your-feature-name
   ```

## Creating a Pull Request

### Title Format

Use conventional commit style for PR titles:

| Prefix | Use For |
|--------|---------|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `docs:` | Documentation only |
| `chore:` | Maintenance, deps |
| `refactor:` | Code restructuring |
| `test:` | Adding/fixing tests |
| `ci:` | CI/CD changes |

**Examples:**
- `feat: add user authentication`
- `fix: resolve login timeout issue`
- `docs: update installation guide`

### Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated (if needed)
```

## Code Review Guidelines

### For Authors

- Prefer small, focused PRs — if larger than ~400 lines, explain why in the description
- Respond to feedback promptly
- Don't take feedback personally — it's about the code
- Explain *why*, not just *what*

### For Reviewers

- Be constructive and kind
- Explain reasoning behind suggestions
- Approve when "good enough" — perfect is the enemy of done
- Use conventional comments:

| Prefix | Meaning |
|--------|---------|
| `nit:` | Minor style preference, optional |
| `suggestion:` | Consider this approach |
| `question:` | Need clarification |
| `issue:` | Must be addressed |

### What Reviewers Look For

- [ ] Tests added or updated for new/changed behavior
- [ ] Documentation updated (if user-facing changes)
- [ ] Type hints on public functions
- [ ] Backwards compatibility considered (or breaking change noted)
- [ ] No unrelated changes bundled in
- [ ] Commit messages follow conventional format

## Merging

### Merge Strategy

This project uses **Rebase and Merge**:
- Replays commits on top of `main` without a merge commit
- Preserves individual commit history for a linear changelog
- Keeps `main` history clean and easy to follow

> **Tip:** Keep commits atomic and well-described since they will appear individually in the main branch history.

### Before Merging

1. All CI checks pass (green checkmarks)
2. At least one approval (if required)
3. No unresolved conversations
4. Branch is up-to-date with `main`

**Updating your branch (rebase workflow):**
```bash
git fetch origin
git rebase origin/main
# Resolve any conflicts, then:
git rebase --continue
git push --force-with-lease
```

> **Solo practice note:** If branch protection requires approval, you'll need a second reviewer (collaborator or second account) or an admin bypass rule. Configure this in repository settings to avoid locking yourself out.

### After Merging

- Delete the feature branch (GitHub can do this automatically)
- Close related issues (use `Closes #123` in PR description)

## Draft PRs

Use a **Draft PR** when:
- You want CI feedback early but the work isn't ready to merge
- You're seeking early design feedback before finishing implementation
- You want to share progress without triggering review notifications

Convert to "Ready for review" when you're done.

## Branch Naming

```
feature/short-description    # New features
fix/issue-description        # Bug fixes
docs/what-changed            # Documentation
chore/maintenance-task       # Maintenance
ci/workflow-change           # CI/CD changes
```

## See Also

- [CONTRIBUTING.md](../../CONTRIBUTING.md) — General contribution guidelines
- [labels.md](../labels.md) — Issue and PR labels
- [dev-setup.md](dev-setup.md) — Environment setup
- [development.md](development.md) — Daily workflows
