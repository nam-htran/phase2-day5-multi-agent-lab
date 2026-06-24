"""LangGraph workflow skeleton."""

from langgraph.graph import StateGraph, END

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.critic import CriticAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def build(self) -> object:
        """Create a LangGraph graph."""
        graph = StateGraph(ResearchState)
        
        # Instantiate agents
        supervisor = SupervisorAgent()
        researcher = ResearcherAgent()
        analyst = AnalystAgent()
        writer = WriterAgent()
        critic = CriticAgent()
        
        # Add nodes
        graph.add_node("supervisor", supervisor.run)
        graph.add_node("researcher", researcher.run)
        graph.add_node("analyst", analyst.run)
        graph.add_node("writer", writer.run)
        graph.add_node("critic", critic.run)
        
        # Add edges
        graph.add_edge("researcher", "supervisor")
        graph.add_edge("analyst", "supervisor")
        graph.add_edge("writer", "supervisor")
        graph.add_edge("critic", "supervisor")
        
        # Conditional routing from supervisor
        def route(state: ResearchState) -> str:
            if not state.route_history:
                return "done"
            next_step = state.route_history[-1]
            if next_step == "done":
                return END
            return next_step

        graph.add_conditional_edges("supervisor", route)
        graph.set_entry_point("supervisor")
        
        return graph.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        app = self.build()
        # LangGraph invoke typically takes dict or BaseModel.
        # It returns a dict if the state is Pydantic in recent versions.
        result = app.invoke(state)
        
        if isinstance(result, dict):
            return ResearchState(**result)
        return result
