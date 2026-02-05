"""
Application entry points (thin wrappers).

This module contains the entry points configured in pyproject.toml. These are
the functions that get called when users run CLI commands. They should be thin
wrappers that delegate to cli.py for argument parsing and engine.py for logic.

File Workflow:
    main.py  → starts the program (entry points, thin wrappers)
    cli.py   → defines CLI contract (argument parsing, commands)
    engine.py → defines behavior (core logic, interface-agnostic)
    api.py   → defines callable interface (HTTP/REST, optional)

Entry points (configured in pyproject.toml):
    - main: Primary CLI command
    - print_version: Show version info
    - doctor: Diagnose environment issues

See also:
    - cli.py: Argument parsing and command structure
    - engine.py: Core business logic
    - api.py: HTTP/REST interface
"""

import sys


def main() -> None:
    """Main CLI entry point.

    Delegates to cli.run() for argument parsing and dispatch.
    """
    from simple_python_boilerplate import cli

    sys.exit(cli.run(cli.parse_args()))


def print_version() -> None:
    """Print version information and exit."""
    from simple_python_boilerplate.engine import get_version_info

    info = get_version_info()
    print(f"simple-python-boilerplate {info['package_version']}")
    print(f"Python {info['python_full']}")


def doctor() -> None:
    """Diagnose environment and configuration issues.

    Delegates to engine.diagnose_environment() for the actual checks,
    then formats the output for the terminal.
    """
    from simple_python_boilerplate.engine import (
        DiagnosticInfo,
        diagnose_environment,
    )

    diag: DiagnosticInfo = diagnose_environment()

    print("🩺 simple-python-boilerplate doctor\n")

    # Version info
    print("== Version ==")
    print(f"  Package version: {diag['version']['package_version']}")
    print(f"  Python version:  {diag['version']['python_version']}")
    print(f"  Platform:        {diag['version']['platform']}")
    print()

    # Python environment
    print("== Environment ==")
    print(f"  Executable: {diag['executable']}")
    print(f"  Prefix:     {diag['prefix']}")
    venv_status = (
        '✅ Yes' if diag['in_virtual_env']
        else '⚠️  No (consider using a venv)'
    )
    print(f"  Virtual env: {venv_status}")
    print()

    # Check for common dev tools
    print("== Dev Tools ==")
    for tool, path in diag['tools'].items():
        if path:
            print(f"  {tool}: ✅ {path}")
        else:
            print(f"  {tool}: ❌ not found")
    print()

    # Check for config files
    print("== Config Files ==")
    for cfg, exists in diag['config_files'].items():
        print(f"  {cfg}: {'✅ found' if exists else '⚠️  missing'}")
    print()

    print("✨ Doctor complete!")
