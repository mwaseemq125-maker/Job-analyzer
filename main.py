"""Command-line entry point for the AI Job Description Analyzer.

Examples
--------
    python main.py --file samples/sample_job.txt
    python main.py --file samples/sample_job.txt --export
    python main.py --provider groq --text "We are hiring a Python developer ..."
    python main.py                      # interactive: paste a JD, finish with END
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import config
from exceptions import AnalyzerError
from graph import stream_analysis
from schemas import HiringReport
from utils.exporter import export_report_json

console = Console()


# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------
def _tags(skills: list[str], style: str) -> Columns:
    return Columns(
        [Text(f" {s} ", style=style) for s in skills] or [Text("-", style="dim")],
        padding=(0, 1),
    )


def render_report(report: HiringReport) -> None:
    """Pretty-print the structured hiring report."""
    console.print()
    console.print(
        Panel.fit(
            Text(f"{report.job_title}", style="bold white", justify="center"),
            title="[bold cyan]STRUCTURED HIRING REPORT[/]",
            subtitle=f"[dim]{report.generated_at}[/]",
            border_style="cyan",
            padding=(1, 6),
        )
    )

    overview = Table(box=box.ROUNDED, show_header=False, border_style="bright_black", expand=True)
    overview.add_column("Field", style="bold cyan", width=20)
    overview.add_column("Value")
    overview.add_row("Job Title", report.job_title)
    overview.add_row("Company", report.company)
    overview.add_row("Experience", report.experience)
    overview.add_row("Job Category", report.job_category)
    overview.add_row("Employment Type", report.employment_type)
    overview.add_row("Work Mode", report.work_mode)
    console.print(overview)

    console.print(Panel(_tags(report.required_skills, "bold black on bright_cyan"),
                        title="Required Skills", border_style="cyan", title_align="left"))
    console.print(Panel(_tags(report.technical_skills, "bold black on bright_green"),
                        title="Technical Skills", border_style="green", title_align="left"))
    console.print(Panel(_tags(report.soft_skills, "bold black on bright_magenta"),
                        title="Soft Skills", border_style="magenta", title_align="left"))

    top = Table(box=box.SIMPLE_HEAVY, show_header=False, expand=True)
    top.add_column("Rank", style="bold yellow", width=4)
    top.add_column("Skill", style="bold")
    for i, skill in enumerate(report.top_3_skills, 1):
        top.add_row(f"#{i}", skill)
    console.print(Panel(top, title="Top 3 Most Important Skills",
                        border_style="yellow", title_align="left"))


# ----------------------------------------------------------------------------
# Input handling
# ----------------------------------------------------------------------------
def read_interactive() -> str:
    console.print(
        Panel(
            "Paste the job description below.\n"
            "When you're done, type [bold]END[/] on a new line and press Enter.",
            title="AI Job Description Analyzer",
            border_style="cyan",
        )
    )
    lines: list[str] = []
    try:
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a job description and generate a structured hiring report."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("-f", "--file", type=Path, help="Path to a text file with the job description")
    source.add_argument("-t", "--text", help="Job description passed directly as text")
    parser.add_argument("-p", "--provider", choices=config.SUPPORTED_PROVIDERS,
                        help="LLM provider (default: LLM_PROVIDER from .env, else gemini)")
    parser.add_argument("-m", "--model", help="Override the model name")
    parser.add_argument("-e", "--export", nargs="?", const="auto", metavar="PATH",
                        help="Export the report as JSON (default folder: ./outputs/)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logs")
    return parser.parse_args()


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO if args.verbose else logging.ERROR)

    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
    if args.model:
        os.environ[f"{config.get_provider().upper()}_MODEL"] = args.model

    try:
        if args.file:
            if not args.file.exists():
                console.print(f"[red]File not found:[/] {args.file}")
                return 1
            job_description = args.file.read_text(encoding="utf-8")
        elif args.text is not None:
            job_description = args.text
        else:
            job_description = read_interactive()

        provider = config.get_provider()
        console.print(f"\n[dim]Provider: {provider} - Model: {config.get_model(provider)}[/]\n")

        report_data: dict | None = None
        with console.status("[bold cyan]Starting workflow...", spinner="dots") as status:
            for node_name, delta in stream_analysis(job_description):
                label = config.NODE_LABELS.get(node_name, node_name)
                if delta.get("error"):
                    raise AnalyzerError(delta["error"])
                console.print(f"[green]✔[/] {label}")
                status.update(f"[bold cyan]Running next step after {label}...")
                if "report" in delta:
                    report_data = delta["report"]

        if report_data is None:
            raise AnalyzerError("The workflow finished without producing a report.")

        report = HiringReport.model_validate(report_data)
        render_report(report)

        if args.export:
            path = None if args.export == "auto" else args.export
            saved = export_report_json(report, path)
            console.print(f"\n[bold green]Report exported to[/] {saved}\n")
        return 0

    except AnalyzerError as exc:
        console.print(f"\n[bold red]Error:[/] {exc}")
        return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/]")
        return 130


if __name__ == "__main__":
    sys.exit(main())
