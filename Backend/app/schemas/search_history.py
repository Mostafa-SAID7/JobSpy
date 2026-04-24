from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class SearchHistoryBase(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    search_type: str = Field(..., min_length=1, max_length=50)


class SearchHistoryCreate(SearchHistoryBase):
    job_id: Optional[UUID] = None
    filters: Optional[Dict[str, Any]] = None
    results_count: int = 0


class SearchHistoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    job_id: Optional[UUID] = None
    query: str
    filters: Optional[Dict[str, Any]] = None
    results_count: int
    search_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class SearchHistoryListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[SearchHistoryResponse]
