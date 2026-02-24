#!/usr/bin/env python3
"""Repo doctor — warn-only health checks for repository structure.

Reads rules from ``.repo-doctor.toml`` and reports missing files,
directories, TOML config sections, and content patterns.  Never blocks;
always exits 0.

Usage::

    python scripts/repo_doctor.py
    python scripts/repo_doctor.py --missing --staged
    python scripts/repo_doctor.py --category ci --min-level info
    python scripts/repo_doctor.py --include-info
    python scripts/repo_doctor.py --profile python --profile docs
    python scripts/repo_doctor.py --fix
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess  # nosec B404
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OnlyIf:
    """Conditional gate: only evaluate the parent rule when *path* contains *regex*."""

    path: str
    regex: str


@dataclass(frozen=True)
class Rule:
    """A single doctor check loaded from ``.repo-doctor.toml``."""

    type: str  # "exists" | "toml_has_path" | "regex_present"
    path: str
    kind: str = "file"  # for exists: "file" | "dir" | "any"
    level: str = "warn"  # "warn" | "info"
    category: str = ""  # grouping tag (e.g. "ci", "security")
    impact: str = ""
    hint: str = ""
    link: str = ""  # ADR or doc reference
    fix: str = ""  # command to auto-fix
    toml_path: str = ""  # for toml_has_path
    regex: str = ""  # for regex_present
    only_if: OnlyIf | None = field(default=None)


@dataclass
class Warning:
    """A single diagnostic produced during evaluation."""

    rule: Rule
    message: str


@dataclass(frozen=True)
class DoctorConfig:
    """Settings from the ``[doctor]`` section of ``.repo-doctor.toml``."""

    ignore_missing: frozenset[str] = field(default_factory=frozenset)
    profiles: tuple[str, ...] = field(default_factory=tuple)


_LEVEL_ORDER: dict[str, int] = {"info": 0, "warn": 1}


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

_GIT_CMD: str | None = shutil.which("git")


def _run_git(root: Path, args: list[str]) -> tuple[int, str, str]:
    """Run a git command and return *(returncode, stdout, stderr)*."""
    if _GIT_CMD is None:
        return 1, "", "git not found on PATH"
    result = subprocess.run(  # nosec B603
        [_GIT_CMD, *args],
        cwd=root,
        text=True,
        capture_output=True,
    )
    return result.returncode, result.stdout, result.stderr


def _repo_root() -> Path:
    """Discover the repository root via ``git rev-parse``."""
    code, out, _ = _run_git(Path.cwd(), ["rev-parse", "--show-toplevel"])
    return Path(out.strip()) if code == 0 else Path.cwd()


def _list_deleted_paths(
    root: Path, *, staged: bool, diff_range: str | None
) -> list[str]:
    """Return repo-relative paths that are deleted in the given scope."""
    if diff_range:
        code, out, _ = _run_git(
            root, ["diff", "--name-status", "--diff-filter=D", diff_range]
        )
        if code != 0:
            return []
    elif staged:
        code, out, _ = _run_git(
            root, ["diff", "--cached", "--name-status", "--diff-filter=D"]
        )
        if code != 0:
            return []
    else:
        return []

    deleted: list[str] = []
    for line in out.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[0].strip() == "D":
            deleted.append(parts[1].strip())
    return deleted


# ---------------------------------------------------------------------------
# File scanning helpers
# ---------------------------------------------------------------------------


def _exists_kind(root: Path, rel: str, kind: str) -> bool:
    """Check whether *rel* exists under *root* with the expected *kind*."""
    target = root / rel
    if kind == "dir":
        return target.is_dir()
    if kind == "any":
        return target.exists()
    return target.is_file()


def _iter_files_under(root: Path, rel: str) -> list[Path]:
    """List all files at or beneath *rel*."""
    base = root / rel
    if base.is_file():
        return [base]
    if base.is_dir():
        return [p for p in base.rglob("*") if p.is_file()]
    return []


def _file_contains_regex(root: Path, rel: str, pattern: str) -> bool:
    """Return ``True`` if any file at or beneath *rel* matches *pattern*."""
    rx = re.compile(pattern)
    for filepath in _iter_files_under(root, rel):
        try:
            text = filepath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if rx.search(text):
            return True
    return False


def _toml_has_path(root: Path, rel: str, dotted: str) -> tuple[bool, str]:
    """Check for a dotted key path in a TOML file.

    Returns:
        A tuple of ``(ok, note)`` where *note* is non-empty on parse failure.
    """
    target = root / rel
    if not target.is_file():
        return False, ""
    if tomllib is None:
        return False, "tomllib not available (need Python 3.11+ for TOML checks)."

    try:
        data = tomllib.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"Could not parse TOML: {exc!s}"

    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False, ""
        cur = cur[part]
    return True, ""


def _matches_deletion(rule_path: str, rule_kind: str, deleted_path: str) -> bool:
    """Return ``True`` if *deleted_path* falls under *rule_path*."""
    if rule_kind != "dir":
        return deleted_path == rule_path
    prefix = rule_path.rstrip("/") + "/"
    return deleted_path.startswith(prefix) or deleted_path == rule_path.rstrip("/")


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def _parse_rule_entries(raw_rules: list[dict[str, Any]]) -> list[Rule]:
    """Convert raw TOML dicts into validated :class:`Rule` objects."""
    rules: list[Rule] = []
    for entry in raw_rules:
        only_if = None
        oi = entry.get("only_if")
        if isinstance(oi, dict) and oi.get("path") and oi.get("regex"):
            only_if = OnlyIf(path=str(oi["path"]), regex=str(oi["regex"]))

        rules.append(
            Rule(
                type=str(entry.get("type", "")).strip(),
                path=str(entry.get("path", "")).strip(),
                kind=str(entry.get("kind", "file")).strip(),
                level=str(entry.get("level", "warn")).strip(),
                category=str(entry.get("category", "")).strip(),
                impact=str(entry.get("impact", "")).strip(),
                hint=str(entry.get("hint", "")).strip(),
                link=str(entry.get("link", "")).strip(),
                fix=str(entry.get("fix", "")).strip(),
                toml_path=str(entry.get("toml_path", "")).strip(),
                regex=str(entry.get("regex", "")).strip(),
                only_if=only_if,
            )
        )
    return [r for r in rules if r.type and r.path]


def _load_doctor_config(data: dict[str, Any]) -> DoctorConfig:
    """Parse the ``[doctor]`` section from parsed TOML *data*."""
    doctor = data.get("doctor", {})
    if not isinstance(doctor, dict):
        return DoctorConfig()

    ignore = doctor.get("ignore_missing", [])
    if not isinstance(ignore, list):
        ignore = []

    profiles = doctor.get("profiles", [])
    if not isinstance(profiles, list):
        profiles = []

    return DoctorConfig(
        ignore_missing=frozenset(str(p) for p in ignore),
        profiles=tuple(str(p) for p in profiles),
    )


def _load_rules(root: Path) -> tuple[list[Rule], DoctorConfig]:
    """Parse ``.repo-doctor.toml`` and return rules plus doctor config."""
    cfg = root / ".repo-doctor.toml"
    if not cfg.exists():
        return [], DoctorConfig()
    if tomllib is None:
        return [], DoctorConfig()

    data = tomllib.loads(cfg.read_text(encoding="utf-8"))
    rules = _parse_rule_entries(data.get("rule", []))
    config = _load_doctor_config(data)
    return rules, config


def _load_profile_rules(root: Path, profiles: list[str]) -> list[Rule]:
    """Load additional rules from ``repo_doctor.d/<name>.toml`` files.

    The special profile name ``"all"`` loads every ``.toml`` file in the
    directory.
    """
    profile_dir = root / "repo_doctor.d"
    if not profile_dir.is_dir() or tomllib is None:
        return []

    files_to_load: list[Path] = []
    for name in profiles:
        if name == "all":
            files_to_load = sorted(profile_dir.glob("*.toml"))
            break
        candidate = profile_dir / f"{name}.toml"
        if candidate.is_file():
            files_to_load.append(candidate)

    all_rules: list[Rule] = []
    for fpath in files_to_load:
        try:
            data = tomllib.loads(fpath.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            # Skip unreadable or unparsable profile files gracefully.
            continue
        all_rules.extend(_parse_rule_entries(data.get("rule", [])))
    return all_rules


# ---------------------------------------------------------------------------
# Rule evaluation
# ---------------------------------------------------------------------------


def _evaluate_rules(
    root: Path,
    rules: list[Rule],
    *,
    check_missing: bool,
    deleted: set[str],
) -> list[Warning]:
    """Evaluate all rules and return a list of warnings."""
    warnings: list[Warning] = []

    # Deletion warnings
    if deleted:
        for rule in rules:
            kind = rule.kind if rule.type == "exists" else "file"
            for deleted_path in deleted:
                if _matches_deletion(rule.path, kind, deleted_path):
                    warnings.append(Warning(rule=rule, message=f"Deleted: {rule.path}"))
                    break

    # Rule checks
    for rule in rules:
        if rule.only_if and not _file_contains_regex(
            root, rule.only_if.path, rule.only_if.regex
        ):
            continue

        if rule.type == "exists":
            if check_missing and not _exists_kind(root, rule.path, rule.kind):
                warnings.append(Warning(rule=rule, message=f"Missing: {rule.path}"))

        elif rule.type == "regex_present":
            if not _exists_kind(root, rule.path, "any"):
                if check_missing:
                    warnings.append(Warning(rule=rule, message=f"Missing: {rule.path}"))
                continue
            if rule.regex and not _file_contains_regex(root, rule.path, rule.regex):
                warnings.append(
                    Warning(
                        rule=rule,
                        message=f"Check failed: expected pattern in {rule.path}",
                    )
                )

        elif rule.type == "toml_has_path":
            if not _exists_kind(root, rule.path, "file"):
                # Target file missing — the anchor "exists" rule covers this.
                continue
            ok, note = _toml_has_path(root, rule.path, rule.toml_path)
            if not ok:
                if note:
                    warnings.append(
                        Warning(
                            rule=rule,
                            message=f"TOML parse issue in {rule.path}: {note}",
                        )
                    )
                warnings.append(
                    Warning(
                        rule=rule,
                        message=(
                            f"Check failed: [{rule.toml_path}] missing in {rule.path}"
                        ),
                    )
                )

        else:
            warnings.append(
                Warning(
                    rule=rule,
                    message=(
                        f"Unknown rule type '{rule.type}' for"
                        f" path '{rule.path}' (ignored)"
                    ),
                )
            )

    return warnings


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _format_warning(
    warning: Warning, *, show_hints: bool, show_links: bool, show_fix: bool
) -> str:
    """Format a single warning as a human-readable string."""
    rule = warning.rule
    tag = f"[{rule.level}]" if rule.level else "[warn]"
    cat = f" ({rule.category})" if rule.category else ""

    lines = [f"{tag}{cat} {warning.message}"]
    if rule.impact:
        lines.append(f"  Impact: {rule.impact}")
    if show_hints and rule.hint:
        lines.append(f"  Hint:   {rule.hint}")
    if show_links and rule.link:
        lines.append(f"  See:    {rule.link}")
    if show_fix and rule.fix:
        lines.append(f"  Fix:    {rule.fix}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Warn-only repo doctor checks "
        "(missing files, deletions, config presence).",
    )
    parser.add_argument(
        "--missing",
        action="store_true",
        help="Report missing files/dirs in working tree.",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Report staged deletions (index).",
    )
    parser.add_argument(
        "--diff",
        default=None,
        metavar="RANGE",
        help='Report deletions in a git diff range, e.g. "origin/main...HEAD".',
    )
    parser.add_argument(
        "--category",
        default=None,
        metavar="CAT",
        help="Only show rules matching this category (e.g. ci, hooks, security).",
    )
    parser.add_argument(
        "--min-level",
        default="warn",
        choices=["info", "warn"],
        help="Minimum severity to display (default: warn). Use 'info' to include everything.",
    )
    parser.add_argument(
        "--include-info",
        action="store_true",
        help="Include info-level checks (shorthand for --min-level info).",
    )
    parser.add_argument(
        "--profile",
        action="append",
        default=None,
        metavar="NAME",
        help=(
            "Load additional rules from repo_doctor.d/NAME.toml "
            "(repeatable; 'all' loads everything)."
        ),
    )
    parser.add_argument(
        "--no-hints",
        action="store_true",
        help="Hide hint lines.",
    )
    parser.add_argument(
        "--no-links",
        action="store_true",
        help="Hide link/reference lines.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show auto-fix commands for rules that define one.",
    )
    return parser


def main() -> int:
    """Entry point — always returns 0 (warn-only, never blocks)."""
    parser = _build_parser()
    args = parser.parse_args()

    # Default: check missing + staged
    if not (args.missing or args.staged or args.diff):
        args.missing = True
        args.staged = True

    root = _repo_root()
    rules, config = _load_rules(root)

    # Merge profile rules (config defaults + CLI overrides)
    profile_names: list[str] = list(config.profiles)
    if args.profile:
        profile_names.extend(args.profile)
    if profile_names:
        rules.extend(_load_profile_rules(root, profile_names))

    if not rules:
        print(
            "Repo doctor: no rules found"
            " (missing .repo-doctor.toml or TOML parser unavailable)."
        )
        return 0

    # Filter by minimum severity level
    min_level = "info" if args.include_info else args.min_level
    min_order = _LEVEL_ORDER.get(min_level, 0)
    rules = [r for r in rules if _LEVEL_ORDER.get(r.level, 0) >= min_order]

    # Filter by category if requested
    if args.category:
        rules = [r for r in rules if r.category == args.category]

    # Remove explicitly ignored paths
    if config.ignore_missing:
        rules = [r for r in rules if r.path not in config.ignore_missing]

    deleted = set(_list_deleted_paths(root, staged=args.staged, diff_range=args.diff))

    warnings = _evaluate_rules(root, rules, check_missing=args.missing, deleted=deleted)

    if warnings:
        print("Repo doctor warnings (non-blocking):")
        print()
        for w in warnings:
            print(
                _format_warning(
                    w,
                    show_hints=not args.no_hints,
                    show_links=not args.no_links,
                    show_fix=args.fix,
                )
            )
            print()
    else:
        print("Repo doctor: all checks passed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
