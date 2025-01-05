import os

import dspy
from dotenv import load_dotenv
from dspy.primitives import Example
from dspy.teleprompt import BootstrapFewShot
from llm.agent.routing_agent import RoutingAgent
from llm.models import llm

load_dotenv()

dspy.settings.experimental = True
dspy.configure(lm=llm)

def agent_name_match(example, prediction, trace=None):
    return example.agent_name.lower() == prediction.agent_name.lower()

teleprompt = BootstrapFewShot(
    metric=agent_name_match
)

trainset = [
    Example(question="What is the capital of France?", agent_name="web_search").with_inputs("question"),
    Example(question="Translate to vietnamese: How is your holidays trip?", agent_name="translate_agent").with_inputs("question"),
    Example(question="Help me to summary the content from the clipboard", agent_name="summary_agent").with_inputs("question"),
    Example(question="lpgkfdaspdsagfjdsriag jrioa fkdosprfkjewq fdaskpfwqeo", agent_name="lack_context").with_inputs("question"),
    Example(question="Hello, how are you?", agent_name="greeting_agent").with_inputs("question")
]

agent = RoutingAgent(lm=llm)

compiled_prompt = teleprompt.compile(agent, trainset=trainset)

path = os.getenv('OPTIMISE_PATH', "llm/optimise")
compiled_prompt.save(f"{path}/{agent.agent_name}/full/", save_program=True)
