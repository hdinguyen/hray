from db.feedback import create_feedback, get_feedback
from fastapi import HTTPException, Request
from llm.pipeline.quick_reply import QuickReplyPipeline

from . import router


@router.get("/quick_reply")
def quick_reply(msg: str):
    if msg.strip() == "":
            return {"status": "success", "display": "lack_context", "data": "I don't have enough context to answer your question, please provide more information"}
    quick_reply = QuickReplyPipeline()
    return quick_reply(msg)

@router.get("/history")
def history():
    return get_feedback()

@router.get("/waiting")
def waiting():
    return {"status": "success", "type": "gif", "data": "https://media.giphy.com/media/4JVTF9zR9BicshFAb7/giphy.gif?cid=ecf05e47d4qx4j1zqt6zd3o57mbbg8hmb0jk3vbnyshjz1m3&ep=v1_gifs_related&rid=giphy.gif&ct=g"}

@router.post("/feedback")
async def feedback(request: Request):
    feedback_data = await request.json()
    try:
        create_feedback(feedback_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
