from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    content_type: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(BaseModel):
    id: Optional[UUID] = None
    filename: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentChunkBase(BaseModel):
    document_id: UUID
    chunk_index: int
    content: str
    token_count: int


class DocumentChunkCreate(DocumentChunkBase):
    pass


class DocumentChunkResponse(DocumentChunkBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentSearchQuery(BaseModel):
    query: str
    limit: int = 5


class SearchResultItem(BaseModel):
    document_id: UUID
    chunk_id: UUID
    document_filename: str
    content: str
    chunk_index: int
    similarity: float

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    results: List[SearchResultItem]
    total: int
    query: str
