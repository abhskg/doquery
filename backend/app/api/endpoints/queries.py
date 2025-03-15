from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query_documents(
    query: QueryRequest = Body(...),
    db: Session = Depends(get_db),
):
    """
    Query against embedded documents and return AI-generated answers.
    """
    # RAG query logic will be implemented here
    return {"question": query.question, "answer": "This is where the AI-generated answer will appear."} 