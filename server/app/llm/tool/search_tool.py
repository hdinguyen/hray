import os
from typing import List, Optional

import aiohttp
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

    async def search(self, query: str) -> List[SearchResult]:
        """
        Perform an asynchronous search query using Brave Search API.

        Args:
            query: The search query string

        Returns:
            List of SearchResult objects containing the search results
        """
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }

        params = {
            "q": query,
            "count": self.num_results
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.base_url,
                headers=headers,
                params=params
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Brave Search API error: {error_text}")

                data = await response.json()

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
