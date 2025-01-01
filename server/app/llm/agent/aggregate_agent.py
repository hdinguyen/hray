import os
from typing import List, Optional

import dspy
from dotenv import load_dotenv
from dspy import InputField, OutputField, Signature
from llm.models import groq
from llm.tool.search_tool import brave_search_tool, google_search_tool
from pydantic import BaseModel, Field

dspy.settings.experimental = True

load_dotenv()

class AggregateAgent(dspy.Module):
    """
    AggregateAgent is a module that will decide and collect data from other related agents
    """
    def __init__(self, lm = None):
        if lm is None:
            lm = groq
        self.lm = lm
        self.react = dspy.ReAct(
            "question -> information",
            tools=[brave_search_tool, google_search_tool]
        )

    def __call__(self, query: str):
        self.set_lm(self.lm)
        return self.react(question=query)

