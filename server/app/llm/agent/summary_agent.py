import os

import dspy
from dotenv import load_dotenv
from llm.models import groq

dspy.settings.experimental = True

load_dotenv()

class SummaryAgent(dspy.Module):
    """
    SummaryAgent is a module that will summarize the information from other agents
    """
    def __init__(self, lm = None):
        if lm is None:
            lm = groq
        self.lm = lm
        self.react = dspy.ChainOfThought(
            "question, information -> answer"
        )

    def __call__(self, question: str, information: str):
        self.set_lm(self.lm)
        return self.react(question=question, information=information)

