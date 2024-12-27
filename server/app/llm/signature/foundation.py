from typing import Optional

from pydantic import BaseModel


class ExaQuery(BaseModel):
    text: str
    category: str

class QueryPurpose(BaseModel):
    purpose: str
    question: str
    queries: list[ExaQuery]

class SummarizedContent(BaseModel):
    content: str
    relevance_score: Optional[float] = None
