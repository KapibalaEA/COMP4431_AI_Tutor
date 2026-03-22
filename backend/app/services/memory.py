import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.chat_session import ChatSession
from app.models.message import Message


async def get_session_or_none(db: AsyncSession, session_id: uuid.UUID) -> ChatSession | None:
    return await db.get(ChatSession, session_id)


async def load_recent_messages_for_llm(
    db: AsyncSession,
    session_id: uuid.UUID,
) -> list[dict[str, str]]:
    settings = get_settings()
    limit = settings.chat_context_max_messages
    stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = list(result.scalars().all())
    rows.reverse()
    return [{"role": m.role, "content": m.content} for m in rows]


async def add_message(
    db: AsyncSession,
    session_id: uuid.UUID,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> Message:
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        message_metadata=metadata,
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    return msg
