import os

import dspy
from dotenv import load_dotenv
from logger.log import logger

load_dotenv()
class ToolChoice(dspy.Signature):
   """Determines which tool would be most appropriate to handle the user's request"""

   purpose = dspy.InputField(desc="Why we need to select a tool - what is the user trying to accomplish?")
   list_of_tools = dspy.InputField(desc="List of available tools that could potentially help")
   query = dspy.InputField(desc="The specific user request/query we need to handle")
   selected_tools = dspy.OutputField(desc="The most appropriate tools from the list to handle this request")


class GenerateAnswer(dspy.Signature):
   """Generates a clear, informative response to help the user understand the answer to their question"""

   purpose = dspy.InputField(desc="Why the user is asking this question - what are they trying to learn or understand?")
   context = dspy.InputField(desc="Relevant background information and facts to inform the answer")
   question = dspy.InputField(desc="The specific question being asked")
   answer = dspy.OutputField(desc="A clear, focused response that directly addresses the user's need")

class ToolRetriever(dspy.Module):
    def __init__(self, lm = None):
        self.generate_query = dspy.ChainOfThought("context, question -> query, purpose")
        self.choose_tool = dspy.ChainOfThought(ToolChoice)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        self.tools = ["answer_payroll_faq", "irrelevant_content", "get_calendar_events", "scan_flight_prices", "forecast_events", "forecast_weather"]
        if lm is None:
            lm = dspy.LM(f"{os.getenv('GROQ_MODEL')}", api_key=f"{os.getenv('GROQ_API_KEY')}")
        self.lm = lm

    def add_tool(self, tool):
        self.tools.append(tool)

    def irrelevant_content(self):
        return "Ask something else."

    def forward(self, question):
        self.set_lm(self.lm)

        context = []
        query_output = self.generate_query(context=context, question=question)
        tool_choice = self.choose_tool(
            purpose="To determine the most appropriate tool to handle the user's question",
            list_of_tools=f"[{', '.join(self.tools)}]",
            query=query_output.query
        )

        if tool_choice.selected_tools == "irrelevant_content":
            return self.irrelevant_content()
        else:
            logger.info(f"Using tool: {tool_choice.selected_tools}")
            return self.generate_answer(
                purpose="To provide helpful information to the user's question",
                context=context,
                question=question
            )
