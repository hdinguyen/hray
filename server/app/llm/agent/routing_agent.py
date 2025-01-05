from typing import List, Literal

from dspy import InputField, Module, OutputField, Predict, Signature
from logger.log import get_logger

logger = get_logger(__name__)

class RoutingSignature(Signature):
    question: str = InputField(description="Original question from user")
    agent_name: Literal["web_search", "lack_context", "translate_agent", "summary_agent", "greeting_agent"] = OutputField(description="This is the agent name that must be used for the next step, could be lack_context if the user's question is not clear or not related to the context")

class RoutingAgent(Module):
    def __init__(self, lm = None):
        self.agent_name = "routing_agent"
        if lm is None:
            logger.fatal("RoutingAgent: lm is not set")
            raise ValueError("lm is not set")
        self.predictor = Predict(RoutingSignature)
        self.predictor.set_lm(lm)


    def __call__(self, question: str):
        return self.predictor(question=question)

