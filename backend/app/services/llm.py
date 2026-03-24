from typing import Any

from openai import OpenAI

from app.core.config import get_settings


def get_openai_client() -> OpenAI:
    s = get_settings()
    return OpenAI(
        api_key=s.openai_api_key or "dummy-key",
        base_url=s.llm_base_url.rstrip("/"),
        timeout=s.llm_timeout_seconds,
        max_retries=s.llm_max_retries,
    )


def chat_completion(
    messages: list[dict[str, Any]],
    *,
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    s = get_settings()
    client = get_openai_client()
    name = model or s.llm_model
    response = client.chat.completions.create(
        model=name,
        messages=messages,
        temperature=temperature,
    )
    choice = response.choices[0]
    content = choice.message.content
    if not content:
        return ""
    return content


def embed_texts(texts: list[str]) -> list[list[float]]:
    s = get_settings()
    client = get_openai_client()
    out: list[list[float]] = []
    batch_size = 16
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(
            model=s.embedding_model,
            input=batch,
        )
        for item in sorted(resp.data, key=lambda d: d.index):
            out.append(list(item.embedding))
    return out


def embed_query(text: str) -> list[float]:
    vectors = embed_texts([text])
    return vectors[0]
