# Labels

This boilerplate includes **label specs** (machine-readable) plus a human-readable catalog.

Why this exists:
- Labels are **repo metadata** (they do **not** copy when you create a new repo from a template).
- A consistent label set makes triage and contribution easier.

**After creating your repo from a template, run the apply script to add labels.**

---

## Rules of Thumb

To avoid "label soup," please follow these guidelines:

- **1× `status:`** — one at a time, update as issue progresses
- **1× `priority:`** — optional until triaged, then pick one
- **1× `type:`** — categorize the nature of work
- **1+ `area:`** — can apply multiple if issue spans areas
- **Optional:** `triage:`, `release:`, `contrib:`, `meta:` as needed

---

## Label Categories and Usage Guide

Labels are organized by **prefix** to make them easy to scan and filter. Here's how to use them.

> **Note:** `status:`, `priority:`, and `type:` labels are in both sets. The extended set adds more granular options plus `area:`, `triage:`, `release:`, `contrib:`, and `meta:` labels.

### Status Labels (`status:`)

Track where an issue/PR is in the workflow. **Apply one at a time** as the issue progresses.

| Label | When to Apply |
|-------|---------------|
| `status: needs-triage` | Default for new issues; not yet reviewed |
| `status: needs-info` | Waiting for reporter to provide details |
| `status: needs-repro` | Need a minimal reproduction case |
| `status: confirmed` | Issue validated and ready to work on |
| `status: in-progress` | Someone is actively working on it |
| `status: blocked` | Can't proceed due to external dependency |
| `status: ready-for-review` | PR ready for maintainer review |
| `status: waiting-on-maintainer` | Ball is in maintainer's court |
| `status: waiting-on-reporter` | Ball is in reporter's court |

**Typical flow:** `needs-triage` → `confirmed` → `in-progress` → `ready-for-review` → closed

### Priority Labels (`priority:`)

Indicate urgency. **Apply exactly one** to triaged issues.

| Label | Meaning | Response Time |
|-------|---------|---------------|
| `priority: p0-critical` | Crash, data loss, security, outage | Drop everything |
| `priority: p1-high` | Important bug or blocking feature | This sprint/week |
| `priority: p2-medium` | Normal priority work | Next few sprints |
| `priority: p3-low` | Nice-to-have, minor improvement | When time permits |
| `priority: backlog` | Accepted but not scheduled | Someday/maybe |

### Area Labels (`area:`)

Identify which part of the codebase is affected. **Can apply multiple.**

| Label | Scope |
|-------|-------|
| `area: cli` | Command-line interface |
| `area: api` | Public API surface |
| `area: docs` | Documentation |
| `area: tests` | Test suite |
| `area: ci` | CI/CD pipelines |
| `area: config` | Configuration/environment |
| `area: packaging` | pyproject.toml, build, publishing |
| `area: windows/linux/macos` | Platform-specific issues |

### Type Labels (`type:`)

Categorize the nature of the work. **Apply one.**

| Label | Use For |
|-------|---------|
| `type: performance` | Slowdowns, regressions |
| `type: refactor` | Internal cleanup, no user-facing change |
| `type: security` | Security-related (non-sensitive) |
| `type: breaking-change` | Backward-incompatible changes |
| `type: chore` | Maintenance, housekeeping |
| `type: build` | Build tooling changes |
| `type: test` | Test-only changes |

### Triage Labels (`triage:`)

Used during triage to track what's needed before work can begin.

| Label | Meaning |
|-------|---------|
| `triage: accepted` | Maintainers agree this should be done |
| `triage: needs-decision` | Blocked on maintainer decision |
| `triage: needs-design` | Needs design discussion first |
| `triage: needs-docs` | Must update docs before shipping |
| `triage: needs-tests` | Must add tests before merge |
| `triage: needs-benchmark` | Need performance numbers |

### Release Labels (`release:`)

Track release-related concerns.

| Label | Meaning |
|-------|---------|
| `release: blocker` | Must fix before release |
| `release: candidate` | Include in release notes |
| `release: backport-needed` | Should backport to stable |
| `release: backport-done` | Backport completed |

### Contributor Labels (`contrib:`)

Help match contributors with issues.

| Label | Meaning |
|-------|---------|
| `contrib: mentor-available` | Maintainer willing to guide |
| `contrib: needs-volunteer` | Seeking help; maintainers busy |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |

### Meta Labels (`meta:`)

Administrative/process labels.

| Label | Meaning |
|-------|---------|
| `meta: duplicate-candidate` | Might be a duplicate |
| `meta: needs-scope` | Requirements unclear |
| `meta: stale` | Inactive; may auto-close |

---

## Color Coding

Colors are intentionally shared to create visual groupings:

| Color | Meaning |
|-------|---------|
| 🔴 Red (`#b60205`, `#d73a4a`) | Critical, blocking, bugs |
| 🟠 Orange (`#d93f0b`) | High priority, needs attention |
| 🟡 Yellow (`#fbca04`) | Needs triage/decision, medium priority |
| 🟢 Green (`#0e8a16`) | Confirmed, accepted, done |
| 🔵 Blue (`#0075ca`, `#0052cc`) | Documentation, in-progress |
| 🟣 Purple (`#d4c5f9`, `#5319e7`) | Waiting, design, refactor |
| ⚪ Gray (`#cfd3d7`, `#eeeeee`) | Duplicate, stale, chore |

---

## Apply labels to your repo

Prereqs:
- Install and authenticate GitHub CLI: `gh auth login`
- Run from the root of your repository

### Using the Python script (recommended)

Apply **baseline** (recommended for most repos):
```bash
python scripts/apply_labels.py --set baseline
```

Apply **extended** (large projects / heavier triage):
```bash
python scripts/apply_labels.py --set extended
```

Target a specific repo:
```bash
python scripts/apply_labels.py --set baseline --repo OWNER/REPO
```

Dry run (preview without making changes):
```bash
python scripts/apply_labels.py --set extended --dry-run
```

### Using the shell script (alternative)

For macOS/Linux/WSL users who prefer shell scripts:

```bash
./scripts/apply-labels.sh baseline              # Apply baseline
./scripts/apply-labels.sh extended              # Apply extended
./scripts/apply-labels.sh baseline OWNER/REPO   # Target specific repo
./scripts/apply-labels.sh baseline --dry-run    # Dry run
```

## Baseline set

GitHub's default labels plus useful extras for basic triage and prioritization. Good for small-to-medium projects. **(17 labels = 9 defaults + 8 extras)**

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
| `status: blocked` | Blocked by dependency/decision/external factor | `#b60205` |
| `priority: p1-high` | Important; should be addressed soon | `#d93f0b` |
| `priority: p2-medium` | Normal priority | `#fbca04` |
| `priority: p3-low` | Nice-to-have | `#c2e0c6` |

## Extended set

Includes everything in baseline plus more granular `status:`, `priority:`, `area:`, `type:`, `triage:`, `release:`, `contrib:`, and `meta:` labels for larger projects with heavier triage needs. **(62 labels = 17 baseline + 45 extras)**

**Notes:**
- Includes GitHub's default labels (`help wanted`, `good first issue`, etc.) with same names/colors
- The script uses upsert logic—existing labels are updated, not duplicated

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
