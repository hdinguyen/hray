import os
from typing import Optional

import dspy
from dotenv import load_dotenv
from llm.tool.search_tool import brave_search

dspy.settings.experimental = True

load_dotenv()

class SearchReact(dspy.Module):
    def __init__(self, lm = None):
        if lm is None:
            lm = dspy.LM(f"{os.getenv('GROQ_MODEL')}", api_key=f"{os.getenv('GROQ_API_KEY')}")
        self.lm = lm
        self.react = dspy.ReAct(
            "question, purpose -> answer",
            tools=[brave_search]
        )

    def __call__(self, query: str, purpose: Optional[str]=None):
        self.set_lm(self.lm)
        # If no purpose provided, use the query itself as the purpose
        if purpose is None:
            purpose = query
        return self.react(question=query, purpose=purpose)

