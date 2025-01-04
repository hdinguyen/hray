import os

from dotenv import load_dotenv
from dspy import LM

load_dotenv()

llm = LM(
    model='openai/xxx',         # "openai/" prefix is required
    api_key="-",                     # this should not be empty or it will not work
    api_base='http://0.0.0.0:8080'
)

llm_default = os.getenv('DEFAULT_MODEL', "LLAMA_CPP")
if llm_default == "GROQ":
    llm = LM(f"{os.getenv('GROQ_MODEL')}", api_key=f"{os.getenv('GROQ_API_KEY')}")
