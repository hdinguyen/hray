import os
from datetime import datetime

import dspy
from dotenv import load_dotenv
from dspy import InputField, OutputField, Signature
from llm.tool.search_tool import brave_search
from pydantic import BaseModel

dspy.settings.experimental = True

load_dotenv()

class DeepThought(BaseModel):
    msg: str = InputField(description="The message is from chat user")
    context: str = InputField(description="The context included the current time information and existing events")

class RoutingSignature(Signature):
    msg: str = InputField(description="The message is from chat user")
    context: str = InputField(description="The context included the current time information and existing events")
    response: list[DeepThought] = OutputField(description="List of next Modules to be called")

class RoutingRag(dspy.Module):
    def __init__(self, lm = None):
        if lm is None:
            lm = dspy.LM(f"{os.getenv('GROQ_MODEL')}", api_key=f"{os.getenv('GROQ_API_KEY')}")
        self.lm = lm
        self.thinker = dspy.ChainOfThought(RoutingSignature)

    def __call__(self, query: str):
        self.set_lm(self.lm)
        return self.thinker(msg=query, context=f"Current time is {datetime.now()}")
