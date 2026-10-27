"""Node 2 - Job Classification: job category, employment type and work mode."""

from __future__ import annotations

from nodes.base import run_structured, safe_node
from prompts import CLASSIFICATION_SYSTEM, CLASSIFICATION_USER
from schemas import JobClassification
from state import AnalyzerState


@safe_node("Job Classification")
def classify_job(state: AnalyzerState) -> dict:
    info = state["job_info"]
    result = run_structured(
        JobClassification,
        CLASSIFICATION_SYSTEM,
        CLASSIFICATION_USER.format(
            job_title=info["job_title"],
            skills=", ".join(info["required_skills"]) or "none listed",
            job_description=state["job_description"],
        ),
    )
    return {"classification": result.model_dump()}
