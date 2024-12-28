from db.feedback import create_feedback
from fastapi import HTTPException, Request
from llm.pipeline.quick_reply import QuickReplyPipeline

from . import router


@router.get("/quick_reply")
def quick_reply(msg: str):
    quick_reply = QuickReplyPipeline()
    return quick_reply(msg)

@router.post("/feedback")
async def feedback(request: Request):
    feedback_data = await request.json()
    try:
        create_feedback(feedback_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
