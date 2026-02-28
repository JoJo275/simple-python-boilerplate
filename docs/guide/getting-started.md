# Getting Started

<!-- TODO (template users): Update package names, module paths, and
     installation commands to match your actual project. Remove the
     Read the Docs section if you only use GitHub Pages. -->

This guide covers installing the project, working with the documentation
locally, and understanding how links behave across different viewing contexts.

## Prerequisites

- Python 3.11 or later
- [Hatch](https://hatch.pypa.io/) (recommended) or plain pip

## Installation

### With Hatch (recommended)

Hatch manages environments automatically — no manual install step needed. Just
run any `hatch run docs:*` command and the environment is created on first use.

```bash
hatch shell          # enter the default dev environment
hatch run docs:serve # or jump straight to a docs command
```

### With pip (editable install + docs dependencies)

```bash
python -m pip install -e ".[docs]"
```

### With Taskfile shortcuts

If you have [Task](https://taskfile.dev/) installed, the Taskfile wraps
common commands:

```bash
task docs:serve   # hatch run docs:serve
task docs:build   # hatch run docs:build
```

## Serving docs locally

=== "Taskfile"

    ```bash
    task docs:serve
    ```

=== "Hatch"

    ```bash
    hatch run docs:serve
    ```

=== "pip"

    ```bash
    mkdocs serve
    ```

Open <http://127.0.0.1:8000> in your browser. Changes to Markdown files are
picked up automatically via live-reload.

## Building docs

=== "Taskfile"

    ```bash
    task docs:build
    ```

=== "Hatch"

    ```bash
    hatch run docs:build
    ```

=== "pip"

    ```bash
    mkdocs build --strict
    ```

The `--strict` flag treats warnings as errors, which is the same mode used by
the CI build.

## How Links Work

Documentation files in this project use **relative Markdown links** to
reference files across the repository — both within `docs/` and outside it
(e.g. `../../pyproject.toml`, `../scripts/clean.py`). This creates a
challenge because the same links need to work in two different contexts:

| Context                      | How links resolve                                                    |
| :--------------------------- | :------------------------------------------------------------------- |
| **Browsing on GitHub**       | GitHub resolves relative paths natively — all links just work        |
| **Deployed MkDocs site**     | MkDocs can only resolve links within `docs/` — external links break |
| **Local `mkdocs serve`**     | Same as deployed site — limited to `docs/`                          |

### The `repo_links.py` Hook

The [`repo_links.py`](../../mkdocs-hooks/repo_links.py) MkDocs build hook
solves this automatically. During `mkdocs build` or `mkdocs serve`, it
intercepts every Markdown link that points outside `docs/` and rewrites it
to an absolute GitHub URL (e.g. `https://github.com/OWNER/REPO/blob/main/pyproject.toml`).

This means:

- **Authors write natural relative links** — no need to think about
  deployment
- **Links work on GitHub** — relative paths resolve natively
- **Links work on the deployed site** — the hook rewrites them at build time
- **No source files are modified** — the rewrite happens in memory only

The hook reads `repo_url` from `mkdocs.yml`. Template users only need to set
that value correctly. See [`mkdocs-hooks/README.md`](../../mkdocs-hooks/README.md)
for configuration options.

### Link Types at a Glance

| Link type                     | Example                                        | Where it works natively     | Hook needed? |
| :---------------------------- | :--------------------------------------------- | :-------------------------- | :----------- |
| Within-docs relative          | `[ADRs](../adr/README.md)`                     | GitHub + MkDocs             | No           |
| Repo-relative (outside docs)  | `[pyproject](../../pyproject.toml)`             | GitHub only                 | **Yes**      |
| Absolute URL                  | `[Python](https://python.org)`                  | Everywhere                  | No           |
| Fragment / anchor             | `[section](#my-heading)`                        | GitHub + MkDocs             | No           |
| Repo-relative with fragment   | `[config](../../pyproject.toml#L10)`            | GitHub only                 | **Yes**      |

## Read the Docs

This project is configured for [Read the Docs](https://readthedocs.org/) via
`.readthedocs.yaml`. RTD builds are triggered automatically on push and use
the project's built-in versioning (tags and branches) — no additional tooling
like `mike` or GitHub Pages is required.

## GitHub Pages

Docs are also deployed via GitHub Pages using the `docs-deploy.yml` workflow.
This triggers on push to `main` when docs-related files change. GitHub Pages
deployment is configured in `mkdocs.yml` and uses the
[`gh-deploy`](https://www.mkdocs.org/user-guide/deploying-your-docs/#github-pages)
action.

## Troubleshooting

!!! warning "API reference page is empty or errors"

    If the API reference page shows errors or is blank:

    1. **Confirm the package is importable.** The `mkdocstrings` plugin
       needs to import your code. Make sure you have installed the project
       in editable mode:

        ```bash
        python -m pip install -e ".[docs]"
        ```

    2. **Check that modules exist under `src/`.** The `mkdocstrings`
       handler is configured with `paths: [src]` in `mkdocs.yml`. API
       directives like `::: simple_python_boilerplate.engine` expect the
       module to be at `src/simple_python_boilerplate/engine.py`.

    3. **Avoid top-level side effects.** Modules rendered by `mkdocstrings`
       are imported at build time. Guard any executable code behind
       `if __name__ == "__main__":` to prevent unintended execution during
       the docs build.

!!! tip "Clearing stale build artifacts"

    If the site behaves unexpectedly after changes, delete the build output
    and rebuild:

    ```bash
    rm -rf site/
    mkdocs build --strict
    ```

    Or use Taskfile / Hatch:

    ```bash
    task clean          # removes site/ and caches
    hatch run docs:build --clean
    ```

!!! note "Broken links in the MkDocs build"

    If `mkdocs build` reports INFO warnings about links not found, check:

    1. **Links outside `docs/`** — these should be caught by the
       `repo_links.py` hook. Verify the hook is registered in `mkdocs.yml`
       under `hooks:`.
    2. **Links to directories** — MkDocs needs an explicit file target.
       Use `../adr/README.md` instead of `../adr/`.
    3. **Links to excluded files** — files in `exclude_docs` or not in
       the `nav` may not resolve.
