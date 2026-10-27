"""Node 4 - Hiring Report: assemble everything into one structured report."""

from __future__ import annotations

from nodes.base import safe_node
from schemas import HiringReport
from state import AnalyzerState


@safe_node("Hiring Report")
def generate_report(state: AnalyzerState) -> dict:
    info = state["job_info"]
    classification = state["classification"]
    skills = state["skill_analysis"]

    # Guarantee a usable top-3 even if the model returned fewer than 3 skills.
    top_3 = list(skills["top_3_skills"])
    for candidate in skills["technical_skills"] + info["required_skills"]:
        if len(top_3) >= 3:
            break
        if candidate.lower() not in (s.lower() for s in top_3):
            top_3.append(candidate)

    report = HiringReport(
        job_title=info["job_title"],
        company=info["company_name"] or "Not specified",
        experience=info["required_experience"],
        required_skills=info["required_skills"],
        job_category=classification["job_category"],
        employment_type=classification["employment_type"],
        work_mode=classification["work_mode"],
        technical_skills=skills["technical_skills"],
        soft_skills=skills["soft_skills"],
        top_3_skills=top_3[:3],
    )
    return {"report": report.model_dump()}
