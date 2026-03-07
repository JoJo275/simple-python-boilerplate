# Security Policy

<!-- TODO (template users): Review this entire file and update it for your
     project. At minimum: replace the advisory URL, set a real email address,
     and update the scope section. -->

## Supported Versions

| Version  | Supported          |
| -------- | ------------------ |
| Latest   | :white_check_mark: |
| < Latest | :x:                |

<!-- TODO (template users): Update this table as you release new versions.
     If you support multiple release branches, list each one. Example:
     | 2.x   | :white_check_mark:  |
     | 1.x   | Security fixes only |
     | < 1.0 | :x:                 |
-->

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Do NOT open a public issue for security vulnerabilities.**

Instead, please report security vulnerabilities via one of the following methods:

1. **GitHub Security Advisories (Preferred)**
   Use [GitHub's private vulnerability reporting](https://github.com/JoJo275/simple-python-boilerplate/security/advisories/new) to submit a report directly.

   <!-- TODO (template users): Replace the advisory URL above with your own:
        https://github.com/YOURNAME/YOURREPO/security/advisories/new -->

   > ℹ️ _If you forked this repo, update the link above to point to your own repository._

2. **Email**
   Contact the maintainers directly at: `joseph26584@gmail.com`

   <!-- Security contact email last verified: 2026-03-03 -->

3. **PGP Encrypted Email** (Optional)
   For sensitive communications, you may encrypt your report using our PGP key.

   **What is PGP?** PGP (Pretty Good Privacy) is a public-key encryption
   system used to sign and encrypt data. In practice, most people use
   [GnuPG (GPG)](https://gnupg.org/) — the free, open-source implementation
   of the OpenPGP standard. You generate a key pair: a **public key** you
   share (so others can encrypt messages to you) and a **private key** you
   keep secret (to decrypt those messages). PGP is widely used for securing
   email, verifying software signatures, and signing git commits.

   > **Download:** [gnupg.org/download](https://gnupg.org/download/) —
   > On Windows, install [Gpg4win](https://gpg4win.org/) which bundles
   > GnuPG with the Kleopatra key manager GUI.

   **Why RSA 4096-bit?** RSA is one of the most widely supported key
   algorithms. A 4096-bit key length provides a large security margin
   against brute-force attacks and is recommended for long-lived keys
   (e.g., security contact keys that may stay in use for years). While
   3072-bit is currently considered secure, 4096-bit costs little extra
   and future-proofs the key.

   <!-- TODO (template users): Enable PGP for security reports by following
        the steps below. Once complete, uncomment the fingerprint/URL block
        at the bottom of this section.
   -->

   **How to set up PGP with RSA 4096-bit:**

   1. **Generate a key pair:**

      ```bash
      gpg --full-generate-key
      ```

      When prompted, select:
      - Key type: **(1) RSA and RSA**
      - Key size: **4096**
      - Expiration: choose an appropriate validity period (e.g., `2y` for 2 years, or `0` for no expiry)
      - Enter your name and the email address associated with this project
      - Set a strong passphrase when prompted

   2. **Get your key fingerprint:**

      ```bash
      gpg --fingerprint YOUR_EMAIL
      ```

      The fingerprint is the 40-character hex string (e.g.,
      `ABCD 1234 EFGH 5678 ...`). Copy this — you'll need it below.

   3. **Publish to a keyserver** (so reporters can find your key):

      ```bash
      gpg --keyserver keys.openpgp.org --send-keys YOUR_FINGERPRINT
      ```

   4. **Export the public key and commit it to the repo root:**

      ```bash
      # Export the ASCII-armored public key
      gpg --armor --export YOUR_EMAIL > pgp-key.asc

      # Stage and commit the key file
      git add pgp-key.asc
      git commit -m "chore: add PGP public key for security reports"
      ```

      <!-- TODO (template users): After committing pgp-key.asc, consider
           adding a note in your README or CONTRIBUTING.md pointing to it
           so reporters know where to find the key. -->

      This makes your public key easily discoverable by anyone cloning the
      repo. Alternatively, you can host it elsewhere and link to it.

   5. **Uncomment the block below** and fill in your fingerprint + URL:

   <!--
   Key fingerprint: `XXXX XXXX XXXX XXXX XXXX  XXXX XXXX XXXX XXXX XXXX`
   Public key: https://keys.openpgp.org/search?q=joseph26584@gmail.com
   -->

### What to Include

Please provide as much information as possible:

- **Description** of the vulnerability
- **Steps to reproduce** or proof-of-concept
- **Affected versions**
- **Potential impact** (what could an attacker do?)
- **Suggested fix** (if you have one)

### Response Timeline

| Action                   | Timeframe          |
| ------------------------ | ------------------ |
| Acknowledgment of report | Within 72 hours    |
| Initial assessment       | Within 7 days      |
| Resolution or mitigation | Varies by severity |
| Public disclosure        | After fix released |

### Disclosure Policy

- We will work with you to understand and resolve the issue quickly.
- We request that you give us reasonable time to address the vulnerability before public disclosure.
- We will credit reporters in the security advisory (unless you prefer to remain anonymous).

### Bug Bounty

We do not currently offer a bug bounty program. However, we deeply appreciate responsible disclosure and will acknowledge contributors in our [Acknowledgments](#acknowledgments) section.

> To set up a bug bounty program, see [docs/templates/SECURITY_with_bounty.md](docs/templates/SECURITY_with_bounty.md) and [docs/templates/BUG_BOUNTY.md](docs/templates/BUG_BOUNTY.md).

### Scope

<!-- TODO (template users): Replace the repository name and update which
     artifacts are covered (e.g., container images, PyPI packages, API). -->

This security policy applies to:

- The `simple-python-boilerplate` repository
- Official releases published to PyPI (if applicable)
- Container images built from this repository (if applicable)

### Out of Scope

The following are generally not considered security vulnerabilities:

- Issues in dependencies (please report to the upstream project)
- Issues requiring physical access to a user's device
- Social engineering attacks
- Denial of service attacks that require significant resources
- Vulnerabilities in development-only dependencies that don't ship in releases

## Automated Security Tooling

This project includes multiple layers of automated security scanning.
All CI workflows are SHA-pinned to prevent supply-chain attacks
([ADR 004](docs/adr/004-pin-action-shas.md)).

| Tool                                                                         | What it does                           | When it runs                                     |
| ---------------------------------------------------------------------------- | -------------------------------------- | ------------------------------------------------ |
| **[Bandit](https://bandit.readthedocs.io/)**                                 | Python static security analysis        | Every PR (`bandit.yml`) + pre-commit hook        |
| **[pip-audit](https://github.com/pypa/pip-audit)**                           | Checks dependencies for known CVEs     | Pre-push hook + nightly (`nightly-security.yml`) |
| **[CodeQL](https://codeql.github.com/)**                                     | Semantic code analysis (GitHub)        | Every PR + weekly (`security-codeql.yml`)        |
| **[Trivy](https://trivy.dev/)**                                              | Container image vulnerability scan     | On container builds (`container-scan.yml`)       |
| **[Gitleaks](https://gitleaks.io/)**                                         | Detects hardcoded secrets              | Pre-push hook                                    |
| **[Dependency Review](https://github.com/actions/dependency-review-action)** | Blocks PRs introducing vulnerable deps | Every PR (`dependency-review.yml`)               |
| **[OpenSSF Scorecard](https://scorecard.dev/)**                              | Supply-chain security posture          | Scheduled (`scorecard.yml`)                      |
| **[Dependabot](https://docs.github.com/en/code-security/dependabot)**        | Automated dependency update PRs        | Daily (`.github/dependabot.yml`)                 |
| **[SBOM](https://cyclonedx.org/)**                                           | Software Bill of Materials generation  | On release (`sbom.yml`)                          |

> See [docs/workflows.md](docs/workflows.md) for the full workflow inventory
> and [docs/design/tool-decisions.md](docs/design/tool-decisions.md) for why
> these tools were chosen.

## Security Best Practices

When using or contributing to this project:

1. **Use Hatch for environments** — Run `hatch shell` or `hatch run <cmd>` instead of global pip installs. Never install packages outside a virtual environment.
2. **Keep dependencies updated** — Run `task deps:outdated` or `task deps:versions` to check. Dependabot handles this automatically for the GitHub repo.
3. **Run security checks locally** — `task security` (bandit) and `task pre-commit:run` catch issues before they reach CI.
4. **Review code before running** — Especially scripts from untrusted sources.
5. **Don't commit secrets** — Gitleaks runs on pre-push, but avoid putting secrets in code in the first place. Use environment variables or GitHub Secrets.
6. **Keep GitHub Actions pinned** — Use `task actions:versions` to audit and `task actions:upgrade` to update SHA pins.
7. **Review Dependabot PRs** — Don't blindly merge. Check changelogs for breaking changes.

## Acknowledgments

We thank the following individuals for responsibly disclosing security issues:

<!-- Add names/handles here as vulnerabilities are reported and fixed.
     Format: - **@handle** — Brief description of the issue (YYYY-MM) -->

_No security vulnerabilities have been reported yet. Be the first!_
