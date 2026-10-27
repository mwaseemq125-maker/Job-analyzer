"""LangGraph workflow: Extraction -> Classification -> Skill Analysis -> Report."""

from __future__ import annotations

from functools import lru_cache
from typing import Iterator, Tuple

from langgraph.graph import END, START, StateGraph

from exceptions import AnalysisError
from nodes import analyze_skills, classify_job, extract_information, generate_report
from schemas import HiringReport
from state import AnalyzerState
from utils.validators import validate_job_description


def _continue_or_end(next_node: str):
    """Conditional edge: stop the workflow as soon as any node reports an error."""

    def router(state: AnalyzerState) -> str:
        return END if state.get("error") else next_node

    return router


@lru_cache(maxsize=1)
def build_graph():
    graph = StateGraph(AnalyzerState)

    graph.add_node("information_extraction", extract_information)
    graph.add_node("job_classification", classify_job)
    graph.add_node("skill_analysis", analyze_skills)
    graph.add_node("hiring_report", generate_report)

    graph.add_edge(START, "information_extraction")
    for current, nxt in [
        ("information_extraction", "job_classification"),
        ("job_classification", "skill_analysis"),
        ("skill_analysis", "hiring_report"),
    ]:
        graph.add_conditional_edges(current, _continue_or_end(nxt), {nxt: nxt, END: END})
    graph.add_edge("hiring_report", END)

    return graph.compile()


def run_analysis(job_description: str) -> HiringReport:
    """Validate the input, run the full workflow and return the final report."""
    text = validate_job_description(job_description)
    result = build_graph().invoke({"job_description": text})
    if result.get("error"):
        raise AnalysisError(result["error"])
    return HiringReport.model_validate(result["report"])


def stream_analysis(job_description: str) -> Iterator[Tuple[str, dict]]:
    """Yield (node_name, state_update) after every node - lets a UI show live progress."""
    text = validate_job_description(job_description)
    for update in build_graph().stream({"job_description": text}, stream_mode="updates"):
        for node_name, delta in update.items():
            yield node_name, delta
