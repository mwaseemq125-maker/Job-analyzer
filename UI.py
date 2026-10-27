"""Streamlit UI for the AI Job Description Analyzer.

Run with:  streamlit run UI.py
"""

from __future__ import annotations

import os

import streamlit as st

import config
import ui_components as ui
from exceptions import AnalyzerError
from graph import stream_analysis
from schemas import HiringReport
from utils.exporter import default_filename, report_to_json

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(ui.CSS, unsafe_allow_html=True)

NODES = list(config.NODE_LABELS.items())  # [(key, label), ...] in workflow order


# ----------------------------------------------------------------------------
# Callbacks
# ----------------------------------------------------------------------------
def load_sample() -> None:
    try:
        st.session_state["jd_input"] = config.SAMPLE_FILE.read_text(encoding="utf-8")
    except OSError:
        st.session_state["jd_input"] = ""


def clear_all() -> None:
    st.session_state["jd_input"] = ""
    st.session_state.pop("report", None)
    st.session_state["done_nodes"] = set()


# ----------------------------------------------------------------------------
# Result rendering
# ----------------------------------------------------------------------------
def render_report(report: HiringReport) -> None:
    st.markdown('<div class="sec">📊 Your Hiring Report</div>', unsafe_allow_html=True)
    tab_overview, tab_skills, tab_export = st.tabs(["📊 Overview", "🛠️ Skills", "💾 Export"])

    with tab_overview:
        st.markdown(ui.job_card_html(report), unsafe_allow_html=True)
        st.markdown(ui.summary_html(report), unsafe_allow_html=True)
        st.markdown(ui.stats_html(report), unsafe_allow_html=True)

        st.markdown(
            '<div class="sec">🏆 Top 3 Most Important Skills'
            "<small>learn these first!</small></div>",
            unsafe_allow_html=True,
        )
        st.markdown(ui.podium_html(report.top_3_skills), unsafe_allow_html=True)

        st.markdown('<div class="sec">📋 Job Details</div>', unsafe_allow_html=True)
        st.markdown(ui.details_html(report), unsafe_allow_html=True)

    with tab_skills:
        st.markdown(
            '<div class="legend">⭐ = one of the top 3 most important skills</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            ui.skill_panel_html(
                "📌 Required Skills", "Skills the job posting asks for directly",
                report.required_skills, "blue", report.top_3_skills,
            ),
            unsafe_allow_html=True,
        )
        left, right = st.columns(2)
        with left:
            st.markdown(
                ui.skill_panel_html(
                    "💻 Technical Skills", "Tools, languages and technologies",
                    report.technical_skills, "green", report.top_3_skills,
                ),
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                ui.skill_panel_html(
                    "🤝 Soft Skills", "People and work-style skills",
                    report.soft_skills, "pink", report.top_3_skills,
                ),
                unsafe_allow_html=True,
            )

    with tab_export:
        st.markdown(
            '<div class="legend">Download the full report as a JSON file, '
            "or copy the data below.</div>",
            unsafe_allow_html=True,
        )
        st.download_button(
            "⬇️ Download JSON report",
            data=report_to_json(report),
            file_name=default_filename(report),
            mime="application/json",
            type="primary",
        )
        st.json(report.model_dump(), expanded=False)


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    provider = st.selectbox(
        "LLM provider",
        config.SUPPORTED_PROVIDERS,
        index=config.SUPPORTED_PROVIDERS.index(config.get_provider()),
        format_func=lambda p: {"gemini": "✨ Google Gemini", "groq": "⚡ Groq"}[p],
    )
    model = st.text_input("Model", value=config.get_model(provider), key=f"model_{provider}")

    env_name = config.API_KEY_ENV[provider]
    has_env_key = bool(os.getenv(env_name))
    api_key = st.text_input(
        env_name,
        type="password",
        placeholder="Loaded from .env" if has_env_key else "Paste your API key",
        help="Leave blank to use the key from your .env file.",
    )

    os.environ["LLM_PROVIDER"] = provider
    os.environ[f"{provider.upper()}_MODEL"] = model
    if api_key:
        os.environ[env_name] = api_key

    if config.get_api_key(provider):
        st.success("API key ready", icon="✅")
    else:
        st.warning("No API key found", icon="⚠️")

    st.divider()
    st.markdown("### 🧭 How to use")
    st.markdown(
        "1. Paste a job description\n"
        "2. Click **Analyze Job**\n"
        "3. Read the report & download it"
    )
    st.caption("Built with LangGraph · Pydantic · Streamlit")


# ----------------------------------------------------------------------------
# Main page
# ----------------------------------------------------------------------------
st.markdown(ui.hero_html(config.APP_NAME, config.APP_TAGLINE), unsafe_allow_html=True)

st.session_state.setdefault("done_nodes", set())
flow_slot = st.empty()
flow_slot.markdown(
    ui.flow_html(NODES, st.session_state["done_nodes"], None), unsafe_allow_html=True
)

st.markdown('<div class="step-title"><span>1</span>Paste the job description</div>',
            unsafe_allow_html=True)
st.text_area(
    "Job description",
    key="jd_input",
    height=260,
    placeholder="Paste a full job posting here... (or click 'Load sample' to try an example)",
    label_visibility="collapsed",
)

b1, b2, b3, _ = st.columns([1.4, 1.2, 1, 3])
analyze = b1.button("🚀 Analyze Job", type="primary", use_container_width=True)
b2.button("📄 Load sample", on_click=load_sample, use_container_width=True)
b3.button("🗑️ Clear", on_click=clear_all, use_container_width=True)

if analyze:
    st.session_state.pop("report", None)
    done: set[str] = set()
    st.session_state["done_nodes"] = done
    flow_slot.markdown(ui.flow_html(NODES, done, NODES[0][0]), unsafe_allow_html=True)

    try:
        report_data: dict | None = None
        for node_name, delta in stream_analysis(st.session_state.get("jd_input", "")):
            if delta.get("error"):
                raise AnalyzerError(delta["error"])
            done.add(node_name)
            keys = [k for k, _ in NODES]
            idx = keys.index(node_name) + 1
            nxt = keys[idx] if idx < len(keys) else None
            flow_slot.markdown(ui.flow_html(NODES, done, nxt), unsafe_allow_html=True)
            if "report" in delta:
                report_data = delta["report"]

        if report_data is None:
            raise AnalyzerError("The workflow finished without producing a report.")
        st.session_state["report"] = HiringReport.model_validate(report_data)
    except AnalyzerError as exc:
        flow_slot.markdown(ui.flow_html(NODES, done, None), unsafe_allow_html=True)
        st.error(str(exc), icon="🚫")

if "report" in st.session_state:
    render_report(st.session_state["report"])
