from typing import List, Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 4


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: Optional[List[str]] = None
