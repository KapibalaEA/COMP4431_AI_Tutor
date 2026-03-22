import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: uuid.UUID
    message: str = Field(..., min_length=1)
    use_rag: bool = False


class SourceItem(BaseModel):
    chunk_id: uuid.UUID
    doc_id: uuid.UUID
    excerpt: str
    distance: float


class AssistantMessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    metadata: dict | None = None
    created_at: datetime


class ChatResponse(BaseModel):
    assistant_message: AssistantMessageOut
    sources: list[SourceItem] = Field(default_factory=list)
