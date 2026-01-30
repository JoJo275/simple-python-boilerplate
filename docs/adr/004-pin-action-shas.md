# ADR 004: Pin GitHub Actions to commit SHAs

## Status

Accepted

## Context

GitHub Actions can be referenced in three ways:

```yaml
# By branch/tag (mutable)
uses: actions/checkout@v4
uses: actions/checkout@main

# By full commit SHA (immutable)
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
```

Using mutable references (tags/branches) is convenient but poses security risks:

- **Tag hijacking** — Attacker compromises action repo and moves tag to malicious commit
- **Supply chain attacks** — Malicious code injected into trusted action
- **Unpredictable behavior** — Tag contents can change without notice

GitHub's security hardening guide recommends pinning to full commit SHAs.

## Decision

Pin all third-party GitHub Actions to full commit SHAs with version comments:

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
- uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5.6.0
```

## Consequences

### Positive

- **Immutable** — SHA cannot be changed; guarantees exact code runs
- **Supply chain security** — Protected against tag hijacking attacks
- **Reproducible** — Same SHA always runs same code
- **Audit trail** — Clear record of exact versions used

### Negative

- **Manual updates** — Must manually update SHAs when new versions release
- **Less readable** — SHAs are not human-friendly (mitigated by version comments)
- **Dependabot friction** — Dependabot updates SHAs but may lag behind

### Mitigations

- Add version comment after SHA for readability
- Use Dependabot to receive update PRs
- Periodically review and update action versions

## References

- [GitHub: Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions)
- [Step Security: Action Hardening](https://www.stepsecurity.io/)
