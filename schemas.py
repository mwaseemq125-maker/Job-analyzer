"""Pydantic models describing the data produced by each workflow node."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from config import EMPLOYMENT_TYPES, JOB_CATEGORIES, WORK_MODES


def _normalize(value: str, allowed: list[str], default: str) -> str:
    """Map a free-form model answer onto a known label (case-insensitive)."""
    cleaned = (value or "").strip().lower().replace("_", "-")
    for option in allowed:
        if cleaned == option.lower():
            return option
    # Loose containment match, e.g. "Full time" -> "Full-time", "AI" -> AI category
    for option in allowed:
        if option.lower() in cleaned or cleaned.replace(" ", "-") == option.lower():
            return option
    if cleaned in {"ai", "ml", "machine learning", "ai/ml", "genai"} and "Artificial Intelligence" in allowed:
        return "Artificial Intelligence"
    return default


def _dedupe(items: List[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for item in items:
        name = (item or "").strip()
        if name and name.lower() not in seen:
            seen.add(name.lower())
            result.append(name)
    return result


# ---------------------------------------------------------------------------
# Node 1 - Information Extraction
# ---------------------------------------------------------------------------
class JobInfo(BaseModel):
    job_title: str = Field(description="Exact job title, e.g. 'AI Engineer'")
    company_name: Optional[str] = Field(
        default=None, description="Hiring company name, or null if not mentioned"
    )
    required_experience: str = Field(
        default="Not specified", description="Experience needed, e.g. '2-4 Years'"
    )
    required_skills: List[str] = Field(
        default_factory=list, description="Every skill / tool / technology required"
    )

    @field_validator("company_name", mode="before")
    @classmethod
    def _blank_company(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        return None if v.lower() in {"", "n/a", "none", "null", "not specified", "unknown"} else v

    @field_validator("required_experience", mode="before")
    @classmethod
    def _default_experience(cls, v):
        return (str(v).strip() if v else "") or "Not specified"

    @field_validator("required_skills", mode="after")
    @classmethod
    def _clean_skills(cls, v):
        return _dedupe(v)


# ---------------------------------------------------------------------------
# Node 2 - Job Classification
# ---------------------------------------------------------------------------
class JobClassification(BaseModel):
    job_category: str = Field(
        description=f"One of: {', '.join(JOB_CATEGORIES)}"
    )
    employment_type: str = Field(
        description=f"One of: {', '.join(EMPLOYMENT_TYPES)}"
    )
    work_mode: str = Field(
        default="Not specified", description=f"One of: {', '.join(WORK_MODES)}"
    )

    @field_validator("job_category", mode="after")
    @classmethod
    def _category(cls, v):
        return _normalize(v, JOB_CATEGORIES, "Other")

    @field_validator("employment_type", mode="after")
    @classmethod
    def _employment(cls, v):
        return _normalize(v, EMPLOYMENT_TYPES, "Not specified")

    @field_validator("work_mode", mode="after")
    @classmethod
    def _mode(cls, v):
        return _normalize(v, WORK_MODES, "Not specified")


# ---------------------------------------------------------------------------
# Node 3 - Skill Analysis
# ---------------------------------------------------------------------------
class SkillAnalysis(BaseModel):
    technical_skills: List[str] = Field(
        default_factory=list, description="Technical / hard skills for the role"
    )
    soft_skills: List[str] = Field(
        default_factory=list, description="Soft / interpersonal skills for the role"
    )
    top_3_skills: List[str] = Field(
        default_factory=list,
        description="The 3 most important skills for success, most important first",
    )

    @field_validator("technical_skills", "soft_skills", mode="after")
    @classmethod
    def _clean(cls, v):
        return _dedupe(v)

    @field_validator("top_3_skills", mode="after")
    @classmethod
    def _top3(cls, v):
        return _dedupe(v)[:3]


# ---------------------------------------------------------------------------
# Node 4 - Final report
# ---------------------------------------------------------------------------
class HiringReport(BaseModel):
    job_title: str
    company: str
    experience: str
    required_skills: List[str]
    job_category: str
    employment_type: str
    work_mode: str
    technical_skills: List[str]
    soft_skills: List[str]
    top_3_skills: List[str]
    generated_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
