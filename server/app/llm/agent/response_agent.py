import os
from typing import Optional

import dspy
from dotenv import load_dotenv
from dspy import InputField, OutputField, Signature

dspy.settings.experimental = True

load_dotenv()

class ResponseSignature(Signature):
    input: str = InputField(description="The input from other modules")
    response: str = OutputField(description="The response in markdown format")

class ResponseAgent(dspy.Module):
    def __init__(self, lm = None):
        if lm is None:
            lm = dspy.LM(f"{os.getenv('GROQ_MODEL')}", api_key=f"{os.getenv('GROQ_API_KEY')}")
        self.lm = lm
        self.responder = dspy.ChainOfThought(ResponseSignature)

    def __call__(self, query: str) -> str:
        """
        Format the response as markdown.

        Args:
            query: The user's query
            context: Optional context information

        Returns:
            Markdown formatted response string
        """
        self.set_lm(self.lm)
        result = self.responder(input=query)
        return result.response
