import os
from typing import List, Optional

# import aiohttp
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class SearchResult(BaseModel):
    """Model for a single search result."""
    title: str
    content: str
    source_url: str
    snippet: Optional[str] = None

class BraveSearch:
    """Tool for performing searches using the Brave Search API."""

    def __init__(self, api_key: Optional[str] = None, num_results: int = 5):
        """
        Initialize the Brave search tool.

        Args:
            api_key: Brave Search API key. If not provided, will look for BRAVE_API_KEY in environment
            num_results: Number of results to return per search (default: 5)
        """
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("Brave API key must be provided or set in BRAVE_API_KEY environment variable")

        self.num_results: int = num_results
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    def __call__(self, query: str) -> List[SearchResult]:
        """
        Synchronous wrapper around the async search method.

        Args:
            query: The search query string

        Returns:
            List of SearchResult objects containing the search results
        """


        response = requests.get(
            self.base_url,
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            },
            params={
                "q": query,
                "count": self.num_results
            }
        )

        if response.status_code != 200:
            raise Exception(f"Brave Search API error: {response.text}")

        data = response.json()

        results = []
        for web_result in data.get("web", {}).get("results", []):
            result = SearchResult(
                title=web_result.get("title", ""),
                content=web_result.get("description", ""),
                source_url=web_result.get("url", ""),
                snippet=web_result.get("description", "")
            )
            results.append(result)

        return results

# Create a default instance
brave_search = BraveSearch()


from dspy import Tool

brave_search_tool = Tool(
    name="brave_search",
    desc="Search the web for information",
    func=BraveSearch()
)
