from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes_chat import router as chat_router
from app.api.v1.routes_health import router as health_router
from app.api.v1.routes_knowledge import router as knowledge_router
from app.api.v1.routes_sessions import router as sessions_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="AI Tutor API",
        version="0.1.0",
        description="Sessions, chat (optional RAG), and knowledge ingestion.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)

    api_v1 = APIRouter(prefix="/api/v1")
    api_v1.include_router(sessions_router)
    api_v1.include_router(chat_router)
    api_v1.include_router(knowledge_router)
    app.include_router(api_v1)

    return app


app = create_app()
