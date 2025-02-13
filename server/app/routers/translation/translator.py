import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException, Request
from llm.agent.translate import Translator
from llm.models import anthropic_llm, llm
from logger.log import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)

from . import router


@router.get("/test")
def test():
    return {"status": "success", "data": "test"}

t = Translator(lm=llm)

class TranslationRequest(BaseModel):
    text: str

executor = ThreadPoolExecutor()

class TempMemory:
    def __init__(self):
        self.memory = []
        self.progress = 0.0
        self.new_terms = []

tmp_memory = TempMemory()

@router.get("/translate/model")
def get_llm():
    return {"status": "success", "data": t.lm.model}

class ModelRequest(BaseModel):
    model: str

@router.post("/translate/model/set")
def set_llm(request: ModelRequest):
    global t
    if request.model == "llm":
        t = Translator(lm=llm)
    elif request.model == "anthropic":
        t = Translator(lm=anthropic_llm)
    return {"status": "success", "data": t.lm.model}


@router.post("/translate")
async def translate(request: TranslationRequest):
    try:
        # Run translation in background without waiting for result
        asyncio.create_task(translate_async(request))
        return {"status": "success", "message": "Translation started"}
    except Exception as e:
        logger.error(f"Failed to start translation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start translation")

async def translate_async(request: TranslationRequest):
    await asyncio.to_thread(t.forward, text=request.text, tmp_memory=tmp_memory)

@router.get("/progress")
def progress():
    return {"status": "success", "data": tmp_memory.progress}

@router.get("/memory")
def memory():
    combined_text = ""
    if tmp_memory.memory:
        # Combine all translations with proper line breaks
        combined_text = "\n".join(item["translation"] for item in tmp_memory.memory)

    return {"status": "success", "data": combined_text}

@router.get("/new_terms")
def new_terms():
    return {"status": "success", "data": tmp_memory.new_terms}
