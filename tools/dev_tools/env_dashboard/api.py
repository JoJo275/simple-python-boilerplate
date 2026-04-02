"""JSON API route handlers."""

from __future__ import annotations

import json
import time

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

from tools.dev_tools.env_dashboard.collector import (
    get_report,
    invalidate_cache,
)
from tools.dev_tools.env_dashboard.redact import parse_redact_param

router = APIRouter()


@router.get("/summary")
async def api_summary(redact: str | None = Query(default=None)) -> JSONResponse:
    """Top summary bar data only."""
    redact_level = parse_redact_param(redact)
    report = get_report(redact_level=redact_level)
    return JSONResponse(report.get("summary", {}))


@router.get("/report")
async def api_report(
    redact: str | None = Query(default=None),
    tier: str = Query(default="standard"),
) -> JSONResponse:
    """Full scan report (all sections, current tier)."""
    redact_level = parse_redact_param(redact)
    tier_enum = _parse_tier(tier)
    report = get_report(tier=tier_enum, redact_level=redact_level)
    return JSONResponse(report)


@router.get("/warnings")
async def api_warnings(redact: str | None = Query(default=None)) -> JSONResponse:
    """Warnings panel data only."""
    redact_level = parse_redact_param(redact)
    report = get_report(redact_level=redact_level)
    return JSONResponse(report.get("warnings", []))


@router.get("/sections/{name}")
async def api_section(
    name: str,
    redact: str | None = Query(default=None),
) -> JSONResponse:
    """Single section by name."""
    redact_level = parse_redact_param(redact)
    report = get_report(redact_level=redact_level)
    sections = report.get("sections", {})
    if name not in sections:
        return JSONResponse({"error": f"Section '{name}' not found"}, status_code=404)
    return JSONResponse(sections[name])


@router.post("/scan")
async def api_scan(
    redact: str | None = Query(default=None),
    tier: str = Query(default="standard"),
) -> JSONResponse:
    """Trigger a fresh scan (cache invalidation + re-collection)."""
    invalidate_cache()
    redact_level = parse_redact_param(redact)
    tier_enum = _parse_tier(tier)
    report = get_report(tier=tier_enum, redact_level=redact_level, force=True)
    return JSONResponse(
        {"status": "ok", "timestamp": report.get("meta", {}).get("timestamp")}
    )


@router.get("/export.json")
async def api_export_json(
    redact: str | None = Query(default=None),
    tier: str = Query(default="standard"),
) -> Response:
    """Full scan as downloadable JSON (PII-redacted by default)."""
    redact_level = parse_redact_param(redact, export=True)
    tier_enum = _parse_tier(tier)
    report = get_report(tier=tier_enum, redact_level=redact_level)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"env-report-{timestamp}.json"

    return Response(
        content=json.dumps(report, indent=2, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _parse_tier(value: str) -> object:
    """Parse tier string to Tier enum."""
    from _env_collectors import Tier

    value_lower = value.lower().strip()
    for t in Tier:
        if t.value == value_lower:
            return t
    return Tier.STANDARD
