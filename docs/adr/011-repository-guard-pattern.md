# ADR 011: Repository guard pattern for optional workflows

## Status

Accepted

## Context

This is a template repository. When someone creates a new project from this template (or forks it), all GitHub Actions workflows are copied over. Many workflows require additional setup (secrets, tokens, external services) that new users haven't configured yet.

Problems without a guard:

- Workflows fail immediately on forks/clones with confusing error messages
- Users waste Actions minutes on workflows they haven't set up
- Some workflows (e.g., PyPI publish, Codecov) may expose configuration issues publicly

Options considered:

- **Disable all optional workflows by default** — Rename files with `_` prefix or put in a `disabled/` folder. Users must manually enable each one.
- **Use `workflow_dispatch` only** — No automatic triggers; users must manually run each workflow. Loses the automation benefit.
- **Repository guard `if:` condition** — Workflows exist and have proper triggers but skip execution unless the repo matches a known slug or opt-in variable is set.

## Decision

Use a repository guard pattern in all optional workflows. Each workflow job includes an `if:` condition that checks one of two opt-in methods:

```yaml
if: >-
  ${{
    github.repository == 'YOURNAME/YOURTEMPLATE'
    || vars.ENABLE_<WORKFLOW_NAME> == 'true'
  }}
```

### Two ways to opt in

| Method | How | Best for |
|--------|-----|----------|
| **Option A** | Replace `YOURNAME/YOURTEMPLATE` with your repo slug in the YAML | Simple, permanent |
| **Option B** | Set `vars.ENABLE_<WORKFLOW>` repository variable to `'true'` | No YAML edits needed; toggleable |

## Consequences

### Positive

- Workflows are visible and well-documented from day one — users can read them to understand what's available
- No file renaming or directory juggling needed to enable/disable
- Guards are self-documenting with TODO comments explaining both options
- Repository variables (Option B) allow enabling/disabling without code changes
- Workflows don't fail on forks — they silently skip

### Negative

- Every optional workflow needs the boilerplate guard condition
- Template users must remember to opt in (guards block execution by default)
- The `YOURNAME/YOURTEMPLATE` placeholder can be confusing if not updated

### Neutral

- Core workflows (test, lint) don't need guards — they should always run
- The pattern is consistent across all optional workflows in this template
