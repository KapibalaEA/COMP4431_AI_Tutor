import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.knowledge import KnowledgeDoc
from app.schemas.knowledge import DocumentItem, DocumentListResponse, IngestResponse, IngestTextBody
from app.services.rag import ingest_text, text_from_upload

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_json(
    body: IngestTextBody,
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    try:
        doc_id = await ingest_text(
            db,
            body.text,
            source=body.source,
            filename=body.filename,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await db.commit()
    return IngestResponse(document_id=doc_id)


@router.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    source: str = Form(default="file"),
) -> IngestResponse:
    data = await file.read()
    try:
        text = text_from_upload(file.filename, data)
        doc_id = await ingest_text(db, text, source=source, filename=file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await db.commit()
    return IngestResponse(document_id=doc_id)


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(db: AsyncSession = Depends(get_db)) -> DocumentListResponse:
    stmt = select(KnowledgeDoc).order_by(KnowledgeDoc.created_at.desc())
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return DocumentListResponse(documents=[DocumentItem.model_validate(r) for r in rows])


@router.delete("/documents/{doc_id}", status_code=204)
async def delete_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    row = await db.get(KnowledgeDoc, doc_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(row)
    await db.commit()
