import io
import re
import uuid
from dataclasses import dataclass

import tiktoken
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.knowledge import KnowledgeChunk, KnowledgeDoc
from app.services import llm


def _encoding() -> tiktoken.Encoding:
    return tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str) -> list[str]:
    settings = get_settings()
    enc = _encoding()
    max_tok = settings.rag_chunk_max_tokens
    overlap = min(settings.rag_chunk_overlap_tokens, max_tok - 1)
    tokens = enc.encode(text)
    if not tokens:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tok, len(tokens))
        piece = enc.decode(tokens[start:end])
        piece = piece.strip()
        if piece:
            chunks.append(piece)
        if end >= len(tokens):
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def _normalize_text(raw: str) -> str:
    t = raw.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def text_from_upload(filename: str | None, data: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return _normalize_text("\n".join(parts))
    return _normalize_text(data.decode("utf-8", errors="replace"))


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    doc_id: uuid.UUID
    content: str
    distance: float


async def retrieve_similar(
    db: AsyncSession,
    query_embedding: list[float],
    *,
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    settings = get_settings()
    k = top_k if top_k is not None else settings.rag_top_k
    distance_expr = KnowledgeChunk.embedding.cosine_distance(query_embedding)
    stmt = (
        select(KnowledgeChunk, distance_expr.label("distance"))
        .order_by(distance_expr)
        .limit(k)
    )
    result = await db.execute(stmt)
    out: list[RetrievedChunk] = []
    for row in result.all():
        chunk, dist = row[0], float(row[1])
        out.append(
            RetrievedChunk(
                chunk_id=chunk.id,
                doc_id=chunk.doc_id,
                content=chunk.content,
                distance=dist,
            )
        )
    return out


async def ingest_text(
    db: AsyncSession,
    text: str,
    *,
    source: str,
    filename: str | None,
) -> uuid.UUID:
    body = _normalize_text(text)
    if not body:
        raise ValueError("Empty document after normalization")

    doc = KnowledgeDoc(source=source, filename=filename)
    db.add(doc)
    await db.flush()

    parts = chunk_text(body)
    if not parts:
        raise ValueError("No chunks produced")

    embeddings = llm.embed_texts(parts)
    for idx, (piece, emb) in enumerate(zip(parts, embeddings, strict=True)):
        row = KnowledgeChunk(
            doc_id=doc.id,
            chunk_index=idx,
            content=piece,
            embedding=emb,
        )
        db.add(row)

    await db.flush()
    return doc.id


def build_rag_system_prompt(retrieved: list[RetrievedChunk]) -> str:
    lines = [
        "你是教學助理。請只根據下列「參考資料」回答，若資料不足請明確說明。",
        "回答末尾請列出引用編號，格式為：[1]、[2]（對應下方參考段落）。",
        "",
        "參考資料：",
    ]
    for i, r in enumerate(retrieved, start=1):
        lines.append(f"[{i}] (文件片段)\n{r.content}\n")
    return "\n".join(lines)
