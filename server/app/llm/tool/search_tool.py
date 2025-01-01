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
    desc="Search the web for information with Brave search engine",
    func=BraveSearch()
)


class GoogleSearch:
    def __init__(self, api_key: Optional[str] = None, engine_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key must be provided or set in GOOGLE_API_KEY environment variable")
        self.engine_id = api_key or os.getenv("GOOGLE_ENGINE_ID")
        if not self.engine_id:
            raise ValueError("Google API key must be provided or set in GOOGLE_API_KEY environment variable")

        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def __call__(self, query: str) -> List[SearchResult]:
        params = {
            "q": query,
            "key": self.api_key,
            "cx": self.engine_id
        }
        r = requests.get(self.base_url, params=params)
        if r.status_code != 200:
            raise Exception(f"Google Search API error: {r.text}")
        data = r.json()
        print(data)
        results = []
        for item in data.get("items", []):
            results.append(SearchResult(title=item.get("title", ""), content=item.get("snippet", ""), source_url=item.get("link", "")))
        return results

google_search_tool = Tool(
    name="google_search",
    desc="Search the web for information with Google search engine",
    func=GoogleSearch()
)
