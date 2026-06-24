"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency, cost, and quality."""
    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    total_cost = 0.0
    for res in state.agent_results:
        # Simplistic mock cost calculation
        length = len(res.content)
        total_cost += (length / 4.0) * 0.00001
        
    llm = LLMClient()
    eval_prompt = (
        f"Query: {query}\nAnswer: {state.final_answer or 'No answer'}\n\n"
        "Score the quality of the answer from 0 to 10 based on relevance, clarity, and citations. "
        "Only output a single floating point number."
    )
    score_response = llm.complete("You are an expert Evaluator.", eval_prompt)
    try:
        # Try to parse the first word as a float
        quality_score = float(score_response.content.strip().split()[0])
        # Clamp between 0 and 10
        quality_score = max(0.0, min(10.0, quality_score))
    except (ValueError, IndexError):
        quality_score = 5.0
        
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        quality_score=quality_score,
        notes="Evaluated by LLM Judge"
    )
    return state, metrics
