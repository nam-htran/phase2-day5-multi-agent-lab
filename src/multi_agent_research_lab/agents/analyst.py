"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        if not state.research_notes:
            return state

        llm = LLMClient()
        system_prompt = (
            "You are a Data Analyst. Extract key claims, compare viewpoints, "
            "and flag weak evidence from the provided research notes."
        )
        
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\nPlease analyze."
        
        response = llm.complete(system_prompt, user_prompt)
        state.analysis_notes = response.content
        
        state.agent_results.append(AgentResult(
            agent=self.name,
            content=response.content
        ))
        
        return state
