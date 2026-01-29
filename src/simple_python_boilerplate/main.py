"""CLI entry points for simple-python-boilerplate."""

import sys
from importlib.metadata import version, PackageNotFoundError


def main() -> None:
    """Main CLI entry point."""
    print("Hello from CLI")


def print_version() -> None:
    """Print version information and exit."""
    try:
        v = version("simple-python-boilerplate")
    except PackageNotFoundError:
        # Fallback for editable installs or development
        from simple_python_boilerplate import __version__
        v = __version__
    
    print(f"simple-python-boilerplate {v}")
    print(f"Python {sys.version}")


def doctor() -> None:
    """Diagnose environment and configuration issues."""
    import platform
    import shutil
    from pathlib import Path
    
    print("🩺 simple-python-boilerplate doctor\n")
    
    # Version info
    print("== Version ==")
    try:
        v = version("simple-python-boilerplate")
    except PackageNotFoundError:
        from simple_python_boilerplate import __version__
        v = f"{__version__} (editable/dev install)"
    print(f"  Package version: {v}")
    print(f"  Python version:  {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"  Platform:        {platform.system()} {platform.release()}")
    print()
    
    # Python environment
    print("== Environment ==")
    print(f"  Executable: {sys.executable}")
    print(f"  Prefix:     {sys.prefix}")
    in_venv = sys.prefix != sys.base_prefix
    print(f"  Virtual env: {'✅ Yes' if in_venv else '⚠️  No (consider using a venv)'}")
    print()
    
    # Check for common dev tools
    print("== Dev Tools ==")
    tools = ["pytest", "ruff", "mypy", "pre-commit"]
    for tool in tools:
        path = shutil.which(tool)
        if path:
            print(f"  {tool}: ✅ {path}")
        else:
            print(f"  {tool}: ❌ not found")
    print()
    
    # Check for config files
    print("== Config Files ==")
    config_files = [
        "pyproject.toml",
        ".pre-commit-config.yaml",
        ".gitignore",
        "requirements.txt",
        "requirements-dev.txt",
    ]
    cwd = Path.cwd()
    for cfg in config_files:
        exists = (cwd / cfg).exists()
        print(f"  {cfg}: {'✅ found' if exists else '⚠️  missing'}")
    print()
    
    print("✨ Doctor complete!")

