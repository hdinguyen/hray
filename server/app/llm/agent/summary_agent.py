import os

import dspy
from dotenv import load_dotenv

dspy.settings.experimental = True

load_dotenv()

class SummaryAgent(dspy.Module):
    """
    SummaryAgent is a module that will summarize the information from other agents
    """
    def __init__(self, lm = None):
        if lm is None:
            lm = dspy.LM(f"{os.getenv('GROQ_MODEL')}", api_key=f"{os.getenv('GROQ_API_KEY')}")
        self.lm = lm
        self.react = dspy.ChainOfThought(
            "question, information -> answer"
        )

    def __call__(self, question: str, information: str):
        self.set_lm(self.lm)
        return self.react(question=question, information=information)

