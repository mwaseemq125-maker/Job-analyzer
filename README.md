# 🧠 AI Job Description Analyzer

Turn any job description into a **structured hiring report** using a 4-node
**LangGraph** workflow powered by **Gemini** or **Groq**.

## Workflow

```
Job Description
      │
      ▼
Node 1  Information Extraction   → title, company, experience, required skills
      ▼
Node 2  Job Classification       → category, employment type, work mode
      ▼
Node 3  Skill Analysis           → technical skills, soft skills, top 3 skills
      ▼
Node 4  Hiring Report            → final structured report (JSON-exportable)
```

State is passed between nodes through a shared `AnalyzerState`. If any node fails,
the graph stops cleanly and a friendly error is shown.

## Project structure

```
ai-job-description-analyzer/
├── main.py            # CLI entry point (rich terminal output)
├── UI.py              # Streamlit web interface
├── graph.py           # LangGraph workflow definition
├── state.py           # Shared graph state
├── schemas.py         # Pydantic models for every node
├── prompts.py         # Prompt templates
├── config.py          # Settings, providers, vocabularies
├── exceptions.py      # Custom errors
├── nodes/
│   ├── extraction.py      # Node 1
│   ├── classification.py  # Node 2
│   ├── skill_analysis.py  # Node 3
│   ├── report.py          # Node 4
│   └── base.py            # structured-output helper + error handling
├── utils/
│   ├── llm.py         # Gemini / Groq factory
│   ├── validators.py  # input validation
│   └── exporter.py    # JSON export
├── samples/sample_job.txt
├── tests/test_pipeline.py
├── outputs/           # exported reports
├── requirements.txt
└── .env.example
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then add your API key
```

Get a free key: [Gemini](https://aistudio.google.com/apikey) · [Groq](https://console.groq.com/keys)

## Run

**Web UI (Streamlit)**
```bash
streamlit run UI.py
```

**Command line**
```bash
python main.py --file samples/sample_job.txt --export
python main.py --provider groq --file samples/sample_job.txt
python main.py                   # interactive: paste a JD, finish with END
```

## Features

- ✅ All 4 LangGraph nodes with state passed between them
- ✅ Gemini **or** Groq (switch in `.env`, CLI flag, or UI sidebar)
- ✅ Pydantic-validated structured output with automatic retries
- ✅ Graceful handling of empty / invalid input and API failures
- ✅ Streamlit UI with live workflow progress and skills shown as tags
- ✅ Export the report as JSON (UI download button or `--export`)
- ✅ Offline tests with a fake LLM: `pytest -q`

## Example output

```
Job Title:       AI Engineer
Company:         ABC Technologies
Experience:      2-4 Years
Required Skills: Python, FastAPI, LangGraph, SQL
Job Category:    Artificial Intelligence
Employment Type: Full-time
Technical Skills: Python, FastAPI, LangGraph, SQL
Soft Skills:     Communication, Teamwork, Problem Solving
Top 3 Skills:    1. Python  2. LangGraph  3. FastAPI
```

> Model names change over time. If a model is retired, set `GEMINI_MODEL` or
> `GROQ_MODEL` in `.env`.
