from fastapi import APIRouter

router = APIRouter(prefix="/agentic")

from . import translator
