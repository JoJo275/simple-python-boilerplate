# Version is set by hatch-vcs from git tags at build/install time.
# The _version.py file is auto-generated and gitignored.
# The fallback below is updated by release-please in its Release PR.
try:
    from simple_python_boilerplate._version import __version__, __version_tuple__
except ImportError:
    __version__ = "0.3.0"  # x-release-please-version
    __version_tuple__ = (0, 1, 0)

__all__ = ["__version__", "__version_tuple__"]
