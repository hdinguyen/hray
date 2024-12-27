import os
from typing import List, Optional

import dspy
from dotenv import load_dotenv
from dspy import ColBERTv2
from llm.tool.search_tool import BraveSearch
from pydantic import BaseModel

load_dotenv()
class SearchResult(BaseModel):
    """Search result model containing the query and retrieved passages with their sources."""
    query: str
    passages: List[dict[str, str]]  # Each dict contains 'content' and 'source_url'
    answer: str
    sources: List[str]


class SearchRAG:
    """Search-based Retrieval-Augmented Generation using DSPy."""

    def __init__(self, search_tool: Optional[BraveSearch] = None, lm = None):
        """Initialize the SearchRAG with a search tool and language model."""
        if search_tool is None:
            search_tool = BraveSearch()
        self.search_tool = search_tool

        # Configure DSPy with default or provided language model
        if lm is None:
            lm = dspy.LM(f"{os.getenv('GROQ_MODEL')}", api_key=f"{os.getenv('GROQ_API_KEY')}")
        self.lm = lm

        # Create the retriever module
        class RetrieverModule(dspy.Module):
            def __init__(self, search_tool):
                super().__init__()
                self.search_tool = search_tool

            async def forward(self, query):
                results = await self.search_tool.search(query)
                passages = [{"content": r.content, "source_url": r.source_url} for r in results]
                return dspy.Prediction(passages=passages)

        # Define the RAG signature
        class RAGSignature(dspy.Signature):
            """Signature for the RAG module."""
            context = dspy.InputField(desc="Retrieved passages to use as context")
            query = dspy.InputField(desc="The user's question")
            answer = dspy.OutputField(desc="Detailed answer based on the context")
            sources = dspy.OutputField(desc="List of source URLs used to generate the answer")

        # Create the RAG module
        class RAGModule(dspy.Module):
            def __init__(self, lm):
                super().__init__()
                self.lm = lm
                self.generate_answer = dspy.ChainOfThought(RAGSignature)

            def forward(self, context, query):
                self.set_lm(self.lm)
                response = self.generate_answer(context=context, query=query)
                sources = [result.source_url for result in context]
                return response.answer, sources

        # Initialize modules
        self.retriever = RetrieverModule(search_tool)
        self.rag_module = RAGModule(lm=self.lm)

    async def generate(self, query: str, num_results: int = 5) -> SearchResult:
        """
        Generate an answer based on retrieved search results.

        Args:
            query: The user's question
            num_results: Maximum number of results to retrieve

        Returns:
            SearchResult object containing the query, retrieved passages, generated answer and sources
        """
        # First retrieve relevant passages
        search_results = await self.search_tool.search(query)

        # Format passages
        passages = [{"content": r.content, "source_url": r.source_url} for r in search_results]

        # Generate answer using the RAG module
        answer, sources = self.rag_module.forward(
            context=search_results,
            query=query
        )

        return SearchResult(
            query=query,
            passages=passages,
            answer=answer,
            sources=sources
        )
