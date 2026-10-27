"""Node 1 - Information Extraction: title, company, experience, required skills."""

from __future__ import annotations

from nodes.base import run_structured, safe_node
from prompts import EXTRACTION_SYSTEM, EXTRACTION_USER
from schemas import JobInfo
from state import AnalyzerState


@safe_node("Information Extraction")
def extract_information(state: AnalyzerState) -> dict:
    job_description = state["job_description"]
    info = run_structured(
        JobInfo,
        EXTRACTION_SYSTEM,
        EXTRACTION_USER.format(job_description=job_description),
    )
    return {"job_info": info.model_dump()}
