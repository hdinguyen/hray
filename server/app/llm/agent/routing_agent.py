import os
from typing import Any, Literal

from dotenv import load_dotenv
from dspy import InputField, Module, OutputField, Predict, Signature
from llm.agent import BaseAgent
from llm.models import llm
from logger.log import get_logger

logger = get_logger(__name__)

load_dotenv()

class RoutingSignature(Signature):
    question: str = InputField(description="Original question from user")
    agent_name: Literal["web_search", "lack_context", "translate_agent", "summary_agent", "greeting_agent"] = OutputField(description="This is the agent name that must be used for the next step, could be lack_context if the user's question is not clear or not related to the context")

class RoutingAgent(BaseAgent):
    def __init__(self, **data):
        super().__init__(**data)
        self.lm = data.get('lm', None)
        optimise_path = os.getenv('OPTIMISE_PATH', "llm/optimise")

        self.predictor = Predict(RoutingSignature)

        file_path = f"{optimise_path}/{self.name}/full/program.pkl"

        if data.get('mode', 'default') != 'training' and os.path.exists(file_path):
            logger.info(f"Loading optimised prompt from {file_path}")
            try:
                self.predictor.load(file_path)
            except Exception as e:
                logger.error(f"Error loading predictor: {e}")
                raise

        if self.lm is None:
            logger.info("RoutingAgent: lm is not set, using the default llm")
            self.lm = llm
        self.predictor.set_lm(self.lm)

    def __call__(self, question: str):
        return self.predictor(question=question)
