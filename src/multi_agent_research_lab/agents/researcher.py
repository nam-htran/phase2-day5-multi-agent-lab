"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        from multi_agent_research_lab.observability.tracing import trace_span
        with trace_span("researcher_agent", {"query": state.request.query}):
            # 1. Search for information
            search_client = SearchClient()
            query = state.request.query
            sources = search_client.search(query, max_results=state.request.max_sources)
            state.sources = sources
            
            # 2. Summarize findings using LLM
            llm = LLMClient()
            system_prompt = "You are a Research Assistant. Summarize the provided sources to answer the query."
            
            source_texts = "\n\n".join([f"Source {i+1} ({s.url}): {s.title}\n{s.snippet}" for i, s in enumerate(sources)])
            user_prompt = f"Query: {query}\n\nSources:\n{source_texts}\n\nPlease write detailed research notes."
            
            response = llm.complete(system_prompt, user_prompt)
            state.research_notes = response.content
            
            # Record agent result
            state.agent_results.append(AgentResult(
                agent=self.name,
                content=response.content
            ))
            
            return state
