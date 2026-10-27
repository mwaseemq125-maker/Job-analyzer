"""Shared LangGraph state passed from node to node."""

from __future__ import annotations

from typing import Any, Dict, Optional, TypedDict


class AnalyzerState(TypedDict, total=False):
    job_description: str          # input
    job_info: Dict[str, Any]      # written by Node 1
    classification: Dict[str, Any]  # written by Node 2
    skill_analysis: Dict[str, Any]  # written by Node 3
    report: Dict[str, Any]        # written by Node 4
    error: Optional[str]          # set by any node on failure -> graph stops
