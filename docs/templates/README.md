# Templates

Reusable file templates that you can copy and adapt for your project.

---

## Security Policy Templates

| Template | Use When |
|----------|----------|
| [SECURITY_no_bounty.md](SECURITY_no_bounty.md) | Standard security policy without bug bounty (most projects) |
| [SECURITY_with_bounty.md](SECURITY_with_bounty.md) | Security policy that includes a bug bounty program |
| [BUG_BOUNTY.md](BUG_BOUNTY.md) | Standalone bug bounty policy (link from SECURITY.md) |

### How to Use

1. Choose the template that fits your needs
2. Copy it to the root of your repository as `SECURITY.md`
3. Update placeholders (project name, contact info, scope, etc.)

---

## Issue Templates

The `issue_templates/` directory contains GitHub issue template examples:

| Directory | Format |
|-----------|--------|
| `issue_forms/` | YAML-based issue forms (recommended) |
| `legacy_markdown/` | Markdown-based templates (older format) |

### How to Use

1. Copy templates to `.github/ISSUE_TEMPLATE/` in your repository
2. Customize the fields and labels for your project
3. See [GitHub's documentation](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository) for details

---

## After Copying

Once you've copied the templates you need, you can delete this `docs/templates/` directory to keep your repository clean.
