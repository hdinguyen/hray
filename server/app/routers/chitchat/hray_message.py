import os
from datetime import datetime

from fastapi import HTTPException, Request
from llm.pipeline.quick_reply import QuickReplyPipeline
from sqlalchemy import (Boolean, Column, DateTime, Integer, String,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import router

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    helpful = Column(Boolean)
    question = Column(String)
    response = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    ignore = Column(Boolean, nullable=False, default=False)

@router.get("/quick_reply")
def quick_reply(msg: str):
    quick_reply = QuickReplyPipeline()
    return quick_reply(msg)

@router.post("/feedback")
async def feedback(request: Request):
    feedback_data = await request.json()

    # Create database connection
    DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'root')}@{os.getenv('POSTGRES_HOST', 'localhost')}/{os.getenv('POSTGRES_DB', 'hray')}"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        new_feedback = Feedback(
            helpful=feedback_data.get("helpful"),
            question=feedback_data.get("question"),
            response=feedback_data.get("response"),
            ignore=False
        )
        db.add(new_feedback)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
