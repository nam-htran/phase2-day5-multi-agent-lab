"""Search client abstraction for ResearcherAgent."""

import os
import requests

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            # Nếu chưa điền key Tavily, trả về dữ liệu giả lập (mock)
            return [
                SourceDocument(
                    title="Mock Document",
                    url="https://example.com/mock",
                    snippet=f"This is a mock snippet for query: {query}",
                    metadata={"source": "mock"}
                )
            ]
            
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_raw_content": False
                },
                timeout=15.0
            )
            response.raise_for_status()
            data = response.json()
            
            documents = []
            for item in data.get("results", []):
                documents.append(
                    SourceDocument(
                        title=item.get("title", "No Title"),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        metadata={"score": item.get("score", 0.0)}
                    )
                )
            return documents
        except Exception as e:
            print(f"Search failed: {e}")
            return []
