"""Export the hiring report to JSON."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from config import OUTPUT_DIR
from schemas import HiringReport


def report_to_json(report: HiringReport, indent: int = 2) -> str:
    """Serialize the report to a pretty JSON string."""
    return json.dumps(report.model_dump(), indent=indent, ensure_ascii=False)


def default_filename(report: HiringReport) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", report.job_title.lower()).strip("_") or "report"
    return f"hiring_report_{slug}_{datetime.now():%Y%m%d_%H%M%S}.json"


def export_report_json(report: HiringReport, path: str | Path | None = None) -> Path:
    """Write the report to disk and return the file path (defaults to ./outputs/)."""
    target = Path(path) if path else OUTPUT_DIR / default_filename(report)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report_to_json(report), encoding="utf-8")
    return target
