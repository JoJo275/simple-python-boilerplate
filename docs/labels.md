# Labels

This boilerplate includes **label specs** (machine-readable) plus a human-readable catalog.

Why this exists:
- Labels are **repo metadata** (they do **not** copy when you create a new repo from a template).
- A consistent label set makes triage and contribution easier.

## Apply labels to your repo

Prereqs:
- Install and authenticate GitHub CLI: `gh auth login`
- Run from the root of your repository

Apply **baseline** (recommended for most repos):
```bash
./scripts/apply-labels.sh baseline
```

Apply **extended** (large projects / heavier triage):
```bash
./scripts/apply-labels.sh extended
```

Target a specific repo:
```bash
./scripts/apply-labels.sh baseline OWNER/REPO
```

Dry run:
```bash
./scripts/apply-labels.sh baseline --dry-run
```

## Baseline set

| Label | Description | Color |
|---|---|---|
| `bug` | Something isn't working | `#d73a4a` |
| `dependencies` | Pull requests that update a dependency file | `#0366d6` |
| `documentation` | Improvements or additions to documentation | `#0075ca` |
| `duplicate` | This issue or pull request already exists | `#cfd3d7` |
| `enhancement` | New feature or request | `#a2eeef` |
| `github_actions` | Pull requests that update GitHub Actions code | `#000000` |
| `good first issue` | Good for newcomers | `#7057ff` |
| `help wanted` | Extra attention is needed | `#008672` |
| `invalid` | This doesn't seem right | `#e4e669` |
| `question` | Further information is requested | `#d876e3` |
| `wontfix` | This will not be worked on | `#ffffff` |
| `status: needs-triage` | New issue; not yet reviewed/confirmed | `#fbca04` |
| `status: needs-info` | Reporter needs to provide missing details | `#fef2c0` |
| `status: needs-repro` | Needs a minimal reproduction case | `#f9d0c4` |
| `status: blocked` | Blocked by dependency/decision/external factor | `#b60205` |
| `priority: p0-critical` | Crash/data loss/security/major outage | `#b60205` |
| `priority: p1-high` | Important; should be addressed soon | `#d93f0b` |
| `priority: p2-medium` | Normal priority | `#fbca04` |
| `priority: p3-low` | Nice-to-have | `#c2e0c6` |
| `priority: backlog` | Accepted but not scheduled | `#bfdadc` |
| `area: cli` | Command-line interface | `#006b75` |
| `area: packaging` | pyproject/build/publishing/installers | `#d4c5f9` |
| `area: docs` | Docs content and examples | `#0075ca` |
| `area: tests` | Test suite, fixtures, harness | `#c5def5` |
| `area: ci` | CI pipelines and automation | `#bfd4f2` |

## Extended set

Notes:
- The extended set **does not** add duplicates of GitHub’s `help wanted` and `good first issue` labels.

| Label | Description | Color |
|---|---|---|
| `bug` | Something isn't working | `#d73a4a` |
| `dependencies` | Pull requests that update a dependency file | `#0366d6` |
| `documentation` | Improvements or additions to documentation | `#0075ca` |
| `duplicate` | This issue or pull request already exists | `#cfd3d7` |
| `enhancement` | New feature or request | `#a2eeef` |
| `github_actions` | Pull requests that update GitHub Actions code | `#000000` |
| `good first issue` | Good for newcomers | `#7057ff` |
| `help wanted` | Extra attention is needed | `#008672` |
| `invalid` | This doesn't seem right | `#e4e669` |
| `question` | Further information is requested | `#d876e3` |
| `wontfix` | This will not be worked on | `#ffffff` |
| `status: needs-triage` | New issue; not yet reviewed/confirmed | `#fbca04` |
| `status: needs-info` | Reporter needs to provide missing details | `#fef2c0` |
| `status: needs-repro` | Needs a minimal reproduction case | `#f9d0c4` |
| `status: blocked` | Blocked by dependency/decision/external factor | `#b60205` |
| `priority: p0-critical` | Crash/data loss/security/major outage | `#b60205` |
| `priority: p1-high` | Important; should be addressed soon | `#d93f0b` |
| `priority: p2-medium` | Normal priority | `#fbca04` |
| `priority: p3-low` | Nice-to-have | `#c2e0c6` |
| `priority: backlog` | Accepted but not scheduled | `#bfdadc` |
| `area: cli` | Command-line interface | `#006b75` |
| `area: packaging` | pyproject/build/publishing/installers | `#d4c5f9` |
| `area: docs` | Docs content and examples | `#0075ca` |
| `area: tests` | Test suite, fixtures, harness | `#c5def5` |
| `area: ci` | CI pipelines and automation | `#bfd4f2` |
| `status: confirmed` | Triaged and confirmed valid | `#0e8a16` |
| `status: in-progress` | Work has started | `#0052cc` |
| `status: ready-for-review` | PR/solution ready for review | `#1d76db` |
| `status: waiting-on-maintainer` | Waiting on maintainer action/decision | `#d4c5f9` |
| `status: waiting-on-reporter` | Waiting on reporter response | `#c5def5` |
| `status: wont-merge` | Decision made not to accept a PR/approach | `#000000` |
| `type: performance` | Performance issue (slowdown/regression) | `#ffcc00` |
| `type: refactor` | Internal cleanup; no user-facing change | `#5319e7` |
| `type: chore` | Maintenance task (non-feature, non-bug) | `#ededed` |
| `type: build` | Build tooling / packaging changes | `#cfd3d7` |
| `type: test` | Test additions/fixes only | `#c5def5` |
| `type: security` | Security-related work (non-sensitive discussion) | `#ee0701` |
| `type: breaking-change` | Backward incompatible change | `#000000` |
| `area: api` | Public API surface | `#1d76db` |
| `area: logging` | Logging/telemetry | `#0e8a16` |
| `area: config` | Configuration files/env behavior | `#0052cc` |
| `area: ux` | User experience and ergonomics | `#a2eeef` |
| `area: performance` | Subsystem performance (hot paths) | `#ffcc00` |
| `area: compatibility` | OS/Python-version compatibility | `#f9d0c4` |
| `area: windows` | Windows-specific | `#1d76db` |
| `area: linux` | Linux-specific | `#0e8a16` |
| `area: macos` | macOS-specific | `#5319e7` |
| `triage: accepted` | Maintainers agree this should be addressed | `#0e8a16` |
| `triage: needs-design` | Needs design discussion before implementation | `#d4c5f9` |
| `triage: needs-decision` | Blocked pending a maintainer decision | `#fbca04` |
| `triage: needs-docs` | Requires docs update to ship | `#0075ca` |
| `triage: needs-tests` | Requires tests before merge/close | `#c5def5` |
| `triage: needs-benchmark` | Needs benchmark numbers to evaluate | `#ffcc00` |
| `release: blocker` | Must be fixed before next release | `#b60205` |
| `release: candidate` | Candidate item for next release notes | `#0052cc` |
| `release: backport-needed` | Should be backported to a stable branch | `#d93f0b` |
| `release: backport-done` | Backport completed | `#0e8a16` |
| `contrib: mentor-available` | Maintainer willing to guide a contributor | `#a2eeef` |
| `contrib: needs-volunteer` | Seeking contributor help; no maintainer bandwidth | `#bfdadc` |
| `meta: duplicate-candidate` | Might be duplicate; needs confirmation | `#cfd3d7` |
| `meta: needs-scope` | Requirements unclear; needs scoping | `#fbca04` |
| `meta: stale` | Inactive; may be closed if no response | `#eeeeee` |

## File layout

- `labels/baseline.json` — baseline label spec
- `labels/extended.json` — extended label spec
- `scripts/apply_labels.py` — upsert logic (create/update labels)
- `scripts/apply-labels.sh` — convenience wrapper
