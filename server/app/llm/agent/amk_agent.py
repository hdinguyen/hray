import os

from dotenv import load_dotenv
from dspy import LM, ChainOfThought, configure, settings
from llm.models import groq
from opentelemetry import trace

load_dotenv()

tracer = trace.get_tracer(__name__)

from datetime import datetime

from dspy import InputField, OutputField, Signature
from pydantic import BaseModel


class AMKEvent(BaseModel):
    '''
    event_start_dt: start time of the event
    event_finish_dt: end time of the event
    event_location: location of the event
    joiners: list of joiners
    conflict: if the event has overlap with existing events then it is conflict
    '''
    event_start_dt: datetime
    event_finish_dt: datetime
    event_location: str
    joiners: str
    conflict: bool

class AmkSignature(Signature):
    msg: str = InputField(description="The message is from chat user")
    context: str = InputField(description="The context included the current time information and existing events")
    response: list[AMKEvent] = OutputField(description="The response is from llm")


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

            configure(lm=groq)
            try:
                result = self.parser(msg=msg, context=context)
                span.set_attributes({
                    "result": str(result),
                    "llm_history":str(groq.history[-1]["messages"])
                })
                return result
            except Exception as e:
                span.set_attribute("error", str(e))
                span.record_exception(e)
                raise

