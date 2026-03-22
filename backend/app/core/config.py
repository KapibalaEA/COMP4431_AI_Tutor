from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aitutor"

    openai_api_key: str = ""

    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 120.0
    llm_max_retries: int = 3

    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    rag_top_k: int = 5
    rag_chunk_max_tokens: int = 512
    rag_chunk_overlap_tokens: int = 64

    chat_context_max_messages: int = 20

    cors_origins: str = "http://localhost:8080,http://127.0.0.1:8080"

    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
