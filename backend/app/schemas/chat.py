from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Reference(BaseModel):
    document_id: str
    page: int
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    document_ids: list[str] = Field(default_factory=list)
    chat_id: Optional[str] = None


class ChatMessageItem(BaseModel):
    id: str
    role: str
    message: str
    references: Optional[list[Reference]] = None
    timestamp: datetime


class ChatResponse(BaseModel):
    id: str
    chat_id: str
    message: str
    references: list[Reference]
    timestamp: datetime


class ChatSessionItem(BaseModel):
    id: str
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryData(BaseModel):
    id: str
    items: list[ChatMessageItem]
    total: int
    page: int
    page_size: int
    total_pages: int
