"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""
        if not state.final_answer:
            return state

        llm = LLMClient()
        system_prompt = (
            "You are a strict Critic. Review the final answer against the research notes. "
            "Provide a brief critique. If it is good, say 'CRITIQUE: PASS'. "
            "If it has issues, say 'CRITIQUE: FAIL' and explain why."
        )
        
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes}\n\n"
            f"Final Answer:\n{state.final_answer}\n\n"
            "Please provide your critique."
        )
        
        response = llm.complete(system_prompt, user_prompt)
        critique_text = response.content
        
        # Append critique to final answer
        state.final_answer += f"\n\n--- Critic Review ---\n{critique_text}"
        
        state.agent_results.append(AgentResult(
            agent=self.name,
            content=critique_text
        ))
        
        return state
