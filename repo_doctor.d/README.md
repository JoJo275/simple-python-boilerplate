# repo_doctor.d/ — Optional Profile Rules

Extra rule sets for `scripts/repo_doctor.py`. These are **not** loaded by
default — activate them on the CLI or in `.repo-doctor.toml`.

## Available Profiles

| Profile     | File             | What it checks                                          |
| ----------- | ---------------- | ------------------------------------------------------- |
| `python`    | `python.toml`    | Deeper packaging, typing, linting, coverage, bandit     |
| `docs`      | `docs.toml`      | MkDocs structure, ADRs, dev guides, standard files      |
| `db`        | `db.toml`        | Schema, migrations, seeds, bootstrap scripts            |
| `ci`        | `ci.toml`        | Workflow hardening, pinning, Dependabot ecosystems      |
| `container` | `container.toml` | Containerfile hygiene, ignore files, multi-stage builds |
| `security`  | `security.toml`  | Security policy, bandit config, secret scanning, audits |

## Usage

**CLI (one-off):**

```bash
python scripts/repo_doctor.py --profile python --profile docs
python scripts/repo_doctor.py --profile all          # load every profile
python scripts/repo_doctor.py --profile db --include-info
```

**Config (persistent):** add to `.repo-doctor.toml`:

```toml
[doctor]
profiles = ["python", "docs"]
```

## Adding a New Profile

1. Create `repo_doctor.d/<name>.toml`.
2. Add `[[rule]]` entries using the same schema as `.repo-doctor.toml`.
3. Update the table above.
