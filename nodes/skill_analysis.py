"""Node 3 - Skill Analysis: technical skills, soft skills and the top 3 skills."""

from __future__ import annotations

from nodes.base import run_structured, safe_node
from prompts import SKILL_SYSTEM, SKILL_USER
from schemas import SkillAnalysis
from state import AnalyzerState


@safe_node("Skill Analysis")
def analyze_skills(state: AnalyzerState) -> dict:
    info = state["job_info"]
    classification = state["classification"]
    result = run_structured(
        SkillAnalysis,
        SKILL_SYSTEM,
        SKILL_USER.format(
            job_title=info["job_title"],
            job_category=classification["job_category"],
            skills=", ".join(info["required_skills"]) or "none listed",
            job_description=state["job_description"],
        ),
    )
    return {"skill_analysis": result.model_dump()}
