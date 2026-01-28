# Security Policy

<!-- 
Example only. Not active for this repository.
For a real program, publish this in your own repo and link it from SECURITY.md.
-->

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :white_check_mark: (security fixes only) |
| < 1.0   | :x:                |

<!-- Update this table as you release new versions -->

## Bug Bounty Program

**We offer rewards for responsibly disclosed security vulnerabilities.**

| Severity | Reward Range |
|----------|--------------|
| Critical | $500 – $2,000 |
| High | $200 – $500 |
| Medium | $50 – $200 |
| Low | Recognition + swag |

For full details, see our [Bug Bounty Policy](docs/examples/BUG_BOUNTY.md).

---

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Do NOT open a public issue for security vulnerabilities.**

Instead, please report security vulnerabilities via one of the following methods:

1. **GitHub Security Advisories (Preferred)**  
   Use [GitHub's private vulnerability reporting](https://github.com/OWNER/REPO/security/advisories/new) to submit a report directly.

   > ℹ️ *If you forked this repo, update the link above to point to your own repository.*

2. **Email**  
   Contact the maintainers directly at: `security@example.com`

3. **PGP Encrypted Email** (Optional)  
   For sensitive communications, you may encrypt your report using our PGP key.
   
   Key fingerprint: `XXXX XXXX XXXX XXXX XXXX  XXXX XXXX XXXX XXXX XXXX`  
   Public key: [keys.openpgp.org](https://keys.openpgp.org/search?q=security@example.com)

### What to Include

Please provide as much information as possible:

- **Description** of the vulnerability
- **Steps to reproduce** or proof-of-concept
- **Affected versions**
- **Potential impact** (what could an attacker do?)
- **Suggested fix** (if you have one)
- **Your reward eligibility** (for bug bounty consideration)

---

## Response Timeline

| Action | Timeframe |
|--------|-----------|
| Acknowledgment of report | Within 72 hours |
| Initial assessment | Within 7 days |
| Status updates | Every 7 days |
| Resolution or mitigation | Varies by severity |
| Reward payment | Within 30 days of fix |
| Public disclosure | After fix is released |

---

## Disclosure Policy

- We will work with you to understand and resolve the issue quickly.
- We request that you give us reasonable time to address the vulnerability before public disclosure (typically 90 days).
- We will credit reporters in the security advisory (unless you prefer to remain anonymous).
- Coordinated disclosure will not affect your bounty eligibility.

---

## Safe Harbor

We support responsible security research. We will not pursue legal action against researchers who:

- Follow this security policy
- Act in good faith to avoid privacy violations and service disruption
- Do not access, modify, or delete data belonging to others
- Report vulnerabilities promptly

---

## Scope

### In Scope

This security policy applies to:

- The `[project-name]` repository
- Official releases published to PyPI
- Documentation site at `https://docs.example.com`

### Out of Scope

The following are generally not considered security vulnerabilities:

- Issues in dependencies (please report to the upstream project)
- Issues requiring physical access to a user's device
- Social engineering attacks
- Denial of service attacks that require significant resources
- Issues in staging/development environments
- Theoretical vulnerabilities without proof of exploitability

---

## Security Best Practices

When using this project:

1. **Keep dependencies updated** – Run `pip list --outdated` regularly
2. **Use virtual environments** – Isolate project dependencies
3. **Review code before running** – Especially from untrusted sources
4. **Enable Dependabot** – For automated security updates on your fork
5. **Pin dependencies** – Use `pip freeze` or `pip-tools` for reproducible builds

---

## Acknowledgments

We thank the following individuals for responsibly disclosing security issues:

<!-- Add names/handles here as vulnerabilities are reported and fixed -->

| Researcher | Vulnerability | Severity | Date |
|------------|---------------|----------|------|
| *Be the first!* | — | — | — |

---

## Contact

- **Security issues:** `security@example.com`
- **General questions:** Open a [Discussion](https://github.com/OWNER/REPO/discussions)
- **Bug bounty questions:** `security@example.com` with subject "Bug Bounty Question"

---

**Last updated:** January 2026
