# Bug Bounty Program

<!-- 
This is a standalone bug bounty policy document.
Include this in your SECURITY.md or link to it separately.
-->

## Overview

We offer rewards for responsibly disclosed security vulnerabilities in [PROJECT NAME]. This program encourages security researchers to help us identify and fix vulnerabilities before they can be exploited.

## Scope

### In Scope

The following are eligible for rewards:

- **Primary repository:** `https://github.com/OWNER/REPO`
- **Official releases:** Packages published to PyPI under `[package-name]`
- **Documentation site:** `https://docs.example.com` (if applicable)

### Vulnerability Types

| Severity | Examples | Reward Range |
|----------|----------|--------------|
| **Critical** | Remote code execution, authentication bypass, data breach | $500 – $2,000 |
| **High** | Privilege escalation, significant data exposure, injection attacks | $200 – $500 |
| **Medium** | Cross-site scripting (XSS), CSRF, information disclosure | $50 – $200 |
| **Low** | Minor information leaks, theoretical attacks | $0 – $50 (swag/recognition) |

> **Note:** Reward amounts are guidelines. Final amounts are determined based on impact, exploitability, and report quality.

### Out of Scope

The following are **not eligible** for rewards:

- Vulnerabilities in third-party dependencies (report to upstream)
- Issues requiring physical access to a user's device
- Social engineering attacks (phishing, etc.)
- Denial of service (DoS/DDoS) attacks
- Issues in non-production environments (staging, dev)
- Previously reported vulnerabilities
- Vulnerabilities disclosed publicly before we can address them
- Automated scanner output without proof of exploitability

---

## Rules of Engagement

To qualify for a reward, you must:

1. **Report privately** — Do not disclose publicly until we've released a fix
2. **Provide details** — Include steps to reproduce, impact assessment, and PoC
3. **Act in good faith** — Do not access, modify, or delete user data
4. **Wait for authorization** — Do not test against production without approval
5. **One report per issue** — Do not submit duplicates or variants of the same issue

### Safe Harbor

We will not pursue legal action against researchers who:

- Follow the rules outlined in this policy
- Act in good faith to avoid privacy violations and service disruption
- Report vulnerabilities promptly and work with us on remediation

---

## How to Report

1. **Preferred:** [GitHub Security Advisory](https://github.com/OWNER/REPO/security/advisories/new)
2. **Email:** `security@example.com`
3. **PGP Encrypted:** Key fingerprint `XXXX XXXX XXXX XXXX XXXX`

### What to Include

- **Summary:** Brief description of the vulnerability
- **Severity:** Your assessment (Critical/High/Medium/Low)
- **Steps to Reproduce:** Detailed instructions or proof-of-concept
- **Impact:** What could an attacker achieve?
- **Affected Versions:** Which versions are vulnerable?
- **Suggested Fix:** Optional but appreciated

---

## Response Timeline

| Action | Timeframe |
|--------|-----------|
| Acknowledgment | Within 72 hours |
| Initial triage | Within 7 days |
| Status update | Every 7 days during investigation |
| Fix deployed | Varies by severity (target: 30–90 days) |
| Reward issued | Within 30 days of fix deployment |

---

## Reward Payment

Rewards are paid via:

- **PayPal** (preferred)
- **GitHub Sponsors** (one-time sponsorship)
- **Cryptocurrency** (BTC, ETH — upon request)
- **Donation to charity** (in your name)

### Requirements

- You must have a PayPal account or alternative payment method
- You must not be on any US sanctions list
- You must be at least 18 years old (or have guardian consent)
- Rewards are subject to applicable tax laws

---

## Recognition

With your permission, we will:

- Credit you in the security advisory
- Add your name to our [Security Hall of Fame](#hall-of-fame)
- Provide a letter of acknowledgment (upon request)

If you prefer to remain anonymous, we will respect that.

---

## Hall of Fame

We thank the following researchers for their contributions:

<!-- Add researchers here as vulnerabilities are reported and fixed -->

| Researcher | Vulnerability | Date |
|------------|---------------|------|
| *Be the first!* | — | — |

---

## Changes to This Policy

We may modify this bug bounty policy at any time. Changes will be posted to this document with an updated revision date.

**Last updated:** January 2026

---

## Questions?

Contact us at `security@example.com` for any questions about this program.
