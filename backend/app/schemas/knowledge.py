import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class IngestTextBody(BaseModel):
    text: str = Field(..., min_length=1)
    source: str = Field(default="paste", max_length=32)
    filename: str | None = Field(default=None, max_length=1024)


class IngestResponse(BaseModel):
    document_id: uuid.UUID


class DocumentItem(BaseModel):
    id: uuid.UUID
    source: str
    filename: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentItem]
