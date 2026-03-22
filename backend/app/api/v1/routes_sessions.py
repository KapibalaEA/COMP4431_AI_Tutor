import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.schemas.session import MessageItem, MessageListResponse, SessionCreateResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
async def create_session(db: AsyncSession = Depends(get_db)) -> SessionCreateResponse:
    row = ChatSession()
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return SessionCreateResponse(session_id=row.id)


@router.get("/{session_id}/messages", response_model=MessageListResponse)
async def list_messages(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> MessageListResponse:
    sess = await db.get(ChatSession, session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="Session not found")

    stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return MessageListResponse(
        messages=[
            MessageItem(
                id=m.id,
                role=m.role,
                content=m.content,
                metadata=m.message_metadata,
                created_at=m.created_at,
            )
            for m in rows
        ],
    )
