# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| Latest  | :white_check_mark: |
| < Latest | :x:               |

<!-- Update this table as you release new versions -->

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Do NOT open a public issue for security vulnerabilities.**

Instead, please report security vulnerabilities via one of the following methods:

1. **GitHub Security Advisories (Preferred)**
   Use [GitHub's private vulnerability reporting](https://github.com/JoJo275/simple-python-boilerplate/security/advisories/new) to submit a report directly.

   > ℹ️ *If you forked this repo, update the link above to point to your own repository.*

2. **Email**
   Contact the maintainers directly at: `security@example.com`

   <!-- TODO: Replace with your actual security contact email -->

3. **PGP Encrypted Email** (Optional)
   For sensitive communications, you may encrypt your report using our PGP key.

   <!-- TODO: Add your PGP key fingerprint here, e.g.:
   Key fingerprint: `XXXX XXXX XXXX XXXX XXXX  XXXX XXXX XXXX XXXX XXXX`
   Public key: https://keys.openpgp.org/search?q=security@example.com
   -->

### What to Include

Please provide as much information as possible:

- **Description** of the vulnerability
- **Steps to reproduce** or proof-of-concept
- **Affected versions**
- **Potential impact** (what could an attacker do?)
- **Suggested fix** (if you have one)

### Response Timeline

| Action | Timeframe |
|--------|----------|
| Acknowledgment of report | Within 72 hours |
| Initial assessment | Within 7 days |
| Resolution or mitigation | Varies by severity |
| Public disclosure | After fix is released |

### Disclosure Policy

- We will work with you to understand and resolve the issue quickly.
- We request that you give us reasonable time to address the vulnerability before public disclosure.
- We will credit reporters in the security advisory (unless you prefer to remain anonymous).

### Bug Bounty

We do not currently offer a bug bounty program. However, we deeply appreciate responsible disclosure and will acknowledge contributors in our [Acknowledgments](#acknowledgments) section.

> To set up a bug bounty program, see [docs/templates/SECURITY_with_bounty.md](docs/templates/SECURITY_with_bounty.md) and [docs/templates/BUG_BOUNTY.md](docs/templates/BUG_BOUNTY.md).

### Scope

This security policy applies to:

- The `simple-python-boilerplate` repository
- Official releases published to PyPI (if applicable)

### Out of Scope

The following are generally not considered security vulnerabilities:

- Issues in dependencies (please report to the upstream project)
- Issues requiring physical access to a user's device
- Social engineering attacks
- Denial of service attacks that require significant resources

## Security Best Practices

When using this project:

1. **Keep dependencies updated** – Run `pip list --outdated` regularly
2. **Use virtual environments** – Isolate project dependencies
3. **Review code before running** – Especially from untrusted sources
4. **Enable Dependabot** – For automated security updates on your fork

## Acknowledgments

We thank the following individuals for responsibly disclosing security issues:

<!-- Add names/handles here as vulnerabilities are reported and fixed -->

*No security vulnerabilities have been reported yet.*
