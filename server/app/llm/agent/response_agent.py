import os
from typing import Optional

import dspy
from dotenv import load_dotenv
from dspy import InputField, OutputField, Signature

dspy.settings.experimental = True

load_dotenv()

class ResponseSignature(Signature):
    question: str = InputField(description="The question from user")
    information: str = InputField(description="The extra information from other modules")
    language: str = InputField(description="Language must use for the response in ISO 639-1 format")
    response: str = OutputField(description="The response in markdown format with replace \n with new line in markdown format")

class LanguageSignature(Signature):
    question: str = InputField(description="Original question from user")
    language: str = OutputField(description="The language must be used for answer in ISO 639-1 format")

class ResponseAgent(dspy.Module):
    def __init__(self, lm = None):
        if lm is None:
            lm = dspy.LM(f"{os.getenv('GROQ_MODEL')}", api_key=f"{os.getenv('GROQ_API_KEY')}")
        self.lm = lm
        self.cot = dspy.ChainOfThought(LanguageSignature)
        self.responder = dspy.ChainOfThought(ResponseSignature)

    def __call__(self, question: str, reality_information: str) -> str:
        """
        Format the response as markdown.

        Args:
            query: The user's query
            language: The language of the query, this used to reponse the same language as the query if the request is not asking for translate
            context: Optional context information

        Returns:
            Markdown formatted response string
        """
        self.set_lm(self.lm)
        language = self.cot(question=question)

        result = self.responder(question=question, information=reality_information, language=language)
        return result.response
