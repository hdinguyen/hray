import os
from datetime import datetime

from logger.log import get_logger

logger = get_logger(__name__)

from sqlalchemy import (Boolean, Column, DateTime, Integer, String,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    helpful = Column(Boolean)
    question = Column(String)
    response = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    ignore = Column(Boolean, nullable=False, default=False)

def get_db():
    DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'root')}@{os.getenv('POSTGRES_HOST', 'postgres')}/{os.getenv('POSTGRES_DB', 'hray')}"
    logger.debug(f"DATABASE_URL: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def create_feedback(feedback_data: dict):
    db = get_db()
    try:
        new_feedback = Feedback(
            helpful=feedback_data.get("helpful"),
            question=feedback_data.get("question"),
            response=feedback_data.get("response"),
            ignore=False
        )
        db.add(new_feedback)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
