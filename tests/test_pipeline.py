"""Offline tests: the LLM is replaced with a fake so no API key is needed."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exceptions import AnalysisError, InvalidInputError  # noqa: E402
from graph import run_analysis  # noqa: E402
from schemas import JobClassification, JobInfo, SkillAnalysis  # noqa: E402
from utils.validators import validate_job_description  # noqa: E402

SAMPLE = (Path(__file__).resolve().parents[1] / "samples" / "sample_job.txt").read_text()

RESPONSES = {
    JobInfo: lambda: JobInfo(
        job_title="AI Engineer",
        company_name="ABC Technologies",
        required_experience="2-4 Years",
        required_skills=["Python", "FastAPI", "LangGraph", "SQL"],
    ),
    JobClassification: lambda: JobClassification(
        job_category="artificial intelligence", employment_type="full time", work_mode="On-site"
    ),
    SkillAnalysis: lambda: SkillAnalysis(
        technical_skills=["Python", "FastAPI", "LangGraph", "SQL"],
        soft_skills=["Communication", "Teamwork", "Problem Solving"],
        top_3_skills=["Python", "LangGraph", "FastAPI", "SQL"],
    ),
}


class _Runnable:
    def __init__(self, schema, fail=False):
        self.schema, self.fail = schema, fail

    def invoke(self, _messages):
        if self.fail:
            raise RuntimeError("boom")
        return RESPONSES[self.schema]()


class _FakeLLM:
    def __init__(self, fail=False):
        self.fail = fail

    def with_structured_output(self, schema):
        return _Runnable(schema, self.fail)


def test_full_workflow_matches_expected_report(monkeypatch):
    monkeypatch.setattr("nodes.base.get_llm", lambda: _FakeLLM())
    report = run_analysis(SAMPLE)

    assert report.job_title == "AI Engineer"
    assert report.company == "ABC Technologies"
    assert report.experience == "2-4 Years"
    assert report.job_category == "Artificial Intelligence"
    assert report.employment_type == "Full-time"
    assert report.top_3_skills == ["Python", "LangGraph", "FastAPI"]
    assert report.soft_skills == ["Communication", "Teamwork", "Problem Solving"]


def test_llm_failure_is_reported_not_crashed(monkeypatch):
    monkeypatch.setattr("nodes.base.get_llm", lambda: _FakeLLM(fail=True))
    monkeypatch.setattr("nodes.base.time.sleep", lambda _s: None)
    with pytest.raises(AnalysisError):
        run_analysis(SAMPLE)


@pytest.mark.parametrize("bad", ["", "   ", None, "hi there", "12345 67890 !!!! ???? 1111 2222 3333 4444"])
def test_invalid_input_rejected(bad):
    with pytest.raises(InvalidInputError):
        validate_job_description(bad)


def test_valid_input_passes():
    assert validate_job_description(SAMPLE).startswith("AI Engineer")
