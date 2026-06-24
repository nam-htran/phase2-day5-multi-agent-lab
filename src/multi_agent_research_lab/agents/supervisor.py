"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        settings = get_settings()
        
        # Enforce max iterations
        if state.iteration >= settings.max_iterations:
            state.record_route("done")
            return state

        # Simple deterministic routing based on state fields
        if not state.research_notes:
            state.record_route("researcher")
        elif not state.analysis_notes:
            state.record_route("analyst")
        elif not state.final_answer:
            state.record_route("writer")
        elif "--- Critic Review ---" not in state.final_answer:
            state.record_route("critic")
        else:
            state.record_route("done")

        return state
