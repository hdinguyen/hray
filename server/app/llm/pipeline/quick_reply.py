import dspy
from llm.agent.aggregate_agent import AggregateAgent
from llm.agent.response_agent import ResponseAgent
from llm.agent.search_agent import SearchReact
from llm.agent.summary_agent import SummaryAgent
from llm.models import llm
from logger.log import get_logger

logger = get_logger(__name__)
class QuickReplyPipeline(dspy.Module):
    def __init__(self, *modules):
        self.modules = modules
        self.aggregate_agent = AggregateAgent(lm=llm)
        self.search_rag = SearchReact(lm=llm)
        self.response_agent = ResponseAgent(lm=llm)
        self.summary_agent = SummaryAgent(lm=llm)

    def forward(self, query: str):
        aggreage_information =self.aggregate_agent(query)
        summary_information = self.summary_agent(query, aggreage_information.information)
        return self.response_agent(question=query, reality_information=summary_information.answer)

