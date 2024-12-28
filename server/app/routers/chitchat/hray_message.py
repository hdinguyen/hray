from llm.pipeline.quick_reply import QuickReplyPipeline

from . import router


@router.get("/quick_reply")
def quick_reply(msg: str):
    quick_reply = QuickReplyPipeline()

    return quick_reply(msg)
