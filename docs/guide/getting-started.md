# Getting Started

This guide covers installing the project and working with the documentation
locally.

## Prerequisites

- Python 3.11 or later
- [Hatch](https://hatch.pypa.io/) (recommended) or plain pip

## Installation

### With pip (editable install + docs dependencies)

```bash
python -m pip install -e ".[docs]"
```

### With Hatch

Hatch manages environments automatically — no manual install step needed. Just
run any `hatch run docs:*` command and the environment is created on first use.

## Serving docs locally

=== "pip"

    ```bash
    mkdocs serve
    ```

=== "Hatch"

    ```bash
    hatch run docs:serve
    ```

Open <http://127.0.0.1:8000> in your browser. Changes to Markdown files are
picked up automatically via live-reload.

## Building docs

=== "pip"

    ```bash
    mkdocs build --strict
    ```

=== "Hatch"

    ```bash
    hatch run docs:build
    ```

The `--strict` flag treats warnings as errors, which is the same mode used by
the CI/RTD build.

## Read the Docs

This project is configured for [Read the Docs](https://readthedocs.org/) via
`.readthedocs.yaml`. RTD builds are triggered automatically on push and use
the project's built-in versioning (tags and branches) — no additional tooling
like `mike` or GitHub Pages is required.

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

    Or let Hatch handle it:

    ```bash
    hatch run docs:build --clean
    ```
