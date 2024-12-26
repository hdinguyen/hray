import os

from dotenv import load_dotenv
from dspy import LM, ChainOfThought, configure, settings
from llm.signature.amk_signature import AmkSignature
from opentelemetry import trace

load_dotenv()

llm = LM(f"{os.getenv('GROQ_MODEL')}", api_key=f"{os.getenv('GROQ_API_KEY')}")
tracer = trace.get_tracer(__name__)

class AmkAgent():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.parser = ChainOfThought(AmkSignature)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'parser'):
            super().__init__()
            self.parser = ChainOfThought(AmkSignature)

    def call(self, msg: str, context: str):
        with tracer.start_as_current_span("amk_agent.call") as span:
            span.set_attributes({
                "message": msg,
                "context": context
            })

            configure(lm=llm)
            try:
                result = self.parser(msg=msg, context=context)
                span.set_attributes({
                    "result": str(result),
                    "llm_history":str(llm.history[-1]["messages"])
                })
                return result
            except Exception as e:
                span.set_attribute("error", str(e))
                span.record_exception(e)
                raise

