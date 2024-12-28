import dspy
from llm.agent.response_agent import ResponseAgent
from llm.agent.search_rag import SearchReact


class QuickReplyPipeline(dspy.Module):
    def __init__(self, *modules):
        self.modules = modules
        self.search_rag = SearchReact()
        self.response_agent = ResponseAgent()

    def forward(self, query: str):
        search_results = self.search_rag(query)
        return self.response_agent(search_results.answer)

