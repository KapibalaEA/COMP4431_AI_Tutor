import uuid
from datetime import datetime

from pydantic import BaseModel


class SessionCreateResponse(BaseModel):
    session_id: uuid.UUID


class MessageItem(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    metadata: dict | None = None
    created_at: datetime


class MessageListResponse(BaseModel):
    messages: list[MessageItem]
