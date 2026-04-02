"""FastAPI app factory and Uvicorn entry point.

Security:
    - Binds to 127.0.0.1 only (local access).
    - Jinja2 autoescape=True (XSS prevention).
    - Read-only — no system mutations.

Usage::

    python -m tools.dev_tools.env_dashboard.app
    # or
    hatch run dashboard:serve
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[2]

# Add scripts/ to sys.path so _env_collectors can be imported
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Add repo root to sys.path so tools.dev_tools.env_dashboard can be imported
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Environment Dashboard",
        description="Local-only environment inspection dashboard",
        docs_url=None,  # Disable Swagger UI for local tool
        redoc_url=None,
    )

    # Mount static files
    static_dir = _HERE / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Set up Jinja2 templates with autoescape (non-negotiable)
    templates = Jinja2Templates(directory=str(_HERE / "templates"))
    templates.env.autoescape = True

    # Store templates on app state for route handlers
    app.state.templates = templates

    # Register routes
    from tools.dev_tools.env_dashboard.api import router as api_router
    from tools.dev_tools.env_dashboard.routes import router as html_router

    app.include_router(html_router)
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


def main() -> None:
    """Start the dashboard server."""
    import uvicorn

    print("Starting Environment Dashboard at http://127.0.0.1:8000")  # noqa: T201
    uvicorn.run(
        "tools.dev_tools.env_dashboard.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(_HERE)],
    )


if __name__ == "__main__":
    main()
