"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""
    lines = [
        "# Benchmark Report", 
        "", 
        "This report compares the performance of the single-agent baseline vs the multi-agent workflow.",
        "",
        "## Metrics Table",
        "",
        "| Run | Latency (s) | Estimated Cost (USD) | Quality Score (0-10) | Notes |", 
        "|---|---:|---:|---:|---|"
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}/10"
        lines.append(f"| **{item.run_name}** | {item.latency_seconds:.2f}s | {cost} | {quality} | {item.notes} |")
        
    lines.append("")
    lines.append("## Analysis")
    lines.append("The Multi-Agent system should theoretically have higher latency but better quality due to specialized roles and fact-checking. Check the Langfuse dashboard for detailed traces.")
    lines.append("")
    return "\n".join(lines) + "\n"
