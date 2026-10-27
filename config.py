"""Central configuration for the AI Job Description Analyzer."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
SAMPLE_FILE = BASE_DIR / "samples" / "sample_job.txt"

APP_NAME = "AI Job Description Analyzer"
APP_TAGLINE = "Turn any job posting into a structured hiring report - powered by LangGraph"

# ----------------------------------------------------------------------------
# LLM providers
# ----------------------------------------------------------------------------
SUPPORTED_PROVIDERS = ("gemini", "groq")

DEFAULT_MODELS = {
    "gemini": "gemini-3.8-flash",
    "groq": "llama-3.3-70b-versatile",
}

API_KEY_ENV = {
    "gemini": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
}


def get_provider() -> str:
    """Return the active LLM provider (read at call time so the UI can change it)."""
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    return provider if provider in SUPPORTED_PROVIDERS else "gemini"


def get_model(provider: str | None = None) -> str:
    """Return the model name for a provider, overridable via <PROVIDER>_MODEL."""
    provider = provider or get_provider()
    return os.getenv(f"{provider.upper()}_MODEL", DEFAULT_MODELS[provider])


def get_api_key(provider: str | None = None) -> str | None:
    provider = provider or get_provider()
    return os.getenv(API_KEY_ENV[provider]) or None


# ----------------------------------------------------------------------------
# Classification vocabularies
# ----------------------------------------------------------------------------
JOB_CATEGORIES = [
    "Artificial Intelligence",
    "Data Science",
    "Data Engineering",
    "Web Development",
    "Mobile Development",
    "DevOps / Cloud",
    "Cybersecurity",
    "Software Engineering",
    "UI/UX Design",
    "QA / Testing",
    "Other",
]

EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Internship", "Contract", "Not specified"]
WORK_MODES = ["Remote", "Hybrid", "On-site", "Not specified"]

# ----------------------------------------------------------------------------
# Input validation limits
# ----------------------------------------------------------------------------
MIN_WORDS = 8
MAX_CHARS = 12_000
MIN_ALPHA_RATIO = 0.4

# ----------------------------------------------------------------------------
# Workflow metadata (used by the UI / CLI for progress display)
# ----------------------------------------------------------------------------
NODE_LABELS = {
    "information_extraction": "Information Extraction",
    "job_classification": "Job Classification",
    "skill_analysis": "Skill Analysis",
    "hiring_report": "Hiring Report",
}
