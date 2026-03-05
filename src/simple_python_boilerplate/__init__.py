# Version is set by hatch-vcs from git tags at build/install time.
# The _version.py file is auto-generated and gitignored.
# The fallback below is updated by release-please in its Release PR.
try:
    from simple_python_boilerplate._version import __version__, __version_tuple__
except ImportError:
    __version__ = "0.5.0"  # x-release-please-version
    # Derive tuple from the string so release-please only needs to
    # update one line.  The marker above is the single source of truth.
    __version_tuple__ = tuple(int(x) for x in __version__.split("."))

__all__ = ["__version__", "__version_tuple__"]
