from fastapi import APIRouter
from llm.agent.amk_agent import AmkAgent
from pydantic import BaseModel

router = APIRouter(prefix="/llm")


class EventInput(BaseModel):
    message: str
    existing_events: list[dict[str, str]]

@router.get("/")
def health_check():
    return {"message": "Hellow from llm"}

@router.post("/event")
def read_root(event: EventInput):
    print(event)
    return AmkAgent().call(msg=event.message, context=f"today is 2024-12-25T09:49:00+08:00 and the existing events are {event.existing_events}")
