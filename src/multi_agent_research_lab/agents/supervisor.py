"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Route to next agent."""
        from multi_agent_research_lab.observability.tracing import trace_span
        with trace_span("supervisor_agent", {"query": state.request.query}):
            if not getattr(state, "iteration", None):
                state.iteration = 0
            state.iteration += 1
            
            if state.iteration > 10:
                state.record_route("done")
                return state
                
            if not state.research_notes:
                state.record_route("researcher")
                return state
                
            if not state.analysis_notes:
                state.record_route("analyst")
                return state
                
            if not state.final_answer:
                state.record_route("writer")
                return state
                
            if "critic" not in state.route_history:
                state.record_route("critic")
                return state
                
            state.record_route("done")
            return state
