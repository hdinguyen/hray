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
