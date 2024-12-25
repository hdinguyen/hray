import os

from dotenv import load_dotenv
from dspy import LM, ChainOfThought, configure, settings
from llm.signature.amk_signature import AmkSignature

load_dotenv()

print(os.getenv("GROQ_API_KEY"))

llm =LM("groq/llama3-8b-8192", api_key=f"{os.getenv("GROQ_API_KEY")}")

class AmkAgent():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.parser = ChainOfThought(AmkSignature)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'parser'):  # Only initialize if not already done
            super().__init__()
            self.parser = ChainOfThought(AmkSignature)

    def call(self, msg: str, context: str):
        configure(lm=llm)
        print(context)
        print(msg)
        return self.parser(msg=msg, context=context)
