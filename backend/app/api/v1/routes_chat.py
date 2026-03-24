import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.chat import AssistantMessageOut, ChatRequest, ChatResponse, SourceItem
from app.services import llm, memory
from app.services.rag import build_rag_system_prompt, retrieve_similar

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    sess = await memory.get_session_or_none(db, body.session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="Session not found")

    await memory.add_message(db, body.session_id, "user", body.message)
    await db.commit()

    sources: list[SourceItem] = []
    rag_system: str | None = None
    if body.use_rag:
        q_emb = llm.embed_query(body.message)
        retrieved = await retrieve_similar(db, q_emb)
        if retrieved:
            rag_system = build_rag_system_prompt(retrieved)
            for r in retrieved:
                excerpt = r.content if len(r.content) <= 400 else r.content[:397] + "..."
                sources.append(
                    SourceItem(
                        chunk_id=r.chunk_id,
                        doc_id=r.doc_id,
                        excerpt=excerpt,
                        distance=r.distance,
                    )
                )

    history = await memory.load_recent_messages_for_llm(db, body.session_id)
    llm_messages: list[dict[str, str]] = []
    if rag_system:
        llm_messages.append({"role": "system", "content": rag_system})
    llm_messages.extend(history)

    try:
        reply_text = llm.chat_completion(llm_messages)
    except Exception as exc:  # noqa: BLE001 — surface LLM errors to client
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc!s}") from exc

    meta = {"sources": [s.model_dump(mode="json") for s in sources]} if sources else None
    asst = await memory.add_message(
        db,
        body.session_id,
        "assistant",
        reply_text,
        metadata=meta,
    )
    await db.commit()
    await db.refresh(asst)

    return ChatResponse(
        assistant_message=AssistantMessageOut(
            id=asst.id,
            role=asst.role,
            content=asst.content,
            metadata=asst.message_metadata,
            created_at=asst.created_at,
        ),
        sources=sources,
    )
