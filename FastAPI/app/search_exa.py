"""
FocusFlow 3D - Person 3: Web Scraper Agent (Exa API).
Uses Exa for web search. Set EXA_API_KEY in env or .env.
Same interface as search.py: search_topic(), get_bookshelf_resources().
"""
import os
import re
from typing import List

# Optional: load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# In-memory cache for demo and rate limits
_cache: dict = {}
CACHE_MAX = 200


def _safe_str(s: str) -> str:
    """Strip problematic chars for Windows/JSON (e.g. emoji)."""
    if not s:
        return ""
    return re.sub(r"[^\x00-\x7F]+", " ", s).strip()[:500]


def _get_exa_client():
    """Lazy init Exa client (requires exa-py and EXA_API_KEY)."""
    from exa_py import Exa
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY is not set. Add it to .env or environment.")
    return Exa(api_key=api_key)


def search_topic(topic: str, max_results: int = 5) -> List[dict]:
    """
    Search web for a topic using Exa.
    Returns list of {title, url, snippet} for bookshelf display.
    """
    key = (topic.strip().lower(), max_results)
    if key in _cache:
        return _cache[key]
    try:
        exa = _get_exa_client()
        results = exa.search(
            query=topic,
            type="auto",
            num_results=max_results,
            contents={"text": {"max_characters": 20000}},
        )
        out = []
        for r in results.results:
            # Exa result: .title, .url; .text when contents requested
            text = getattr(r, "text", None) or getattr(r, "content", None) or ""
            if isinstance(text, list):
                text = " ".join(str(x) for x in text)[:500]
            else:
                text = _safe_str(str(text)[:500])
            out.append({
                "title": _safe_str(getattr(r, "title", "") or ""),
                "url": getattr(r, "url", "") or "",
                "snippet": text or _safe_str(getattr(r, "description", "") or ""),
            })
        if len(_cache) < CACHE_MAX:
            _cache[key] = out
        return out
    except Exception as e:
        return [{"title": "Error", "url": "", "snippet": str(e)}]


def get_bookshelf_resources(topics: List[str], per_topic: int = 3) -> List[dict]:
    """For each topic, fetch resources and tag with topic. Frontend can show on bookshelf."""
    resources = []
    for topic in topics:
        if not topic or not topic.strip():
            continue
        topic = topic.strip()
        for item in search_topic(topic, max_results=per_topic):
            item["topic"] = topic
            resources.append(item)
    return resources
