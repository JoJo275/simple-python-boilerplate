"""HTML route handlers — full pages and htmx partials."""

from __future__ import annotations

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from tools.dev_tools.env_dashboard.collector import get_report
from tools.dev_tools.env_dashboard.export import render_export
from tools.dev_tools.env_dashboard.redact import parse_redact_param

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    redact: str | None = Query(default=None),
    tier: str = Query(default="standard"),
) -> HTMLResponse:
    """Dashboard home page."""
    tier_enum = _parse_tier(tier)
    redact_level = parse_redact_param(redact)
    report = get_report(tier=tier_enum, redact_level=redact_level)

    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "report": report,
            "summary": report.get("summary", {}),
            "warnings": report.get("warnings", []),
            "sections": report.get("sections", {}),
            "meta": report.get("meta", {}),
            "redact_level": redact_level.value,
        },
    )


@router.get("/section/{name}", response_class=HTMLResponse)
async def section_partial(
    request: Request,
    name: str,
    redact: str | None = Query(default=None),
    tier: str = Query(default="standard"),
) -> HTMLResponse:
    """Render a single section as an htmx partial."""
    tier_enum = _parse_tier(tier)
    redact_level = parse_redact_param(redact)
    report = get_report(tier=tier_enum, redact_level=redact_level)
    sections = report.get("sections", {})
    section_data = sections.get(name, {})

    template_name = f"partials/{name}.html"
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        template_name,
        context={
            "data": section_data,
            "section_name": name,
            "redact_level": redact_level.value,
        },
    )


def _parse_tier(value: str) -> object:
    """Parse tier string to Tier enum."""
    from _env_collectors import Tier

    value_lower = value.lower().strip()
    for t in Tier:
        if t.value == value_lower:
            return t
    return Tier.STANDARD


@router.get("/export.html", response_class=HTMLResponse)
async def export_html(
    request: Request,
    redact: str | None = Query(default=None),
    tier: str = Query(default="standard"),
) -> HTMLResponse:
    """Self-contained HTML export (no JS, inline CSS)."""
    tier_enum = _parse_tier(tier)
    redact_level = parse_redact_param(redact, export=True)
    report = get_report(tier=tier_enum, redact_level=redact_level)

    templates = request.app.state.templates
    html = render_export(templates, report, redact_level.value)
    return HTMLResponse(html)
