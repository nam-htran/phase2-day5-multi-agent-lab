"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Critique the final answer and flag if it needs revision."""
        from multi_agent_research_lab.observability.tracing import trace_span
        with trace_span("critic_agent", {"query": state.request.query}):
            if not state.final_answer:
                return state
                
            llm = LLMClient()
            system_prompt = (
                "You are an expert Reviewer. Review the provided 'Final Answer' against the 'Research Query'. "
                "Output your review. If the answer is poor, start your response with 'CRITIQUE: FAIL'. "
                "Otherwise, start with 'CRITIQUE: PASS'."
            )
            
            user_prompt = (
                f"Query: {state.request.query}\n\n"
                f"Final Answer:\n{state.final_answer}\n\n"
                "Please review."
            )
            
            response = llm.complete(system_prompt, user_prompt)
            review = response.content
            
            state.agent_results.append(AgentResult(
                agent=self.name,
                content=review
            ))
            
            if review.strip().startswith("CRITIQUE: FAIL"):
                state.final_answer = ""
                
            return state
