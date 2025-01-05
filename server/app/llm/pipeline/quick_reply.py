import dspy
from llm.agent.aggregate_agent import AggregateAgent
from llm.agent.routing_agent import RoutingAgent
from llm.agent.search_agent import SearchReact
from llm.agent.summary_agent import SummaryAgent
from llm.models import llm
from logger.log import get_logger

logger = get_logger(__name__)
class QuickReplyPipeline(dspy.Module):
    def __init__(self, *modules):
        self.modules = modules
        self.routing_agent = RoutingAgent(lm=llm)

    def forward(self, query: str):
        agent_name = self.routing_agent(question=query)
        if agent_name == "web_search":
            return {"status": "success", "display": "result", "data": "web_search"}
        return {"status": "success", "display": "lack_context", "data": "I don't have enough context to answer your question, please provide more information"}

