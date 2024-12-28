from fastapi import APIRouter

router = APIRouter(prefix="/llm")

# Import all routes from the different files
from . import amk_badminton, hray_message
