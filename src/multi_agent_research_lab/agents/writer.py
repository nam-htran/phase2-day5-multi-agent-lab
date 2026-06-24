"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        if not state.research_notes:
            return state

        llm = LLMClient()
        system_prompt = (
            "You are a Technical Writer. Produce a comprehensive and clear "
            "final answer using the research notes and analysis. "
            f"Tailor the response for an audience of: {state.request.audience}. "
            "Use citations or source references where appropriate."
        )
        
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes}\n\n"
            f"Analysis Notes:\n{state.analysis_notes or 'None'}\n\n"
            "Please write the final answer."
        )
        
        response = llm.complete(system_prompt, user_prompt)
        state.final_answer = response.content
        
        state.agent_results.append(AgentResult(
            agent=self.name,
            content=response.content
        ))
        
        return state
