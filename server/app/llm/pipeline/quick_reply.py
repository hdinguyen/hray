import dspy
from langdetect import detect
from llm.agent.response_agent import ResponseAgent
from llm.agent.search_rag import SearchReact
from logger.log import get_logger

logger = get_logger(__name__)
class QuickReplyPipeline(dspy.Module):
    def __init__(self, *modules):
        self.modules = modules
        self.search_rag = SearchReact()
        self.response_agent = ResponseAgent()

    def forward(self, query: str):
        language = detect(query)
        logger.info(f"Query: {query}")
        logger.info(f"Language: {language}")
        search_results = self.search_rag(query)
        return self.response_agent(search_results.answer, language)

