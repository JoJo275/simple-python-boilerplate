# Issue Templates Archive

This directory stores issue templates that are **not active** in `.github/ISSUE_TEMPLATE/`.

## Active Templates

Only the essential templates live in `.github/ISSUE_TEMPLATE/`:

- `bug_report.yml` — Bug reports
- `feature_request.yml` — Feature requests
- `documentation.yml` — Documentation issues
- `config.yml` — Template chooser configuration

## Archived Templates

### `issue_forms/` — GitHub Issue Forms (YAML)

Additional structured templates (design proposals, performance reports, etc.).
To activate one, copy it to `.github/ISSUE_TEMPLATE/`.

### `legacy_markdown/` — Markdown Templates

Older `.md`-based templates. GitHub Issue Forms (`.yml`) are preferred because
they enforce required fields and provide structured input. These are kept for
reference or for repos that prefer the free-form markdown style.

## How to Activate a Template

```bash
cp docs/templates/issue_templates/issue_forms/design_proposal.yml .github/ISSUE_TEMPLATE/
```

Or just drag and drop the file in your code editor.
