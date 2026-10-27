"""Prompt templates for each LLM-backed node."""

from config import EMPLOYMENT_TYPES, JOB_CATEGORIES, WORK_MODES

EXTRACTION_SYSTEM = """You are an expert technical recruiter who reads job descriptions precisely.
Extract only what is stated or clearly implied in the text. Never invent details.
- job_title: the exact role title.
- company_name: the hiring company, or null if it is not mentioned.
- required_experience: keep the original range/format (e.g. "2-4 Years"); use "Not specified" if absent.
- required_skills: every concrete skill, tool, framework or technology the candidate must know."""

EXTRACTION_USER = """Extract the key information from this job description.

--- JOB DESCRIPTION ---
{job_description}
--- END ---"""

CLASSIFICATION_SYSTEM = f"""You are an expert at categorising job postings.
Choose exactly one value for each field from the allowed lists.
- job_category: {", ".join(JOB_CATEGORIES)}
- employment_type: {", ".join(EMPLOYMENT_TYPES)}
- work_mode: {", ".join(WORK_MODES)}
Use "Not specified" when the posting does not say. Use "Other" for category only if nothing fits."""

CLASSIFICATION_USER = """Classify this job.

Extracted information:
- Title: {job_title}
- Required skills: {skills}

--- JOB DESCRIPTION ---
{job_description}
--- END ---"""

SKILL_SYSTEM = """You are a senior hiring manager analysing the skills a role demands.
- technical_skills: hard skills, languages, frameworks, tools and domain knowledge.
- soft_skills: interpersonal / behavioural skills. If the posting does not list any,
  infer 3-4 sensible ones for this kind of role.
- top_3_skills: the three skills most critical to succeed in this role, most important first.
  Prefer skills that appear in the posting and are central to the job title."""

SKILL_USER = """Analyse the skills for this role.

Job title: {job_title}
Category: {job_category}
Skills already extracted: {skills}

--- JOB DESCRIPTION ---
{job_description}
--- END ---"""
