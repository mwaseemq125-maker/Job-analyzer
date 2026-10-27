"""Presentation layer helpers for the Streamlit UI (pure Python - no Streamlit import)."""

from __future__ import annotations

import html
from typing import Iterable

from schemas import HiringReport

NODE_ICONS = {
    "information_extraction": "🔍",
    "job_classification": "🏷️",
    "skill_analysis": "🧩",
    "hiring_report": "📑",
}

NOT_SPECIFIED = "Not specified"

# ----------------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, .stApp, .stMarkdown, .stTextArea textarea, .stButton button,
.stTabs button, label, .stSelectbox, .stTextInput input { font-family: 'Poppins', sans-serif; }

.stApp {
    background-image:
        radial-gradient(1100px 520px at 8% -8%, rgba(99,102,241,.20), transparent 60%),
        radial-gradient(900px 480px at 100% 0%, rgba(236,72,153,.16), transparent 55%),
        radial-gradient(800px 500px at 50% 110%, rgba(20,184,166,.12), transparent 60%);
}
.block-container { padding-top: 1.6rem; max-width: 1150px; }
#MainMenu, footer, [data-testid="stAppDeployButton"], .stDeployButton { display: none !important; }

/* ---------- Hero ---------- */
.hero {
    position: relative; overflow: hidden; border-radius: 26px; padding: 2.4rem 2.6rem; color: #fff;
    margin-bottom: 1.4rem;
    background: linear-gradient(120deg, #4f46e5, #7c3aed, #db2777, #f59e0b);
    background-size: 300% 300%; animation: shift 12s ease infinite;
    box-shadow: 0 18px 44px rgba(124,58,237,.38);
}
.hero::after {
    content: "🧠"; position: absolute; right: 2rem; top: 50%; transform: translateY(-50%);
    font-size: 6.5rem; opacity: .22;
}
.hero h1 { margin: 0; padding: 0; font-size: 2.4rem; font-weight: 800; color: #fff; letter-spacing: -.5px; }
.hero p  { margin: .6rem 0 0; font-size: 1.05rem; color: rgba(255,255,255,.93); max-width: 640px; }
.hero .chips span {
    display: inline-block; background: rgba(255,255,255,.22); padding: .28rem .85rem;
    border-radius: 999px; font-size: .78rem; font-weight: 600; margin: 1rem .45rem 0 0;
}
@keyframes shift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }

/* ---------- Workflow progress ---------- */
.flow { display: flex; gap: .7rem; margin: .2rem 0 1.6rem; flex-wrap: wrap; }
.fstep {
    flex: 1; min-width: 190px; display: flex; gap: .8rem; align-items: center; border-radius: 18px;
    padding: .9rem 1rem; border: 1px solid rgba(148,163,184,.28); background: rgba(148,163,184,.08);
    transition: all .3s;
}
.fstep .ic {
    font-size: 1.45rem; width: 46px; height: 46px; border-radius: 14px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; background: rgba(148,163,184,.2);
}
.fstep small { display: block; font-size: .66rem; letter-spacing: 1.3px; opacity: .6; font-weight: 700; }
.fstep b { font-size: .92rem; font-weight: 600; }
.fstep.active { border-color: #f59e0b; background: rgba(245,158,11,.13); animation: pulse 1.2s infinite; }
.fstep.active .ic { background: linear-gradient(135deg,#f59e0b,#ef4444); }
.fstep.done { border-color: rgba(34,197,94,.6); background: rgba(34,197,94,.11); }
.fstep.done .ic { background: linear-gradient(135deg,#22c55e,#14b8a6); }
@keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(245,158,11,.5)} 50%{box-shadow:0 0 0 9px rgba(245,158,11,0)} }

/* ---------- Section headings ---------- */
.step-title { font-size: 1.1rem; font-weight: 700; margin: .2rem 0 .5rem; }
.step-title span {
    display: inline-flex; width: 28px; height: 28px; border-radius: 50%; margin-right: .5rem;
    align-items: center; justify-content: center; font-size: .85rem; color: #fff;
    background: linear-gradient(135deg,#6366f1,#ec4899);
}
.sec { font-size: 1.18rem; font-weight: 700; margin: 1.7rem 0 .8rem; }
.sec small { font-weight: 500; opacity: .6; font-size: .8rem; margin-left: .4rem; }

/* ---------- Buttons / inputs ---------- */
button[kind="primary"], [data-testid="stBaseButton-primary"] {
    background: linear-gradient(120deg,#6366f1,#ec4899) !important; border: 0 !important;
    font-weight: 700 !important; border-radius: 12px !important;
    box-shadow: 0 8px 20px rgba(236,72,153,.35);
}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover { filter: brightness(1.1); transform: translateY(-1px); }
.stTextArea textarea { border-radius: 14px; }
.stTabs [data-baseweb="tab-list"] { gap: .4rem; }
.stTabs [data-baseweb="tab"] { font-weight: 600; font-size: 1rem; padding: .6rem 1.1rem; border-radius: 12px 12px 0 0; }

/* ---------- Result: job card ---------- */
.job-card {
    display: flex; gap: 1.3rem; align-items: center; border-radius: 24px; padding: 1.6rem 1.8rem;
    background: linear-gradient(135deg, rgba(99,102,241,.25), rgba(236,72,153,.18));
    border: 1px solid rgba(139,92,246,.45); box-shadow: 0 14px 34px rgba(99,102,241,.2);
}
.avatar {
    width: 72px; height: 72px; border-radius: 20px; flex-shrink: 0; color: #fff; font-size: 2.1rem;
    font-weight: 800; display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg,#6366f1,#ec4899);
}
.job-title { font-size: 1.75rem; font-weight: 800; line-height: 1.2; }
.job-company { opacity: .82; margin: .2rem 0 .7rem; font-weight: 500; }
.pill {
    display: inline-block; padding: .32rem .9rem; border-radius: 999px; font-size: .82rem; font-weight: 600;
    margin: .15rem .4rem .15rem 0; border: 1px solid;
}
.p-violet { background: rgba(139,92,246,.2); color: #c4b5fd; border-color: rgba(139,92,246,.55); }
.p-green  { background: rgba(34,197,94,.18);  color: #86efac; border-color: rgba(34,197,94,.5); }
.p-sky    { background: rgba(14,165,233,.18); color: #7dd3fc; border-color: rgba(14,165,233,.5); }
.p-orange { background: rgba(245,158,11,.2);  color: #fcd34d; border-color: rgba(245,158,11,.55); }

/* ---------- Summary ---------- */
.summary {
    margin: 1.2rem 0; padding: 1.1rem 1.4rem; border-radius: 18px; line-height: 1.7; font-size: 1rem;
    border-left: 6px solid #f59e0b; background: rgba(245,158,11,.11);
}
.summary .t { display: block; font-size: .72rem; letter-spacing: 1.3px; color: #f59e0b; font-weight: 700; margin-bottom: .3rem; }

/* ---------- Stat tiles ---------- */
.stats { display: grid; grid-template-columns: repeat(4,1fr); gap: .9rem; margin: 1rem 0; }
.stat { border-radius: 20px; padding: 1.1rem 1.2rem; color: #fff; box-shadow: 0 8px 20px rgba(0,0,0,.18); }
.stat .n { font-size: 2.1rem; font-weight: 800; line-height: 1; }
.stat .l { font-size: .82rem; opacity: .95; margin-top: .4rem; font-weight: 500; }
.g-violet { background: linear-gradient(135deg,#6366f1,#8b5cf6); }
.g-green  { background: linear-gradient(135deg,#10b981,#14b8a6); }
.g-pink   { background: linear-gradient(135deg,#ec4899,#f43f5e); }
.g-orange { background: linear-gradient(135deg,#f59e0b,#f97316); }

/* ---------- Top 3 podium ---------- */
.podium { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; }
.medal { border-radius: 22px; padding: 1.4rem 1rem; text-align: center; border: 1px solid; }
.medal .m { font-size: 2.6rem; line-height: 1; }
.medal .s { font-size: 1.25rem; font-weight: 700; margin-top: .5rem; }
.medal .r { font-size: .7rem; letter-spacing: 1.2px; text-transform: uppercase; opacity: .75; margin-top: .25rem; font-weight: 600; }
.m1 { background: linear-gradient(160deg,rgba(251,191,36,.3),rgba(245,158,11,.06)); border-color: rgba(251,191,36,.65); }
.m2 { background: linear-gradient(160deg,rgba(203,213,225,.26),rgba(148,163,184,.05)); border-color: rgba(203,213,225,.55); }
.m3 { background: linear-gradient(160deg,rgba(251,146,60,.26),rgba(234,88,12,.05)); border-color: rgba(251,146,60,.55); }

/* ---------- Detail grid ---------- */
.details { display: grid; grid-template-columns: repeat(3,1fr); gap: .9rem; }
.d { border-radius: 16px; padding: .9rem 1.1rem; background: rgba(148,163,184,.1); border: 1px solid rgba(148,163,184,.25); }
.d .k { font-size: .68rem; text-transform: uppercase; letter-spacing: 1.1px; opacity: .65; font-weight: 600; }
.d .v { font-weight: 600; margin-top: .25rem; }

/* ---------- Skill panels & tags ---------- */
.panel { border-radius: 20px; padding: 1.2rem 1.3rem; border: 1px solid; margin-bottom: 1.1rem; }
.panel-title { font-weight: 700; font-size: 1.05rem; margin-bottom: .2rem; display: flex; justify-content: space-between; align-items: center; }
.panel-sub { font-size: .8rem; opacity: .65; margin-bottom: .7rem; }
.count { font-size: .78rem; padding: .15rem .65rem; border-radius: 999px; background: rgba(255,255,255,.14); }
.panel-blue  { border-color: rgba(14,165,233,.5);  background: rgba(14,165,233,.08); }
.panel-green { border-color: rgba(34,197,94,.5);   background: rgba(34,197,94,.08); }
.panel-pink  { border-color: rgba(236,72,153,.5);  background: rgba(236,72,153,.08); }
.tag { display: inline-block; padding: .38rem .95rem; margin: .25rem .35rem .25rem 0; border-radius: 999px; font-size: .86rem; font-weight: 600; }
.tag-blue  { background: rgba(14,165,233,.2);  color: #7dd3fc; border: 1px solid rgba(14,165,233,.5); }
.tag-green { background: rgba(34,197,94,.2);   color: #86efac; border: 1px solid rgba(34,197,94,.5); }
.tag-pink  { background: rgba(236,72,153,.2);  color: #f9a8d4; border: 1px solid rgba(236,72,153,.5); }
.tag.star  { box-shadow: 0 0 0 2px rgba(251,191,36,.85); }
.legend { font-size: .82rem; opacity: .7; margin-bottom: .8rem; }

@media (max-width: 820px) {
    .stats { grid-template-columns: repeat(2,1fr); }
    .podium, .details { grid-template-columns: 1fr; }
    .job-card { flex-direction: column; text-align: center; }
    .hero::after { display: none; }
}
</style>
"""


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------
def _e(text: object) -> str:
    return html.escape(str(text))


def join_natural(items: Iterable[str]) -> str:
    """['a','b','c'] -> 'a, b and c'."""
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def plain_summary(report: HiringReport) -> str:
    """A friendly 2-3 sentence explanation of the report (no LLM needed)."""
    company = report.company if report.company != NOT_SPECIFIED else "A company"
    article = "an" if report.job_title[:1].lower() in "aeiou" else "a"

    parts = [f"{company} is hiring {article} <b>{_e(report.job_title)}</b>"]
    if report.job_category not in ("Other", NOT_SPECIFIED):
        parts[0] += f" in the <b>{_e(report.job_category)}</b> field"
    parts[0] += "."

    details = []
    if report.employment_type != NOT_SPECIFIED:
        details.append(report.employment_type.lower())
    if report.work_mode != NOT_SPECIFIED:
        details.append(report.work_mode.lower())
    if details:
        parts.append(f"It is a <b>{_e(' / '.join(details))}</b> job.")
    if report.experience != NOT_SPECIFIED:
        parts.append(f"They are looking for <b>{_e(report.experience)}</b> of experience.")
    if report.top_3_skills:
        parts.append(
            f"The most important skills to get this job are <b>{_e(join_natural(report.top_3_skills))}</b>."
        )
    return " ".join(parts)


# ----------------------------------------------------------------------------
# HTML builders
# ----------------------------------------------------------------------------
def hero_html(title: str, tagline: str) -> str:
    return (
        f'<div class="hero"><h1>{_e(title)}</h1><p>{_e(tagline)}</p>'
        '<div class="chips"><span>⚡ LangGraph</span><span>✨ Gemini / Groq</span>'
        "<span>🧱 Pydantic</span><span>📊 Streamlit</span></div></div>"
    )


def flow_html(nodes: list[tuple[str, str]], done: set[str], active: str | None) -> str:
    """Workflow progress cards: pending / active (pulsing) / done."""
    cards = []
    for i, (key, label) in enumerate(nodes, 1):
        state = "done" if key in done else "active" if key == active else ""
        icon = "✅" if key in done else NODE_ICONS.get(key, "•")
        cards.append(
            f'<div class="fstep {state}"><div class="ic">{icon}</div>'
            f"<div><small>STEP {i}</small><b>{_e(label)}</b></div></div>"
        )
    return f'<div class="flow">{"".join(cards)}</div>'


def pill(text: str, css: str) -> str:
    return f'<span class="pill {css}">{_e(text)}</span>'


def job_card_html(r: HiringReport) -> str:
    seed = r.company if r.company != NOT_SPECIFIED else r.job_title
    pills = [pill(f"🗂️ {r.job_category}", "p-violet")]
    if r.employment_type != NOT_SPECIFIED:
        pills.append(pill(f"💼 {r.employment_type}", "p-green"))
    if r.work_mode != NOT_SPECIFIED:
        pills.append(pill(f"📍 {r.work_mode}", "p-sky"))
    if r.experience != NOT_SPECIFIED:
        pills.append(pill(f"⏳ {r.experience}", "p-orange"))
    return (
        f'<div class="job-card"><div class="avatar">{_e(seed[:1].upper())}</div><div>'
        f'<div class="job-title">{_e(r.job_title)}</div>'
        f'<div class="job-company">🏢 {_e(r.company)}</div>'
        f'<div>{"".join(pills)}</div></div></div>'
    )


def summary_html(r: HiringReport) -> str:
    return f'<div class="summary"><span class="t">📝 IN SIMPLE WORDS</span>{plain_summary(r)}</div>'


def stats_html(r: HiringReport) -> str:
    tiles = [
        (len(r.required_skills), "Skills required", "g-violet"),
        (len(r.technical_skills), "Technical skills", "g-green"),
        (len(r.soft_skills), "Soft skills", "g-pink"),
        (len(r.top_3_skills), "Top priority skills", "g-orange"),
    ]
    inner = "".join(
        f'<div class="stat {css}"><div class="n">{n}</div><div class="l">{_e(label)}</div></div>'
        for n, label, css in tiles
    )
    return f'<div class="stats">{inner}</div>'


def podium_html(skills: list[str]) -> str:
    medals = [("🥇", "m1", "Must-have"), ("🥈", "m2", "Very important"), ("🥉", "m3", "Important")]
    cards = "".join(
        f'<div class="medal {css}"><div class="m">{icon}</div>'
        f'<div class="s">{_e(skill)}</div><div class="r">{_e(rank)}</div></div>'
        for (icon, css, rank), skill in zip(medals, skills)
    )
    return f'<div class="podium">{cards}</div>'


def details_html(r: HiringReport) -> str:
    rows = [
        ("🏢 Company", r.company),
        ("⏳ Experience", r.experience),
        ("🗂️ Job category", r.job_category),
        ("💼 Employment type", r.employment_type),
        ("📍 Work mode", r.work_mode),
        ("🕒 Report created", r.generated_at),
    ]
    inner = "".join(
        f'<div class="d"><div class="k">{_e(k)}</div><div class="v">{_e(v)}</div></div>'
        for k, v in rows
    )
    return f'<div class="details">{inner}</div>'


def skill_panel_html(
    title: str, subtitle: str, skills: list[str], color: str, highlight: Iterable[str] = ()
) -> str:
    starred = {h.lower() for h in highlight}
    if skills:
        tags = "".join(
            f'<span class="tag tag-{color}{" star" if s.lower() in starred else ""}">'
            f'{"⭐ " if s.lower() in starred else ""}{_e(s)}</span>'
            for s in skills
        )
    else:
        tags = '<span style="opacity:.6">Nothing found</span>'
    return (
        f'<div class="panel panel-{color}"><div class="panel-title"><span>{title}</span>'
        f'<span class="count">{len(skills)}</span></div>'
        f'<div class="panel-sub">{_e(subtitle)}</div>{tags}</div>'
    )
