#!/usr/bin/env python3
"""Interactive project customization — replace boilerplate placeholders.

Replaces template placeholders with your project's values, renames the
package directory, strips optional directories, and optionally swaps the
license.  A lightweight alternative to template engines like Copier or
Cookiecutter — runs once after cloning with no external dependencies.

See ADR 014 for the design rationale behind manual customization.

Usage::

    python scripts/customize.py
    python scripts/customize.py --dry-run
    python scripts/customize.py --non-interactive \\
        --project-name my-project --author "Jane Doe" \\
        --github-user janedoe
"""

from __future__ import annotations

import argparse
import datetime
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

# Original placeholders baked into the template
TEMPLATE_PROJECT_NAME = "simple-python-boilerplate"
TEMPLATE_PACKAGE_NAME = "simple_python_boilerplate"
TEMPLATE_GITHUB_USER = "JoJo275"
TEMPLATE_GITHUB_URL_PLACEHOLDER = "YOURNAME/YOURREPO"
TEMPLATE_AUTHOR = "Joseph"
TEMPLATE_DESCRIPTION = "Simple Python boilerplate using src/ layout"
TEMPLATE_CLI_PREFIX = "spb"

# Directories to skip when scanning files
SKIP_DIRS: set[str] = {
    ".git",
    ".venv",
    ".venv-1",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "site",
    ".egg-info",
}

# File extensions to process (text-based files only)
TEXT_EXTENSIONS: set[str] = {
    ".py",
    ".toml",
    ".yml",
    ".yaml",
    ".md",
    ".txt",
    ".cfg",
    ".ini",
    ".json",
    ".sh",
    ".ps1",
    ".bat",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".rst",
    ".in",
}

# Files to never modify (relative to ROOT)
SKIP_FILES: set[Path] = {
    Path("scripts") / "customize.py",
}

# Optional directories / files that can be stripped
STRIPPABLE: dict[str, dict[str, object]] = {
    "db": {
        "label": "Database directory (schema, migrations, seeds, queries)",
        "paths": [
            "db/",
            "scripts/sql/",
            f"src/{TEMPLATE_PACKAGE_NAME}/sql/",
        ],
    },
    "experiments": {
        "label": "Experiments / scratch code directory",
        "paths": ["experiments/"],
    },
    "var": {
        "label": "Local data / state directory (var/)",
        "paths": ["var/"],
    },
    "docs-templates": {
        "label": "Security-policy templates (docs/templates/)",
        "paths": ["docs/templates/"],
    },
    "container": {
        "label": "Container build files and scan workflows",
        "paths": [
            "Containerfile",
            ".github/workflows/container-build.yml",
            ".github/workflows/container-scan.yml",
        ],
    },
}

# ---------------------------------------------------------------------------
# License templates
# ---------------------------------------------------------------------------

MIT_LICENSE = """\
MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

BSD_3_LICENSE = """\
BSD 3-Clause License

Copyright (c) {year}, {author}

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

LICENSE_CHOICES: dict[str, dict[str, str | None]] = {
    "apache-2.0": {
        "name": "Apache License 2.0",
        "classifier": "License :: OSI Approved :: Apache Software License",
        "template": None,  # keep the existing LICENSE file
    },
    "mit": {
        "name": "MIT License",
        "classifier": "License :: OSI Approved :: MIT License",
        "template": MIT_LICENSE,
    },
    "bsd-3-clause": {
        "name": "BSD 3-Clause License",
        "classifier": "License :: OSI Approved :: BSD License",
        "template": BSD_3_LICENSE,
    },
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Config:
    """User-provided customization values collected via prompts or CLI."""

    project_name: str = ""
    package_name: str = ""
    author: str = ""
    github_user: str = ""
    description: str = ""
    cli_prefix: str = ""
    license_id: str = "apache-2.0"
    strip_dirs: list[str] = field(default_factory=list)
    dry_run: bool = False


@dataclass(frozen=True)
class Replacement:
    """A single text substitution to apply across the project."""

    old: str
    new: str
    description: str


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------


def _prompt(label: str, default: str = "") -> str:
    """Prompt the user for a text value, showing an optional default.

    Args:
        label: Prompt text.
        default: Value used when the user presses Enter.

    Returns:
        The user's input, or *default* if they pressed Enter.
    """
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"  {label}{suffix}: ").strip()
        if value:
            return value
        if default:
            return default
        print("    (required — please enter a value)")


def _prompt_yn(label: str, *, default: bool = True) -> bool:
    """Prompt for yes/no.

    Args:
        label: Prompt text.
        default: Value used when the user presses Enter.

    Returns:
        ``True`` for yes, ``False`` for no.
    """
    hint = "Y/n" if default else "y/N"
    value = input(f"  {label} [{hint}]: ").strip().lower()
    if not value:
        return default
    return value in ("y", "yes")


def _prompt_choice(label: str, choices: dict[str, str], default: str) -> str:
    """Prompt the user to pick one item from a numbered list.

    Args:
        label: Header text.
        choices: Mapping of key → display string.
        default: Key returned when the user presses Enter.

    Returns:
        The chosen key.
    """
    print(f"  {label}")
    keys = list(choices.keys())
    for i, key in enumerate(keys, 1):
        marker = " (default)" if key == default else ""
        print(f"    {i}. {choices[key]}{marker}")
    while True:
        raw = input(f"  Choice [1-{len(keys)}]: ").strip()
        if not raw:
            return default
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        except ValueError:
            if raw in keys:
                return raw
        print(f"    (enter a number 1-{len(keys)})")


def _prompt_multi(label: str, choices: dict[str, str]) -> list[str]:
    """Prompt the user to select zero or more items from a numbered list.

    Args:
        label: Header text.
        choices: Mapping of key → display string.

    Returns:
        List of selected keys (may be empty).
    """
    print(f"  {label}")
    keys = list(choices.keys())
    for i, key in enumerate(keys, 1):
        print(f"    {i}. {choices[key]}")
    print("    0. None of the above")
    raw = input("  Selection (comma-separated, e.g. 1,3): ").strip()
    if not raw or raw == "0":
        return []
    selected: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        try:
            idx = int(part) - 1
            if 0 <= idx < len(keys) and keys[idx] not in selected:
                selected.append(keys[idx])
        except ValueError:
            if part in keys and part not in selected:
                selected.append(part)
    return selected


# ---------------------------------------------------------------------------
# Interactive configuration
# ---------------------------------------------------------------------------


def _validate_project_name(name: str) -> str | None:
    """Return an error message if *name* is not a valid project slug."""
    if not re.match(r"^[a-z][a-z0-9]+(-[a-z0-9]+)*$", name):
        return (
            "Use lowercase letters, digits, and hyphens "
            "(e.g. my-cool-project). Must start with a letter."
        )
    return None


def gather_config_interactive() -> Config:
    """Run an interactive Q&A session and return a populated Config."""
    cfg = Config()

    print("\n=== Project Customization ===\n")
    print("Replace boilerplate placeholders with your project's values.")
    print("Press Enter to accept [defaults].\n")

    # --- Project identity ---------------------------------------------------
    print("── Project Identity ──")
    while True:
        cfg.project_name = _prompt("Project name (lowercase-hyphenated)")
        err = _validate_project_name(cfg.project_name)
        if err is None:
            break
        print(f"    {err}")

    cfg.package_name = _prompt(
        "Package name (underscored)",
        cfg.project_name.replace("-", "_"),
    )
    cfg.author = _prompt("Author name")
    cfg.github_user = _prompt("GitHub username or org")
    cfg.description = _prompt(
        "One-line description",
        f"{cfg.project_name} — a Python project",
    )

    # Derive CLI prefix from initials of hyphenated name
    parts = cfg.project_name.split("-")
    default_cli = (
        "".join(p[0] for p in parts if p) if len(parts) > 1 else cfg.project_name
    )
    cfg.cli_prefix = _prompt("CLI command prefix", default_cli)

    # --- License ------------------------------------------------------------
    print("\n── License ──")
    license_options = {k: str(v["name"]) for k, v in LICENSE_CHOICES.items()}
    cfg.license_id = _prompt_choice("Choose a license:", license_options, "apache-2.0")

    # --- Strip optional directories -----------------------------------------
    print("\n── Optional Directories ──")
    print("  The following directories are optional and can be removed:")
    strip_options = {k: str(v["label"]) for k, v in STRIPPABLE.items()}
    cfg.strip_dirs = _prompt_multi("Remove any of these?", strip_options)

    return cfg


# ---------------------------------------------------------------------------
# Replacement planning
# ---------------------------------------------------------------------------


def plan_replacements(cfg: Config) -> list[Replacement]:
    """Build an ordered list of text substitutions from the config.

    Ordering matters: more-specific patterns (e.g. ``YOURNAME/YOURREPO``)
    are applied before their substrings to avoid partial replacements.

    Args:
        cfg: Populated customization config.

    Returns:
        Ordered list of :class:`Replacement` instances.
    """
    reps: list[Replacement] = []
    github_slug = f"{cfg.github_user}/{cfg.project_name}"

    # 1. GitHub URL placeholder (most specific — contains '/')
    reps.append(
        Replacement(
            old=TEMPLATE_GITHUB_URL_PLACEHOLDER,
            new=github_slug,
            description=f"GitHub URL placeholder -> {github_slug}",
        )
    )

    # 2. Project name (hyphenated)
    if cfg.project_name != TEMPLATE_PROJECT_NAME:
        reps.append(
            Replacement(
                old=TEMPLATE_PROJECT_NAME,
                new=cfg.project_name,
                description=f"Project name -> {cfg.project_name}",
            )
        )

    # 3. Package name (underscored)
    if cfg.package_name != TEMPLATE_PACKAGE_NAME:
        reps.append(
            Replacement(
                old=TEMPLATE_PACKAGE_NAME,
                new=cfg.package_name,
                description=f"Package name -> {cfg.package_name}",
            )
        )

    # 4. GitHub username (standalone occurrences in SECURITY.md, issue templates)
    reps.append(
        Replacement(
            old=TEMPLATE_GITHUB_USER,
            new=cfg.github_user,
            description=f"GitHub user -> {cfg.github_user}",
        )
    )

    # 5. Author (scoped to pyproject.toml authors field to avoid false positives)
    if cfg.author != TEMPLATE_AUTHOR:
        reps.append(
            Replacement(
                old=f'name = "{TEMPLATE_AUTHOR}"',
                new=f'name = "{cfg.author}"',
                description=f"Author -> {cfg.author}",
            )
        )

    # 6. Description
    if cfg.description != TEMPLATE_DESCRIPTION:
        reps.append(
            Replacement(
                old=TEMPLATE_DESCRIPTION,
                new=cfg.description,
                description=f"Description -> {cfg.description}",
            )
        )

    # 7. CLI entry-point prefix (compound names first to avoid partial match)
    if cfg.cli_prefix != TEMPLATE_CLI_PREFIX:
        reps.extend(
            Replacement(
                old=f"{TEMPLATE_CLI_PREFIX}{suffix}",
                new=f"{cfg.cli_prefix}{suffix}",
                description=f"CLI command -> {cfg.cli_prefix}{suffix}",
            )
            for suffix in ("-version", "-doctor")
        )
        reps.append(
            Replacement(
                old=f'{TEMPLATE_CLI_PREFIX} = "',
                new=f'{cfg.cli_prefix} = "',
                description=f"CLI base command -> {cfg.cli_prefix}",
            )
        )

    return reps


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------


def _should_process(path: Path) -> bool:
    """Return True if *path* is a text file we should scan for replacements."""
    if not path.is_file():
        return False
    if path.suffix not in TEXT_EXTENSIONS:
        return False
    rel = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    return rel not in SKIP_FILES


def apply_replacements(
    replacements: list[Replacement],
    *,
    dry_run: bool = False,
) -> dict[Path, int]:
    """Apply text replacements across all eligible files in the project.

    Args:
        replacements: Ordered substitutions (applied in sequence per file).
        dry_run: If ``True``, report changes without writing files.

    Returns:
        Mapping of modified file paths to number of individual substitutions.
    """
    modified: dict[Path, int] = {}

    for path in sorted(ROOT.rglob("*")):
        if not _should_process(path):
            continue
        try:
            original = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError):
            continue

        text = original
        count = 0
        for r in replacements:
            hits = text.count(r.old)
            if hits > 0:
                text = text.replace(r.old, r.new)
                count += hits

        if count > 0:
            modified[path] = count
            if not dry_run:
                path.write_text(text, encoding="utf-8")

    return modified


def rename_package_dir(cfg: Config, *, dry_run: bool = False) -> bool:
    """Rename ``src/simple_python_boilerplate/`` to the new package name.

    Also cleans up stale ``.egg-info`` if present.

    Args:
        cfg: Customization config.
        dry_run: If ``True``, report without renaming.

    Returns:
        ``True`` if a rename was performed (or would be in dry-run mode).
    """
    if cfg.package_name == TEMPLATE_PACKAGE_NAME:
        return False

    old_dir = ROOT / "src" / TEMPLATE_PACKAGE_NAME
    new_dir = ROOT / "src" / cfg.package_name

    if not old_dir.is_dir():
        print(f"  WARNING: src/{TEMPLATE_PACKAGE_NAME}/ not found — skipping rename")
        return False
    if new_dir.exists():
        print(f"  WARNING: src/{cfg.package_name}/ already exists — skipping rename")
        return False

    if dry_run:
        print(
            f"  Would rename: src/{TEMPLATE_PACKAGE_NAME}/ -> src/{cfg.package_name}/"
        )
    else:
        old_dir.rename(new_dir)
        print(f"  Renamed: src/{TEMPLATE_PACKAGE_NAME}/ -> src/{cfg.package_name}/")

    # Remove stale .egg-info (will be regenerated by pip install -e .)
    old_egg = ROOT / "src" / f"{TEMPLATE_PACKAGE_NAME}.egg-info"
    if old_egg.is_dir():
        if dry_run:
            print(f"  Would remove: src/{TEMPLATE_PACKAGE_NAME}.egg-info/")
        else:
            shutil.rmtree(old_egg)
            print(f"  Removed stale: src/{TEMPLATE_PACKAGE_NAME}.egg-info/")

    return True


def strip_directories(
    keys: list[str],
    *,
    dry_run: bool = False,
) -> list[str]:
    """Remove optional directories and files from the project.

    Args:
        keys: Keys from :data:`STRIPPABLE` identifying what to remove.
        dry_run: If ``True``, report without deleting.

    Returns:
        Relative paths that were removed (or would be removed).
    """
    removed: list[str] = []

    for key in keys:
        entry = STRIPPABLE.get(key)
        if entry is None:
            continue
        paths: list[str] = entry["paths"]  # type: ignore[assignment]
        for rel_path in paths:
            target = ROOT / rel_path
            if not target.exists():
                continue
            removed.append(rel_path)
            if dry_run:
                kind = "directory" if target.is_dir() else "file"
                print(f"  Would remove {kind}: {rel_path}")
            else:
                if target.is_dir():
                    shutil.rmtree(target)
                    print(f"  Removed directory: {rel_path}")
                else:
                    target.unlink()
                    print(f"  Removed file: {rel_path}")

    return removed


def apply_license(cfg: Config, *, dry_run: bool = False) -> bool:
    """Write the chosen license file and update the pyproject.toml classifier.

    Args:
        cfg: Config with ``license_id`` and ``author`` set.
        dry_run: If ``True``, report without writing.

    Returns:
        ``True`` if the license was changed (or would be).
    """
    choice = LICENSE_CHOICES.get(cfg.license_id)
    if choice is None:
        return False

    template_text: str | None = choice["template"]
    new_classifier: str = choice["classifier"]  # type: ignore[assignment]
    old_classifier: str = LICENSE_CHOICES["apache-2.0"]["classifier"]  # type: ignore[assignment]
    changed = False

    # Replace the LICENSE file if a new template was selected
    license_path = ROOT / "LICENSE"
    if template_text is not None:
        year = datetime.datetime.now(tz=datetime.UTC).year
        content = template_text.format(year=year, author=cfg.author)
        if dry_run:
            print(f"  Would replace LICENSE with {choice['name']}")
        else:
            license_path.write_text(content, encoding="utf-8")
            print(f"  Replaced LICENSE with {choice['name']}")
        changed = True

    # Update the license classifier in pyproject.toml
    if new_classifier != old_classifier:
        pyproject = ROOT / "pyproject.toml"
        if pyproject.is_file():
            text = pyproject.read_text(encoding="utf-8")
            if old_classifier in text:
                if dry_run:
                    print("  Would update license classifier in pyproject.toml")
                else:
                    text = text.replace(old_classifier, new_classifier)
                    pyproject.write_text(text, encoding="utf-8")
                    print("  Updated license classifier in pyproject.toml")
                changed = True

    return changed


# ---------------------------------------------------------------------------
# Safety check
# ---------------------------------------------------------------------------


def _already_customized() -> bool:
    """Heuristic: return ``True`` if the template appears already customized."""
    pkg_dir = ROOT / "src" / TEMPLATE_PACKAGE_NAME
    if not pkg_dir.is_dir():
        return True

    pyproject = ROOT / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8", errors="ignore")
        if f'name = "{TEMPLATE_PROJECT_NAME}"' not in text:
            return True

    return False


# ---------------------------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------------------------


def print_plan(cfg: Config, replacements: list[Replacement]) -> None:
    """Print a human-readable summary of planned changes for confirmation.

    Args:
        cfg: Customization config.
        replacements: Planned text substitutions.
    """
    print("\n=== Customization Plan ===\n")

    print("Text replacements:")
    for r in replacements:
        print(f"  - {r.description}")

    if cfg.package_name != TEMPLATE_PACKAGE_NAME:
        print("\nDirectory rename:")
        print(f"  - src/{TEMPLATE_PACKAGE_NAME}/ -> src/{cfg.package_name}/")

    if cfg.license_id != "apache-2.0":
        name = LICENSE_CHOICES[cfg.license_id]["name"]
        print(f"\nLicense: switch to {name}")

    if cfg.strip_dirs:
        print("\nDirectories to remove:")
        for key in cfg.strip_dirs:
            entry = STRIPPABLE[key]
            print(f"  - {entry['label']}")
            paths: list[str] = entry["paths"]  # type: ignore[assignment]
            for p in paths:
                exists = (ROOT / p).exists()
                marker = "" if exists else " (not found)"
                print(f"      {p}{marker}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Interactive project customization — replaces boilerplate "
            "placeholders with your project's values."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  python scripts/customize.py
  python scripts/customize.py --dry-run
  python scripts/customize.py --non-interactive \\
      --project-name my-project --author "Jane Doe" \\
      --github-user janedoe
""",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without modifying any files",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Skip interactive prompts; use CLI arguments for all values",
    )
    parser.add_argument("--project-name", help="Project name (lowercase-hyphenated)")
    parser.add_argument(
        "--package-name",
        help="Python package name (underscored; auto-derived from --project-name if omitted)",
    )
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--github-user", help="GitHub username or organization")
    parser.add_argument("--description", help="One-line project description")
    parser.add_argument(
        "--cli-prefix",
        help="CLI command prefix (default: initials of project name)",
    )
    parser.add_argument(
        "--license",
        choices=list(LICENSE_CHOICES.keys()),
        default="apache-2.0",
        dest="license_id",
        help="License to use (default: apache-2.0)",
    )
    parser.add_argument(
        "--strip",
        nargs="*",
        choices=list(STRIPPABLE.keys()),
        default=[],
        metavar="DIR",
        help=(
            f"Optional directories to remove. Choices: {', '.join(STRIPPABLE.keys())}"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip the already-customized safety check",
    )
    parser.add_argument(
        "--enable-workflows",
        metavar="OWNER/REPO",
        help=(
            "Enable all GitHub workflows by replacing 'YOURNAME/YOURREPO' placeholder. "
            "Pass your repo slug (e.g. 'myorg/myproject'). Runs only this operation."
        ),
    )
    return parser.parse_args(argv)


def config_from_args(args: argparse.Namespace) -> Config:
    """Build a :class:`Config` from parsed CLI arguments (non-interactive).

    Args:
        args: Parsed CLI arguments.

    Returns:
        Populated Config instance.

    Raises:
        SystemExit: If required arguments are missing.
    """
    missing: list[str] = []
    if not args.project_name:
        missing.append("--project-name")
    if not args.author:
        missing.append("--author")
    if not args.github_user:
        missing.append("--github-user")

    if missing:
        print(
            f"ERROR: --non-interactive requires: {', '.join(missing)}",
            file=sys.stderr,
        )
        raise SystemExit(2)

    package_name = args.package_name or args.project_name.replace("-", "_")
    parts = args.project_name.split("-")
    cli_prefix = args.cli_prefix or (
        "".join(p[0] for p in parts if p) if len(parts) > 1 else args.project_name
    )
    description = args.description or f"{args.project_name} — a Python project"

    return Config(
        project_name=args.project_name,
        package_name=package_name,
        author=args.author,
        github_user=args.github_user,
        description=description,
        cli_prefix=cli_prefix,
        license_id=args.license_id,
        strip_dirs=args.strip or [],
        dry_run=args.dry_run,
    )


# ---------------------------------------------------------------------------
# Enable Workflows Only
# ---------------------------------------------------------------------------


def enable_workflows_only(repo_slug: str, *, dry_run: bool = False) -> int:
    """Enable all workflows by replacing the YOURNAME/YOURREPO placeholder.

    This is a quick operation that only touches workflow files and related docs.

    Args:
        repo_slug: The GitHub repository slug (e.g., 'myorg/myproject').
        dry_run: If True, show what would change without modifying files.

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    # Validate slug format
    if "/" not in repo_slug or repo_slug.count("/") != 1:
        print(f"ERROR: Invalid repo slug '{repo_slug}'. Expected 'owner/repo' format.")
        return 1

    owner, repo = repo_slug.split("/")
    if not owner or not repo:
        print(
            f"ERROR: Invalid repo slug '{repo_slug}'. Both owner and repo are required."
        )
        return 1

    replacements = [
        Replacement(
            old=TEMPLATE_GITHUB_URL_PLACEHOLDER,
            new=repo_slug,
            description=f"GitHub URL placeholder -> {repo_slug}",
        ),
    ]

    tag = "DRY RUN — " if dry_run else ""
    print(f"{tag}Enabling workflows with repo slug: {repo_slug}")
    print()

    modified = apply_replacements(replacements, dry_run=dry_run)

    if not modified:
        print("No files needed updating (placeholder may already be replaced).")
        return 0

    for path, count in modified.items():
        rel = path.relative_to(ROOT)
        print(f"  {rel} ({count} replacement{'s' if count != 1 else ''})")

    total = sum(modified.values())
    n_files = len(modified)
    print(
        f"\nTotal: {total} replacement{'s' if total != 1 else ''}"
        f" in {n_files} file{'s' if n_files != 1 else ''}"
    )

    if dry_run:
        print("\nDry run complete — no files were modified.")
    else:
        print("\nWorkflows enabled! They will now run on your repository.")

    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point for the customize script.

    Returns:
        Exit code: 0 on success, 1 on abort or error.
    """
    args = parse_args()

    # Handle --enable-workflows as a standalone operation
    if args.enable_workflows:
        return enable_workflows_only(args.enable_workflows, dry_run=args.dry_run)

    # Safety check: warn if the template appears already customized
    if not args.force and _already_customized():
        print(
            "WARNING: This project appears to have already been customized "
            f"(src/{TEMPLATE_PACKAGE_NAME}/ is missing or pyproject.toml "
            "has been modified)."
        )
        if args.non_interactive:
            print("Use --force to run anyway.", file=sys.stderr)
            return 1
        if not _prompt_yn("Run anyway?", default=False):
            print("Aborted.")
            return 0

    # Gather configuration
    if args.non_interactive:
        cfg = config_from_args(args)
    else:
        cfg = gather_config_interactive()

    cfg.dry_run = args.dry_run

    # Plan and show
    replacements = plan_replacements(cfg)
    print_plan(cfg, replacements)

    # Confirm (interactive only, skip for dry-run since it's non-destructive)
    if (
        not args.non_interactive
        and not cfg.dry_run
        and not _prompt_yn("Proceed with these changes?")
    ):
        print("Aborted.")
        return 0

    tag = "DRY RUN — " if cfg.dry_run else ""

    # Step 1: Strip optional directories (before rename so paths still match)
    if cfg.strip_dirs:
        print(f"\n{tag}Stripping optional directories...")
        strip_directories(cfg.strip_dirs, dry_run=cfg.dry_run)

    # Step 2: Text replacements across all files
    print(f"\n{tag}Applying text replacements...")
    modified = apply_replacements(replacements, dry_run=cfg.dry_run)
    for path, count in modified.items():
        rel = path.relative_to(ROOT)
        print(f"  {rel} ({count} replacement{'s' if count != 1 else ''})")
    total = sum(modified.values())
    n_files = len(modified)
    print(
        f"  Total: {total} replacement{'s' if total != 1 else ''}"
        f" in {n_files} file{'s' if n_files != 1 else ''}"
    )

    # Step 3: Rename package directory
    print(f"\n{tag}Package directory...")
    if not rename_package_dir(cfg, dry_run=cfg.dry_run):
        print("  (no rename needed)")

    # Step 4: License
    print(f"\n{tag}License...")
    if not apply_license(cfg, dry_run=cfg.dry_run):
        print("  (keeping Apache-2.0)")

    # Done
    if cfg.dry_run:
        print("\nDry run complete — no files were modified.")
    else:
        print("\nCustomization complete!")
        ws_file = ROOT / f"{TEMPLATE_PROJECT_NAME}.code-workspace"
        print("\nNext steps:")
        print("  1. Review the changes:  git diff")
        print("  2. Reinstall:           pip install -e '.[dev]'")
        print("  3. Run tests:           task test  (or pytest)")
        print(f'  4. Verify import:       python -c "import {cfg.package_name}"')
        if ws_file.exists():
            print(
                f"  5. Rename workspace:    {TEMPLATE_PROJECT_NAME}.code-workspace"
                f" -> {cfg.project_name}.code-workspace"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
