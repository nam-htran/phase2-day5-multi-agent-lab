"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer` based on notes."""
        from multi_agent_research_lab.observability.tracing import trace_span
        with trace_span("writer_agent", {"query": state.request.query}):
            llm = LLMClient()
            system_prompt = (
                "You are an expert Writer. Synthesize the provided research notes "
                "and analysis notes into a clear, comprehensive final answer. "
                "Always cite sources and use a professional tone."
            )
            
            user_prompt = (
                f"Query: {state.request.query}\n\n"
                f"Research Notes:\n{state.research_notes or 'None'}\n\n"
                f"Analysis Notes:\n{state.analysis_notes or 'None'}\n\n"
                "Please write the final comprehensive response."
            )
            
            response = llm.complete(system_prompt, user_prompt)
            state.final_answer = response.content
            
            state.agent_results.append(AgentResult(
                agent=self.name,
                content=response.content
            ))
            
            return state
