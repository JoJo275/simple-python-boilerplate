# .github/

<!--
TODO: This README is NOT common practice.
      It exists only to document GitHub configuration for template users.
      REMOVE this file when using this template for a real project.
-->

GitHub-specific configuration files and templates.

## Contents

| File/Directory | Description |
|----------------|-------------|
| [workflows/](workflows/) | GitHub Actions CI/CD workflows |
| [ISSUE_TEMPLATE/](ISSUE_TEMPLATE/) | Issue templates |
| [PULL_REQUEST_TEMPLATE.md](PULL_REQUEST_TEMPLATE.md) | PR template |
| [dependabot.yml](dependabot.yml) | Dependabot configuration |
| [CODEOWNERS](CODEOWNERS) | Code ownership rules |
| [FUNDING.yml](FUNDING.yml) | Sponsorship links |
| [copilot-instructions.md](copilot-instructions.md) | GitHub Copilot guidelines |

## Workflows

| Workflow | Trigger | Description |
|----------|---------|-------------|
| [test.yml](workflows/test.yml) | Push/PR to main | Run pytest |
| [lint-format.yml](workflows/lint-format.yml) | Push/PR to main | Ruff linting and formatting |
| [release.yml](workflows/release.yml) | Tag push | Build and publish |
| [spellcheck.yml](workflows/spellcheck.yml) | Push/PR | Spell checking |

## Key Decisions

- **Actions pinned to SHAs** — See [ADR 004](../docs/adr/004-pin-action-shas.md)
- **Separate workflow files** — See [ADR 003](../docs/adr/003-separate-workflow-files.md)

## For Template Users

1. Update [CODEOWNERS](CODEOWNERS) with your team
2. Update [FUNDING.yml](FUNDING.yml) or remove it
3. Review and customize workflow triggers
4. Update issue/PR templates for your project
