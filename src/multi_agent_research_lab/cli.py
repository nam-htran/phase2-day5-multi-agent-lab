"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    llm = LLMClient()
    response = llm.complete(
        system_prompt="You are a helpful AI assistant.",
        user_prompt=query
    )
    state.final_answer = response.content
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


@app.command("benchmark")
def benchmark(
    queries: Annotated[str, typer.Option("--queries", "-q", help="Research queries, separated by semicolon")] = "Multi-Agent vs Single-Agent khác nhau thế nào?",
) -> None:
    """Run benchmark comparing single-agent vs multi-agent."""
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    from multi_agent_research_lab.evaluation.report import render_markdown_report
    from pathlib import Path

    _init()
    query_list = [q.strip() for q in queries.split(";") if q.strip()]
    metrics = []

    # Single-agent runner
    def baseline_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        llm = LLMClient()
        response = llm.complete("You are a helpful AI assistant. Answer in Vietnamese.", q)
        state.final_answer = response.content
        return state

    # Multi-agent runner
    def workflow_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        return workflow.run(state)

    for i, q in enumerate(query_list):
        console.print(f"Benchmarking query {i+1}/{len(query_list)}: {q}")
        
        # Baseline
        console.print("- Running Single-Agent Baseline...")
        _, bl_metrics = run_benchmark(f"Baseline (Q{i+1})", q, baseline_runner)
        metrics.append(bl_metrics)
        
        # Multi-agent
        console.print("- Running Multi-Agent Workflow...")
        _, ma_metrics = run_benchmark(f"Multi-Agent (Q{i+1})", q, workflow_runner)
        metrics.append(ma_metrics)

    report_md = render_markdown_report(metrics)
    
    # Write to file
    out_dir = Path("reports")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "benchmark_report.md"
    out_file.write_text(report_md, encoding="utf-8")
    
    console.print(f"\n[bold green]Benchmark completed! Report saved to {out_file}[/bold green]")


if __name__ == "__main__":
    app()
