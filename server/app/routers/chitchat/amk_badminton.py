from datetime import datetime

from llm.agent.amk_agent import AmkAgent
from pydantic import BaseModel

from . import router


class EventInput(BaseModel):
    message: str
    existing_events: list[dict[str, str]]

@router.post("/event")
def read_root(event: EventInput):
    return AmkAgent().call(msg=event.message, context=f"today is {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')} and the existing events are {event.existing_events}")
